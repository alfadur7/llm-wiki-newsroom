# L2-3 Cluster Overview + L2-4 Root Overview Guide

## Authoring

This guide specifies how to author the EDITOR block of landscape-axis overview files. There are two scopes; apply only the relevant Part depending on the task at hand:

- **Part 1 — Cluster Overview (L2-3)**: `wiki/overviews/<cluster>.md`, a single-cluster landscape file. Narrative coverage by subject area.
- **Part 2 — Root Overview (L2-4)**: `wiki/overview.md`, the global landscape file. A bottom-up roll-up of the **N cluster overviews** (the current cluster count is determined dynamically from the length of `graph/_clusters.json::clusters[]`) plus a cross-domain narrative.

**Read order within this guide**: whichever Part you work on, first read the three **common blocks** below (background, authoring principles, feedback loop) in full, then move to the relevant Part. The common blocks gather only what the two Parts share, avoiding repetition while preserving reproducibility.

Authoring iterates against the combined two Guides/Rubric as its basis. A Claude with no prior knowledge must be able to read this guide alone and reproduce the same quality.

### Read Scope (by task scenario)

When entering a task, first identify the single row matching your scenario and read only that row's four columns in full — CLAUDE.md section, this guide, Rubric, supporting guide. No additional reading beyond the table is required.

| Task | CLAUDE.md section | This guide | Rubric | Supporting procedure |
|------|---------------|----------|--------|------------|
| Author/update a cluster overview (`wiki/overviews/<cluster>.md`) | Roles · Universal Cycle · Human Reviewer Gate | Three common blocks + Part 1 | Part 1 | — |
| Rewrite the aggregate (`wiki/overview.md`) | Roles · Universal Cycle · Human Reviewer Gate | Three common blocks + Part 2 | Part 2 | — |
| Both tasks together | Union of the two rows above | Three common blocks + entire guide | Entire Rubric | — |
| Qualitative review cycle after Rubric PASS | Same as the relevant scenario | Same as the relevant scenario | Same as the relevant scenario | [`agents/desk.md` → 6-lens qualitative review](../agents/desk.md) |

### Common Background (applies to Part 1 and Part 2)

#### What writing traditions does this follow

The raw material of this wiki is news articles and consulting reports. The EDITOR block of overview pages takes the editorial conventions of these two fields as its reference, and **the definition, authoring principles, source texts, and qualitative/quantitative criteria of each technique are owned by the craft skill SKILL.md as SoT**. When entering authoring (Columnist) or review (Desk), explicitly read the relevant skill:

- [`journalism-writing`](../skills/journalism-writing/SKILL.md) — Lede · Nut graph · Kicker · PAGE · Explainer · inverted pyramid
- [`consulting-writing`](../skills/consulting-writing/SKILL.md) — SCR · So-what · Bold-bullet · numeric precision/density · MECE
- [`encyclopedia-writing`](../skills/encyclopedia-writing/SKILL.md) — link density · first mention · lead-body · NPOV restraint · slug alias · abbreviation glossing
- [`scholarly-citation`](../skills/scholarly-citation/SKILL.md) — leveraging evidence grade · citation type metadata

The table below **maps** each part of this wiki's overview pages to the craft criterion it corresponds to. References use **dotted IDs**; the technique definitions and authoring criteria are owned by each skill's `criteria.json` and SKILL.md as SoT (reproducibility).

| Wiki component | Corresponding craft criterion (dotted ID) |
|-----------|-----------|
| `## Overview` (Overview) 4 paragraphs | `jrn.lede` · `jrn.nutgraf` · `jrn.kicker` · `con.scr` · `con.so-what` |
| `## Overview` tension-axis declaration | `jrn.page` |
| `## Subtopics` (Subtopics) | `jrn.explainer` |
| `## Key Trends & Figures` (Key Trends & Figures) | `jrn.inverted-pyramid` · `con.bold-bullet` |
| Document-wide notation/neutrality | `enc.link-density` · `enc.first-mention` · `enc.lead-body` · `enc.verdict-restraint` · `enc.slug-alias` · `enc.abbr-gloss` |
| Numeric precision/density | `con.numeric-precision` · `con.numeric-density` |
| Leveraging schema metadata | `cit.grade-meta` · `cit.cite-type-meta` |
| (Part 2 additions) cluster completeness/drill/balance/scope | `con.mece-clusters` · `enc.summary-style` · `jrn.due-impartiality` · `enc.coatrack` |

For the genre framing of the overview file itself (Beat reporting · Forrester Landscape) and entity grouping (stakeholder map), see the `jrn`/`con` SKILL.md.

### Common Authoring Principles (applies to Part 1 and Part 2)

The definitions, criteria, and thresholds for craft principles (numeric precision/density → `con`; verdict restraint, abbreviation glossing, link density, first mention, lead-body, slug alias → `enc`) are owned as SoT by the craft skills' `criteria.json`/SKILL.md in the mapping table above. The following are this wiki's own **house-style/notation conventions** (mechanical rules with no external craft source text, plus project-application conventions for craft), applied in common to both Parts.

