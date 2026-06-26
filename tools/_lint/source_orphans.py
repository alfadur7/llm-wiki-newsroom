"""Detect source ↔ hub reference integrity issues (both directions).

(A) Orphan sources — a source page that no hub points to.
(B) Declared-but-absent sources — slugs in hub frontmatter with no matching
    file. Sub-classified by token-set Jaccard against existing source slugs:

      - HIGH (≥0.5) → auto-fixable typo: real source exists, the hub's
        slug is a paraphrase. With --fix the slug is renamed in-place
        (or just removed if the correct slug already coexists in the
        same hub's sources list — the typo+correct duplicate pattern).
      - LOW-HIGH (0.25-0.5) → SUGGESTION: best candidate listed for
        human review, not auto-applied. Synonym/transliteration typos
        (e.g. `bok-stablecoin-skepticism-shin` ↔
        `shinhhyunsong-stablecoin-bok`) land here because token overlap
        is incidental.
      - < LOW → NO MATCH: no plausible candidate. Either a planned
        source never ingested or a fabricated reference. Reported but
        not auto-removed (editorial decision).

With --fix:
  1. Sync each source's `## Connections` wikilinks into the referenced hub's
     `sources:` frontmatter (legacy tools/_backfill_source_slugs.py).
  2. Auto-correct HIGH-confidence typo slugs in hub frontmatter.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import (  # noqa: E402
    WIKI,
    FRONTMATTER_BLOCK_RE,
    WIKILINK_TARGET_RE as LINK_RE,
    parse_frontmatter,
    read_text_cached,
    real_source_files,
)

SRC = WIKI / "sources"

SOURCES_KEY_RE = re.compile(r"^sources:")
BLOCK_ITEM_RE = re.compile(r"^[ \t]*-\s+")
LAST_UPDATED_RE = re.compile(r"^(last_updated:\s*).*$", re.MULTILINE)
CONN_RE = re.compile(r"## Connections\n(.*?)(?=\n## |\Z)", re.DOTALL)

_SLUG_TOKEN_RE = re.compile(r"[-_]+")

# Token-set Jaccard thresholds for declared-but-absent slug correction.
# Slugs are kebab-case English keyword summaries; sibling-typo cases that
# share most domain terms reach 0.5+, while paraphrase/transliteration
# drift drops into the suggestion band where token overlap is incidental
# and the human reviewer must confirm.
_SLUG_FUZZY_HIGH = 0.5
_SLUG_FUZZY_LOW = 0.25


def _slug_tokens(slug: str) -> set[str]:
    return {t for t in _SLUG_TOKEN_RE.split(slug.lower()) if t}


def _best_slug_match(unknown: str, candidates: list[str]) -> tuple[str | None, float]:
    u = _slug_tokens(unknown)
    if not u:
        return None, 0.0
    best: str | None = None
    best_score = 0.0
    for c in candidates:
        ct = _slug_tokens(c)
        if not ct:
            continue
        score = len(u & ct) / len(u | ct)
        if score > best_score:
            best_score, best = score, c
    return best, best_score


def _hub_sources(text: str) -> list[str]:
    """Declared `sources:` slugs from a hub's frontmatter via the canonical
    parser, so inline (`[a, b]`) AND block (`- a` lines) forms both resolve.
    The previous inline-only reader silently saw a block-style list as empty,
    hiding those sources from detection (and risking corruption on rewrite)."""
    val = parse_frontmatter(text).get("sources")
    if isinstance(val, list):
        return [s for s in val if isinstance(s, str) and s]
    if isinstance(val, str) and val:
        return [val]
    return []


def _format_list(items: list[str]) -> str:
    if not items:
        return "[]"
    return "[" + ", ".join(items) + "]"


def _rewrite_sources(text: str, items: list[str], today: str) -> str:
    """Return `text` with its frontmatter `sources:` set to the inline list
    `items`, and `last_updated` bumped to `today` when that field exists.

    A block-style `sources:` (a `sources:` line followed by `- item` lines) is
    normalized to inline in place — the following block lines are consumed so
    the rewrite never leaves orphaned `- item` lines below an inline value.
    Returns `text` unchanged if there is no frontmatter to anchor on."""
    fm_match = FRONTMATTER_BLOCK_RE.match(text)
    if not fm_match:
        return text
    fm = fm_match.group(1)
    body = text[fm_match.end():]

    lines = fm.split("\n")
    out: list[str] = []
    i = 0
    replaced = False
    while i < len(lines):
        line = lines[i]
        if SOURCES_KEY_RE.match(line):
            i += 1
            while i < len(lines) and BLOCK_ITEM_RE.match(lines[i]):
                i += 1
            out.append("sources: " + _format_list(items))
            replaced = True
            continue
        out.append(line)
        i += 1
    if not replaced:
        if not items:
            # No existing `sources:` line and nothing to add — leave untouched
            # rather than append an empty `sources: []`.
            return text
        out.append("sources: " + _format_list(items))

    fm_new = "\n".join(out)
    if LAST_UPDATED_RE.search(fm_new):
        fm_new = LAST_UPDATED_RE.sub(f"\\g<1>{today}", fm_new)
    return f"---\n{fm_new}\n---\n{body}"


def _apply_backfill() -> int:
    """Sync each source's `## Connections` links into the referenced hub's
    frontmatter `sources:` list. Bumps `last_updated` on modified hubs.

    Returns the number of hub files updated.
    """
    hubs: dict[str, Path] = {}
    for subdir in ("entities", "concepts"):
        for p in (WIKI / subdir).glob("*.md"):
            if not p.name.startswith("_"):
                hubs[p.stem] = p

    additions: dict[str, list[str]] = defaultdict(list)
    for src in real_source_files():
        stem = src.stem
        text = read_text_cached(src)
        m = CONN_RE.search(text)
        if not m:
            continue
        links = {L.split("#", 1)[0].strip() for L in LINK_RE.findall(m.group(1))}
        for hub_name in links:
            if hub_name not in hubs:
                continue
            hub_text = read_text_cached(hubs[hub_name])
            existing = _hub_sources(hub_text)
            if stem not in existing:
                additions[hub_name].append(stem)

    if not additions:
        print("\n[--fix] Nothing to backfill; hub sources: frontmatter is already in sync.")
        return 0

    today = date.today().isoformat()
    for hub_name, new_slugs in additions.items():
        p = hubs[hub_name]
        text = read_text_cached(p)
        existing = _hub_sources(text)
        merged = existing + [s for s in new_slugs if s not in existing]
        p.write_text(_rewrite_sources(text, merged, today), encoding="utf-8")

    total = sum(len(v) for v in additions.values())
    print(f"\n[--fix] Updated {len(additions)} hub files "
          f"(+{total} source-slug entries). Run `python tools/build.py index` next.")
    return len(additions)


def _classify_declared_absent(
    declared_absent: list[str],
    declared_by: dict[str, list[str]],
    sources: set[str],
) -> tuple[list, list, list]:
    """Split declared-but-absent slugs into three buckets by best
    token-set Jaccard match against existing source slugs.

    Returns (fixable, suggestions, no_match):
      fixable    — [(typo_slug, target_slug, score, declared_by_pages)]
      suggestions — same shape, weak match band
      no_match   — [(typo_slug, declared_by_pages)]
    """
    candidates = sorted(sources)
    fixable: list[tuple[str, str, float, list[str]]] = []
    suggestions: list[tuple[str, str, float, list[str]]] = []
    no_match: list[tuple[str, list[str]]] = []

    for slug in declared_absent:
        target, score = _best_slug_match(slug, candidates)
        hubs = declared_by[slug]
        if target is not None and score >= _SLUG_FUZZY_HIGH:
            fixable.append((slug, target, score, hubs))
        elif target is not None and score >= _SLUG_FUZZY_LOW:
            suggestions.append((slug, target, score, hubs))
        else:
            no_match.append((slug, hubs))

    return fixable, suggestions, no_match


def _apply_typo_fixes(
    fixable: list[tuple[str, str, float, list[str]]],
) -> tuple[int, int]:
    """Apply HIGH-confidence slug renames in hub frontmatter `sources:`
    lists. If the target slug already coexists in the same hub (typo +
    correct duplicate pattern), the typo is simply removed.

    Returns (hubs_touched, slugs_fixed).
    """
    hub_paths: dict[str, Path] = {}
    for subdir in ("entities", "concepts", "syntheses", "trails", "timelines"):
        d = WIKI / subdir
        if not d.exists():
            continue
        for p in d.glob("*.md"):
            if not p.name.startswith("_"):
                hub_paths[f"{subdir}/{p.stem}"] = p

    today = date.today().isoformat()
    touched: set[str] = set()
    fixed_slugs: set[str] = set()
    for slug, target, _score, hubs in fixable:
        for page_id in hubs:
            p = hub_paths.get(page_id)
            if p is None:
                continue
            text = read_text_cached(p)
            items = _hub_sources(text)
            if slug not in items:
                continue
            if target in items:
                # Typo + correct duplicate — drop the typo only.
                items = [s for s in items if s != slug]
            else:
                items = [target if s == slug else s for s in items]
            p.write_text(_rewrite_sources(text, items, today), encoding="utf-8")
            touched.add(page_id)
            fixed_slugs.add(slug)

    # Count only slugs actually rewritten in ≥1 hub — a fixable entry whose
    # hub path is missing or whose slug is absent from the list is skipped,
    # so reporting len(fixable) would overcount.
    return len(touched), len(fixed_slugs)


def _apply_conn_source_backfill(conn_unregistered: dict[str, list[str]]) -> int:
    """Register each hub's own `## Connections` source links into its frontmatter
    `sources:` list. Returns the number of hub files updated."""
    hub_paths: dict[str, Path] = {}
    for subdir in ("entities", "concepts", "syntheses", "trails", "timelines"):
        d = WIKI / subdir
        if not d.exists():
            continue
        for p in d.glob("*.md"):
            if not p.name.startswith("_"):
                hub_paths[f"{subdir}/{p.stem}"] = p

    today = date.today().isoformat()
    touched = 0
    for page_id, new_slugs in conn_unregistered.items():
        p = hub_paths.get(page_id)
        if p is None:
            continue
        text = read_text_cached(p)
        existing = _hub_sources(text)
        merged = existing + [s for s in new_slugs if s not in existing]
        p.write_text(_rewrite_sources(text, merged, today), encoding="utf-8")
        touched += 1
    return touched


def run(*, json_out: bool = False, fix: bool = False) -> int:
    sources = {p.stem for p in real_source_files()}

    referenced: set[str] = set()
    declared_by: dict[str, list[str]] = {}
    conn_unregistered: dict[str, list[str]] = {}
    for subdir in ("entities", "concepts", "syntheses", "trails", "timelines"):
        d = WIKI / subdir
        if not d.exists():
            continue
        for p in d.glob("*.md"):
            if p.name.startswith("_"):
                continue
            text = read_text_cached(p)
            slugs = _hub_sources(text)
            referenced.update(slugs)
            page_id = f"{subdir}/{p.stem}"
            for slug in slugs:
                declared_by.setdefault(slug, []).append(page_id)
            # hub `## Connections` source link ⊆ frontmatter sources invariant —
            # hub.md "Source consistency". `## Connections` may contain source
            # links (hub.md "list of related hub/source links"), but a linked
            # source must also be registered in frontmatter sources so that
            # backlink/graph-edge consistency holds. Unregistered = consistency gap.
            cm = CONN_RE.search(text)
            if cm:
                conn_links = {L.split("#", 1)[0].strip() for L in LINK_RE.findall(cm.group(1))}
                conn_unreg = sorted((conn_links & sources) - set(slugs))
                if conn_unreg:
                    conn_unregistered[page_id] = conn_unreg

    wikilinked: set[str] = set()
    for p in WIKI.rglob("*.md"):
        if p.name.startswith("_"):
            continue
        text = read_text_cached(p)
        for m in LINK_RE.findall(text):
            wikilinked.add(m.split("#", 1)[0].strip())

    orphans = sorted(sources - referenced - wikilinked)

    hubs: set[str] = set()
    for subdir in ("entities", "concepts"):
        for p in (WIKI / subdir).glob("*.md"):
            if not p.name.startswith("_"):
                hubs.add(p.stem)

    recoverable: list[str] = []
    dead_end: list[str] = []
    for stem in orphans:
        text = read_text_cached(SRC / f"{stem}.md")
        m = CONN_RE.search(text)
        links = [L.split("#", 1)[0].strip() for L in LINK_RE.findall(m.group(1))] if m else []
        valid = [L for L in links if L in hubs]
        (recoverable if valid else dead_end).append(stem)

    declared_absent = sorted(
        (slug for slug in declared_by if slug not in sources),
        key=lambda s: -len(declared_by[s]),
    )

    fixable, suggestions, no_match = _classify_declared_absent(
        declared_absent, declared_by, sources
    )

    if json_out:
        print(json.dumps({
            "total_sources": len(sources),
            "orphans": len(orphans),
            "recoverable": recoverable,
            "dead_end": dead_end,
            "declared_absent": {
                "fixable": [
                    {"slug": s, "target": t, "score": round(sc, 3), "declared_by": h}
                    for s, t, sc, h in fixable
                ],
                "suggestions": [
                    {"slug": s, "target": t, "score": round(sc, 3), "declared_by": h}
                    for s, t, sc, h in suggestions
                ],
                "no_match": [
                    {"slug": s, "declared_by": h} for s, h in no_match
                ],
            },
        }, ensure_ascii=False, indent=2))
    else:
        print(f"Total sources: {len(sources)}")
        print(f"Orphan sources: {len(orphans)}")
        print(f"  Recoverable (run `python tools/lint.py graph orphans --fix`): {len(recoverable)}")
        print(f"  Dead-end (no usable `## Connections` links — manual attention): {len(dead_end)}")
        if dead_end:
            print("\nDead-end orphans:")
            for s in dead_end:
                print(f"  {s}")
        print(f"\nDeclared-but-absent sources: {len(declared_absent)}")
        print("  (slugs in some hub's `sources:` frontmatter with no matching file —")
        print("   typo on the hub OR genuinely planned but uningested source)")

        if fixable:
            label = "FIXED" if fix else "AUTO-FIXABLE"
            print(f"\n  [{label}: {len(fixable)}] (Jaccard ≥ {_SLUG_FUZZY_HIGH:.2f})")
            for slug, target, score, hubs in fixable[:30]:
                preview = ", ".join(hubs[:3])
                more = f" (+{len(hubs)-3})" if len(hubs) > 3 else ""
                print(f"    {slug} [score={score:.2f}]")
                print(f"      → {target}")
                print(f"      declared by {len(hubs)}: {preview}{more}")
            if len(fixable) > 30:
                print(f"    ... +{len(fixable)-30} more")

        if suggestions:
            print(
                f"\n  [SUGGESTION: {len(suggestions)}] "
                f"({_SLUG_FUZZY_LOW:.2f} ≤ Jaccard < {_SLUG_FUZZY_HIGH:.2f} — human review)"
            )
            for slug, target, score, hubs in suggestions[:30]:
                preview = ", ".join(hubs[:3])
                more = f" (+{len(hubs)-3})" if len(hubs) > 3 else ""
                print(f"    {slug} [score={score:.2f}]")
                print(f"      ?  {target}")
                print(f"      declared by {len(hubs)}: {preview}{more}")
            if len(suggestions) > 30:
                print(f"    ... +{len(suggestions)-30} more")

        if no_match:
            print(
                f"\n  [NO MATCH: {len(no_match)}] "
                f"(no plausible candidate — planned source or fabricated reference)"
            )
            for slug, hubs in no_match[:30]:
                preview = ", ".join(hubs[:3])
                more = f" (+{len(hubs)-3})" if len(hubs) > 3 else ""
                print(f"    {slug}  declared by {len(hubs)}: {preview}{more}")
            if len(no_match) > 30:
                print(f"    ... +{len(no_match)-30} more")

        n_conn = sum(len(v) for v in conn_unregistered.values())
        print(
            f"\nHub `## Connections` source links not in own frontmatter `sources:`: "
            f"{n_conn} across {len(conn_unregistered)} hub(s)"
        )
        print("  (`## Connections` may contain source links, but registering them in frontmatter sources is required — hub.md 'Source consistency')")
        if conn_unregistered:
            label = "FIXED" if fix else "AUTO-FIXABLE"
            print(f"  [{label}: {len(conn_unregistered)} hub]")
            for page_id, slugs in sorted(conn_unregistered.items(), key=lambda x: -len(x[1]))[:30]:
                print(f"    {page_id}: {len(slugs)} — {slugs[:5]}")

    if fix:
        _apply_backfill()
        if fixable:
            hubs_n, slugs_n = _apply_typo_fixes(fixable)
            print(
                f"\n[--fix] Auto-corrected {slugs_n} declared-absent slug(s) "
                f"across {hubs_n} hub file(s). Run `python tools/build.py index` next."
            )
        if conn_unregistered:
            n = _apply_conn_source_backfill(conn_unregistered)
            print(
                f"\n[--fix] Registered {sum(len(v) for v in conn_unregistered.values())} "
                f"`## Connections` source link(s) into {n} hub frontmatter(s). "
                f"Run `python tools/build.py index` next."
            )

    return 0 if (not orphans and not declared_absent and not conn_unregistered) else 1
