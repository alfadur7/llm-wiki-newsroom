# Gap Detection & Auto-Backfill

The SoT for how the wiki diagnoses weak areas ("gaps") deterministically, then routes each kind to the right channel: background auto-enrichment for what can be filled automatically, an operator decision surface for what cannot. This file defines the gap types, thresholds, the query-generation contract, and the single-queue inbox model that the gap-detection code reads as its spec.

## Goals

1. Diagnose wiki gaps deterministically with a single tool (`tools/lint.py graph gaps`).
2. Handle gaps where auto-enrichment is effective (single-source · stale-hub · secondarily sparse-cluster) via a background chain keyed on the `_inbox.md` single queue.
3. Route gaps where auto-enrichment is a poor fit to their owning channel: bridge → the operator decision surface (`/wiki-discover --gaps`, Track B); contradiction → the contradiction cycle (`/wiki-lint contradiction`, Track C).
4. Unify the three entry channels (mobile · interactive · background) into a single inbox.

## Calibrating thresholds

The thresholds below were tuned against a real corpus, on a few empirical observations that generalize well — for example, an absolute "90-day staleness" cutoff is useless once a wiki is actively maintained (nothing is ever that old), so staleness is defined **relative** to a page's cluster rather than absolute; and a "degree ≤ 1" orphan test is meaningless once most hubs are well-connected. Treat the numbers as defaults and re-tune them for your own corpus from `graph/_graph.json` · `graph/_clusters.json` · `wiki/_backlinks.json` and the hub frontmatter.

## Track separation (the core decision)

Background auto-enrichment is far more effective for some gap kinds than others. Tying them all into one chain produces ROI variance and side effects, so gaps split into tracks:

| Gap | Auto-enrich effectiveness | Why | Track |
|---|---|---|---|
| single-source hub | high | Going from 1 → 2 sources on an existing hub resolves it; passes the Safe 6 conditions naturally | **Track A (auto)** |
| stale-hub (relative staleness) | high | Adding a source the hub cites auto-refreshes its `last_updated` | **Track A (auto)** |
| sparse-cluster | medium | Cluster cohesion needs sources that cite several hubs at once; creating a new hub is gated | **Track A (side effect)** |
| bridge node | low | The two clusters don't naturally meet, which is why a bridge exists — auto-enrichment can't route around that; the real fix is a new bridge hub (gated) | **Track B (operator surface)** |
| contradiction (orphan-claims · cap-theme · stale-theme) | very low (can backfire) | These are all theme-MD rewrite/mapping work — the `lint contradiction` cycle's domain | **Track C (separate cycle)** |
| derived coverage (synthesis · trail · timeline) | — | A missing page that **integrates** already-ingested material; filled by columnist authoring, not external search — a different problem from an input gap | **Track D (derivation)** |

### Track model

```
Track A (background auto: single-source · stale-hub main + sparse-cluster secondary)
  lint graph gaps → wiki-news --gap [sparse-cluster|single-source|stale-hub] --batch
    → append meta to _inbox.md
    → /wiki-ingest inbox --safe (once L2 is stable)

Track B (operator decision surface: bridge + auto-deferred candidates)
  /wiki-discover --gaps
    → combined report of bridges + items the Track A gate deferred
    → operator decision → new hub / cluster redesign

Track C (separate cycle, contradiction: orphan-claims · cap-theme · stale-theme)
  /wiki-lint contradiction theme --fix
    → theme-MD rewrite · burn · orphan mapping

Track D (derived coverage: synthesis · trail · timeline)
  lint graph gaps → /wiki-discover --gaps Track D surface
    → columnist authoring chain (synthesis/trail --fix → write → self-VERIFY₀ → desk VERIFY₂)
    → no external search / inbox (integrates internal material)
```

## Gap definitions (thresholds)

Input gaps (Track A·B·C — external source ingest · operator decision · theme management) plus derived-coverage gaps (Track D — missing internal-integration pages). The identifier is a self-describing semantic slug; that slug is the single identifier across `--gaps` · `--gap-type` · the JSON keys · the inbox meta.

