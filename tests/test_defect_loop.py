"""Regression tests for the automated defect-to-guideline improvement loop infra (log_defect + mine_failures).

Guards the deterministic parts of corpus ingestion (parse / validate /
append — cluster slug, decision and stage enums, transition audit fields)
and clustering (cluster grouping with legacy-mechanism fallback,
recurring-after-fix priority, addressable=false separation, watermark
window, --pages listing).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import log_defect as ld  # noqa: E402
import mine_failures as mfa  # noqa: E402


# --- log_defect: parse ---

def test_parse_accepts_array_and_jsonl():
    arr = ld.parse_records('[{"kind":"defect"},{"kind":"transition"}]')
    jsonl = ld.parse_records('{"kind":"defect"}\n{"kind":"transition"}')
    assert len(arr) == 2 and len(jsonl) == 2


def test_parse_empty_is_empty():
    assert ld.parse_records("   ") == []


def test_parse_tolerates_utf8_bom():
    """PowerShell prepends a BOM when piping to a native command, so the documented
    `... | python tools/log_defect.py` usage arrives with one even from a BOM-less
    file — and `.strip()` does not remove it, so json failed at char 0."""
    assert ld.parse_records('﻿[{"kind":"defect"}]') == [{"kind": "defect"}]
    assert ld.parse_records('﻿{"kind":"defect"}') == [{"kind": "defect"}]


# --- log_defect: validate ---

def _valid_defect(**over):
    rec = {"kind": "defect", "target": "t.md", "cluster": "density-shortfall",
           "caught_at": "lint:source"}
    rec.update(over)
    return rec


def _valid_transition(**over):
    rec = {"kind": "transition", "cluster": "density-shortfall@desk",
           "surface": "layers/overview.md", "decision": "accept",
           "rationale": "held-in improved, no slice regressed",
           "model": "claude-sonnet-5", "treatment": "prevent"}
    rec.update(over)
    return rec


def test_validate_rejects_bad_kind_and_missing_keys():
    assert ld.validate({"kind": "nope"})
    assert ld.validate({"kind": "defect", "target": "x"})  # cluster / caught_at missing
    assert ld.validate(_valid_defect()) is None
    assert ld.validate(_valid_transition()) is None


def test_validate_enforces_cluster_slug():
    assert ld.validate(_valid_defect(cluster="Not A Slug"))
    assert ld.validate(_valid_transition(cluster="UPPER@desk"))
    assert ld.validate(_valid_transition(cluster="ok-slug@desk")) is None


def test_validate_enforces_decision_enum():
    assert ld.validate(_valid_transition(decision="approved"))
    for d in ld.DECISIONS:
        assert ld.validate(_valid_transition(decision=d)) is None


def test_validate_enforces_caught_at_stage():
    assert ld.validate(_valid_defect(caught_at="vibes:only"))
    for s in ld.STAGES:
        assert ld.validate(_valid_defect(caught_at=f"{s}:detail")) is None


def test_validate_requires_transition_audit_fields():
    assert ld.validate(_valid_transition(rationale=""))
    assert ld.validate(_valid_transition(model=""))


def test_append_fills_date_and_rejects_invalid(tmp_path):
    log = tmp_path / "_defect-log.jsonl"
    n = ld.append_records([_valid_defect()], path=log)
    assert n == 1
    rec = json.loads(log.read_text(encoding="utf-8").strip())
    assert rec["date"]  # auto-filled
    try:
        ld.append_records([{"kind": "defect"}], path=log)
        assert False, "invalid record passed validation"
    except ValueError:
        pass


def test_validate_requires_treatment_on_accept():
    """Without it `mine_failures` reads the accept as non-preventive and quietly drops
    the cluster out of the recurrence tier — so the judgment is forced at ingest."""
    rec = _valid_transition()
    del rec["treatment"]
    assert ld.validate(rec)
    assert ld.validate(_valid_transition(treatment="added a checker"))   # free text refused
    for tr in ("prevent", "detect", "both", "remediate"):
        assert ld.validate(_valid_transition(treatment=tr)) is None
    # reject and defer put nothing in place, so nothing is required of them
    r = _valid_transition(decision="reject")
    del r["treatment"]
    assert ld.validate(r) is None


def test_validate_enforces_severity_vocabulary():
    assert ld.validate(_valid_defect(severity="Medium"))
    assert ld.validate(_valid_defect(severity="med"))
    for s in ("critical", "high", "medium", "low"):
        assert ld.validate(_valid_defect(severity=s)) is None


def test_validate_enforces_layer_vocabulary():
    """Writing the content type into the layer slot was the real drift path, and the
    two tokens this repo used before (`guideline`/`meta`) each carried both prose and
    code — so the aggregate read a field that meant nothing."""
    assert ld.validate(_valid_defect(layer="source"))
    assert ld.validate(_valid_defect(layer="guideline"))
    for lay in ("L2-1", "L2-2", "L2-3", "L2-4", "meta", "tools"):
        assert ld.validate(_valid_defect(layer=lay)) is None


def test_validate_rejects_a_non_boolean_addressable():
    """A string passes the `is False` comparison, so "no" leaks in as addressable."""
    assert ld.validate(_valid_defect(addressable="yes"))
    assert ld.validate(_valid_defect(addressable="no"))
    for b in (True, False):
        assert ld.validate(_valid_defect(addressable=b)) is None



# --- mine_failures: cluster + priority ---

def _defect(cluster, caught_at="desk:density", target="t.md", date="2026-06-25", addressable=True):
    return {"kind": "defect", "cluster": cluster, "caught_at": caught_at,
            "target": target, "date": date, "addressable": addressable}


def test_recurring_after_fix_ranks_first():
    records = [
        _defect("translationese"), _defect("translationese"), _defect("translationese"),  # support 3, untreated
        _defect("density-shortfall"),                                      # support 1, recurring after fix
        _valid_transition(),
    ]
    a = mfa.analyze(records, since=None)
    # recurring-after-fix (density-shortfall) ranks ahead of translationese despite lower support
    assert a["ranked"][0][0] == "density-shortfall"
    assert "density-shortfall" in a["fixed"]


def test_legacy_mechanism_records_still_group():
    # Pre-schema records carry only free-text `mechanism` — grouping falls back.
    records = [{"kind": "defect", "mechanism": "translationese",
                "caught_at": "desk:density", "target": "t.md", "date": "2026-06-25"}]
    a = mfa.analyze(records, since=None)
    assert a["ranked"][0][0] == "translationese"


def test_addressable_false_is_separated():
    records = [_defect("source-thin", addressable=False), _defect("translationese")]
    a = mfa.analyze(records, since=None)
    assert "source-thin" in a["blocked"]
    assert all(m != "source-thin" for m, _ in a["ranked"])


def test_since_window_excludes_old():
    records = [_defect("old-one", date="2026-01-01"), _defect("recent-one", date="2026-06-25")]
    a = mfa.analyze(records, since="2026-03-01")
    mechs = {m for m, _ in a["ranked"]}
    assert mechs == {"recent-one"}


def test_pages_lists_all_targets():
    records = [_defect("dense", target=f"p{i}.md") for i in range(5)]
    capped = mfa.analyze(records, since=None)
    full = mfa.analyze(records, since=None, pages=True)
    assert len(dict(capped["ranked"])["dense"]["targets"]) == 3
    assert len(dict(full["ranked"])["dense"]["targets"]) == 5


def test_checkpoint_records_recurrence(tmp_path, monkeypatch):
    monkeypatch.setattr(mfa, "WATERMARK_PATH", tmp_path / "wm.json")
    entry = mfa.write_checkpoint("2026-06-25", None, "c1",
                                 {"density-shortfall": 1}, ["density-shortfall"])
    assert entry["recurring_after_fix"] == ["density-shortfall"]
    assert mfa.read_watermark() == "2026-06-25"


# --- mine_failures: the recurrence tier splits on treatment ---
# Counting every accept as a treatment pins a cluster at the top of the priority table
# for as long as its checker keeps working. Only prevention earns the tier.

def _accept(cluster, treatment, surface="tools/_lint/source.py"):
    return {"kind": "transition", "cluster": cluster, "surface": surface,
            "decision": "accept", "rationale": "r", "model": "m", "treatment": treatment}


def test_detector_only_accept_leaves_the_recurrence_tier():
    records = [
        _defect("detector-fixed"), _defect("detector-fixed"), _defect("detector-fixed"),
        _defect("prevention-fixed"),
        _accept("detector-fixed", "detect"),
        _accept("prevention-fixed", "prevent", ".claude/layers/hub.md"),
    ]
    a = mfa.analyze(records, since=None)
    assert a["non_preventive"] == {"detector-fixed"}
    assert a["recurred"] == {"prevention-fixed"}
    # support 1 beats support 3 — prevention-after-recurrence outranks a working checker
    assert a["ranked"][0][0] == "prevention-fixed"


def test_one_preventive_accept_is_enough_to_hold_the_tier():
    records = [_defect("mixed"),
               _accept("mixed", "detect"),
               _accept("mixed", "prevent", ".claude/agents/reporter.md")]
    a = mfa.analyze(records, since=None)
    assert a["non_preventive"] == set()
    assert "mixed" in a["recurred"]
