#!/usr/bin/env python3
"""Count the number of 'real' sources and cluster distribution where a given name/term appears.

A raw `grep -rl <name> wiki/sources/` over-counts frequency because it includes
auto-generated files (`_catalog*.md`, `_source_map.json`) — the rationale being
the 2026-06-24 incident where a claimant tally inflated to 5 (including
3 from catalogs) and nearly led to a wrong call on creating an entity stub. This
tool excludes auto-generated files via `_lib.real_source_files()` and also shows
the primary cluster distribution via `graph/_clusters.json::source_assignments`,
turning the entity-stub threshold check (≥3 sources ∩ multi-cluster —
`feedback_no_single_source_stub`) into a tool. **For claimant/term frequency
calls, use this tool instead of a raw grep.**

Usage:
  python tools/count_mentions.py "Anthropic"
  python tools/count_mentions.py "Anthropic" --claimant   # only grade lines ([fact]/[analysis]/[forecast]), anywhere in the body
  python tools/count_mentions.py "Dario|Amodei"           # term is a regex (alias OR allowed)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import real_source_files, GRAPH  # noqa: E402

_GRADE_LINE = re.compile(r"^- \[(?:fact|analysis|forecast)\]")


def _source_clusters() -> dict:
    """sources/<slug>.md → primary cluster (graph/_clusters.json)."""
    try:
        sa = json.loads((GRAPH / "_clusters.json").read_text(encoding="utf-8")).get("source_assignments", {})
    except (OSError, ValueError):
        return {}
    return sa


def run(term: str, claimant_only: bool) -> int:
    try:
        pat = re.compile(term)
    except re.error as e:
        print(f"ERROR: term is not a valid regex — {e}", file=sys.stderr)
        return 2
    sa = _source_clusters()
    hits: list[tuple[str, str]] = []
    for fp in real_source_files():
        text = fp.read_text(encoding="utf-8", errors="replace")
        if claimant_only:
            matched = any(pat.search(ln) for ln in text.splitlines() if _GRADE_LINE.match(ln))
        else:
            matched = bool(pat.search(text))
        if matched:
            cluster = sa.get(f"sources/{fp.name}", {}).get("primary", "?")
            hits.append((fp.stem, cluster))

    clusters = sorted({c for _, c in hits})
    scope = " [claimant lines only]" if claimant_only else ""
    print(f"'{term}': {len(hits)} real source(s){scope}  (auto-generated `_` excluded)")
    for stem, c in sorted(hits):
        print(f"    {c:24} {stem}")
    print(f"  clusters: {len(clusters)} → {clusters}")
    meets = len(hits) >= 3 and len(clusters) >= 2
    print(f"  entity stub threshold (≥3 source ∩ ≥2 cluster): {'met' if meets else 'not met'} "
          f"(feedback_no_single_source_stub)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Tally name/term frequency and cluster distribution over real sources (auto-generated excluded)")
    ap.add_argument("term", help="name/term to search for (regex — aliases as `A|B`)")
    ap.add_argument("--claimant", action="store_true",
                    help="tally only the grade lines (`[fact]`/`[analysis]`/`[forecast]`), anywhere in the body")
    args = ap.parse_args()
    return run(args.term, args.claimant)


if __name__ == "__main__":
    raise SystemExit(main())
