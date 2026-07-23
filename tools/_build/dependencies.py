"""Layer-cascade dependency index — `graph/_dependencies.json`.

The wiki is a dependency DAG: L1 raw → L2-1 source → L2-2 hub/timeline →
L2-3 overview/contradiction/synthesis/trail → L2-4 root. Each page derives
from the layer(s) below it. This phase computes, for every page, the set of
upstream pages it derives from plus the newest upstream timestamp — the data
a single uniform staleness rule consumes ("a page is stale if any upstream
changed after its own last_updated", `tools/_lint/staleness.py`).

This module is purely additive: it reads existing build outputs
(`_clusters.json`, `_contradictions*.json`) + page frontmatter and writes one
new JSON. It changes no existing behavior. The staleness rule it feeds is
**orthogonal to** (not a replacement for) the existing per-type checks — it
adds uniform upstream-content freshness across all types, while set-change
(overview AUTO-drift·contradiction claims-drift) and within-page metadata
hygiene (freshness) stay as separate signals (see `tools/_lint/staleness.py`).

Per-type upstream (the layer a page is built from):
  - source (L2-1)            → [] (L1 raw is external, not tracked)
  - entity/concept (L2-2)    → frontmatter `sources:` (L2-1 source slugs;
                                kept complete by source_orphans → hub sync)
  - timeline (L2-2)          → body wikilinks (the hubs/sources it chronicles;
                                timelines carry no `sources:` frontmatter and
                                are not reached by the source→hub sync, so the
                                body links are the only derivation signal)
  - synthesis (L2-3)         → frontmatter `sources:` (derives from L2-1 directly)
  - trail (L2-3)             → leading hub wikilink of each numbered `## Path` item (L2-2;
                                matches trail.py PATH_ITEM_LINKED_RE — inline explanatory
                                links inside an item's body are not path hops, so excluded)
  - overview/<cluster> (L2-3)→ that cluster's member hubs (_clusters.json members)
  - contradiction/<theme>    → claim sources (_contradictions_themes → _contradictions)
  - overview.md (L2-4 root)  → all overviews/*.md (L2-3)
  - contradiction.md (root)  → all contradictions/*.md (L2-3, non-`_`)

`last_updated` per page = frontmatter `last_updated` / `date` / (trail) `created`.
**Sources are the exception**: a source's stored date is its *content* date
(`scraped` / `published`), NOT its wiki-page `last_updated`. A source's
`last_updated` bumps on structural edits (Phase 2 schema migration, claimant
re-attribution, desk ADAPT) that introduce no new facts; keying upstream
staleness on it produced phantom staleness in every hub citing a re-edited
source. Sources are upstream-only (type=="source" → no upstream → never checked
as downstream), so this changes only how a source's date propagates to the hubs
that cite it. (2026-06-13 recalibration — 61% of stale flags traced to the
2026-05-03/04 Phase 2 migration cohort, whose articles were 2024 content.)
upstream_max_date = max content/last_updated among upstream. L2-4 root meta
files have no frontmatter `last_updated` (null) — out of staleness scope for now
(a git/log-based root timestamp is a future addition, not yet implemented).

**Hubs propagate a composite date.** As an *upstream* of derived pages
(overview·timeline·trail), an entity/concept hub contributes
max(its own `last_updated`, newest cited source content date) — not its
frontmatter date alone. A hub's `last_updated` is its narrative date and no
longer bumps on a pure `sources:` append (rule SoT: `.claude/layers/hub.md`),
so new-source arrival must reach the derived layer through the cited sources'
content dates, while a narrative rewrite still travels through `last_updated`.
A non-narrative hub edit moves neither date, so hub churn stops propagating
phantom staleness downstream. The hub's own record keeps `last_updated` = its
narrative date, which is the baseline for its own staleness against its sources.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import WIKI, WIKI_SUBDIRS, GRAPH, CLUSTERS_JSON, WIKILINK_RE, parse_frontmatter, strip_code, strip_frontmatter, atomic_write_if_changed, fm_sources  # noqa: E402

_GYEONGNO_RE = re.compile(r"^##\s+Path\s*$.*?(?=^##\s|\Z)", re.MULTILINE | re.DOTALL)


def _first_date(fm: dict, keys: tuple[str, ...]) -> str | None:
    """First frontmatter value among `keys` that parses as ISO YYYY-MM-DD."""
    for key in keys:
        v = fm.get(key)
        if v:
            m = re.match(r"\d{4}-\d{2}-\d{2}", str(v).strip())
            if m:
                return m.group(0)
    return None


def _page_date(fm: dict) -> str | None:
    """Frontmatter timestamp as ISO YYYY-MM-DD: last_updated (most types) or
    date (sources) or created (trails use created, not last_updated)."""
    return _first_date(fm, ("last_updated", "date", "created"))


def _source_content_date(fm: dict) -> str | None:
    """Content date for a source (L2-1): the article's capture/publication date
    (`scraped` → `published`), NOT the wiki-page `last_updated`. Falls back to
    `_page_date` only when both are absent (legacy/malformed source). See module
    docstring for why source `last_updated` must not drive upstream staleness."""
    return _first_date(fm, ("scraped", "published")) or _page_date(fm)


def _scan_pages() -> tuple[dict, dict]:
    """Walk wiki/ subdir pages once. Return (meta, stem_to_rel).

    meta[rel] = {"type", "last_updated", "sources"[], "body"} ; stem_to_rel
    maps every wikilink form (stem · subdir/stem.md) → rel for link resolution.
    """
    meta: dict = {}
    stem_to_rel: dict = {}
    for sub in WIKI_SUBDIRS:
        d = WIKI / sub
        if not d.is_dir():
            continue
        for fp in sorted(d.glob("*.md")):
            if fp.name.startswith("_"):
                continue
            rel = f"{sub}/{fp.name}"
            content = fp.read_text(encoding="utf-8", errors="replace")
            fm = parse_frontmatter(content)
            srcs = [s.strip("'\"").removesuffix(".md") for s in fm_sources(fm)]
            ptype = fm.get("type", "unknown")
            page_date = _source_content_date(fm) if ptype == "source" else _page_date(fm)
            meta[rel] = {
                "type": ptype,
                "last_updated": page_date,
                "sources": srcs,
                "body": strip_code(strip_frontmatter(content)),
            }
            stem = fp.name[:-3]
            stem_to_rel.setdefault(stem, rel)
            stem_to_rel.setdefault(rel, rel)
    return meta, stem_to_rel


def _source_rel(slug: str, stem_to_rel: dict) -> str | None:
    """Resolve a source slug to its sources/<slug>.md rel if it exists."""
    rel = f"sources/{slug}.md"
    return rel if rel in stem_to_rel or (WIKI / rel).is_file() else None


def _body_link_upstream(body: str, stem_to_rel: dict) -> list[str]:
    """Every wikilink in the body, resolved to rel paths (timeline: the
    hubs/sources it chronicles)."""
    out: list[str] = []
    for lm in WIKILINK_RE.finditer(body):
        target = stem_to_rel.get(lm.group(1).strip())
        if target and target not in out:
            out.append(target)
    return out


_PATH_ITEM_RE = re.compile(r"^\s*\d+\.\s")


def _trail_path_upstream(body: str, stem_to_rel: dict) -> list[str]:
    """Leading hub wikilink of each `## Path` numbered item — the path hops only.
    Mirrors trail.py PATH_ITEM_LINKED_RE: inline explanatory links inside an
    item's prose are NOT hops, so they are excluded (else an incidentally
    mentioned hub's date would falsely mark the trail stale)."""
    m = _GYEONGNO_RE.search(body)
    if not m:
        return []
    out: list[str] = []
    for line in m.group(0).splitlines():
        if not _PATH_ITEM_RE.match(line):
            continue
        lm = WIKILINK_RE.search(line)  # first wikilink on the item line = the hop
        if not lm:
            continue
        target = stem_to_rel.get(lm.group(1).strip())
        if target and target not in out:
            out.append(target)
    return out


