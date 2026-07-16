"""Gap inventory — self-describing diagnostic for backfill/derivation planning.

Each gap is named by what it *is* (a semantic slug), not an opaque number.
Slugs are partitioned across four tracks per
`.claude/operations/gap-detection-rollout.md`:

  Track A (auto-backfill targets — wiki-news --gap [...] --batch)
    sparse-cluster   coherence == "mixed" AND size >= 20
                     (domain-ambiguity signal)
    single-source    len(sources) == 1 AND degree >= 9
                     AND neighbor-cluster count >= 2
                     (influential single-source hub)
    stale-hub        hub_age - cluster_avg_age >= 14 days
                     AND cluster_avg_age <= 10 days
                     (stuck hub in an active area)

  Track B (wiki operator decision surface — /wiki-discover --gaps)
    bridge           tools/_discover/surprising.compute()
                     top-N — junction connecting multiple clusters

  Track C (separate cycle — /wiki-lint contradiction)
    orphan-claims    theme JSON `unassigned` residue
    cap-theme        real_claim_count >= 30
    stale-theme      theme.last_updated < max(mapped_source.last_updated) - 7 days

  Track D (derivation coverage — filled by columnist authoring, not via external search)
    synthesis        an integration-worthy theme (≥30 claims) but no synthesis
    trail            a bridge hub but no trail passing through it
    timeline         a hub with accumulated material (≥25 sources) but no timeline

Output: a single Gap Inventory section with the four tracks separated so
the operator sees at a glance which gaps are auto-fillable vs. which need
human / theme-management / derivation attention. JSON mode for programmatic
consumers (wiki-discover --gaps, wiki-news --gap --batch).

Exit code 0 if all tracks empty, 1 otherwise. Same convention as the rest
of the lint suite.
"""
from __future__ import annotations

import json
import math
import re
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import parse_frontmatter, read_text_cached, WIKILINK_RE, WIKI, CLUSTERS_JSON, GRAPH_JSON, HUB_PREFIXES, fm_sources  # noqa: E402

GRAPH_PATH = GRAPH_JSON
CLUSTERS_PATH = CLUSTERS_JSON
THEMES_PATH = WIKI / "contradictions/_contradictions_themes.json"
CLAIMS_PATH = WIKI / "contradictions/_contradictions.json"
THEMES_DIR = WIKI / "contradictions"
HUB_DIRS = [WIKI / "entities", WIKI / "concepts"]
SYNTHESES_DIR = WIKI / "syntheses"
TRAILS_DIR = WIKI / "trails"
TIMELINES_DIR = WIKI / "timelines"

# Canonical gap slugs grouped by track. Order within each track is the
# display order. The flat list (VALID_GAP_TYPES) is the `--gap-type` /
# `--gaps` choice set and the single source of truth for valid slugs.
TRACK_A_SLUGS = ["sparse-cluster", "single-source", "stale-hub"]
TRACK_B_SLUGS = ["bridge"]
TRACK_C_SLUGS = ["orphan-claims", "cap-theme", "stale-theme"]
TRACK_D_SLUGS = ["synthesis", "trail", "timeline"]
VALID_GAP_TYPES = TRACK_A_SLUGS + TRACK_B_SLUGS + TRACK_C_SLUGS + TRACK_D_SLUGS

