Query the LLM Wiki and synthesize an answer.

Usage: `/wiki-query <question>` — required argument

**If `$ARGUMENTS` is empty**: print the usage below and **stop**.

```
Usage: /wiki-query <question>

Examples:
  /wiki-query OpenSourceInitiative open source AI definition
  /wiki-query What are the main themes across all sources?
  /wiki-query summarize the open weights vs open source debate
```

## Traversal Pattern

Classify the question as one of 6 types (Entity-centric / Relation / Topic / Fact / Meta / Contradiction), then branch.

| Mode | Cycle | Owner |
|---|---|---|
| **Simple answer** (no save) | Reading | Reporter (mode=ground) — broad wiki read + `tools/query.py graph` + answer synthesis |
| **Synthesis save** | L2-3 synthesis cycle | Columnist GROUND·APPLY → Copy Editor → Desk → Editor-in-Chief gate |

The rule for question-type classification → mode branch is the sole responsibility of the [`## Mode Routing`](#mode-routing-query-type--mode-dispatch) section below.

## Question Type Classification (6 Types)

Read the question and classify it as 1 of 6 types, then enter the relevant procedure. When ambiguous, default to Topic.

| Type | Trigger | Recommended `--edge-type` | Entry tool |
|---|---|---|---|
| **Contradiction** | "Contradiction between A and B?", "What's at issue?" | `contradicts` | `tools/query.py graph neighbors X --edge-type contradicts` |
| **Entity-centric** | "What does X cite·oppose?" | `cites,contradicts` | `tools/query.py graph neighbors X` |
| **Topic** | "Overview of field X", "Definition of X" | `defines,cites` | `mcp__qmd__query` (structured: `intent`+`vec`/`lex`) |
| **Fact** | "Did X announce Y?" | `cites` | `mcp__qmd__query` (`lex`-centered) |
| **Relation** | "Relationship between A and B?" | (full default) | `tools/query.py graph explain A B` |
| **Meta** | "Wiki structure", "Hub distribution" | (full default) | read root meta pages |

**Additional natural-language intent mapping** (when the user does not state one of the 6 types):
- "where opinions diverge" · "controversy" → `--edge-type contradicts`
- "primary source" · "announcement·citation" → `--edge-type cites`
- "defined concept" → `--edge-type defines`
- "simple mention" → `--edge-type references`
- "appearing together" · "co-occurring" → `--edge-type inferred`

`mcp__qmd__query`·`mcp__qmd__get` are available only when the qmd MCP is installed (separate setup — see the "Local semantic search" section in `README.md`). Topic·Fact fallback in an uninstalled environment: `tools/query.py graph neighbors` + direct Read of candidate pages.

Combining multiple types: `--edge-type cites,contradicts`. **The natural-language intent mapping is merely a secondary signal for `--edge-type` and is unrelated to the mode branch** — the mode is decided solely by the table below.

**Search craft** (how to drive the content-search entry tool):
- If you know the exact term·title·person name, lean `lex`; for conceptual·indirect phrasing, lean `vec`.
- **Write the `intent` (what you seek + the nearby concepts to avoid)·`lex`·`vec` of `mcp__qmd__query` yourself** — do not pass the user's sentence as-is and leave it to the expansion model.
- Agents use the MCP. `tools/query.py qmd …` is the path for human terminals·documentation examples.

## Mode Routing (Query Type → Mode Dispatch)

The default is that all types are **simple-answer** (Reporter mode·no save). A synthesis save is decided by two signals: **the per-type default recommendation + explicit approval from the wiki operator**.

| Type | Default mode | Synthesis save recommendation | Follow-up chain (optional) |
|---|---|---|---|
| **Topic** | simple-answer | **Recommended** — field overviews·concept definitions have lasting value as a wiki asset | on finding a missing overview·hub, route `/wiki-ingest` or hub-stub enrichment |
| **Contradiction** | simple-answer | Not recommended — the issue SoT is `wiki/contradictions/<theme>.md` (synthesis would duplicate it) | on finding a new issue, chain `/wiki-lint contradiction theme --fix` |
| **Entity-centric** | simple-answer | Not recommended — information is concentrated in the entity hub | on finding a missing hub fact, route a hub update |
| **Relation** | simple-answer | Optional — only when the two-hub relationship narrative is a new insight not in the wiki | — |
| **Fact** | simple-answer | Not recommended — simple fact verification | — |
| **Meta** | simple-answer | Not recommended — wiki-structure analysis is one-off | route `/wiki-graph`·`/wiki-discover` |

Branch flow:
1. The Reporter synthesizes an answer in simple-answer mode (see [`## Common Wrap-up`](#common-wrap-up-reporter-simple-answer-mode) below)
2. At the end of the answer, combine the "Synthesis save recommendation" signal from the table above with the wiki operator's remarks this turn to propose whether to save
3. On explicit approval from the wiki operator, enter [`## Synthesis Save Mode`](#synthesis-save-mode-columnist-cycle) (Columnist cycle)
4. If unstated·declined, end the turn — output only the answer, no save

## Common Wrap-up (Reporter Simple-Answer Mode)

- Search results (snippets·docids) are **only a lead** — pull the body via `mcp__qmd__get`/`multi_get` for facts·quotes·nuance before answering. Read the top ≤10 pages
- Synthesize an answer with `[[PageName]]` wikilinks including citations
- End the answer with a `## Sources` section listing the referenced pages
- Right after the answer, per the per-type recommendation signal in the [`## Mode Routing`](#mode-routing-query-type--mode-dispatch) table above, propose to the wiki operator whether to save to `wiki/syntheses/<slug>.md`

## Synthesis Save Mode (Columnist Cycle)

On a save decision, enter the L2-3 synthesis authoring cycle:
1. Columnist GROUND — the simple-answer material + additional reading (own context)
2. Columnist APPLY — write the synthesis page (frontmatter + answer + citations·attribution)
3. Copy Editor VERIFY₁ — schema·attribution
4. Desk VERIFY₂ — qualitative review (Q-A persona)
5. Editor-in-Chief publish gate + `log.md` append

## Edge Filter (Phase 2 Routing)

The path·explain·neighbors subcommands of `tools/query.py graph` all support the `--edge-type <kinds>` option — traverse only some of the 5 edge types (`contradicts` / `cites` / `defines` / `references` / `inferred`).

## Empty-Wiki Handling

If the wiki is empty, say so and suggest `/wiki-ingest`.

## Human Reviewer Gate

- Synthesis save decision (memory git-approval — new page creation)
- Desk qualitative-review defects of critical/high
