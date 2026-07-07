"""Build global wiki meta: wiki/index.md, _backlinks.json, _source_map.json.

After the Phase B pipeline refactor, catalog generation moved to
`tools/_build/clusters.py` (landscape axis ownership) and contradictions
JSON refresh runs as its own phase. This module is now lean — it only
produces the global drill-down meta files:

  - wiki/index.md              — 2-tier catalog (overview + contradictions
                                  links, cluster table, entity/concept/
                                  synthesis/trail/timeline listings)
  - wiki/sources/_source_map.json (URL-primary, path-fallback dedup keys
                                    for ingest)
  - wiki/_backlinks.json       — reverse-link index across wiki pages

Depends on graph/_clusters.json (for the cluster table row counts) and
expects wiki/sources/_catalog*.md files to already exist by the time this
runs (emitted by the preceding `clusters` pipeline phase).

Side effect on wiki/sources/<slug>.md: this phase also auto-fills the
`source_url:` frontmatter field when it is empty and the referenced raw
markdown file's frontmatter exposes a URL. This is the only build phase
that mutates editable (non-`_`-prefixed) wiki files, and it does so
narrowly — one frontmatter line, only when missing — to harden the
by_url dedup map against Obsidian re-scrape quirks (typographic-quote
filename variants leaving the original raw file as a 0-byte stub, which
breaks `_extract_raw_url` fallback). Once `source_url` is populated on
the wiki page, by_url stays valid even if the raw file later goes
0-byte.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import (  # noqa: E402
    WIKI as wiki,
    CLUSTERS_JSON,
    GRAPH_JSON,
    WIKILINK_STEM_RE,
    atomic_write_if_changed,
    atomic_write_text,
    graph_structure_fingerprint,
    normalize_quotes,
    parse_frontmatter,
    parse_page_meta,
    parse_source_alts,
    safe_link_text,
    title_sort_key,
)


def _sync_source_url(content: str, current_url: str, raw_url: str) -> tuple[str, str]:
    """Sync wiki source's `source_url:` frontmatter from the raw md URL.

    Returns (new_content, action). action ∈ {"added", "noop", "mismatch"}.

    - raw_url empty (raw missing/0-byte/no URL field) → noop, can't sync.
    - current_url present and equals raw_url → noop.
    - current_url present and differs → mismatch (advisory; do NOT overwrite,
      since the wiki frontmatter may be the canonical URL deliberately set
      against an AMP/redirect/utm raw variant).
    - current_url empty + raw_url found → insert `source_url:` line right
      after `source_file:` in frontmatter. If the file has an empty
      `source_url:` line (no value), replace it in place.
    """
    if not raw_url:
        return content, "noop"
    if current_url:
        return content, "noop" if current_url == raw_url else "mismatch"

    if not content.startswith("---"):
        return content, "noop"
    fm_end = content.find("\n---", 4)
    if fm_end == -1:
        return content, "noop"

    fm_block = content[4:fm_end]
    lines = fm_block.split("\n")
    new_line = f'source_url: "{raw_url}"'

    replaced = False
    for i, line in enumerate(lines):
        if re.match(r"^source_url:\s*$", line):
            lines[i] = new_line
            replaced = True
            break

    if not replaced:
        inserted = False
        for i, line in enumerate(lines):
            if line.startswith("source_file:"):
                lines.insert(i + 1, new_line)
                inserted = True
                break
        if not inserted:
            lines.append(new_line)

    new_fm = "\n".join(lines)
    new_content = content[:4] + new_fm + content[fm_end:]
    return new_content, "added"


def _extract_raw_url(raw_path: str) -> str | None:
    p = Path(raw_path)
    if not p.exists():
        return None
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    if text.startswith("---"):
        fm_end = text.find("\n---", 4)
        if fm_end != -1:
            fm = text[4:fm_end]
            for field in ("source", "url"):
                m = re.search(rf'^{field}:\s*["\']?([^"\'\n]+)', fm, re.MULTILINE | re.IGNORECASE)
                if m:
                    url = m.group(1).strip().rstrip('"').rstrip("'")
                    if url.startswith(("http://", "https://")):
                        return url

    m = re.search(r'\*\*URL:\*\*\s*(https?://\S+)', text, re.IGNORECASE)
    if m:
        return m.group(1).strip().rstrip(").,;")

    return None


def sync_source_urls() -> tuple[int, list[tuple[str, str, str]]]:
    """Backfill `source_url:` frontmatter on wiki/sources/*.md from raw md.

    Mutating side effect — the only place this build pipeline writes editable
    (non-`_`-prefixed) wiki content. Extracted from run() so the
    URL-sync responsibility is named separately from the meta-build
    responsibility (index.md / _source_map.json / _backlinks.json), which is
    a pure read-side derivation.

    Returns (added_count, mismatch_list). Idempotent: a second call after
    the first does nothing because every wiki source page now carries an
    explicit `source_url:` line.
    """
    sources_dir = wiki / "sources"
    if not sources_dir.exists():
        return 0, []
    added = 0
    mismatch: list[tuple[str, str, str]] = []
    for f in sorted(os.listdir(sources_dir)):
        if not f.endswith(".md") or f.startswith("_"):
            continue
        fp = sources_dir / f
        content = fp.read_text(encoding="utf-8", errors="replace")
        _title, _ptype, _desc, source_file, _date, source_url = parse_page_meta(content, f)
        if not source_file:
            continue
        raw_url = _extract_raw_url(source_file)
        new_content, action = _sync_source_url(content, source_url, raw_url or "")
        if action == "added":
            atomic_write_text(fp, new_content)
            added += 1
        elif action == "mismatch":
            mismatch.append((f.replace(".md", ""), source_url, raw_url or ""))
    return added, mismatch


def run() -> None:
    sections: dict[str, list] = {
        "sources": [], "entities": [], "concepts": [],
        "syntheses": [], "trails": [], "timelines": []
    }

    # Mutation phase — backfill source_url frontmatter before the read
    # passes below see the file contents. Kept inline so index meta-build
    # always observes a hardened by_url map.
    sync_added, sync_mismatch = sync_source_urls()

    sources_alts: dict[str, tuple[list[str], list[str]]] = {}
    for subdir in ["sources", "entities", "concepts", "syntheses", "trails", "timelines"]:
        d = wiki / subdir
        if not d.exists():
            continue
        for f in sorted(os.listdir(d)):
            if not f.endswith(".md") or f.startswith("_"):
                continue
            fp = d / f
            content = fp.read_text(encoding="utf-8", errors="replace")
            title, page_type, description, source_file, date, source_url = parse_page_meta(content, f)
            rel_path = f"{subdir}/{f}"

            sections[subdir].append((title, rel_path, description, source_file, date, source_url))
            if subdir == "sources":
                slug = f.replace(".md", "")
                alt_urls, alt_paths = parse_source_alts(content)
                if alt_urls or alt_paths:
                    sources_alts[slug] = (alt_urls, alt_paths)

    for _section in ("entities", "concepts", "syntheses", "trails", "timelines"):
        sections[_section].sort(key=title_sort_key)

    # Split syntheses into the timely stream (weekly briefings) and analytical
    # reports. The timely stream surfaces at the top as `## Recent Developments` (reverse-
    # chronological, newest week first), separate from evergreen analyses — the
    # Wikipedia ITN / Portal:Current events model for keeping recent items from
    # being buried among older reports. Capped so the recency channel itself
    # stays bounded as the weekly series grows.
    weekly = [s for s in sections["syntheses"] if Path(s[1]).stem.startswith("weekly-briefing-")]
    analyses = [s for s in sections["syntheses"] if not Path(s[1]).stem.startswith("weekly-briefing-")]
    weekly.sort(key=lambda s: Path(s[1]).stem, reverse=True)  # newest ISO week first

    clusters_path = CLUSTERS_JSON
    if not clusters_path.exists():
        raise SystemExit(
            "graph/_clusters.json not found. Run the pipeline in order:\n"
            "  python tools/build.py graph\n"
            "  python tools/build.py clusters"
        )

    clusters_data = json.loads(clusters_path.read_text(encoding="utf-8"))
    source_assignments = clusters_data.get("source_assignments", {})
    threshold = float(clusters_data.get("source_weight_threshold", 0.3))

    # Content-based staleness: compare the clustering-relevant fingerprint of
    # the current _graph.json against the one clusters recorded. mtime is
    # unreliable here — atomic_write_if_changed skips rewriting (no mtime bump)
    # when content is unchanged, so a label-only graph edit that leaves the
    # partition input untouched would falsely trip an mtime comparison.
    graph_json = GRAPH_JSON
    recorded_fp = clusters_data.get("graph_fingerprint")
    if graph_json.exists() and recorded_fp is not None:
        current_fp = graph_structure_fingerprint(
            json.loads(graph_json.read_text(encoding="utf-8"))
        )
        if current_fp != recorded_fp:
            print("WARNING: _clusters.json is stale (graph structure changed since last clustering). Run `python tools/build.py clusters` to refresh.")

    # Per-cluster source counts (for the index.md cluster table).
    # Source counted under every cluster with weight >= threshold (multi-listing).
    cluster_counts: dict[str, int] = {}
    for _path, entry in source_assignments.items():
        weights = entry.get("weights", {})
        matched = [slug for slug, w in weights.items() if w >= threshold]
        if not matched:
            matched = [entry["primary"]]
        for slug in matched:
            cluster_counts[slug] = cluster_counts.get(slug, 0) + 1

    # Ordered catalog table rows (size-desc via clusters[] order, dedup slug).
    catalog_rows: list[tuple[str, int, str]] = []
    seen_slugs: set[str] = set()
    for c in clusters_data.get("clusters", []):
        slug = c["slug"]
        if slug in seen_slugs:
            continue
        count = cluster_counts.get(slug, 0)
        if not count:
            continue
        seen_slugs.add(slug)
        catalog_rows.append((c["name"], count, f"_catalog-{slug}.md"))

    lines: list[str] = []
    lines.append("# Wiki Index\n")
    lines.append("This file is auto-generated and updated.\n")

    lines.append("## Overview")
    lines.append("- [Overview](overview.md) — wiki-wide view along the landscape axis")
    if (wiki / "contradiction.md").exists():
        prev_ct = wiki / "contradictions" / "_contradictions.json"
        n_ct = len(json.loads(prev_ct.read_text(encoding="utf-8"))) if prev_ct.exists() else 0
        n_str = f"{n_ct}" if n_ct else "all"
        lines.append(f"- [Contradiction Analysis](contradiction.md) — wiki-wide view along the conflict axis ({n_str} contradictions, drill down by theme)")
    lines.append("")

    # Timely stream — surfaced above the evergreen catalogs so recent items
    # are not buried. Reverse-chronological (newest week first), capped.
    if weekly:
        RECENT_CAP = 8
        shown = weekly[:RECENT_CAP]
        total = len(weekly)
        head = f"## Recent Developments ({total})" if total <= RECENT_CAP else f"## Recent Developments (latest {RECENT_CAP}/{total})"
        lines.append(head)
        lines.append(
            "Weekly briefing series — newest week at the top (recency channel). For evergreen "
            "field overviews see [Overview](overview.md) above; for in-depth analyses see the "
            "`## Analyses` section below.\n"
        )
        for title, path, desc, *_ in shown:
            title = safe_link_text(title)
            if desc:
                lines.append(f"- [{title}]({path}) — {desc}")
            else:
                lines.append(f"- [{title}]({path})")
        if total > RECENT_CAP:
            lines.append(f"- _For the {total - RECENT_CAP} earlier weekly briefings, see `wiki/syntheses/weekly-briefing-*`_")
        lines.append("")

    lines.append(f"## Sources ({len(sections['sources'])})")
    lines.append("For the full source list see the [source catalog](sources/_catalog.md), or browse by cluster:\n")
    lines.append("| Cluster | Count | Catalog |")
    lines.append("|----------|------|---------|")
    for name, count, cname in sorted(catalog_rows, key=lambda x: -x[1]):
        lines.append(f"| {name} | {count} | [{name} catalog](sources/{cname}) |")

    lines.append(f"\n## Entities ({len(sections['entities'])})")
    for title, path, desc, *_ in sections["entities"]:
        title = safe_link_text(title)
        if desc:
            lines.append(f"- [{title}]({path}) — {desc}")
        else:
            lines.append(f"- [{title}]({path})")

    lines.append(f"\n## Concepts ({len(sections['concepts'])})")
    for title, path, desc, *_ in sections["concepts"]:
        title = safe_link_text(title)
        if desc:
            lines.append(f"- [{title}]({path}) — {desc}")
        else:
            lines.append(f"- [{title}]({path})")

    lines.append(f"\n## Analyses ({len(analyses)})")
    for title, path, desc, *_ in analyses:
        title = safe_link_text(title)
        if desc:
            lines.append(f"- [{title}]({path}) — {desc}")
        else:
            lines.append(f"- [{title}]({path})")

    if sections["trails"]:
        lines.append(f"\n## Associative Trails ({len(sections['trails'])})")
        for title, path, desc, *_ in sections["trails"]:
            title = safe_link_text(title)
            if desc:
                lines.append(f"- [{title}]({path}) — {desc}")
            else:
                lines.append(f"- [{title}]({path})")

    if sections["timelines"]:
        lines.append(f"\n## Timelines ({len(sections['timelines'])})")
        for title, path, desc, *_ in sections["timelines"]:
            title = safe_link_text(title)
            if desc:
                lines.append(f"- [{title}]({path}) — {desc}")
            else:
                lines.append(f"- [{title}]({path})")

    output = "\n".join(lines) + "\n"
    atomic_write_if_changed(wiki / "index.md", output)

    by_url: dict[str, str] = {}
    by_path: dict[str, str] = {}
    missing_raw: list[tuple[str, str]] = []
    alt_url_count = 0
    alt_path_count = 0
    for title, rel_path, desc, source_file, date, source_url in sections["sources"]:
        if not source_file:
            continue
        slug = rel_path.replace("sources/", "").replace(".md", "")
        norm_path = normalize_quotes(source_file)
        by_path[norm_path] = slug
        # URL precedence:
        #   1. wiki source page's `source_url:` frontmatter (authoritative;
        #      used for PDFs and any page where raw file has no URL metadata)
        #   2. raw markdown file's `source:` / `url:` frontmatter (legacy HTML
        #      clippings scraped by Obsidian Web Clipper)
        url = source_url or _extract_raw_url(source_file)
        if url:
            by_url[url] = slug
        # Variant share-link / re-scrape paths. When the same article is fetched
        # via a different short URL or re-clipped to a different raw filename,
        # `source_url_alt` / `source_file_alt` accumulate on the canonical wiki
        # source page. Index every alt to the same slug so the next ingest of
        # that variant matches by_url (or by_path) instead of looking new.
        alt_urls, alt_paths = sources_alts.get(slug, ([], []))
        for alt_url in alt_urls:
            if alt_url and alt_url not in by_url:
                by_url[alt_url] = slug
                alt_url_count += 1
        for alt_path in alt_paths:
            if alt_path:
                norm_alt = normalize_quotes(alt_path)
                if norm_alt not in by_path:
                    by_path[norm_alt] = slug
                    alt_path_count += 1
        # Source-file existence check. A `source_file:` value pointing at a
        # missing raw file silently breaks ingest dedup (the path-fallback
        # lookup misses, the article looks new, a duplicate source page is
        # almost created). Surface as advisory; the deep audit + autofix
        # lives in `python tools/lint.py graph raw-files [--fix]`.
        if not (Path(source_file).is_file() or Path(norm_path).is_file()):
            missing_raw.append((slug, source_file))

    source_map = {"by_url": by_url, "by_path": by_path}
    map_path = wiki / "sources" / "_source_map.json"
    atomic_write_if_changed(map_path, json.dumps(source_map, ensure_ascii=False, indent=2))

    # 2026-06-01 — scan set limited to the 3 graph node types (source/entity/
    # concept), consistent with _graph.json. syntheses dropped: synthesis is
    # now an overlay (not a node), and its reverse-lookup is carried by
    # graph/_overlays.json node_overlays, not here. Measured impact: 0 hub
    # false-orphans (the 48 synthesis-only-backlink targets were 44 sources +
    # 4 contradictions, no entity/concept hub). See plan §5.
    backlinks: dict[str, list] = defaultdict(list)
    for subdir in ["sources", "entities", "concepts"]:
        d = wiki / subdir
        if not d.exists():
            continue
        for f in sorted(os.listdir(d)):
            if not f.endswith(".md") or f.startswith("_"):
                continue
            fp = d / f
            content = fp.read_text(encoding="utf-8", errors="replace")
            page_name = f.replace(".md", "")
            rel = f"{subdir}/{f}"
            # parse_frontmatter shares the canonical boundary (`find("\n---", 4)`)
            # — the previous split("---", 2) form mis-parsed values containing
            # a literal `---` (same trap parse_page_meta already fixed).
            fm_title = parse_frontmatter(content).get("title")
            pg_title = fm_title if isinstance(fm_title, str) and fm_title else page_name
            # Strip `#anchor` and `|alias` so [[Hub#section]] / [[Hub|alias]]
            # all key on the bare hub stem. Without `#` exclusion, anchored
            # references would scatter into separate `Hub#section` keys and
            # never aggregate to the hub itself, leaving real backlinks
            # invisible in the dedup map.
            for m in WIKILINK_STEM_RE.finditer(content):
                target = m.group(1).strip()
                if target != page_name:
                    backlinks[target].append({"from": rel, "title": pg_title})

    backlinks_dedup: dict[str, list] = {}
    for target, refs in backlinks.items():
        seen: set[str] = set()
        unique: list = []
        for r in refs:
            if r["from"] not in seen:
                seen.add(r["from"])
                unique.append(r)
        backlinks_dedup[target] = unique

    bl_path = wiki / "_backlinks.json"
    atomic_write_if_changed(bl_path, json.dumps(backlinks_dedup, ensure_ascii=False, indent=2))

    print(f"index.md: {len(sections['entities'])} entities, {len(sections['concepts'])} concepts, {len(sections['syntheses'])} syntheses")
    print(f"Cluster table: {len(catalog_rows)} rows, {len(sections['sources'])} total sources")
    alt_note = ""
    if alt_url_count or alt_path_count:
        alt_note = f" (alt: +{alt_url_count} url, +{alt_path_count} path)"
    print(f"Source map: {len(by_url)} by_url + {len(by_path)} by_path -> sources/_source_map.json{alt_note}")
    print(f"Backlinks: {len(backlinks_dedup)} targets -> _backlinks.json")
    if sync_added:
        print(f"source_url sync: {sync_added} added (frontmatter hardened against raw 0-byte)")
    if sync_mismatch:
        print(f"source_url sync: {len(sync_mismatch)} mismatch (advisory; not overwritten)")
        for slug, cur, raw in sync_mismatch[:5]:
            print(f"  - {slug}")
            print(f"      wiki: {cur}")
            print(f"      raw:  {raw}")
        if len(sync_mismatch) > 5:
            print(f"  ... and {len(sync_mismatch) - 5} more")
    if missing_raw:
        print(
            f"WARNING: {len(missing_raw)} source page(s) reference a raw file that does not exist on disk."
        )
        print(
            "  Run `python tools/lint.py graph raw-files` for the full report, "
            "`--fix` to repair auto-fixable cases."
        )
