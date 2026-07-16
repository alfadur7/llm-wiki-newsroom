---
user-invocable: false
---

# Commands — 9 Slash Command SoT

This folder gathers the project's 9 slash commands in a single place. Each command file specifies its traversal pattern (which Layer × Cycle cells it passes through, and in which cycle-stage flow) plus the Human Reviewer Gate. The nature of each role and the Layer × Cycle matrix have their SoT in [`.claude/agents/README.md`](../agents/README.md).

## Task Index

The slash-argument notation in each row quotes the child file's `Usage` line as the single SoT, verbatim. Natural-language triggers are a secondary signal.

| Task | Slash | Natural-language example | SoT |
|---|---|---|---|
| Ingest | `/wiki-ingest <file\|folder\|inbox>` | "ingest raw/file.md" | [`wiki-ingest.md`](wiki-ingest.md) |
| Query | `/wiki-query <question>` | "query: ..." | [`wiki-query.md`](wiki-query.md) |
| Lint | `/wiki-lint [<group>] [<subcmd\|target>] [--fix]` | "lint the wiki" | [`wiki-lint.md`](wiki-lint.md) |
| Build graph | `/wiki-graph` | — | [`wiki-graph.md`](wiki-graph.md) |
| News search | `/wiki-news [cluster\|keyword \| --gap [<slug>] [--batch] [--no-filter]]` | — | [`wiki-news.md`](wiki-news.md) |
| Export | `/wiki-export` | (for Claude.ai Project Knowledge) | [`wiki-export.md`](wiki-export.md) |
| Discover | `/wiki-discover <seed \| --random \| --surprising \| --gaps [<slug>]>` | "diagnose gaps" → `--gaps` | [`wiki-discover.md`](wiki-discover.md) |
| Trail | `/wiki-trail <create\|follow\|list> [args]` | — | [`wiki-trail.md`](wiki-trail.md) |
| Timeline | `/wiki-timeline <entity\|concept> [year]` | — | [`wiki-timeline.md`](wiki-timeline.md) |

## Convention — "Extend Before Adding"

When introducing a new capability, first check whether it can be absorbed as a **natural extension of an existing command** (adding an argument or mode) before creating a separate slash command. More commands means more cognitive load, so adding a command is the last resort.

## Convention — "Announce Before Delegating"

Just before the Editor-in-Chief invokes one of the 4 roles (Reporter, Columnist, Desk, Copy Editor) via the `Agent` tool, it first prints one line of text stating who is being delegated which Layer × Cycle stage. This one line stays consistent with the `subagent_type` indicator that the harness shows automatically, so the multi-agent flow remains visible to the wiki operator without gaps.

Format: `Delegating {Layer} {Cycle stage} to {role}.`

Examples:
- "Delegating L2-1 GROUND·APPLY to the Reporter."
- "Delegating L2-3 cluster overview GROUND·APPLY to the Columnist."
- "Delegating VERIFY (quantitative) to the Copy Editor."
- "Requesting L2-4 VERIFY (qualitative) from the Desk."

The Editor-in-Chief's own work (routing, gating, log append) is performed directly in its own context rather than via the `Agent` tool, so no announce is needed.

### Agent `description` Argument Prefix (Double-Enforcement)

To stay consistent with the announce line above, attach a role-label prefix to the first token of the `description` argument when calling `Agent`. This is a fall-back that lets the caller immediately identify the role even when the announce was omitted.

Format: `[<role>] <3-5 word task name>`

The 4 role labels: `[Reporter]` · `[Columnist]` · `[Desk]` · `[Copy Editor]`.

Examples:
- `"[Reporter] SKT AIOps source"`
- `"[Columnist] AI coding cluster overview"`
- `"[Copy Editor] /wiki-lint source group"`
- `"[Desk] anthropic-dual-strategy 6-lens review"`

The Claude Code Agent guide's recommendation of a "3-5 word description" prioritizes clarity of meaning; if attaching the 1-token prefix slightly exceeds that, semantic consistency takes precedence.

## Natural Language Examples

Works in natural language too, without slash commands:
- "Ingest this file: raw/papers/attention-is-all-you-need.md"
- "What does the wiki say about transformer models?"
- "Check the wiki for orphan pages and contradictions"
- "Build the graph and show me what's connected to RAG"

