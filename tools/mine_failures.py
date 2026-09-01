#!/usr/bin/env python3
"""Aggregate the `tools/_defect-log.jsonl` corpus to surface recurring defects — the automatic defect channel.

Sibling of `mine_feedback.py` (the operator-utterance channel). The difference is the
input source — not human utterances, but verifier-grounded defects caught by lint/Desk
and ingested via `log_defect.py`. Being a prefilter, it prescribes nothing — it only
aggregates and prioritizes; which surface to fix is judged by the Editor-in-Chief who
reads it (the input to the SoT self-evolution workflow's § Propose, Input analysis).

Grouping key = `cluster` (the slugified mechanism-cluster join key shared with
transitions; legacy records without it fall back to `mechanism`). The same cluster is
broken out by caught_at stage — which rung it escaped from signals which surface is empty.

Priority = **recurrence after *preventive* treatment > support count**. A cluster that had
prevention put in place (`treatment` of `prevent`·`both`) and reappeared anyway is top
priority — that is a treatment failure. Counting every accept as a treatment is wrong:
a cluster accepted by adding a **checker** (`detect`) accumulates records because the
checker works, and one accepted by cleaning up instances (`remediate`) never had a
prevention. Both are held out of the recurrence tier and marked `▷unprev`.
Vocabulary SoT: `log_defect.py` TREATMENTS; the judgment is made by a human at ingest.

**A cluster carrying a closed verdict (`reject`·`defer`) drops to a lower tier.** `accept`
does not close one — a treatment's effect is still under observation and a recurrence
after it is this tool's top signal. The verdict is kept in the ledger (`latest_decisions`
below does not cut by window) but never reached the screen, so an axis already rejected or
deferred stood up as "top priority" every cycle: 6 of this corpus's clusters hold one. The
tier reads "judged", not "settled", because a bundle disposition can cover several clusters
at once — the marker states which proposal was judged, not that the cluster is finished.

Only the **latest** verdict counts. Picking any reject from the whole history hides a later
one — this corpus has a cluster accepted in August and rejected a week later, and another
deferred and then accepted, which an any-verdict read would get backwards in both
directions.

Support count measures **review effort, not defect rate** — a deeply reviewed batch takes
the ranking (this corpus runs 8 to 42 defects a week). Read a large support as "looked at
hard here" before reading it as "fails most here". The review window is managed by a
watermark (same design as `mine_feedback`) — `--checkpoint` advances the boundary and
records this cycle's cluster and recurrence history.

Defects ingested as `addressable:false` (source quality, contested topics, tool limits) are
surfaced separately as "won't patch" — to prevent guideline bloat.

Usage:
    python tools/mine_failures.py               # only after the watermark (or all if none)
    python tools/mine_failures.py --all         # full re-review
    python tools/mine_failures.py --since 2026-06-01
    python tools/mine_failures.py --checkpoint --note "..."   # confirm review complete
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _review  # noqa: E402  # shares the review-cycle watermark skeleton (isomorphic to mine_feedback)

LOG_PATH = Path(__file__).resolve().parent / "_defect-log.jsonl"
WATERMARK_PATH = Path(__file__).resolve().parent / "_failure-review.json"


def read_log(path: Path = LOG_PATH) -> list[dict]:
    """List of corpus records — skips broken lines. Empty list if none."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    out = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def read_watermark() -> str | None:
    return _review.read_watermark(WATERMARK_PATH)


def fixed_clusters(records: list[dict]) -> set[str]:
    """Set of clusters pointed to by accepted transitions — the recurrence criterion.

    transition.cluster has the form `slug` or `slug@stage` → take only the part before `@`.
    """
    return {str(r.get("cluster", "")).split("@")[0]
            for r in records
            if r.get("kind") == "transition" and r.get("decision") == "accept"}


# The re-open condition a verdict states in its own prose — picked up as a literal, no
# dedicated field. This corpus writes it as "Re-open when ..." in `note`; only 2 of the 6
# closed clusters carry one, and a field for that minority would drag a backfill of the
# rest behind it. Where it is absent, `surface` already says in one line which proposal
# was judged, which is what the marker exists to show.
_REOPEN_RE = re.compile(r"Re-open when\b[^\n]*")
_REOPEN_FIELDS = ("note", "rationale")


