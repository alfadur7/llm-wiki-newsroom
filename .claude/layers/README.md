# Layers — Per-Content-Type Authoring & Review SoT

This folder holds the guidance needed to author and review **each content type** of this project's wiki (L2-1 source · L2-2 hub · L2-3 cluster overview + L2-4 root overview · L2-3 theme contradiction + L2-4 aggregate contradiction) at high quality and against a fixed format. It is the Source of Truth read on entry into the **GROUND·APPLY·ADAPT stages** (Reporter · Columnist) and the **VERIFY qualitative stage** (Desk).

## 7 Content Types + Index (8 files)

| File | Content covered | Combined areas |
|---|---|---|
| [source.md](source.md) | L2-1 source page (`wiki/sources/<slug>.md`) | Page Format · Authoring · Evaluation Rubric |
| [hub.md](hub.md) | L2-2 entity·concept hub (`wiki/entities/<slug>.md`·`wiki/concepts/<slug>.md`) | Page Format · Body Structure |
| [timeline.md](timeline.md) | L2-2 standalone timeline page (`wiki/timelines/<slug>.md`) | Page Format · Authoring · Evaluation Rubric |
| [overview.md](overview.md) | L2-3 cluster overview (`wiki/overviews/<cluster>.md`) + L2-4 root overview (`wiki/overview.md`) | Authoring (Part 1+2) · Evaluation Rubric (Part 1+2) |
| [contradiction.md](contradiction.md) | L2-3 theme contradiction (`wiki/contradictions/<theme>.md`) + L2-4 aggregate (`wiki/contradiction.md`) | Authoring (Part 1+2) · Evaluation Rubric (Part 1+2) |
| [synthesis.md](synthesis.md) | L2-3 Q-A synthesis (`wiki/syntheses/<slug>.md`) | Page Format · Authoring · Evaluation Rubric |
| [trail.md](trail.md) | L2-3 associative trail (`wiki/trails/<slug>.md`) | Page Format · Authoring · Evaluation Rubric |
| README.md | This index — Layer definitions · axis structure · common frontmatter · Root Meta Files Exception | (itself) |

## Layer Classification (Karpathy 3 tiers → 4 Layer 2 sub-layers)

| Sub-layer | File·folder | Type | GROUND·APPLY owner |
|-----------|---------|------|------|
| **L1** — Raw originals | `raw/*` | (immutable) | (external — user / mobile inbox / fetch_*.py) |
| **L2-1** — Source reflections | `wiki/sources/<slug>.md` | `source` | Reporter |
| **L2-2** — Extracted abstractions | `wiki/entities/`·`wiki/concepts/`·`wiki/timelines/`·`wiki/contradictions/_contradictions.json` (auto-generated DB, not authored) | `entity`·`concept`·`timeline`·(JSON) | stub: Reporter / full hub·timeline: Columnist |
| **L2-3** — Topic-level analyses | `wiki/overviews/<cluster>.md`·`wiki/contradictions/<theme>.md`·`wiki/syntheses/<slug>.md`·`wiki/trails/<slug>.md` | `overview`·`contradiction`·`synthesis`·`trail` | Columnist |
| **L2-4** — Wiki-wide aggregation | `wiki/overview.md`·`wiki/contradiction.md` | (root meta) | Columnist |

## Axis Structure (L2-3 ↔ L2-4)

| Axis × scope | L2-3 (per-domain) | L2-4 (wiki-wide) |
|---------|-------------|-------------|
| **Landscape** (the lay of the land, **per cluster**) | `wiki/overviews/<cluster>.md` | `wiki/overview.md` |
| **Conflict** (issues·contradictions, **per theme**) | `wiki/contradictions/<theme>.md` | `wiki/contradiction.md` |
| **Q-A** | `wiki/syntheses/<slug>.md` | — |
| **Path** | `wiki/trails/<slug>.md` | — |

**Terminology**:
- **`cluster`** — a Leiden community slug from `graph/_clusters.json`. Algorithm-produced, 1:1 mapping.
- **`theme`** — an editor-defined classification slug on the Conflict axis. Independent of cluster; may cut across several clusters.

**Aggregation principle**: each L2-4 file is responsible **only for its own axis**. `overview.md` aggregates only `overviews/*.md` bottom-up; `contradiction.md` aggregates only `contradictions/*.md`. No cross-links between axes — the entry-point role belongs solely to `wiki/index.md`.

