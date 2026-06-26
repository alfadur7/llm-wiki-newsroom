"""Composite-score ranking of surprising hub connections.

Scores every entity/concept hub on three signals and returns the top-N:

  B = betweenness centrality      (how often this node sits on a shortest
                                   path between other hubs — bridge role)
  X = cross-cluster ratio         (neighbors span many clusters / few)
  F = frequency penalty           (down-weight very-high-degree hubs that
                                   are "obvious" and not surprising)

  composite = B × X / log(degree + 2)

The top-ranked hubs are the ones that quietly stitch disparate parts of
the wiki together — Memex-style serendipity seeds. Only entities/ and
concepts/ pages enter the ranking (HUB_PREFIXES filter); source nodes
and root meta pages — already excluded from the graph at build time —
are naturally outside this scope.

Output: ranked list with composite score, degree, betweenness,
cross-cluster ratio, and the cluster labels the hub connects.
"""
from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))  # _discover/ → tools/ root (shared modules)
from _lib import GRAPH, _build_id_map  # noqa: E402

GRAPH_PATH = GRAPH / "_graph.json"
CLUSTERS_PATH = GRAPH / "_clusters.json"

HUB_PREFIXES = ("entities/", "concepts/")

DEFAULT_TOP = 15


def compute(top: int | None = None) -> tuple[list[dict], int, int] | None:
    """Headless: produce the ranked surprising-hub list without printing.

    Returns `(results, sampled_k, excluded_isolates)` or `None` if required
    inputs / dependencies are missing (caller decides how to surface the
    error — for `run()` it's a stderr line + exit code 1; for `lint.py
    graph gaps` it's a fold-into-summary placeholder)."""
    if not GRAPH_PATH.exists() or not CLUSTERS_PATH.exists():
        return None
    try:
        import networkx as nx
    except ImportError:
        return None

    g = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    c = json.loads(CLUSTERS_PATH.read_text(encoding="utf-8"))
    id_map = _build_id_map(g["nodes"])
    hub_assign = c.get("hub_assignments", {})
    nodes_by_id = {n["id"]: n for n in g["nodes"]}

    G = nx.Graph()
    hub_ids = {n["id"] for n in g["nodes"] if n["id"].startswith(HUB_PREFIXES)}
    G.add_nodes_from(sorted(hub_ids))
    for e in g["edges"]:
        src = id_map.get(e.get("from"))
        dst = id_map.get(e.get("to"))
        if not src or not dst or src == dst:
            continue
        if src not in hub_ids or dst not in hub_ids:
            continue
        if G.has_edge(src, dst):
            G[src][dst]["weight"] = G[src][dst].get("weight", 0) + 1
        else:
            G.add_edge(src, dst, weight=1)

    isolates = [n for n in G.nodes if G.degree(n) == 0]
    G.remove_nodes_from(isolates)
    n_nodes = G.number_of_nodes()
    if n_nodes == 0:
        return [], 0, len(isolates)
    k = min(n_nodes, 200)
    # `weight` accumulates as a co-occurrence COUNT (stronger tie → larger
    # value), but networkx betweenness interprets the weight attribute as a
    # DISTANCE. Feeding the raw count would make stronger ties look farther
    # apart — the inverse of intent. Convert count → distance (1/count) so a
    # more-connected pair is treated as closer, matching _query/graph.py.
    for _u, _v, _d in G.edges(data=True):
        _d["distance"] = 1.0 / _d["weight"]
    bet = nx.betweenness_centrality(G, k=k, weight="distance", seed=42, normalized=True)

    results: list[dict] = []
    for node in G.nodes:
        nbrs = list(G.neighbors(node))
        deg = len(nbrs)
        if deg < 3:
            continue
        nbr_clusters = Counter(hub_assign.get(n, "unassigned") for n in nbrs)
        own_cluster = hub_assign.get(node, "unassigned")
        own_cluster_count = nbr_clusters.get(own_cluster, 0)
        cross = 1.0 - (own_cluster_count / deg)
        freq_penalty = math.log(deg + 2)
        composite = bet[node] * cross / freq_penalty
        results.append({
            "id": node,
            "label": nodes_by_id[node].get("label", node),
            "own_cluster": own_cluster,
            "degree": deg,
            "betweenness": round(bet[node], 5),
            "cross_cluster_ratio": round(cross, 3),
            "composite": round(composite, 6),
            "neighbor_clusters": dict(nbr_clusters.most_common()),
        })

    results.sort(key=lambda r: r["composite"], reverse=True)
    top_n = top if top is not None else DEFAULT_TOP
    return results[:top_n], k, len(isolates)


def run(json_out: bool = False, top: int | None = None) -> int:
    if not GRAPH_PATH.exists() or not CLUSTERS_PATH.exists():
        print("graph/_graph.json or _clusters.json missing. Run `python tools/build.py` first.",
              file=sys.stderr)
        return 1
    try:
        import networkx as nx  # noqa: F401 — `compute` will surface the same error
    except ImportError:
        print("networkx not installed. Run: python -m pip install 'networkx>=3.2'", file=sys.stderr)
        return 1

    res = compute(top=top)
    if res is None:
        return 1
    results, k, excluded = res
    if not results:
        print("No hubs in graph.", file=sys.stderr)
        return 1

    if json_out:
        print(json.dumps({
            "method": "composite: betweenness × cross_cluster / log(degree+2)",
            "sampled_k_for_betweenness": k,
            "excluded_isolates": excluded,
            "results": results,
        }, ensure_ascii=False, indent=2))
        return 0

    print(f"Surprising connections — top {len(results)} bridge hubs")
    print(f"(composite = betweenness × cross-cluster-ratio / log(degree+2); "
          f"betweenness approximated with k={k})")
    print()
    print(f"{'#':<3}{'hub':<32}{'own cluster':<26}{'deg':>5}{'bet':>8}{'cross':>7}{'score':>9}")
    print("─" * 90)
    for i, r in enumerate(results, 1):
        label = r["label"][:30]
        cluster = (r["own_cluster"] or "—")[:24]
        print(f"{i:<3}{label:<32}{cluster:<26}{r['degree']:>5}{r['betweenness']:>8.4f}{r['cross_cluster_ratio']:>7.2f}{r['composite']:>9.5f}")

    print()
    print("Top neighbor-cluster mix (what each hub connects):")
    for i, r in enumerate(results[:10], 1):
        mix = ", ".join(f"{c}({n})" for c, n in list(r["neighbor_clusters"].items())[:4])
        print(f"  {i}. {r['label']}: {mix}")
    return 0