The Editor-in-Chief analyzes the natural-language trigger and routes to the appropriate traversal pattern.

## Command SoT Standard Structure

Each command file fills the same 6 sections in the same order — so that even a command file Claude sees for the first time has a consistent skeleton and Claude knows in advance where to find what (reproducibility). When a natural-language trigger arrives, the Editor-in-Chief reads the traversal, sub-procedure, and gate from consistent locations.

1. **Nature·Trigger** (1-2 sentences or a short paragraph) — gives a self-contained statement of what task this command performs and on what trigger. A single line is fine if it is clear enough on one line.
2. **`Usage`** + usage notation + examples — the single SoT for slash-argument notation (the Task Index table quotes this line verbatim).
3. **`## Traversal Pattern`** — which cell of the [Layer × Cycle matrix](../agents/README.md#layer--cycle-matrix-design-skeleton) it passes through, in which cycle-stage flow, plus a per-stage role-assignment table.
4. **`## Sub-procedure`** (where applicable) — the area of sole responsibility of this command. Only procedures listed in the [`## Sub-procedure Locations`](#sub-procedure-locations) table below.
5. **Procedure-detail H2** — per-step tool calls, intermediate artifacts, and verification points. The generic naming is `## Operation` or `## Procedure`, but you may use a semantically clearer H2 name that fits the command's nature, e.g. `## 12-Step Procedure` (wiki-ingest), `## Mode 1 / Mode 2` (wiki-discover), `## Authoring Procedure` (wiki-timeline), or `## Common Wrap-up` + `## Synthesis Save Mode` (wiki-query). The key is that it be **readable step-by-step from a single location**.
6. **`## Human Reviewer Gate`** — the gate specific to this command. The global gates have their single SoT in [`CLAUDE.md` "Human Reviewer Gate"](../../CLAUDE.md#human-reviewer-gate).

## Sub-procedure Locations

Command-specific procedures (mapping rules, sync rules, etc.) live inside the relevant command file in this folder. This folder is their area of sole responsibility.

| Sub-procedure | Location |
|---|---|
| Contradiction Theme Mapping (raw DB → JSON mapping procedure) | [`wiki-lint.md` → `## Sub-procedure: Contradiction Theme Mapping Procedure`](wiki-lint.md#sub-procedure-contradiction-theme-mapping-procedure) |
| Conflict Axis Sync Rule (4-tier bottom-up sync) | [`wiki-lint.md` → `## Sub-procedure: Conflict Axis Sync Rule`](wiki-lint.md#sub-procedure-conflict-axis-sync-rule) |
| Parallel Batch Mode (ingest fanout) | [`wiki-ingest.md`](wiki-ingest.md) |

The [A]–[G] code definitions of the Cluster Health Diagnostic are not a separate sub-procedure; the per-code definitions · action guides are SoT in `tools/_lint/graph_clusters.py` (module docstring + report output — single SoT), with the pass/fail posture noted in the `graph clusters` row of the [`wiki-lint.md` → `## Group Structure`](wiki-lint.md#group-structure) table.

## Invocation Flow

```
User (natural language or slash) → Editor-in-Chief → decide traversal pattern
   → invoke the role for the relevant cell in the agents/README.md Layer × Cycle matrix
   → run the cycle: GROUND → APPLY → VERIFY (quantitative + qualitative) → ADAPT
   → Editor-in-Chief gate → consolidate results + log append
```

## Human Reviewer Gate Hierarchy

The `## Human Reviewer Gate` section of each command file is interpreted as the **union of the CLAUDE.md global gates and this command's specific gates**. The global gates (`ADAPT 3rd FAIL on the same cause` · `new cluster slug` · `new contradiction theme slug` · `new entity/concept stub` · `L2-4 root publish` · `guide skeleton change` · `external commit·push (inbox queue files excepted)` · `large-scale body rewrite`) have their single SoT in [`CLAUDE.md` "Human Reviewer Gate"](../../CLAUDE.md#human-reviewer-gate) — each command file does not re-list these gates and specifies **only the specific gates** that arise within its own trigger area.

Decision steps when adding a new command:
1. Which Layer × which Cycle cell is the traversal?
2. Can it be absorbed by extending an existing command? (Extend Before Adding)
3. Does it have a sub-procedure that is this command's sole responsibility?
4. Beyond the CLAUDE.md global gates, does this command have a specific gate?