# Thresholds — derived from current wiki measurements (568 hubs, median
# hub-hub degree 16, p25 9, age median 9d max 35d, 9 clusters size 25-115).
# See gap-detection-rollout.md "Calibrating thresholds".
SPARSE_CLUSTER_MIN_SIZE = 20
SINGLE_SOURCE_MIN_DEGREE = 9         # p25 of hub-hub degree — floor for "normal influence"
SINGLE_SOURCE_MIN_CLUSTER_COUNT = 2  # adjacent to multiple clusters
STALE_HUB_AGE_GAP_DAYS = 14          # hub_age - cluster_avg_age
STALE_HUB_CLUSTER_FRESH_DAYS = 10    # cluster_avg_age ceiling (active area)
CAP_THEME_CLAIM_FLOOR = 30           # 60% of the 50 cap
# The catch-all residual theme is exempt from cap-theme — by definition it is the
# residual of genuine one-offs (cross-domain one-time comparisons) that fit no
# other theme, so it is normal for a large claim count to remain even after all
# cohesive sub-axes have been extracted. Forcing a split would force fragmentation
# (memory feedback_lint_recalibrate_over_churn). Isomorphic to the single-axis
# exemption. SoT: gap-detection-rollout.md cap-theme section.
CAP_THEME_EXEMPT_SLUGS = {"other-fragmentary"}
STALE_THEME_DAYS = 7                 # theme MD vs latest mapped source
# Track D (derivation coverage — material has accumulated but the integration page
# is absent). Unlike the input gaps (Track A-C), this is filled by columnist
# authoring rather than external search (gap-detection-rollout 2nd boundary).
SYNTHESIS_CLAIM_FLOOR = 30           # theme ≥30 claims but no integrating synthesis (reuses the cap-theme signal)
TIMELINE_SOURCES_FLOOR = 25          # hub ≥25 sources (chronicle-volume floor — auxiliary gate)
TIMELINE_MIN_SECTION_EVENTS = 18     # year (20YY) mentions ≥ N inside the hub body's `## Timeline` section
# timeline split signal: has the `## Timeline` section already grown in the hub
# body (accumulated dated events) matured enough to split into its own page? All 8
# existing timelines were split off from a hub that carried this section. No cluster
# allowlist needed (reads the hub's own structure, so it's robust to reorg).
TIMELINE_SECTION_RE = re.compile(r"^##[^#\n]*(Timeline|시간축|연대기|타임라인)", re.MULTILINE)
_YEAR_RE = re.compile(r"20\d{2}")


def _timeline_section_events(node_id: str) -> int:
    """Count year (20YY) mentions inside the hub body's `## Timeline` section.
    0 if the hub has no such section (the discriminating signal). The section
    runs from its heading to the next `## ` heading (or EOF)."""
    p = WIKI / node_id
    try:
        body = read_text_cached(p)
    except OSError:
        return 0
    m = TIMELINE_SECTION_RE.search(body)
    if not m:
        return 0
    rest = body[m.end():]
    nxt = re.search(r"^##\s", rest, re.MULTILINE)
    section = rest[: nxt.start()] if nxt else rest
    return len(_YEAR_RE.findall(section))


def _today() -> date:
    return date.today()


def _parse_iso_date(s) -> date | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).split("T")[0]).date()
    except (ValueError, TypeError):
        return None


def _load_hub_frontmatter() -> dict[str, dict]:
    """Return {hub_id: {sources, last_updated, type}} for every hub MD."""
    out: dict[str, dict] = {}
    for d in HUB_DIRS:
        if not d.exists():
            continue
        for p in d.glob("*.md"):
            try:
                fm = parse_frontmatter(read_text_cached(p))
            except Exception:
                continue
            hub_id = f"{d.name}/{p.name}"
            out[hub_id] = {
                "sources": fm_sources(fm),
                "last_updated": _parse_iso_date(fm.get("last_updated")),
                "title": fm.get("title") or p.stem,
            }
    return out


def _build_hub_subgraph(graph: dict, clusters: dict) -> tuple[dict[str, set[str]], dict[str, str]]:
    """Build adjacency + cluster lookup for hub-hub edges only.

    Returns `(neighbors_by_hub, hub_to_cluster)`. Mirrors the hub subgraph
    construction in `_discover/surprising.compute()` so degree thresholds
    use the same denominator the operator already sees in `--surprising`."""
    hub_ids = {n["id"] for n in graph["nodes"] if n["id"].startswith(HUB_PREFIXES)}
    nbrs: dict[str, set[str]] = defaultdict(set)
    for e in graph["edges"]:
        src = e.get("from")
        dst = e.get("to")
        if not src or not dst or src == dst:
            continue
        if src not in hub_ids or dst not in hub_ids:
            continue
        nbrs[src].add(dst)
        nbrs[dst].add(src)
    hub_to_cluster = clusters.get("hub_assignments", {})
    return nbrs, hub_to_cluster