| Track | Gap | Definition | Threshold | severity |
|---|---|---|---|---|
| A | **sparse-cluster** | weak label cohesion, size ≥ 20 | `coherence == "mixed"` AND `size >= 20` AND (`containment < 0.9` OR top-tag share < 60%) | `1 - containment` |
| A | **single-source** | 1 source but normal influence | `len(sources) == 1` AND `hub_hub_degree >= 9` AND `cluster_count >= 2` | `log(degree+1) × 0.5` |
| A | **stale-hub** | cluster active but this hub alone stagnant | `(hub_age - cluster_avg_age) >= 14d` AND `cluster_avg_age <= 10d` | `(hub_age - cluster_avg_age) / 14` |
| B | **bridge** | multi-cluster junction | `discover.py surprising` composite-score top-N (default 10 via `detect_bridge_nodes` / 15 via the standalone CLI) | normalized composite score |
| C | **orphan-claims** | raw claim not mapped to a theme | a source in `_contradictions.json` is in no theme's `sources:` | `count × 0.1` |
| C | **cap-theme** | real-claim count near cap | `real_claim_count >= 30` (60% of the cap of 50) — the catch-all `other-fragmentary` theme is exempt (`CAP_THEME_EXEMPT_SLUGS`): by definition it holds genuine one-off residuals that fit no other theme, so a large count is normal even after full sub-axis extraction; forcing a split would force fragmentation | `(real - 30) / 20` |
| C | **stale-theme** | claims accumulated vs theme MD not updated | `theme.last_updated < max(mapped_source.last_updated) - 7d` | `stale_days / 7` |
| D | **synthesis** | integration-worthy theme but no synthesis | `claim_count >= 30` AND no synthesis references `[[<theme>]]` | `(claim - 30) / 20 + 1` |
| D | **trail** | bridge hub but no trail passes through it | bridge node AND no trail passes through | composite score |
| D | **timeline** | hub `## Timeline` section mature enough to split out | ≥ 18 year mentions (20YY) in the hub's `## Timeline` section AND `len(sources) >= 25` AND no `timelines/<stem>.md` | `section_events / 10 + sources / 100` |

### Priority score

```
priority = impact × severity
  impact   = log(degree + 1) × cluster_size_norm
  severity = per-gap definition above
```

A novelty weight can be added later, once `_health-log.jsonl` trend data has accumulated.

### Enrichment channels (per gap kind)

Two complementary channels fill `_inbox.md` for Track A — a **link crawl** (following adjacent pages an existing source cited) and a **web-search query** (contract below). `/wiki-news --gap` default routing:
- **hub-level gaps** (single-source · stale-hub) → `tools/_news/crawl.py --gap-seed`. The seed derives automatically from hub → backlinks → `source_url`, so no query gate is needed (the seed is already a trusted source). After a domain-allowlist and `by_url` dedup check, it appends with `source=auto-crawl`. Seed derivation, the relevance lexicon, and the cap are SoT in [`tools/_news/crawl.py`](../../tools/_news/crawl.py).
- **cluster-level gaps** (sparse-cluster) → web search. There is no single seed URL, so a query pulls in new sources.

### Query-generation contract (Track A only)

Queries are generated in **English by default**; the Korean-language variants below fire only under `WIKI_LANG=ko` (see [`tools/_news/gap_queries.py`](../../tools/_news/gap_queries.py)). Tune the intent words for your domain.

| Gap | Q1 | Q2 | Q3 (optional) |
|---|---|---|---|
| **sparse-cluster** | `<cluster_name> 2026 trends` | `<cluster_name> <top_tag1> <top_tag2> 2026` (dedup words already in the cluster name) | — |
| **single-source** | `<hub> <cluster_top_hub> 2026` | `<hub> 2026 announcement` | `<hub> <cluster_name> trends` |
| **stale-hub** | `<hub> 2026 update` | `<hub> <cluster_top_hub> 2026` | — |

Normalization:
- **`<hub>`**: `tools/_news/normalize.hub_label()` — strips parenthetical glosses (`"Tesla (TSLA)"` → `"Tesla"`).
- **tags**: `tools/_news/normalize.normalize_tags()` — case-fold + synonym mapping (`['llm', 'AI', 'LLM']` → `['LLM', 'AI']`).

### Domain filter

Web search applies a curated allowlist of trusted, non-aggregator news domains as the default set, with an interactive `--no-filter` opt-out; `--batch` forces the filter (to guarantee background quality). The set is SoT in [`tools/_news/domains.py`](../../tools/_news/domains.py) — validate and adjust it for your corpus and language.

