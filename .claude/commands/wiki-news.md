Search for latest news related to the LLM Wiki's key topics.

Usage: `/wiki-news [cluster|keyword | --gap [<slug>] [--batch] [--no-filter]]` — argument optional

**If `$ARGUMENTS` is empty**: show the usage below, then proceed with an all-cluster search (do not stop).

```
Usage: /wiki-news [cluster|keyword | --gap [<slug>] [--batch] [--no-filter]]

Examples:
  /wiki-news                          # search all clusters (default)
  /wiki-news open-source-ai-definition  # a specific cluster (slug)
  /wiki-news open weights             # a specific cluster (name)
  /wiki-news DeepSeek open model      # free keyword
  /wiki-news --gap                    # gap fill: hub-gaps crawl, cluster-gaps search → _inbox.md (Track A)
  /wiki-news --gap single-source      # enrich a single gap type
  /wiki-news --gap single-source --batch  # skip the gate (operator pre-approved batch mode)
  /wiki-news --gap --no-filter        # disable the domain filter
```

The `--gap` slug is Track A only: `sparse-cluster` · `single-source` · `stale-hub`.

## Traversal Pattern

Reading domain — the Reporter does an external search per cluster via parallel spawn, then (optionally) an ingest chain. It runs independent cluster queries concurrently in breadth-first parallel mode.

| Phase | Cycle | Owner |
|---|---|---|
| Read wiki context | GROUND (own context) | Editor-in-Chief (read overview·index·`graph/_clusters.json`) |
| Build cluster queries | — | Editor-in-Chief |
| External WebSearch | GROUND breadth-first | Reporter multi-spawn (1 instance per cluster) |
| Duplicate check | — | Editor-in-Chief (`_source_map.json` matching) |
| Write report | — | Editor-in-Chief |
| (optional) inbox queue append | — | Editor-in-Chief (`_inbox.md`) — fetch·ingest is the separate `/wiki-ingest inbox` |

Cluster slug list SoT: `graph/_clusters.json::clusters[].slug` (single SoT, varies with ingest accumulation).

## Procedure (Editor-in-Chief Orchestration)

1. **Read wiki context** — `wiki/overview.md` (key themes·entities), `wiki/index.md` (cluster breakdown), `graph/_clusters.json` (clusters[].members·top_tags·source_assignments)
2. **Build search queries**:
   - If a cluster argument is given — match slug/name against `_clusters.json::clusters[]`, extract 3-5 member hubs with clear labels, combine the hub names (e.g. `open-source-ai-definition` → "OpenSourceInitiative Meta open weights AI definition 2026")
   - If no argument — the top 5 clusters by `_clusters.json` size, combining 2-3 hubs each
   - Add specific event·person keywords from the overview.md narrative (e.g. "DeepSeek open model release")
   - Append the current year for recency
   - Queries default to English; build Korean queries (for Korean news sources) only under `WIKI_LANG=ko`
3. **Reporter parallel spawn** — perform WebSearch per cluster (independent cluster queries run concurrently)
4. **Duplicate check** — match each result's title·URL against `wiki/sources/_source_map.json` (or grep `wiki/sources/` for similar keywords)
5. **Write report** — markdown report of category·title·source·date·ingest status (new / already ingested)
6. **Recommend top articles** — suggest ingest + wait for the user's decision
7. **After the user's decision** — append the chosen article URLs to `_inbox.md` as `# source=interactive` (fetch·ingest is the separate `/wiki-ingest inbox`), or save the report to `wiki/syntheses/`

## Gap Mode (`--gap [<slug>] [--batch] [--no-filter]`)

Perform Track A enrichment via **two channels** by gap type — hub-level gaps (single-source·stale-hub) follow the adjacent pages cited by existing sources via a **deterministic crawl** (the Editor-in-Chief calls `crawl.py` internally), while cluster-level gaps (sparse-cluster) use a **WebSearch query** (Reporter). Both converge into `_inbox.md`, and ingest is delegated to `/wiki-ingest inbox`.

Definitions, thresholds, and domain set have their SoT in [`.claude/operations/gap-detection-rollout.md`](../operations/gap-detection-rollout.md) + [`tools/_news/domains.py`](../../tools/_news/domains.py). Crawl seed derivation, relevance lexicon, and cap have their SoT in [`tools/_news/crawl.py`](../../tools/_news/crawl.py).

### Procedure

1. Call `python tools/lint.py graph gaps --json [--gap-type <slug>] --top 5` — Track A diagnosis (bridge·contradiction are outside this mode's domain).
2. **hub-level gaps (single-source·stale-hub)** → call `python tools/_news/crawl.py --gap-seed --append-inbox` internally. Seeds are auto-derived hub→backlinks→`source_url`; the adjacent pages cited by each hub's existing sources are appended to `_inbox.md` as `source=auto-crawl` after passing the domain allowlist·`by_url` dedup check (no external search·query gate needed — the seeds are already trusted sources).
3. **cluster-level gaps (sparse-cluster)** → generate queries with `python tools/_news/gap_queries.py --json --limit 5` → interactive gate (skipped with `--batch`) → WebSearch in parallel with the editor-selected domain set (`GLOBAL_IT_FINANCE_NEWS` for global/English topics, `KOREAN_IT_FINANCE_NEWS` for Korean-entity gaps, or their union for a broad sweep — the lists live in `tools/_news/domains.py`; the filter is lifted with `--no-filter`) → `by_url` dedup → append to `_inbox.md` in the form `URL  # source=auto-gap gap=<slug> cluster=<slug> ts=<iso>`.
4. Report the crawl hub/candidate counts + WebSearch new count + `_inbox.md` queue length. Ingest is the explicit `/wiki-ingest inbox`.

### Hard Cap

| Item | Value |
|---|---|
| (WebSearch) queries per gap | 2–3 (varies by gap type) |
| (WebSearch) result cap per query | 6 |
| (WebSearch) new-source cap per gap | 8 |
| gaps processed per cycle (`--batch`) | 5 |
| (crawl) `--max-pages`·`--max-depth`·`--per-domain-cap`·`--min-score` | `tools/_news/crawl.py` defaults SoT |
| `_inbox.md` queue length alarm | 30 |

## Fetch·Ingest Delegation

This command is responsible only up to WebSearch·report·`_inbox.md` append. The fetch (2-stage: deterministic + WebFetch fallback)·raw storage·source authoring are owned solely by [`wiki-ingest.md`](wiki-ingest.md) Inbox Mode — appending the chosen article URLs to `_inbox.md` lets `/wiki-ingest inbox` carry out everything from fetch to ingest (because the raw is the dedup ground truth, source pages are created only after the raw lands).

## Human Reviewer Gate

- Discovery of a new cluster slug (an external keyword does not fit existing clusters)
- Person entity stub candidate (memory hub-stub-threshold policy — only for key people cited multiple times)
- Ingest decision (chain into `/wiki-ingest` — explicit approval)
- **`--gap` mode query approval** (when `--batch` is absent) — the human reviewer edits·approves the `tools/_news/gap_queries.py` output. `--batch` is used only with operator pre-approval