def latest_decisions(records: list[dict]) -> dict[str, dict]:
    """cluster → the **latest** transition record judging it.

    Several verdicts on one date: the one appended later wins (the ledger is append-only).
    """
    out: dict[str, dict] = {}
    for r in records:
        if r.get("kind") != "transition" or not r.get("decision"):
            continue
        c = str(r.get("cluster", "")).split("@")[0]
        if c not in out or str(r.get("date", "")) >= str(out[c].get("date", "")):
            out[c] = r
    return out


# Treatments that earn a place in the recurrence tier — only those that stop the defect
# from occurring. `detect` (a checker was added) makes what follows the checker working,
# and `remediate` (instances cleaned up) left no prevention behind at all.
_PREVENTIVE = ("prevent", "both")

# Verdicts that drop a cluster a tier — to pull one back up you have to refute the
# rationale standing in the ledger.
_CLOSED = ("reject", "defer")


def accept_clusters(records: list[dict], *treatments: str) -> set[str]:
    """Clusters of accept transitions carrying one of the given treatments."""
    return {str(r.get("cluster", "")).split("@")[0]
            for r in records
            if r.get("kind") == "transition" and r.get("decision") == "accept"
            and r.get("treatment") in treatments}


def analyze(records: list[dict], since: str | None, pages: bool = False):
    """Group defects by cluster, sorted by (recurrence after prevention, support).

    addressable=false is split out; a non-preventive accept (detect·remediate) is
    reported but held out of the recurrence tier. A cluster whose latest verdict is
    closed (reject·defer) sorts below every unjudged one, whatever its support.
    """
    fixed = fixed_clusters(records)
    recurred = accept_clusters(records, *_PREVENTIVE)   # prevented, and back anyway
    non_preventive = fixed - recurred
    judged = latest_decisions(records)                  # cluster → latest verdict record
    closed = {c for c, r in judged.items() if r.get("decision") in _CLOSED}
    clusters: dict[str, dict] = defaultdict(
        lambda: {"count": 0, "stages": Counter(), "targets": []})
    blocked: Counter = Counter()  # addressable=false mechanism → count
    in_window = 0
    for r in records:
        if r.get("kind") != "defect":
            continue
        if not _review.in_window(r.get("date"), since):
            continue
        in_window += 1
        mech = r.get("cluster") or r.get("mechanism") or "(unknown)"
        if r.get("addressable") is False:
            blocked[mech] += 1
            continue
        c = clusters[mech]
        c["count"] += 1
        c["stages"][str(r.get("caught_at", "?")).split(":")[0]] += 1
        if (pages or len(c["targets"]) < 3) and r.get("target"):
            c["targets"].append(r["target"])
    ranked = sorted(clusters.items(),
                    key=lambda kv: (kv[0] not in closed, kv[0] in recurred,
                                    kv[1]["count"]), reverse=True)
    return {"ranked": ranked, "blocked": blocked, "fixed": fixed,
            "judged": judged, "closed": closed,
            "recurred": recurred, "non_preventive": non_preventive,
            "in_window": in_window}


def write_checkpoint(when: str, since: str | None, note: str,
                     mechs: dict, recurring: list[str]) -> dict:
    """Advance the review boundary + append this cycle's cluster and recurrence history (to be committed to the repo)."""
    history = _review.load_history(WATERMARK_PATH)
    entry = {"checkpoint": when, "reviewed_since": since, "note": note,
             "cluster_counts": mechs, "cluster_total": sum(mechs.values()),
             "recurring_after_fix": recurring}
    history.append(entry)
    _review.write_review(WATERMARK_PATH, when, history)
    return entry


_DECISION_MARK = {"reject": "⊘rejected", "defer": "⏸deferred", "accept": "✓treated"}


