#!/usr/bin/env python3
"""Append defect/transition records to the `tools/_defect-log.jsonl` corpus.

The ingest entry point for the automatic defect-to-guideline improvement loop (the
automatic channel of the SoT self-evolution workflow). At cycle close, the
Editor-in-Chief loads that cycle's lint FAILs + Desk actionable defects in one batch,
and records the accept/reject transitions of guideline edits into the same corpus. The
corpus must measure longitudinal recurrence rates across local and cloud, so it is
committed and machine-shared (the same category as `_feedback-review.json`; unlike
graph/_health-log.jsonl, it is not gitignored). `mine_failures.py` reads this corpus
in aggregate.

Why the ingest point is a single batch at the cycle gate rather than every lint run:
self-VERIFY₀ + VERIFY₁ + regression repetition double-counts the same FAIL and inflates
commit noise. One batch → low noise.

Two record kinds (`kind`):
- defect:     {date, layer, target, caught_at, check, mechanism, severity, addressable, run}
- transition: {date, cluster, surface, change, held_in_delta, held_out_delta, decision, commit,
               held_in_sampled, held_out_sampled}  # fresh-sampled page lists (audit · anti-cherry-pick)

caught_at has the form `<stage>:<detail>` (e.g. `lint:source`, `desk:density`) — the
leading segment (lint/desk) carries which rung of the verification ladder it escaped
from, signaling which surface is empty.

Usage:
    echo '{"kind":"defect","target":"...","mechanism":"...","caught_at":"lint:source"}' \
        | python tools/log_defect.py
    python tools/log_defect.py < records.json   # accepts either a JSON array or JSONL
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent / "_defect-log.jsonl"

# Required keys per kind — reject if missing (prevents a garbage corpus). Other keys are free.
REQUIRED = {
    "defect": ("target", "mechanism", "caught_at"),
    "transition": ("cluster", "surface", "decision"),
}


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
    for stream in (sys.stdin, sys.stdout):  # Windows defaults to cp949 → force UTF-8 so non-ASCII record text round-trips
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
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
