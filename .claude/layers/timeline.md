# L2-2 Timeline Page Guide

## Page Format

A standalone timeline page (`wiki/timelines/<slug>.md`) is a **source-indexed chronology** — an index that strings together the sources covering one topic in date order, plus the through-running narrative of that trajectory. It is a **path overlay** (ordered members) like a trail, but where a trail strings hubs into a learning path, a timeline strings **sources in chronological order**. Unlike the `## Timeline` (Timeline) summary section in a hub body (pointer-style, [hub.md](hub.md)), a standalone timeline page's purpose is for **each entry to directly index a source**.

### Standard structure

```markdown
---
title: "Timeline: Topic Name"
type: timeline
tags: []
last_updated: YYYY-MM-DD
---

## Timeline: [[Hub]] (N entries)

## Flow Summary

**Trajectory overview**: Phase-1 stage (YYYY) → Phase-2 stage (YYYY) → … one-line arrow trajectory.

- **YYYY~YYYY phase name**: that period in one paragraph. Point to key events·entities with `[[entity]]`, while detail·numbers stay with the source.
- …

**Latest state**: current phase in 1–2 sentences. Name the count of inflection points (★).

---

### YYYY (N entries)
- **YYYY-MM-DD** [[source-id]] — one-line event summary.
- ★ **YYYY-MM-DD** [[source-id]] — inflection-point event, one line.
…
```

### Key schema conventions

