# L2-3 Trail Page Guide

## Page Format

A trail page (`wiki/trails/<slug>.md`) is an **ordered associative path** (Memex trail-blazing) — it strings 5–12 hubs (authoring target; the lint struct.path-length band is 4–12) into a single line for a learner to walk along, plus the through-running narrative of that path. Its distinctive role is a **navigation path** — not a single-domain overview, and not a question synthesis.

### Standard structure

```markdown
---
title: "Path Title (English)"
type: trail
tags: []
created: YYYY-MM-DD
---

## Path

1. [[Hub1]] — starting-point role · one-line transition commentary.
2. [[Hub2]] — reason for the transition to the next step.
...

## Commentary

1–2 paragraphs — name the path's through-running narrative and tension.
```

### Key schema conventions

- **frontmatter** = `title`·`type`·`tags`·`created`. Unlike source·hub, a trail does **not** keep `last_updated`·`sources:` (only `created` at authoring time — accommodating existing trail reality).
- **`## Path` (Path)** = a numbered ordered list. Each item is in the form `N. [[Hub]] — commentary`, starting with a wikilink (struct.path-links). Hop count 4–12 (struct.path-length).
- **`## Commentary` (Commentary)** = a 1–2 paragraph through-running narrative. Names what the path shows and what tension·paradox it has (struct.through-line).

### Authoring & evaluation entry points

