#!/usr/bin/env python3
"""Append defect/transition records to the `tools/_defect-log.jsonl` corpus.

The ingest entry point for the automatic defect-to-guideline improvement loop (the
automatic channel of the SoT self-evolution workflow). At cycle close, the
Editor-in-Chief loads that cycle's lint FAILs + Desk actionable defects in one batch,
and records the accept/reject transitions of guideline edits into the same corpus. The
corpus accumulates longitudinal recurrence rates locally; it is gitignored operator-local
state (like `graph/_health-log.jsonl` and `_feedback-review.json`), so accumulated history
and any operator notes stay out of the public mirror. `mine_failures.py` reads this corpus
in aggregate.

Why the ingest point is a single batch at the cycle gate rather than every lint run:
self-VERIFY₀ + VERIFY₁ + regression repetition double-counts the same FAIL and inflates
commit noise. One batch → low noise.

Two record kinds (`kind`):
- defect:     {date, layer, target, caught_at, check, cluster, mechanism, severity, addressable, run}
- transition: {date, cluster, surface, change, held_in_delta, held_out_delta, decision,
               rationale, model, commit, held_in_sampled, held_out_sampled}

`cluster` is the slugified mechanism-cluster key (kebab-case; transitions may
suffix `@<stage>`) — the join key between defects, transitions, and the
mine_failures grouping. `mechanism` stays as an optional free-text label.
caught_at has the form `<stage>:<detail>` (e.g. `lint:source`, `desk:density`) —
the leading segment carries which verification surface caught it. Transition
`rationale` (one-line why) + `model` (which model produced the measured output)
make the accept/reject ledger auditable.

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
# Verification surfaces a defect can escape from / be caught at (caught_at prefix).
STAGES = ("lint", "desk", "blind", "probe")


def parse_records(raw: str) -> list[dict]:
    """Parse the stdin body into a list of records — accepts either a JSON array or JSONL (one record per line)."""
    raw = raw.strip()
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
    if kind == "transition" and rec["decision"] not in DECISIONS:
        return f"decision must be one of {list(DECISIONS)} (got {rec['decision']!r})"
    if kind == "defect":
        stage = str(rec["caught_at"]).split(":")[0]
        if stage not in STAGES:
            return f"caught_at stage must be one of {list(STAGES)} (got {stage!r})"
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
    raise SystemExit(main())
