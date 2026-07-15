# L2-1 Source Page Guide

## Page Format

A source page (`wiki/sources/<slug>.md`) enforces **three epistemic primitives** as its schema — claim atomization · citation type · evidence grade. The definition, authoring procedure, and decision tree for each primitive live in the [`## Authoring`](#authoring) section below.

### Standard Structure

```markdown
---
title: "Source Title (English)"
type: source
tags: []
published: YYYY-MM-DD      # report date — from raw published or extracted from article body; leave blank if unknown
scraped: YYYY-MM-DD        # collection (scrape) date — raw `created` as-is. Weekly-briefing aggregation key
source_file: raw/...       # raw/NewsScrap/<slug>.md or raw/PDF/<slug>.pdf
source_url: "https://..."  # URL SoT (HTML auto-enriched at ingest, PDF manual)
last_updated: YYYY-MM-DD    # bump to today's date when the source MD is edited (auto-stamped at ingest)
---

## Summary
2–4 sentence summary.

## Key Claims
- [<grade>] [[claimant]] — content [[evidence-slug#section]]
  # grade: [fact] primary · [analysis] secondary · [forecast] tertiary

## Key Quotes
> "quotation" — [[Speaker]]

## Connections
- <type>: [[Hub]] — one-line description
  # type: cites: · references: · contradicts: · defines:
```

### Schema Core Conventions

Detailed classification criteria and decision trees are in the [`## Authoring`](#authoring) section below:

- **`## Key Claims`** (Key Claims) line = the atomic unit `[<grade>] [[claimant]] — content`. The grade marker plus an entity wikilink are mandatory. Even one missing line makes lint FAIL.
- **`## Connections`** (Connections) line = `<type>: [[Hub]] — description`. A missing prefix makes lint FAIL. The `contradicts:` line is the **single SoT of the theme contradiction DB** (`tools/_build/contradictions.py` extracts it at the line level).
- The prefix directly determines the `_graph.json` edge relation via `tools/_build/graph.py` line-level parsing (overriding the section heuristic).

### Authoring & Evaluation Entry Points

- How to write — the [`## Authoring`](#authoring) section below
- Quality judgment (Rubric automated metrics) — the [`## Evaluation Rubric`](#evaluation-rubric) section below
- Recommended command — `python tools/lint.py source [<slug>]` ([wiki-lint.md → source Subcommand](../commands/wiki-lint.md))

## Authoring

This guide governs how to author, migrate, and iterate on `wiki/sources/<slug>.md` files. A source page is a **Layer 2-1 source reflection** (see .claude/layers/README.md) — the entry point that absorbs a raw document into the wiki's epistemic primitives. The goal of this guide is to enforce the Phase 2 three-layer schema (claim atomization · citation type · evidence grade) starting from the authoring stage.

A Claude instance with no prior knowledge should be able to reproduce the same quality by reading this guide alone (Claude reproducibility principle).

### Read Scope (by work scenario)

When entering a task, first identify the single row matching your scenario and read closely only the four columns of that row — the CLAUDE.md section · this guide · the Rubric · the auxiliary guide. No additional Read beyond the table is needed.

| Task | Page Format | This Guide | Rubric | Auxiliary Guide |
|------|------------|----------|--------|------------|
| Author one new source (`wiki/sources/<slug>.md`) | `.claude/layers/source.md` | full | full | — |
| Perform the source portion within the ingest workflow | `.claude/layers/source.md` | full | full | `.claude/commands/wiki-ingest.md` |

### Which writing tradition does it follow

A source page follows the **verifiable-attribution craft** derived from the traditions of scholarly citation, journalistic attribution, and hypertext citation anchoring. The technique definitions, authoring criteria, and primary sources (claim atomization · evidence grading · claimant attribution · citation typing · anchoring) have their SoT in the [`scholarly-citation`](../skills/scholarly-citation/SKILL.md) `criteria.json` and SKILL.md, while wikilink density and slug notation live in [`encyclopedia-writing`](../skills/encyclopedia-writing/SKILL.md). Read these explicitly when entering authoring (Reporter, Columnist) or review (Desk).

The table below is the **mapping** of which craft criterion each part of a source page corresponds to (dotted IDs; the definitions live in the skill):

| Source component | Corresponding craft criterion (dotted ID) |
|---|---|
| `## Key Claims` atomic unit | `cit.grade-marker` · `cit.claimant-link` · `cit.atomic` · `cit.composite-split` · `cit.claimant-valid` |
| `## Connections` citation type | `cit.cite-type` · `cit.cite-distribution` · `cit.cite-type-hub` |
| evidence anchor · `## Key Quotes` | `cit.anchor` · `cit.speaker-link` · `cit.anchor-valid` |
| total wikilinks · slug notation | `enc.link-density` · `enc.slug-alias` |

### Execution Order (step-by-step guide)

This guide applies at step 4 (authoring the source page) of the 12-step procedure that `/wiki-ingest` runs. For the general procedure, see `.claude/commands/wiki-ingest.md`. (Existing source migration and iteration apply the same authoring order below.)

1. **Read the raw document end to end** — identify key claims, quotations, figures, and the entities/concepts mentioned.
2. **Write the frontmatter** — fill in title · type · tags · published · scraped · source_file · source_url (field meanings are in the schema comments above). If `tags` is empty, the source lint T1 hard gate blocks it (consumed as the node badge in the graph browser); candidates are suggested from the `## Connections` hubs by `python tools/_ingest/suggest_tags.py --file wiki/sources/<slug>.md`. The URL SoT convention is in .claude/layers/source.md.
3. **Write `## Summary`** — a 2–4 sentence English summary.
4. **Write `## Key Claims` atomic units** — decompose the raw claims into atomic units of the form `[<grade>] [[claimant]] — content [optional anchor]`. The grade judgment, the claimant-absent fallback, and the anchor convention are in [Authoring Principles](#authoring-principles) and [Decision Trees](#decision-trees-making-ambiguous-cases-deterministic) below.
5. **Write `## Key Quotes`** — a `> "quotation" — [[Speaker]]` blockquote. The Speaker is an entity wikilink. If the raw has a direct quotation from the speaker themselves, preserve it verbatim (do not replace it with a one-line summary) — a thin section here is the root cause of downstream themes and hubs hallucinating quotations. You may omit the section only when the raw genuinely has no direct quotations (analysis or forecast pieces).
6. **Write `## Connections` citation type prefixes** — for each hub/source link, attach a `<prefix>: [[Hub]] — one-line description`, classified by citation type (`cites:` · `references:` · `contradicts:` · `defines:`). The classification criteria are in [Authoring Principles](#authoring-principles) and [Decision Trees](#decision-trees-making-ambiguous-cases-deterministic) below. `contradicts:` is the single SoT of the theme contradiction DB.

### Authoring Principles

This section is the **application and examples for this wiki's sources** of the cit craft (claim atomization · citation typing · evidence grading) — the SoT of the craft principles and criteria is [`scholarly-citation`](../skills/scholarly-citation/SKILL.md); below are the notation conventions and examples mapped onto the source format. The **deterministic judgment** of ambiguous cases is handled by the [Decision Trees](#decision-trees-making-ambiguous-cases-deterministic) section below (principle = intent, tree = behavior).

#### Claim atomization (`## Key Claims`)

- **Enforce atomicity**: one line = one claim. "A does X and B does Y" splits into two lines.
- **State the grade**: every claim must carry a `[fact]`/`[analysis]`/`[forecast]` marker. Even one line without it makes lint FAIL.
- **Mandatory claimant wikilink**: every claim must have at least one `[[claimant]]` entity wikilink. A plain-text subject ("the government", "the industry") is a weasel. Convert vague subjects like "the foundation" or "the community" into the nearest concrete entity (e.g., "OpenSourceInitiative", "Meta").
- **Claimant = the speaking subject** (≠ the analysis target): the claimant is the subject who *said, analyzed, or announced* the claim. If the content is "<X> analyzed/announced", the claimant is `[[X]]`, and the entity that is the *target* of analysis goes under `## Connections references:` (beware of misattributing the target as the claimant in research and commentary sources).
- **No concept-hub fallback when the speaking entity exists**: if the speaker X explicitly stated as "according to X", "X's report", or "X announced" has an entity page, the claimant is `[[X]]` — do not fall back to an about-subject concept hub. The concept fallback (priority ③ below) applies only when the speaker has no entity (anonymous, an uncreated person, or a publication with no entity).
- **Content is a one-liner with a verb**: do not just list noun phrases like "405B-parameter model" or "AI acceleration". Make it a complete statement that includes a verb.
- **Evidence anchor recommended**: when a `[fact]` or `[analysis]` cites an external source, `[[<source-slug>#section]]` is recommended. For a self-source (this source's own body), omit the anchor.

Examples:
- ✅ `[fact] [[Meta]] — released Llama 3.1 under a community license that permits commercial use below a monthly-active-user threshold [[llama-3-1-release#Key Quotes]]`
- ✅ `[analysis] [[OpenSourceInitiative]] — argues that withheld training data prevents Llama from meeting the Open Source AI Definition`
- ✅ `[forecast] [[Mozilla]] — expects open-weight model adoption to keep accelerating among downstream developers`
- ❌ `Meta released Llama 3.1 under a community license` — missing grade marker
- ❌ `[fact] the foundation announced a new license` — missing claimant wikilink (weasel)
- ❌ `[analysis] [[Meta]] — OSI analyzed whether Llama qualifies as open source` — the claimant must be the speaking subject (OSI), not the analysis target (Meta)

#### Citation type (`## Connections`)

- **Mandatory prefix**: every line is of the form `<type>: [[Hub]] — description`. Even one line without a prefix makes lint FAIL.
- **Default safe = `references:`**: when the semantic strength is ambiguous, use `references:`. That is more accurate than wrongly attaching `cites:`.
- **`cites:` criterion**: when this source has pulled in a hub's **specific claim, figure, or quotation**. A mere contextual mention is `references:`.
- **Body evidence required (no dangling)**: every `## Connections` line must have a supporting passage in `## Key Claims` or the summary. Do not add a hub that never appears in the body to the connections only.
- **`contradicts:` single SoT**: all contradiction relations are recorded on a `## Connections` `contradicts:` line (covering both source↔hub stance opposition and source↔other-source factual/interpretive disagreement). `tools/_build/contradictions.py` extracts these lines to build the theme contradiction DB (`_contradictions.json`), so all contradiction attribution gathers in this one place.
- **`defines:` scope of use**: only when the hub is a concept and this source presents its definition or scope. Almost never used on entity hubs.

Examples:
- ✅ `cites: [[Meta]] — quotes the Llama community-license terms on commercial use`
- ✅ `references: [[OpenSourceInitiative]] — mentions the Open Source AI Definition context`
- ✅ `contradicts: [[deepseek-open-weights]] — states the opposing position on releasing weights without training data`
- ✅ `defines: [[OpenSourceAI]] — defines the four freedoms an open-source AI system must grant`
- ❌ `[[Meta]] — Llama community license` — missing prefix

#### Evidence grade (`[fact]`/`[analysis]`/`[forecast]`)

- **Meaning of the three grades**:
  - `[fact]` primary — quotation from the speaker themselves · primary statistics · financial statements · statutory text · raw text of an official press release
  - `[analysis]` secondary — explanation by an official body or expert · third-party analysis · critique · meta-research
  - `[forecast]` tertiary — future estimate · forecast · commentary · prediction · scenario
- **When classification is ambiguous**: default to `[analysis]`. A conservative `[analysis]` classification is safer than over-claiming `[fact]`.
- **Self-source allowed**: if this source is itself the primary utterance and you preserved that quotation in this page's body, use `[fact]`. In that case the anchor is a self-anchor (`[[<self-slug>#Key Quotes]]`) or omitted.

#### Common Principles

- **English body (default)**: apply .claude/policies/language.md. The body is English by default; the claimant and hub wikilinks match the file name. A native-script (e.g. Korean) filename is the exception for a subject whose name is native-script only — see [naming.md](../policies/naming.md).
- **Alias convention for wikilinks**: if a kebab-case slug of 10+ characters is exposed raw in the body, an alias is mandatory — `[[osi-open-source-ai-definition|OSI Open Source AI Definition]]`. A short slug (`[[RAG]]`) needs no alias.
- **`source_url` SoT**: the frontmatter `source_url` is the SoT for the URL. It may be auto-enriched from the raw MD frontmatter, but PDFs are filled in manually.
- **`last_updated` bump**: when the source MD is edited, bump the frontmatter `last_updated` to today's date (YYYY-MM-DD).
- **Attribution distancing**: the narrator voice must not absorb self-claims, external criticism, or superlatives as assertions. When the raw has a speaking subject, distance with "according to X's announcement" or "X stated that…"; hedge superlatives like "world's first / nation's first" with "claims to be…". In a multi-camp comparison source, if only one camp is directly quoted while the others are narrator-absorbed (an asymmetry), note "no official comment" for the weaker camp at least once. When a vendor-only source has no self-acknowledged limitation, you must surface "external assessment is outside the raw's scope".

### Decision Trees (making ambiguous cases deterministic)

Following these rules in ambiguous cases achieves both consistency across new ingests and minimal human-review burden.

#### Citation type decision tree (`## Connections`)

```
hub is an entity?
  ├─ utterance/figure/quote attribution?    → cites:
  ├─ explicit opposing stance?              → contradicts:
  └─ otherwise                              → references:

hub is a concept?
  ├─ presents definition/scope?             → defines:
  ├─ explicit opposition to this source's stance? → contradicts:
  └─ otherwise (mere application/context)   → references:

judgment ambiguous                          → references: (default safe)
```

**Decision-keyword dictionary**:
- `cites:` signals — "announced · stated · mentioned · quoted · replied · said · disclosed · commented", or specific figures (`%` · `$100M` · `10,000 people`). But only when this source directly quotes the hub's announcement, figure, or quotation in the body. If the hub merely appears as a comparison target in the body, downgrade to `references:`.
- `contradicts:` signals — "oppose · conflict · rebut · negate · object · the opposite". However, **evolution vocabulary** ("pivot · evolve · shift in view · change of direction · paradigm shift") is NOT `contradicts:` — classify it as `references:` (it describes a stage change or evolution of view, not a rebuttal or negation).
- `defines:` signals — "definition · concept · scope · is defined as"
- everything else → `references:`

#### Evidence grade decision tree (`## Key Claims`)

```
primary material + explicit speaking subject? (any one of the below satisfies = OR)
  ├─ direct quotation from the speaker ("disclosed that…" · "announced that…")    → [fact]
  ├─ primary statistics · financial statements · statutory text · raw press-release text   → [fact]
  └─ specific figure (% · 100M · persons · hours) AND named subject                → [fact]
future tense · "forecast · expect · predict · will be · observe · likelihood of"?  → [forecast]
"analyze · interpret · assess · diagnose · explain · point out"?                   → [analysis]
judgment ambiguous                                                                → [analysis] (default safe)
```

**Decision-keyword dictionary**:
- `[fact]` signals — direct quotation ("disclosed that…" · "announced that…") · primary statistics/financial statements/statutory text · (specific figure AND named speaking subject) — any one of the three (OR)
- `[forecast]` signals — "forecast · expect · predict · will be · observe · likelihood of"
- `[analysis]` signals — "analyze · interpret · assess · diagnose · explain · point out"
- everything else → `[analysis]`

#### Claimant wikilink absent — fallback (priority)

```
1. entity that appears in the raw body + has a wiki page    → use
2. the first entity wikilink in the source's `## Connections`        → use
3. the source's dominant concept hub (only when the speaker entity is absent)  → use
4. none of the above                                        → confidence=Low (skip)
```

`Low` confidence is queued for main-thread review and excluded from batch auto-commit.

#### Citation type–hub consistency check (automated lint)

A sub-agent self-checks whether the `<type>:` prefix is consistent with the hub kind:

| prefix | allowed hub type |
|--------|------------|
| `cites:` | entity (preferred) · concept (exception) |
| `references:` | any hub |
| `contradicts:` | entity · concept (both) |
| `defines:` | **concept only** (entity = misclassification) |

→ on finding `defines: [[<entity>]]`, auto-correct to `references:` or `cites:`.

#### Composite claim split rule

When two atomic claims are juxtaposed on one line, split them:

```
detection patterns:
  - English "and" (or "·") joining two [[hub]] links with their own predicates on one line
  - "[[A]] X · [[B]] Y" multiple [[hub]] + verb combination
  (Only the Korean conjunction 와/및 · verb-ending 했고…했다 forms are machine-matched by G3/G5;
   the English cues above are author-applied / Desk-reviewed, not lint-enforced.)

handling:
  → split into two lines, attach a grade marker separately to each
```

Examples:
- ❌ `[fact] [[Meta]] — released open weights, and [[DeepSeek]] — released open weights`
- ✅ `[fact] [[Meta]] — released open weights` + `[fact] [[DeepSeek]] — released open weights`

### Feedback Loop (iterate until the Rubric conditions are met)

Iteratively improve the source page until it meets the completion condition (roster `source.roster` — 7 required PASS + 12+/14 total PASS).

1. **Iteration 1 (draft)**: author per the execution order above.
2. **Evaluate**: judge immediately from the `[Rubric]` lines output by `python tools/lint.py source <slug>`.
3. **Completion judgment**: completion condition met → done. Not met → step 4.
4. **Iteration N+1 (reinforce)**: for each FAIL/PARTIAL criterion, the reinforcement standard's SoT is **that craft skill's SKILL.md and criteria.json** (the dotted IDs in the mapping table above) — take each criterion's PASS condition as the direct target. For the S1 schema section, see the structural section above.

**Safeguard**: if the same criterion keeps FAILing after two consecutive reinforcement attempts → re-examine the guide and skill criteria (e.g., a quotation-heavy source lacking primary material naturally lacks `[fact]` — apply the Two-tier whitelist).

## Evaluation Rubric

This Rubric pairs with `.claude/layers/source.md`'s definition of "how to write" to provide the evaluation criteria that judge "how well it was written". The targets are all `wiki/sources/<slug>.md` files.

**Judgment method**:
- Each criterion is three-level — **PASS / PARTIAL / FAIL** (PARTIAL is excluded from the completion count).
- **Automated (A)** criteria are machine-verified from the metrics output by `python tools/lint.py source [<slug>]`.
- **Manual (M)** criteria are judged by Claude or a human reviewer reading the body.

**Criteria SoT**: the source-evaluation criterion roster (applied criteria and required flags) is `_manifest.json` `source.roster` (14 criteria); the definition, PASS condition, and measurement of each craft criterion are in the skill `criteria.json`/SKILL.md from the "which writing tradition" mapping table above (cit.* in the scholarly-citation `evaluate_citation` bundle; enc.link-density and slug-alias in encyclopedia-writing). Structural criteria with no external craft source are in the section below.

#### Structural criteria (not craft — held solely by layers)

| Dotted ID (legacy) | Criterion | PASS condition | Judgment | Required |
|---|---|---|---|---|
| `struct.schema-sections` (S1) | required sections complete | all three of `## Summary`·`## Key Claims`·`## Connections` present (`## Key Quotes` is optional) | A | ✅ |

**Completion condition** (roster `source.roster` — 14 criteria):
- all 7 required (roster `required`: G1·G2·C1·S1·L1·G4·C3) PASS
- **at least 12 of 14 total** PASS (= total−2, roster-computed · PARTIAL excluded)
- advisory FAILs (G3·G5·C2·A1·A2·A3, etc.) are reinforced by reference to that craft skill's criteria, with some exemptions depending on the source kind (the Two-tier policy below)

**Two-tier residual-fail policy** — two constants in `tools/_lint/source.py` separate permanent exemption from natural accumulation margin:

- **`INTRINSICALLY_UNFIXABLE_SOURCES`** (permanent whitelist): the area of permanently accepted plain text under the `feedback_no_single_source_stub` policy — fundamentally one-off claimants (failing the stub threshold of ≥3 mentions + ≥2 clusters), generic-noun subjects (`construction industry`, `government`), or self-source repetition (multi-cluster 0). A whitelisted source is excluded from the ACCEPTABLE_FAILS count and surfaces only as a `[Whitelist] N permanent residual` advisory. When listing one, a policy-reason comment (one-off claim source · generic-noun form · no multi-cluster appearance) is mandatory. SoT-unified — the same threshold from `.claude/policies/naming.md` "entity-addition threshold" and the memory `feedback_no_single_source_stub` governs both areas (entity-stub creation · source-schema claimant) together.
- **`ACCEPTABLE_FAILS = 10`** (natural accumulation margin): the regression detector for the accumulated fails of new ingests outside the whitelist. Exceeding the threshold is a hard fail. The whitelist split restores the original intent (a temporary margin), blocking regression masking. Raise the constant only after stating a policy-change reason.

**etc. whitelist operation**: when a residual one-off claimant accumulates ≥3 mentions + ≥2 clusters in future ingests → create the entity stub → restore the body wikilink → remove the source from the whitelist (G2/G4 PASS regresses back as the stub threshold is met). This is pending-followup #6 — monitoring the accumulation of one-off claimants.

**Evaluation execution order**:
1. Automated (A) criteria — run `python tools/lint.py source [<slug>]`, judge immediately from the output metrics.
2. If not met → return to the feedback loop (Iteration N+1).

#### Interpreting the automated (A) metric output

For readability, the lint output uses **legacy codes** (G1~G5·C1~C3·A1~A3·S1·W1·L1) — the correspondence to the mapping-table dotted IDs has its SoT in each craft skill `criteria.json`'s `legacy` field (e.g., G1=`cit.grade-marker` · C1=`cit.cite-type` · W1=`enc.link-density` · L1=`enc.slug-alias` · S1=structural). When `python tools/lint.py source [<slug>]` runs, **three lines** are output per source file (17 metrics — including F1·T1·Sc1, where T1 tags and Sc1 scraped are hard gates that block on a blank/missing value):

```
sources/<slug>.md:
  [Rubric] G1 grade=N/N ✅  G2 claimant=N/N ✅  G3 atomic=N ✅  G4 valid_claimant=N/N ✅  G5 composite=N ✅
  [Rubric] C1 prefix=N/N ✅  C2 ref_ratio=N% ✅  C3 type_hub=N/N ✅
  [Rubric] A1 anchored=N/M ✅  A2 quote_attr=N/N ✅  A3 valid_anchor=N/N ✅  S1 sections=3/3 ✅  W1 links=N ✅  L1 raw_slugs=0 ✅  F1 last_updated=✅  T1 tags=✅  Sc1 scraped=✅
```

When a cap is exceeded, a token recurs, or consistency is violated, an auxiliary advisory is shown:

```
  [Rubric] G1 missing grade lines: ['line N: ...']
  [Rubric] G2 missing claimant lines: ['line N: ...']
  [Rubric] C1 missing prefix lines: ['line N: ...']
  [Rubric] L1 raw slug samples: [...]
```

- **✅ = PASS**, **⚠️ = FAIL**, **— = exempt** (e.g., A2 for a source with no raw quotations)
- PASS condition per metric:
  - **G1**: `grade_marker = N/N` — among `## Key Claims` lines, those matching the grade-marker regex `^-\s*\[(fact|analysis|forecast)\]` (the English grade tokens `[fact]`/`[analysis]`/`[forecast]`) / all claim lines. N/N = 100% PASS; partial match FAILs.
  - **G2**: `claimant_wikilink = N/N` — among `## Key Claims` lines, those with a `[[<entity>]]` wikilink right after the grade marker / all claim lines. N/N = 100% PASS.
  - **G3**: `atomic_violations = 0` — the automated heuristic matches only the Korean conjunctions `와`/`및` joining two `[[hub]]` links (dormant on English prose; the English "and"/`+ ` composite split is author-applied / Desk-reviewed, not lint-enforced). 0 = PASS.
  - **C1**: `prefix = N/N` — among `## Connections` lines, those matching the `^- (cites|references|contradicts|defines):` regex / all lines. N/N = 100% PASS.
  - **C2**: `ref_ratio = N%` — the share of `references:` prefixes among `## Connections` lines. ≤ 95% PASS (over 95% is an advisory). Exempt (`—`) if there are fewer than 5 lines.
  - **A1**: `anchored = N/M` — among `## Key Claims` `[fact]`/`[analysis]` lines, those with a `[[<slug>#<section>]]` anchor pattern / all `[fact]`/`[analysis]` lines. Advisory — even 0% is PASS (same as Phase 1 Xanadu).
  - **A2**: `quote_speakers = N/N` — number of `## Key Quotes` blockquotes / of those, the number with a speaker wikilink in `— [[Speaker]]` form. Exempt (`—`) if there are 0 blockquotes.
  - **S1**: `sections = 3/3` — all three headers `## Summary`·`## Key Claims`·`## Connections` present (`## Key Quotes` absent is OK). 3/3 PASS.
  - **W1**: `links ≥ 5` — total wikilinks in the body (frontmatter excluded).
  - **L1**: `raw_slugs = 0` — zero matches for raw-exposed `[[<kebab-case slug of 10+ chars>]]` (without `|`) in the body.

### Sources

The primary sources of the craft criteria have their SoT in each craft skill's SKILL.md `## Sources` — [`scholarly-citation`](../skills/scholarly-citation/SKILL.md) (Toulmin · scite/Elicit · WP:ASF · Smart Citations · Xanadu/Hyper-G · APA — all of cit.*) · [`encyclopedia-writing`](../skills/encyclopedia-writing/SKILL.md) (WP MoS/Linking — enc.link-density · slug-alias). Structural (S1) has no external primary source (an in-house convention).