**house-style (mechanical rules — not craft, retained in layers)**:
- **`house.repetition`** (repetition of key figures/cases): a unique figure or case (e.g., "Llama 3.1's 405B parameters") appears ≤ 2 times across the whole document. A third occurrence in Part 2 is allowed only when it is a reinterpretation from a new angle of the cross-domain narrative (a simple re-citation violates the "connecting narrative"). Symmetric with contradiction N4.
- **`house.date-format`** (date notation): the house date format is YYYY-MM-DD or YYYY-MM only. Frontmatter and git metadata are exceptions. (Korean-style forms such as `YYYY년 M월` ["YYYY year M month"] or `YYYY 1~3월` ["YYYY Jan–Mar"] are flagged only under WIKI_LANG=ko.)
- **`house.sentence-length`** (sentence length): one sentence ≤ 200 characters, and **≤ 3 independent events** serialized (in English, with "and" or a serial comma/`·`; a single list-subject "A, B, and C did ~", counting as one event, is an exception). When exceeded, break with periods into units of 2–3 events. Character length is caught by S6, but event serialization is a semantic judgment and therefore the authoring/Desk domain. (The Korean connectives `~고`/`~며` are counted only under WIKI_LANG=ko.)
- **Paragraph separation (structural)**: each paragraph has 2–4 short sentences, no single-sentence standalone paragraphs (except a one-line section closer), composed of ≥ 2 paragraphs. The **anti-pattern** "one paragraph = one very long sentence" is the direct cause of simultaneous S6/R2/W2 advisory violations — after drafting, count the paragraphs and sentences in each section to self-verify, and when you identify a target for separation, also check the adjacent paragraphs (before and after) for the same pattern.
- **Numeric precision baseline**: the comparison baseline is, for Part 1, the relevant section of `wiki/overview.md`; for Part 2, the union of the cluster overviews' `## Key Trends & Figures` sections.

**Alias application convention** (`enc.slug-alias` craft as applied in this wiki — when a kebab-case filename is exposed, a pipe alias `[[FileName|DisplayName]]` is required, across concepts, clusters, and entities):
- **concept**: e.g., `[[OpenWeights|open weights]]` · `[[OpenWashing|open-washing]]` · `[[ModelLicensing|model licensing]]` · `[[OpenSourceAI|open-source AI]]`.
- **cluster**: SoT is `graph/_clusters.json::clusters[].name` (no hardcoding; dynamic reference). E.g., `[[open-weights|Open Weights]]`.
- **No alias needed**: industry abbreviations and global brands (`[[OSI]]` · `[[GPL]]` · `[[Meta]]` · `[[Mozilla]]`, etc.).
- **Product-name spacing**: `[[DeepSeekR1|DeepSeek R1]]` · `[[Llama3|Llama 3]]`, etc.
- **source slug**: a kebab-case slug of 10+ characters takes `[[slug|English summary alias]]`. Symmetric with contradiction L1.
- (Korean particle correction after adding an alias — 을/를 · 이/가 · 은/는 · 와/과 — applies only under WIKI_LANG=ko.)

### Common Feedback Loop (applies to Part 1 and Part 2)

Iterate and improve until the overview file meets the completion conditions (the mapping-table craft criteria + structural/house-style, manifest roster counts). There is no limit on the number of iterations. The lint command is, for Part 1, `python tools/lint.py overview <slug>`; for Part 2, `python tools/lint.py overview aggregate`.

1. **Iteration 1 (draft)**: write/rewrite the EDITOR block from the input material.
2. **Evaluation**: automatic (A) criteria are judged from the lint output `[Rubric]` line (for Part 2, `[Rubric L2-4]`); manual (M) criteria are judged PASS/PARTIAL/FAIL by reviewing the body.
3. **Completion judgment**: completion conditions met → done. Not met → step 4.
4. **Iteration N+1 (reinforcement)**: the reinforcement criteria for each FAIL/PARTIAL criterion are owned as SoT by **the relevant craft skill SKILL.md/criteria.json** (mapping-table dotted ID) — take each criterion's PASS condition as the direct target. For structural/house-style see the common authoring principles above; for broken links see `python tools/lint.py graph structure`.

**Safety valve**: once the required criteria PASS and only optional criteria remain, whether to add an iteration is the human reviewer's judgment. If the same criterion FAILs twice in a row and persists, re-examine the criterion itself (it may be unachievable given domain characteristics — e.g., the total link count of a small cluster with little data). Only in this exception is deferral to a follow-up cycle permitted.

### Part 1 — Cluster Overview Authoring Guide

**What this Part explains**: how to author the `wiki/overviews/<cluster>.md` file. This file is the **overview page for a particular cluster (topic grouping)**, unfolding the entire field into a single document. For example, `open-weights.md` covers the "open weights" field.

#### The file's dual structure — AUTO block + EDITOR block

Each overview file mixes two regions:

- **AUTO block**: a region wrapped in markers such as `<!-- AUTO:MEMBERS BEGIN -->`. A Python script (`python tools/build.py clusters`) generates and updates it automatically, and humans do not edit it directly. It mainly contains the top list of entities/concepts belonging to the cluster and a list of key sources.
- **EDITOR block**: every region outside the AUTO markers. Narrative content authored directly by a human (or Claude). This Part explains how to author the six EDITOR-block sections at a consistent quality.

#### Execution order (step-by-step guide)

The concrete procedure a Claude performing this task for the first time should follow. Each step's output becomes the next step's input.

