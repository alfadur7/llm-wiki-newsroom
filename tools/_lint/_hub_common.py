"""Shared helpers for the L2-2 hub triage advisories (promotion / demotion).

`hub_promotion.py` and `hub_demotion.py` are mirror-image triages over the
same frontmatter fields (`sources:`·`gate:`·`kind:`) and the same
graph/_graph.json + _clusters.json inbound/cluster model. The helpers below
were verbatim copies in both modules ("parity" by docstring); hoisting them
here makes that parity structural instead of remembered.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import FRONTMATTER_BLOCK_RE, WIKI, parse_frontmatter  # noqa: E402

ENTITIES_DIR = WIKI / "entities"
CONCEPTS_DIR = WIKI / "concepts"
HUB_SPECS = [(ENTITIES_DIR, "entities"), (CONCEPTS_DIR, "concepts")]

HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

_GRAPH_CACHE: dict | None = None


def iter_hub_files(directory: Path) -> list[Path]:
    """Sorted hub pages under `directory` (`*.md`, excluding `_`-prefixed auto-generated ones).

    The single SoT for the `_`-filter that the hub_* lint modules share across
    directory traversal and counting.
    """
    return sorted(p for p in directory.glob("*.md") if not p.name.startswith("_"))


def body_text(content: str) -> str:
    """Body text with frontmatter + HTML comments removed (length decisions use body_len)."""
    fm = FRONTMATTER_BLOCK_RE.match(content)
    body = content[fm.end():] if fm else content
    return HTML_COMMENT_RE.sub("", body)


def load_graph() -> dict:
    """graph/_graph.json + _clusters.json (lazy). Maps inbound froms and cluster."""
    global _GRAPH_CACHE
    if _GRAPH_CACHE is not None:
        return _GRAPH_CACHE
    base = WIKI.parent / "graph"
    inbound: dict[str, list[str]] = {}
    node_cluster: dict[str, str] = {}
    try:
        graph = json.loads((base / "_graph.json").read_text(encoding="utf-8"))
        for edge in graph.get("edges", []):
            tgt, src = edge.get("to"), edge.get("from")
            if tgt and src:
                inbound.setdefault(tgt, []).append(src)
    except (OSError, ValueError):
        pass
    try:
        clusters = json.loads((base / "_clusters.json").read_text(encoding="utf-8"))
        node_cluster.update(clusters.get("hub_assignments", {}))
        for node, assign in clusters.get("source_assignments", {}).items():
            if isinstance(assign, dict) and assign.get("primary"):
                node_cluster[node] = assign["primary"]
    except (OSError, ValueError):
        pass
    _GRAPH_CACHE = {"inbound": inbound, "cluster": node_cluster}
    return _GRAPH_CACHE


def body_len(content: str) -> int:
    return len(re.sub(r"\s", "", body_text(content)))


def gate(content: str) -> str | None:
    """frontmatter `gate:` value (full/delegated/absorbed) — a hub whose
    promotion triage was concluded by the Desk gate. Excluded from triage
    (removes repeated-surface noise).

    The three are the promotion triage's three terminal outcomes: `full`
    (full-hub authoring complete), `delegated` (delegated to an adjacent owner),
    `absorbed` (absorbed into a parent). In particular, `full` is attached
    regardless of body length — hub.md defines stub↔full by the cycle it passes
    through (columnist full authoring + Desk VERIFY), not by body length, so even
    a compact owner hub that has passed the cycle is promotion-complete.
    Body length is just a first-pass surfacing heuristic for un-gated hubs, not
    the decision criterion."""
    val = parse_frontmatter(content).get("gate")
    return val if val in ("full", "delegated", "absorbed") else None


def sources_count(content: str) -> int:
    sources = parse_frontmatter(content).get("sources") or []
    return len(sources) if isinstance(sources, list) else 0


def kind(content: str) -> str | None:
    """entity frontmatter `kind:` (person/org/product). naming.md classification convention."""
    return parse_frontmatter(content).get("kind")
