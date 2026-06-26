Export wiki to merged files for Claude.ai Project Knowledge.

Usage: `/wiki-export`

## Traversal Pattern

Outside the matrix — Meta layer (deterministic). The Editor-in-Chief calls `tools/export.py`.

| Cycle | Owner |
|---|---|
| Trigger | Editor-in-Chief |
| Export | `tools/export.py` (deterministic) |
| Commit·Push | Editor-in-Chief → explicit approval from the wiki operator (memory git-approval) |

## Output (`wiki-export/` Folder)

**Root meta copies** (1:1 copy)
- `overview.md`·`contradiction.md`·`index.md`

**Sub-folder merges** (`# All FOLDER (N)` header + `---` separator) — synthesis layer only
- `all-overviews.md` · `all-contradictions.md` · `all-timelines.md` · `all-syntheses.md` · `all-trails.md`
- **`all-entities.md` and `all-concepts.md` are NOT generated** (hub bodies = the graph layer). Those two files alone, at ~1.24M tokens, would overwhelm the Claude.ai project context (~200K, **fully loaded, not searched**) → the chief culprit of context-overflow errors. The full text lives in the `graph/_pages.json` nodes (`#q=`), and the directory is held by `index.md` (one line + deep link per entity·concept).

**Sources — a one-line index instead of full bodies**
- `all-sources-index.md` (single file) — one line per source (`` `slug` — title (date)``), grouped by `graph/_clusters.json` primary cluster. **No summary snippet** (slim — the snippet was most of this index's ~118K tokens, the headline is enough, and the full text is one graph deep link away).

**Claude.ai project instruction document** (`README.md`)
- `README.md` — the **complete custom-instruction document**: 2-tier structure explanation + file-structure table (derived from ROOT_META + FOLDER_MERGES + index, drift-impossible) + **upload budget guide** (Core/Optional are auto-filled greedily up to `_CONTEXT_LIMIT` in `_TIER_PRIORITY` order and split — as the corpus grows, large synthesis files are auto-demoted to Optional; fixed numbers, drift-impossible) + answer rules + deep-link convention + wiki-structure reference. **Paste this entire document into the Claude.ai project instruction field.** The per-file handoff block is discarded (the instruction field is the single channel — removing the 11× ~9K-token duplication).

**2-tier model**: RAG (synthesis layer + directory) = answer synthesis / Graph (entity·concept·source full text) = deep-link drill-down. The RAG corpus is kept at 0.93 MB by excluding entity·concept bodies, and the Core set is auto-selected within the limit by priority-greedy fill.

**Excluded**: `_`-prefixed files (auto-generated JSON, etc.). Stale artifacts dropped from FOLDER_MERGES (`all-entities.md`, etc.) are cleaned up by `_prune_stale` on every run.

**Hosting deploy assets** (`_site/` — `<slug>.html` + `<slug>-{graph,clusters,overlays,pages}.json`)
- `stage_site()` in `tools/_export/site.py` copies `graph/graph.html` (no inline, ~90KB) + `_graph.json`·`_clusters.json`·`_pages.json` into `_site/` **with a `<slug>-` prefix**, and injects `<meta robots noindex>` + `window.ASSET_PREFIX="<slug>-"` into the HTML. graph.html fetches the JSON from the obscure path with that prefix (graph/clusters at init, pages lazily on click). For hosting and viewing from a phone ([`operations/graph-hosting-setup.md`](../operations/graph-hosting-setup.md) SoT).
- The filenames and RAG link template are determined by the `tools/_lib.py` constants `BASE_URL`·`STANDALONE_SLUG` (shared by export and briefing) (single SoT, drift-impossible). **The data JSON carries the same slug prefix**, so the path is unguessable → without the slug you cannot fetch the data either.

**Deep-link convention (single SoT)**: when `BASE_URL` is set, `export.py`'s `_deeplink_protocol()` builds the convention text and embeds it into `README.md` (single channel for the instruction field). The convention directs **all entity·concept·source deep links**:
- **entity·concept citation** → `#q=<title>` (non-Latin titles as-is) — see the full body, connections, and backlinks in the graph.
- **source citation** → `#q=<source-slug>` — primary source. The slug comes from `all-sources-index.md` or a wikilink in the synthesis body.
- **A `[[title]]`·`[[slug|alias]]` wikilink target in a synthesis body is itself the `#q=` key** (no separate lookup needed).

An English title resolves directly: `#q=Meta`. Because graph.html decodes the hash with `decodeURIComponent`, a non-Latin title such as `#q=신한은행` also resolves via idmap. The graph browser (full text) ↔ RAG (synthesis Q&A) complement each other.

## Operation

```bash
python tools/export.py
```

The output automatically reports file sizes and total volume + RAG budget (Core/Optional estimated tokens) + stale prune + `_site/` deploy-asset volume. It needs `_graph.json`·`_clusters.json`·`_pages.json`, so run it after `python tools/build.py` (the Action is build→export in sequence).

## Human Reviewer Gate

- External commit·push (a GitHub push is needed for the Project Knowledge integration — explicit approval from the wiki operator)
