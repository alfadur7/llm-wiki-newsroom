# L2-3 Theme Contradiction + L2-4 Aggregate Guide

## Authoring

This guide specifies how to author the EDITOR block of a conflict-axis issue file. There are two scopes; apply only the relevant Part depending on the scope of your work:

- **Part 1 — Theme Contradiction (L2-3)**: `wiki/contradictions/<theme>.md`, a single-issue analysis file. It explains one axis of contention through the evidence of the A·B(+C) camps.
- **Part 2 — Aggregate Contradictions (L2-4)**: `wiki/contradiction.md`, the global issue-survey file. A bottom-up roll-up of **N theme files** (the current theme count is confirmed dynamically as the number of keys in `wiki/contradictions/_contradictions_themes.json::themes`) plus a global tension-axis narrative.

**Internal read order for this guide**: whichever Part you work on, first read the **Common Background** below (editorial tradition · craft mapping table) carefully, then move to your Part. For the craft definitions shared by both Parts, the skills in the mapping table are the SoT; each Part's authoring principles sit on top of that with only the rules specific to this project's data and procedures.

A Claude with no prior knowledge must be able to reproduce the same quality by reading this guide alone (the Claude-reproducibility principle).

### Read Scope (by work scenario)

When you enter a task, first identify the single row that matches your scenario, then read carefully only the four columns of that row — CLAUDE.md section · this guide · Rubric · supporting guide. No additional reading beyond the table is necessary.