def _impact_score(degree: int, cluster_size: int, max_cluster_size: int) -> float:
    """Common impact multiplier — log(degree+1) × cluster_size_norm."""
    norm = (cluster_size / max_cluster_size) if max_cluster_size else 1.0
    return math.log(degree + 1) * norm


def detect_sparse_cluster(clusters: dict) -> list[dict]:
    """sparse-cluster: mixed coherence with size >= 20 (severity = 1 - containment)."""
    out: list[dict] = []
    for cl in clusters.get("clusters", []):
        if cl.get("coherence") != "mixed":
            continue
        if cl.get("size", 0) < SPARSE_CLUSTER_MIN_SIZE:
            continue
        # clusters.py always writes the `containment` key but its value is
        # None for auto-labelled clusters (no anchors). A mixed, size≥20
        # auto-labelled cluster reaches here, so coerce None → 1.0 (severity 0)
        # rather than crashing on `1.0 - None`.
        containment = cl.get("containment")
        containment = 1.0 if containment is None else containment
        severity = round(1.0 - containment, 3)
        out.append({
            "slug": cl["slug"],
            "name": cl.get("name", cl["slug"]),
            "size": cl["size"],
            "coherence": cl["coherence"],
            "containment": containment,
            "severity": severity,
            "priority": round(math.log(cl["size"] + 1) * (1.0 - containment + 0.1), 4),
        })
    out.sort(key=lambda r: r["priority"], reverse=True)
    return out


def detect_single_source(hub_fm: dict[str, dict],
                         nbrs: dict[str, set[str]],
                         hub_to_cluster: dict[str, str],
                         max_cluster_size: int,
                         cluster_size: dict[str, int]) -> list[dict]:
    """single-source: 1-source hubs with non-trivial degree spanning ≥2 clusters."""
    out: list[dict] = []
    for hub_id, fm in hub_fm.items():
        if len(fm["sources"]) != 1:
            continue
        deg = len(nbrs.get(hub_id, set()))
        if deg < SINGLE_SOURCE_MIN_DEGREE:
            continue
        nbr_clusters = {hub_to_cluster.get(n) for n in nbrs.get(hub_id, set())
                        if hub_to_cluster.get(n)}
        if len(nbr_clusters) < SINGLE_SOURCE_MIN_CLUSTER_COUNT:
            continue
        own_cluster = hub_to_cluster.get(hub_id, "unassigned")
        impact = _impact_score(deg, cluster_size.get(own_cluster, 0), max_cluster_size)
        out.append({
            "id": hub_id,
            "title": fm["title"],
            "cluster": own_cluster,
            "degree": deg,
            "cluster_neighbors": sorted(nbr_clusters),
            "source": fm["sources"][0],
            "priority": round(impact * 0.5, 4),
        })
    out.sort(key=lambda r: r["priority"], reverse=True)
    return out