def verdict_lines(r: dict) -> list[str]:
    """The verdict marker — `surface` (which proposal was judged) plus a re-open condition if stated."""
    mark = _DECISION_MARK.get(str(r.get("decision")), str(r.get("decision")))
    surface = str(r.get("surface") or "(surface unrecorded)").replace("\n", " ")
    when = str(r.get("date", "?"))
    stamp = "" if when in surface else f"{when} · "  # a bundle disposition dates its own surface
    out = [f"            {mark} {stamp}{surface[:76]}"]
    blob = " ".join(str(r.get(k) or "") for k in _REOPEN_FIELDS)
    m = _REOPEN_RE.search(blob)
    if m:
        out.append(f"            └ {m.group(0)[:88]}")
    return out


def mine(since: str | None, pages: bool = False) -> int:
    records = read_log()
    if not records:
        print(f"no defect corpus at {LOG_PATH} (no defects ingested yet — log_defect.py)",
              file=sys.stderr)
        return 1
    a = analyze(records, since, pages=pages)
    print(f"defect corpus: {LOG_PATH.name} ({sum(1 for r in records if r.get('kind')=='defect')} defect)")
    print(f"review window: {('after ' + since) if since else 'ALL (no watermark)'}")
    print(f"in-window defects: {a['in_window']}  ·  prevented clusters: {len(a['recurred'])}"
          f"  ·  non-preventive accepts: {len(a['non_preventive'])}")
    print()
    print("=== Open — this cycle's review set (recurrence after preventive treatment ▶ first) ===")
    if not a["ranked"]:
        print("  (no addressable defects in window)")
    elif all(mech in a["closed"] for mech, _ in a["ranked"]):
        print("  (none — every cluster in window holds a closed verdict)")
    tier_open = False
    for mech, c in a["ranked"]:
        if mech in a["closed"] and not tier_open:
            tier_open = True
            print()
            print("--- Judged — refute the ledger's rationale before re-deliberating the same proposal ---")
        flag = ("▶recur " if mech in a["recurred"]
                else "▷unprev" if mech in a["non_preventive"] else "       ")
        stages = " ".join(f"{s}:{n}" for s, n in c["stages"].most_common())
        print(f"  {flag} {c['count']:4d}  {mech}  [{stages}]")
        verdict = a["judged"].get(mech)
        if verdict:
            for line in verdict_lines(verdict):
                print(line)
        if mech not in a["closed"]:
            # Only closed clusters fold their target list away — they are not what you
            # are about to edit. Everything else keeps its examples.
            label = 'pages' if pages else 'e.g.'
            print(f"            {label}: {', '.join(c['targets'])}")
    if a["blocked"]:
        print()
        print("=== Won't patch (addressable=false — source quality, contested topics, tool limits) ===")
        for mech, n in a["blocked"].most_common():
            print(f"  {n:4d}  {mech}")
    print(f"\n[watermark] after review complete: python tools/mine_failures.py --checkpoint --note \"...\"")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--since", default=None, help="only defects after this date (YYYY-MM-DD) (ignores the watermark)")
    p.add_argument("--all", action="store_true", help="ignore the watermark and re-review everything")
    p.add_argument("--checkpoint", nargs="?", const="", default=None,
                   help="confirm review complete — advance the watermark to today (or a given YYYY-MM-DD)")
    p.add_argument("--note", default="", help="review note to record in the history on --checkpoint")
    p.add_argument("--pages", action="store_true", help="list every defect page per cluster (default: 3 examples)")
    args = p.parse_args()
    if args.checkpoint is not None:
        when = args.checkpoint or date.today().isoformat()
        prev = read_watermark()
        a = analyze(read_log(), prev)
        mechs = {m: c["count"] for m, c in a["ranked"]}
        # Non-preventive accepts are out — the history's "settling" trend must not be
        # polluted by a cluster whose records are a new checker doing its job.
        recurring = [m for m, _ in a["ranked"] if m in a["recurred"]]
        write_checkpoint(when, prev, args.note, mechs, recurring)
        print(f"[watermark] review complete confirmed: {when} → {WATERMARK_PATH.name} (to be committed to the repo)")
        if recurring:
            print(f"[self-improvement] {len(recurring)} mechanism(s) recurring after treatment: {', '.join(recurring)} "
                  f"(0 = settled)")
        return 0
    since = None if args.all else (args.since or read_watermark())
    return mine(since, pages=args.pages)


if __name__ == "__main__":
    raise SystemExit(main())