| Task | CLAUDE.md section | This guide | Rubric | Supporting procedure |
|------|---------------|----------|--------|------------|
| Author a new theme MD (`wiki/contradictions/<theme>.md`) | Roles · Universal Cycle · Human Reviewer Gate | Common Background + Part 1 | Part 1 | [`commands/wiki-lint.md` → Contradiction Theme Mapping](../commands/wiki-lint.md#sub-procedure-contradiction-theme-mapping-procedure) (claim → theme mapping procedure) |
| Rewrite the aggregate (`wiki/contradiction.md`) | Roles · Universal Cycle · Human Reviewer Gate | Common Background + Part 2 | Part 2 | — |
| Both tasks together (theme batch follow-up) | Union of the two rows above | Common Background + all | All | Same as above |
| Qualitative review cycle after Rubric PASS | Same as the relevant scenario | Same as the relevant scenario | Same as the relevant scenario | [`agents/desk.md` → 6-lens qualitative review](../agents/desk.md) |

### Common Background (applies to Part 1 and Part 2)

#### Which writing tradition does this follow

The goal of an issue document is to **juxtapose opposing viewpoints and fairly give the reader the material to judge for themselves**. Unlike the beat-report and summary style of a landscape-axis overview, it follows the dialectical, argumentative, and neutral-balance traditions, and **the definition, authoring criteria, and original source of each technique are owned by the craft skill's SKILL.md as SoT**. When entering authoring (Columnist) or review (Desk), explicitly read the relevant skill:

- [`journalism-writing`](../skills/journalism-writing/SKILL.md) — Hegelian dialectic (thesis·antithesis·synthesis) · Toulmin argument (Claim-Warrant · Rebuttal · Qualifier) · synthesis monitoring balance · C-stance convention
- [`encyclopedia-writing`](../skills/encyclopedia-writing/SKILL.md) — NPOV (ASF attribution · due weight · neutral faction labels · verdict restraint) · landscape back-reference · slug alias · roll-up drill/balance/coatrack
- [`scholarly-citation`](../skills/scholarly-citation/SKILL.md) — citation consistency for synthesis writing (cite consistency · evidence grounding · anchoring) · use of evidence-grade / citation-type metadata
- [`consulting-writing`](../skills/consulting-writing/SKILL.md) — (Part 2) MECE completeness of tension axes

The table below is the **mapping** of which part of an issue page corresponds to which craft criterion (dotted IDs; definitions live in each skill's `criteria.json` · SKILL.md):

| Wiki component | Corresponding craft criterion (dotted ID) |
|-----------|-----------|
| `## Opposing Positions` (Opposition Structure — thesis·antithesis declaration) | `jrn.thesis-antithesis` · `jrn.toulmin-claim` · `enc.npov-asf` · `enc.label-neutral` · `jrn.c-section-size` · `jrn.c-stance-naming` |
| `## Representative Evidence` (Representative Evidence — grounding) | `enc.due-weight` · `cit.cite-consistency` · `cit.grounding` · `cit.anchor-evidence` |
| `## Derived Tensions & Generational Readings` (Derived Tensions · Generational Readings — rebuttal·qualifier) | `jrn.rebuttal` · `jrn.qualifier` |
| `## Interpretive Direction` (Interpretive Direction — synthesis) | `jrn.monitoring-balance` · `enc.verdict-restraint` |
| Notation·linking throughout the document | `enc.link-density` · `enc.slug-alias` · `enc.back-reference` |
| Use of schema metadata | `cit.grade-meta` · `cit.cite-type-meta` |
| (Part 2 additional) Tension-axis completeness · drill · balance · scope | `con.mece-axes` · `enc.summary-style` · `enc.due-balance` · `enc.coatrack` |

The `Claim type 4-way classification` (the `type` field in `_contradictions.json` — **real**: clear opposition · **superseded**: a resolved past issue · **related**: reference · **soft**: classification failed) is a term in this wiki's data schema, and it governs theme tone and qualifier strength (structural `struct.type-reflection`).

### Part 1 — Theme Contradiction Authoring Guide

**What this Part explains**: how to author a `wiki/contradictions/<theme>.md` file. This file is a **deep-analysis page for a specific theme (an issue classification defined by the editor)**, unpacking one axis of contention together with its evidence. For example, `open-training-data-requirement.md` covers the issue "OSAID Definition vs Open Training-Data Requirement."

#### File structure — frontmatter + 4 EDITOR sections

The theme file **has no internal-management AUTO block** (a structural difference from landscape-axis overviews). The related raw claim data (`_contradictions.json`) and the theme ↔ claim mapping (`_contradictions_themes.json`) exist only in the program-layer JSON, while the theme page the reader sees consists of pure editorial content (frontmatter + 4 H2 sections). When authoring, Claude reads these JSONs directly and uses them as material.

#### Execution order (step-by-step guide)

The concrete procedure a Claude performing this task for the first time should follow. The output of each step becomes the input to the next.

1. **Confirm the target theme**: Read `wiki/contradictions/_contradictions_themes.json` to confirm the slug · name · claim_ids of the theme to author. The theme slug is editor-defined and independent of the cluster slug, so it may cut across several clusters.
2. **Confirm the file exists**: if `wiki/contradictions/<theme>.md` does not exist, first auto-generate the skeleton with `/wiki-lint contradiction --fix`. When a theme declared in the JSON has no corresponding MD, this command generates it from the Theme Contradiction Format template (frontmatter + 4 H2 TODO placeholders).
3. **Read through claim_ids**: after obtaining the target theme's `claim_ids` array from `_contradictions_themes.json`, Read `_contradictions.json` and resolve the record (`source` · `claim` · `type` · `type_score` · `evidence_strength`) corresponding to each id. This claim list is the **primary material** for the body narrative. **Grasp 100% of the claims exhaustively** (sources are read selectively — see step 4). The two scores are orthogonal — `type_score` is the strength of the classification keyword match, and `evidence_strength` is the Phase-2-metadata-based evidence strength (weighted by anchor · recency · share of primary sources · hub type). A claim with both ≥ 0.6 is a priority candidate for ## Representative Evidence; a claim with both ≤ 0.3 is a candidate for drop review.
4. **Register frontmatter `sources:` (Step 1 Select)**: use **both JSONs together** — the ones loaded into memory in step 3 — as input for this step: `_contradictions_themes.json` (theme → claim_ids mapping) + `_contradictions.json` (the claim records' `source` · `type` · `type_score` · `evidence_strength`). If you enter this step having read only one of them, Step 1 Select breaks, so do not enter this step before completing the reads in step 3. From the two JSONs, register in the frontmatter `sources:` array the sources you judge valuable (A/B(+C) camp evidence · background context · term definitions · qualifier · rebuttal material · landscape back-reference), using **descending sort by `evidence_strength` as the primary criterion** (for the detailed matrix, see "Score-based prioritization" in the authoring principles below). The frontmatter serves as the editor's **"official reference declaration,"** becoming the superset of the later Step 2 Read · Step 3 Cite. This array is used as input for generating the graph and `_backlinks.json` in `tools/build.py`.
5. **Identify the related cluster overview(s)**: judge which cluster survey(s) this theme relates to → skim the `## Overview` (Overview) · `## Subtopics` (Subtopics) of `wiki/overviews/<cluster>.md` (securing landscape-axis back-reference material). **Mapping rule**: if the name of the target theme (`_contradictions_themes.json::themes[<slug>].name`, English by default) or the core keywords extracted from its `claim_ids` overlap semantically with a cluster name (`_clusters.json::clusters[].name`), it is a candidate. 1:N mapping (one theme cutting across several clusters) is allowed and normal. Do not keep a static mapping table in the guide — both the theme and cluster SoTs change over time.
6. **Read through representative-evidence sources (Step 2 Read)**: among the sources registered in the frontmatter via Step 1 Select, select as representative evidence the **top 5–6 by `evidence_strength` + 1 preserved from the mid/old segment of the recency distribution** (historical origin · prevents recency bias) (the Rubric S2 band is 3–7, and this top 5–6 + 1 preserved target sits within it; see "Score-based prioritization" in the authoring principles below). Open the selected source MDs with the `Read` tool and read through the `## Summary` (Summary) · `## Key Claims` (Key Claims) · `## Key Quotes` (Key Quotes) · `## Connections` (Connections) sections. **This Read is mandatory** — because claim text is a one-sentence summary, material such as the original-quote of an N1 ASF attribution, specific figures, the camp's self-acknowledged limitations in a T3 Rebuttal, internal logical contradictions, or research-design limitations is often absent from the claim text. Writing from memory or guesswork without reading risks mismatch with the source. **Sources used for qualifiers or background context are not subject to the mandatory Read** — registering them in frontmatter based on claim text alone is sufficient (handled in Step 1).
7. **Author the 4 H2 sections (Step 3 Cite)**: use the `Edit` tool to replace each section's `_TODO: ...` placeholder with real content. For how to author the four sections, see "Role division of the 4 EDITOR sections" + "Authoring principles" below. When writing the body, insert as a `[[<slug>]]` or `[[<slug>|display alias]]` wikilink only those frontmatter-registered sources that **fit the context of that paragraph**. Even if a source is in the frontmatter, you may choose not to cite it in the body if the context does not fit. **Consistency principle (Rubric L2 enforced)**: every claim-related source that appears in the body via wikilink or substring **must be registered in the frontmatter** (body ⊆ frontmatter). Step 1 Select must register a broad enough set for Step 3 Cite to cite freely. **At the moment the work is complete, you must update the frontmatter's `last_updated` field to today's date (YYYY-MM-DD)** (a value identical to the existing one is a FAIL — to prevent content changes from being inconsistent with metadata).
7a. **self-VERIFY₀ (quantitative lint)** — confirm `python tools/lint.py contradiction <theme>` PASSes. On FAIL, fix the defect and rerun. After ≤ 2 self-attempts for the same reason, either PASS or force a handoff (SoT: [`agents/columnist.md`](../agents/columnist.md) self-VERIFY₀).
8. **Evaluate · iterate**: judge against the `.claude/layers/contradiction.md` Part 1 criteria → if it falls short, run the feedback loop.

#### Input material detail

1. **The relevant theme record in `_contradictions_themes.json`** — theme slug · name · claim_ids. **The SoT for which claims belong to this theme.**
2. **The claim records in `_contradictions.json`** — looked up by the claim_ids above. Each record's `source` · `claim` · `type` · `type_score` · `evidence_strength` fields are the raw material for the body narrative. Judge evidence priority along the two dimensions `type_score` (keyword match) + `evidence_strength` (Phase 2 metadata).
3. **The H2 sections of the source files the claims came from** — to secure original context, quotes, figures. Priority order: `## Summary` → `## Key Claims` → `## Connections` (the `contradicts:` line).
4. **The related cluster overview file(s)** — landscape-axis back-reference material. Provides the reader a drill-down back-route to which domain survey the theme belongs to.

#### Role division of the 4 EDITOR sections

| Section | Format | Responsibility | Tradition correspondence |
|------|------|------|----------|
| `## Opposing Positions` | 2–3 paragraphs of prose + A·B bold labels | Clearly declare Thesis·Antithesis + summarize each camp's actor, claim, and core grounds. Use a C label when a third viewpoint exists. | Hegel thesis-antithesis · WP:ASF |
| `## Representative Evidence` | **5–7 bullets (authoring target; the lint S2 band is 3–7, upper bound strict)** | Cross-present both camps' evidence as an **attribution triad** of `[[source-slug]]` + actor name + specific figure/quote. "Representative" means the minimal set of the most persuasive evidence, not a full evidence list — 8 or more becomes a reference list, diluting the weight of each item. No single-camp skew allowed. **Selection criterion**: top 5–6 by `evidence_strength` + 1 preserved historical-origin item (see "Score-based prioritization" in the authoring principles below). | Toulmin Data/Grounds · WP:DUE |
| `## Derived Tensions & Generational Readings` | 2–3 paragraphs or 2–5 bullets | Change over time (reflecting superseded) · differences in view by generation/camp · secondary issues · Qualifier (scope limitation) · acknowledged rebuttals | Toulmin Rebuttal/Qualifier · dialectic evolution |
| `## Interpretive Direction` | 1–2 paragraphs | The editor's hedged assessment + domain implications + future monitoring points. No flat verdicts; state scope explicitly ("in the short term," "on this metric"). | Synthesis · BBC Due Impartiality |

#### Per-paragraph layout of the 2–3 paragraphs in `## Opposing Positions` (recommended rule)

| Paragraph | Role | Length | Content |
|------|------|------|------|
| Paragraph 1 | Frame the issue | 2–4 sentences · **number tokens ≤ 4 · wikilinks ≤ 5** | Compress "who and what this issue pits against each other" into **one paragraph (2–4 sentences)** (do not compress into a single standalone sentence). First state the structure "A claims X, B claims Y." Inverted pyramid — if 6+ figures or 6+ wikilinks are densely packed, the paragraph loses its intended function (declaring the issue frame). Distribute overflow information to paragraph 2 (A·B juxtaposition) or to `## Representative Evidence`. (Corresponds to Rubric S3) |
| Paragraph 2 | A position + B position (juxtaposed) | 3–5 sentences each, or 2 bold labels | Juxtapose, one paragraph each, the key claim, lead actor, and core grounds per camp in the form `**Position A**: ...` / `**Position B**: ...`. Point-counterpoint convention. |
| (Optional) Paragraph 3 | Third viewpoint | **2–4 sentences strict + at most the word count of each A·B paragraph** | Only when a C mediator / exception viewpoint genuinely exists. Set off as a separate paragraph with a `**C — Mediation/Third view**:` label. **If C is longer than A·B, the reader misreads the convergence point as the main opposition** — undermining the identity of the `## Opposing Positions` section. If the issue is rich in C, move it to `## Derived Tensions & Generational Readings`. No forced insertion. |

#### Authoring principles (craft application + project procedure)

For the craft principles (NPOV · Toulmin · Hegelian dialectic · citation consistency · notation in the "Which writing tradition" mapping table above), the definitions, authoring criteria, and examples are owned by the relevant skill's `criteria.json` · SKILL.md as SoT. The No-verdict-first position · reappearance upper bounds (N4·N6) · type reflection · Korean headings · the 4 H2 sections live in the **structural · house-style sections** of the Rubric below. For the common principles on cadence (sentence length · paragraph separation), [overview.md "Common Authoring Principles"](overview.md#common-authoring-principles-applies-to-part-1-and-part-2) is the SoT.

Below are principles specific to **this wiki's data (`_contradictions.json` scores) and the frontmatter procedure** that do not reduce to craft or structural rules.

- **claim_ids coverage**: in the EDITOR body, **directly or indirectly restate** the claims in this theme's `claim_ids` from `_contradictions_themes.json` (at least half). Reconstruct the meaning, but reflecting none of the claims is a FAIL (the reader cannot verify why this is the theme).
- **Score-based prioritization (`type_score` · `evidence_strength`)**: the two scores in `_contradictions.json` are **orthogonal signals** — `type_score` (classification keyword match strength) · `evidence_strength` (Phase-2-metadata-based evidence strength, weighted by anchor 0.30 + recency 0.15 + share of primary sources 0.40 + hub type 0.15). They are the **primary decision tool** for prioritizing claim read-through, source selection, and body citation.

  | type_score \ evidence_strength | Low (≤0.3) | Medium (0.3–0.6) | High (≥0.6) |
  |---|---|---|---|
  | **High (≥0.6)** | weasel risk — weight the body weakly + accompany with a qualifier | standard evidence — candidate pool for `## Representative Evidence` | **strong evidence** — priority candidate for `## Representative Evidence`, suitable for a lead citation |
  | **Medium (0.3–0.6)** | drop review — exclude if replaceable | standard (where most claims fall) | reclassification review — weak classification signal but strong evidence |
  | **Low (≤0.3, mostly soft)** | **drop candidate** — avoid citing in the body | drop, or background context only | reclassification priority — worth a manual reclassification |

  Application: **Step 1 Select** = descending evidence_strength as primary + combined with a claim-text value judgment. **Step 2 Read** = top 5–6 + 1 preserved from the mid/old recency segment (historical origin). **Step 3 Cite** = for the lead and representative evidence, prioritize `type_score ≥ 0.6 + evidence_strength ≥ 0.5`; mark low `type_score` + high `evidence_strength` as a reclassification candidate in a reader-review note.
- **Source-selection 3-stage set relationship (Select → Read → Cite)**: execution-order steps 4·6·7 make the frontmatter the topmost set and Read · body cite subsets — `Claim-related sources ⊇ Frontmatter ⊇ {Read, Body cite}` (S2 evidence = Read ∩ Body cite · background context = Body cite − Read). The body ⊆ frontmatter consistency is enforced by `cit.cite-consistency`; the representative-evidence Read discipline (preventing narration that guesses from claim text · partial gaming is the editor's self-discipline) is enforced by the `cit.grounding` craft (skill SoT).
- **Citation anchor · recency (project application)**: the anchor format and the definition of anchorable sections (`#Summary` · `#Key Claims` · `#Key Quotes`) are owned by [`source.md` "Evidence anchor"](source.md) · `cit.anchor-evidence` as SoT. **The frontmatter `sources:` lists slugs only, without anchors** (protecting the graph dedup key); anchors are a body-wikilink notation matter only. recency is built into `evidence_strength` (weight 0.15), so no separate check is needed — `[Claims drift] top5_new` is consistently recency-primary.

#### Use of Phase 2 source-schema metadata (cit.grade-meta · cit.cite-type-meta)

The theme body narrative consciously reflects the evidence grade (`[fact]` Data / `[analysis]` Analysis / `[forecast]` Forecast), claimant, and citation type (`cites` / `references` / `contradicts` / `defines`) schema that source pages emit, adding attribution depth. The craft definition for this use is owned by [`scholarly-citation`](../skills/scholarly-citation/SKILL.md) "Use of schema metadata" as SoT. Caveats specific to this wiki's conflict axis:

- **No blanket camp demotion**: when absorbing grade asymmetry, do not flatly demote one camp as "second-tier analysis grade." Confirm via the actual sources whether the opposing camp also holds primary material before describing it — demoting only one camp is a bias that bypasses due weight.
- **State the absence of the A camp's voice**: if one side of the opposition (especially a frequently-cited big company) has no first-person self-defense voice within the source scope, do not fill in its position with narrator assertion. Instead state in the body that "this camp's official voice is absent from the source scope, and its position is reconstructed from the opposing/third-party voices" — blocking the paradox where the camp with the weakest attribution is described most assertively.
- **Dual claimant notation**: explicitly cite the `[[claimant]]` from a source's `## Key Claims` as the speaking actor in the body (`[[KISA]] released the first breach statistics ([[slug|source]])`) — making the claimant entity itself a wikilink to strengthen graph connectivity.
- **Natural absorption (block ritual compliance)**: do not expose schema vocabulary in the body as label prefixes or schema dumps (`[fact] [[claimant]] — `) for the sake of hitting a count. Introducing it once + 2–3 natural occurrences is the healthy pattern, and up to 2–3× the count threshold is normal; beyond that triggers Desk qualitative review. When the count is exceeded, the Desk separately judges the frequency of schema dumps from the frequency of evaluative-proposition absorption (if absorbed via the latter, it PASSes even when over the count).

#### `other-fragmentary.md` special case

`wiki/contradictions/other-fragmentary.md` is the residual-issue collection that does not converge into a theme. Unlike other themes it is an acceptance bucket **with no single axis of contention**, so the following adjustments are allowed:

- `## Opposing Positions` describes "what binds the residual claims together" (e.g. **groups by character** such as timeline updates · pending Soft judgments · individual single-entity cases)
- `## Representative Evidence` distributes representative sources per character group, **2–3 per group**
- `## Derived Tensions & Generational Readings` and `## Interpretive Direction` cover "why it did not converge into another theme" and "the follow-up refinement plan"
- In Rubric judgment, Part 1's A·B attribution balance (N2 DUE) is exempted (no axis of contention). The remaining criteria apply the same.

#### Feedback loop (iterate until the Rubric conditions are met)

Iterate and improve the theme file until it meets the completion conditions (roster `contradiction-theme.roster` — required 11 PASS + overall 26+/28 PASS; `other-fragmentary` exempts 4 criteria (N2·D5·D6·S3): -4 total / -1 required → 10 required + overall 22+/24 PASS). No limit on the number of iterations.

1. **Iteration 1 (draft)**: author the 4 H2 sections based on the input material (`_contradictions_themes.json` claim_ids + `_contradictions.json` records + Read of the core sources).
2. **Evaluation**: judge the automated (A) criteria via the `[Rubric]` line in the `python tools/lint.py contradiction <theme>` output, and the manual (M) criteria via body review as PASS/PARTIAL/FAIL.
3. **Completion judgment**: completion conditions met → done. Short → step 4.
4. **Iteration N+1 (reinforce)**: for each FAIL/PARTIAL criterion, the reinforcement criteria are owned by **the relevant craft skill's SKILL.md · criteria.json** (dotted IDs in the mapping table above) as SoT — take each criterion's PASS condition directly as the target. For structural · house-style (N3·N4·N6·D4·S1·S2·S3·X1), use the structural section of the Rubric below; for broken links (W4), use `python tools/lint.py graph structure`. When reinforcing, base the keep/remove decision on the `evidence_strength` criterion from "Score-based prioritization" above (S2 below the lower bound = add an un-cited high-ranked slug; N4·N6 reappearance = replace the lower-scored one).

**Safety guard**: once the required criteria PASS and only optional criteria remain, additional iterations are at the human reviewer's discretion. If the same criterion keeps FAILing twice in a row, re-examine the criterion itself (e.g. for a theme with fewer than 5 claims, achieving ≥3 evidence bullets is impossible — an intrinsic exception clause).

### Part 2 — Aggregate Contradictions Authoring Guide

**What this Part explains**: how to rewrite the `wiki/contradiction.md` file. This file is the **L2-4 conflict-axis global survey**, composed of a bottom-up roll-up of **N `wiki/contradictions/<theme>.md`** files (the current theme count is confirmed dynamically as the number of keys in `_contradictions_themes.json::themes`) plus a global tension-axis narrative. Its writing craft combines the Common Background "Which writing tradition" mapping-table skills (NPOV `enc.*` · Toulmin/Hegel `jrn.*`) + L2-4-specific craft (`con.mece-axes` · `enc.summary-style` · `enc.due-balance` · `enc.coatrack`).

#### Execution order (step-by-step guide)

1. **Read the current `contradiction.md`** — grasp existing content (the rewrite baseline · identify what to remove)
2. **Read the N theme files** — focused on each file's `## Opposing Positions` · `## Interpretive Direction` (the raw material for implications; N is determined dynamically as the number of keys in `_contradictions_themes.json::themes`). **When reading, check each file's `last_updated` + the recent PASS status of `python tools/lint.py contradiction <theme>` — on finding a FAIL or stale file, stop entering L2-4, fix that theme first, then re-enter** (scenario: rolling up the root over a stale theme propagates the wrong body content all the way to the root).
3. **Confirm `_contradictions_themes.json`** — theme slug · name · claim_ids distribution (preamble figures material)
4. **Confirm `_contradictions.json`** — total claim count · type distribution (real/superseded/related/soft counts — used in the "summary of recent update" preamble)
5. **Design the tension axes** — fix 2–4 global tension-axis names to fit the current theme distribution. Group themes under each axis. Axis re-naming is allowed (no obligation to keep the previous 3 axes).
6. **Rewrite** — rewrite the entire contradiction.md with the `Write` tool (no frontmatter, starting from the root heading `# Contradictions by Theme`). Preserve useful meta-insights from the existing "Implications" section but update them to fit the current theme distribution.
7. **Evaluate · iterate** — judge against `.claude/layers/contradiction.md` Part 2. Iterate if short.
7a. **self-VERIFY₀ (quantitative lint)** — confirm `python tools/lint.py contradiction aggregate` PASSes. After ≤ 2 self-attempts for the same reason, either PASS or force a handoff (SoT: [`agents/columnist.md`](../agents/columnist.md) self-VERIFY₀).
8. After the completion judgment, add a `## [YYYY-MM-DD] lint | contradictions aggregate rewrite` line to `log.md`.

#### Part 2 authoring principles

Part 1 craft applies directly at aggregate scale (the unit being the theme summary) — ASF attribution (`enc.npov-asf`) · even due weight (`enc.due-weight`, per-theme summary length) · Qualifier (`jrn.qualifier`, scope-limiting terms in implications) · slug alias (`enc.slug-alias`, no English exposure of theme links). The definitions and criteria are owned by the mapping-table skills above as SoT.

L2-4-specific principles (apply to Part 2 only):
- **Bottom-up roll-up + paragraph separation**: turn each theme file's `## Opposing Positions` · `## Interpretive Direction` into **1 paragraph of 3–5 short sentences per theme** (**1–2 paragraphs** also allowed when a theme is information-rich). contradiction.md holds not the details that overlap the child files but **the tension-axis narrative that sits above them**. Each sentence ≤ 200 characters · do not enumerate 5+ facts in one paragraph — split by meaning unit with periods or into additional paragraphs (same principle as overview.md's common-authoring "paragraph-separation principle"). Patterns like other-fragmentary that compress many fragment-issues into one paragraph should be split into a structured form such as **character-group bullets**.
- **Tension-axis grouping · naming**: group all themes into **2–4 global tension axes**, each axis a `### <axis name>` subsection header (MECE completeness `con.mece-axes` — every theme under at least one axis, residuals under `### Other`). The value-neutrality of the vocabulary on both sides of an axis name is governed by the `enc.label-neutral` craft as SoT — e.g. instead of `expectation vs evidence` (which privileges "evidence"), use `forecast vs measurement`. Axis re-naming and count adjustment are fluid as the theme distribution shifts.
- **Drill-down link**: at the head of each theme summary paragraph, provide the entry point to the child file in the form `[[<theme-slug>|<theme name>]]` (`enc.summary-style` — the WP `{{Main}}` convention).
- **Implications block**: place the meta-insights derived across all themes in the `## Implications` (Implications) section as **3–6 bullets** (each bullet a `**bold one-line conclusion**` + 2–4 sentences of elaboration). The **cross-theme observations** that cannot be derived from a single theme are the core of the editorial value. **Operational-meta separation principle**: do not mix **operational meta-information** such as classifier stability or signal-to-noise ratio into the domain-insight implications; instead separate it into its own H2 (e.g. `## Classification Stability Notes`) placed just before `## Source References`. If domain insight and operational meta coexist under the same label, the label's meaning blurs.
- **Implications entity attribution**: each `## Implications` bullet contains **at least one direct reference to a theme or entity**, and when a new entity first appears, narrate it continuing from the preceding-body context (overview · per-topic deep analysis). No inserting a judgment without a lead-in, like "Anthropic emerges as ~" — the meta-insight stays persuasive only if the underlying theme/entity is made explicit to the reader.
- **Implications prescription strength**: control `## Implications` bullet sentences with the 3-level strength (observation · recommendation · assertion) of the `enc.verdict-restraint` craft — if flat verdicts pile up beneath hedged expressions, you get the dual structure of formal NPOV + substantive bias (loose criterion FAIL ≤ 2).
- **Statistical-figure consistency**: when citing the same metric (claim count · type ratio · entity centrality, etc.) across the preamble · overview · implications · source references, **keep the same calculation basis and the same denominator**. When a denominator switch is needed (e.g. `real only` vs `real + superseded`), avoid misunderstanding by stating the context. This is a borderline issue often found in Desk qualitative review, so it is an L2-4-specific caution principle.
- **Preamble figure SoT**: take the total contradiction count and theme count from `wiki/contradictions/_contradictions.json` (count) and `_contradictions_themes.json` (theme count) as SoT. Any mismatch with either is subject to editor review.
- **No landscape-axis references**: do not use `[[<cluster-slug>]]`-form references. This file is conflict-axis only; the `wiki/index.md` exclusively handles landscape-axis entry points (.claude/layers/README.md). Same logic as Wikipedia:Coatrack — the nominal subject (the conflict survey) must not be obscured by the tangential subject (landscape).
- **The aggregate file has no frontmatter**: the root meta-file convention (.claude/layers/README.md (Root Meta Files Exception)) — start from the root heading `# Contradictions by Theme`. `last_updated` management is replaced by recording the re-aggregation event in `log.md`.

#### Use of Phase 2 source-schema metadata (cit.grade-meta · cit.cite-type-meta)

Apply the same craft as Part 1 ([`scholarly-citation`](../skills/scholarly-citation/SKILL.md) "Use of schema metadata" SoT) at aggregate scale. The **cross-theme meta-observations** that cannot be derived from a single theme — comparing per-axis evidence-grade distributions · attaching attribution strength to `## Implications` bullets · reflecting the distinction between cites/references — become possible with this added dimension. Part 1's conflict-axis caveats (no blanket camp demotion · state the absence of the A camp's voice · natural absorption) apply the same. In particular, **preserve drill-up attribution**: an absence of a camp's voice or an attribution asymmetry that a child theme MD explicitly handled is inherited in the aggregate summary too as a one-clause hedge (no narrator flattening into assertion).

#### L2-4-specific structure template

```markdown
# Contradictions by Theme

A Layer 2-4 conflict-axis global survey classifying the **N source-to-source contradictions** accumulated in the wiki into M topic clusters + other fragmentary oppositions. The deep analysis of each topic is in `wiki/contradictions/<topic>.md` (linked from this page); the raw individual-issue DB is `wiki/contradictions/_contradictions.json` (auto-generated; the classifier assigns `type` · `type_score` · `evidence_strength`). The drill-down entry point is [[index]].

**Summary of recent update** (YYYY-MM-DD): … (1–2 sentences on the type distribution · theme reorganization rationale)

## Synopsis

This wiki's contradictions converge into K **tension axes**.

**First, <axis 1 name>** — 2–4 sentences of commentary.

**Second, <axis 2 name>** — 2–4 sentences of commentary.

(axis count fluid 2–4)

---

## Per-Theme Deep Analysis (M + Other)

### <axis 1 name>

1. **[[<theme-slug>|<theme name>]]** (~N items) — 3–5 sentence summary. Concisely present the actors · core claims · representative evidence.
2. **[[<theme-slug>|<theme name>]]** (~N items) — …

### <axis 2 name>

3. **[[<theme-slug>|<theme name>]]** (~N items) — …

### Other

K. **[[other-fragmentary|Residual Fragmentary Issues]]** (~N items) — acceptance-bucket character summary.

## Implications

**① <one-line conclusion>** — 2–4 sentences of elaboration.

**② <one-line conclusion>** — …

(3–6 bullets)

## Source References

- Program-layer raw DB: `wiki/contradictions/_contradictions.json` (auto-generated; detail per source and per type)
- Per-topic deep dives: the `[[contradictions/<slug>]]` files in the list above, M+1 items
- Related trails · syntheses: … (link 1–2 trails/syntheses closely tied to conflict — do not include landscape cluster links)
```

#### Feedback loop

Same as L2-3 — iterate until the required Rubric criteria PASS. Confirm automated metrics via the `python tools/lint.py contradiction aggregate` output.

## Evaluation Rubric

This Rubric pairs with `.claude/layers/contradiction.md` defining "how to write" by providing the evaluation criteria that judge "how well it was written." Apply only the relevant Part depending on the scope of your work:

- **Part 1 — Theme Contradiction Rubric (L2-3)**: targets `wiki/contradictions/<theme>.md`. 28 criteria (`contradiction-theme.roster`).
- **Part 2 — Aggregate Contradictions Rubric (L2-4)**: targets `wiki/contradiction.md`. 19 criteria (`contradiction-aggregate.roster`) — Part 1 common craft + L2-4-specific (D1·D2·D3·F1·F2).

### Read Scope (by work scenario)

| Task | Required reading |
|------|---------|
| Evaluate · iterate a theme MD | This Rubric Part 1 |
| Evaluate aggregate `wiki/contradiction.md` | This Rubric Part 2 |
| Both evaluations together | All |

**Judgment method**:
- Each criterion is judged on the 3-level **PASS / PARTIAL / FAIL** (PARTIAL is excluded from the completion count — strict judgment).
- **Automated (A)** criteria are machine-verified via the `python tools/lint.py contradiction [<theme>]` output metrics; **manual (M)** criteria are judged via body review.
- The criterion roster · required · thresholds are in `_manifest.json` `contradiction-theme/aggregate.roster`; the definitions are owned single-SoT by the craft skill's `criteria.json` · SKILL.md (mapping-table dotted IDs) — since Part 1/Part 2 point at the same criterion, mirror duplication and drift monitoring are unnecessary.

---

### Part 1 — Theme Contradiction Evaluation Rubric

**Criteria SoT**: the theme evaluation criterion roster (applicable criteria · required) is `_manifest.json` `contradiction-theme.roster` (28 criteria); the definition · PASS condition · measurement of each craft criterion is owned by the "Which writing tradition" mapping-table skill's `criteria.json` · SKILL.md (NPOV `enc.*` · Toulmin/Hegel `jrn.*` · citation consistency `cit.*`). The structural · house-style criteria with no external craft original are in the section below.

#### structural · house-style criteria (not craft — owned solely by layers)

Structural and mechanical conventions with no external craft original. Measurement remains deterministic in `tools/_lint/contradiction.py` (S·X1·broken) · the `evaluate_contradiction_npov` bundle (N4·N6 reappearance); the definition is single here (no mirror).

| Dotted ID (legacy) | Criterion | PASS condition | Judgment | Required |
|---|---|---|---|---|
| `struct.verdict-position` (N3) | Avoid verdict-first | `## Interpretive Direction` is the 4th section and no editor's conclusion is inserted ahead of it in earlier sections | M | ✅ |
| `struct.schema-sections` (S1) | 4 H2 sections complete | `## Opposing Positions` · `## Representative Evidence` · `## Derived Tensions & Generational Readings` · `## Interpretive Direction` all 4 present + 0 `_TODO:` | A | ✅ |
| `struct.evidence-count` (S2) | Representative evidence 3–7 | 3–7 source-slug citations in `## Representative Evidence` + 3–7 unique slugs (exceeding the upper bound = reference-list-ification FAIL) | A | ✅ |
| `struct.lead-density` (S3) | Opposition lead density | first paragraph (the lead just before the A·B labels) figures ≤4 AND wikilinks ≤5 (inverted pyramid) | A |  |
| `struct.source-coverage` (X1) | source coverage | 70%+ of the unique sources derived from claim_ids appear in the body (denominator is the JSON SoT, deterministic) | A |  |
| `struct.type-reflection` (D4) | type distribution reflection | the claim type distribution (real/superseded/related/soft) matches the tone — emphasize the timeline if superseded is dominant, strengthen qualifiers if soft is dominant | M |  |
| `enc.broken-link` (W4) | real filenames | 0 broken wikilinks (`python tools/lint.py graph structure`) | A | ✅ |
| `house.source-repetition` (N4) | source slug reappearance ≤2 | source-slug reappearance ≤2 (introduce + deepen, 2 times standard). Entity/concept wikilinks excluded from the count | A (warning) |  |
| `house.figure-repetition` (N6) | figure-token reappearance ≤2 | no 3+ reappearance of the same figure token (a different measurement plane from N4 — the text surface). On reappearance in the derived-tensions position, advisory if no timeline/context-shift keyword is present | A (warning) |  |

**Completion conditions** (roster `contradiction-theme.roster` — 28 criteria):
- All 11 required (roster `required`: N1·N2·N3·T1·T3·T4·D2·S1·S2·W4·L2) PASS
- **26 or more PASS** of the 28 total (= total−2, computed by `_manifest_counts` · PARTIAL excluded from the count — strict)
- For advisory FAILs (structural · house-style · `cit.*` etc.), reinforce by referring to the relevant craft skill · structural-section criteria; if still short, return to a follow-up iteration
- **`other-fragmentary` exception**: due to the absence of a single axis of contention, 4 criteria — N2 (due weight) · D5 (C size) · D6 (C naming) · S3 (lead density) — are exempted (lint shows `—`). The completion condition is total −4 · required −1 (only N2 required) → **10 required + overall 22+/24 PASS** (computed by `_manifest_counts` `exclude_total=4 · exclude_required=1`)

**Evaluation execution order**:
1. Automated (A) criteria — judge immediately via the `[Rubric]` line of the `python tools/lint.py contradiction <theme>` output.
2. Manual (M) criteria (N1·N2·N3·T1·T3·D2·D4) — Claude or a human reviewer judges PASS/PARTIAL/FAIL while reading the body (criteria are in the mapping-table skill's SKILL.md · structural section).
3. If the required criteria fall short → return to the Authoring Guide feedback loop (Iteration N+1).

#### Interpreting the automated (A) metric output

The lint output is labeled with **legacy codes** (N4·N5·S2·X1·G1 etc.) for readability — the correspondence with the mapping-table dotted IDs is owned by the `legacy` field of each craft skill's `criteria.json` as SoT (e.g. N7=`enc.label-neutral` · T4=`jrn.qualifier` · L2=`cit.cite-consistency` · N4=`house.source-repetition` · S2=`struct.evidence-count`). Running `python tools/lint.py contradiction [<theme>]` prints **four lines** per theme file (split by dimension — the automated 20 criteria in a 4-line structure):

```
  contradictions/<theme>.md:
    [Rubric] S1=4/4 todo=0 ✅  S2 evidence=5 slugs=4 ✅  S3 lead nums=3/wiki=4 ✅  W1 links=38 ✅  D1 labels=2 ✅  D5 C=0/A=85/B=92 ✅  D6 C_meta=0 ✅
    [Rubric] N4 reuse_max=2 ✅  N5 verdict_fails=1 ✅  N6 num_reuse_max=2 ✅  N7 label_skew=0 ✅  T4 qualifiers=2 ✅
    [Rubric] X1 source_refs=5/8 (63%) ⚠️  X2 landscape=1 ✅  L1 raw_slugs=0 ✅  L2 cite_miss=0 ✅  L3 grounded=2/5 ✅
    [Rubric] G1 grade_meta=3 ✅  G2 cite_type_meta=1 ✅
```

If there is an upper-bound exceedance, a reappearing token, or a consistency violation, the following supplementary advisory lines are appended, one per line:

```
    [Rubric] N4 over-reused slugs: <source-slug>×N, <source-slug>×N
    [Rubric] N6 over-reused figures: "METR 19%"×4, "Llama 405B"×3
    [Rubric] N7 label value-words: A=[], B=[empirical evidence, skepticism]
    [Rubric] D6 C meta-critique keywords: [internal contradiction, self-serving]
    [Rubric] L1 raw slug samples: [...]
    [Rubric] L2 missing from frontmatter: [slug1, slug2]
    [Rubric] L3 missing evidence grounding: [slug1, slug2]
    [Rubric] G1 grade meta below threshold (need ≥2)
    [Rubric] G2 cite-type meta below threshold (need ≥1)
```

- **✅ = PASS**, **⚠️ = FAIL**, **— = exempt** (`other-fragmentary`'s N2·D5·D6·S3)
- Output token = threshold (each criterion's definition SoT is the mapping-table skill's `criteria.json` or the structural section above):
  - dialectic · NPOV craft → skill: `N5 verdict_fails ≤2` · `N7 label_skew ==0` · `T4 qualifiers ≥1` · `D1 labels ≥2` · `D5 C_words ≤ max(A,B)` · `D6 C_meta ==0`
  - citation · linking craft → skill: `W1 links ≥30` · `X2 landscape ≥1` · `L1 raw_slugs ==0` · `L2 cite_miss ==0` · `L3 grounded ≥1` · `G1 grade_meta ≥2` · `G2 cite_type_meta ≥1`
  - structural · house → structural section above: `S1 4/4 todo=0` · `S2 evidence/slug 3~7` · `S3 lead nums≤4 wiki≤5` · `X1 source_refs/total ≥0.7` · `N4 reuse_max ≤2` · `N6 num_reuse_max ≤2`
- Measurement nuance (skill `checks.py` · `tools/_lint/contradiction.py` is SoT): `N4` · `S2` are by source slug (entity/concept wikilinks excluded from the count) · the `X1` denominator is the JSON SoT (no editor gaming) · `L2` is the set difference claim source ∩ body − frontmatter (non-claim mentions excluded from the count) · `L3` blocks only the "0 Reads extreme" (partial gaming is the editor's self-discipline) · the figure vocabulary (`NUMBER_TOKEN_RE`) is owned by the skill `checks.py` (encyclopedia-writing) and consumed by contradiction.py, while the assertion/qualifier/camp-word dictionaries are owned by the skill `checks.py` (encyclopedia-writing · journalism-writing) as SoT.
- **W4** (required) is separate: 0 broken links in `python tools/lint.py graph structure`.

#### `[Freshness]` warning (advisory outside the Rubric)

Whether the Authoring Guide's "must update `last_updated` on completion" convention was followed is planned for future incorporation into `python tools/lint.py contradiction`, following the same pattern as overview. For now the path is a manual check:

```
git log -1 --format=%cs -- wiki/contradictions/<theme>.md
grep '^last_updated:' wiki/contradictions/<theme>.md
```

If the two dates diverge, the frontmatter `last_updated` update was missed. The reason this is not incorporated as a Rubric criterion is the same as for overview — it is **metadata hygiene**, not a quality evaluation, so it is kept as a separate advisory layer.

#### `[Claims drift]` warning (advisory outside the Rubric)

Because a theme MD is a pure editorial document with no AUTO block, overview's AUTO drift pattern cannot be applied directly. Instead an isomorphic version is introduced via **JSON-SoT-based drift** — comparing `_contradictions_themes.json[theme].claim_ids` + `_contradictions.json` records against the git HEAD version to compute three metrics:

- **`claim_jaccard`**: `|new ∩ old| / |new ∪ old|` (claim_id sets)
- **`source_delta`**: the rate of change in the size of the unique source set derived from claim_ids (in the output format `(srcs A→B)`, A·B are source file counts)
- **`top5_new`**: the number of new slugs in the top-5 of a **recency-primary** 3-level stable sort ((source date desc, claim count desc, slug asc)) that were not in the previous top-5. recency-primary is unified to mean "the latest editorially influential sources" — a new source can enter the top-5 on the date axis even if it comes in with a single claim

**Layer distinction (avoid confusion when interpreting)**: `claim_jaccard` is by **claim_id set**, while `source_delta` · `top5_new` are by **source file set**. The two layers cannot be summed or directly compared — since several claims are extracted from one source and one claim references exactly one source, generally claim count ≥ source count. Reading the `(srcs A→B)` figure in the drift report as a claim count produces a misdiagnosis, since it will not match the raw claim total (the number of records in `_contradictions.json`).

3-level thresholds (centrally managed as constants in `tools/_lint/contradiction.py`):

| Tier | Condition (any one) | Output |
|---|---|---|
| 🟢 stable | jaccard ≥ 0.85 · delta ≤ 15% · top5_new ≤ 1 | silent |
| 🟡 drift | middle range | `[Claims drift] ... 🟡 drift — representative evidence re-review recommended` |
| 🔴 rewrite | jaccard < 0.70 · delta > 30% · top5_new ≥ 4 | `[Claims drift] ... 🔴 rewrite — /wiki-lint contradiction <theme> --fix recommended` |

Why the top5_new threshold is tighter than overview's (1/4 vs 2/6): a theme has fewer sources than a cluster (roughly 5–20) — at the same relative-change ratio, the absolute count is small, so it must be more sensitive.

#### `[Claims staleness]` warning (orthogonal to drift)

Drift looks at "has it diverged from the baseline," but staleness looks at "is the baseline itself old." If the **most recent source date** among a theme's claim_ids is **180 days (6 months) or more in the past**, the advisory is printed — this theme has stopped receiving new material.

- Judgment: `today - max(source.date for claim in theme.claim_ids) > 180 days`
- Output: `[Claims staleness] newest_claim=YYYY-MM-DD (N days ago) ⚠️ — no new material in 6 months+`
- silent condition: the above condition not met, or the theme has no claims or date resolution fails

Why this is not incorporated as a Rubric criterion: it is **ingestion health**, not a quality evaluation — a theme may receive new claims following the flow of external events, or may be in a natural stable period. No effect on exit code.

#### `## Representative Evidence` recency-priority principle (linked to the Authoring Guide)

The Authoring Guide's "recency priority" convention (the "Citation anchor · recency" authoring principle above) and the `top5_new` metric share **the same recency axis**. When the editor selects the most recent among evidence candidates of equal relevance, the `top5_new` metric converges to a stable state — a design where convention compliance leads directly to lint stability.

But to prevent recency bias, at least 1 item from the mid/old segment of the full claim_ids date distribution is preserved in the evidence list (keeping historical-origin evidence). lint does not check this lower bound — it is the editor's judgment domain.

---

### Part 2 — Aggregate Contradictions Evaluation Rubric

**Criteria SoT**: the `wiki/contradiction.md` evaluation criterion roster is `_manifest.json` `contradiction-aggregate.roster` (19 criteria); the craft definitions · PASS conditions · measurement are owned by the "Which writing tradition" mapping-table skill's `criteria.json` · SKILL.md above. Part 1 common craft (`enc.npov-asf` · `enc.due-weight` · `enc.verdict-restraint` · `enc.label-neutral` · `jrn.toulmin-claim` · `jrn.qualifier` · `enc.link-density` · `cit.grade-meta` · `cit.cite-type-meta`) applies at aggregate scale (the unit being the theme summary), while the **L2-4-specific craft** is `con.mece-axes` (D1 tension-axis MECE) · `enc.summary-style` (D2 drill-down alias) · `enc.due-balance` (D3 per-axis balance ≤4:1) · `enc.coatrack` (F1 landscape blocking). structural is in the section below. Since Part 1/Part 2 point at the same criterion via the roster, mirror duplication and drift monitoring are unnecessary.

#### structural criteria (not craft — owned solely by layers)

| Dotted ID (legacy) | Criterion | PASS condition | Judgment | Required |
|---|---|---|---|---|
| `struct.verdict-position` (N3) | Avoid verdict-first | `## Implications` is positioned after `## Per-Theme Deep Analysis` | M | ✅ |
| `struct.schema-sections` (S1) | Required sections complete | `## Synopsis` · `## Per-Theme Deep Analysis` · `## Implications` · `## Source References` all 4 present | A | ✅ |
| `struct.insights-count` (S2) | Implications ≥3 | 3+ numbered bullets `**①` · `**②` under `## Implications` | A |  |
| `struct.theme-coverage` (X1) | theme coverage | every declared theme (including other-fragmentary) appears 1+ times as a `[[<slug>]]` or `[[<slug>\|<theme name>]]` wikilink (the lint accepts raw or aliased forms) | A | ✅ |
| `struct.headline-stats` (F2) | Preamble statistics match | "N source-to-source contradictions" = the number of records in `_contradictions.json`; "M topic clusters" = the number of non-`other-fragmentary` themes in `_contradictions_themes.json` | A | ✅ |
| `enc.broken-link` (W4) | real filenames | 0 broken wikilinks (`python tools/lint.py graph structure`) | A | ✅ |

**Completion conditions** (roster `contradiction-aggregate.roster` — 19 criteria):
- All 12 required (roster `required`: N1·N2·N3·T1·T4·S1·W4·X1·D1·D2·F1·F2) PASS
- **17 or more PASS** of the 19 total (= total−2, computed by `_manifest_counts`)
- D3 (`enc.due-balance`) is a warning — a FAIL judgment is accompanied by a human reviewer (natural skew in per-axis theme counts is possible)

**Evaluation execution order**: same as Part 1 — automated (A) via the `[Rubric L2-4]` line of the `python tools/lint.py contradiction aggregate` output, manual (M) via body review.

#### Interpreting the automated (A) metric output

Running `python tools/lint.py contradiction aggregate` prints each `wiki/contradiction.md` evaluation result in **four lines** (same hierarchy as the overview aggregate · 4-line structure — dimension split):

```
wiki/contradiction.md:
  [Rubric L2-4] T4 qualifiers=N ✅/⚠️  S1 sections=4/4 ✅  S2 insights=N ✅/⚠️  W1 links=N ✅/⚠️
  [Rubric L2-4] N5 verdict_fails=N ✅/⚠️  N7 axis_skew=N ✅/⚠️
  [Rubric L2-4] X1 theme_coverage=M/M ✅  D1 axes=N ✅/⚠️  D2 alias=N/N ✅  D3 balance=max/min=R ✅/⚠️  F1 cluster_refs=N ✅/⚠️  F2 stats=ok/drift ✅/⚠️
  [Rubric L2-4] G1 grade_meta=N ✅/⚠️  G2 cite_type_meta=N ✅/⚠️
```

- **✅ = PASS**, **⚠️ = FAIL** · output token = threshold (definition SoT is the mapping-table skill or the structural section above · **aggregate-scale thresholds**):
  - craft → skill: `N5 verdict_fails ≤2` (implications) · `N7 axis_skew ==0` (axis titles) · `T4 qualifiers ≥1` (implications) · `W1 links ≥50` · `D1 axes 2~4` (`### Other` excluded from the count) · `D2 alias N/N` (theme-reference pipe alias) · `D3 balance max/min ≤4` (warning) · `F1 cluster_refs ==0` · `G1 grade_meta ≥2` · `G2 cite_type_meta ≥1`
  - structural → section above: `S1 sections 4/4` · `S2 insights ≥3` · `X1 theme_coverage M/M` · `F2 stats ok` (preamble statistics)
- Reuses the same measurement dictionaries as Part 1 (assertion/camp-word/qualifier — skill `checks.py`). **W4** (required) is separate: 0 broken links in `graph structure`.

FAIL detail appears as supplementary advisory lines:

```
    [Rubric L2-4] X1 missing themes: [...]
    [Rubric L2-4] D2 un-aliased theme refs: [...]
    [Rubric L2-4] F1 cluster refs (forbidden): [...]
    [Rubric L2-4] F2 drift: ['claims declared=N actual=M', ...]
```

---

### Sources

The originals of the craft criteria are owned by each craft skill's SKILL.md `## Sources` as SoT — [`encyclopedia-writing`](../skills/encyclopedia-writing/SKILL.md) (WP NPOV · ASF · DUE · Balancing aspects · MoS Linking · Summary style · Coatrack — all enc.*) · [`journalism-writing`](../skills/journalism-writing/SKILL.md) (Toulmin · Hegel · BBC due impartiality — jrn.*) · [`consulting-writing`](../skills/consulting-writing/SKILL.md) (MECE — con.mece-axes) · [`scholarly-citation`](../skills/scholarly-citation/SKILL.md) (Xanadu · scite · APA — cit.*). structural · house-style have no external original (self-defined convention).
