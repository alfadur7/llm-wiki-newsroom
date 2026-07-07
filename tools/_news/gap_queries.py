"""Generate search queries from `lint graph gaps --json` output.

Three Track-A gap types are auto-fillable per the Phase 2C design
(`.claude/operations/gap-detection-rollout.md`):

  sparse-cluster  → cluster-scope query for overview refresh
  single-source   → hub-specific query with cluster context
  stale-hub       → hub-specific query with "announcement update" intent

Phase 2C validation (5 queries × 10 results, 2026-05-15) measured 68% novel
sources against `_source_map.json`, so the per-gap query count is capped to
keep the inbox queue from overflowing operator review capacity. Hard caps:
2-3 queries per gap / 6 results per query / 8 new sources per gap.

Query intent tokens are language-gated via `korean_mode()` (the `_QT` table
below): the English-native engine appends "trends"/"announcement"/etc., while
WIKI_LANG=ko swaps in the Korean wording validated for Korean news search:
  - "발표" (announce, not "최신"/latest) — surfaces press releases, not
    official-site/app pages
  - cluster_top_hub combination for single-source — strongest single signal
  - cluster_name combination for stale-hub — context narrows to active domain
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

YEAR = str(datetime.now().year)  # recency token for generated search queries

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import CLUSTERS_JSON, GRAPH_JSON, HUB_PREFIXES, REPO_ROOT, WIKI, korean_mode, parse_frontmatter  # noqa: E402
from _news.normalize import hub_korean_label, normalize_tags  # noqa: E402

GRAPH_PATH = GRAPH_JSON
CLUSTERS_PATH = CLUSTERS_JSON
HUB_DIRS = [WIKI / "entities", WIKI / "concepts"]


def _qt() -> dict[str, str]:
    """Query intent tokens, language-gated. Read live so WIKI_LANG can toggle
    per run. English-native by default; Korean wording under WIKI_LANG=ko."""
    if korean_mode():
        return {
            "issue_trends": "쟁점 동향",
            "announcement": "발표",
            "trends": "동향",
            "announcement_update": "발표 업데이트",
        }
    return {
        "issue_trends": "trends",
        "announcement": "announcement",
        "trends": "trends",
        "announcement_update": "announcement update",
    }

# Per-gap query count cap. sparse-cluster scope queries are intrinsically
# broader so 2 variants suffice; single-source/stale-hub hub-specific queries
# benefit from a 3rd context variant when cluster data is available.
QUERIES_PER_SPARSE_CLUSTER = 2
QUERIES_PER_SINGLE_SOURCE = 3
QUERIES_PER_STALE_HUB = 2


def _load_hub_fm() -> dict[str, dict]:
    """Load frontmatter for every entity/concept hub, keyed by `'entities/X.md'`."""
    out: dict[str, dict] = {}
    for d in HUB_DIRS:
        if not d.exists():
            continue
        for p in d.glob("*.md"):
            try:
                fm = parse_frontmatter(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            out[f"{d.name}/{p.name}"] = fm
    return out


def _hub_label(hub_id: str, hub_fm: dict[str, dict]) -> str:
    """Return the searchable label for a hub id, falling back to its stem.

    Non-string titles (parse_frontmatter yields a list for inline/block-list
    values) fall back to the stem too — hub_korean_label would TypeError on a
    list. Single definition shared with `crawl.build_vocabulary`."""
    t = hub_fm.get(hub_id, {}).get("title")
    raw = t if isinstance(t, str) and t else hub_id.split("/")[-1].removesuffix(".md")
    return hub_korean_label(raw)


def _cluster_top_hubs(clusters: dict, graph: dict, hub_fm: dict[str, dict]) -> dict[str, list[str]]:
    """Compute degree-ranked hub labels per cluster (used for single-source context query).

    Mirrors `_lint/graph_gaps._build_hub_subgraph` adjacency for consistency
    with the gap diagnosis output — degree is distinct-neighbor count, so
    parallel hub-hub edges don't inflate the ranking. Hubs without a
    frontmatter title fall back to their filename stem so the caller never
    gets an empty string."""
    nbrs: dict[str, set[str]] = defaultdict(set)
    for e in graph["edges"]:
        s, d = e.get("from"), e.get("to")
        if s and d and s.startswith(HUB_PREFIXES) and d.startswith(HUB_PREFIXES) and s != d:
            nbrs[s].add(d)
            nbrs[d].add(s)
    hub_assign = clusters.get("hub_assignments", {})
    by_cluster: dict[str, list[str]] = defaultdict(list)
    for hub_id, slug in hub_assign.items():
        by_cluster[slug].append(hub_id)
    out: dict[str, list[str]] = {}
    for slug, members in by_cluster.items():
        members.sort(key=lambda h: len(nbrs.get(h, ())), reverse=True)
        out[slug] = [_hub_label(h, hub_fm) for h in members]
    return out


def _cluster_top_tags(clusters: dict, hub_fm: dict[str, dict]) -> dict[str, list[str]]:
    """Top-N tags per cluster after `normalize_tags` collapse, ordered by frequency."""
    out: dict[str, list[str]] = {}
    for c in clusters.get("clusters", []):
        counter: Counter = Counter()
        for hub_id in c.get("members", []):
            fm = hub_fm.get(hub_id)
            if not fm:
                continue
            tags = fm.get("tags") or []
            for t in normalize_tags(tags):
                counter[t] += 1
        out[c["slug"]] = [t for t, _ in counter.most_common(5)]
    return out


def build_queries_for_sparse_cluster(rows: list[dict],
                                     cluster_info: dict[str, dict],
                                     cluster_tags: dict[str, list[str]]) -> list[dict]:
    """sparse-cluster → cluster-scope queries (2 per gap).

    The second query drops tags that already appear inside the cluster name
    so a cluster like `LLM·파운데이션 모델` (LLMs·foundation models) doesn't
    re-emit `LLM` and `AI` as the top tags."""
    out: list[dict] = []
    for row in rows:
        slug = row["slug"]
        name = cluster_info.get(slug, {}).get("name", slug)
        name_lower = name.lower()
        tags = cluster_tags.get(slug, [])
        # Drop tags already represented in the cluster name (case-insensitive,
        # substring match — Korean tags rarely collide, English acronyms do).
        unique_tags = [t for t in tags if t.lower() not in name_lower]
        qt = _qt()
        queries = [f"{name} {YEAR} {qt['issue_trends']}"]
        if unique_tags:
            tag_part = " ".join(unique_tags[:2])
            queries.append(f"{name} {tag_part} {YEAR}")
        queries = queries[:QUERIES_PER_SPARSE_CLUSTER]
        out.append({
            "gap": "sparse-cluster",
            "target": slug,
            "target_label": name,
            "queries": queries,
            "priority": row.get("priority", 0),
        })
    return out


def build_queries_for_single_source(rows: list[dict],
                                    cluster_info: dict[str, dict],
                                    cluster_top_hubs: dict[str, list[str]],
                                    hub_fm: dict[str, dict]) -> list[dict]:
    """single-source hub → cluster-context queries (≤3 per gap)."""
    out: list[dict] = []
    for row in rows:
        hub_id = row["id"]
        cluster_slug = row.get("cluster", "")
        title = _hub_label(hub_id, hub_fm)
        cname = cluster_info.get(cluster_slug, {}).get("name", cluster_slug)
        # cluster top hub excluding the gap hub itself
        peers = [p for p in cluster_top_hubs.get(cluster_slug, []) if p != title]
        queries: list[str] = []
        qt = _qt()
        if peers:
            queries.append(f"{title} {peers[0]} {YEAR}")
        queries.append(f"{title} {YEAR} {qt['announcement']}")
        if cname:
            queries.append(f"{title} {cname} {qt['trends']}")
        queries = queries[:QUERIES_PER_SINGLE_SOURCE]
        out.append({
            "gap": "single-source",
            "target": hub_id,
            "target_label": title,
            "cluster": cluster_slug,
            "queries": queries,
            "priority": row.get("priority", 0),
        })
    return out


def build_queries_for_stale_hub(rows: list[dict],
                                cluster_info: dict[str, dict],
                                cluster_top_hubs: dict[str, list[str]],
                                hub_fm: dict[str, dict]) -> list[dict]:
    """stale-hub → hub-specific with cluster context (2 per gap)."""
    out: list[dict] = []
    for row in rows:
        hub_id = row["id"]
        cluster_slug = row.get("cluster", "")
        title = _hub_label(hub_id, hub_fm)
        peers = [p for p in cluster_top_hubs.get(cluster_slug, []) if p != title]
        qt = _qt()
        queries = [f"{title} {YEAR} {qt['announcement_update']}"]
        if peers:
            queries.append(f"{title} {peers[0]} {YEAR}")
        elif cluster_info.get(cluster_slug, {}).get("name"):
            queries.append(f"{title} {cluster_info[cluster_slug]['name']} {YEAR}")
        queries = queries[:QUERIES_PER_STALE_HUB]
        out.append({
            "gap": "stale-hub",
            "target": hub_id,
            "target_label": title,
            "cluster": cluster_slug,
            "queries": queries,
            "priority": row.get("priority", 0),
        })
    return out


def load_gaps_json(*, limit: int = 5, gap_type: str | None = None) -> dict[str, Any]:
    """Run `lint graph gaps --json` and return the parsed object.

    Shared by this module's CLI and `tools/_news/crawl.py` so both consume gap
    diagnosis through one code path. Uses `sys.executable` + an absolute script
    path pinned to `REPO_ROOT` so the call resolves regardless of cwd or which
    `python` is on PATH. Raises RuntimeError if the lint phase is unavailable
    (e.g. the graph has not been built yet) or its output cannot be parsed.
    """
    import subprocess

    # NOTE: --top only bounds the stdout table + bridge (Track-B) output; the
    # JSON branch emits full Track-A lists. Track-A capping for these callers is
    # done client-side (crawl.py [:limit] slice, build_all limit_per_type).
    lint_args = [sys.executable, str(REPO_ROOT / "tools" / "lint.py"),
                 "graph", "gaps", "--json", "--top", str(limit)]
    if gap_type:
        lint_args += ["--gap-type", gap_type]
    res = subprocess.run(lint_args, capture_output=True, text=True,
                         encoding="utf-8", cwd=REPO_ROOT)
    if res.returncode not in (0, 1):  # 1 just means "gaps exist", not failure
        raise RuntimeError(res.stderr or "lint graph gaps failed")
    body = res.stdout
    if "{" in body:  # strip the lint header bars so json.loads can parse
        body = body[body.index("{"):]
    try:
        return json.loads(body)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"failed to parse lint output: {e}") from e


def build_all(gaps_json: dict[str, Any], *, limit_per_type: int | None = None) -> list[dict]:
    """Build the full query plan from `lint graph gaps --json` output.

    `gaps_json` is the parsed object from the lint command. Returns one entry
    per gap candidate, ordered: single-source (highest hit rate in validation)
    → stale-hub → sparse-cluster. `limit_per_type` caps each gap type's
    candidate count — pass the operator's batch budget to keep the inbox
    queue bounded.
    """
    if not GRAPH_PATH.exists() or not CLUSTERS_PATH.exists():
        return []
    graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    clusters = json.loads(CLUSTERS_PATH.read_text(encoding="utf-8"))
    cluster_info = {c["slug"]: c for c in clusters.get("clusters", [])}
    hub_fm = _load_hub_fm()
    top_hubs = _cluster_top_hubs(clusters, graph, hub_fm)
    top_tags = _cluster_top_tags(clusters, hub_fm)

    track_a = gaps_json.get("track_a", {})
    sparse = track_a.get("sparse-cluster", []) or []
    single = track_a.get("single-source", []) or []
    stale = track_a.get("stale-hub", []) or []
    if limit_per_type is not None:
        sparse = sparse[:limit_per_type]
        single = single[:limit_per_type]
        stale = stale[:limit_per_type]

    plan: list[dict] = []
    # single-source first — validation showed highest novel-source yield (80%)
    plan.extend(build_queries_for_single_source(single, cluster_info, top_hubs, hub_fm))
    plan.extend(build_queries_for_stale_hub(stale, cluster_info, top_hubs, hub_fm))
    plan.extend(build_queries_for_sparse_cluster(sparse, cluster_info, top_tags))
    return plan


# CLI for sanity checking — `python -m tools._news.gap_queries` or
# `python tools/_news/gap_queries.py` reads from stdin or runs lint inline.
def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=5,
                    help="cap on candidates per gap type (default 5)")
    ap.add_argument("--gap-type",
                    choices=["sparse-cluster", "single-source", "stale-hub"],
                    default=None,
                    help="restrict to a single Track-A gap slug")
    ap.add_argument("--json", action="store_true",
                    help="emit machine-readable JSON")
    args = ap.parse_args()

    try:
        gaps_json = load_gaps_json(limit=args.limit, gap_type=args.gap_type)
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 2

    plan = build_all(gaps_json, limit_per_type=args.limit)

    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0

    print(f"Gap query plan — {len(plan)} candidates")
    print("=" * 72)
    for entry in plan:
        head = f"[{entry['gap']}] {entry['target_label']}"
        if entry.get("cluster"):
            head += f"  (cluster: {entry['cluster']})"
        print(f"\n{head}")
        for i, q in enumerate(entry["queries"], 1):
            print(f"  Q{i}: {q}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