def detect_stale_hub(hub_fm: dict[str, dict],
                     hub_to_cluster: dict[str, str],
                     cluster_size: dict[str, int],
                     nbrs: dict[str, set[str]],
                     max_cluster_size: int) -> list[dict]:
    """stale-hub: hub age >> cluster average age (cluster active, hub stuck)."""
    today = _today()
    # Per-cluster age aggregate
    cluster_ages: dict[str, list[int]] = defaultdict(list)
    for hub_id, fm in hub_fm.items():
        lu = fm.get("last_updated")
        if not lu:
            continue
        cluster = hub_to_cluster.get(hub_id)
        if not cluster:
            continue
        cluster_ages[cluster].append((today - lu).days)
    cluster_avg: dict[str, float] = {
        c: sum(ages) / len(ages) for c, ages in cluster_ages.items() if ages
    }

    out: list[dict] = []
    for hub_id, fm in hub_fm.items():
        lu = fm.get("last_updated")
        if not lu:
            continue
        cluster = hub_to_cluster.get(hub_id)
        avg = cluster_avg.get(cluster)
        if avg is None or avg > STALE_HUB_CLUSTER_FRESH_DAYS:
            continue
        hub_age = (today - lu).days
        gap = hub_age - avg
        if gap < STALE_HUB_AGE_GAP_DAYS:
            continue
        deg = len(nbrs.get(hub_id, set()))
        impact = _impact_score(deg, cluster_size.get(cluster, 0), max_cluster_size)
        severity = round(gap / 14.0, 2)
        out.append({
            "id": hub_id,
            "title": fm["title"],
            "cluster": cluster,
            "hub_age_days": hub_age,
            "cluster_avg_age_days": round(avg, 1),
            "gap_days": round(gap, 1),
            "degree": deg,
            "priority": round(impact * severity, 4),
        })
    out.sort(key=lambda r: r["priority"], reverse=True)
    return out


def detect_bridge_nodes(top: int = 10) -> list[dict]:
    """bridge: surfaces tools/_discover/surprising.compute() top-N verbatim."""
    from _discover.surprising import compute  # type: ignore
    res = compute(top=top)
    if res is None:
        return []
    results, _k, _excluded = res
    return [
        {
            "id": r["id"],
            "title": r["label"],
            "cluster": r["own_cluster"],
            "degree": r["degree"],
            "cross_cluster_ratio": r["cross_cluster_ratio"],
            "composite": r["composite"],
            "priority": r["composite"],
        }
        for r in results
    ]


