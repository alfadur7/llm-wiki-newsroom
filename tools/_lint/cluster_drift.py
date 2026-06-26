"""Cluster drift signal — warm-start vs cold-start partition quality.

Reads the current `graph/_clusters.json` (warm-start product) and runs a
transient cold-start Leiden on the same graph to compute the quality gap.
Cold > warm by more than QUALITY_THRESHOLD signals that warm-start is
stuck in a stale local optimum — operator should consider
`python tools/build.py clusters --cold` to re-anchor.

Opt-in subcommand (NOT in `all`): cold Leiden runs the full partition
algorithm again — adds ~2-5 seconds vs <100ms for the rest of the lint
suite, so we keep it explicit. Designed to be run periodically (e.g.,
monthly) or after suspect changes.

CLI:
    python tools/lint.py graph drift           # quality comparison
    python tools/lint.py graph drift --json    # machine output

Exit codes:
    0 — partition healthy (warm within threshold of cold optimum)
    1 — drift detected (cold optimum significantly better)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
CLUSTERS_PATH = ROOT / "graph" / "_clusters.json"

# Relative quality gap threshold. RBConfiguration quality is unnormalised
# (scales with edge count: ~3700 for the wiki's ~16K edges), so a fixed
# absolute number is meaningless across builds. Use ratio instead:
#   delta / warm_quality > _resolved_threshold() → advisory.
# 0.005 (0.5%) picked as the gap where cold-start is meaningfully better;
# below this is partition-tie-breaking noise. Override with the
# `WIKI_LINT_DRIFT_THRESHOLD` env var or the `--threshold` CLI flag when
# operator data suggests the default is too tight or too loose.
DEFAULT_QUALITY_THRESHOLD = 0.005


def _resolved_threshold(cli_override: float | None) -> float:
    """Resolve the runtime threshold: CLI > env > default."""
    if cli_override is not None:
        return cli_override
    env_val = os.environ.get("WIKI_LINT_DRIFT_THRESHOLD")
    if env_val:
        try:
            return float(env_val)
        except ValueError:
            print(
                f"WARN: WIKI_LINT_DRIFT_THRESHOLD={env_val!r} is not a float — "
                f"falling back to default {DEFAULT_QUALITY_THRESHOLD}",
                file=sys.stderr,
            )
    return DEFAULT_QUALITY_THRESHOLD


# Backward-compatible alias for callers that may import the constant.
QUALITY_THRESHOLD = DEFAULT_QUALITY_THRESHOLD

SEED = 42  # mirrors tools/_build/clusters.py
RESOLUTION = 1.0


def run(json_out: bool = False, threshold: float | None = None) -> int:
    try:
        import leidenalg
        import igraph as ig
    except ImportError:
        print("ERROR: leidenalg/igraph not installed. Run: python -m pip install 'igraph' 'leidenalg'", file=sys.stderr)
        return 2

    if not CLUSTERS_PATH.exists():
        print(f"ERROR: {CLUSTERS_PATH} not found. Run `python tools/build.py clusters` first.", file=sys.stderr)
        return 2

    sys.path.insert(0, str(ROOT / "tools"))
    from _build.clusters import build_hub_graph  # noqa: E402

    G, _hub_labels, _data, _id_map, _isolated = build_hub_graph(verbose=False)

    # Build igraph mirror of G (must match _run_leiden's vertex assignment).
    nodes = sorted(G.nodes())
    node_idx = {n: i for i, n in enumerate(nodes)}
    edges = [(node_idx[u], node_idx[v]) for u, v in G.edges()]
    weights = [G[u][v].get("weight", 1.0) for u, v in G.edges()]
    g_ig = ig.Graph(n=len(nodes), edges=edges, edge_attrs={"weight": weights})
    g_ig.vs["name"] = nodes

    # Warm partition — load membership from current _clusters.json.
    clusters_data = json.loads(CLUSTERS_PATH.read_text(encoding="utf-8"))
    hub_to_comm: dict[str, int] = {}
    for idx, c in enumerate(clusters_data.get("clusters", [])):
        for hub in c.get("members", []):
            hub_to_comm[hub] = idx
    n_warm_comms = len(clusters_data.get("clusters", []))

    # Each vertex needs a community index. Hubs in current G but not in
    # _clusters.json (rare — should match exactly under normal flow) get
    # placed in a fresh community per vertex so they don't artificially
    # collapse partitions. Warm partition must reflect what's currently
    # serialised, not invent placements.
    next_fresh = n_warm_comms
    warm_membership: list[int] = []
    for n in nodes:
        if n in hub_to_comm:
            warm_membership.append(hub_to_comm[n])
        else:
            warm_membership.append(next_fresh)
            next_fresh += 1

    warm_partition = leidenalg.RBConfigurationVertexPartition(
        g_ig,
        initial_membership=warm_membership,
        weights="weight",
        resolution_parameter=RESOLUTION,
    )
    quality_warm = warm_partition.quality()
    n_warm = len(set(warm_membership))

    # Cold partition — fresh Leiden from singleton start.
    cold_partition = leidenalg.find_partition(
        g_ig,
        leidenalg.RBConfigurationVertexPartition,
        weights="weight",
        resolution_parameter=RESOLUTION,
        seed=SEED,
    )
    quality_cold = cold_partition.quality()
    n_cold = len(set(cold_partition.membership))

    quality_threshold = _resolved_threshold(threshold)
    delta = quality_cold - quality_warm
    # RBConfiguration quality is modularity-like and can be ≤0 for a degenerate
    # warm partition — the exact case this check exists to flag. Normalizing by
    # |quality_warm| keeps the relative-delta meaningful there (a much-better
    # cold partition still trips the threshold) instead of being silenced to 0.
    denom = abs(quality_warm)
    rel_delta = delta / denom if denom > 0 else (1.0 if delta > 0 else 0.0)
    drifted = rel_delta > quality_threshold

    if json_out:
        print(json.dumps({
            "warm_quality": quality_warm,
            "cold_quality": quality_cold,
            "delta": delta,
            "rel_delta": rel_delta,
            "warm_clusters": n_warm,
            "cold_clusters": n_cold,
            "threshold": quality_threshold,
            "drifted": drifted,
        }, indent=2))
        return 1 if drifted else 0

    print(f"Warm partition (current _clusters.json): quality={quality_warm:.2f}, clusters={n_warm}")
    print(f"Cold partition (fresh Leiden, transient): quality={quality_cold:.2f}, clusters={n_cold}")
    pct = rel_delta * 100
    print(f"Delta (cold - warm): {delta:+.2f}  ({pct:+.3f}% of warm; threshold: ±{quality_threshold * 100:.1f}%)")
    print()

    if drifted:
        print(f"⚠️  DRIFT — cold-start partition is {pct:.3f}% better than warm.")
        print(f"   Warm-start may be stuck in a stale local optimum. Consider:")
        print(f"     python tools/build.py clusters --cold")
        print(f"   to re-anchor. Note: cold rebuild may produce new auto-slug")
        print(f"   clusters that need editorial labelling in graph/cluster_labels.json.")
        return 1

    if delta < 0:
        print(f"OK — warm partition is {-pct:.3f}% BETTER than cold (not stuck).")
    else:
        print(f"OK — warm partition within {quality_threshold * 100:.1f}% of cold optimum.")
    return 0
