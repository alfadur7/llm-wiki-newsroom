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
- [<grade>] <claimant> — content [[evidence-slug#section]]
  # grade: [fact] primary · [analysis] secondary · [forecast] tertiary

## Key Quotes
> "quotation" — [[Speaker]]        # the speaker's page exists
> "quotation" — Speaker, role      # no page — plain text

## Connections
- <type>: [[Hub]] — one-line description
  # type: cites: · references: · contradicts: · defines:
```

### Schema Core Conventions

Detailed classification criteria and decision trees are in the [`## Authoring`](#authoring) section below:

- **`## Key Claims`** (Key Claims) line = the atomic unit `[<grade>] <claimant> — content`. The grade marker plus a named claimant are mandatory (`[[entity]]` when the speaker has a page, otherwise their plain-text real name). Even one missing line makes lint FAIL.
- **`## Connections`** (Connections) line = `<type>: [[Hub]] — description`. A missing prefix makes lint FAIL. The `contradicts:` line is the **single SoT of the theme contradiction DB** (`tools/_build/contradictions.py` extracts it at the line level).
- The prefix directly determines the `_graph.json` edge relation via `tools/_build/graph.py` line-level parsing (overriding the section heuristic).

### Authoring & Evaluation Entry Points

- How to write — the [`## Authoring`](#authoring) section below
- Quality judgment (Rubric automated metrics) — the [`## Evaluation Rubric`](#evaluation-rubric) section below
- Recommended command — `python tools/lint.py source [<slug>]` ([wiki-lint.md → source Subcommand](../commands/wiki-lint.md))

## Authoring

This guide governs how to author, migrate, and iterate on `wiki/sources/<slug>.md` files. A source page is a **Layer 2-1 source reflection** (see .claude/layers/README.md) — the entry point that absorbs a raw document into the wiki's epistemic primitives. The goal of this guide is to enforce the Phase 2 three-layer schema (claim atomization · citation type · evidence grade) starting from the authoring stage.

A Claude instance with no prior knowledge should be able to reproduce the same quality by reading this guide alone (Claude reproducibility principle).

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
4. **Write `## Key Claims` atomic units** — decompose the raw claims into atomic units of the form `[<grade>] <claimant> — content [optional anchor]` (the claimant is an `[[entity]]` or a plain-text real name). The grade judgment, claimant selection, and the anchor convention are in [Authoring Principles](#authoring-principles) and [Decision Trees](#decision-trees-making-ambiguous-cases-deterministic) below.
5. **Write `## Key Quotes`** — a `> "quotation" — Speaker, role` blockquote. Link the speaker when their page exists; when it does not (usually below the [`policies/naming.md`](../policies/naming.md) threshold) the terminal form is plain text plus the role (`— Bruce Perens, OSI co-founder`) — linking a page that does not exist leaves nothing but a broken link. The link target must be the speaker themselves: the speaker of `Matt Garman, AWS CEO` is Matt Garman, not `[[AWS]]`, and a concept hub never speaks. If the raw has a direct quotation from the speaker themselves, preserve it verbatim (do not replace it with a one-line summary) — a thin section here is the root cause of downstream themes and hubs hallucinating quotations. You may omit the section only when the raw genuinely has no direct quotations (analysis or forecast pieces).
6. **Write `## Connections` citation type prefixes** — for each hub/source link, attach a `<prefix>: [[Hub]] — one-line description`, classified by citation type (`cites:` · `references:` · `contradicts:` · `defines:`). The classification criteria are in [Authoring Principles](#authoring-principles) and [Decision Trees](#decision-trees-making-ambiguous-cases-deterministic) below. `contradicts:` is the single SoT of the theme contradiction DB.

### Authoring Principles

This section is the **application and examples for this wiki's sources** of the cit craft (claim atomization · citation typing · evidence grading) — the SoT of the craft principles and criteria is [`scholarly-citation`](../skills/scholarly-citation/SKILL.md); below are the notation conventions and examples mapped onto the source format. The **deterministic judgment** of ambiguous cases is handled by the [Decision Trees](#decision-trees-making-ambiguous-cases-deterministic) section below (principle = intent, tree = behavior).

#### Claim atomization (`## Key Claims`)

- **Enforce atomicity**: one line = one claim. "A does X and B does Y" splits into two lines.
- **State the grade**: every claim must carry a `[fact]`/`[analysis]`/`[forecast]` marker. Even one line without it makes lint FAIL.
- **Mandatory named claimant**: every claim names who said it — `[[claimant]]` when the speaker has a page, their plain-text real name when they fall below the [naming.md](../policies/naming.md) entity-addition threshold. Never link a page that does not exist, and never reach for a nearby entity to fill the slot (misattribution is the worse defect).
- **Anonymous subjects stay barred**: "the government", "the industry", "the foundation", "the community" fail in either form — resolve them to the concrete speaker. Plain text naming a page that *does* exist fails too: link it.
- **Claimant = the speaking subject** (≠ the analysis target): the claimant is the subject who *said, analyzed, or announced* the claim. If the content is "<X> analyzed/announced", the claimant is `[[X]]`, and the entity that is the *target* of analysis goes under `## Connections references:` (beware of misattributing the target as the claimant in research and commentary sources).
- **The stated speaker wins**: when the raw says "according to X", "X's report", or "X announced", the claimant is X — never the about-subject concept hub the source mostly discusses. Link X if it has a page, otherwise write X in plain text.
- **Content is a one-liner with a verb**: do not just list noun phrases like "405B-parameter model" or "AI acceleration". Make it a complete statement that includes a verb.
- **Evidence anchor recommended**: when a `[fact]` or `[analysis]` cites an external source, `[[<source-slug>#section]]` is recommended. For a self-source (this source's own body), omit the anchor.

Examples:
- ✅ `[fact] [[Meta]] — released Llama 3.1 under a community license that permits commercial use below a monthly-active-user threshold [[llama-3-1-release#Key Quotes]]`
- ✅ `[analysis] [[OpenSourceInitiative]] — argues that withheld training data prevents Llama from meeting the Open Source AI Definition`
- ✅ `[forecast] [[Mozilla]] — expects open-weight model adoption to keep accelerating among downstream developers`
- ❌ `Meta released Llama 3.1 under a community license` — missing grade marker
- ✅ `[fact] Pleias — released a fully open multilingual training dataset of over 2 trillion permissibly licensed tokens` — plain-text claimant, below the page-creation threshold
- ❌ `[fact] the foundation announced a new license` — anonymous subject (weasel); name the speaker
- ❌ `[analysis] Meta — argues its licence terms are compatible with open source` — plain text for a speaker who *has* a page; link it as `[[Meta]]`
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
  ├─ contradiction signal (any of the 3 branches below)? → contradicts:
  └─ otherwise                              → references:

hub is a concept?
  ├─ presents definition/scope?             → defines:
  ├─ contradiction signal (any of the 3 branches below)? → contradicts:
  └─ otherwise (mere application/context)   → references:

judgment ambiguous                          → references: (default safe)
```

**Decision-keyword dictionary**:
- `cites:` signals — "announced · stated · mentioned · quoted · replied · said · disclosed · commented", or specific figures (`%` · `$100M` · `10,000 people`). But only when this source directly quotes the hub's announcement, figure, or quotation in the body. If the hub merely appears as a comparison target in the body, downgrade to `references:`.
- `contradicts:` signals — **3 branches, any one suffices**:
  1. **Stance opposition** — "oppose · conflict · rebut · negate · object · the opposite" (explicit opposing-position vocabulary).
  2. **Action opposition** — one side takes a hostile formal action against the other (a lawsuit, an antitrust complaint, a regulatory corrective order, an appeal against a ruling). The action itself is the contradiction — no opposition vocabulary is required in the sentence.
  3. **Factual counterexample** — the source reports a concrete fact that contradicts the hub's claim (a promised release that did not ship, a measured figure refuting a stated one). The factual clash is the contradiction — again, no opposition vocabulary required.

  However, **evolution vocabulary** ("pivot · evolve · shift in view · change of direction · paradigm shift") is NOT `contradicts:` — classify it as `references:` (it describes a stage change or evolution of view, not a rebuttal or negation).
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

#### Claimant selection (priority)

```
1. the speaker has a wiki page                       → [[entity]]
2. the speaker is named in the raw but has no page   → plain-text real name + role
3. the speaker cannot be identified from the raw     → confidence=Low (skip)
```

Never substitute a *different* entity for a speaker who has no page — not the first
link in `## Connections`, not the source's dominant concept hub. Both were fallback
steps here until 2026-07-30 and were the direct cause of misattributed claims; step 2
is the answer they were standing in for.

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

- **`INTRINSICALLY_UNFIXABLE_SOURCES`** (permanent whitelist): reserved for lines whose speaker cannot be named at all — a generic-noun subject (`construction industry`, `government`) or a multi-actor enumeration. Falling below the stub threshold does **not** qualify: that speaker's plain-text name is a normal G2 pass. A whitelisted source is excluded from the ACCEPTABLE_FAILS count and surfaces only as a `[Whitelist] N permanent residual` advisory. When listing one, a policy-reason comment naming which unnameable form applies is mandatory.
- **`ACCEPTABLE_FAILS = 10`** (natural accumulation margin): the regression detector for the accumulated fails of new ingests outside the whitelist. Exceeding the threshold is a hard fail. The whitelist split restores the original intent (a temporary margin), blocking regression masking. Raise the constant only after stating a policy-change reason.

**etc. whitelist operation**: before adding a slug, empty the whitelist and measure that a real FAIL survives — an entry made to clear the threshold disables the check instead of recording a fact. When a whitelisted subject later resolves into a nameable speaker who accumulates ≥3 mentions + ≥2 clusters → create the entity stub → link it in the body → drop the whitelist entry.

**Evaluation execution order**:
1. Automated (A) criteria — run `python tools/lint.py source [<slug>]`, judge immediately from the output metrics.
2. If not met → return to the feedback loop (Iteration N+1).

#### Interpreting the automated (A) metric output

For readability, the lint output uses **legacy codes** (G1~G5·C1~C3·A1~A3·S1·W1·L1) — the correspondence to the mapping-table dotted IDs has its SoT in each craft skill `criteria.json`'s `legacy` field (e.g., G1=`cit.grade-marker` · C1=`cit.cite-type` · W1=`enc.link-density` · L1=`enc.slug-alias` · S1=structural). When `python tools/lint.py source [<slug>]` runs, **three lines** are output per source file (17 metrics — including F1·T1·Sc1, where T1 tags and Sc1 scraped are hard gates that block on a blank/missing value):

```
sources/<slug>.md:
  [Rubric] G1 grade=N/N ✅  G2 claimant=N/N ✅  G3 atomic=N ✅  G4 valid_claimant=N/N ✅  G5 composite=N ✅
  [Rubric] C1 prefix=N/N ✅  C2 ref_ratio=N% ✅  C3 type_hub=N/N ✅
  [Rubric] A1 anchored=N/M ✅  A2 quote_attr=N/M ✅  A3 valid_anchor=N/N ✅  S1 sections=3/3 ✅  W1 links=N ✅  L1 raw_slugs=0 ✅  F1 last_updated=✅  T1 tags=✅  Sc1 scraped=✅
```

When a cap is exceeded, a token recurs, or consistency is violated, an auxiliary advisory is shown:

```
  [Rubric] G1 missing grade lines: ['line N: ...']
  [Rubric] G2 missing claimant lines: ['line N: ...']
  [Rubric] C1 missing prefix lines: ['line N: ...']
  [Rubric] L1 raw slug samples: [...]
```

- **✅ = PASS**, **⚠️ = FAIL**, **— = exempt** (e.g., A2 for a source with no raw quotations, or whose quotes all carry a plain-text speaker)
- PASS condition per metric:
  - **G1**: `grade_marker = N/N` — among `## Key Claims` lines, those matching the grade-marker regex `^-\s*\[(fact|analysis|forecast)\]` (the English grade tokens `[fact]`/`[analysis]`/`[forecast]`) / all claim lines. N/N = 100% PASS; partial match FAILs.
  - **G2**: `claimant_named = N/N` — among `## Key Claims` lines, those naming a claimant right after the grade marker / all claim lines. A `[[<entity>]]` wikilink counts, as does a plain-text name that is not anonymous, not over-long, and not the title of an existing page. N/N = 100% PASS.
  - **G3**: `atomic_violations = 0` — the automated heuristic matches only the Korean conjunctions `와`/`및` joining two `[[hub]]` links (dormant on English prose; the English "and"/`+ ` composite split is author-applied / Desk-reviewed, not lint-enforced). 0 = PASS.
  - **C1**: `prefix = N/N` — among `## Connections` lines, those matching the `^- (cites|references|contradicts|defines):` regex / all lines. N/N = 100% PASS.
  - **C2**: `ref_ratio = N%` — the share of `references:` prefixes among `## Connections` lines. ≤ 95% PASS (over 95% is an advisory). Exempt (`—`) if there are fewer than 5 lines.
  - **A1**: `anchored = N/M` — among `## Key Claims` `[fact]`/`[analysis]` lines, those with a `[[<slug>#<section>]]` anchor pattern / all `[fact]`/`[analysis]` lines. Advisory — even 0% is PASS (same as Phase 1 Xanadu).
  - **A2**: `quote_attr = N/M` — among the denominator (blockquotes that link a speaker + blockquotes naming none), those linked to a target that exists. Plain-text speakers leave the denominator, since whether they should have been linked is not machine-decidable — step 5 owns that judgment, and *blocking* on a broken speaker link is `graph structure`'s job (required). Exempt (`—`) if the denominator is 0.
  - **S1**: `sections = 3/3` — all three headers `## Summary`·`## Key Claims`·`## Connections` present (`## Key Quotes` absent is OK). 3/3 PASS.
  - **W1**: `links ≥ 5` — total wikilinks in the body (frontmatter excluded).
  - **L1**: `raw_slugs = 0` — zero matches for raw-exposed `[[<kebab-case slug of 10+ chars>]]` (without `|`) in the body.

### Sources

The primary sources of the craft criteria have their SoT in each craft skill's SKILL.md `## Sources` — [`scholarly-citation`](../skills/scholarly-citation/SKILL.md) (Toulmin · scite/Elicit · WP:ASF · Smart Citations · Xanadu/Hyper-G · APA — all of cit.*) · [`encyclopedia-writing`](../skills/encyclopedia-writing/SKILL.md) (WP MoS/Linking — enc.link-density · slug-alias). Structural (S1) has no external primary source (an in-house convention).