def detect_contradiction(themes_data: dict) -> dict:
    """Contradiction track: orphan-claims, cap-theme, stale-theme."""
    orphan: list[dict] = []
    cap: list[dict] = []
    stale: list[dict] = []

    unassigned = themes_data.get("unassigned", []) or []
    if unassigned:
        orphan.append({
            "claim_count": len(unassigned),
            "sample_claim_ids": unassigned[:5],
            "priority": round(len(unassigned) * 0.1, 2),
        })

    today = _today()
    themes = themes_data.get("themes", {})
    # cap-theme counts `type: "real"` claims only (gap-detection-rollout.md:
    # real_claim_count ≥ 30 — unlike the Track D synthesis floor, which uses the
    # total claim_ids count). _contradictions.json is a top-level array of claim
    # records carrying `id` + `type`. Unknown ids (or a missing/corrupt claims
    # file) default to "real" so the signal degrades to the raw count instead of
    # silently disabling cap-theme.
    claim_type: dict[str, str] = {}
    try:
        claim_type = {
            c.get("id"): c.get("type")
            for c in json.loads(read_text_cached(CLAIMS_PATH))
            if isinstance(c, dict)
        }
    except (OSError, ValueError):
        pass
    # The same source recurs in the `sources:` of multiple themes — cache scoped to one call.
    _src_lu_cache: dict[str, object] = {}
    for slug, td in themes.items():
        claim_count = sum(
            1 for cid in td.get("claim_ids", [])
            if claim_type.get(cid, "real") == "real"
        )
        if claim_count >= CAP_THEME_CLAIM_FLOOR and slug not in CAP_THEME_EXEMPT_SLUGS:
            cap.append({
                "slug": slug,
                "name": td.get("name", slug),
                "claim_count": claim_count,
                "priority": round((claim_count - CAP_THEME_CLAIM_FLOOR) / 20.0, 2),
            })

        # stale-theme: theme MD vs latest mapped source last_updated
        theme_md = THEMES_DIR / f"{slug}.md"
        if not theme_md.exists():
            continue
        try:
            fm = parse_frontmatter(read_text_cached(theme_md))
        except Exception:
            continue
        theme_lu = _parse_iso_date(fm.get("last_updated"))
        if not theme_lu:
            continue
        # Latest mapped source last_updated — best-effort: scan source files
        # listed in theme MD `sources:` frontmatter (cheap, mostly cached).
        latest_src = None
        for src_path in (fm.get("sources") or []):
            if src_path in _src_lu_cache:
                d = _src_lu_cache[src_path]
            else:
                # Theme `sources:` frontmatter holds bare source slugs —
                # wiki/sources/<slug>.md, same convention as
                # _build/contradictions.py. Keep path forms as fallback.
                p = WIKI / "sources" / f"{src_path}.md"
                if not p.exists():
                    p = Path(src_path)
                if not p.exists():
                    p = WIKI / src_path
                d = None
                if p.exists():
                    try:
                        src_fm = parse_frontmatter(read_text_cached(p))
                        d = _parse_iso_date(src_fm.get("last_updated"))
                    except (OSError, ValueError):
                        pass
                _src_lu_cache[src_path] = d
            if d and (latest_src is None or d > latest_src):
                latest_src = d
        if latest_src and (latest_src - theme_lu).days >= STALE_THEME_DAYS:
            stale.append({
                "slug": slug,
                "theme_last_updated": theme_lu.isoformat(),
                "latest_source_date": latest_src.isoformat(),
                "stale_days": (latest_src - theme_lu).days,
                "priority": round((latest_src - theme_lu).days / 7.0, 2),
            })

    cap.sort(key=lambda r: r["priority"], reverse=True)
    stale.sort(key=lambda r: r["priority"], reverse=True)
    return {"orphan-claims": orphan, "cap-theme": cap, "stale-theme": stale}


def _referenced_stems(dir_path: Path) -> set[str]:
    """Wikilink target stems referenced by any .md in dir_path. Used for
    coverage linkage — 'does any synthesis/trail already point at this?'"""
    out: set[str] = set()
    if not dir_path.exists():
        return out
    for fp in dir_path.glob("*.md"):
        if fp.name.startswith("_"):
            continue
        try:
            text = read_text_cached(fp)
        except Exception:
            continue
        for m in WIKILINK_RE.finditer(text):
            out.add(m.group(1).strip())
    return out


def detect_synthesis_coverage(themes_data: dict) -> list[dict]:
    """synthesis (Track D): contradiction theme with ≥SYNTHESIS_CLAIM_FLOOR claims
    but no synthesis integrating it (no synthesis references `[[<theme-slug>]]`).
    Reuses the cap-theme claim-count signal + a synthesis-existence linkage check."""
    covered = _referenced_stems(SYNTHESES_DIR)
    out: list[dict] = []
    for slug, td in themes_data.get("themes", {}).items():
        cc = len(td.get("claim_ids", []))
        if cc >= SYNTHESIS_CLAIM_FLOOR and slug not in covered:
            out.append({
                "slug": slug, "name": td.get("name", slug), "claim_count": cc,
                "priority": round((cc - SYNTHESIS_CLAIM_FLOOR) / 20.0 + 1.0, 2),
            })
    out.sort(key=lambda r: r["priority"], reverse=True)
    return out


def detect_trail_coverage(bridge_rows: list[dict]) -> list[dict]:
    """trail (Track D): bridge node not traversed by any trail. Reuses the
    bridge ranking + a trail-existence linkage check."""
    covered = _referenced_stems(TRAILS_DIR)
    out: list[dict] = []
    for r in bridge_rows:
        if Path(r["id"]).stem not in covered:
            out.append({
                "id": r["id"], "title": r["title"], "cluster": r.get("cluster"),
                "degree": r["degree"], "composite": r["composite"],
                "priority": r["composite"],
            })
    return out


