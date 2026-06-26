---
name: encyclopedia-writing
description: Encyclopedic neutral-reference writing craft — NPOV (attribute facts not opinions, due weight, neutral faction labels, verdict restraint), summary style and Coatrack avoidance, wikilink conventions (link density, first-mention, slug alias, abbreviation glossing). Use when writing or reviewing a neutral encyclopedic/wiki reference, landscape overview, hub, or source page, or when a source-based connected document that advocates no particular viewpoint is needed.
---

# encyclopedia-writing

Neutral-reference writing craft drawn from the encyclopedic editing tradition (the Wikipedia policy family). It keeps this wiki's overview, issue, and hub pages a connected reference that is grounded in facts and sources and advocates no particular viewpoint. `criteria.json` is the SoT for each criterion's definition, comparator, and source; content-type thresholds and algorithm params are injected by `.claude/layers/_manifest.json` (the skill is content-type-agnostic). Examples are illustrative of the target English prose; the localization rules that are intrinsically about Korean rendering are retained for any Korean-localized labels.

## Wikilink connectivity (enc.link-density · enc.first-mention · enc.lead-body)

A reference's value comes from the link density that lets a reader move to adjacent concepts; at the same time, re-linking the same target within one section is visual noise.

- **enc.link-density** — the EDITOR region (excluding AUTO blocks) holds at least the threshold number of `[[wikilink]]`s. "Articles on highly technical subjects might demand a higher density of links," so technical/finance domains are allowed slightly above the ceiling.
- **enc.first-mention** — "link a term at most once per major section, at first occurrence." A second link of the same stem within a section becomes plain text. A section that structurally cites the same target twice (e.g. adjacent-field boundary prose) is exempted via the manifest's `exempt_sections`.
- **enc.lead-body** — "the lead of an article usually has a greater density of links than later parts of the article"; this is expected, since the reader's first encounter is where navigation options should be densest. Because which span counts as the lead is content-type-bound, the orchestrator measures it.

All three are deterministic; `checks.py` (link-density·first-mention) or the orchestrator (lead-body) computes PASS/FAIL with manifest-injected thresholds/params.

## Neutrality & notation (enc.verdict-restraint · enc.slug-alias · enc.abbr-gloss · enc.encyclopedic-tone)

A reference advocates no viewpoint (NPOV) and follows readable notation conventions (MoS). Deterministic; thresholds injected by manifest.

- **enc.verdict-restraint** — "avoid stating opinions as facts" and "describe disputes, but do not engage in them." Write evaluative sentences in three strengths — observation ("the metric points the opposite way") and conditional recommendation ("appears to be"·"may be") are fine, but a verdict ("is reasonable"·"has the most explanatory power"·"is consistent with") over the threshold must be softened with hedging/attribution. Repeated verdicts under hedged wording stay neutral in form but biased in substance. (ko-localization renderings: observation `~ 지표가 정반대를 가리킨다`; conditional `~로 보인다`·`~일 가능성이 있다`; verdict `~이 합리적이다`·`가장 설명력이 높다`·`~에 부합한다`.)
- **enc.slug-alias** — do not expose a long raw kebab-case identifier; show a human-readable alias (MoS overlinking/readability). This wiki uses English aliases by default; native-script aliases only under WIKI_LANG=ko.
- **enc.abbr-gloss** — "an acronym should be written out in full for the first time, followed by the abbreviation in parentheses" (commonly used abbreviations such as global brands are exempt). Applies to abbreviations appearing in body text.
- **enc.encyclopedic-tone** — keep the encyclopedic register; do not self-reference the editorial artifact or editorial decisions (WP:SELFREF — an article "shouldn't refer to [the work] in a non-neutral fashion"). Editorializing such as "this document treats … as"·"here we keep only …" is deleted or absorbed into a factual statement. (ko-localization renderings: `본 문서는 ~로 둔다`·`여기서는 ~만 유지한다`.)

## Issue neutrality & balance (enc.npov-asf · enc.due-weight · enc.label-neutral · enc.back-reference)

A piece covering a dispute advocates no side and fairly juxtaposes both, grounded in facts and sources (WP:NPOV — ASF and DUE run through every section).

