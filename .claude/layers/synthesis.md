# L2-3 Synthesis Page Guide

## Page Format

A synthesis page (`wiki/syntheses/<slug>.md`) is a **cross-source analytical answer to a standing question** — it integrates already-ingested material (source·hub·theme) into a single navigable document and frames the tensions. Its distinctive role is **question-centered integration** — not a single-source reflection (L2-1), not a single-cluster overview, and not a single-issue contradiction.

### Standard structure

```markdown
---
title: "Question/Topic (English)"
type: synthesis
tags: []
sources: [slug1, slug2, ...]   # source slugs being integrated (attribution SoT)
last_updated: YYYY-MM-DD
---

# Question/Topic

## Summary
2–4 sentences — answer the standing question conclusion-first + state the core tension in 1 line.

## 1. Title of first analysis section
Prose analysis (mix in tables as needed). Attribute claims with inline `[[source-slug]]` in the body.

## 2. Next analysis section
...

## Connections
- [[cluster-overview]] — higher-level view on the landscape axis
- [[trail-slug]] — related Memex trail
- [[ConceptA]]·[[ConceptB]] — core concepts
- [[EntityA]]·[[EntityB]] — core entities
- [[theme-slug]] — theme on the conflict axis
```

### Key schema conventions

- **`## Summary` (Summary)** = lede/abstract. Answer the standing question conclusion-first and state the core tension in 1 line (conclusion up front).
- **`## N.` analysis sections** ≥ 1. Numbered headings (`## 1.`·`## 2.` …). In the body, attribute each claim to its source with inline `[[source-slug]]` (synthesis does **not** use source pages' `cites:`·`references:` typed prefixes — inline attribution within prose).
- **`## Connections` (Connections)** = a wikilink roster grouped by axis (cluster overview · trail · concept · entity · theme). Unlike source pages, grouped by role without typed prefixes (`enc.connection-grouping`).
- **`sources:` frontmatter** = the attribution SoT for the material being integrated. Must reappear in the body (struct.source-coverage).

### Placement rules

Eligible for `wiki/syntheses/` = a **cross-source analytical answer** (has `sources:` AND has `## Connections` AND through-running prose). **Ineligible** = time-stamped news-triage / weekly briefings (`news-*`·`weekly-briefing-*` filenames, no `sources`, mostly triage tables). `python tools/lint.py synthesis` surfaces ineligible files as a `[Placement] ⚠️` advisory but does **not** auto-move or delete them (operator triage area).

### Authoring & evaluation entry points

- Authoring — [`## Authoring`](#authoring) below
- Quality judgment — [`## Evaluation Rubric`](#evaluation-rubric) below
- Recommended command — `python tools/lint.py synthesis [<slug>]` ([wiki-lint.md](../commands/wiki-lint.md))

## Authoring

This guide specifies how to author and iterate on `wiki/syntheses/<slug>.md`. A synthesis is the **Layer 2-3 Q-A axis** (.claude/layers/README.md) — an integrated analysis that answers one question across several hubs·sources·themes. The author is the Columnist (GROUND·APPLY·ADAPT). A Claude instance with no prior knowledge must be able to reproduce the same quality from this guide alone.

### Read Scope (per work scenario)

| Task | Page Format | This guide | Rubric | Auxiliary guide |
|------|------------|----------|--------|------------|
| Author 1 new synthesis | `.claude/layers/synthesis.md` | full | full | — |
| Qualitative review after Rubric PASS | same | same | same | [`agents/desk.md` 6 lenses](../agents/desk.md) |

### Which writing traditions it follows

A synthesis follows craft drawn from journalism explainer reporting, management-consulting executive answers, and the verifiable-attribution tradition. Technique definitions, criteria, and primary sources are the SoT in the craft skills' `criteria.json`·SKILL.md, referenced by **dotted ID**. The table below **maps** each part of a synthesis to its corresponding craft criterion (selection basis: comparison against any exemplar saved under `wiki/syntheses/` once query answers have been written there — no exemplar ships in the seed corpus yet).

| Synthesis component | Corresponding craft criterion (dotted ID) |
|---|---|
| `## Summary` (question, conclusion up front) | `jrn.lede` · `jrn.nutgraf` · `con.scr` · `con.so-what` |
| `## Summary` tension framing | `jrn.page` |
| `## N.` analysis sections | `jrn.explainer` · `jrn.inverted-pyramid` · `con.bold-bullet` |
| Inline source attribution in body | `cit.grounding` · `cit.grade-meta` · `cit.cite-type-meta` |
| `## Connections` per-axis roster | `enc.connection-grouping` |
| Notation·neutrality | `enc.link-density` · `enc.slug-alias` · `enc.first-mention` · `enc.verdict-restraint` · `enc.summary-style` · `enc.coatrack` |
| Numbers | `con.numeric-precision` · `con.numeric-density` |

> **A synthesis does not use `cit.cite-consistency`** (typed-prefix consistency) — because, unlike a source page, its `## Connections` has no `cites:`·`references:` prefixes. A synthesis's citation discipline is inline-claim → source attribution in the body (`cit.grounding`).

### Execution order (step-by-step guide)

1. **Identify the standing question** — fix in one sentence "which standing question/tension does this integrate an answer to."
2. **Gather material to integrate** — read the relevant source·hub·theme. Fill the attributed source slugs into frontmatter `sources:`.
3. **Write `## Summary`** — answer the question conclusion-first (`jrn.lede`) + state the core tension in 1 line (`con.scr` Resolution declaration).
4. **Write `## N.` analysis sections** — develop the argument in numbered sections. Attribute each claim with inline `[[source-slug]]` in the body (`cit.grounding`). Tables·bullets per `con.bold-bullet`.
5. **Write `## Connections`** — roster cluster overview·trail·concept·entity·theme **grouped by axis** (`enc.connection-grouping`).
6. **Update `last_updated`** — today's date on completion.
6a. **self-VERIFY₀** — confirm `python tools/lint.py synthesis <slug>` PASS. After ≤ 2 self-attempts on the same cause, either PASS or force handoff (SoT: [`agents/columnist.md`](../agents/columnist.md)).

### Authoring principles

Craft principles, criteria, and thresholds are the SoT in the craft skills' `criteria.json`·SKILL.md from the mapping table above. Below are house-style and structural conventions specific to the synthesis format:

- **Conclusion up front** (`con.so-what`): `## Summary` answers the question conclusion-first. Don't lay out background first and defer the conclusion.
- **Inline-attribution obligation** (`cit.grounding`): every key claim·number in the body is attributed to its source via `[[source-slug]]`. The narrator does not assert without a source (`enc.verdict-restraint`).
- **Integration value**: a synthesis is **a through-running analysis laid on top of** its underlying hubs·sources, not a repetition of their detail. If it's a mere summary, an overview·hub suffices.
- **Slug alias** (`enc.slug-alias`): no raw exposure of kebab-case slugs ≥ 10 chars — `[[ai-coding-10x-productivity-myth|METR 19% productivity myth]]`.
- **Numeric precision** (`con.numeric-precision`): comparison numbers state unit·basis·point-in-time.

### Feedback loop (iterate until Rubric conditions met)

Iterate and improve until the synthesis meets the completion condition (roster `synthesis.roster` — 8 required PASS + 25+/27 total PASS).

1. **Iteration 1 (draft)**: author per the execution order above.
2. **Evaluation**: the `[Rubric]` line (automatic metrics) in `python tools/lint.py synthesis <slug>` output + a body review against the mapping-table M criteria.
3. **Completion judgment**: met → done. Not met → step 4.
4. **Iteration N+1 (reinforce)**: the reinforcement criteria for each FAIL criterion are in the relevant craft skill's SKILL.md·criteria.json (the dotted IDs in the mapping table). Structural ones are in the Rubric structural section below.

**Safeguard**: on 2 consecutive FAILs of the same criterion, re-examine the criterion itself (the seed-calibration threshold-adjustment area).

## Evaluation Rubric

This Rubric pairs with "how to write" (Authoring) to judge "how well it was written." The target is `wiki/syntheses/<slug>.md`.

**Judgment method**:
- Each criterion is 3-tier: **PASS / PARTIAL / FAIL** (PARTIAL is excluded from the completion count).
- **Automatic (A)** = metrics from `python tools/lint.py synthesis [<slug>]` output. What synthesis lint measures automatically is only **structural (schema-sections·source-coverage·source-exists) + enc.slug-alias (L1)** + advisories (W1·F1·Placement).
- **Manual (M)** = judged by Claude·Desk reading the body (most of the craft mapping-table dotted IDs — `jrn.*`·`con.*`·`cit.grounding`·`enc.connection-grouping`, etc.).

**Criteria SoT**: the criterion roster·required are `_manifest.json` `synthesis.roster` (27 criteria); craft definitions·PASS conditions are the mapping-table skills' `criteria.json`·SKILL.md. Structural criteria with no external craft source are in the section below.

#### Structural criteria (not craft — held solely by layers)

| Dotted ID | Criterion | PASS condition | Judgment | Required |
|---|---|---|---|---|
| `struct.schema-sections` | Required sections complete | `## Summary` + `## Connections` present AND ≥ 1 numbered `## N.` analysis section | A | ✅ |
| `struct.source-coverage` | Sources reappear in body | of frontmatter `sources:`, the share reappearing as `[[slug]]` in the body ≥ 70% | A | ✅ |
| `struct.through-line` | Through-running narrative | a single question·tension threading the sections is stated (not a mere topic listing) | M | ✅ |

**Completion conditions** (roster `synthesis.roster` — 27 criteria):
- All 8 required (roster `required`: struct.schema-sections·struct.source-coverage·struct.source-exists·struct.through-line·enc.broken-link·jrn.lede·con.scr·cit.grounding) PASS
- **25 or more of the 27 total PASS** (= total−2, computed by `_manifest_counts` · PARTIAL excluded)
- `enc.slug-alias` (L1) is **optional (advisory)** for synthesis — inline source citations and cross-layer links legitimately expose long kebab slugs, so it is not a hard gate (report only)
- `python tools/lint.py synthesis <slug> --fix` rewrite block computes the completion-condition string from the roster

#### Reading the automatic (A) metric output

```
syntheses/<slug>.md:
  [Rubric] S1 sections=2/2+num✓ ✅  SrcCov=15/17 (88%) ✅  SrcExist=✅  L1 raw_slugs=0 ✅  W1 links=N ✅  F1 last_updated=✅
```

- **✅ = PASS**, **⚠️ = FAIL**
- **S1**: 2 sections `## Summary`+`## Connections` AND ≥ 1 numbered `## N.` section (`num✓`)
- **SrcCov**: of frontmatter `sources:`, the share reappearing as `[[slug]]` in the body ≥ 70% (exempt with `—` when no sources declared)
- **SrcExist**: each slug in frontmatter `sources:` is a real file at `wiki/sources/<slug>.md` (hallucination guard — surfaces ⚠️ + the slug list if missing)
- **L1**: 0 raw kebab slugs ≥ 10 chars (without alias) exposed in the body
- **W1** (advisory): body wikilinks ≥ 10
- **F1** (advisory): frontmatter `last_updated` present
- broken-link (enc.broken-link, required) is delegated to `python tools/lint.py graph structure`
- **[Placement]** (advisory): surfaces ⚠️ if news/briefing format (no effect on exit code)

#### Migration

This lint is in **advisory mode** (`synthesis.py` `ADVISORY_MODE = True`) — until the seed-calibration batch (consolidated-layer standardization plan, step 2) normalizes existing files and adjusts thresholds via exemplar comparison, it shows only the FAIL count and keeps exit 0. After calibration, hard-switch to `ADVISORY_MODE = False` (same precedent as source.py).

## Sources

The primary sources for the craft criteria are the SoT in each craft skill's SKILL.md `## Sources` — [`journalism-writing`](../skills/journalism-writing/SKILL.md) (Lede·Nut graph·Explainer·PAGE·inverted pyramid)·[`consulting-writing`](../skills/consulting-writing/SKILL.md) (SCR·So-what·Bold-bullet·numbers)·[`encyclopedia-writing`](../skills/encyclopedia-writing/SKILL.md) (links·notation·neutrality·connection grouping)·[`scholarly-citation`](../skills/scholarly-citation/SKILL.md) (grounding·grade/cite-type meta). Structural criteria have no external source (own convention).
