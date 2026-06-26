"""Build knowledge graph from wiki pages.

Writes graph/_graph.json with EXTRACTED wikilink edges plus INFERRED
edges between pages sharing 3+ common link targets.

Wikilink targets are normalized to canonical node IDs at emit time via
_build_id_map — the raw `[[신한은행]]` text is resolved to
`entities/신한은행.md` so that downstream consumers (graph.html filter,
clusters.py, lint) can compare edge endpoints against node IDs directly.
Unresolvable targets (dangling refs) are counted and reported.

Root meta files (`wiki/overview.md`, `wiki/contradiction.md`,
`wiki/index.md`) are excluded as nodes — they are wiki-wide aggregation
files whose link profiles (overview.md alone has 657 outbound edges)
drown out structural signal in graph.html and pull every other node
toward themselves under FA2 layout. Their content is reachable through
the catalogs and the specific theme/overview pages they aggregate.
(log.md and lint-report.md live at the repo root, outside the walked
vault, so they are never scanned here.)

Each EXTRACTED edge carries a `relation` attribute. Phase 2(2026-05-02)
introduced **line-level citation type prefix** on `## Connections` items —
`cites:`/`references:`/`contradicts:`/`defines:` directly precede the
wikilink and override the section heuristic. When the prefix is absent
the section heuristic is applied as fallback. Four kinds:

  contradicts — `## Opposing Positions`, `## Derived Tensions & Generational Readings` (theme MDs),
                or any `## Connections` line starting with `contradicts:`
                (source-page contradiction relations live exclusively in
                `## Connections` `contradicts:` lines)
  cites       — sources/ `## Key Claims` · `## Key Quotes`,
                contradictions/ `## Representative Evidence`, any `## Sources` ·
                `## Source References`, or any `## Connections` line starting with `cites:`
  defines     — entities/ · concepts/ `## Overview`,
                or any `## Connections` line starting with `defines:`
  references  — default fallback (every other section, including
                `## Connections` lines starting with `references:` or no prefix)

EXTRACTED edges from `## Key Claims` claim lines additionally carry an
`evidence_grade` attribute (`fact`/`analysis`/`forecast`) when the line begins
with one of those markers — Phase 2 evidence grade primitive.

When the same target appears in multiple sections of one file, the
emitted edge keeps the highest-priority relation
(contradicts > defines > cites > references) so the structural signal
dominates over generic mentions. INFERRED edges have no relation field
(co-occurrence is not a typed relationship).
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import WIKI, atomic_write_if_changed, parse_frontmatter as _parse_fm, _build_id_map  # noqa: E402


ROOT_META = {
    "overview.md", "contradiction.md", "index.md",
}

# 2026-06-01 — graph nodes limited to the 3 substance types. The 5 meta
# page types (overview·contradiction·synthesis·timeline·trail) are no longer
# graph nodes; they are rendered as overlays (overview via the cluster
# legend, the other 4 via _overlays.json built by overlays.py). Excluding
# them here drops both their nodes and their meta→member edges from
# _graph.json. See ~/.claude/plans/meta-overlay-graph.md.
META_NODE_TYPES = {"overview", "contradiction", "synthesis", "timeline", "trail"}
BASE_NODE_TYPES = {"source", "entity", "concept"}


def _title_and_type(content: str) -> tuple[str, str]:
    fm = _parse_fm(content)
    return fm.get("title", ""), fm.get("type", "unknown")


# Wikilink with a trailing " — description" (or "--") on the same line.
_LABELED_LINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]\s*(?:—|--)\s*(.+?)(?:\n|$)")
# All wikilinks (used for the second dedup-aware pass).
_ANY_LINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")

# H2 section header at line start. Used to slice each file into
# (start, end, section_title) spans so each wikilink can be tagged with
# the relation_type implied by its enclosing section.
_H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)

# Priority order for resolving multiple sections referencing the same target
# within a single source file. Higher = wins.
RELATION_PRIORITY = {"contradicts": 4, "defines": 3, "cites": 2, "references": 1}

# Phase 2 — evidence_grade priority for per-target promotion. When the
# same target appears in multiple claim lines with different grades, the
# emitted edge keeps the highest-fidelity grade so structural signal
# (primary source > analysis > forecast) is preserved.
GRADE_PRIORITY = {"fact": 3, "analysis": 2, "forecast": 1}

# Phase 2 — line-level citation type prefix on `## Connections` items. Overrides
# section heuristic when present. Format: `- cites: [[Hub]] — ...` etc.
_CITATION_PREFIX_RE = re.compile(
    r"^\s*-\s*(cites|references|contradicts|defines)\s*:", re.MULTILINE
)

# Phase 2 — evidence grade marker on `## Key Claims` claim lines.
# Format: `- [fact] [[claimant]] — ...` / `[analysis]` / `[forecast]`.
_GRADE_MARKER_RE = re.compile(r"^\s*-\s*\[(fact|analysis|forecast)\]")


def _section_to_relation(rel: str, section_title: str) -> str:
    """Map (file path, H2 section title) → relation_type.

    `rel` is the wiki-relative path (e.g. "sources/foo.md") so we can
    apply file-type-conditional rules (e.g. `## Overview` is `defines` only
    in entities/concepts pages, otherwise `references`).
    """
    section = section_title.strip()
    # Theme MD contradiction-bearing sections (source pages emit contradicts
    # relations only via `## Connections` `contradicts:` lines parsed by
    # _CITATION_PREFIX_RE — this fallback is for theme MDs without the prefix).
    if any(k in section for k in ("Opposing Positions", "Derived Tensions")):
        return "contradicts"
    # Source page citation/quote sections.
    if rel.startswith("sources/") and section in ("Key Claims", "Key Quotes"):
        return "cites"
    # Contradiction theme evidence section.
    if rel.startswith("contradictions/") and section == "Representative Evidence":
        return "cites"
    # Source/reference list at any analytical page (overview, synthesis, trail).
    if section in ("Sources", "Source References"):
        return "cites"
    # Definition section only in entity/concept pages.
    if rel.startswith(("entities/", "concepts/")) and section == "Overview":
        return "defines"
    # Default — generic in-body reference.
    return "references"


def _section_spans(content: str, rel: str) -> list[tuple[int, int, str]]:
    """Slice content into (char_start, char_end, relation_type) spans by H2.

    Pre-section content (frontmatter, intro, H1) maps to the empty section
    title and resolves to "references" via _section_to_relation.
    """
    matches = list(_H2_RE.finditer(content))
    if not matches:
        return [(0, len(content), _section_to_relation(rel, ""))]
    spans: list[tuple[int, int, str]] = []
    if matches[0].start() > 0:
        spans.append((0, matches[0].start(), _section_to_relation(rel, "")))
    for i, m in enumerate(matches):
        title = m.group(1).strip()
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        spans.append((body_start, body_end, _section_to_relation(rel, title)))
    return spans


def _relation_at(spans: list[tuple[int, int, str]], pos: int) -> str:
    """Return the relation_type for the section containing char position `pos`."""
    for start, end, relation in spans:
        if start <= pos < end:
            return relation
    return "references"


def _line_at(content: str, pos: int) -> str:
    """Return the full line of text containing char position `pos`."""
    line_start = content.rfind("\n", 0, pos) + 1
    line_end = content.find("\n", pos)
    if line_end == -1:
        line_end = len(content)
    return content[line_start:line_end]


def _line_relation_override(line: str) -> str | None:
    """Phase 2 — if the line starts with `cites:`/`references:`/...,
    return that relation; else None."""
    m = _CITATION_PREFIX_RE.match(line)
    if m:
        return m.group(1)
    return None


def _line_grade(line: str) -> str | None:
    """Phase 2 — if the line starts with `[fact]`/`[analysis]`/`[forecast]`,
    return that grade; else None."""
    m = _GRADE_MARKER_RE.match(line)
    if m:
        return m.group(1)
    return None


def run() -> None:
    nodes: list[dict] = []
    file_contents: list[tuple[str, str]] = []  # (rel, content)

    # Pass 1 — collect all nodes so the id_map is complete before we
    # resolve any edge target (forward references are common in wikilinks).
    # Sort `dirs` and `files` in-place so the traversal order is reproducible
    # across runs (filesystem-native order is not stable). This makes every
    # downstream artefact (edge order in _graph.json, NetworkX neighbor
    # iteration in clusters.warm-start, INFERRED page-pair scan) deterministic.
    for root, dirs, files in os.walk(WIKI):
        dirs.sort()
        files.sort()
        for f in files:
            if not f.endswith(".md") or f.startswith("_"):
                continue
            fp = Path(root) / f
            if fp.parent == WIKI and f in ROOT_META:
                continue
            rel = str(fp.relative_to(WIKI)).replace("\\", "/")
            content = fp.read_text(encoding="utf-8", errors="replace")
            title, page_type = _title_and_type(content)
            # Meta page types are not graph nodes (rendered as overlays).
            # Skipping them from both `nodes` and `file_contents` drops their
            # nodes AND their meta→member edges in one move.
            if page_type in META_NODE_TYPES:
                continue
            if not title:
                title = f.replace(".md", "")
            nodes.append({"id": rel, "label": title, "type": page_type})
            file_contents.append((rel, content))

    id_map = _build_id_map(nodes)

    # Pass 2 — emit edges with canonical `to` IDs. Per-file seen set
    # avoids the prior O(N²) any()-scan across the growing global edges list.
    edges: list[dict] = []
    orphan_targets: Counter = Counter()

    for rel, content in file_contents:
        spans = _section_spans(content, rel)
        # target → {"relation": str, "label": str | None, "grade": str | None}.
        # Per file we keep at most one edge per (from, to); when the same target
        # appears in multiple sections we promote to the highest-priority
        # relation. Grade is attached when any matching line carries a marker.
        per_target: dict[str, dict] = {}

        def _resolve_relation(pos: int) -> str:
            """Phase 2 — line-level prefix overrides section heuristic."""
            line = _line_at(content, pos)
            override = _line_relation_override(line)
            if override is not None:
                return override
            return _relation_at(spans, pos)

        def _consider(target: str, relation: str, label: str | None, grade: str | None) -> None:
            existing = per_target.get(target)
            if existing is None:
                per_target[target] = {"relation": relation, "label": label, "grade": grade}
                return
            if RELATION_PRIORITY[relation] > RELATION_PRIORITY[existing["relation"]]:
                existing["relation"] = relation
            if label and not existing.get("label"):
                existing["label"] = label
            # Phase 2 — promote grade if the new claim line has higher
            # fidelity (fact > analysis > forecast). First-seen-wins fallback when
            # both are absent or equal-priority.
            if grade:
                current = existing.get("grade")
                if current is None or GRADE_PRIORITY[grade] > GRADE_PRIORITY[current]:
                    existing["grade"] = grade

        # Labeled wikilinks first — they carry useful hover text. Record each
        # link's `[[` offset so the generic pass below doesn't re-process the
        # very same link (both patterns start with `\[\[`, so m.start() aligns).
        # Without this a dangling labeled link inflates its orphan count by 2.
        labeled_spans: set[int] = set()
        for m in _LABELED_LINK_RE.finditer(content):
            labeled_spans.add(m.start())
            raw = m.group(1).strip()
            target = id_map.get(raw)
            if not target:
                orphan_targets[raw] += 1
                continue
            label = m.group(2).strip()[:80]
            line = _line_at(content, m.start())
            _consider(target, _resolve_relation(m.start()), label, _line_grade(line))

        # Generic wikilinks — keep the strongest relation seen so far. Skip any
        # link already handled by the labeled pass.
        for m in _ANY_LINK_RE.finditer(content):
            if m.start() in labeled_spans:
                continue
            raw = m.group(1).strip()
            target = id_map.get(raw)
            if not target:
                orphan_targets[raw] += 1
                continue
            line = _line_at(content, m.start())
            _consider(target, _resolve_relation(m.start()), None, _line_grade(line))

        for target, attrs in per_target.items():
            edge = {
                "from": rel,
                "to": target,
                "type": "EXTRACTED",
                "relation": attrs["relation"],
            }
            if attrs.get("label"):
                edge["label"] = attrs["label"]
            if attrs.get("grade"):
                edge["evidence_grade"] = attrs["grade"]
            edges.append(edge)

    # INFERRED edges — pages sharing 5+ common outbound targets.
    # Threshold raised from 3 to 5 on 2026-04-30 after audit found INFERRED
    # edges (15538) exceeded EXTRACTED (12713) and shared=3 alone produced
    # 9219 of those (59%). Adding 14 global-bank entities + 4 new concept
    # hubs in one ingest had inflated edges/node by 13.7% (13.57 → 15.43)
    # and re-shuffled Leiden communities 10 → 8. shared>=5 keeps only
    # high-signal recommendations and matches the existing confidence
    # ceiling at len(common)/5.0 = 1.0.
    #
    # Same-pair EXTRACTED suppression: if a typed EXTRACTED edge already
    # exists between the pair, the INFERRED co-occurrence signal is
    # redundant — the typed relation (contradicts/defines/cites/references)
    # is the stronger carrier. This extends the in-file relation-priority
    # principle (line 42-46 "highest-priority relation dominates over
    # generic mentions") to page-pair scope.
    extracted_pairs: set[tuple[str, str]] = set()
    for e in edges:
        extracted_pairs.add(tuple(sorted([e["from"], e["to"]])))

    page_links: dict[str, set[str]] = {}
    for e in edges:
        page_links.setdefault(e["from"], set()).add(e["to"])

    inferred: set[tuple[str, str]] = set()
    inferred_redundant_skipped = 0
    pages = list(page_links.keys())
    for i in range(len(pages)):
        for j in range(i + 1, len(pages)):
            common = page_links[pages[i]] & page_links[pages[j]]
            if len(common) >= 5:
                pair_key = tuple(sorted([pages[i], pages[j]]))
                if pair_key in extracted_pairs:
                    inferred_redundant_skipped += 1
                    continue
                confidence = min(1.0, len(common) / 5.0)
                key = (pages[i], pages[j])
                if key not in inferred:
                    inferred.add(key)
                    edges.append({
                        "from": pages[i],
                        "to": pages[j],
                        "type": "INFERRED",
                        "confidence": round(confidence, 2),
                        "shared": sorted(common)[:5],
                    })

    type_counts = Counter(n["type"] for n in nodes)
    edge_type_counts = Counter(e["type"] for e in edges)
    relation_counts = Counter(e["relation"] for e in edges if "relation" in e)
    target_counts = Counter(e["to"] for e in edges if e["type"] == "EXTRACTED")

    print(f"Nodes: {len(nodes)}")
    print(
        f"Edges: {len(edges)} "
        f"(EXTRACTED: {edge_type_counts.get('EXTRACTED', 0)}, "
        f"INFERRED: {edge_type_counts.get('INFERRED', 0)}, "
        f"INFERRED skipped as EXTRACTED-redundant: {inferred_redundant_skipped})"
    )
    if relation_counts:
        rel_summary = ", ".join(f"{r}: {c}" for r, c in relation_counts.most_common())
        print(f"  EXTRACTED relations — {rel_summary}")
    print("\nNode types:")
    for t, c in type_counts.most_common():
        print(f"  {t}: {c}")
    print("\nTop 20 hubs (inbound EXTRACTED links):")
    for name, cnt in target_counts.most_common(20):
        print(f"  {name}: {cnt}")

    if orphan_targets:
        total_orphans = sum(orphan_targets.values())
        print(
            f"\nUnresolved wikilink targets: {len(orphan_targets)} distinct, "
            f"{total_orphans} occurrences"
        )
        print("  Top 10 dangling refs (target: count):")
        for raw, cnt in orphan_targets.most_common(10):
            print(f"    {raw}: {cnt}")

    os.makedirs("graph", exist_ok=True)
    graph_data = {
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "extracted_edges": edge_type_counts.get("EXTRACTED", 0),
            "inferred_edges": edge_type_counts.get("INFERRED", 0),
            "relations": dict(relation_counts),
            "types": dict(type_counts),
        },
    }
    atomic_write_if_changed(
        Path("graph/_graph.json"),
        json.dumps(graph_data, ensure_ascii=False, indent=2),
    )
    print("\nWrote graph/_graph.json")
