#!/usr/bin/env python3
"""Append defect/transition records to the `tools/_defect-log.jsonl` corpus.

The ingest entry point for the automatic defect-to-guideline improvement loop (the
automatic channel of the SoT self-evolution workflow). At cycle close, the
Editor-in-Chief loads that cycle's escaped defects in one batch — which classes, and on
what trigger, is specified in `.claude/agents/editor-in-chief.md` — and records the
accept/reject transitions of guideline edits into the same corpus. The
corpus accumulates longitudinal recurrence rates; unlike the review watermarks
(`_feedback-review.json`, `_failure-review.json`) it is committed, so a fresh clone starts
with the recurrence history rather than blind. That makes it public — keep the free-text
fields (mechanism · rationale · note) technical English. `mine_failures.py` reads this
corpus in aggregate.

Why the ingest point is a single batch at the cycle gate rather than every lint run:
self-VERIFY₀ + VERIFY₁ + regression repetition double-counts the same FAIL and inflates
commit noise. One batch → low noise.

Two record kinds (`kind`):
- defect:     {date, layer, target, caught_at, check, cluster, mechanism, severity, addressable,
               grounded_at?, run}
- transition: {date, cluster, surface, change, held_in_delta, held_out_delta, decision,
               rationale, model, note, commit, held_in_sampled, held_out_sampled}
               # model = the measuring apparatus's model generation (MODELS — a join key)
               # note  = prose about the apparatus's composition (which role, how many rotations)

`cluster` is the slugified mechanism-cluster key (kebab-case; transitions may
suffix `@<stage>`) — the join key between defects, transitions, and the
mine_failures grouping. `mechanism` stays as an optional free-text label.
caught_at has the form `<stage>:<detail>` (e.g. `lint:source`, `desk:density`) —
the leading segment carries which verification surface caught it. Transition
`rationale` (one-line why) + `model` (the generation that produced the measured
output — MODELS vocabulary) make the accept/reject ledger auditable.

`grounded_at` is optional — the rung at which the authoring role stopped on the GROUND
Ladder (`R0`-`R4`; SoT is `.claude/agents/README.md` § GROUND Ladder). Validated for form
when present: a typo'd rung would silently corrupt the very distribution the field exists
to observe (which rung under-read defects concentrate at).

The two fields are the record's two coordinates in the four-loop model (CLAUDE.md § The
Four Loops): `grounded_at` is the input side (how deep the author read before writing),
`caught_at` the feedback side (the surface that caught it — `lint`·`desk` are the content
ladder's surfaces, spanning the inner and outer loops; `desk:bundle` is the Reground loop;
`blind`·`probe` the Meta loop's own verification).

`operator` is the wiki operator (CLAUDE.md § Human Reviewer Gate), a stopping condition
inside the other loops rather than a cycle of its own, so the mapping above gains no
entry for it. Use it for a defect the operator caught — at the gate or after everything
shipped — and not as a fallback when the catching surface is merely unclear: no
automated surface reports these, so a wrong value here has no correction path.

Usage:
    echo '{"kind":"defect","target":"...","cluster":"...","caught_at":"lint:source"}' \
        | python tools/log_defect.py
    python tools/log_defect.py < records.json   # accepts either a JSON array or JSONL
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

import _lib  # noqa: F401  # reconfigures stdout/stderr to UTF-8 (Windows cp949 console)

LOG_PATH = Path(__file__).resolve().parent / "_defect-log.jsonl"

# Required keys per kind — reject if missing (prevents a garbage corpus). Other keys are free.
REQUIRED = {
    "defect": ("target", "cluster", "caught_at"),
    "transition": ("cluster", "surface", "decision", "rationale", "model"),
}
# `cluster` join key: kebab-case slug; transitions may carry an `@<stage>` suffix.
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*(@[a-z0-9-]+)?$")
DECISIONS = ("accept", "reject", "defer")

# What an accept transition actually put in place — `mine_failures` splits its
# recurrence tier on this. Records that pile up after a new *checker* are that
# checker working, not a treatment failing, so tiering them with prevention-after-
# recurrence points the priority table at a solved problem.
#   prevent    a rule·gate·hook·code change stopped the defect from occurring
#   detect     a check·advisory was added or widened so it becomes visible
#   both       one treatment did both (a new rule plus its lint wiring)
#   remediate  only the existing instances were cleaned up — nothing prevents a repeat
# A field rather than a heuristic on `surface`: guessing from the path misreads a
# guideline SoT whose name contains `lint` as a checker.
TREATMENTS = ("prevent", "detect", "both", "remediate")

# Vocabularies for the optional grading fields. Without a check these split silently —
# a Korean or title-case severity, a content type written into the layer slot, a
# string `"no"` in a boolean field — and an aggregate that reads them just goes quiet.
SEVERITIES = ("critical", "high", "medium", "low")
# `meta` is the instruction prose (`.claude/**/*.md`, CLAUDE.md, README.md), `tools`
# everything executable or configured around it (tools/, hooks/, skill checks, repo
# config). Derive the value from the target, not from the topic: the two tokens this
# repo used before (`guideline` and `meta`) each carried both kinds — 19 of one pointed
# at code and 6 of the other at prose — so the field said nothing until it was pinned.
LAYERS = ("L2-1", "L2-2", "L2-3", "L2-4", "meta", "tools")
# The measuring apparatus's model generation. The self-evolution workflow hangs a
# longitudinal comparison on this field, which free text made impossible: 13 transitions
# carried 6 notations for 3 generations — `claude-opus-5[1m]` and `opus-5` split the same
# generation — and 5 of them held a whole sentence describing the apparatus rather than a
# generation. Composition prose (which role ran, how many rotations) belongs in `note`;
# this field is a join key. A measurement mixing families is `unknown` with the
# composition in `note` — guessing an attribution puts a wrong value in the key silently.
MODELS = ("opus-5", "opus-4.8", "fable-5", "sonnet-5", "haiku-4.5", "unknown")
# Verification surfaces a defect can escape from / be caught at (caught_at prefix).
# `operator` carries a narrow-use rule — read the module docstring before reaching for it.
STAGES = ("lint", "desk", "blind", "probe", "operator")


def parse_records(raw: str) -> list[dict]:
    """Parse the stdin body into a list of records — accepts either a JSON array or JSONL (one record per line)."""
    # A BOM is not whitespace, so `.strip()` leaves it and json fails at char 0.
    # Measured source on Windows: PowerShell prepends EF BB BF when piping to a
    # native command, so `Get-Content records.json -Raw | python tools/log_defect.py`
    # fails even though the file itself has no BOM (a Windows editor can also write
    # one directly). Stripped here rather than at the CLI so every caller is covered.
    raw = raw.lstrip("﻿").strip()
    if not raw:
        return []
    try:
        obj = json.loads(raw)
        return obj if isinstance(obj, list) else [obj]
    except json.JSONDecodeError:
        pass  # JSONL fallback
    out = []
    for i, line in enumerate(raw.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError as e:
            raise ValueError(f"line {i}: invalid JSON — {e}") from e
    return out


def validate(rec: dict) -> str | None:
    """Validate a single record — return a problem message (or None if valid)."""
    kind = rec.get("kind")
    if kind not in REQUIRED:
        return f"kind must be one of {sorted(REQUIRED)} (got {kind!r})"
    missing = [k for k in REQUIRED[kind] if not rec.get(k)]
    if missing:
        return f"{kind} missing required keys: {missing}"
    if not SLUG_RE.match(str(rec["cluster"])):
        return f"cluster must be a kebab-case slug (got {rec['cluster']!r})"
    if kind == "transition":
        if rec["decision"] not in DECISIONS:
            return f"decision must be one of {list(DECISIONS)} (got {rec['decision']!r})"
        # Required on accept only — reject and defer put nothing in place, so the
        # field has no value to carry.
        if rec["decision"] == "accept" and rec.get("treatment") not in TREATMENTS:
            return (f"an accept transition needs treatment as one of {list(TREATMENTS)} "
                    f"(got {rec.get('treatment')!r}) — input to the recurrence tier")
        if rec["model"] not in MODELS:
            return (f"model must be one of {list(MODELS)} (got {rec['model']!r}) — "
                    f"apparatus composition goes in note, a mixed family is unknown")
    if kind == "defect":
        stage = str(rec["caught_at"]).split(":")[0]
        if stage not in STAGES:
            return f"caught_at stage must be one of {list(STAGES)} (got {stage!r})"
        ga = rec.get("grounded_at")
        if ga is not None and not re.fullmatch(r"R[0-4]", str(ga)):
            return f"grounded_at must be of the form R0-R4 (got {ga!r})"
        # Optional fields, but a value that is present keeps to the vocabulary.
        sev = rec.get("severity")
        if sev is not None and sev not in SEVERITIES:
            return f"severity must be one of {list(SEVERITIES)} (got {sev!r})"
        lay = rec.get("layer")
        if lay is not None and lay not in LAYERS:
            return (f"layer must be one of {list(LAYERS)} (got {lay!r}) — the Layer slug, "
                    f"not the content type (source·hub·timeline)")
        adr = rec.get("addressable")
        if adr is not None and not isinstance(adr, bool):
            # A string passes the `is False` comparison, so "no" leaks in as addressable.
            return f"addressable must be a true/false boolean (got {adr!r})"
    return None


def append_records(records: list[dict], path: Path = LOG_PATH) -> int:
    """Append validated records to the corpus. Fill in today's date if missing. Return the number appended."""
    lines = []
    for rec in records:
        err = validate(rec)
        if err:
            raise ValueError(err)
        rec.setdefault("date", date.today().isoformat())
        lines.append(json.dumps(rec, ensure_ascii=False))
    if not lines:
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(lines) + "\n")
    return len(lines)


def main() -> int:
    # stdin is not covered by _lib's stdout/stderr reconfigure — force UTF-8
    # here so non-ASCII record text round-trips on a cp949 Windows console.
    if hasattr(sys.stdin, "reconfigure"):
        try:
            sys.stdin.reconfigure(encoding="utf-8")
        except Exception:
            pass
    try:
        records = parse_records(sys.stdin.read())
    except ValueError as e:
        print(f"ERROR: failed to parse stdin — {e}", file=sys.stderr)
        return 2
    if not records:
        print("ERROR: no records to ingest (stdin is empty)", file=sys.stderr)
        return 2
    try:
        n = append_records(records)
    except ValueError as e:
        print(f"ERROR: record validation failed — {e}", file=sys.stderr)
        return 2
    print(f"appended {n} record(s) → {LOG_PATH.name}")
    return 0


if __name__ == "__main__":
    _lib.reject_args(__doc__)
    raise SystemExit(main())
