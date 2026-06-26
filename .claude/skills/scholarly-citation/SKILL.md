---
name: scholarly-citation
description: Verifiable-attribution and citation-discipline craft — atomic claim decomposition, evidence grading (primary/analysis/forecast tiers), claimant attribution, citation typing (cites/references/contradicts/defines), source anchoring (Xanadu). Use when writing or reviewing a reference or synthesis page that attributes and cites source-based claims so they stay traceable, or when claim attribution, citation typing, or evidence grading is needed.
---

# scholarly-citation

Verifiable-attribution craft drawn from scholarly/scientific citation traditions (citation classification, typing, anchoring). It ensures every claim in this wiki is atomized, evidence-graded, attributed to a speaker, typed by citation meaning, and anchored to a source location — and therefore traceable. Unlike the three borrowed traditions (narrative, exec summary, encyclopedic neutrality), this craft synthesizes external sources into an atomic-claim schema and is the project's signature. `criteria.json` is the SoT for each criterion's definition, comparator, and source; wiki-global state (page existence·hub type·section titles) is injected by the orchestrator (`tools/_lint/source.py`). The schema literals (`## Key Claims`, `[fact]`, `cites:` etc.) are the wiki's actual schema markers and section headers.

## Claim atomization & grading (cit.grade-marker · cit.atomic · cit.composite-split)

One claim, one line, one utterance. Each line of `## Key Claims` (Key Claims) marks an evidence grade — `[fact]` (primary source), `[analysis]` (secondary analysis), `[forecast]` (forecast). Putting two subjects' claims on one line (joined by "and"/"&" or a comma series spanning two hubs; ko: the conjunctions `와`/`및`), or chaining verb phrases on one line ("…did, and …did"; ko: `~했고, ~했다`), breaks atomicity.

## Claimant attribution (cit.claimant-link · cit.claimant-valid · cit.speaker-link)

Every claim is bound to who said it. A `[[claimant]]` wikilink right after the grade marker names the speaker; anonymous subjects ("the government"·"industry sources"; ko `정부는`·`업계에서는`) are forbidden (WP:ASF — "avoid stating opinions as facts"; attribute them to a named source). A blockquote carries a speaker-attribution wikilink (APA author-date principle — identify the cited author). The attribution target must exist as a real page.

## Citation typing (cit.cite-type · cit.cite-distribution · cit.cite-type-hub)

Each line of `## Connections` (Connections) types the citation's meaning — `cites:` (direct grounds)·`references:` (context)·`contradicts:` (dispute)·`defines:` (definition). This extends scite Smart Citations' Supporting / Mentioning / Contrasting classes (with `defines:` added). If every line collapses to the default-safe `references:`, that signals avoidance of meaning classification. `defines:` points only to a concept hub.

## Source anchoring (cit.anchor · cit.anchor-valid)

An external-evidence citation anchors to the source's section — `[[slug#section]]` (ko: `[[slug#섹션]]`). This applies Xanadu citation anchoring (visible links to the precise source location, Ted Nelson) at the source level; a gradual migration, so 0% still passes (advisory), but the anchor target's slug and section must exist.

## Synthesis citation integrity (cit.cite-consistency · cit.grounding · cit.anchor-evidence)

A piece synthesizing many sources follows Select→Read→Cite discipline — the declared source set (frontmatter) is the top set, and both the sources read and the sources cited in the body are subsets of it.

- **cit.cite-consistency** — every source cited in the body is registered in the declared source list (body ⊆ declaration). Citing an undeclared source is an editorial slip (omission).
- **cit.grounding** — a source offered as representative evidence must actually be read and used. When at least one of the source's direct-quote / key-claim items appears in the body as a substring, that is objective evidence of having read it (writing from a one-line summary by memory/guess risks divergence from the source). The deterministic lint blocks only the "never read at all" extreme; full read-through rests on editor self-discipline.
- **cit.anchor-evidence** — when a direct quote is placed in representative evidence, mark the citation location with a source section anchor (`[[slug#section]]`; ko `[[slug#섹션]]`) — the same Xanadu principle applied to synthesis evidence. A gradual migration, so advisory.

## Schema meta-use (cit.grade-meta · cit.cite-type-meta)

The synthesizing piece's narrative consciously reflects the evidence-grade (`[fact]`·`[analysis]`·`[forecast]`) and citation-type (`cites:`·`references:`·`contradicts:`·`defines:`) schema attached to sources — noting which grades the evidence base rests on, the dominant claimant, strong coupling (cites) vs context (references) — to deepen attribution. Confine attribution strength to factual statements; do not let it spill into verdict conclusions. Deterministic measurement (`count_grade_meta`·`count_cite_type_meta`) counts grade/cite-type meta expressions as advisory.

## Sources

Each URL points to the relevant page as of the last verification.

- [Toulmin Argument — Purdue OWL](https://owl.purdue.edu/owl/general_writing/academic_writing/historical_perspectives_on_argumentation/toulmin_argument.html) — Claim·Data·Warrant·Qualifier decomposition (claim atomization)
- [scite citation classification](https://scite.ai/) · [Elicit](https://elicit.com/) — claim atomization + citation-context classification (evidence grading·citation typing)
- [Wikipedia:Manual of Style/Words to watch — WP:ASF](https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Words_to_watch#Attribution) — Attribute Statements to Facts (claimant attribution)
- [scite Smart Citations](https://scite.ai/) — Supporting/Mentioning/Contrasting classification (→ extended with defines)
- [Project Xanadu citation anchoring (Nelson 1965)](https://en.wikipedia.org/wiki/Project_Xanadu) · [Hyper-G typed edges (Maurer 1996)](https://www.iicm.tugraz.at/) — citation-location anchoring
- [APA in-text citation guidelines](https://apastyle.apa.org/style-grammar-guidelines/citations/basic-principles) — name the cited speaker
