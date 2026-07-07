"""graph/_clusters.json diagnostic — Leiden cluster health report.

Consumes the output of `_build/clusters.py`. File name mirrors the data
source (graph/_clusters.json) so the lint counterpart is discoverable
alongside the builder.

Reports:
  - [A] Isolated hubs (entities/concepts with no edges → excluded from clustering)
  - [B] Small clusters (size < MIN_SIZE) — likely over-split, candidate for merge
  - [C] Mixed clusters (coherence='mixed' and size >= MIN_MIXED_SIZE) — tag
    distribution too dispersed; either refine label anchors or accept as
    cross-cutting theme (informational — not counted in actionable total)
  - [D] Unlabeled clusters — no match in graph/cluster_labels.json; human
    review needed to add a stable label
  - [E] Unassigned sources — sources with no outbound edges to any clustered hub
  - [F] Orphan labels — slug in graph/cluster_labels.json without a matching
    community in the current Leiden output (former cluster dissolved or
    anchor_members drifted). Informational — label pruning is domain
    judgment (CLAUDE.md naming rule), not lint-automatable.
  - [G] Fragile bridges — pairs of clusters connected by exactly one edge.
    Flags community-boundary fragility: removing that single [[wikilink]]
    would sever the two domains entirely. Informational — resolution may
    be "reinforce with more cross-references" (if the link reflects real
    relation) or "accept as truly distant domains". Surfaces hidden
    refactor risk before cluster boundaries shift.

Every invocation appends a one-line JSONL record of core health metrics
(node/edge counts, edges-per-node, isolated-hub rate, community count,
largest-community size, fragile-bridge count) to graph/_health-log.jsonl.
Enables trend detection: catch connectivity regressions over ingest
bursts without manual snapshots.

`--fix` mode regenerates `_graph.json` and `_clusters.json` from current
wiki state before the diagnostic runs. This mirrors the SoT-freshness
contract: when the user asks to fix cluster health, they expect the
underlying SoT JSON to reflect the current wiki, not yesterday's build.
The deterministic Python rebuild (Leiden) makes this safe to run
automatically — no human/LLM judgment is involved. Downstream MD
side-effects (catalogs, overview AUTO blocks) are NOT regenerated here
to keep the operation surprise-free; run `python tools/build.py
clusters` for the full landscape-axis cascade.

Exit code 0 if nothing actionable, 1 otherwise. JSON mode for automation.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import CLUSTER_LABELS_JSON, CLUSTERS_JSON, GRAPH, GRAPH_JSON, HUB_PREFIXES, _build_id_map  # noqa: E402

CLUSTERS_PATH = CLUSTERS_JSON
LABELS_PATH = CLUSTER_LABELS_JSON
GRAPH_PATH = GRAPH_JSON
HEALTH_LOG_PATH = GRAPH / "_health-log.jsonl"

MIN_SIZE = 3          # below this, cluster is over-split
MIN_MIXED_SIZE = 10   # mixed clusters smaller than this are ignored (noise)
FRAGILE_EDGE_THRESHOLD = 1  # cluster-pair with <= this many edges is fragile

# G3 health thresholds (2026-04-30) — advisory only, do not affect actionable
# count. Tuned from the 14-bank ingest incident where INFERRED edges (55%
# of total, +14.9% in one ingest) re-shuffled Leiden communities. See
# log.md "[2026-04-30] graph | G1 + B 적용" for derivation.
INFERRED_RATIO_THRESHOLD = 0.30        # INFERRED edge count / EXTRACTED edge count
INFERRED_WEIGHT_THRESHOLD = 0.20       # INFERRED hub-hub weight / total hub-hub weight
EDGE_INFLATION_RATIO = 1.5             # edges Δ% / nodes Δ% — sustained gap above this
                                       # signals algorithmic edge fanout, not data growth
HYSTERESIS_FLOOR = 0.50                # carry-over rate of stable labels across builds


def _regenerate_sot() -> None:
    """Rebuild _graph.json + _clusters.json from current wiki state.

    Imports the build modules directly (not subprocess) so errors propagate
    cleanly and the call stays inside the same Python process. Only the
    JSON outputs are rebuilt; downstream MD-mutating steps
    (clusters.run_catalogs / clusters.run_pages) are intentionally
    skipped to keep `graph --fix` from silently editing overview MDs.
    """
    print("[graph clusters --fix] regenerating SoT JSONs (graph + clusters)...")
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from _build import graph as graph_build, clusters as clusters_build  # noqa: E402

    graph_build.run()
    clusters_build.run()
    print()


def _node_to_cluster(clusters_data: dict) -> dict[str, str]:
    """Map each node id (hubs + sources with primary assignment) to its cluster slug."""
    mapping: dict[str, str] = {}
    for path, slug in clusters_data.get("hub_assignments", {}).items():
        if slug:
            mapping[path] = slug
    for path, info in clusters_data.get("source_assignments", {}).items():
        primary = info.get("primary") if isinstance(info, dict) else None
        if primary:
            mapping[path] = primary
    return mapping


def _resolve_edge_target(target: str, nodes_by_id: set[str], id_map: dict[str, str]) -> str | None:
    """Resolve an edge's `to` field to a full node id.

    `_graph.json` edges are written with canonical full-path targets, so the
    direct id match is the live path. The fallback resolves any legacy /
    non-canonical form via `_lib._build_id_map` — the same stem→id resolver
    the build·query·discover paths share, so lint cannot drift from build.
    """
    if target in nodes_by_id:
        return target
    return id_map.get(target)


def _find_fragile_bridges(graph_data: dict, clusters_data: dict) -> list[dict]:
    """Identify cluster-pairs connected by <= FRAGILE_EDGE_THRESHOLD edges.

    Returns each fragile pair with slugs, edge count, and one sample edge
    (the first inter-cluster edge encountered) to help the reviewer locate
    the actual link. Directionality is collapsed — (A, B) and (B, A) are
    the same pair.
    """
    nodes = graph_data.get("nodes", [])
    nodes_by_id = {n["id"] for n in nodes}
    id_map = _build_id_map(nodes)

    node_cluster = _node_to_cluster(clusters_data)

    pair_counts: Counter[tuple[str, str]] = Counter()
    pair_sample: dict[tuple[str, str], dict[str, str]] = {}
    for edge in graph_data.get("edges", []):
        from_id = edge.get("from") if edge.get("from") in nodes_by_id else None
        to_id = _resolve_edge_target(edge.get("to", ""), nodes_by_id, id_map)
        if not from_id or not to_id:
            continue
        from_cluster = node_cluster.get(from_id)
        to_cluster = node_cluster.get(to_id)
        if not from_cluster or not to_cluster or from_cluster == to_cluster:
            continue
        pair = tuple(sorted((from_cluster, to_cluster)))
        pair_counts[pair] += 1
        if pair not in pair_sample:
            pair_sample[pair] = {
                "from": from_id,
                "to": to_id,
                "type": edge.get("type", ""),
                "label": edge.get("label", ""),
            }

    fragile = []
    for pair, count in sorted(pair_counts.items()):
        if count <= FRAGILE_EDGE_THRESHOLD:
            fragile.append({
                "cluster_a": pair[0],
                "cluster_b": pair[1],
                "edge_count": count,
                "sample_edge": pair_sample[pair],
            })
    return fragile


def _compute_health(graph_data: dict, clusters_data: dict, fragile_count: int) -> dict:
    """Produce the core health metrics written to the JSONL trend log.

    Includes 4 G3 metrics added 2026-04-30 to detect signal-quality drift:
      - inferred_extracted_ratio: INFERRED edge count / EXTRACTED edge count.
        High values signal weak-signal inflation in the auto-inference layer.
      - inferred_weight_share: INFERRED hub-hub weight / total hub-hub weight.
        High values signal author-intent (EXTRACTED) being out-voted by
        co-citation heuristics (INFERRED) in Leiden modularity.
      - hysteresis_share: stable-label carry-over rate across builds.
        Low values signal community boundaries shifting fast enough to lose
        label identity — the underlying instability that prompted the
        2026-04-30 G1+B fix.
      - cluster_count_change is computed against the previous health-log
        entry by the trend formatter, not stored here (it's a delta, not a
        snapshot).
    """
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])
    clusters = clusters_data.get("clusters", [])
    stats = clusters_data.get("stats", {})
    hub_nodes = stats.get("hub_nodes") or 0
    isolated_hubs = len(clusters_data.get("isolated_hubs", []))
    total_hubs = hub_nodes + isolated_hubs
    sizes = [c.get("size", 0) for c in clusters]

    # G3 M-1: INFERRED/EXTRACTED ratio + INFERRED weight share at hub-hub
    # level (the slice Leiden actually consumes, mirroring _build/clusters.py
    # weighting logic — keep these two in sync if the builder weighting changes).
    hub_ids = {n["id"] for n in nodes if n["id"].startswith(HUB_PREFIXES)}
    id_map = _build_id_map(nodes)

    ext_count = inf_count = 0
    ext_weight = inf_weight = 0.0
    for e in edges:
        src = id_map.get(e.get("from"))
        dst = id_map.get(e.get("to"))
        if not src or not dst or src == dst:
            continue
        if src not in hub_ids or dst not in hub_ids:
            continue
        if e.get("type") == "EXTRACTED":
            ext_count += 1
            ext_weight += 1.0
        elif e.get("type") == "INFERRED":
            inf_count += 1
            inf_weight += float(e.get("confidence", 0.5))

    # Special-case ext_count=0 with inf_count>0 — the worst signal-quality
    # state (only inferred edges, no author wikilinks). The ratio is
    # undefined (division by zero); emit `None` rather than float("inf") so
    # the JSONL trend log stays valid JSON for strict external consumers
    # (jq, JS JSON.parse) — `Infinity` is a Python-only extension. The G3
    # advisory and stdout formatter below treat None as "definitely over
    # threshold".
    if ext_count == 0:
        inferred_extracted_ratio = None if inf_count > 0 else 0.0
    else:
        inferred_extracted_ratio = round(inf_count / ext_count, 3)
    total_weight = ext_weight + inf_weight
    inferred_weight_share = round(inf_weight / total_weight, 3) if total_weight else 0.0

    # G3 M-1: hysteresis carry-over rate. Denominator is "matched labels"
    # (clusters that resolved to a label, whether by hysteresis or anchor) —
    # auto-labelled clusters are excluded because they have no stable
    # identity to preserve.
    cluster_count = stats.get("cluster_count") or len(clusters)
    unlabeled = stats.get("unlabeled_clusters") or 0
    matched = max(0, cluster_count - unlabeled)
    hyst_carried = stats.get("hysteresis_carried") or 0
    hysteresis_share = round(hyst_carried / matched, 3) if matched else 0.0

    return {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "nodes": len(nodes),
        "edges": len(edges),
        "edges_per_node": round(len(edges) / len(nodes), 2) if nodes else 0.0,
        "isolated_hubs": isolated_hubs,
        "isolated_hub_rate": round(isolated_hubs / total_hubs, 4) if total_hubs else 0.0,
        "unassigned_sources": len(clusters_data.get("unassigned_sources", [])),
        "communities": len(clusters),
        # Persist `unlabeled_clusters` so the next build's hysteresis advisory
        # can compute `prev_matched = prev.communities - prev.unlabeled_clusters`
        # accurately. Without this key, the gate at _format_trend_lines silently
        # treats every prev community as "matched" and the advisory fires
        # whenever hysteresis_share < floor, even when the prior partition had
        # no labelled clusters to carry over.
        "unlabeled_clusters": unlabeled,
        "largest_community": max(sizes) if sizes else 0,
        "fragile_bridges": fragile_count,
        "inferred_extracted_ratio": inferred_extracted_ratio,
        "inferred_weight_share": inferred_weight_share,
        "hysteresis_share": hysteresis_share,
    }


def _read_prev_health() -> dict | None:
    """Return the last JSONL record from _health-log.jsonl, or None.

    Read happens BEFORE _append_health_log adds the current build's row,
    so it's truly the previous build's snapshot. Tolerant to malformed
    lines (e.g. truncated final write) — falls back to None silently.
    """
    if not HEALTH_LOG_PATH.exists():
        return None
    try:
        with HEALTH_LOG_PATH.open(encoding="utf-8") as fh:
            lines = [l for l in fh if l.strip()]
        if not lines:
            return None
        return json.loads(lines[-1])
    except (OSError, ValueError):
        return None


def _format_trend_lines(curr: dict, prev: dict | None) -> list[str]:
    """Compose trend lines comparing current build to previous health-log entry.

    Two parts:
      1. Δ% across key metrics — always shown if a previous entry exists.
      2. Threshold-violation advisories — surfaced when G3 thresholds are
         crossed. Informational (not added to actionable count); same
         posture as [F] orphan labels and [G] fragile bridges.
    """
    if not prev:
        return []

    def pct(c: float, p: float) -> float | None:
        if p in (0, None):
            return None
        return (c - p) / p * 100

    headline_metrics = [
        ("nodes", "nodes"),
        ("edges", "edges"),
        ("edges_per_node", "e/n"),
        ("communities", "comms"),
        ("largest_community", "largest"),
    ]
    deltas: list[str] = []
    for key, label in headline_metrics:
        c = curr.get(key, 0)
        p = prev.get(key, 0)
        d = pct(c, p)
        if d is None:
            continue
        if abs(d) < 0.05:
            deltas.append(f"{label} ±0.0%")
        else:
            deltas.append(f"{label} {d:+.1f}%")

    lines: list[str] = []
    if deltas:
        lines.append(f"  trend vs prev build: {', '.join(deltas)}")

    # G3 thresholds — informational advisories, do not affect exit code.
    violations: list[str] = []
    inf_ratio = curr.get("inferred_extracted_ratio", 0)
    if inf_ratio is None:
        # ext_count == 0 with inferred edges present — ratio undefined, the
        # worst signal-quality state. Always an advisory.
        violations.append(
            f"⚠ INFERRED/EXTRACTED ratio=∞ (0 EXTRACTED hub-hub edges) — "
            f"auto-inference layer carrying the graph alone (no author wikilinks)"
        )
    elif inf_ratio > INFERRED_RATIO_THRESHOLD:
        violations.append(
            f"⚠ INFERRED/EXTRACTED ratio={inf_ratio:.2f} > "
            f"{INFERRED_RATIO_THRESHOLD:.2f} — auto-inference layer producing "
            f"more edges than author wikilinks (weak-signal inflation)"
        )
    inf_share = curr.get("inferred_weight_share", 0)
    if inf_share > INFERRED_WEIGHT_THRESHOLD:
        violations.append(
            f"⚠ INFERRED weight share={inf_share:.1%} > "
            f"{INFERRED_WEIGHT_THRESHOLD:.0%} — co-citation heuristics outweighing "
            f"author intent in Leiden modularity"
        )
    edges_pct = pct(curr.get("edges", 0), prev.get("edges", 0))
    nodes_pct = pct(curr.get("nodes", 0), prev.get("nodes", 0))
    if (
        edges_pct is not None and nodes_pct is not None
        and nodes_pct > 0 and edges_pct > EDGE_INFLATION_RATIO * nodes_pct
    ):
        violations.append(
            f"⚠ edges {edges_pct:+.1f}% > {EDGE_INFLATION_RATIO}× nodes "
            f"{nodes_pct:+.1f}% — edge inflation without proportional data growth"
        )
    # Hysteresis only meaningful when previous build had labels to carry over
    if prev.get("hysteresis_share") is not None:
        hyst = curr.get("hysteresis_share", 0)
        # Skip flag if no labels needed carrying (prev had no matched labels)
        prev_matched = (prev.get("communities", 0) or 0) - (prev.get("unlabeled_clusters", 0) or 0)
        if prev_matched > 0 and hyst < HYSTERESIS_FLOOR:
            violations.append(
                f"⚠ hysteresis carry-over={hyst:.1%} < {HYSTERESIS_FLOOR:.0%} "
                f"— stable labels not surviving Leiden re-balance"
            )

    if violations:
        lines.append("")
        for v in violations:
            lines.append(f"  {v}")
        lines.append(
            "  Trend advisories are informational. See log.md "
            "[2026-04-30] G1+B entry for tuning history."
        )

    return lines


def _append_health_log(metrics: dict) -> None:
    """Append one JSONL record per invocation for trend analysis.

    Non-fatal on write failure — lint reporting must not be blocked by
    disk issues. Advisory only.
    """
    try:
        HEALTH_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with HEALTH_LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(metrics, ensure_ascii=False) + "\n")
    except OSError:
        pass


def run(json_out: bool = False, fix: bool = False) -> int:
    if fix:
        _regenerate_sot()

    if not CLUSTERS_PATH.exists():
        print(f"ERROR: {CLUSTERS_PATH} not found. Run `python tools/build.py clusters` first.", file=sys.stderr)
        return 1

    data = json.loads(CLUSTERS_PATH.read_text(encoding="utf-8"))
    clusters = data.get("clusters", [])
    isolated = data.get("isolated_hubs", [])
    unassigned = data.get("unassigned_sources", [])

    small = [c for c in clusters if c["size"] < MIN_SIZE]
    mixed = [c for c in clusters if c["coherence"] == "mixed" and c["size"] >= MIN_MIXED_SIZE]
    unlabeled = [c for c in clusters if c["matched_label_slug"] is None]

    # [G] Fragile bridges — inter-cluster edges where a community pair is
    # held together by a single link. Requires _graph.json to resolve
    # actual edges; if missing (e.g. standalone cluster check), skip with
    # empty result — metrics still populate the log for trend continuity.
    fragile: list[dict] = []
    graph_data: dict = {}
    if GRAPH_PATH.exists():
        try:
            graph_data = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
            fragile = _find_fragile_bridges(graph_data, data)
        except (ValueError, OSError):
            graph_data = {}

    # G3 M-2: read previous build's snapshot BEFORE appending current row,
    # so the trend formatter compares against the genuine prior state.
    prev_health = _read_prev_health()
    health = _compute_health(graph_data, data, len(fragile))
    _append_health_log(health)

    # [F] Orphan labels — defined in cluster_labels.json but no matching
    # community in this Leiden run. Emerges when a cluster dissolves
    # (members absorbed into other communities) or when anchor_members
    # drift apart from actual wiki linkage. Informational only: label
    # removal is domain judgment per CLAUDE.md, so lint flags but does
    # not auto-prune.
    labels_defined: list[str] = []
    if LABELS_PATH.exists():
        try:
            labels_data = json.loads(LABELS_PATH.read_text(encoding="utf-8"))
            labels_defined = [
                l.get("slug") for l in labels_data.get("labels", [])
                if isinstance(l, dict) and l.get("slug")
            ]
        except (ValueError, OSError):
            pass
    cluster_slugs = {c["slug"] for c in clusters}
    orphan_labels = [s for s in labels_defined if s not in cluster_slugs]

    # [C] Mixed clusters reflect cross-cutting themes (top-tag share < 25%),
    # which is often a natural domain characteristic rather than a defect.
    # Reported below as informational with anchor-refinement suggestions,
    # but excluded from the pass/fail count so reviewers aren't forced to
    # flatten genuine cross-cutting taxonomies. Use `graph/cluster_labels.json`
    # anchor_members edits to shift a cluster's center of gravity when desired.
    issues_total = len(isolated) + len(small) + len(unlabeled) + len(unassigned)

    if json_out:
        out = {
            "stats": data.get("stats", {}),
            "health": health,
            "isolated_hubs": isolated,
            "small_clusters": [{"slug": c["slug"], "size": c["size"], "members": c["member_labels"]} for c in small],
            "mixed_clusters": [
                {"slug": c["slug"], "size": c["size"], "top_tags": c["top_tags"], "coherence": c["coherence"]}
                for c in mixed
            ],
            "unlabeled_clusters": [
                {"id": c["id"], "size": c["size"], "top_tags": c["top_tags"], "sample_members": c["member_labels"][:5]}
                for c in unlabeled
            ],
            "unassigned_sources": unassigned,
            "orphan_labels": orphan_labels,
            "fragile_bridges": fragile,
            "actionable": issues_total,
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0 if issues_total == 0 else 1

    print(f"Clusters: {len(clusters)}  (method={data.get('method')}, seed={data.get('seed')})")
    stats = data.get("stats", {})
    print(f"  hubs: {stats.get('hub_nodes')} clustered + {stats.get('isolated_hubs')} isolated")
    print(f"  sources: {stats.get('sources_assigned')} assigned + {stats.get('sources_unassigned')} unassigned")
    print(
        f"  health: {health['nodes']}N / {health['edges']}E "
        f"(edges/node={health['edges_per_node']}) · "
        f"orphan-hub={health['isolated_hub_rate']:.1%} · "
        f"communities={health['communities']} (largest={health['largest_community']}) · "
        f"fragile-bridges={health['fragile_bridges']}"
    )
    print(f"  trend log: {HEALTH_LOG_PATH}")
    # ratio is None when there are 0 EXTRACTED hub-hub edges (undefined) — show ∞.
    _ratio = health.get("inferred_extracted_ratio", 0)
    _ratio_str = "∞" if _ratio is None else f"{_ratio:.2f}"
    print(
        f"  signal: INFERRED/EXTRACTED ratio={_ratio_str} · "
        f"INFERRED weight share={health.get('inferred_weight_share', 0):.1%} · "
        f"hysteresis carry-over={health.get('hysteresis_share', 0):.1%}"
    )
    for line in _format_trend_lines(health, prev_health):
        print(line)
    print()

    def _print_orphan_labels() -> None:
        if not orphan_labels:
            return
        print(f"[F] Orphan labels (defined in {LABELS_PATH} but no matching community) — {len(orphan_labels)}:")
        for s in orphan_labels:
            print(f"     '{s}' — cluster dissolved or anchor_members drift. Whether to remove the label is an editorial call.")
        print("     Informational — outside the actionable count (CLAUDE.md naming rule: no automatic editing).")
        print()

    def _print_fragile_bridges() -> None:
        if not fragile:
            return
        print(f"[G] Fragile bridges (cluster pairs connected by ≤{FRAGILE_EDGE_THRESHOLD} edge) — {len(fragile)}:")
        for fb in fragile:
            sample = fb["sample_edge"]
            label_suffix = f" — {sample['label']}" if sample.get("label") else ""
            print(f"     {fb['cluster_a']} ↔ {fb['cluster_b']} ({fb['edge_count']} edge): {sample['from']} → {sample['to']}{label_suffix}")
        print("     Informational — severing the single edge would split the two domains. Reinforce with cross-references if the relation is real, or accept it if they are genuinely distant domains.")
        print()

    if not issues_total:
        print("OK — no actionable cluster issues.")
        if orphan_labels or fragile:
            print()
            _print_orphan_labels()
            _print_fragile_bridges()
        return 0

    if isolated:
        print(f"[A] Isolated hubs (no edges, excluded from clustering) — {len(isolated)}:")
        for h in isolated[:20]:
            print(f"     {h}")
        if len(isolated) > 20:
            print(f"     ... and {len(isolated) - 20} more. Add [[wikilinks]] from sources or hubs.")
        print()

    if small:
        print(f"[B] Small clusters (size < {MIN_SIZE}) — {len(small)}:")
        for c in small:
            print(f"     #{c['id']} [{c['slug']}] size={c['size']}: {', '.join(c['member_labels'][:5])}")
        print("     Tuning suggestion: consider merging with a neighbor, or adjusting resolution.")
        print()

    if mixed:
        print(f"[C] Mixed clusters (coherence='mixed', size>={MIN_MIXED_SIZE}) — {len(mixed)}:")
        for c in mixed:
            tags = ", ".join(f"{t}({n})" for t, n in c["top_tags"][:3])
            print(f"     #{c['id']} [{c['slug']}] size={c['size']} tags: {tags}")
            # Anchor refinement proposal — show members representing each of
            # the top 3 tags so the reviewer sees candidate anchor hubs
            # without leaving the report. Actual anchor_members edit stays
            # human-approved (naming = domain judgment, per CLAUDE.md).
            top_members = c.get("member_labels", [])[:6]
            if top_members:
                print(f"        sample members: {', '.join(top_members)}")
            print(
                f"        suggestion: pick 5~10 hubs from this cluster aligned with "
                f"'{c['top_tags'][0][0] if c.get('top_tags') else '<focus tag>'}' and "
                f"add to `anchor_members` in {LABELS_PATH} (no automatic editing by Claude · human approval required)."
            )
        print(f"     Action: refine anchor_members in {LABELS_PATH}, or accept as cross-cutting theme.")
        print()

    if unlabeled:
        print(f"[D] Unlabeled clusters (no match in {LABELS_PATH}) — {len(unlabeled)}:")
        for c in unlabeled:
            tags = ", ".join(f"{t}({n})" for t, n in c["top_tags"][:3])
            sample = ", ".join(c["member_labels"][:4])
            print(f"     #{c['id']} auto-slug='{c['slug']}' size={c['size']}")
            print(f"        top_tags: {tags}")
            print(f"        sample:   {sample}")
        print(f"     Action: add a {{slug, name, anchor_members}} entry to {LABELS_PATH} and rerun.")
        print()

    if unassigned:
        print(f"[E] Unassigned sources (no clustered hub link) — {len(unassigned)}:")
        for s in unassigned[:15]:
            print(f"     {s}")
        if len(unassigned) > 15:
            print(f"     ... and {len(unassigned) - 15} more. Add [[wikilinks]] to entities/concepts.")
        print()

    _print_orphan_labels()
    _print_fragile_bridges()

    return 1
