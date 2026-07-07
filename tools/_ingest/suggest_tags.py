"""Suggest frontmatter `tags` candidates for source pages.

Companion to the T1 hard gate in `tools/_lint/source.py` (empty source
tags now FAIL lint). `tags` is a semantic field — it can't be auto-filled
— so this helper surfaces *candidates* derived from a source's `## Connections`
hub links (the connected entities/concepts are the natural thematic tags).
The reporter picks 4–6 from the candidates instead of leaving `tags: []`.

The deployed graph browser renders frontmatter tags as per-node meta
badges, so filled tags are real navigational value, not dead metadata.

Usage:
  python tools/_ingest/suggest_tags.py --file wiki/sources/xyz.md
  python tools/_ingest/suggest_tags.py            # scan all empty-tag sources
  python tools/_ingest/suggest_tags.py --json     # machine-readable

Exit codes:
  0 - no empty-tag sources found (or single file already tagged)
  1 - empty-tag source(s) surfaced with candidates
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))  # _ingest/ → tools/ root
from _lib import WIKI, WIKILINK_STEM_RE, parse_frontmatter  # noqa: E402

SOURCES = WIKI / "sources"
# `## Connections` block wikilink targets exclude source↔source links (lowercase
# kebab slugs like `nirs-innovation-isp`) — those aren't thematic tags.
SOURCE_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)+$")


def _connection_hubs(content: str) -> list[str]:
    """Ordered-unique hub names from the `## Connections` section."""
    m = re.search(r"^## Connections\s*$(.*?)(?=^## |\Z)", content, re.M | re.S)
    block = m.group(1) if m else ""
    out: list[str] = []
    for name in WIKILINK_STEM_RE.findall(block):
        name = name.strip()
        if not name or name == "index":
            continue
        if SOURCE_SLUG_RE.match(name):  # source↔source link, not a tag
            continue
        if name not in out:
            out.append(name)
    return out


def _is_empty_tags(content: str) -> bool:
    tags = parse_frontmatter(content).get("tags")
    return not (isinstance(tags, list) and any(str(t).strip() for t in tags))


def _suggest(path: Path) -> dict:
    content = path.read_text(encoding="utf-8", errors="replace")
    fm = parse_frontmatter(content)
    raw_title = fm.get("title", "")
    title = raw_title.strip() if isinstance(raw_title, str) else ""
    return {
        "slug": path.name[:-3],
        "title": title,
        "empty": _is_empty_tags(content),
        "candidates": _connection_hubs(content)[:8],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", type=str, help="Single source file (overrides scan)")
    ap.add_argument("--json", action="store_true", help="Machine-readable output")
    ap.add_argument(
        "--all", action="store_true",
        help="Include sources that already have tags (default: only empty)",
    )
    args = ap.parse_args()

    if args.file:
        path = Path(args.file)
        if not path.is_file():
            print(f"ERROR: not found: {path}", file=sys.stderr)
            return 2
        targets = [path]
    else:
        targets = [p for p in sorted(SOURCES.glob("*.md")) if not p.name.startswith("_")]

    rows = [_suggest(p) for p in targets]
    scanned = len(rows)
    if not args.all and not args.file:
        rows = [r for r in rows if r["empty"]]

    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 1 if any(r["empty"] for r in rows) else 0

    empty_rows = [r for r in rows if r["empty"]]
    if args.file:
        r = rows[0]
        status = "EMPTY — needs filling" if r["empty"] else "already filled"
        print(f"{r['slug']} ({status})")
        if r["candidates"]:
            print(f"  Candidate tags (connection hubs): {', '.join(r['candidates'])}")
            print(f"  → Recommend picking 4-6 + adding topic terms. e.g. tags: [{', '.join(r['candidates'][:5])}]")
        else:
            print("  No connection hubs — derive tags directly from the body topic.")
        return 1 if r["empty"] else 0

    if not empty_rows:
        print(f"OK — no empty-tag sources ({scanned} scanned).")
        return 0

    print(f"{len(empty_rows)} empty-tag source(s) — candidate tags (based on connection hubs):")
    for r in empty_rows:
        cand = ", ".join(r["candidates"]) if r["candidates"] else "(no connection hubs — derive from the body)"
        print(f"  {r['slug']}\n    candidates: {cand}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
