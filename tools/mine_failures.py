#!/usr/bin/env python3
"""Aggregate the `tools/_defect-log.jsonl` corpus to surface recurring defects — the automatic defect channel.

Sibling of `mine_feedback.py` (the operator-utterance channel). The difference is the
input source — not human utterances, but verifier-grounded defects caught by lint/Desk
and ingested via `log_defect.py`. Being a prefilter, it prescribes nothing — it only
aggregates and prioritizes; which surface to fix is judged by the Editor-in-Chief who
reads it (the stage-1 input of the SoT self-evolution workflow).

Grouping key = `mechanism` (an authoring-habit label). The same mechanism is broken out
by caught_at stage (lint/desk) — which rung it escaped from signals which surface is empty.

Priority = **recurrence after treatment > support count**. A mechanism that was fixed once
(an accept transition) yet reappeared is top priority (treatment failure). The review window
is managed by a watermark (same design as `mine_feedback`) — `--checkpoint` advances the
boundary and records this cycle's cluster and recurrence history.

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
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import _review  # shares the review-cycle watermark skeleton (isomorphic to mine_feedback)

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


def fixed_mechanisms(records: list[dict]) -> set[str]:
    """Set of mechanisms pointed to by accepted transitions — the recurrence criterion.

    transition.cluster has the form `mechanism` or `mechanism@stage` → take only the part before `@`.
    """
    return {str(r.get("cluster", "")).split("@")[0]
            for r in records
            if r.get("kind") == "transition" and r.get("decision") == "accept"}


def analyze(records: list[dict], since: str | None):
    """Group defects by mechanism, sorted by (recurrence, support). addressable=false is split out."""
    fixed = fixed_mechanisms(records)
    clusters: dict[str, dict] = defaultdict(
        lambda: {"count": 0, "stages": Counter(), "targets": [], "addressable": True})
    blocked: Counter = Counter()  # addressable=false mechanism → count
    in_window = 0
    for r in records:
        if r.get("kind") != "defect":
            continue
        if since and str(r.get("date", "")) <= since:
            continue
        in_window += 1
        mech = r.get("mechanism") or "(unknown)"
        if r.get("addressable") is False:
            blocked[mech] += 1
            continue
        c = clusters[mech]
        c["count"] += 1
        c["stages"][str(r.get("caught_at", "?")).split(":")[0]] += 1
        if len(c["targets"]) < 3 and r.get("target"):
            c["targets"].append(r["target"])
    ranked = sorted(clusters.items(),
                    key=lambda kv: (kv[0] in fixed, kv[1]["count"]), reverse=True)
    return {"ranked": ranked, "blocked": blocked, "fixed": fixed,
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


def mine(since: str | None) -> int:
    records = read_log()
    if not records:
        print(f"no defect corpus at {LOG_PATH} (no defects ingested yet — log_defect.py)",
              file=sys.stderr)
        return 1
    a = analyze(records, since)
    print(f"defect corpus: {LOG_PATH.name} ({sum(1 for r in records if r.get('kind')=='defect')} defect)")
    print(f"review window: {('after ' + since) if since else 'ALL (no watermark)'}")
    print(f"in-window defects: {a['in_window']}  ·  already-treated mechanisms: {len(a['fixed'])}")
    print()
    print("=== Recurring defects (recurrence after treatment ▶ first) ===")
    if not a["ranked"]:
        print("  (no addressable defects in window)")
    for mech, c in a["ranked"]:
        flag = "▶recur" if mech in a["fixed"] else "      "
        stages = " ".join(f"{s}:{n}" for s, n in c["stages"].most_common())
        print(f"  {flag} {c['count']:4d}  {mech}  [{stages}]")
        print(f"            e.g.: {', '.join(c['targets'])}")
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
    args = p.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if args.checkpoint is not None:
        when = args.checkpoint or date.today().isoformat()
        prev = read_watermark()
        a = analyze(read_log(), prev)
        mechs = {m: c["count"] for m, c in a["ranked"]}
        recurring = [m for m, _ in a["ranked"] if m in a["fixed"]]
        write_checkpoint(when, prev, args.note, mechs, recurring)
        print(f"[watermark] review complete confirmed: {when} → {WATERMARK_PATH.name} (to be committed to the repo)")
        if recurring:
            print(f"[self-improvement] {len(recurring)} mechanism(s) recurring after treatment: {', '.join(recurring)} "
                  f"(0 = settled)")
        return 0
    since = None if args.all else (args.since or read_watermark())
    return mine(since)


if __name__ == "__main__":
    raise SystemExit(main())