## Common frontmatter

Every page under the sub-directories (`sources/`, `entities/`, `concepts/`, `syntheses/`, `trails/`, `timelines/`, `overviews/`, `contradictions/`) includes the following frontmatter.

```yaml
---
title: "Page Title"
type: source | entity | concept | synthesis | trail | timeline | overview | contradiction
kind: person | org | product   # entities only — person/org/product (naming.md)
tags: []
sources: []       # list of source slugs that inform this page
last_updated: YYYY-MM-DD
---
```

Per-layer additional fields (L2-1 source's `source_url`·`source_file`·`date`, L2-3 cluster overview's `cluster`, etc.) are defined by each content file (`source.md`·`overview.md`, etc.).

**Two per-type exceptions** (the content file is the SoT): a **trail** carries `created` only — no `sources:`·`last_updated:` ([trail.md](trail.md)); a **timeline** omits `sources:` ([timeline.md](timeline.md)).

## Root Meta Files Exception

The meta files at the `wiki/` root (`index.md`·`overview.md`·`contradiction.md`·`log.md`·`lint-report.md`) start directly with `# Title`, **without frontmatter**.

**Reason**: root files are not targets of `tools/build.py` or the `_backlinks.json` scanner (which process only sub-directories), so their frontmatter would not be functionally consumed.

`last_updated` management is handled instead by the re-aggregation event records in `log.md`.

## Invocation Conventions

- **GROUND·APPLY·ADAPT stages** (Reporter · Columnist) → read 1 relevant content file (e.g. the `contradiction.md` Authoring section when writing a contradiction theme).
- **APPLY-stage body prose** (common to all content types) → follow the translationese-avoidance discipline in [`../policies/language.md`](../policies/language.md) `## Prose Style` (verb-centric · avoid inanimate subjects · short sentences · reduce double passives).
- **VERIFY qualitative stage** (Desk) → the relevant content file + `.claude/agents/desk.md` (the SoT for the 6 qualitative-review lenses and the promotion loop — Cognition principle 1, full context).
- **VERIFY quantitative stage** (Copy Editor) → `tools/lint.py` automatically reads the relevant content file's Evaluation Rubric H2 section.

For per-role capability boundaries, see the [`.claude/agents/`](../agents/) SoT. For the Universal Cycle and the standard ADAPT chain, see the [`.claude/agents/README.md`](../agents/README.md) SoT.

## Trade-off — Consolidation Policy

This folder is consolidated on a **single-file-per-content-type** principle (Page Format + Authoring + Rubric in one file). Rationale:

- **Consistency with dedupe policy** — dimension definitions, execution order, and feedback loops must not be deduped. Keeping them in one file guarantees internal consistency.
- **Cognition principle 1** — the VERIFY qualitative stage (Desk) obtains both the authoring standard and the evaluation criteria in a single read. Zero message-passing loss.
- **GROUND·APPLY cross-Part awareness** — when authoring Part 1 (L2-3), the Part 2 (L2-4) aggregation constraints are naturally in view.

Per-file H2 structure (navigable):

| File | H2 structure |
|---|---|
| [source.md](source.md) | `## Page Format` → `## Authoring` → `## Evaluation Rubric` |
| [hub.md](hub.md) | `## Page Format` → `## Body Structure` (hub authoring craft has its SoT in the dotted-ID craft skills — applied to stub and full alike — so page format + body structure are combined without separate `## Authoring`·`## Evaluation Rubric` sections; stubs still receive Desk VERIFY₂ limited to format·attribution·tone) |
| [timeline.md](timeline.md) | `## Page Format` → `## Authoring` → `## Evaluation Rubric` |
| [overview.md](overview.md) | `## Authoring` (`### Part 1`·`### Part 2`) → `## Evaluation Rubric` (`### Part 1`·`### Part 2`) |
| [contradiction.md](contradiction.md) | `## Authoring` (`### Part 1`·`### Part 2`) → `## Evaluation Rubric` (`### Part 1`·`### Part 2`) |
| [synthesis.md](synthesis.md) | `## Page Format` → `## Authoring` → `## Evaluation Rubric` |
| [trail.md](trail.md) | `## Page Format` → `## Authoring` → `## Evaluation Rubric` |