- **frontmatter** = `title`·`type`·`tags`·`last_updated`. (Same common schema as source·hub. Differs from trail's `created`-only exception.)
- **`## Flow Summary` (Flow summary)** = trajectory overview (one-line arrow) + per-period phase paragraphs + latest state. **No restating facts·numbers·quotes** (`enc.summary-style`) — detail is the SoT in the indexed sources.
- **`### YYYY (N entries)`** = per-year dated entries (H1·year `(N entries)` = total count of dated entries, including historical anchors). **Each entry's first wikilink is `[[source-id]]`** (struct.source-indexed) — the condition for classifying the overlay as `path` (builder `tools/_build/overlays.py:_timeline_overlay`, `src_n > hub_n`).
  - **Date**: the most precise form available — `YYYY-MM-DD` preferred; use `YYYY-MM` when the source supports only the month or `published` is absent (no day-level — `scraped` is the collection date, not the event date). The inflection mark `★` goes before the date — assigned to a policy-regime shift, a key institution's first adoption, or a market-structure inflection.
  - **Lossless historical·future anchors**: pre-ingest events without sources (founding-era milestones)·future roadmaps should **not be dropped** — write them entity-first as `- **YYYY** — [[entity]] description` / `- **YYYY (planned)** —` and **inline chronologically into that year's `### YYYY` section** (no separate anchor section — chronological readability). Being few, they don't break the path classification (`src_n > hub_n`) and remain on the date axis as entity-node members.
  - **Raw source-id exposure allowed**: a long kebab slug in a dated entry like `[[broadcom-vmware-…]]` is exempt from `enc.slug-alias` because **indexing is the purpose** (a key difference from trail). But in `## Flow Summary` prose, no raw slug exposure (use the common display name·`[[entity]]`).

### Authoring & evaluation entry points

- Authoring — [`## Authoring`](#authoring) below
- Quality judgment — [`## Evaluation Rubric`](#evaluation-rubric) below
- Recommended command — `python tools/lint.py timeline [<slug>]` ([wiki-lint.md](../commands/wiki-lint.md))

## Authoring

This guide specifies how to author and iterate on `wiki/timelines/<slug>.md`. A timeline is a **Layer 2-2 path overlay** ([README.md](README.md)) — a chronology stringing sources in time order. The author is the Columnist. A Claude instance with no prior knowledge must be able to reproduce the same quality from this guide alone.

### Read Scope (per work scenario)

| Task | Page Format | This guide | Rubric | Auxiliary guide |
|------|------------|----------|--------|------------|
| Author 1 new timeline | `.claude/layers/timeline.md` | full | full | — |
| Convert region → source-indexed | same | full | full | source corpus GROUND |
| Qualitative review after Rubric PASS | same | same | same | [`agents/desk.md` 6 lenses](../agents/desk.md) |

### Which writing traditions it follows

A timeline follows the encyclopedic summary-style and verifiable-attribution traditions. `## Flow Summary` compresses the trajectory without restating facts (`enc.summary-style`), and dated entries attribute events to a source (the `cit.*` spirit — the first link is the source). References are by **dotted ID**, definitions are the SoT in the craft skills.

| Timeline component | Corresponding craft criterion (dotted ID) |
|---|---|
| `## Flow Summary` trajectory narrative | `enc.summary-style` · `jrn.lede` (one-line overview) · `enc.first-mention` |
| `### YYYY` dated entries | `struct.source-indexed` (first link = source) · `enc.broken-link` |
| Overall prose notation | `enc.link-density` · `house.sentence-length` |

### Execution order (step-by-step guide)

1. **GROUND — identify sources**: identify topic-related sources in `wiki/sources/` in time order (qmd local search + Glob). For each event → fix the corresponding source-id **after confirming it exists** (do not invent one).
2. **Write `## Flow Summary`** — trajectory overview (one-line arrow) + per-period phase paragraphs + latest state. Trajectory only, without restating facts·numbers (`enc.summary-style`).
3. **Write `### YYYY` dated entries** — years descending, each entry `- **YYYY-MM-DD** [[source-id]] — one line` (only sourceless historical anchors are `[[entity]]`-first). The one-line summary must be a fact the indexed source actually supports, and beware of mis-indexing a different event on the same date — cross-check against the source body (mis-attribution is the biggest risk, caught by Desk). **Inferred indexing**: if the event date precedes the indexed source's publication date and the source mentions it only as a retrospective·prior-precedent·vendor self-report rather than first-hand reporting, attach the caveat `(recorded as a prior precedent by the YYYY source)` to the line (blocks the impression of a first-hand report that does not exist).
3a. **self-VERIFY₀** — `python tools/lint.py timeline <slug>` → confirm `SourceIndexed … → path ✅`. After ≤ 2 self-attempts on the same cause, either PASS or force handoff.

### Feedback loop (iterate until Rubric conditions met)

Iterate and improve until the timeline meets the completion condition (roster `timeline.roster` — 3 required PASS + 5+/7 total PASS).

1. **Iteration 1 (draft/conversion)**: author per the execution order above.
2. **Evaluation**: the `[Rubric]` line (automatic metrics) in `python tools/lint.py timeline <slug>` output + a body review against the mapping-table M criteria.
3. **Completion judgment**: met → done. Not met → step 4.
4. **Iteration N+1 (reinforce)**: the reinforcement criteria for each FAIL criterion are in the relevant craft skill·structural section.

## Evaluation Rubric

This Rubric pairs with "how to write" (Authoring) to judge "how well it was written." The target is `wiki/timelines/<slug>.md`.

**Judgment method**:
- Each criterion is 3-tier: **PASS / PARTIAL / FAIL** (PARTIAL is excluded from the completion count).
- **Automatic (A)** = metrics from `python tools/lint.py timeline [<slug>]` output. What timeline lint measures automatically is **structural (schema-sections·source-indexed)**.
- **Manual (M)** = judged by Claude·Desk reading the body (`enc.summary-style`·`enc.first-mention`, etc.).

**Criteria SoT**: the criterion roster·required are `_manifest.json` `timeline.roster` (7 criteria); craft definitions are the mapping-table skills' `criteria.json`·SKILL.md. Structural criteria with no external craft source are in the section below.

#### Structural criteria (not craft — held solely by layers)

| Dotted ID | Criterion | PASS condition | Judgment | Required |
|---|---|---|---|---|
| `struct.schema-sections` | Required sections complete | `## Flow Summary` + ≥ 1 `### YYYY` dated section present | A | ✅ |
| `struct.source-indexed` | Source-indexed (path classification) | among dated entries, source-led (first link is a real file in `wiki/sources/`) > entity-led, and source-led ≥ 1 | A | ✅ |

**Completion conditions** (roster `timeline.roster` — 7 criteria):
- All 3 required (roster `required`: struct.schema-sections·struct.source-indexed·enc.broken-link) PASS
- **5 or more of the 7 total PASS** (= total−2, computed by `_manifest_counts` · PARTIAL excluded)
- `python tools/lint.py timeline <slug> --fix` rewrite block computes the completion-condition string from the roster

#### Reading the automatic (A) metric output

```
timelines/<slug>.md:
  [Rubric] S1 schema=flow-summary+YYYY ✅  SourceIndexed src=25/hub=7/total=32 → path ✅
```

- **✅ = PASS**, **⚠️ = FAIL**
- **S1**: `## Flow Summary` + ≥ 1 `### YYYY` section present
- **SourceIndexed**: classification of dated entries' first links — if `src` (source-led) > `hub` (entity-led), classified as `path` and PASS. If `region`, it's a conversion target (make the first link `[[source-id]]`)
- broken-link is delegated to `python tools/lint.py graph structure`

#### Migration

This lint is in **advisory mode** (`timeline.py` `ADVISORY_MODE = True`) — until the seed-calibration batch (converting the remaining region timelines to source-indexed), it shows only the FAIL count and keeps exit 0. After calibration, hard-switch to `ADVISORY_MODE = False`. Conversion is lossless on principle (historical anchors preserved).

## Sources

The primary sources for the craft criteria are the SoT in each craft skill's SKILL.md `## Sources` — [`encyclopedia-writing`](../skills/encyclopedia-writing/SKILL.md) (summary style·first mention·links·neutrality)·[`scholarly-citation`](../skills/scholarly-citation/SKILL.md) (source attribution). The structural criteria (schema-sections·source-indexed) have no external source (own convention — consistent with the builder's path/region classification).