### Hard caps

| Item | Value | Rationale |
|---|---|---|
| queries per gap | 2–3 (varies by gap kind) | 1 lacks diversity, 4+ is excessive |
| results per query | 6 | keeps a cycle's volume manageable |
| new sources per gap | 8 | overflow is sorted by priority, then cut |
| gaps processed per cycle (`--batch`) | 5 | bounds the per-cycle enrichment volume |
| `_inbox.md` queue-length alarm | 30 | sized to operator review capacity |

## Single inbox

The three entry channels — mobile share-sheet, interactive `/wiki-news`, and background auto-enrichment — unify into the single `raw/_inbox.md` queue. The mobile shortcut JS is unchanged (a plain URL append still works).

### Meta-line format

```
https://example.com/article-A
https://example.com/article-B  # source=auto-gap gap=single-source hub=AICC ts=2026-05-15T02:00Z
https://example.com/article-C  # source=interactive query="..."
```

- The meta separator is **two spaces + `#`** after the URL (a URL's own `#fragment` attaches with no space, so it stays safe).
- A URL with no meta defaults to `source=mobile`.
- Meta keys (common; varies by channel): `source` · `gap` · `hub` · `cluster` · `query` · `priority` · `ts` · `found_on` · `score` (the crawl channel writes `found_on`/`score`).

### fetch_inbox.py behavior

- `parse_inbox` → returns `(url, meta_dict)` tuples.
- The meta is carried through `fetch_one` → `save_markdown` into the raw frontmatter `ingest_source` · `ingest_meta` fields.
- The `_archive.md` line format gains one or two meta keys.

## Automation levels

| Level | Auto scope | Operator gate |
|---|---|---|
| **L1** Search-only | `lint gaps` → `wiki-news --batch` → `_inbox.md` append | explicit `/wiki-ingest inbox` call |
| **L2** Safe Auto-Ingest | L1 + automatic `/wiki-ingest inbox --safe` for raw that passes the Safe 6 | gate-triggered raw is split to `raw/_review_queue.md` for operator review; commit/push stays manual |
| ~~L3~~ Full Auto + Commit | — | **rejected** — an agent must never commit on its own |

### Safe 6 conditions (eligible for L2 auto-ingest)

A raw item is eligible for auto-ingest only if all hold:
1. URL/path/SHA dedup OK
2. body ≥ 100 chars
3. every speaker entity in the body already has a stub (no new-person-stub trigger)
4. every `## Connections` candidate hub is an existing page (no new-cluster trigger)
5. no new contradiction-theme mapping required (orphan claims are OK)
6. the new source connects to ≥ 1 existing hub (prevents an orphan source)

Otherwise it moves to `raw/_review_queue.md` for operator review.

## Risks + mitigations

| Risk | Mitigation |
|---|---|
| background auto-ingest pollutes the wiki | Safe 6 conditions + alarm when `_health-log.jsonl` gap trend worsens |
| `_review_queue.md` grows unbounded | report queue length daily at the tail of log.md; auto-stop background when it exceeds the threshold (e.g. ≥30) |
| repeatedly searching the same gap | compare against the previous cycle's gap state → diversify the query or skip an unresolved gap |
| concurrent background runs | a `raw/.bg_cycle.lock` file lock |
| web-search cost blowup | hard caps: ≤3 queries per gap, ≤5 candidates per gap type |
| background commit violates policy | the code never calls `git commit` |

## SoT

- Detection logic: `tools/_lint/graph_gaps.py` (registered as the `gaps` sub-command of the `graph` group in `tools/lint.py`).
- Enrichment: `tools/_news/` (`domains.py` · `normalize.py` · `gap_queries.py` · `crawl.py`).
- Inbox: `tools/_ingest/fetch_inbox.py` + [`../policies/directory-layout.md`](../policies/directory-layout.md) (`_inbox.md` single-responsibility) + [`mobile-inbox-setup.md`](mobile-inbox-setup.md).
- Commands: [`../commands/wiki-news.md`](../commands/wiki-news.md) · [`../commands/wiki-discover.md`](../commands/wiki-discover.md) · [`../commands/wiki-lint.md`](../commands/wiki-lint.md) (graph gaps row).
