Discover unexpected connections in the LLM Wiki (Memex serendipity).

Usage: `/wiki-discover <seed | --random | --surprising | --gaps [<slug>]>`

**If `$ARGUMENTS` is empty**: print the usage below and **stop**.

```
Usage: /wiki-discover <seed | --random | --surprising | --gaps [<slug>]>

Examples:
  /wiki-discover Meta             # start from a specific entity
  /wiki-discover AgenticAI        # start from a concept page
  /wiki-discover --random         # random seed among mid-band backlink hubs
  /wiki-discover --surprising     # auto-rank top N bridge hubs by composite score
  /wiki-discover --gaps           # 10-type gap diagnosis + Track A/B/C/D split commentary
  /wiki-discover --gaps synthesis # only a specific gap type
```

gap slug: sparse-cluster · single-source · stale-hub (A) · bridge (B) · orphan-claims · cap-theme · stale-theme (C) · synthesis · trail · timeline (D).

## Traversal Pattern

Reading domain — Meta (graph-traversal tools) + supporting Reporter commentary.

| Cycle | Owner | Action |
|---|---|---|
| Trigger | Editor-in-Chief | slash → mode branch (Mode 1: Seed Discovery / Mode 2: Surprising Bridge Hubs / Mode 3: Gap Inventory) |
| Graph traversal | Meta (`tools/discover.py` · `tools/lint.py graph gaps` · `wiki/_backlinks.json`) | seed identification · 2-hop exploration · bridge ranking · gap diagnosis |
| Surface | Reporter (mode=ground) | discovered connections + gap commentary |
| **(optional) Follow-up** | Editor-in-Chief | when the human reviewer has intent, route via re-running the seed · a deeper `/wiki-query` · `/wiki-news --gap` · a `/wiki-ingest` chain (procedure in the [`## Follow-up`](#follow-up) section below) |

## Mode 1: Seed Discovery (`<seed>` or `--random`)

1. Load `wiki/_backlinks.json`
2. Select the seed:
   - If a seed argument is given, use that entity/concept
   - If `--random`, pick a random mid-band hub with backlinks in the 5–30 range
3. **2-hop exploration** — read the seed page → read the top 5 pages by seed backlinks → identify pages among the common references that are not directly connected to the seed
4. Output format:
   ```
   ## 🔍 Discovery: starting from [seed page]

   ### Unexpected connections
   1. **[[PageA]]** ← [1-2 sentences on why it connects]
   ...

   ### Suggested explorations
   - [a question or direction worth digging into deeper]
   ```

## Mode 2: Surprising Bridge Hubs (`--surprising`)

Automatically rank, among existing hubs, the bridge nodes that cross cluster boundaries the most.

1. `python tools/discover.py surprising [--top 15] [--json]`
2. Score: `betweenness centrality × cross-cluster-ratio / log(degree + 2)`
   - **betweenness**: how often it appears on shortest paths (bridge role)
   - **cross-cluster-ratio**: the degree to which its neighbors span other clusters (cross-domain)
   - **log(degree+2) penalty**: suppresses high-degree "obvious hubs"
3. Interpreting results: the topmost hubs are the wiki's "watershed" nodes. The `neighbor_clusters` distribution immediately tells you which two clusters it bridges.

## Mode 3: Gap Inventory (`--gaps [<slug>]`)

Deterministically diagnose 10 gap types and surface them split by Track. Read-only — no auto-enrichment or authoring trigger. Follow-up actions are explicitly invoked by the human reviewer (`/wiki-news --gap` · `/wiki-lint contradiction` · a Columnist authoring chain).

Definitions, thresholds, and priorities have their SoT in [`.claude/operations/gap-detection-rollout.md`](../operations/gap-detection-rollout.md).

1. Call `python tools/lint.py graph gaps --json [--gap-type <slug>] [--top 8]`
2. Split the output JSON into 4 zones — Track A·B·C·D — with commentary:

   **Track A — auto-enrichment targets** (sparse-cluster·single-source·stale-hub) — bring in external sources
   - Recommended follow-up: `/wiki-news --gap [<slug>] [--batch]`

   **Track B — human-decision domain** (bridge + hub candidates held back from Track A)
   - Recommended follow-up: create a new bridge hub or redesign the cluster (unsuitable for auto-enrichment)

   **Track C — separate cycle** (orphan-claims·cap-theme·stale-theme)
   - Recommended follow-up: `/wiki-lint contradiction theme --fix` (theme MD rewrite · burn · orphan mapping)

   **Track D — derivation coverage** (synthesis·trail·timeline) — pages that consolidate already-accumulated material are missing. Filled by Columnist authoring rather than external search (separate from the input track)
   - synthesis missing → `/wiki-lint synthesis <slug> --fix` (skeleton + rewrite block) → Columnist authoring
   - trail missing → `/wiki-lint trail <slug> --fix` or `/wiki-trail create`
   - timeline split-out → split a hub's `## Timeline` section into a separate chronology page (`.claude/layers/hub.md` timeline)

3. End the output with a 1-line follow-up action summary per Track. Absent explicit instruction, terminate read-only.

When interpretation is ambiguous, quote and report the `thresholds` block of `lint graph gaps` verbatim.

## Follow-up

- Re-run `/wiki-discover <hub>` with 1–2 top hubs as the seed → 2-hop analysis
- If the user wants, route a deeper `/wiki-query` on a specific bridge hub, or new [[wikilink]] enrichment work
- If there is intent to enrich the Track A items from the Mode 3 results, call `/wiki-news --gap <G>`
- Delegate Track C items to `/wiki-lint contradiction theme --fix`
- Delegate Track D items to a Columnist authoring chain (`/wiki-lint synthesis|trail <slug> --fix` → authoring → self-VERIFY₀ → Desk VERIFY₂)

## Human Reviewer Gate

The read-only discovery stage has no gate of its own. If a follow-up leads to new wikilink enrichment, new page authoring, or external search, it delegates to that work's gate (e.g. `/wiki-ingest` · `/wiki-query` synthesis save · `/wiki-news --gap`).