- **enc.npov-asf** — attribute every value-judgment/interpretation/claim with a named subject + source + figure/quote (≥2 of the 3); "avoid stating opinions as facts," and use no weasel words ("some say"·"many people"·"as is known"; ko renderings `혹자는`·`많은 사람이`·`알려진 바로는`). judge=M. e.g. ✅ "The IPCC warned of coastal-city risk in its 2021 report" (named source + date) / ❌ "Many experts believe coastal cities are at risk" (anonymous plurality — weasel)
- **enc.due-weight** — coverage is proportionate to prominence in reliable sources, not skewed to one side (WP:DUE); a minority view does not get equal space and is explicitly framed as a minority. judge=M. e.g. ✅ "The Earth is spherical and the scientific consensus is overwhelming; a minority dissents but without credible grounds" (proportionate weight + minority noted) / ❌ "The Earth is round. But some believe it is flat." (false balance)
- **enc.label-neutral** — both faction labels (or the aggregate's tension-axis titles) must be drawn from an equivalent vocabulary set. If only one side gets a value-laden word ("myth"·"empirical proof"·"skepticism"·"innovation," etc.), that side is privileged or demoted — unify both on a structural/standpoint basis ("replacement vs augmentation"·"industry-led vs regulation-led"). Deterministic check for one-sided skew = 0. **ko-localization rendering rule (WIKI_LANG=ko only)** — even when the English original is neutral, a literal Korean rendering can introduce connotation, so when localizing a title to Korean, check the following English→Korean mapping (applies to labels, titles, and body alike):

  | English (neutral) | Literal Korean (connotation introduced) | Recommended Korean (equivalent) |
  |---|---|---|
  | dual strategy | 이중성 (hypocrisy) | 이중 트랙·양 트랙 병행 |
  | paradox | 역설 (wrong) | 반전·교차 구도 |
  | tension | 긴장 (instability) | 대립·교차 압력 |
  | trade-off | 절충 (concession) | 상충 균형·양립 조건 |
  | hype | 과장 (value judgment) | 기대 담론·전망 강조 |
  | myth | 신화 (falsehood) | 담론·통설·전망 |
- **enc.back-reference** — a narrow issue piece keeps at least one entry-point link up to its parent/landscape overview (an upward link so the reader can move issue → field landscape; WP Summary style).

## Aggregation linking (enc.summary-style · enc.coatrack)

Encyclopedic conventions for a higher roll-up that covers lower detail. Deterministic; thresholds injected by manifest.

- **enc.summary-style** — "sections of long articles should be spun off into their own articles, leaving summaries in their place"; each subsection carries an entry-point link to its detail page (the `{{Main}}` hatnote). The roll-up summarizes and provides a drill-down path, not a copy of the detail.
- **enc.coatrack** — keep the roll-up's nominal subject from being obscured; a coatrack article "gets away from its nominal subject, and instead gives more attention to ... tangential subjects." Block references that drift to another axis (WP Coatrack·Scope).

## Navigational anchor (enc.nav-anchor-density · enc.connection-grouping)

A navigational-anchor page does not carry deep exposition; it serves as an entry point to adjacent pages. Deterministic; thresholds injected by manifest.

- **enc.nav-anchor-density** — when an anchor page's body prose exceeds the advisory ceiling, spin the deep-dive off into a sub-page (Summary style spinoff). A central anchor (a heavily-cited core page) is legitimately content-rich and exempt.
- **enc.connection-grouping** — when a connection list's flat links grow numerous, group them into sub-categories (`### Category`; ko `### 카테고리`) (MoS Layout). A grouped list passes regardless of count.

## Sources

Each URL points to the relevant page as of the last verification.

- [Wikipedia:Manual of Style/Linking](https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Linking) — wikilink density standard·lead-body gradient·first-mention principle·slug alias (overlinking avoidance)
- [Wikipedia:Neutral point of view](https://en.wikipedia.org/wiki/Wikipedia:Neutral_point_of_view) — verdict restraint·[Due and undue weight](https://en.wikipedia.org/wiki/Wikipedia:Neutral_point_of_view#Due_and_undue_weight) (due weight)·[Balancing aspects](https://en.wikipedia.org/wiki/Wikipedia:Neutral_point_of_view#Balancing_aspects_of_an_article) (per-axis balance)
- [Wikipedia:Manual of Style/Words to watch — WP:ASF](https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Words_to_watch#Attribution) — Attribute Statements to Facts·no weasel words (neutral faction labels·ASF attribution)
- [Wikipedia:Manual of Style/Self-references to avoid](https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Self-references_to_avoid) — encyclopedic tone·no editorial self-reference
- [Wikipedia:Manual of Style/Abbreviations](https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Abbreviations) — gloss abbreviation in parentheses on first appearance
- [Wikipedia:Summary style](https://en.wikipedia.org/wiki/Wikipedia:Summary_style) · [Template:Main](https://en.wikipedia.org/wiki/Template:Main) — drill-down entry point for aggregating pieces ({{Main}})
- [Wikipedia:Coatrack articles](https://en.wikipedia.org/wiki/Wikipedia:Coatrack_articles) · [Wikipedia:Scope](https://en.wikipedia.org/wiki/Wikipedia:Scope) — block tangential subjects·scope discipline
- [Wikipedia:Manual of Style/Layout](https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Layout) — connection-list grouping (navigational anchor)