def detect_timeline_coverage(hub_fm: dict[str, dict]) -> list[dict]:
    """timeline (Track D): a hub whose *embedded chronicle has already grown* —
    its body carries a `## Timeline` section thick with dated events — and has
    ≥TIMELINE_SOURCES_FLOOR sources, but no standalone timeline page yet.

    This generalizes the actual split pattern: every one of the 8 existing
    timelines was split off from a hub that first grew an in-body timeline section
    (all 8 still carry one, 18–157 date mentions). The timeline section is the ripe
    signal — the chronicle outgrew the hub and merits its own page. Raw source
    count alone surfaced 91 (every busy global vendor); the section gate is
    discriminating (only 68/566 hubs carry one) and drops the noise to ~14
    genuine split candidates — robust to cluster reorg (no allowlist) since it
    reads the hub's own structure, not its domain label."""
    existing = (
        {p.stem for p in TIMELINES_DIR.glob("*.md") if not p.name.startswith("_")}
        if TIMELINES_DIR.exists() else set()
    )
    out: list[dict] = []
    for node_id, fm in hub_fm.items():
        stem = Path(node_id).stem
        if stem in existing:
            continue
        nsrc = len(fm.get("sources") or [])
        if nsrc < TIMELINE_SOURCES_FLOOR:
            continue
        events = _timeline_section_events(node_id)
        if events < TIMELINE_MIN_SECTION_EVENTS:
            continue
        out.append({
            "id": node_id, "title": fm.get("title") or stem,
            "sources": nsrc, "section_events": events,
            "priority": round(events / 10.0 + nsrc / 100.0, 2),
        })
    out.sort(key=lambda r: r["priority"], reverse=True)
    return out


def _print_table(rows: list[dict], cols: list[tuple[str, str, int]],
                 limit: int | None = None) -> None:
    """`cols`: list of `(header, key, width)`."""
    if not rows:
        print("  (none)")
        return
    header = "  " + "".join(f"{h:<{w}}" for h, _, w in cols)
    print(header)
    print("  " + "─" * (sum(w for _, _, w in cols) - 1))
    for r in rows[: limit or len(rows)]:
        line = "  " + "".join(f"{str(r.get(k, '')):<{w}}"[: w] for _, k, w in cols)
        print(line)


