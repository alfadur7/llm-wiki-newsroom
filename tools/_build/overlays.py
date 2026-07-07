"""Build graph/_overlays.json — meta-page overlay structures for graph.html.

The 5 meta page types are no longer graph nodes (graph.py limits nodes to
source/entity/concept). This module re-reads the meta pages and emits, per
overlay, the base-node members it spans plus order/flavor metadata, so
graph.html can render them as lenses over the base graph.

overview is NOT emitted here — it binds to the existing cluster legend/hull.
This module covers the other 4 types:
  - trail      → path  (ordered `## Path` items)
  - timeline   → path (source-indexed) | region (narrative) — classified per file
  - synthesis  → region (`## Connections`/`## Sources` wikilinks)
  - contradiction → region (theme claim source + contradicts target union)

Runs AFTER the contradictions phase: contradiction overlays read
wiki/contradictions/_contradictions_themes.json (built there). id_map is
rebuilt from graph/_graph.json (base nodes only) so meta wikilinks resolve
only to base nodes — meta→meta links are dropped, matching the graph.

Output graph/_overlays.json:
  { "overlays": [ {type, slug, title, flavor, members:[{id, order?, date?, note?}]} ],
    "node_overlays": { "<node id>": [ {type, slug, title} ] } }
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import GRAPH, GRAPH_JSON, TIMELINE_DATE_ONLY_RE, TIMELINE_ENTRY_RE, WIKI, WIKILINK_STEM_RE, atomic_write_if_changed, parse_frontmatter as _parse_fm, section_body, _build_id_map  # noqa: E402

CONTRA_CLAIMS = WIKI / "contradictions" / "_contradictions.json"
CONTRA_THEMES = WIKI / "contradictions" / "_contradictions_themes.json"

# other-fragmentary is a residual catch-all of unrelated claims — a region
# over it highlights a scattered, meaningless set, so it is excluded.
CONTRADICTION_SKIP = {"other-fragmentary"}

# A `## Opposing Positions` faction bullet: "- **Side A's position (…)**: … [[link]] …". Top-level
# bullets only (no leading indent) so nested detail lines aren't read as sides.
# Members are coloured per-faction in graph.html (not a sub-hull — factions
# overlap spatially under FA2, so colour+label distinguishes them, the hull
# stays single).
_SIDE_RE = re.compile(r"^-\s*\*\*(.+?)\*\*\s*:?\s*(.*)$", re.MULTILINE)

# All wikilinks — stem only, alias/anchor consumed (shared _lib definition).
_ANY_LINK_RE = WIKILINK_STEM_RE
# Trail `## Path` numbered item: "1. [[Hub]] — note".
_TRAIL_ITEM_RE = re.compile(
    r"^\s*\d+\.\s*\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]\s*(?:—|--)?\s*(.*)$", re.MULTILINE
)
# Timeline dated entry: "- **2026-04** ..." / "- ★ **2026-05-13** — ...".
_TL_ENTRY_RE = TIMELINE_ENTRY_RE
# A bold token that is a date — keeps the prescribed `**YYYY (planned)**`
# future anchor, rejects `## Flow Summary` range-label bullets ("2019~2021
# laying the groundwork"). Shared _lib definition so the timeline lint's
# path/region mirror cannot drift from this builder.
_DATE_ONLY_RE = TIMELINE_DATE_ONLY_RE


def _resolve(raw: str, id_map: dict[str, str]) -> str | None:
    return id_map.get(raw.strip())


def _is_source(nid: str) -> bool:
    return nid.startswith("sources/")


def _date_key(date_str: str) -> tuple[int, int, int]:
    nums = [int(x) for x in re.findall(r"\d+", date_str)]
    y = nums[0] if nums else 0
    mo = nums[1] if len(nums) > 1 else 0
    d = nums[2] if len(nums) > 2 else 0
    return (y, mo, d)


def _title_of(content: str, stem: str) -> str:
    return _parse_fm(content).get("title", "") or stem


def _meta_files(subdir: str) -> list[tuple[str, str]]:
    """(rel, content) for active meta pages in wiki/<subdir>/ (flat, skip
    `_`-prefixed files and the _archive subdir)."""
    d = WIKI / subdir
    out: list[tuple[str, str]] = []
    if not d.is_dir():
        return out
    for f in sorted(d.iterdir()):
        if f.is_dir() or not f.name.endswith(".md") or f.name.startswith("_"):
            continue
        rel = f"{subdir}/{f.name}"
        out.append((rel, f.read_text(encoding="utf-8", errors="replace")))
    return out


def _trail_overlay(rel: str, content: str, id_map: dict) -> dict | None:
    body = section_body(content, "Path")
    members = []
    order = 0
    for m in _TRAIL_ITEM_RE.finditer(body):
        nid = _resolve(m.group(1), id_map)
        if not nid:
            continue
        order += 1
        members.append({"id": nid, "order": order, "note": m.group(2).strip()[:200]})
    if not members:
        return None
    stem = rel.rsplit("/", 1)[-1].removesuffix(".md")
    return {"type": "trail", "slug": stem, "title": _title_of(content, stem),
            "flavor": "path", "members": members}


def _timeline_overlay(rel: str, content: str, id_map: dict) -> dict | None:
    stem = rel.rsplit("/", 1)[-1].removesuffix(".md")
    title = _title_of(content, stem)
    # Parse dated entries: collect (date_key, date_str, target_nid, type).
    entries = []
    src_n = hub_n = 0
    for m in _TL_ENTRY_RE.finditer(content):
        date_str, rest = m.group(1), m.group(2)
        if not _DATE_ONLY_RE.match(date_str):
            continue  # Flow Summary range label, not a dated entry
        lm = _ANY_LINK_RE.search(rest)
        nid = _resolve(lm.group(1), id_map) if lm else None
        if nid:
            if _is_source(nid):
                src_n += 1
            else:
                hub_n += 1
        entries.append((_date_key(date_str), date_str.strip(), nid))
    resolved = [(k, ds, nid) for (k, ds, nid) in entries if nid]
    base = {"type": "timeline", "slug": stem, "title": title}
    if resolved and src_n > hub_n:
        # source-indexed → path, chronological (oldest first).
        resolved.sort(key=lambda e: e[0])
        members = [{"id": nid, "order": i + 1, "date": ds}
                   for i, (_k, ds, nid) in enumerate(resolved)]
        return {**base, "flavor": "path", "members": members}
    # narrative → region (unique hub members). Fallback chain: dated-entry
    # hubs → Flow Summary hubs → full body (prose-only timelines like KB Kookmin Bank).
    seen: set = set()
    members: list = []
    for nid in (nid for (_k, _ds, nid) in resolved):
        if nid not in seen:
            seen.add(nid)
            members.append({"id": nid})
    if not members:
        _collect(section_body(content, "Flow Summary"), id_map, seen, members)
    if not members:
        _collect(content, id_map, seen, members)
    if not members:
        return None
    return {**base, "flavor": "region", "members": members}


def _collect(text: str, id_map: dict, seen: set, members: list) -> None:
    for m in _ANY_LINK_RE.finditer(text):
        nid = _resolve(m.group(1), id_map)
        if nid and nid not in seen:
            seen.add(nid)
            members.append({"id": nid})


def _synthesis_overlay(rel: str, content: str, id_map: dict) -> dict | None:
    # Synthesis pages are heterogeneous: essay-style carry `## Connections`/`## Sources`,
    # briefing-style carry a `sources:` frontmatter list + inline body links.
    # Union all three (frontmatter → sections → full-body fallback) so every
    # style resolves; meta-only pages (links all non-base) legitimately drop.
    seen: set = set()
    members: list = []
    for stem in _parse_fm(content).get("sources", []) or []:
        nid = _resolve(stem, id_map)
        if nid and nid not in seen:
            seen.add(nid)
            members.append({"id": nid})
    _collect(section_body(content, "Connections") + "\n" + section_body(content, "Sources"),
             id_map, seen, members)
    if not members:
        _collect(content, id_map, seen, members)  # briefing w/o sections
    if not members:
        return None
    stem = rel.rsplit("/", 1)[-1].removesuffix(".md")
    return {"type": "synthesis", "slug": stem, "title": _title_of(content, stem),
            "flavor": "region", "members": members}


def _contradiction_sides(content: str, id_map: dict) -> list[dict]:
    """Parse `## Opposing Positions` faction bullets into [{label, members:[id]}].

    Each top-level `- **<label>**: …` bullet is one faction; its wikilinks
    (resolved to base nodes) are its members. graph.html colours these nodes +
    labels per faction so the single region hull's members read as opposing
    camps. Returned only when ≥2 factions resolve members (else the single
    region stands alone)."""
    body = section_body(content, "Opposing Positions")
    if not body:
        return []
    sides = []
    for m in _SIDE_RE.finditer(body):
        label, line = m.group(1).strip(), m.group(0)
        seen, members = set(), []
        for lm in _ANY_LINK_RE.finditer(line):
            nid = _resolve(lm.group(1), id_map)
            if nid and nid not in seen:
                seen.add(nid)
                members.append(nid)
        if members:
            sides.append({"label": label, "members": members})
    return sides if len(sides) >= 2 else []


def _contradiction_overlays(id_map: dict) -> list[dict]:
    if not (CONTRA_THEMES.exists() and CONTRA_CLAIMS.exists()):
        return []
    themes = json.loads(CONTRA_THEMES.read_text(encoding="utf-8")).get("themes", {})
    claims = {c["id"]: c for c in json.loads(CONTRA_CLAIMS.read_text(encoding="utf-8"))}
    contra_dir = WIKI / "contradictions"
    overlays = []
    for slug, theme in themes.items():
        if slug in CONTRADICTION_SKIP:
            continue
        seen, members = set(), []
        for cid in theme.get("claim_ids", []):
            c = claims.get(cid)
            if not c:
                continue
            cands = [c.get("source", "")]
            lm = _ANY_LINK_RE.search(c.get("claim", ""))
            if lm:
                cands.append(lm.group(1))
            for raw in cands:
                nid = _resolve(raw, id_map)
                if nid and nid not in seen:
                    seen.add(nid)
                    members.append({"id": nid})
        # Faction split from the theme MD's `## Opposing Positions`. Side members union
        # into the region so the hull encloses them and the reverse map is
        # complete (faction links may name hubs the claims don't).
        md = contra_dir / f"{slug}.md"
        sides = _contradiction_sides(
            md.read_text(encoding="utf-8", errors="replace"), id_map
        ) if md.exists() else []
        for s in sides:
            for nid in s["members"]:
                if nid not in seen:
                    seen.add(nid)
                    members.append({"id": nid})
        if members:
            ov = {"type": "contradiction", "slug": slug,
                  "title": theme.get("name", slug),
                  "flavor": "region", "members": members}
            if sides:
                ov["sides"] = sides
            overlays.append(ov)
    return overlays


def run() -> None:
    if not GRAPH_JSON.exists():
        raise SystemExit("overlays.run: graph/_graph.json missing — run graph phase first.")
    nodes = json.loads(GRAPH_JSON.read_text(encoding="utf-8"))["nodes"]
    id_map = _build_id_map(nodes)

    overlays: list[dict] = []
    dropped: list[str] = []  # meta pages with no base-node members (surfaced, not silent)
    for subdir, fn in (("trails", _trail_overlay), ("timelines", _timeline_overlay),
                       ("syntheses", _synthesis_overlay)):
        for rel, content in _meta_files(subdir):
            ov = fn(rel, content, id_map)
            if ov:
                overlays.append(ov)
            else:
                dropped.append(rel)
    overlays.extend(_contradiction_overlays(id_map))

    # Reverse map: base node id → overlays it belongs to (node-info panel).
    node_overlays: dict[str, list[dict]] = {}
    for ov in overlays:
        ref = {"type": ov["type"], "slug": ov["slug"], "title": ov["title"]}
        for mem in ov["members"]:
            node_overlays.setdefault(mem["id"], []).append(ref)

    data = {"overlays": overlays, "node_overlays": node_overlays}
    atomic_write_if_changed(GRAPH / "_overlays.json",
                            json.dumps(data, ensure_ascii=False, indent=2))

    from collections import Counter
    by_type = Counter(ov["type"] for ov in overlays)
    by_flavor = Counter(ov["flavor"] for ov in overlays)
    print(f"_overlays.json — {len(overlays)} overlays "
          f"({dict(by_type)}, flavors {dict(by_flavor)}), "
          f"{len(node_overlays)} member nodes")
    if dropped:
        print(f"  dropped {len(dropped)} meta pages (no base-node members, "
              f"only meta/prose refs): {', '.join(dropped)}")


if __name__ == "__main__":
    run()
