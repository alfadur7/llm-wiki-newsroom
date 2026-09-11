Search for latest news related to the LLM Wiki's key topics.

Usage: `/wiki-news [cluster|keyword | --gap [<slug>] [--no-filter]]` — argument optional

**If `$ARGUMENTS` is empty**: show the usage below, then proceed with an all-cluster search (do not stop).

```
Usage: /wiki-news [cluster|keyword | --gap [<slug>] [--no-filter]]

Examples:
  /wiki-news                          # search all clusters (default)
  /wiki-news open-source-ai-definition  # a specific cluster (slug)
  /wiki-news open weights             # a specific cluster (name)
  /wiki-news DeepSeek open model      # free keyword
  /wiki-news --gap                    # gap fill: deterministic hub crawl → _inbox.md (Track A)
  /wiki-news --gap single-source      # enrich a single gap type
  /wiki-news --gap --no-filter        # disable the domain filter
```

The `--gap` slug is Track A only: `single-source` · `stale-hub`.

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

## Gap Mode (`--gap [<slug>] [--no-filter]`)

Every Track A enrichment is hub-level: a **deterministic crawl** (the Editor-in-Chief calls `crawl.py` internally) follows the adjacent pages cited by existing sources into `_inbox.md`, and ingest is delegated to `/wiki-ingest inbox`. The cluster-level `sparse-cluster` gap was removed (rationale in the `NON_BACKLOG_BUCKETS` comment in [`tools/_lint/graph_gaps.py`](../../tools/_lint/graph_gaps.py)), and with it the automatic WebSearch path — operator-run WebSearch reinforcement stays valid through `tools/_news/gap_queries.py` (procedure: [`operations/gap-detection-rollout.md`](../operations/gap-detection-rollout.md) § Enrichment channels).

Definitions, thresholds, and domain set have their SoT in [`.claude/operations/gap-detection-rollout.md`](../operations/gap-detection-rollout.md) + [`tools/_news/domains.py`](../../tools/_news/domains.py). Crawl seed derivation, relevance lexicon, and cap have their SoT in [`tools/_news/crawl.py`](../../tools/_news/crawl.py).

### Procedure

1. Call `python tools/_news/crawl.py --gap-seed --append-inbox [--gap-type <slug>] [--no-filter]` internally. **Do not call `lint graph gaps` separately** — `crawl.py` runs that diagnosis inside itself. Seeds are auto-derived hub→backlinks→`source_url`; the adjacent pages cited by each hub's existing sources are appended to `_inbox.md` as `source=auto-crawl` after passing the domain allowlist·`by_url` dedup check (no external search needed — the seeds are already trusted sources).
2. Report the crawl hub/candidate counts + `_inbox.md` queue length. Ingest is the explicit `/wiki-ingest inbox`.

### Hard Cap

| Item | Value |
|---|---|
| `--gap-limit` (hubs per gap type) | 5 |
| (crawl) `--max-pages`·`--max-depth`·`--per-domain-cap`·`--min-score` | `tools/_news/crawl.py` defaults SoT |
| `_inbox.md` queue length alarm | 30 |

## Fetch·Ingest Delegation

This command is responsible only up to WebSearch·report·`_inbox.md` append. The fetch (2-stage: deterministic + WebFetch fallback)·raw storage·source authoring are owned solely by [`wiki-ingest.md`](wiki-ingest.md) Inbox Mode — appending the chosen article URLs to `_inbox.md` lets `/wiki-ingest inbox` carry out everything from fetch to ingest (because the raw is the dedup ground truth, source pages are created only after the raw lands).

## Human Reviewer Gate

- Discovery of a new cluster slug (an external keyword does not fit existing clusters)
- Person entity stub candidate ([`policies/naming.md`](../policies/naming.md) entity-stub threshold — only for key people cited multiple times)
- Ingest decision (chain into `/wiki-ingest` — explicit approval)
- **`--gap` mode** — no per-query gate: the automatic channel is a link crawl with no queries to approve. Ingest is still the explicit `/wiki-ingest inbox`
