"""Produce the list of source slugs **scraped** in the previous (or specified) ISO week.

The weekly briefing's aggregation key is the **scrape time**, not the git-commit (ingest) time —
because ingest depends on when the batch runs and is therefore inaccurate. The authoritative
signal is **`scraped`** in each `wiki/sources/<slug>.md` frontmatter (the scrape date filled in
from raw `created` at ingest time). Everything is committed, so the cloud routine works
exhaustively without raw (independent of the `published` report date and the `last_updated`
edit date).

Usage:
    python tools/list_week_sources.py --week 2026-W23          # source slugs scraped that week
    python tools/list_week_sources.py --week 2026-W23 --json   # JSON array

Note (routine): if the cloud routine's TZ is UTC, the week number can drift around midnight, so
the routine passes an explicit `--week` converted to KST (the default depends on the local today).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
# _lib import also reconfigures stdout/stderr to UTF-8 (Windows cp949 console).
from _lib import WIKI, parse_frontmatter, real_source_files  # noqa: E402

_WEEK_RE = re.compile(r"^(\d{4})-[Ww](\d{1,2})$")


def parse_week(s: str) -> tuple[int, int]:
    m = _WEEK_RE.match(s.strip())
    if not m:
        raise ValueError(f"--week must be in 'YYYY-Www' format (e.g. 2026-W23): {s!r}")
    return int(m.group(1)), int(m.group(2))


def last_completed_week(today: date | None = None) -> tuple[int, int]:
    """Previous completed ISO week = the week of the 'most recent Sunday'. (If today is Monday, yesterday's Sunday.)"""
    today = today or date.today()
    last_sunday = today - timedelta(days=today.isoweekday())  # Mon(1) -> yesterday's Sunday
    iso = last_sunday.isocalendar()
    return iso[0], iso[1]


def _pd(val) -> date | None:
    if not isinstance(val, str) or len(val) < 10:
        return None
    try:
        return date.fromisoformat(val[:10])
    except ValueError:
        return None


def slugs_in_week(year: int, week: int) -> list[str]:
    """Sorted list of source slugs scraped in the (year, week) ISO week.

    Decided by each wiki/sources page's `scraped`. Pages without `scraped` are excluded + warned
    (after migration and new ingest all pages have it — a missing one signals incomplete authoring)."""
    out: list[str] = []
    for p in real_source_files():
        sc = _pd(parse_frontmatter(p.read_text(encoding="utf-8", errors="replace")).get("scraped"))
        if sc is None:
            print(f"[skip] no scraped: {p.stem}", file=sys.stderr)
            continue
        iso = sc.isocalendar()
        if (iso[0], iso[1]) == (year, week):
            out.append(p.stem)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="List source slugs scraped in a given ISO week")
    ap.add_argument("--week", type=str, help="ISO week 'YYYY-Www' (defaults to the previous completed week)")
    ap.add_argument("--json", action="store_true", help="output as a JSON array")
    # Compat: --slugs that past callers appended is now the default behavior, so it is ignored.
    ap.add_argument("--slugs", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()

    try:
        year, week = parse_week(args.week) if args.week else last_completed_week()
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    slugs = slugs_in_week(year, week)
    print(f"[{year}-W{week:02d}] {len(slugs)} scraped sources", file=sys.stderr)

    if args.json:
        print(json.dumps(slugs, ensure_ascii=False, indent=2))
    else:
        for s in slugs:
            print(s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
