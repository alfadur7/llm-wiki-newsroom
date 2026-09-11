"""Cluster drift signal — is the current partition the one the graph implies?

Three signals: (1) the quality gap against a single cold run, (2) the ARI
against the consensus partition of N cold runs, (3) a per-cluster split rate.
(2) exists because modularity is degenerate — Good, de Montjoye & Clauset
(Phys Rev E 81 046106, 2010) show exponentially many high-scoring partitions
that disagree with each other, so one quality number cannot justify "this
community count is right".

Reads the current `graph/_clusters.json` (warm-start product) and runs a
transient cold-start Leiden on the same graph to compute the quality gap.
Cold > warm by more than DEFAULT_QUALITY_THRESHOLD signals that warm-start is
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
    2 — missing dependency (leidenalg/igraph) or missing graph/_clusters.json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import CLUSTERS_JSON as CLUSTERS_PATH  # noqa: E402

# Relative quality gap threshold. RBConfiguration quality is unnormalised — it
# scales with total edge weight (this corpus: ~15 for the 33-edge hub subgraph),
# so a fixed absolute number is meaningless across builds and corpus sizes,
# and absolute values are not comparable across corpora. Use ratio instead:
#   delta / warm_quality > _resolved_threshold() → advisory.
# 0.005 (0.5%) picked as the gap where cold-start is meaningfully better;
# below this is partition-tie-breaking noise. Override with the
# `WIKI_LINT_DRIFT_THRESHOLD` env var or the `--threshold` CLI flag when
# operator data suggests the default is too tight or too loose.
DEFAULT_QUALITY_THRESHOLD = 0.005

# Consensus stability — the complement to a single cold comparison. Lancichinetti
# & Fortunato (Sci Rep 2:336, 2012) is the standard answer to degeneracy: run the
# partition N times, keep the pairs that co-occur often enough, and re-cluster that
# co-assignment graph into a consensus partition. How closely warm matches it (ARI)
# is the answer to "is the current partition a coincidence?".
CONSENSUS_RUNS = 20
CONSENSUS_CO_THRESHOLD = 0.5    # LF2012's recommendation — keep a pair only if it is
                                # grouped together in at least half the runs.
# Carried default, not a local calibration: it was set against a 681-hub corpus where
# warm scored 0.781 against consensus while independent cold runs agreed with each
# other at 0.706 — i.e. it fires only when warm diverges further than two cold runs
# routinely do. Re-derive it here once this corpus is large enough for the consensus
# to have anything to disagree about.
CONSENSUS_ARI_FLOOR = 0.60
# A run counts as a split when the largest surviving piece holds less than this share
# of the original cluster — the line between a few boundary nodes moving and a chunk
# detaching.
SPLIT_DETACH_SHARE = 0.9
SPLIT_RATE_FLAG = 0.5           # surface a cluster that splits in at least half the runs.


def _ari(a: list[int], b: list[int]) -> float:
    """Adjusted Rand Index. Computed from the stdlib — sklearn is not a dependency here."""
    from collections import Counter
    n = len(a)
    if n < 2:
        return 1.0
    def c2(k):
        return k * (k - 1) / 2
    joint = Counter(zip(a, b))
    ra, rb = Counter(a), Counter(b)
    sij = sum(c2(v) for v in joint.values())
    sa, sb = sum(c2(v) for v in ra.values()), sum(c2(v) for v in rb.values())
    total = c2(n)
    expected = sa * sb / total
    maximum = (sa + sb) / 2
    return 1.0 if maximum == expected else (sij - expected) / (maximum - expected)


def _split_rates(partitions: list[list[int]], clusters_data: dict,
                 node_index: dict[str, int]) -> list[tuple[str, int, float, float]]:
    """Per-cluster split rate — how often a cluster's members scatter across cold runs.

    Reuses the partitions consensus already ran (no extra Leiden calls). It is an axis
    neither containment nor the consensus ARI can see: a cluster whose declared anchors
    all sit in place and which matches the consensus can still break in half every run.

    Returns [(slug, size, split_rate, mean_largest_share)], split rate descending.
    """
    from collections import Counter
    runs = len(partitions) or 1
    out = []
    for c in clusters_data.get("clusters", []):
        vids = [node_index[m] for m in c.get("members", []) if m in node_index]
        if not vids:
            continue
        splits, shares = 0, []
        for part in partitions:
            largest = Counter(part[v] for v in vids).most_common(1)[0][1]
            share = largest / len(vids)
            shares.append(share)
            if share < SPLIT_DETACH_SHARE:
                splits += 1
        out.append((c["slug"], len(vids), splits / runs, sum(shares) / runs))
    out.sort(key=lambda r: -r[2])
    return out


def _consensus(ig, leidenalg, g_ig, n_vertices: int,
               resolution: float) -> tuple[list[int], int, list[list[int]]]:
    """LF2012 consensus — re-cluster the co-assignment graph of N cold runs.

    Returns (membership, run_count, partitions). Each run is a cold start under its
    own seed, so none of them inherits the warm history; `partitions` comes back so
    `_split_rates` can reuse the same runs.
    """
    from collections import Counter
    from itertools import combinations
    co: Counter = Counter()
    partitions: list[list[int]] = []
    for seed in range(1, CONSENSUS_RUNS + 1):
        part = leidenalg.find_partition(
            g_ig, leidenalg.RBConfigurationVertexPartition, weights="weight",
            resolution_parameter=resolution, seed=seed, n_iterations=-1,
        )
        partitions.append(list(part.membership))
        by_comm: dict[int, list[int]] = {}
        for vertex, comm in enumerate(part.membership):
            by_comm.setdefault(comm, []).append(vertex)
        for members in by_comm.values():
            co.update(combinations(sorted(members), 2))
    keep = [(u, v) for (u, v), hits in co.items()
            if hits / CONSENSUS_RUNS >= CONSENSUS_CO_THRESHOLD]
    weights = [co[(u, v)] / CONSENSUS_RUNS for u, v in keep]
    cg = ig.Graph(n=n_vertices, edges=keep, edge_attrs={"weight": weights})
    part = leidenalg.find_partition(
        cg, leidenalg.RBConfigurationVertexPartition, weights="weight",
        resolution_parameter=resolution, seed=1, n_iterations=-1,
    )
    return list(part.membership), CONSENSUS_RUNS, partitions


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


def run(json_out: bool = False, threshold: float | None = None) -> int:
    try:
        import leidenalg
        import igraph as ig
    except ImportError:
        # Deliberately does NOT use the build's Louvain fallback: this check
        # compares a warm partition against a transient cold one, and a
        # cross-backend comparison measures the backend, not the drift.
        print("ERROR: leidenalg/igraph not installed. Run: python -m pip install 'igraph' 'leidenalg'", file=sys.stderr)
        return 2

    if not CLUSTERS_PATH.exists():
        print(f"ERROR: {CLUSTERS_PATH} not found. Run `python tools/build.py clusters` first.", file=sys.stderr)
        return 2

    from _build.clusters import RESOLUTION, SEED, build_hub_graph, to_igraph  # noqa: E402  (tools/ on sys.path at module top)

    G, _hub_labels, _data, _id_map, _isolated = build_hub_graph(verbose=False)

    # igraph mirror of G — to_igraph is the same conversion _run_leiden uses,
    # so the warm-membership indexing below shares its vertex assignment.
    g_ig = to_igraph(G)
    nodes = g_ig.vs["name"]
    node_idx = {n: i for i, n in enumerate(nodes)}

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

    cons_membership, cons_runs, cons_parts = _consensus(ig, leidenalg, g_ig, len(nodes), RESOLUTION)
    splits = _split_rates(cons_parts, clusters_data, node_idx)
    fragile = [r for r in splits if r[2] >= SPLIT_RATE_FLAG]
    n_cons = len(set(cons_membership))
    cons_ari = _ari(warm_membership, cons_membership)
    cons_diverged = cons_ari < CONSENSUS_ARI_FLOOR

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
            "consensus_runs": cons_runs,
            "consensus_clusters": n_cons,
            "consensus_ari": round(cons_ari, 4),
            "consensus_ari_floor": CONSENSUS_ARI_FLOOR,
            "consensus_diverged": cons_diverged,
            "split_rate_flag": SPLIT_RATE_FLAG,
            "cluster_split_rates": [
                {"slug": sl, "size": sz, "split_rate": round(rt, 3),
                 "mean_largest_share": round(sh, 3)}
                for sl, sz, rt, sh in splits
            ],
        }, indent=2))
        return 1 if (drifted or cons_diverged) else 0

    print(f"Warm partition (current _clusters.json): quality={quality_warm:.2f}, clusters={n_warm}")
    print(f"Cold partition (fresh Leiden, transient): quality={quality_cold:.2f}, clusters={n_cold}")
    pct = rel_delta * 100
    print(f"Delta (cold - warm): {delta:+.2f}  ({pct:+.3f}% of warm; threshold: ±{quality_threshold * 100:.1f}%)")
    print(f"Consensus ({cons_runs}-run, LF2012): clusters={n_cons}, ARI vs warm={cons_ari:.3f} "
          f"(floor {CONSENSUS_ARI_FLOOR})")
    print()
    if cons_diverged:
        print(f"CONSENSUS DIVERGENCE — warm sits at ARI {cons_ari:.3f} from the {cons_runs}-run consensus.")
        print(f"   The consensus holds {n_cons} clusters, warm holds {n_warm}: the current partition")
        print(f"   does not represent the consensus structure. Quality alone cannot settle this —")
        print(f"   modularity is degenerate (see the module docstring). Check the declared anchors")
        print(f"   first (`lint graph clusters`), and if it still diverges:")
        print(f"     python tools/build.py clusters --cold")
    elif n_cons != n_warm:
        print(f"NOTE — the consensus cluster count ({n_cons}) differs from warm ({n_warm}), but ARI "
              f"{cons_ari:.3f} says the structure agrees: a few boundaries moved.")
    print()
    print(f"[Split rate] share of the {cons_runs} cold runs in which more than "
          f"{round((1 - SPLIT_DETACH_SHARE) * 100)}% of a cluster's members detached from its main body")
    for slug, size, rate, share in splits:
        mark = "  !" if rate >= SPLIT_RATE_FLAG else "   "
        print(f"{mark} {slug:24s} size={size:4d}  split {rate:4.0%}  largest piece {share:.2f}")
    if fragile:
        print(f"     — {len(fragile)} cluster(s) break in at least half the runs. This is the axis")
        print(f"       containment and the consensus ARI cannot see. It reads as \"the boundary is")
        print(f"       soft\", not \"split it\". No remedy is prescribed here — splitting, reinforcing")
        print(f"       the seam links and adding sources were each measured against a far larger")
        print(f"       corpus upstream and rejected, and that measurement has not been reproduced")
        print(f"       here. Record it as a diagnosis; forcing it is manipulating the graph to")
        print(f"       satisfy a metric.")
    print()

    if drifted:
        print(f"⚠️  DRIFT — cold-start partition is {pct:.3f}% better than warm.")
        print(f"   Warm-start may be stuck in a stale local optimum. Consider:")
        print(f"     python tools/build.py clusters --cold")
        print(f"   to re-anchor. Note: cold rebuild may produce new auto-slug")
        print(f"   clusters that need editorial labelling in graph/cluster_labels.json.")
        return 1

    quality_ok = (f"warm partition is {-pct:.3f}% BETTER than cold (not stuck)."
                  if delta < 0 else
                  f"warm partition within {quality_threshold * 100:.1f}% of cold optimum.")
    if cons_diverged:
        # Quality is fine but the consensus diverged — opening with OK would contradict exit 1.
        print(f"   (the quality axis is healthy: {quality_ok})")
        return 1
    print(f"OK — {quality_ok}")
    print(f"OK — consensus ARI {cons_ari:.3f} >= {CONSENSUS_ARI_FLOOR} (structure agrees).")
    return 0
