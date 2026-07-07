"""Graph traversal handlers for `tools/query.py graph ...`.

Registered as the `graph` subcommand group of the top-level query dispatcher.
Queries the persistent graph (graph/_graph.json) and cluster assignments
(graph/_clusters.json) to answer focused structural questions without
spinning up the full Claude synthesis
pipeline. Each subcommand returns a compact, budget-aware report that an
LLM can consume efficiently.

Node names accept any of these forms and resolve to the canonical node id:
  Meta, Meta.md, entities/Meta.md
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))  # _query/ → tools/ root (shared modules)
# _lib import also reconfigures stdout/stderr to UTF-8 (Windows cp949 console).
from _lib import CLUSTERS_JSON, GRAPH_JSON, _build_id_map  # noqa: E402

GRAPH_PATH = GRAPH_JSON
CLUSTERS_PATH = CLUSTERS_JSON

DEFAULT_BUDGET = 60

# Hyper-G typed edge relations (2026-05-02). EXTRACTED edges carry one of
# these in their `relation` field; INFERRED edges have no relation.
RELATION_KINDS = {"contradicts", "defines", "cites", "references"}


def _parse_edge_filter(spec: str | None) -> set[str] | None:
    """Parse a comma-separated --edge-type spec into a normalized filter set.

    Accepted tokens: contradicts, defines, cites, references, inferred.
    `None` (no filter) → traverse every edge. Returning an empty set is not
    valid — every spec must include at least one accepted kind.
    """
    if not spec:
        return None
    allowed = RELATION_KINDS | {"inferred"}
    requested = {t.strip().lower() for t in spec.split(",") if t.strip()}
    invalid = requested - allowed
    if invalid:
        raise SystemExit(
            f"Unknown --edge-type token(s): {', '.join(sorted(invalid))}. "
            f"Allowed: {', '.join(sorted(allowed))}."
        )
    return requested


def _edge_passes_filter(edge: dict, allowed: set[str] | None) -> bool:
    """True if `edge` is kept under the current --edge-type filter."""
    if allowed is None:
        return True
    if edge.get("type") == "INFERRED":
        return "inferred" in allowed
    return edge.get("relation", "references") in allowed


def _load(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"{path} not found. Run `python tools/build.py` first.")
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(name: str, id_map: dict[str, str]) -> str:
    if name in id_map:
        return id_map[name]
    raise SystemExit(
        f"Node not found: {name!r}\n"
        f"Try a stem like 'Meta' or full id like 'entities/Meta.md'."
    )


def _build_nx_graph(
    nodes: list[dict], edges: list[dict], id_map: dict[str, str],
    edge_filter: set[str] | None = None,
):
    """Build an undirected weighted NetworkX graph with rationale on edges.

    Edge cost (Dijkstra distance, lower = closer):
      EXTRACTED  : cost 1.0    (explicit wikilink, ground truth)
      INFERRED   : cost 2.0 / confidence  (uncertain, penalized vs explicit)

    `edge_filter` (when provided) restricts which relation kinds traverse —
    used by `--edge-type contradicts` etc. to ask "shortest path among
    contradiction-only edges". Pass None to keep every edge.
    """
    try:
        import networkx as nx
    except ImportError:
        raise SystemExit("networkx not installed. Run: python -m pip install 'networkx>=3.2'")

    G = nx.Graph()
    for n in nodes:
        G.add_node(n["id"], label=n.get("label", n["id"]), type=n.get("type", "unknown"))

    agg: dict[tuple[str, str], dict] = {}
    for e in edges:
        if not _edge_passes_filter(e, edge_filter):
            continue
        src = id_map.get(e.get("from"))
        dst = id_map.get(e.get("to"))
        if not src or not dst or src == dst:
            continue
        a, b = sorted([src, dst])
        key = (a, b)
        etype = e.get("type", "EXTRACTED")
        if etype == "EXTRACTED":
            cost = 1.0
        elif etype == "INFERRED":
            conf = max(0.1, float(e.get("confidence", 0.5)))
            cost = 2.0 / conf
        else:
            cost = 3.0
        label = e.get("label", "")
        relation = e.get("relation") if etype == "EXTRACTED" else None
        prev = agg.get(key)
        if prev is None or cost < prev["cost"]:
            agg[key] = {
                "cost": cost, "label": label, "type": etype,
                "relation": relation, "direction": (src, dst),
            }
        elif label and not prev.get("label"):
            prev["label"] = label

    for (a, b), attrs in agg.items():
        G.add_edge(a, b, cost=attrs["cost"], weight=1.0 / attrs["cost"],
                   label=attrs["label"], edge_type=attrs["type"],
                   relation=attrs["relation"],
                   direction=attrs["direction"])
    return G


def _label(nodes_by_id: dict[str, dict], nid: str) -> str:
    return nodes_by_id.get(nid, {}).get("label") or nid.rsplit("/", 1)[-1].removesuffix(".md")


def _cluster_of(nid: str, clusters_data: dict) -> str:
    return clusters_data.get("hub_assignments", {}).get(nid, "") or \
           clusters_data.get("source_assignments", {}).get(nid, {}).get("primary", "")


def _print_budgeted(lines: list[str], budget: int) -> None:
    """Print up to `budget` lines, with a truncation note if more remain."""
    for line in lines[:budget]:
        print(line)
    if len(lines) > budget:
        print(f"... ({len(lines) - budget} more lines, raise --budget to see)")


# ───────────────────────── subcommands ─────────────────────────

def cmd_path(args) -> int:
    g_data = _load(GRAPH_PATH)
    clusters_data = _load(CLUSTERS_PATH) if CLUSTERS_PATH.exists() else {}
    id_map = _build_id_map(g_data["nodes"])
    nodes_by_id = {n["id"]: n for n in g_data["nodes"]}

    src = _resolve(args.src, id_map)
    dst = _resolve(args.dst, id_map)
    edge_filter = _parse_edge_filter(getattr(args, "edge_type", None))

    # _build_nx_graph first so its ImportError → friendly install-hint fires
    # before the bare `import networkx` (needed below for NetworkXNoPath).
    G = _build_nx_graph(g_data["nodes"], g_data["edges"], id_map, edge_filter=edge_filter)
    import networkx as nx

    if src not in G or dst not in G:
        raise SystemExit(f"Node missing from graph: {src if src not in G else dst}")
    try:
        path = nx.shortest_path(G, src, dst, weight="cost")
    except nx.NetworkXNoPath:
        out = {"src": src, "dst": dst, "path": None, "reason": "no path"}
        if edge_filter:
            out["edge_type"] = sorted(edge_filter)
        print(json.dumps(out, ensure_ascii=False, indent=2) if args.json
              else f"No path found between {_label(nodes_by_id, src)} and {_label(nodes_by_id, dst)}"
                   + (f" under --edge-type {','.join(sorted(edge_filter))}" if edge_filter else "")
                   + ".")
        return 1

    hops = []
    for a, b in zip(path, path[1:]):
        edge = G[a][b]
        direction = edge.get("direction", (a, b))
        hops.append({
            "from": a, "from_label": _label(nodes_by_id, a),
            "to": b, "to_label": _label(nodes_by_id, b),
            "type": edge.get("edge_type", ""),
            "relation": edge.get("relation"),
            "cost": round(edge.get("cost", 0), 2),
            "directed_from": direction[0],
            "rationale": edge.get("label", ""),
        })

    if args.json:
        print(json.dumps({
            "src": src, "dst": dst,
            "length": len(path) - 1,
            "path": path,
            "labels": [_label(nodes_by_id, p) for p in path],
            "clusters": [_cluster_of(p, clusters_data) for p in path],
            "hops": hops,
        }, ensure_ascii=False, indent=2))
        return 0

    header = f"Shortest path: {_label(nodes_by_id, src)} → {_label(nodes_by_id, dst)}  ({len(path)-1} hop{'s' if len(path)>2 else ''})"
    if edge_filter:
        header += f"  [--edge-type {','.join(sorted(edge_filter))}]"
    lines = [header]
    lines.append("")
    for i, h in enumerate(hops, 1):
        arrow = "→" if h["directed_from"] == h["from"] else "←"
        # When EXTRACTED has a relation, show "EXTRACTED · contradicts" form so
        # users see at a glance what kind of edge each hop traversed.
        type_str = h["type"]
        if h.get("relation"):
            type_str += f" · {h['relation']}"
        lines.append(f"{i}. [{h['from_label']}]  {arrow}  [{h['to_label']}]  ({type_str}, cost={h['cost']})")
        if h["rationale"]:
            rationale = h["rationale"]
            if len(rationale) > 100:
                rationale = rationale[:97] + "…"
            lines.append(f"     because: {rationale}")
        cl_from = _cluster_of(h["from"], clusters_data)
        cl_to = _cluster_of(h["to"], clusters_data)
        if cl_from and cl_to and cl_from != cl_to:
            lines.append(f"     cluster: [{cl_from}] → [{cl_to}]  (cross-cluster bridge)")

    _print_budgeted(lines, args.budget)
    return 0


def cmd_explain(args) -> int:
    g_data = _load(GRAPH_PATH)
    clusters_data = _load(CLUSTERS_PATH) if CLUSTERS_PATH.exists() else {}
    id_map = _build_id_map(g_data["nodes"])
    nodes_by_id = {n["id"]: n for n in g_data["nodes"]}
    edge_filter = _parse_edge_filter(getattr(args, "edge_type", None))

    nid = _resolve(args.node, id_map)
    node = nodes_by_id[nid]
    my_cluster = _cluster_of(nid, clusters_data)

    outbound: list[dict] = []
    inbound: list[dict] = []
    relation_breakdown: dict[str, dict[str, int]] = {
        "outbound": defaultdict(int), "inbound": defaultdict(int),
    }
    for e in g_data["edges"]:
        if not _edge_passes_filter(e, edge_filter):
            continue
        src = id_map.get(e.get("from"))
        dst = id_map.get(e.get("to"))
        relation = (e.get("relation") or "references") if e.get("type") == "EXTRACTED" else "inferred"
        if src == nid and dst:
            outbound.append({"target": dst, "label": _label(nodes_by_id, dst),
                             "type": e.get("type", "EXTRACTED"), "relation": relation,
                             "rationale": e.get("label", "")})
            relation_breakdown["outbound"][relation] += 1
        elif dst == nid and src:
            inbound.append({"source": src, "label": _label(nodes_by_id, src),
                            "type": e.get("type", "EXTRACTED"), "relation": relation,
                            "rationale": e.get("label", "")})
            relation_breakdown["inbound"][relation] += 1

    in_by_cluster: dict[str, int] = defaultdict(int)
    for e in inbound:
        cl = _cluster_of(e["source"], clusters_data)
        in_by_cluster[cl or "unassigned"] += 1

    rationales = [
        {"other": e["target"], "label": e["label"],
         "rationale": e["rationale"], "direction": "→"}
        for e in outbound if e["rationale"]
    ] + [
        {"other": e["source"], "label": e["label"],
         "rationale": e["rationale"], "direction": "←"}
        for e in inbound if e["rationale"]
    ]

    result = {
        "id": nid,
        "label": node.get("label", nid),
        "type": node.get("type", "unknown"),
        "cluster": my_cluster,
        "outbound_count": len(outbound),
        "inbound_count": len(inbound),
        "relation_breakdown": {
            "outbound": dict(relation_breakdown["outbound"]),
            "inbound": dict(relation_breakdown["inbound"]),
        },
        "outbound": outbound[:20],
        "inbound_by_cluster": dict(sorted(in_by_cluster.items(), key=lambda kv: -kv[1])),
        "rationale_edges": rationales[:15],
    }
    if edge_filter:
        result["edge_type"] = sorted(edge_filter)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    lines = [
        f"[{result['label']}] ({result['type']}, id={nid})",
        f"cluster: {my_cluster or '—'}",
        f"connections: {result['outbound_count']} outbound, {result['inbound_count']} inbound"
        + (f"  [--edge-type {','.join(sorted(edge_filter))}]" if edge_filter else ""),
        "",
    ]
    # Relation breakdown — surfaces what kind of role this node plays.
    # "cites 50 / contradicts 0 / defines 12" answers the same question
    # the graph.html legend does in viz form: what edges live around this
    # hub.
    in_rel = result["relation_breakdown"]["inbound"]
    out_rel = result["relation_breakdown"]["outbound"]
    if in_rel or out_rel:
        all_relations = sorted(set(in_rel) | set(out_rel),
                               key=lambda r: -(in_rel.get(r, 0) + out_rel.get(r, 0)))
        rel_strs = []
        for r in all_relations:
            rel_strs.append(f"{r} {in_rel.get(r, 0)}/{out_rel.get(r, 0)}")
        lines.append("relations (in/out): " + "  ·  ".join(rel_strs))
        lines.append("")
    if result["inbound_by_cluster"]:
        lines.append("Inbound by cluster:")
        for cl, n in result["inbound_by_cluster"].items():
            lines.append(f"  {cl}: {n}")
        lines.append("")
    if outbound:
        lines.append(f"Outbound ({len(outbound)} total, showing top):")
        for e in outbound[:10]:
            cl = _cluster_of(e["target"], clusters_data)
            cl_str = f"  [{cl}]" if cl else ""
            r = f"  — {e['rationale'][:60]}" if e["rationale"] else ""
            lines.append(f"  → {e['label']}{cl_str}{r}")
        lines.append("")
    if rationales:
        lines.append(f"Rationale edges (the 'why' of connections):")
        for r in rationales[:8]:
            snippet = r["rationale"]
            if len(snippet) > 90:
                snippet = snippet[:87] + "…"
            lines.append(f"  {r['direction']} {r['label']}: {snippet}")

    _print_budgeted(lines, args.budget)
    return 0


def cmd_neighbors(args) -> int:
    g_data = _load(GRAPH_PATH)
    clusters_data = _load(CLUSTERS_PATH) if CLUSTERS_PATH.exists() else {}
    id_map = _build_id_map(g_data["nodes"])
    nodes_by_id = {n["id"]: n for n in g_data["nodes"]}
    edge_filter = _parse_edge_filter(getattr(args, "edge_type", None))

    nid = _resolve(args.node, id_map)

    neighbors: set[str] = set()
    for e in g_data["edges"]:
        if not _edge_passes_filter(e, edge_filter):
            continue
        src = id_map.get(e.get("from"))
        dst = id_map.get(e.get("to"))
        if src == nid and dst:
            neighbors.add(dst)
        elif dst == nid and src:
            neighbors.add(src)

    grouped: dict[str, list[str]] = defaultdict(list)
    for n in neighbors:
        grouped[_cluster_of(n, clusters_data) or "unassigned"].append(_label(nodes_by_id, n))

    if args.json:
        print(json.dumps({
            "node": nid,
            "label": _label(nodes_by_id, nid),
            "neighbor_count": len(neighbors),
            "by_cluster": {k: sorted(v) for k, v in grouped.items()},
        }, ensure_ascii=False, indent=2))
        return 0

    header = f"Neighbors of [{_label(nodes_by_id, nid)}]: {len(neighbors)} total"
    if edge_filter:
        header += f"  [--edge-type {','.join(sorted(edge_filter))}]"
    lines = [header]
    for cl, labels in sorted(grouped.items(), key=lambda kv: -len(kv[1])):
        lines.append(f"\n[{cl}]  ({len(labels)})")
        for lbl in sorted(labels):
            lines.append(f"  {lbl}")
    _print_budgeted(lines, args.budget)
    return 0


# ───────────────────────── registration ─────────────────────────

EDGE_TYPE_HELP = (
    "comma-separated relation kinds to traverse "
    "(contradicts, defines, cites, references, inferred). "
    "Default: every edge."
)


def register(subparsers) -> None:
    """Attach path/explain/neighbors subsubcommands to the given subparsers group."""
    p_path = subparsers.add_parser("path", help="shortest traversal between two nodes")
    p_path.add_argument("src")
    p_path.add_argument("dst")
    p_path.add_argument("--budget", type=int, default=DEFAULT_BUDGET)
    p_path.add_argument("--json", action="store_true")
    p_path.add_argument("--edge-type", dest="edge_type", default=None, help=EDGE_TYPE_HELP)
    p_path.set_defaults(func=cmd_path)

    p_exp = subparsers.add_parser("explain", help="node summary with rationale edges")
    p_exp.add_argument("node")
    p_exp.add_argument("--budget", type=int, default=DEFAULT_BUDGET)
    p_exp.add_argument("--json", action="store_true")
    p_exp.add_argument("--edge-type", dest="edge_type", default=None, help=EDGE_TYPE_HELP)
    p_exp.set_defaults(func=cmd_explain)

    p_nb = subparsers.add_parser("neighbors", help="direct neighbors grouped by cluster")
    p_nb.add_argument("node")
    p_nb.add_argument("--budget", type=int, default=DEFAULT_BUDGET)
    p_nb.add_argument("--json", action="store_true")
    p_nb.add_argument("--edge-type", dest="edge_type", default=None, help=EDGE_TYPE_HELP)
    p_nb.set_defaults(func=cmd_neighbors)