def _load_json(path: Path) -> dict | list | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _hub_propagated(meta: dict, stem_to_rel: dict) -> dict[str, str | None]:
    """Composite upstream-propagation date per entity/concept hub — see the
    module docstring: max(narrative `last_updated`, newest cited source content
    date). This is only the date a hub contributes AS UPSTREAM; its own
    `deps[hub].last_updated` stays the narrative date."""
    out: dict[str, str | None] = {}
    for rel, m in meta.items():
        if m["type"] not in ("entity", "concept"):
            continue
        dates = [m["last_updated"]] if m["last_updated"] else []
        for s in m["sources"]:
            r = _source_rel(s, stem_to_rel)
            if r and r in meta and meta[r]["last_updated"]:
                dates.append(meta[r]["last_updated"])
        out[rel] = max(dates) if dates else None
    return out


def run() -> None:
    meta, stem_to_rel = _scan_pages()

    # Cluster members → overview upstream. clusters[i].members are rel paths.
    clusters = _load_json(CLUSTERS_JSON) or {}
    cluster_members: dict[str, list[str]] = {}
    for c in clusters.get("clusters", []):
        slug = c.get("slug")
        if slug:
            cluster_members[slug] = [m for m in c.get("members", []) if isinstance(m, str)]

    # Theme claim_ids → claim sources → contradiction-theme upstream.
    themes = (_load_json(WIKI / "contradictions" / "_contradictions_themes.json") or {}).get("themes", {})
    claims = _load_json(WIKI / "contradictions" / "_contradictions.json") or []
    claim_source: dict[str, str] = {}
    for cl in claims if isinstance(claims, list) else []:
        cid, src = cl.get("id"), cl.get("source")
        if cid and src:
            claim_source[cid] = src if src.startswith("sources/") else f"sources/{src}"

    deps: dict[str, dict] = {}
    propagated = _hub_propagated(meta, stem_to_rel)

    def _emit(rel: str, last_updated: str | None, upstream: list[str]) -> None:
        upstream = [u for u in upstream if u != rel]
        dates = [d for u in upstream if u in meta
                 if (d := propagated.get(u) or meta[u]["last_updated"])]
        deps[rel] = {
            "last_updated": last_updated,
            "upstream": upstream,
            "upstream_max_date": max(dates) if dates else None,
        }

    for rel, m in meta.items():
        t = m["type"]
        if t == "source":
            up: list[str] = []
        elif t in ("entity", "concept", "synthesis"):
            up = [r for s in m["sources"] if (r := _source_rel(s, stem_to_rel))]
        elif t == "timeline":
            up = _body_link_upstream(m["body"], stem_to_rel)
        elif t == "trail":
            up = _trail_path_upstream(m["body"], stem_to_rel)
        elif t == "overview":
            slug = rel.removeprefix("overviews/").removesuffix(".md")
            up = cluster_members.get(slug, [])
        elif t == "contradiction":
            slug = rel.removeprefix("contradictions/").removesuffix(".md")
            cids = themes.get(slug, {}).get("claim_ids", [])
            up = sorted({claim_source[c] for c in cids if c in claim_source})
        else:
            up = []
        _emit(rel, m["last_updated"], up)

    # L2-4 root meta files (no frontmatter → last_updated null; upstream = L2-3 axis).
    for root_name, axis_dir in (("overview.md", "overviews"), ("contradiction.md", "contradictions")):
        if not (WIKI / root_name).is_file():
            continue
        up = sorted(
            f"{axis_dir}/{p.name}" for p in (WIKI / axis_dir).glob("*.md") if not p.name.startswith("_")
        )
        _emit(root_name, None, up)

    out = {
        "_meta": {
            "phase": "dependencies",
            "note": "layer-cascade upstream index — page → {upstream pages it derives from, newest upstream date}. Consumed by tools/_lint/staleness.py (uniform staleness rule). Additive; no existing behavior changed.",
            "page_count": len(deps),
        },
        "pages": deps,
    }
    atomic_write_if_changed(GRAPH / "_dependencies.json", json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    stale_now = sum(
        1 for d in deps.values()
        if d["last_updated"] and d["upstream_max_date"] and d["upstream_max_date"] > d["last_updated"]
    )
    print(f"  graph/_dependencies.json — {len(deps)} pages indexed "
          f"({stale_now} with upstream newer than last_updated)")