def run(*, json_out: bool = False,
        gap_type: str | None = None,
        top: int | None = None) -> int:
    """Entry point — invoked by `python tools/lint.py graph gaps`.

    `gap_type` filters to a single slug (see VALID_GAP_TYPES). When unset,
    every track is surfaced. `top` caps per-track row count in stdout
    table mode; JSON mode emits full lists regardless."""
    if not GRAPH_PATH.exists() or not CLUSTERS_PATH.exists():
        print("graph/_graph.json or _clusters.json missing. "
              "Run `python tools/build.py` first.", file=sys.stderr)
        return 1
    graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    clusters = json.loads(CLUSTERS_PATH.read_text(encoding="utf-8"))
    cluster_size = {c["slug"]: c["size"] for c in clusters.get("clusters", [])}
    max_cluster_size = max(cluster_size.values()) if cluster_size else 1

    hub_fm = _load_hub_frontmatter()
    nbrs, hub_to_cluster = _build_hub_subgraph(graph, clusters)

    def _want(slug: str) -> bool:
        return gap_type is None or gap_type == slug

    track_a: dict = {}
    if _want("sparse-cluster"):
        track_a["sparse-cluster"] = detect_sparse_cluster(clusters)
    if _want("single-source"):
        track_a["single-source"] = detect_single_source(
            hub_fm, nbrs, hub_to_cluster, max_cluster_size, cluster_size
        )
    if _want("stale-hub"):
        track_a["stale-hub"] = detect_stale_hub(
            hub_fm, hub_to_cluster, cluster_size, nbrs, max_cluster_size
        )

    track_b: dict = {}
    if _want("bridge"):
        track_b["bridge"] = detect_bridge_nodes(top=top or 10)

    themes_data: dict = {}
    if THEMES_PATH.exists():
        try:
            themes_data = json.loads(THEMES_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            # A corrupt SoT must not read as "no gaps": warn, and hard-fail when
            # the caller explicitly asked for a themes-backed bucket. A *missing*
            # file stays a legitimate pre-contradiction-cycle empty state.
            print(f"WARN: {THEMES_PATH} is not valid JSON ({e}) — "
                  f"Track C / synthesis skipped.", file=sys.stderr)
            if gap_type in TRACK_C_SLUGS or gap_type == "synthesis":
                return 1

    track_c: dict = {}
    if themes_data and (gap_type is None or gap_type in TRACK_C_SLUGS):
        contra = detect_contradiction(themes_data)
        for slug in TRACK_C_SLUGS:
            if _want(slug):
                track_c[slug] = contra[slug]

    # Track D — derivation coverage (synthesis·trail·timeline absent). The track
    # filled by columnist authoring (separate from input gaps). synthesis/trail/
    # timeline reuse existing signals (cap-theme·bridge·hub sources); only the
    # "does the integration page exist" comparison is new.
    track_d: dict = {}
    if _want("synthesis") and themes_data:
        track_d["synthesis"] = detect_synthesis_coverage(themes_data)
    if _want("trail"):
        bridge_rows = track_b.get("bridge")
        if bridge_rows is None:
            bridge_rows = detect_bridge_nodes(top=top or 10)
        track_d["trail"] = detect_trail_coverage(bridge_rows)
    if _want("timeline"):
        track_d["timeline"] = detect_timeline_coverage(hub_fm)

    counts = {k: len(v) for k, v in {**track_a, **track_b, **track_c, **track_d}.items()}
    total = sum(counts.values())

    if json_out:
        print(json.dumps({
            "thresholds": {
                "sparse-cluster.min_size": SPARSE_CLUSTER_MIN_SIZE,
                "single-source.min_degree": SINGLE_SOURCE_MIN_DEGREE,
                "single-source.min_cluster_count": SINGLE_SOURCE_MIN_CLUSTER_COUNT,
                "stale-hub.age_gap_days": STALE_HUB_AGE_GAP_DAYS,
                "stale-hub.cluster_fresh_days": STALE_HUB_CLUSTER_FRESH_DAYS,
                "cap-theme.claim_floor": CAP_THEME_CLAIM_FLOOR,
                "stale-theme.stale_days": STALE_THEME_DAYS,
                "synthesis.claim_floor": SYNTHESIS_CLAIM_FLOOR,
                "timeline.sources_floor": TIMELINE_SOURCES_FLOOR,
                "timeline.min_section_events": TIMELINE_MIN_SECTION_EVENTS,
            },
            "counts": counts,
            "track_a": track_a,
            "track_b": track_b,
            "track_c": track_c,
            "track_d": track_d,
        }, ensure_ascii=False, indent=2))
        return 0 if total == 0 else 1

    # Human-readable output — split by track so the operator sees auto-fillable
    # vs. decision-required gaps at a glance.
    cap = top or 8
    print(f"Gap Inventory — {total} candidates across {len(counts)} buckets")
    print()
    if track_a:
        print("─── Track A — auto-backfill targets (wiki-news --gap [...] --batch) ───")
        if "sparse-cluster" in track_a:
            print(f"\n[sparse-cluster] Sparse / Mixed Cluster — {len(track_a['sparse-cluster'])}")
            _print_table(track_a["sparse-cluster"], [
                ("cluster", "slug", 32), ("size", "size", 6),
                ("coh", "coherence", 8), ("cont", "containment", 7), ("prio", "priority", 8),
            ], limit=cap)
        if "single-source" in track_a:
            print(f"\n[single-source] Single-source hub — {len(track_a['single-source'])}")
            _print_table(track_a["single-source"], [
                ("hub", "title", 28), ("cluster", "cluster", 24),
                ("deg", "degree", 5), ("prio", "priority", 8),
            ], limit=cap)
        if "stale-hub" in track_a:
            print(f"\n[stale-hub] Relative staleness — {len(track_a['stale-hub'])}")
            _print_table(track_a["stale-hub"], [
                ("hub", "title", 28), ("cluster", "cluster", 24),
                ("age", "hub_age_days", 5), ("avg", "cluster_avg_age_days", 6),
                ("gap", "gap_days", 6), ("prio", "priority", 8),
            ], limit=cap)
        print()
    if track_b:
        print("─── Track B — wiki operator decision surface (/wiki-discover --gaps) ───")
        if "bridge" in track_b:
            print(f"\n[bridge] Bridge node — top {len(track_b['bridge'])}")
            _print_table(track_b["bridge"], [
                ("hub", "title", 28), ("cluster", "cluster", 24),
                ("deg", "degree", 5), ("xcl", "cross_cluster_ratio", 6),
                ("score", "composite", 9),
            ], limit=cap)
        print()
    if track_c:
        print("─── Track C — separate cycle (/wiki-lint contradiction) ───")
        if track_c.get("orphan-claims"):
            print(f"\n[orphan-claims] Orphan claims — {len(track_c['orphan-claims'])}")
            for r in track_c["orphan-claims"]:
                print(f"  unassigned claims: {r['claim_count']} (sample: {r['sample_claim_ids']})")
        if track_c.get("cap-theme"):
            print(f"\n[cap-theme] Cap-approaching theme — {len(track_c['cap-theme'])}")
            _print_table(track_c["cap-theme"], [
                ("theme", "slug", 40), ("claims", "claim_count", 7), ("prio", "priority", 8),
            ], limit=cap)
        if track_c.get("stale-theme"):
            print(f"\n[stale-theme] Stale theme MD — {len(track_c['stale-theme'])}")
            _print_table(track_c["stale-theme"], [
                ("theme", "slug", 40),
                ("theme_lu", "theme_last_updated", 13),
                ("src_lu", "latest_source_date", 13),
                ("stale", "stale_days", 7),
            ], limit=cap)
        print()
    if track_d:
        print("─── Track D — derivation coverage surface (columnist authoring: synthesis·trail·timeline) ───")
        if track_d.get("synthesis"):
            print(f"\n[synthesis] Synthesis absent (theme ≥{SYNTHESIS_CLAIM_FLOOR} claims) — {len(track_d['synthesis'])}")
            _print_table(track_d["synthesis"], [
                ("theme", "slug", 40), ("claims", "claim_count", 7), ("prio", "priority", 8),
            ], limit=cap)
        if track_d.get("trail"):
            print(f"\n[trail] Trail absent (bridge node) — {len(track_d['trail'])}")
            _print_table(track_d["trail"], [
                ("hub", "title", 28), ("cluster", "cluster", 24),
                ("deg", "degree", 5), ("score", "composite", 9),
            ], limit=cap)
        if track_d.get("timeline"):
            print(f"\n[timeline] Timeline split candidate (hub `## Timeline` section matured — "
                  f"year mentions ≥{TIMELINE_MIN_SECTION_EVENTS}, sources ≥{TIMELINE_SOURCES_FLOOR}) "
                  f"— {len(track_d['timeline'])}")
            _print_table(track_d["timeline"], [
                ("hub", "title", 32), ("src", "sources", 6),
                ("sec_ev", "section_events", 8), ("prio", "priority", 8),
            ], limit=cap)
        print()

    if total == 0:
        print("All gap buckets empty — no actionable candidates.")
        return 0
    return 1
