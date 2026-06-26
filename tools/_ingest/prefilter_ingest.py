"""Classify raw files for ingest dedup.

Scans a raw folder and categorizes each file into one of:
  (a) URL-dup    — frontmatter URL matches `_source_map.json::by_url`
  (b) Path-dup   — file path matches `_source_map.json::by_path` (URL miss)
  (c) Genuine new — neither match, non-zero size, not under Raindrop legacy

Replaces the manual sweep that `/wiki-ingest <folder>` would otherwise have
Claude perform from scratch each time. Output is the deterministic answer
to "what's actually new in this folder?", which is what step 1 of the
ingest workflow needs.

Usage:
    python tools/_ingest/prefilter_ingest.py raw/NewsScrap
    python tools/_ingest/prefilter_ingest.py raw/PDF --json

Exit codes:
    0  always (informational tool; never blocks). Stats go to stdout.

Why URL-first: Obsidian Web Clipper re-scrapes the same URL into filename
variants (typographic quote drift, parenthesis position changes). The
scraped path differs but the URL is preserved, so by_url catches the dup
where by_path would miss. by_path is fallback for sources without URL
metadata (PDFs without raw md, AiChat-derived sources).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))  # _ingest/ → tools/ root (shared modules)
from _lib import WIKI, canonicalize_url, normalize_quotes, parse_frontmatter  # noqa: E402

EXCLUDE_SEGMENT = "/Raindrop/"
SCAN_EXTS = (".md", ".pdf")


def extract_url(raw_path: Path) -> str | None:
    """Read raw md frontmatter and return source/url/source_url, if any."""
    if raw_path.suffix.lower() != ".md":
        return None
    try:
        text = raw_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    # Reuse the canonical frontmatter parser (sibling suggest_links/suggest_tags
    # do the same) instead of a hand-rolled boundary + per-field regex. Keys are
    # matched case-insensitively: a few raw clippings capitalize `Source:`, and
    # parse_frontmatter is case-sensitive, so normalizing keys avoids missing a
    # capitalized key and re-ingesting that source as a false "genuine new".
    fm = parse_frontmatter(text)
    if not fm:
        return None
    fm_ci = {k.lower(): v for k, v in fm.items()}
    for field in ("source", "url", "source_url"):
        val = fm_ci.get(field)
        if isinstance(val, str) and val.startswith(("http://", "https://")):
            return val
    return None


def classify(folder: Path) -> dict:
    map_path = WIKI / "sources" / "_source_map.json"
    if not map_path.exists():
        raise SystemExit(
            f"ERROR: {map_path} not found. Run `python tools/build.py index` first."
        )
    sm = json.loads(map_path.read_text(encoding="utf-8"))
    by_url: dict = sm.get("by_url", {})
    by_path: dict = sm.get("by_path", {})
    # Canonical index catches re-scrape variants whose URL differs from a known
    # source only by tracking params (utm_*, fbclid). Built once; exact match wins.
    by_url_canon: dict = {canonicalize_url(k): v for k, v in by_url.items()}

    url_dup: list = []
    path_dup: list = []
    genuine_new: list = []
    skipped_empty: list = []
    skipped_excluded: list = []

    candidates: list[Path] = []
    for ext in SCAN_EXTS:
        candidates.extend(folder.rglob(f"*{ext}"))

    for f in sorted(candidates):
        rel = f.as_posix()

        if EXCLUDE_SEGMENT in rel:
            skipped_excluded.append(rel)
            continue

        # The `_` prefix marks auto-managed meta files (e.g. raw/_inbox.md,
        # raw/_archive.md). These are operational queue files, not ingest
        # candidates, so exclude them from classification.
        if f.name.startswith("_"):
            skipped_excluded.append(rel)
            continue

        try:
            size = f.stat().st_size
        except OSError:
            continue
        if size == 0:
            skipped_empty.append(rel)
            continue

        url = extract_url(f)
        if url and url in by_url:
            url_dup.append({"path": rel, "url": url, "slug": by_url[url]})
            continue
        if url and canonicalize_url(url) in by_url_canon:
            url_dup.append(
                {"path": rel, "url": url, "slug": by_url_canon[canonicalize_url(url)]}
            )
            continue

        norm = normalize_quotes(rel)
        if norm in by_path:
            path_dup.append({"path": rel, "slug": by_path[norm]})
            continue

        genuine_new.append({"path": rel, "url": url, "size": size})

    return {
        "folder": folder.as_posix(),
        "stats": {
            "total_scanned": len(candidates),
            "url_dup": len(url_dup),
            "path_dup": len(path_dup),
            "genuine_new": len(genuine_new),
            "skipped_empty": len(skipped_empty),
            "skipped_excluded": len(skipped_excluded),
        },
        "genuine_new": genuine_new,
        "url_dup": url_dup,
        "path_dup": path_dup,
        "skipped_empty": skipped_empty,
        "skipped_excluded": skipped_excluded,
    }


def render_markdown(result: dict, verbose: bool = False) -> str:
    s = result["stats"]
    lines = [
        f"=== ingest prefilter: {result['folder']} ===",
        "",
        f"Scanned:     {s['total_scanned']:>5} files (.md + .pdf)",
        f"  URL-dup:     {s['url_dup']:>5}  (already in _source_map.by_url)",
        f"  Path-dup:    {s['path_dup']:>5}  (already in _source_map.by_path)",
        f"  Empty:       {s['skipped_empty']:>5}  (0 bytes, skipped)",
        f"  Excluded:    {s['skipped_excluded']:>5}  (Raindrop legacy, skipped)",
        f"  Genuine new: {s['genuine_new']:>5}",
        "",
    ]

    if result["genuine_new"]:
        lines.append(f"--- Genuine new ({len(result['genuine_new'])}) ---")
        for item in result["genuine_new"]:
            url_part = f"  url: {item['url']}" if item["url"] else "  url: (none)"
            lines.append(f"- {item['path']}")
            lines.append(f"  {url_part}")
        lines.append("")
    else:
        lines.append("No genuine new candidates — all files match existing sources.")
        lines.append("")

    if verbose and result["path_dup"]:
        lines.append(f"--- Path-dup ({len(result['path_dup'])}, URL miss but path known) ---")
        for item in result["path_dup"]:
            lines.append(f"- {item['path']}  → {item['slug']}")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Classify raw files for ingest dedup (URL-first prefilter)."
    )
    ap.add_argument("folder", help="raw folder path (e.g., raw/NewsScrap, raw/PDF)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    ap.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="markdown output: also list path-dup entries (default: counts only)",
    )
    args = ap.parse_args()

    folder = Path(args.folder)
    if not folder.is_dir():
        print(f"ERROR: {folder} is not a directory", file=sys.stderr)
        return 2

    result = classify(folder)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(result, verbose=args.verbose))
    return 0


if __name__ == "__main__":
    sys.exit(main())