1. **Identify the target cluster**: read `graph/_clusters.json` to confirm the slug/name of the target cluster. The full cluster list and current count are confirmed dynamically from the SoT `_clusters.json::clusters[]` — the guide does not hardcode the roster (renames/additions/removals happen frequently here, so this avoids a stale trap).
2. **Confirm file existence**: if `wiki/overviews/<slug>.md` does not exist, first auto-generate a skeleton with `python tools/lint.py overview --fix`. This command creates a missing file from the Cluster Overview Format template for every cluster slug in `_clusters.json` and inserts the AUTO markers.
3. **Map the baseline section**: read `wiki/overview.md` and identify the numbered section (`## N. ...`) that best fits at the time of writing. **Mapping rule**: using the target cluster's name (`_clusters.json::clusters[].name`) as a keyword, search the `## N. <cluster name>` headings in `wiki/overview.md` and pick the closest in meaning. 1:N mapping (one cluster spanning several sections) is allowed. This guide does not hardcode a static cluster→section mapping — `wiki/overview.md` is itself a product rewritten as the cluster taxonomy changes, so the mapping itself varies over time.
4. **Locate the AUTO block**: open the target `wiki/overviews/<slug>.md` with the `Read` tool and confirm the positions of the `<!-- AUTO:MEMBERS BEGIN -->` and `<!-- AUTO:SOURCES BEGIN -->` markers. **Never edit lines inside this block** (they are auto-regenerated when `python tools/build.py clusters` runs, and manual edits are overwritten on the next build).
5. **Identify related theme files**: among `wiki/contradictions/*.md`, select themes whose keywords overlap with the cluster slug/name. The full theme list/count is confirmed dynamically from the SoT `wiki/contradictions/_contradictions_themes.json::themes` keys. **Mapping rule**: a theme file is a candidate if its stem or frontmatter `title:` overlaps in meaning with the cluster name's keyword. 1:N mapping (one cluster referencing several themes + one theme spanning several clusters) is allowed. This guide does not hardcode a static cluster→theme mapping — the theme taxonomy is often reorganized in the `_contradictions_themes.json` Phase 2 re-derivation, so this avoids a stale trap.
6. **Gather input material**: read the above four kinds (the overview.md section, the file's AUTO-block content, the top 20–40 entries of `wiki/sources/_catalog-<slug>.md`, the related theme files) to secure the raw authoring material.
7. **Author the EDITOR sections**: with the `Edit` tool, replace each EDITOR section's `_TODO: ...` placeholder with actual content. Do not change the AUTO marker lines (`<!-- AUTO:... -->`), and do not touch the lists inside them. For how to author the six sections, see "Six EDITOR section role split" + "Part 1 specific principles" below (common principles are in the "Common Authoring Principles" block above). **At the moment the work completes, you must update the frontmatter `last_updated` field to today's date (YYYY-MM-DD)** (if it equals the previous value, this is judged FAIL not PASS — to prevent a mismatch between content edits and metadata). The `[Freshness]` warning of `python tools/lint.py overview` automatically detects this omission.
7a. **self-VERIFY₀ (quantitative lint)** — confirm `python tools/lint.py overview <slug>` PASS. On FAIL, fix the defects and rerun. After ≤ 2 self-attempts for the same cause, either PASS or forced handoff (SoT: [`agents/columnist.md`](../agents/columnist.md) self-VERIFY₀).
8. **Evaluate/iterate**: per the common feedback loop, judge against Rubric Part 1 → iterate if not met.

#### Input material detail

1. **The relevant field section of `wiki/overview.md`** — the wiki-wide roll-up file, which already has an edited, high-quality summary. Take it as the **baseline** for quality/scope.
2. **The target overview file's `AUTO:MEMBERS` block** — an auto-selected top list of entities/concepts. The starting point for meaningful grouping; the ranking is "top N by in-cluster connections" (based on how often it is referenced within that cluster).
3. **The top 20–40 entries of `wiki/sources/_catalog-<cluster>.md`** — the source catalog belonging to the cluster. The raw material for finding concrete figures, project names, and recent cases.
4. **Related `wiki/contradictions/<theme>.md` files** — analysis documents that separately organize the tensions/oppositions of this field. Reference material for the tension-axis narrative and a deep-link target.

#### Six EDITOR section role split

| Section | Format | Responsibility | Corresponding craft (dotted ID) |
|------|------|------|----------|
| `## Overview` | exactly 4 prose paragraphs | field definition · scale · driving background · **tension-axis declaration** (2–3 branches) | `jrn.lede` · `jrn.nutgraf` · `jrn.kicker` · `con.scr` |
| `## Recent Changes` | 3–5 bullets (reverse chronological) | a **timeliness channel** that surfaces new events of the last ~3 months with explicit dates, newest on top | structural (live-blog "what we know so far") |
| `## Key Entities & Concepts` | 5–6 semantic groups | rearrange the names from AUTO:MEMBERS into groups such as actors/partners/concepts + annotate each role | `jrn` stakeholder map |
| `## Subtopics` | 6–8 topics, mixing paragraphs and bullets | 3–4 as paragraph narrative (the core tension axes dissolved in), the rest as bullets | `jrn.explainer` |
| `## Key Trends & Figures` | 3–4 subsections (minimum 3), each a `**Bold title**` + bullets | **Investment scale** / **Timeline** / **AI & new-tech adoption figures** / **Recent cases** recommended (flexibly changeable). A reference-table character. | `jrn.inverted-pyramid` · `con.bold-bullet` |
| `## Adjacent Domains & Scope` | 2–4 bullets | a `[[<slug>]]` reference to an adjacent cluster overview + a one-line description of each boundary | structural (Leiden boundary correspondence) |

#### Paragraph-by-paragraph layout of the `## Overview` 4 paragraphs (strict rules)

| Paragraph | Role | Length | Content |
|------|------|------|------|
| Para 1 | Lede | 2–4 sentences | Open the field with concrete figures, proper nouns, project names. "So what upfront" — present the field's core conclusion compressed **across 2–4 sentences** (no single-sentence compression). No abstract summary. |
| Para 2 | Nut graph (first half) | 3–6 sentences | Of the 4W1H, narrate scope/timing/actors/reason in earnest. The "heart of the story" in one paragraph. |
| Para 3 | Nut graph (second half) / Body | 3–6 sentences | Explain background, driving motivation, core challenges. An expansion of Para 2. |
| Para 4 | Kicker / Resolution | 3–5 sentences | Declare the 2–3 tension-axis branches. Name the axes in the form "innovation vs stability" · "A vs B" + summarize both camps of each axis. A forward-looking close. |

#### `## Recent Changes` authoring rules

This is the timeliness channel positioned right after `## Overview`. The evergreen body (the remaining sections) keeps a topical, timeless narrative, and recent events are surfaced with dates only in this section — structurally blocking the problem of recent news getting buried among older events.

- **Format**: 3–5 bullets, reverse chronological (newest on top). Each bullet starts with `YYYY-MM[-DD]` + a one-line summary + one key hub `[[wikilink]]`.
- **Scope**: new events of the last ~3 months. If there are no events within the window, give the 1–2 most recent changes + state "stable period since."
- **Link restraint**: ≤ 1–2 wikilinks per bullet (preserving the `## Overview` lead's density advantage — W2). Overlap with other body sections is fine (a W3-exempt section).
- **Freshness**: when the newest item exceeds 90 days, the `[Recency]` advisory recommends an update.

#### Part 1 specific principles

Along with the common authoring principles (block above), the following items apply only to Part 1:

- **AUTO block no-edit principle**: do not change the `<!-- AUTO:... BEGIN/END -->` markers or the lines inside them with any tool, `Edit` or `Write`. This block is auto-regenerated by `clusters.run_pages()` when `python tools/build.py clusters` runs, so manual edits are overwritten and lost on the next build. When authoring EDITOR sections, replace only the region outside the AUTO markers, and to prevent mistakes take care that the AUTO marker lines are not included in `Edit`'s `old_string`/`new_string`.
- **Adherence to the 4-paragraph Overview form**: the role/length/content of each of the 4 paragraphs is owned by the [Paragraph-by-paragraph layout of the `## Overview` 4 paragraphs (strict rules)] table above as SoT. This principle is a declaration of the obligation to follow the table, enforcing the ban on single-sentence compression of Para 1 and on paragraph consolidation.
- **Narrate the tension axes with PAGE framing** (`jrn.page`): narrate the 2–3 tension-axis branches of the Overview's last paragraph using at least 2 of the 4 PAGE elements (criteria from jrn SKILL.md). In 2–3 of the subtopics, cross-reference the related `wiki/contradictions/<theme>.md` as `[[theme-slug]]` to provide a drill-down path (this-wiki application).
- **Role separation of the AUTO block and the EDITOR block**: AUTO:MEMBERS is a list produced by mechanical ranking (by connection count). The EDITOR's role is **semantic grouping, role annotation, and context**. In the EDITOR, do not simply repeat the AUTO content; add groups, relationships, and narrative.
- **Paragraph↔bullet rhythm**: `## Overview` is all paragraph prose. `## Key Trends & Figures` is all bullets (`jrn.inverted-pyramid`). `## Subtopics` is **mixed roughly 5:5** — topics with a core tension axis dissolved in get paragraph narrative, peripheral topics get bullets.
- **Bold-bullet structure of `## Key Trends & Figures`** (`con.bold-bullet`): each subsection is a pair of a **bold subheading (key claim)** + **bullets (supporting data)** (criteria from con SKILL.md). E.g., `**Open-weight model releases**` followed by `- Meta Llama 3.1: 405B-parameter weights released under a community license — ...`.
- **Explicit adjacent fields and scope**: clusters auto-grouped by the Leiden clustering algorithm do not have cleanly cut topic boundaries, so make the scope distinction from adjacent clusters explicit in a `## Adjacent Domains & Scope` subsection. The content is 2–4 bullets, each a `[[<adjacent-cluster-slug>|<cluster name>]]`-format wikilink (the alias principle is in the common block, e.g., `[[open-weights|Open Weights]]` covers the release model · `[[licensing-open-washing|Licensing & Open-Washing]]` covers license terms) + a one-line description of the boundary with that field's content. This section includes only references to adjacent overviews within the landscape axis — conflict-axis theme links (per X2) are placed separately in the body such as `## Overview`/`## Subtopics`. `python tools/lint.py overview` automatically detects alias-less cluster-slug links in this section.
- **Leveraging paired_exempt + semantic branching of anchor invasion**: the `paired_with` field in `graph/cluster_labels.json` defines an essential coupling between clusters, and the lint anchor-invasion advisory computes a paired-exempt count separately (e.g., `[paired-exempt: 3 refs — licensing-open-washing(3)]`). paired-exempt is an essential coupling, so it is not a target for narrative-separation treatment. If invasion beyond paired-exempt is found, branch semantically in the following two directions — **(i) Integrate**: if the invading anchor touches this cluster's essence, naturally integrate it within the narrative (keep the first-mention wikilink, annotate the role); **(ii) Demote**: if it is outside this cluster's essence, demote to plain text or weaken to a single cross-reference word, and guide the narrative's main body to the adjacent cluster overview. The integrate-vs-demote decision must be consistent with the cluster's identity definition (the `## Overview` paragraph), and a cross-reference meta-note like "the main narrative is the [[<adjacent-cluster-slug>|<Name>]] cluster; this cluster covers only the ... aspect" is the standard pattern when demoting. This branching judgment is the Desk's qualitative-review domain, not a target for automatic lint exemption (false-negative risk).

#### Leveraging source schema metadata (`cit.grade-meta` · `cit.cite-type-meta`)

The cluster overview narrative consciously reflects the evidence-grade (`[fact]` ["source/primary"] · `[analysis]` ["analysis"] · `[forecast]` ["forecast"]) and citation-type (`cites:` · `references:` · `contradicts:` · `defines:`) schema emitted by source pages — adding depth by meta-mentioning the evidence-base grade, the dominant claimant, and the cites-vs-references distinction. The authoring/measurement criteria are owned by [`scholarly-citation`](../skills/scholarly-citation/SKILL.md) as SoT. Keep attribution limited to factual statements, consistent with `enc.verdict-restraint` (verdict restraint).

Evaluation/iteration follows the [`### Common Feedback Loop`](#common-feedback-loop-applies-to-part-1-and-part-2) above (Part 1 lint = `python tools/lint.py overview <slug>`, including the `[Freshness]` warning).

### Part 2 — Root Overview Authoring Guide

**What this Part explains**: how to rewrite the `wiki/overview.md` file. This file is the **L2-4 landscape-axis global overview**, composed of a bottom-up roll-up of the **N `wiki/overviews/<cluster>.md`** files (the current cluster count is determined dynamically from the length of `graph/_clusters.json::clusters[]`) plus a cross-domain narrative.

#### Execution order (step-by-step guide)

1. **Read the current `overview.md`** — understand existing content (identify the rewrite baseline and removal targets)
2. **Read all N cluster overviews** — focusing on each file's `## Overview` 4 paragraphs · `## Key Trends & Figures` · `## Adjacent Domains & Scope` (the target N is determined dynamically from `_clusters.json::clusters[]`). **When reading, check each file's `last_updated` + the recent PASS status of `python tools/lint.py overview <slug>` — if you find a FAIL or stale file, halt the L2-4 entry, treat that L2-3 first, then re-enter** (scenario: rolling up the root on top of a stale L2-3 propagates wrong content all the way to the root).
3. **Check `wiki/index.md` statistics** — the material for the lead's numbers
4. **Check `graph/_clusters.json`** — each cluster's `name` (display alias) · `size` (scale)
5. **Design the structure** — fix the order of the N cluster sections, select 2–3 cross-domain narrative topics. Pre-sketch each cluster section as a 4-beat (branch point · main body · tension axis · drill-down) paragraph structure, and each cross-narrative as a 2–4 paragraph structure.
6. **Rewrite** — rewrite the entire overview.md with the `Write` tool (no frontmatter, starting from the root heading `# Overview`). Apply both the common authoring principles (block above) + the Part 2 specific principles below. **Do not interpret this as "compress each cluster section into one paragraph"** — separate the 4 beats into distinct paragraphs, with each paragraph ≤ 4 sentences and each sentence ≤ 200 characters (see the common authoring principles "paragraph-separation principle" / "sentence-length cap"). Place a `## Recent Changes` section right after the lead (see Part 2 specific principles below).
7. **Evaluate/iterate** — per the common feedback loop, judge against Rubric Part 2. Iterate if not met. **Self-verification obligation**: after the first draft, run `python tools/lint.py overview aggregate`, and if even one of the advisories (S6 long_sents · R2 dense_paras · W2 lead-body) is ⚠️, re-read the body, separate the paragraphs, then re-diagnose.
7a. **self-VERIFY₀ (quantitative lint)** — confirm `python tools/lint.py overview aggregate` PASS. After ≤ 2 self-attempts for the same cause, either PASS or forced handoff (SoT: [`agents/columnist.md`](../agents/columnist.md) self-VERIFY₀).
8. End after the completion judgment. Since there is no frontmatter, the `last_updated` update is skipped, but record the re-roll-up event in `log.md`.

#### Part 2 specific principles

Along with the common authoring principles (block above), the following items apply only to Part 2:

- **`## Recent Changes` (right after the lead)**: a timeliness channel that surfaces the core events of the last ~3 months across all clusters in 5–7 bullets, reverse chronological (newest on top). Each bullet `YYYY-MM[-DD]` + one line + one hub `[[wikilink]]`. Separate it from the timeless connecting narrative of the cluster sections so recent events are not buried. Theme links forbidden (F1); `[Recency]` advisory when over 90 days. The cluster sections below maintain the following 4-beat.
- **Bottom-up roll-up + 4-beat paragraph structure**: each cluster section restates the lower files' `## Overview` + `## Key Trends & Figures` in **3–4 paragraphs**, separating the following 4 beats into distinct paragraphs — **(1) Branch point**: the core event/figure/timing that defined the cluster, in one paragraph. **(2) Main body**: the core entities, camps, and anchor concepts, in one paragraph. **(3) Tension axis**: the head-on colliding camps or the core contradiction, in one paragraph. **(4) Drill-down**: close with `Details: [[<slug>|<Name>]]` (may be appended to the end of the preceding paragraph). overview.md holds the **connecting narrative laid on top**, not details that duplicate the lower files, but the "compress the whole cluster into one paragraph" pattern is forbidden (see the common authoring principles "paragraph-separation principle").
- **Drill-down link**: at the end of each cluster section, provide an entry point to the lower file in the form `Details: [[<slug>|<cluster name>]]` — the Wikipedia `{{Main}}` template convention.
- **Cross-domain narrative**: organize 2–3 macro topics that cut across multiple clusters into separate subsections. The connecting topics not absorbable into a single cluster section are the heart of editorial value.
- **Conflict-axis reference ban**: do not use `[[<theme>]]`-format references. This file is landscape-axis only; the conflict-axis entry point is the sole responsibility of `wiki/index.md` (.claude/layers/README.md). The same logic as Wikipedia:Coatrack — the nominal subject (the landscape overview) must not be obscured by a tangential subject (the conflict axis).
- **No implementation terms (reader-facing)**: the root is the wiki's top-level entry point, the first screen a reader with no prior knowledge sees. Do not expose the clustering mechanism (cold partition · anchor · re-condensation), internal file/field names (cluster_labels.json · paired_with), graph edge types (cites/references/contradicts), or internal axis names (conflict/landscape axis) in the EDITOR prose. Render field reorganization plainly without the mechanism, and gloss an abbreviation once at first mention (reader-organizing vocabulary such as "grouping" / "field" is allowed).
- **Cluster section order**: topic-flow driven (maintain domain adjacency such as definition · weights · licensing). Sorting by the `size` in `_clusters.json` is not required.
- **Lead figure SoT**: scale statistics (counts of sources · entities · concepts · overview · synthesis · trail · timeline) take the values in `wiki/index.md` as SoT. If a discrepancy is found across `graph/_clusters.json`/the sources catalog, it is a target for editor review.

#### Leveraging source schema metadata (`cit.grade-meta` · `cit.cite-type-meta`)

Apply Part 1's schema-metadata leverage at aggregate scale — meta-mention not at the cluster unit but the **whole-wiki evidence-base strength/attribution anchor** in the lead/cross-domain narrative (e.g., a particular hub being the dominant claimant across several clusters). Place it in the EDITOR region outside the AUTO:STATS block. The authoring/measurement criteria are owned by [`scholarly-citation`](../skills/scholarly-citation/SKILL.md) as SoT.

Evaluation/iteration follows the [`### Common Feedback Loop`](#common-feedback-loop-applies-to-part-1-and-part-2) above (Part 2 lint = `python tools/lint.py overview aggregate`). Part 2 specific craft reinforcement keys: `con.mece-clusters` (cluster completeness) · `enc.summary-style` (drill-down) · `jrn.due-impartiality` (cross-cluster balance) · `enc.coatrack` (theme-axis blocking). With no frontmatter, the `[Freshness]` warning does not apply — after editing, record the re-roll-up event in `log.md`.

## Evaluation Rubric

This Rubric pairs with `.claude/layers/overview.md` defining "how to write," providing the evaluation criteria that judge "how well it was written." Apply only the relevant Part depending on the task scope:

- **Part 1 — Cluster Overview Rubric (L2-3)**: targets `wiki/overviews/<cluster>.md`. 30 criteria (`overview-cluster.roster`).
- **Part 2 — Root Overview Rubric (L2-4)**: targets `wiki/overview.md`. 29 criteria (`overview-aggregate.roster`) — Part 1 common + L2-4 specific craft (D1 · D2 · D3 · F1).

**Judgment method**:
- Each criterion is judged in 3 levels, **PASS / PARTIAL / FAIL** (PARTIAL is excluded from the completion count — strict judgment).
- **Automatic (A)** criteria are machine-verified by metrics output when `python tools/lint.py overview` runs.
- **Manual (M)** criteria are judged by Claude or a human reviewer reading the body.
- The criterion roster/required/threshold are owned by `_manifest.json` `overview-cluster/aggregate.roster`, and the definitions by the craft skill `criteria.json`/SKILL.md (mapping-table dotted ID) as the single SoT — since Part 1/Part 2 point at the same criterion, mirror duplication and drift monitoring are unnecessary.

### Read Scope (by task scenario)

| Task | Required Read |
|------|---------|
| Evaluate/iterate a cluster overview | This Rubric Part 1 |
| Evaluate the aggregate `wiki/overview.md` | This Rubric Part 2 |
| Both evaluations together | Entire Rubric |

### Part 1 — Cluster Overview Evaluation Rubric

**Criteria SoT**: the cluster-overview evaluation criterion roster (applied criteria, required status) is owned by `_manifest.json`'s `overview-cluster.roster`; the definition/PASS-condition/measurement of each craft criterion by the owning skill's `criteria.json`/SKILL.md (the "what writing traditions" mapping-table dotted ID above). The structural/house-style with no external craft source text are in the section below.

#### structural/house-style criteria (not craft — solely held in layers)

Structural and mechanical rules with no external craft source text. Measurement is retained deterministically in `tools/_lint/overview.py`, and the definitions are held solely here (no mirror) — they are placed in layers because they are coupled to this wiki's page format.

| Dotted ID (legacy) | Criterion | PASS condition | Judgment | Required |
|---|---|---|---|---|
| `struct.scope-match` (S1) | Scope match | Covers + extends all items the relevant section of `wiki/overview.md` covers | M | ✅ |
| `struct.cross-tension` (X1) | Tension-axis cross | Each tension axis declared in the Overview reappears in ≥ 2 subtopics | M | ✅ |
| `struct.auto-editor` (X3) | AUTO-EDITOR separation | `## Key Entities & Concepts` is grouping/role annotation, not a plain copy of AUTO:MEMBERS | M | ✅ |
| `enc.broken-link` (W4) | Real filenames | 0 broken wikilinks (`python tools/lint.py graph structure`) | A | ✅ |
| `struct.theme-drilldown` (X2) | Contradiction drill-down link | A `[[<theme>]]`-format `wiki/contradictions/<theme>.md` reference is inserted in the body | A |  |
| `struct.prose-rhythm` (S3) | Narrative/bullet rhythm | Roughly half the subtopics are paragraph narrative, the rest bullets | M |  |
| `struct.prose-min` (S4) | Paragraph narrative ≥ 2 | 2+ subtopics are in paragraph form | A |  |
| `struct.subsection-min` (S5) | Trends·figures ≥ 3 subsections | `## Key Trends & Figures` has ≥ 3 `**Bold**` subsections | A |  |
| `house.repetition` (R1) | Repetition of key figures/cases | A unique figure/unit token appears ≤ 2 times across the document (a 3rd occurrence only for a new cross-angle) | A (warning) |  |
| `house.date-format` (L2) | Date notation unified | Mixed forms other than YYYY-MM-DD/YYYY-MM ≤ 3 | A (warning) |  |
| `house.sentence-length` (S6) | Sentence-length cap | One sentence ≤ 200 characters, ≤ 3 exceedances | A (warning) |  |

**Completion conditions** (criterion roster/required are owned by `_manifest.json` `overview-cluster.roster` — currently 30 criteria):
- All 11 required (roster `required`) PASS
- **≥ 28 of all 30 PASS** (= total−2, computed from the roster · PARTIAL excluded from the count — strict)
- For advisory (structural/house-style/`cit.*` etc.) FAILs, reinforce by reference to the relevant craft skill/structural-section criteria; if unmet, return to a follow-up iteration
- The `python tools/lint.py overview <slug>` rewrite block computes the completion-condition string from the roster (`_manifest_counts`)

**Evaluation execution order**:
1. Automatic (A) criteria — judge immediately from the `[Rubric]` line of `python tools/lint.py overview` output.
2. Manual (M) criteria — Claude/a human reviewer reads the body and judges PASS/PARTIAL/FAIL (criteria from the mapping-table skill SKILL.md).
3. If required criteria are unmet → return to the Authoring Guide feedback loop (Iteration N+1).

#### Interpreting the automatic (A) metric output

The lint output is notated for readability with **legacy codes** (W1 · W2 · W3 · X2 · G1 · G2 etc.) — the correspondence with the mapping-table dotted IDs is owned by the `legacy` field of each craft skill's `criteria.json` as SoT (e.g., W1=`enc.link-density` · G1=`cit.grade-meta` · X2=`struct.theme-drilldown`). When `python tools/lint.py overview` runs, the following one-line format is output for each overview file:

```
  overviews/<slug>.md:
    [Rubric] W1 links=119 (≥150) ⚠️  W2 lead/body=5.5/6.93 ratio=0.79 ⚠️  W3 dup=15 ⚠️  X2 contradiction_refs=4 ✅
    [Rubric] G1 grade_meta=0 ⚠️  G2 cite_type_meta=0 ⚠️
```
(The R1 · R2 · B1 · L1 · L2 · L3 · S6 advisory lines are omitted in this excerpt — the full set of lines is owned by `tools/_lint/overview.py` as SoT)

- **✅ = PASS** (criterion met), **⚠️ = FAIL** (criterion unmet, an iteration target)
- PASS condition per metric:
  - **W1**: `links` value **≥ 150** (count of wikilinks in the EDITOR region, excluding the AUTO block)
  - **W2**: `ratio` **≥ 1.0** (`## Overview` per-paragraph link density ≥ the body sections' average)
  - **W3**: `dup == 0` — duplicate wikilinks of the same term within a section must be 0 to PASS (`_W3_THRESHOLD` = manifest `enc.first-mention` threshold = 0; even 1 means FAIL). The `## Adjacent Domains & Scope` section is excluded from the count because its structure cites each adjacent cluster twice in the form `[[slug|Display Name]]` + boundary description.
  - **X2**: `contradiction_refs ≥ 1` — count of `[[<theme>]]`-format references
  - **G1**: `grade_meta ≥ 2` — number of evidence-grade/attribution meta-expressions appearing in the EDITOR region. The lint matches the English tokens `[fact]` · `[analysis]` · `[forecast]`, `attribution`, `grade A/B/C`, and `evidence grade`. (Korean/ko-mode meta-phrases — `1차 fact`, `발화 주체`, `fact급`/`analysis급`/`forecast급`, `증거 등급` — are dormant on the English corpus.)
  - **G2**: `cite_type_meta ≥ 1` — number of citation-type meta-expressions appearing in the EDITOR region. The lint matches the English citation-type literals `cites:` · `references:` · `contradicts:` · `defines:`. (Korean meta-phrases — `정의 attribution`, `맥락 참조`, `인용 강도`, `강한 결합`, `약한 참조` — fire only under WIKI_LANG=ko.)
- **W4** (required) is checked separately: after running `python tools/lint.py graph structure`, the overview file in question must not be in the "Broken links" list to PASS
- **C2 · S4 · S5** are outside the automatic-metric output range and are manually confirmed in the Desk's qualitative review (they require semantic analysis, outside the deterministic-lint domain).

#### `[Freshness]` warning (advisory outside the Rubric)

`python tools/lint.py overview` automatically detects whether the Authoring Guide's "update `last_updated` on completion" convention was executed. In two situations it outputs a one-line warning next to the overview file:

```
  [Freshness] ⚠️ last_updated=2026-04-18 but EDITOR region has uncommitted edits (today=2026-04-19) — update frontmatter before commit
  [Freshness] ⚠️ last_updated=2026-04-18 but EDITOR last changed in commit on 2026-04-19 — frontmatter was not refreshed
```

- **uncommitted case**: EDITOR-region edits in the working tree (AUTO-block-only rebuilds do not warn) + `last_updated` earlier than today → requests a frontmatter update before commit
- **commit-elapsed case**: the date of the most recent commit that touched the file > `last_updated` → the update was missed in a past iteration

Reason it is not incorporated as a Rubric criterion: it is **metadata hygiene**, not quality evaluation (the 30-criterion roster), so it sits as a separate advisory layer. No effect on the exit code. Silently skipped when git is not installed or on error.

#### `[AUTO drift]` warning (advisory outside the Rubric)

If the AUTO:MEMBERS/AUTO:SOURCES blocks diverge greatly from the git HEAD version, there is a risk that the EDITOR body goes stale by referencing past members/events/figures. `python tools/lint.py overview` measures this automatically with three metrics:

- **`member_jaccard`**: Jaccard similarity of the [[slug]] set of AUTO:MEMBERS (old ∩ new / old ∪ new)
- **`source_delta`**: rate of change of the "total N items" count (`|new-old|/max(old,1)`) · in the output format `(srcs A→B)`, A and B are source-file counts
- **`top10_new`**: number of new slugs among the top 10 of AUTO:SOURCES that were not in the previous top 10

**Layer distinction (avoid confusion when interpreting)**: `member_jaccard` is based on the **cluster-member hub (entity/concept) set**, while `source_delta`/`top10_new` are based on the **source-file set**. The two layers cannot be summed or directly compared — a cluster co-hosts N hubs and M sources, generally independent sets. Reading the drift report's `(srcs A→B)` value as a hub count or cluster size causes a misdiagnosis because it does not match the member count in `_clusters.json`.

3-tier thresholds (centrally managed as constants in `tools/_lint/overview.py`):

| Tier | Condition (any one) | Output |
|---|---|---|
| 🟢 stable | jaccard ≥ 0.85 · delta ≤ 15% · top10_new ≤ 2 | silent |
| 🟡 drift | jaccard 0.70–0.85 · delta 15–30% · top10_new 3–5 | `[AUTO drift] ... 🟡 drift — EDITOR re-review recommended` |
| 🔴 rewrite | jaccard < 0.70 · delta > 30% · top10_new ≥ 6 | `[AUTO drift] ... 🔴 rewrite — /wiki-lint overview <slug> --fix recommended` |

Reason it is not incorporated as a Rubric criterion: it is **change-magnitude monitoring**, not quality evaluation, so it sits as a separate advisory layer. No effect on the exit code. Silently skipped if the file is not in git HEAD (a new file) or has no AUTO block at all.

The AUTO:SOURCES sort in `tools/_build/clusters.py:_render_sources_block()` is implemented as a 3-tier stable sort of **weight desc + date desc + slug asc**, so rebuilding the same wiki state produces no top-15 shuffle (preventing a false drift positive).

---

### Part 2 — Root Overview Evaluation Rubric

Evaluation specific to `wiki/overview.md`. The criterion roster/required are owned by `_manifest.json` `overview-aggregate.roster` (29 criteria); the craft definitions/PASS-conditions/measurement by the mapping-table skill `criteria.json`/SKILL.md. structural/house-style share the dotted IDs of the Part 1 structural section above, but the scope is aggregate (baseline = cluster overview, unit = cluster section). **L2-4 specific craft**: `con.mece-clusters` (D1 cluster completeness) · `enc.summary-style` (D2 drill-down `{{Main}}`) · `jrn.due-impartiality` (D3 cross-cluster reference balance) · `enc.coatrack` (F1 theme-axis blocking).

**Completion conditions** (roster `overview-aggregate.roster` — 29 criteria):
- All 10 required (roster `required`) PASS
- **≥ 27 of all 29 PASS** (= total−2, computed from the roster · PARTIAL excluded from the count)
- For advisory (`jrn.due-impartiality`/house-style etc.) FAILs, reinforce by reference to the relevant skill/structural section (D3/house-style accompanied by human review)

**Evaluation execution order**: same as Part 1 — automatic (A) is the `[Rubric L2-4]` line of `python tools/lint.py overview aggregate` output, manual (M) is body review.

#### Interpreting the automatic (A) metric output

When `python tools/lint.py overview` runs, the following lines are output for `wiki/overview.md`:

```
wiki/overview.md:
  [Rubric L2-4] W1 links=N (≥200) ✅/⚠️  W2 ratio=X ✅/⚠️  W3 dup=N ✅/⚠️
  [Rubric L2-4] D1 clusters=N/N ✅  D2 drilldowns=N/N ✅  D3 balance=max/min ratio ✅/⚠️  F1 theme_refs=N ✅/⚠️
  [Rubric L2-4] R1 hot_tokens=N ✅/⚠️  L1 raw_slugs=N ✅/⚠️
  [Rubric L2-4] G1 grade_meta=N ✅/⚠️  G2 cite_type_meta=N ✅/⚠️
```
(The R2 dense_paras · B1 verdicts · L2 date_nonstd · L3 abbr_unexplained · S6 long_sents lines are omitted in this excerpt — the full set of lines is owned by `tools/_lint/overview.py` as SoT)

### Sources

The primary source texts of the craft criteria are owned by each craft skill SKILL.md's `## Sources` as SoT — [`journalism-writing`](../skills/journalism-writing/SKILL.md) (Nut graph · PAGE · Explainer · Beat · inverted pyramid · BBC due impartiality) · [`consulting-writing`](../skills/consulting-writing/SKILL.md) (McKinsey SCR · BCG bold-bullet · MECE · Forrester) · [`encyclopedia-writing`](../skills/encyclopedia-writing/SKILL.md) (WP MoS/Linking · NPOV · Summary style · Coatrack). structural/house-style have no external source text (own conventions).
