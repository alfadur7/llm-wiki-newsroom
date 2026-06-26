"""Landscape axis builder — owns every cluster-indexed artefact.

Three concerns, one module per axis (mirrors contradictions.py on the
conflict axis):

  1. run()          — graph/_clusters.json (Leiden topology clustering
                      over entity+concept subgraph; propagates source
                      assignments; stable labels via cluster_labels.json).
  2. run_catalogs() — wiki/sources/_catalog-<cluster>.md + _catalog.md
                      (per-cluster source listings; migrated from index.py
                      in the Phase B pipeline refactor).
  3. run_pages()    — wiki/overviews/<cluster>.md (L2-3) + wiki/overview.md
                      (L2-4) AUTO-block regeneration. EDITOR blocks are
                      preserved; files without AUTO markers are skipped
                      so hand-authored content is never overwritten.

Pipeline ordering (tools/build.py): graph → clusters → contradictions → index.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date as _date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import (  # noqa: E402
    WIKI,
    _build_id_map,
    atomic_write_if_changed,
    atomic_write_text,
    graph_structure_fingerprint,
    parse_frontmatter,
    parse_page_meta,
    read_source_date,
    safe_link_text,
    update_auto_block,
)

GRAPH_PATH = Path("graph/_graph.json")
LABELS_PATH = Path("graph/cluster_labels.json")
OUTPUT_PATH = Path("graph/_clusters.json")

RESOLUTION = 1.0  # Leiden RB-Configuration resolution (Louvain-equivalent default).
                  # Migrated from NetworkX Louvain to leidenalg/python-igraph
                  # Leiden (Traag, Waltman, van Eck 2019) on 2026-04-25 to
                  # eliminate Louvain's modularity-degeneracy churn — at
                  # ~470 hubs the wiki was hitting cases where a 7-source
                  # ingest flipped community count 7→10 and migrated 86
                  # bank-it-modernization members across boundaries.
                  # Leiden's refinement step + connectivity guarantee makes
                  # community boundaries far more stable under incremental
                  # graph mutation while remaining deterministic for a
                  # fixed seed. Resolution semantics match Louvain.
SEED = 42
HUB_PREFIXES = ("entities/", "concepts/")
SOURCE_WEIGHT_THRESHOLD = 0.3  # sources list under every cluster with weight >= this
COHERENCE_THRESHOLD = 0.25      # top tag share required for "single"-tag coherence
                                # (wiki tag vocabulary is deliberately broad;
                                # 25% coverage already signals a dominant theme)
HYSTERESIS_THRESHOLD = 0.5      # Jaccard similarity threshold for treating a new
                                # community as continuation of a previous-build
                                # cluster — added 2026-04-30 to keep stable label
                                # slugs bound to the same hub-set across builds
                                # even when Leiden re-balances boundaries after
                                # large ingests. Reuses the previous-build label
                                # only if the prior label is still defined in
                                # cluster_labels.json; auto-labels (no anchor
                                # match) are NOT preserved — they're transient
                                # by design and must re-resolve each build.


def _slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[\s·/,()]+", "-", s)
    s = re.sub(r"[^a-z0-9\-가-힣]+", "", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "unlabeled"


# Local alias kept for backward compatibility within this module —
# delegates to the project-wide atomic_write_if_changed helper. Centralized
# implementation gives every build artefact temp+rename atomicity plus the
# dirty-check that avoids phantom-modified state in `git status`.
_write_if_changed = atomic_write_if_changed


def _collect_hub_tags() -> dict[str, list[str]]:
    hub_tags: dict[str, list[str]] = {}
    for subdir in ("entities", "concepts"):
        for p in sorted((WIKI / subdir).glob("*.md")):
            rel = f"{subdir}/{p.name}"
            fm = parse_frontmatter(p.read_text(encoding="utf-8", errors="replace"))
            tags = fm.get("tags", [])
            hub_tags[rel] = [t for t in tags if isinstance(t, str)] if isinstance(tags, list) else []
    return hub_tags


def _load_labels() -> list[dict]:
    if not LABELS_PATH.exists():
        return []
    data = json.loads(LABELS_PATH.read_text(encoding="utf-8"))
    return data.get("labels", [])


def _load_prev_membership() -> dict[str, int] | None:
    """Read previous-build hub → community-index mapping for Leiden warm-start.

    Distinct from `_load_prev_assignments` (label hysteresis): this captures
    the partition *structure* — every cluster including auto-labelled ones —
    so warm-start can preserve community boundaries even before stable labels
    settle. Returns None if no previous _clusters.json exists (cold-start
    fallback path).
    """
    if not OUTPUT_PATH.exists():
        return None
    try:
        prev = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    membership: dict[str, int] = {}
    for idx, c in enumerate(prev.get("clusters", [])):
        for hub in c.get("members", []):
            membership[hub] = idx
    return membership or None


def _compute_initial_membership(
    G_nx, sorted_nodes: list[str], prev_membership: dict[str, int] | None
) -> list[int] | None:
    """Build per-vertex initial community list for Leiden warm-start.

    Each vertex (in `sorted_nodes` order, matching igraph index assignment) is
    assigned an initial community by:
      1. **Direct lookup** — if the hub was in the prior partition, reuse its
         community index. Identity-preserving for unchanged hubs.
      2. **Neighborhood inheritance** — if the hub is new (or renamed; same
         from the algorithm's POV), assign the modal community of its in-graph
         neighbors that *were* in the prior partition. Renamed hubs land in
         their old community because their inbound edges all point to the
         same prior community as before.
      3. **Fresh community** — if no neighbors map to the prior partition
         (rare: isolated new component), allocate a new community index.

    Returns None when prev_membership is None (cold-start path).
    """
    if prev_membership is None:
        return None
    n_prev_comms = max(prev_membership.values()) + 1 if prev_membership else 0
    next_fresh = n_prev_comms

    initial: list[int] = []
    for node in sorted_nodes:
        if node in prev_membership:
            initial.append(prev_membership[node])
            continue
        neighbor_comms = [
            prev_membership[n]
            for n in G_nx.neighbors(node)
            if n in prev_membership
        ]
        if neighbor_comms:
            counts = Counter(neighbor_comms)
            top = max(counts.values())
            initial.append(min(c for c, n in counts.items() if n == top))
        else:
            initial.append(next_fresh)
            next_fresh += 1
    return initial


def _load_prev_assignments() -> dict[str, set[str]]:
    """Read previous-build cluster -> members mapping for hysteresis matching.

    Returns dict of stable label slug -> set(member ids) for clusters whose
    previous-build assignment came from cluster_labels.json (i.e. had a
    matched_label_slug). Auto-labelled clusters from the previous build are
    excluded — those slugs are transient (e.g. `ai-llm-ai` synthesised on the
    fly when no cluster_labels.json entry matched) and must re-resolve each
    build, otherwise hysteresis would lock in noise.

    Multi-match labels can map a single slug to multiple communities; we
    union their members so the next build's Jaccard test can match either
    half of the previously-split community.
    """
    if not OUTPUT_PATH.exists():
        return {}
    try:
        prev = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    out: dict[str, set[str]] = {}
    for c in prev.get("clusters", []):
        slug = c.get("matched_label_slug")
        members = c.get("members") or []
        if not slug or not members:
            continue
        out.setdefault(slug, set()).update(members)
    return out


def _match_labels(
    communities: list[set[str]],
    labels: list[dict],
    prev_assignments: dict[str, set[str]] | None = None,
) -> list[dict]:
    """Assign each community a stable slug via two-pass matching.

    Pass 1 — Hysteresis: a community whose member-set has Jaccard >=
    HYSTERESIS_THRESHOLD with a previous-build cluster's member-set inherits
    that previous label, but only if the label is still defined in
    cluster_labels.json. This binds 'same community' (in the hub-set sense)
    to 'same slug' across builds even when Leiden boundaries re-balance.

    Pass 2 — Anchor containment: remaining unassigned communities run the
    pre-existing greedy match by `anchor_members` containment, robust against
    cluster-size asymmetry.

    Greedy ordering inside each pass: highest-quality match (Jaccard for
    pass 1, containment for pass 2) wins first. Each community is claimed
    at most once. Each label is claimed at most once UNLESS it has
    `multi_match: true` — then multiple communities can share that slug
    (used when the topology intentionally splits a theme).

    Per-label `match_threshold` (default 0.5) applies only to pass 2.
    """
    default_threshold = 0.5
    assignments: list[dict | None] = [None] * len(communities)
    taken_labels: set[str] = set()
    label_by_slug = {lbl["slug"]: lbl for lbl in labels}

    # Pass 1: Hysteresis — preserve label slugs across builds.
    if prev_assignments:
        hyst_candidates: list[tuple[float, int, int, int, str]] = []
        for ci, comm in enumerate(communities):
            for slug, prev_members in prev_assignments.items():
                if slug not in label_by_slug:
                    continue  # prev label removed from cluster_labels.json
                union = comm | prev_members
                if not union:
                    continue
                inter = comm & prev_members
                jaccard = len(inter) / len(union)
                if jaccard >= HYSTERESIS_THRESHOLD:
                    hyst_candidates.append(
                        (jaccard, len(inter), -len(comm), ci, slug)
                    )

        hyst_candidates.sort(reverse=True)
        for jaccard, _inter, _neg_size, ci, slug in hyst_candidates:
            if assignments[ci] is not None:
                continue
            lbl = label_by_slug[slug]
            multi = bool(lbl.get("multi_match", False))
            if (not multi) and slug in taken_labels:
                continue
            anchors = set(lbl.get("anchor_members", []))
            anchor_hits = len(communities[ci] & anchors) if anchors else 0
            assignments[ci] = {
                "slug": slug,
                "name": lbl.get("name", slug),
                "color": lbl.get("color"),
                "matched_label_slug": slug,
                "containment": round(anchor_hits / len(anchors), 3) if anchors else None,
                "anchor_hits": anchor_hits,
                "multi_match": multi,
                "match_method": "hysteresis",
                "hysteresis_jaccard": round(jaccard, 3),
            }
            if not multi:
                taken_labels.add(slug)

    # Pass 2: Anchor containment for remaining communities.
    candidates: list[tuple[float, int, int, int, int]] = []
    for ci, comm in enumerate(communities):
        if assignments[ci] is not None:
            continue
        for li, lbl in enumerate(labels):
            anchors = set(lbl.get("anchor_members", []))
            if not anchors:
                continue
            inter = len(comm & anchors)
            containment = inter / len(anchors)
            if inter > 0:
                candidates.append((containment, inter, -len(comm), ci, li))

    candidates.sort(reverse=True)
    for containment, inter, _neg_size, ci, li in candidates:
        lbl = labels[li]
        if assignments[ci] is not None:
            continue
        multi = bool(lbl.get("multi_match", False))
        if (not multi) and lbl["slug"] in taken_labels:
            continue
        threshold = float(lbl.get("match_threshold", default_threshold))
        if containment < threshold:
            continue  # per-label threshold, keep scanning other (label,community) pairs
        assignments[ci] = {
            "slug": lbl["slug"],
            "name": lbl.get("name", lbl["slug"]),
            "color": lbl.get("color"),
            "matched_label_slug": lbl["slug"],
            "containment": round(containment, 3),
            "anchor_hits": inter,
            "multi_match": multi,
            "match_method": "anchor",
        }
        if not multi:
            taken_labels.add(lbl["slug"])

    return assignments  # may contain None entries for unmatched


def _auto_label(top_tags: list[tuple[str, int]], members: list[str], existing_slugs: set[str]) -> dict:
    """Fallback label from top tags or first member; guarantee unique slug."""
    base = "-".join(t for t, _ in top_tags[:2]) if top_tags else members[0].rsplit("/", 1)[-1].removesuffix(".md")
    slug = _slugify(base)
    candidate = slug
    i = 2
    while candidate in existing_slugs:
        candidate = f"{slug}-{i}"
        i += 1
    return {"slug": candidate, "name": base, "matched_label_slug": None, "containment": None, "anchor_hits": 0}


def _run_leiden(
    G_nx, resolution: float, seed: int,
    initial_membership: list[int] | None = None,
) -> list[set[str]]:
    """Run Leiden community detection on a NetworkX weighted graph.

    Convert to igraph (leidenalg requires igraph), run RB-Configuration
    quality function (Louvain-equivalent so the `resolution` value is
    directly comparable to the prior Louvain resolution), and project
    each partition back to the NetworkX node-id namespace.

    Node order is sorted before conversion to keep the igraph vertex
    indices reproducible — combined with a fixed `seed` this makes the
    pipeline deterministic for identical input graphs.

    `initial_membership` (warm-start): when supplied as a length-N list of
    community indices (one per vertex in sorted node order), Leiden begins
    refinement from this partition instead of singletons. Use to preserve
    cluster boundaries across hub-rename / small-ingest perturbations
    (alphabetical sort key change → vertex index reshuffle → cold-start
    Leiden lands at a different local optimum). Pass None for cold start.
    """
    import igraph as ig
    import leidenalg

    nodes = sorted(G_nx.nodes())
    node_idx = {n: i for i, n in enumerate(nodes)}
    edges = [(node_idx[u], node_idx[v]) for u, v in G_nx.edges()]
    weights = [G_nx[u][v].get("weight", 1.0) for u, v in G_nx.edges()]

    g_ig = ig.Graph(n=len(nodes), edges=edges, edge_attrs={"weight": weights})
    g_ig.vs["name"] = nodes

    kwargs = {
        "weights": "weight",
        "resolution_parameter": resolution,
        "seed": seed,
    }
    if initial_membership is not None:
        kwargs["initial_membership"] = initial_membership

    partition = leidenalg.find_partition(
        g_ig,
        leidenalg.RBConfigurationVertexPartition,
        **kwargs,
    )
    return [set(g_ig.vs[i]["name"] for i in c) for c in partition]


def build_hub_graph(verbose: bool = True):
    """Reconstruct the hub-only weighted subgraph from `graph/_graph.json`.

    Same construction as `run()`'s pre-Leiden block, exposed for callers
    (e.g., lint drift check) that need the graph but not the partition.
    Returns (G, hub_labels, raw_data, id_map, isolated_hubs). Edge weights
    match RBConfiguration semantics (EXTRACTED 1.0, INFERRED += confidence).
    `raw_data` and `id_map` are returned for callers that need to walk
    sources after partitioning (avoids reloading _graph.json).
    `isolated_hubs` is the list removed from G (degree-0 nodes — appear in
    summary stats but excluded from clustering).
    """
    import networkx as nx

    if not GRAPH_PATH.exists():
        raise SystemExit("graph/_graph.json not found. Run `python tools/build.py graph` first.")

    data = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    nodes = data["nodes"]
    edges = data["edges"]
    id_map = _build_id_map(nodes)

    hub_ids = {n["id"] for n in nodes if n["id"].startswith(HUB_PREFIXES)}
    hub_labels = {n["id"]: n.get("label", n["id"]) for n in nodes if n["id"] in hub_ids}

    G = nx.Graph()
    G.add_nodes_from(sorted(hub_ids))

    weights: dict[tuple[str, str], float] = defaultdict(float)
    for e in edges:
        src = id_map.get(e.get("from"))
        dst = id_map.get(e.get("to"))
        if not src or not dst or src == dst:
            continue
        if src not in hub_ids or dst not in hub_ids:
            continue
        a, b = sorted([src, dst])
        if e.get("type") == "EXTRACTED":
            weights[(a, b)] += 1.0
        elif e.get("type") == "INFERRED":
            weights[(a, b)] += float(e.get("confidence", 0.5))

    for (a, b), w in weights.items():
        G.add_edge(a, b, weight=w)

    isolated_hubs = [n for n in G.nodes if G.degree(n) == 0]
    G.remove_nodes_from(isolated_hubs)

    if verbose:
        print(f"Hub subgraph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        print(f"Isolated hubs (excluded from clustering): {len(isolated_hubs)}")

    return G, hub_labels, data, id_map, isolated_hubs


def run(cold: bool = False) -> None:
    """Build _clusters.json. cold=True forces fresh Leiden (singleton start);
    default uses warm-start from previous _clusters.json when available."""
    try:
        import igraph  # noqa: F401
        import leidenalg  # noqa: F401
    except ImportError:
        raise SystemExit(
            "leidenalg/igraph not installed. Run: python -m pip install 'igraph' 'leidenalg'"
        )

    # Load previous-build assignments BEFORE we start writing the new
    # _clusters.json — hysteresis needs the prior member-sets intact.
    prev_assignments = _load_prev_assignments()

    G, hub_labels, data, id_map, isolated_hubs = build_hub_graph(verbose=True)
    edges = data["edges"]

    # Warm-start: inherit previous-build partition as Leiden initial state.
    # Stabilises cluster boundaries against hub-rename / small-ingest
    # perturbations that would otherwise reroll vertex indices via the
    # alphabetical sort key. `--cold` forces a fresh singleton start
    # (use periodically to escape stale local optima).
    sorted_hubs = sorted(G.nodes())
    prev_membership = None if cold else _load_prev_membership()
    initial_membership = _compute_initial_membership(G, sorted_hubs, prev_membership)
    if initial_membership is not None:
        n_known = sum(1 for n in sorted_hubs if n in (prev_membership or {}))
        n_inherited = len(sorted_hubs) - n_known
        print(
            f"Warm-start: {n_known} hubs from prior partition + "
            f"{n_inherited} via neighborhood inheritance"
        )
    else:
        reason = "--cold" if cold else "no prior _clusters.json"
        print(f"Cold-start ({reason})")

    communities_raw = _run_leiden(
        G, resolution=RESOLUTION, seed=SEED,
        initial_membership=initial_membership,
    )
    communities = [
        set(c) for c in sorted(communities_raw, key=lambda c: (-len(c), min(c)))
    ]
    print(f"Communities found: {len(communities)} (Leiden, RB-Configuration)")

    labels = _load_labels()
    label_assignments = _match_labels(communities, labels, prev_assignments)
    used_slugs: set[str] = {la["slug"] for la in label_assignments if la}
    hyst_count = sum(1 for la in label_assignments if la and la.get("match_method") == "hysteresis")
    if prev_assignments:
        print(
            f"Hysteresis: {hyst_count}/{sum(1 for la in label_assignments if la)} "
            f"matched labels carried over from previous build "
            f"(Jaccard >= {HYSTERESIS_THRESHOLD})"
        )

    hub_tags = _collect_hub_tags()

    clusters_out: list[dict] = []
    hub_assignments: dict[str, str] = {}

    for idx, comm in enumerate(communities):
        members = sorted(comm)
        tag_counter: Counter = Counter()
        for m in members:
            for t in hub_tags.get(m, []):
                tag_counter[t] += 1
        top_tags = tag_counter.most_common(5)

        la = label_assignments[idx]
        if la is None:
            la = _auto_label(top_tags, members, used_slugs)
            used_slugs.add(la["slug"])

        if top_tags and members:
            dominant = top_tags[0][1]
            coherence = "single" if dominant / len(members) >= COHERENCE_THRESHOLD else "mixed"
        else:
            coherence = "untagged"

        for m in members:
            hub_assignments[m] = la["slug"]

        clusters_out.append({
            "id": idx,
            "slug": la["slug"],
            "name": la["name"],
            "color": la.get("color"),
            "matched_label_slug": la["matched_label_slug"],
            "containment": la.get("containment"),
            "anchor_hits": la.get("anchor_hits"),
            "match_method": la.get("match_method"),
            "hysteresis_jaccard": la.get("hysteresis_jaccard"),
            "size": len(members),
            "members": members,
            "member_labels": [hub_labels.get(m, m) for m in members],
            "top_tags": top_tags,
            "coherence": coherence,
        })

    # Propagate to sources via weighted vote of linked hubs (approach B).
    source_linked_hubs: dict[str, Counter] = defaultdict(Counter)
    for e in edges:
        src = e.get("from", "")
        dst = id_map.get(e.get("to"))
        if not src.startswith("sources/") or dst not in hub_assignments:
            continue
        if e.get("type") == "EXTRACTED":
            source_linked_hubs[src][hub_assignments[dst]] += 1.0
        elif e.get("type") == "INFERRED":
            source_linked_hubs[src][hub_assignments[dst]] += float(e.get("confidence", 0.5))

    source_assignments: dict[str, dict] = {}
    for src, vote in source_linked_hubs.items():
        total = sum(vote.values())
        if not total:
            continue
        weights_norm = {slug: round(c / total, 3) for slug, c in vote.items()}
        primary = max(weights_norm.items(), key=lambda kv: kv[1])[0]
        source_assignments[src] = {"primary": primary, "weights": weights_norm}

    unassigned_sources = [
        n["id"] for n in data["nodes"]
        if n["id"].startswith("sources/") and n["id"] not in source_assignments
    ]

    mixed_clusters = sum(1 for c in clusters_out if c["coherence"] == "mixed")
    unlabeled = sum(1 for c in clusters_out if c["matched_label_slug"] is None)

    out = {
        "method": "leiden",
        "graph_fingerprint": graph_structure_fingerprint(data),
        "resolution": RESOLUTION,
        "seed": SEED,
        "source_weight_threshold": SOURCE_WEIGHT_THRESHOLD,
        "coherence_threshold": COHERENCE_THRESHOLD,
        "hysteresis_threshold": HYSTERESIS_THRESHOLD,
        "stats": {
            "hub_nodes": G.number_of_nodes(),
            "hub_edges": G.number_of_edges(),
            "isolated_hubs": len(isolated_hubs),
            "cluster_count": len(clusters_out),
            "mixed_clusters": mixed_clusters,
            "unlabeled_clusters": unlabeled,
            "hysteresis_carried": hyst_count,
            "sources_assigned": len(source_assignments),
            "sources_unassigned": len(unassigned_sources),
        },
        "clusters": clusters_out,
        "hub_assignments": hub_assignments,
        "source_assignments": source_assignments,
        "isolated_hubs": sorted(isolated_hubs),
        "unassigned_sources": sorted(unassigned_sources),
    }
    atomic_write_if_changed(
        OUTPUT_PATH, json.dumps(out, ensure_ascii=False, indent=2)
    )
    print(f"\nWritten: {OUTPUT_PATH}")

    print("\nClusters:")
    for c in clusters_out:
        tag_str = ", ".join(f"{t}({n})" for t, n in c["top_tags"][:3]) or "—"
        tag_marker = "○" if c["matched_label_slug"] else "✎"  # ✎ = needs labeling
        print(f"  {tag_marker} #{c['id']:2d}  [{c['slug']:30s}]  size={c['size']:3d}  {c['coherence']:8s}  tags: {tag_str}")

    print(f"\nSources: {len(source_assignments)} assigned, {len(unassigned_sources)} unassigned")
    if unlabeled:
        print(f"\n{unlabeled} cluster(s) have no label match — review graph/cluster_labels.json")
    if mixed_clusters:
        print(f"{mixed_clusters} cluster(s) flagged 'mixed' (top tag <{int(COHERENCE_THRESHOLD*100)}% coverage) — candidates for label refinement")


# ============================================================
# Catalog generation (migrated from index.py in Phase B refactor)
# ============================================================

SOURCES_DIR = WIKI / "sources"
OVERVIEWS_DIR = WIKI / "overviews"


def _load_clusters_data() -> dict:
    if not OUTPUT_PATH.exists():
        raise SystemExit(
            f"{OUTPUT_PATH} not found. Run `python tools/build.py clusters` first."
        )
    return json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))


def _scan_sources() -> list[tuple]:
    """Return list of (title, rel_path, desc, source_file, date, source_url) for wiki/sources/*.md."""
    out: list[tuple] = []
    if not SOURCES_DIR.exists():
        return out
    for f in sorted(os.listdir(SOURCES_DIR)):
        if not f.endswith(".md") or f.startswith("_catalog"):
            continue
        fp = SOURCES_DIR / f
        content = fp.read_text(encoding="utf-8", errors="replace")
        title, page_type, description, source_file, date, source_url = parse_page_meta(content, f)
        out.append((title, f"sources/{f}", description, source_file, date, source_url))
    return out


def _group_sources_by_cluster(
    sources: list[tuple],
    clusters_data: dict,
) -> tuple[dict[str, list], dict[str, dict]]:
    """Map cluster slug -> [(title, path, desc, tag_str, date), ...] (weight >= threshold).

    Also returns cluster_meta (slug -> cluster dict) for downstream formatting.
    """
    source_assignments = clusters_data.get("source_assignments", {})
    cluster_meta = {c["slug"]: c for c in clusters_data.get("clusters", [])}
    threshold = float(clusters_data.get("source_weight_threshold", 0.3))

    cluster_files: dict[str, list] = {}
    for title, path, desc, _source_file, date, _source_url in sources:
        entry = source_assignments.get(path)
        if not entry:
            continue
        weights = entry.get("weights", {})
        matched = [slug for slug, w in weights.items() if w >= threshold]
        if not matched:
            matched = [entry["primary"]]
        tag_str = ", ".join(cluster_meta[s]["name"] for s in matched if s in cluster_meta) if len(matched) > 1 else ""
        for slug in matched:
            cluster_files.setdefault(slug, []).append((title, path, desc, tag_str, date))

    for slug in cluster_files:
        cluster_files[slug].sort(key=lambda x: x[4] or "0000-00-00", reverse=True)
    return cluster_files, cluster_meta


def _link_display(title: str) -> str:
    """Bracket-safe, length-capped display text for a source catalog link.

    Sanitize before truncating so the cap never severs a multi-char sequence.
    """
    s = safe_link_text(title)
    return s[:45] + "…" if len(s) > 45 else s


def run_catalogs() -> None:
    """Regenerate wiki/sources/_catalog-<cluster>.md + _catalog.md.

    Migrated from index.py. Reads _clusters.json + scans wiki/sources/.
    Sources appear under every cluster where weight >= SOURCE_WEIGHT_THRESHOLD.
    """
    clusters_data = _load_clusters_data()
    sources = _scan_sources()
    cluster_files, _cluster_meta = _group_sources_by_cluster(sources, clusters_data)

    # Wipe stale per-cluster catalogs only (slug no longer produces output).
    # Keeping live catalogs lets _write_if_changed skip writes when content is
    # identical, avoiding phantom-modified state in git status.
    expected_slugs = {
        c["slug"] for c in clusters_data.get("clusters", [])
        if cluster_files.get(c["slug"])
    }
    for old in SOURCES_DIR.glob("_catalog-*.md"):
        slug = old.stem[len("_catalog-"):]
        if slug not in expected_slugs:
            old.unlink()

    # Aggregate hub size per slug (multi_match labels may span communities).
    slug_hub_size: dict[str, int] = {}
    for c in clusters_data.get("clusters", []):
        slug_hub_size[c["slug"]] = slug_hub_size.get(c["slug"], 0) + c["size"]

    catalog_summary: list[tuple] = []  # (display_name, count, catalog_filename, slug)
    emitted_slugs: set[str] = set()

    for c in clusters_data.get("clusters", []):
        slug = c["slug"]
        if slug in emitted_slugs:
            continue  # multi_match: same slug already written
        files = cluster_files.get(slug)
        if not files:
            continue
        name = c["name"]
        catalog_name = f"_catalog-{slug}.md"
        lines = [f"# Source Catalog: {name} ({len(files)})\n"]
        lines.append("[← Back to index](../index.md)\n")
        lines.append(f"> Cluster `{slug}` · Leiden topology-based · {slug_hub_size[slug]} hubs\n")
        for title, path, desc, tag_str, *_ in files:
            short = _link_display(title)
            rel = path.replace("sources/", "")
            tag_suffix = f" `[{tag_str}]`" if tag_str else ""
            if desc:
                lines.append(f"- [{short}]({rel}) — {desc}{tag_suffix}")
            else:
                lines.append(f"- [{short}]({rel}){tag_suffix}")
        _write_if_changed(SOURCES_DIR / catalog_name, "\n".join(lines) + "\n")
        catalog_summary.append((name, len(files), catalog_name, slug))
        emitted_slugs.add(slug)

    total_sources = len(sources)
    all_lines = [f"# Source Catalog: All ({total_sources})\n"]
    all_lines.append("[← Back to index](../index.md)\n")
    all_lines.append("> Clusters are auto-generated from Leiden topology — a source may be listed under multiple clusters.\n")
    seen_catalog_slugs: set[str] = set()
    for c in clusters_data.get("clusters", []):
        slug = c["slug"]
        if slug in seen_catalog_slugs:
            continue
        files = cluster_files.get(slug)
        if not files:
            continue
        seen_catalog_slugs.add(slug)
        all_lines.append(f"\n## {c['name']} ({len(files)})\n")
        for title, path, desc, tag_str, *_ in files:
            short = _link_display(title)
            rel = path.replace("sources/", "")
            tag_suffix = f" `[{tag_str}]`" if tag_str else ""
            if desc:
                all_lines.append(f"- [{short}]({rel}) — {desc}{tag_suffix}")
            else:
                all_lines.append(f"- [{short}]({rel}){tag_suffix}")
    _write_if_changed(SOURCES_DIR / "_catalog.md", "\n".join(all_lines) + "\n")

    print(f"Source catalogs: {len(catalog_summary)} clusters, {total_sources} total sources")
    for name, count, cname, _slug in sorted(catalog_summary, key=lambda x: -x[1]):
        print(f"  {name}: {count} -> sources/{cname}")


# ============================================================
# L2-3 overviews/<cluster>.md + L2-4 overview.md AUTO blocks
# ============================================================


def _intra_cluster_degree(graph_data: dict, members: list[str]) -> dict[str, float]:
    """Sum edge weights within a cluster for each member node."""
    id_map = _build_id_map(graph_data["nodes"])
    member_set = set(members)
    deg: dict[str, float] = defaultdict(float)
    for e in graph_data.get("edges", []):
        src = id_map.get(e.get("from"))
        dst = id_map.get(e.get("to"))
        if src not in member_set or dst not in member_set or src == dst:
            continue
        w = 1.0 if e.get("type") == "EXTRACTED" else float(e.get("confidence", 0.5))
        deg[src] += w
        deg[dst] += w
    return deg


def _render_members_block(cluster: dict, graph_data: dict, top_n: int = 15) -> str:
    """Render AUTO:MEMBERS body — top entities + concepts by intra-cluster degree."""
    members = cluster.get("members", [])
    deg = _intra_cluster_degree(graph_data, members)
    entities = [m for m in members if m.startswith("entities/")]
    concepts = [m for m in members if m.startswith("concepts/")]
    entities.sort(key=lambda m: (-deg.get(m, 0), m))
    concepts.sort(key=lambda m: (-deg.get(m, 0), m))

    def _fmt(items: list[str], cap: int) -> list[str]:
        lines = []
        for m in items[:cap]:
            stem = m.split("/", 1)[1].removesuffix(".md")
            lines.append(f"- [[{stem}]]")
        if len(items) > cap:
            lines.append(f"- … ({len(items)} total, see `graph/_clusters.json`)")
        return lines

    body: list[str] = [f"## Key Members (auto-extracted, top {top_n} by intra-cluster connectivity)", ""]
    body.append(f"**Entities** ({len(entities)})")
    body.extend(_fmt(entities, top_n) if entities else ["- _none_"])
    body.append("")
    body.append(f"**Concepts** ({len(concepts)})")
    body.extend(_fmt(concepts, top_n) if concepts else ["- _none_"])
    return "\n".join(body)


# The legacy `date:` field was split into `published:`/`scraped:` and removed


def _render_sources_block(cluster: dict, clusters_data: dict, top_n: int = 15) -> str:
    """Render AUTO:SOURCES body — top N sources by (weight, date, slug).

    Sort is a three-stage stable Timsort cascade:

      1. Tertiary: slug ascending (determinism — ensures identical ordering
         across builds when primary + secondary are both tied).
      2. Secondary: `date:` frontmatter descending (newer first). Surfaces
         editorially relevant recent sources when many sources share the
         maximum weight (w=1.0 is common for sources assigned primarily to
         a single cluster).
      3. Primary: weight descending.

    Stable sort preserves the tertiary order within equal secondary groups,
    and the secondary order within equal primary groups — so the final
    result is: highest weight first, ties broken by newest date, further
    ties broken alphabetically. This makes the AUTO:SOURCES block
    reproducible across builds (drift detectors can compare old vs new
    without false positives from dict-iteration shuffling).
    """
    slug = cluster["slug"]
    source_assignments = clusters_data.get("source_assignments", {})
    threshold = float(clusters_data.get("source_weight_threshold", 0.3))
    in_cluster: list[tuple[str, float, str]] = []
    for path, entry in source_assignments.items():
        w = entry.get("weights", {}).get(slug, 0.0)
        if w >= threshold:
            in_cluster.append((path, w, read_source_date(path)))

    # Three-stage stable sort (least significant key first)
    in_cluster.sort(key=lambda x: x[0])                    # tertiary: slug asc
    in_cluster.sort(key=lambda x: x[2], reverse=True)      # secondary: date desc
    in_cluster.sort(key=lambda x: -x[1])                   # primary: weight desc

    body: list[str] = ["## Sources", ""]
    body.append(f"{len(in_cluster)} total — see [{cluster['name']} catalog](../sources/_catalog-{slug}.md).")
    body.append("")
    body.append(f"Top {min(top_n, len(in_cluster))} by weight:")
    for path, w, _d in in_cluster[:top_n]:
        stem = path.removeprefix("sources/").removesuffix(".md")
        body.append(f"- [[{stem}]] _(w={w:.2f})_")
    return "\n".join(body)


def _skeleton_overview(cluster: dict) -> str:
    """New-file template for wiki/overviews/<slug>.md (when missing)."""
    today = _date.today().isoformat()
    return (
        f"---\n"
        f"title: \"{cluster['name']}\"\n"
        f"type: overview\n"
        f"tags: []\n"
        f"cluster: {cluster['slug']}\n"
        f"sources: []\n"
        f"last_updated: {today}\n"
        f"---\n\n"
        f"# {cluster['name']}\n\n"
        f"## Overview\n\n"
        f"_TODO: 2–4 paragraphs on what this field is, why it matters, and the scope accumulated in the wiki._\n\n"
        f"## Key Entities & Concepts\n\n"
        f"_TODO: Summarize the top members from the AUTO:MEMBERS block along with their roles and positions._\n\n"
        f"## Subtopics\n\n"
        f"_TODO: 2–4 sentences of commentary per subtopic + [[wikilinks]]._\n\n"
        f"## Key Trends & Figures\n\n"
        f"_TODO: Major events, figures, and recent examples._\n\n"
        f"<!-- AUTO:MEMBERS BEGIN -->\n"
        f"<!-- AUTO:MEMBERS END -->\n\n"
        f"<!-- AUTO:SOURCES BEGIN -->\n"
        f"<!-- AUTO:SOURCES END -->\n"
    )


def _update_overview_file(path: Path, cluster: dict, clusters_data: dict, graph_data: dict, created: bool) -> str:
    """Update AUTO blocks in an overview file. Returns status: 'created'|'updated'|'skipped'."""
    if created:
        atomic_write_text(path, _skeleton_overview(cluster))

    content = path.read_text(encoding="utf-8")
    members_body = _render_members_block(cluster, graph_data)
    sources_body = _render_sources_block(cluster, clusters_data)

    new_content, m_found = update_auto_block(content, "MEMBERS", members_body)
    new_content, s_found = update_auto_block(new_content, "SOURCES", sources_body)

    if not (m_found or s_found):
        return "skipped"

    if new_content != content:
        atomic_write_text(path, new_content)
    return "created" if created else "updated"


def _count_files(subdir: str) -> int:
    d = WIKI / subdir
    if not d.exists():
        return 0
    return sum(
        1 for f in os.listdir(d)
        if f.endswith(".md") and not f.startswith("_")
    )


def _render_stats_block(clusters_data: dict) -> str:
    """Render AUTO:STATS body for L2-4 overview.md — wiki-wide counts + cluster sizes."""
    sources = _scan_sources()
    n_sources = len(sources)
    n_entities = _count_files("entities")
    n_concepts = _count_files("concepts")
    n_overviews = _count_files("overviews")
    n_syntheses = _count_files("syntheses")
    n_trails = _count_files("trails")
    n_timelines = _count_files("timelines")

    dates = [d for (_t, _p, _desc, _sf, d, _su) in sources if d and re.match(r"\d{4}-\d{2}-\d{2}", d)]
    date_span = f"{min(dates)[:4]}~{max(dates)[:4]}" if dates else "date unknown"

    # Per-cluster source counts
    source_assignments = clusters_data.get("source_assignments", {})
    threshold = float(clusters_data.get("source_weight_threshold", 0.3))
    cluster_counts: dict[str, int] = {}
    for _path, entry in source_assignments.items():
        for slug, w in entry.get("weights", {}).items():
            if w >= threshold:
                cluster_counts[slug] = cluster_counts.get(slug, 0) + 1
    # unique cluster ordering: use clusters list (which is size-desc)
    ordered: list[tuple[str, int]] = []
    seen: set[str] = set()
    for c in clusters_data.get("clusters", []):
        slug = c["slug"]
        if slug in seen:
            continue
        seen.add(slug)
        ordered.append((c["name"], cluster_counts.get(slug, 0)))

    cluster_line = ", ".join(f"**{n}({count})**" for n, count in ordered)

    body = (
        f"This wiki is a knowledge base "
        f"comprising **{n_sources} source documents** ({date_span}), "
        f"**{n_entities} entities**, **{n_concepts} concepts**, "
        f"**{n_overviews} field overviews**, **{n_syntheses} analysis reports**, "
        f"**{n_trails} associative trails**, and **{n_timelines} timelines**.\n\n"
        f"Sources are automatically classified into {len(ordered)} topic clusters via Leiden "
        f"topology clustering: {cluster_line}. A single source may span multiple clusters "
        f"(listed in every catalog where its weight is ≥{threshold}); for the full cluster "
        f"list and members, see [[index]] or `graph/_clusters.json`."
    )
    return body


def run_pages(cluster: str | None = None, aggregate_only: bool = False) -> None:
    """Regenerate AUTO blocks in wiki/overviews/<cluster>.md + wiki/overview.md.

    cluster=None, aggregate_only=False — update every existing overviews/*.md
                                          with AUTO markers + the L2-4 aggregate.
    cluster="<slug>"                   — update or create the single overview file.
    aggregate_only=True                — update only wiki/overview.md (AUTO:STATS).

    Files without AUTO markers are skipped with a warning — never overwrites
    hand-authored content.
    """
    clusters_data = _load_clusters_data()
    clusters_by_slug = {c["slug"]: c for c in clusters_data.get("clusters", [])}

    if aggregate_only:
        _update_aggregate_only(clusters_data)
        return

    OVERVIEWS_DIR.mkdir(parents=True, exist_ok=True)

    if not GRAPH_PATH.exists():
        raise SystemExit(f"{GRAPH_PATH} not found — run `python tools/build.py graph` first.")
    graph_data = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))

    created_count = updated_count = skipped_count = 0

    if cluster is not None:
        c = clusters_by_slug.get(cluster)
        if not c:
            raise SystemExit(f"Cluster slug '{cluster}' not found in {OUTPUT_PATH}.")
        target = OVERVIEWS_DIR / f"{cluster}.md"
        was_new = not target.exists()
        status = _update_overview_file(target, c, clusters_data, graph_data, created=was_new)
        if status == "created":
            created_count += 1
            print(f"  + created overviews/{cluster}.md (skeleton with AUTO blocks)")
        elif status == "updated":
            updated_count += 1
            print(f"  ~ updated overviews/{cluster}.md AUTO blocks")
        else:
            skipped_count += 1
            print(f"  ! skipped overviews/{cluster}.md — no AUTO markers (migrate manually)")
    else:
        seen_slugs: set[str] = set()
        for c in clusters_data.get("clusters", []):
            slug = c["slug"]
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)
            target = OVERVIEWS_DIR / f"{slug}.md"
            if not target.exists():
                continue  # bulk run doesn't create skeletons
            status = _update_overview_file(target, c, clusters_data, graph_data, created=False)
            if status == "updated":
                updated_count += 1
            else:
                skipped_count += 1
                print(f"  ! skipped overviews/{slug}.md — no AUTO markers")

    _update_aggregate_only(clusters_data)

    print(f"Overview pages: {created_count} created, {updated_count} updated, {skipped_count} skipped")


def _update_aggregate_only(clusters_data: dict) -> None:
    """Update AUTO:STATS in wiki/overview.md. Silent skip if markers absent."""
    target = WIKI / "overview.md"
    if not target.exists():
        print("  ! wiki/overview.md missing — aggregate update skipped")
        return
    content = target.read_text(encoding="utf-8")
    stats_body = _render_stats_block(clusters_data)
    new_content, found = update_auto_block(content, "STATS", stats_body)
    if not found:
        print("  ! wiki/overview.md has no AUTO:STATS marker — aggregate update skipped")
        return
    if new_content != content:
        atomic_write_text(target, new_content)
        print("  ~ updated wiki/overview.md AUTO:STATS")