- Authoring — [`## Authoring`](#authoring) below
- Quality judgment — [`## Evaluation Rubric`](#evaluation-rubric) below
- Recommended command — `python tools/lint.py trail [<slug>]` ([wiki-lint.md](../commands/wiki-lint.md))

## Authoring

This guide specifies how to author and iterate on `wiki/trails/<slug>.md`. A trail is the **Layer 2-3 Path axis** (.claude/layers/README.md) — an associative path stringing existing hubs in order. The author is the Columnist. A Claude instance with no prior knowledge must be able to reproduce the same quality from this guide alone.

### Read Scope (per work scenario)

| Task | Page Format | This guide | Rubric | Auxiliary guide |
|------|------------|----------|--------|------------|
| Author 1 new trail | `.claude/layers/trail.md` | full | full | — |
| Qualitative review after Rubric PASS | same | same | same | [`agents/desk.md` 6 lenses](../agents/desk.md) |

### Which writing traditions it follows

A trail follows the journalism explainer-reporting·kicker traditions. Each step of the path explains "why this connection" in one line (explainer), and the closing commentary closes out the whole path's insight (kicker). References are by **dotted ID**, definitions are the SoT in the craft skills. The table below maps each part of a trail to craft (selection basis: comparison against any exemplar saved under `wiki/trails/` once a trail has been written there — no exemplar ships in the seed corpus yet).

| Trail component | Corresponding craft criterion (dotted ID) |
|---|---|
| `## Path` per-hop commentary | `jrn.explainer` · `enc.first-mention` · `enc.slug-alias` |
| `## Commentary` through-running narrative | `jrn.kicker` · `enc.verdict-restraint` |
| Overall links·notation | `enc.link-density` |

> A trail's `## Commentary` is a short navigation essay, so it does not use `con.scr` (the management-document Situation-Complication-Resolution structure) — for closing insight, `jrn.kicker` is the right craft.

### Execution order (step-by-step guide)

1. **Select the path line** — identify 5–12 hubs (authoring target; the lint struct.path-length band is 4–12) that run through one topic, in order (chronological·causal·learning order).
2. **Write `## Path`** — each hop as a numbered item `N. [[Hub]] — role·transition commentary`. Each line starts with a wikilink (with `jrn.explainer`, one line of "why this connection").
3. **Write `## Commentary`** — name the path's through-running narrative and tension in 1–2 paragraphs (`jrn.kicker`).
3a. **self-VERIFY₀** — confirm `python tools/lint.py trail <slug>` PASS. After ≤ 2 self-attempts on the same cause, either PASS or force handoff.

### Authoring principles

Craft principles·criteria are the SoT in the mapping-table skills' `criteria.json`·SKILL.md. Below are conventions specific to the trail format:

- **One-line commentary per item**: each hop does not merely list the hub name but explains in one line "why this step·how it leads to the next" (`jrn.explainer`).
- **Name the through-running narrative**: `## Commentary` states the big picture·paradox the path reveals (`jrn.kicker`). No mere re-listing of steps.
- **Hub location of hop causal grounds (no hop displacement)**: the causal claim each hop N→N+1 commentary makes must actually exist in the body of hub N or N+1. If the grounds exist only in an adjacent hop (N-1, etc.), either call that hop in the commentary and make the bridge explicit, or reorder — wikilink existence (broken-link 0) does not guarantee the connection's validity, and a leap whose grounds are displaced to another hop is surfaced in Desk qualitative review.
- **Slug alias** (`enc.slug-alias`): no raw exposure of kebab-case slugs ≥ 10 chars.

### Feedback loop (iterate until Rubric conditions met)

Iterate and improve until the trail meets the completion condition (roster `trail.roster` — 5 required PASS + 10+/12 total PASS).

1. **Iteration 1 (draft)**: author per the execution order above.
2. **Evaluation**: the `[Rubric]` line (automatic metrics) in `python tools/lint.py trail <slug>` output + a body review against the mapping-table M criteria.
3. **Completion judgment**: met → done. Not met → step 4.
4. **Iteration N+1 (reinforce)**: the reinforcement criteria for each FAIL criterion are in the relevant craft skill·structural section.

## Evaluation Rubric

This Rubric pairs with "how to write" (Authoring) to judge "how well it was written." The target is `wiki/trails/<slug>.md`.

**Judgment method**:
- Each criterion is 3-tier: **PASS / PARTIAL / FAIL** (PARTIAL is excluded from the completion count).
- **Automatic (A)** = metrics from `python tools/lint.py trail [<slug>]` output. What trail lint measures automatically is **structural (schema-sections·path-links·path-length) + enc.slug-alias (L1)**.
- **Manual (M)** = judged by Claude·Desk reading the body (`jrn.explainer`·`jrn.kicker`·`struct.through-line`, etc.).

**Criteria SoT**: the criterion roster·required are `_manifest.json` `trail.roster` (12 criteria); craft definitions are the mapping-table skills' `criteria.json`·SKILL.md. Structural criteria with no external craft source are in the section below.

#### Structural criteria (not craft — held solely by layers)

| Dotted ID | Criterion | PASS condition | Judgment | Required |
|---|---|---|---|---|
| `struct.schema-sections` | Required sections complete | `## Path` + `## Commentary` present | A | ✅ |
| `struct.path-links` | Path items linked | all numbered items in `## Path` start with `N. [[Hub]]` | A | ✅ |
| `struct.path-length` | Path length | hop count 4–12 | A |  |
| `struct.through-line` | Through-running narrative | `## Commentary` names the path's insight·tension (not a mere re-listing) | M | ✅ |

**Completion conditions** (roster `trail.roster` — 12 criteria):
- All 5 required (roster `required`: struct.schema-sections·struct.path-links·struct.through-line·enc.broken-link·enc.slug-alias) PASS
- **10 or more of the 12 total PASS** (= total−2, computed by `_manifest_counts` · PARTIAL excluded)
- `python tools/lint.py trail <slug> --fix` rewrite block computes the completion-condition string from the roster

#### Reading the automatic (A) metric output

```
trails/<slug>.md:
  [Rubric] S1 sections=2/2 ✅  PathLinks=10/10 ✅  PathLen=10 (4–12) ✅  L1 raw_slugs=0 ✅
```

- **✅ = PASS**, **⚠️ = FAIL**
- **S1**: 2 sections `## Path`+`## Commentary` present
- **PathLinks**: share of `## Path` numbered items starting with `N. [[...]]` = PASS when all
- **PathLen**: hop count 4–12
- **L1**: 0 raw kebab slugs ≥ 10 chars (without alias) exposed in the body
- broken-link is delegated to `python tools/lint.py graph structure`

#### Migration

This lint is in **advisory mode** (`trail.py` `ADVISORY_MODE = True`) — until the seed-calibration batch (consolidated-layer standardization plan, step 2), it shows only the FAIL count and keeps exit 0. After calibration, hard-switch to `ADVISORY_MODE = False`.

## Sources

The primary sources for the craft criteria are the SoT in each craft skill's SKILL.md `## Sources` — [`journalism-writing`](../skills/journalism-writing/SKILL.md) (Explainer·Kicker)·[`encyclopedia-writing`](../skills/encyclopedia-writing/SKILL.md) (first mention·slug-alias·links·neutrality). Structural criteria have no external source (own convention).
