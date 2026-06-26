---
name: consulting-writing
description: Management-consulting writing craft — McKinsey SCR (Situation·Complication·Resolution), Minto Pyramid/MECE, BCG bold-bullet executive summary, so-what upfront, numeric precision, Forrester Landscape. Use when writing or reviewing an executive summary for decision-makers or a roll-up/landscape overview, or when a conclusion-first compressed structure, MECE completeness, or bold-bullet summary is needed.
---

# consulting-writing

Writing craft drawn from management-consulting deliverables — the executive-summary / pyramid structure that compresses a complex domain for decision-makers, and the MECE completeness of a roll-up. `criteria.json` is the SoT for each criterion's definition, comparator, and source; shared parsing for the deterministic checks is orchestrator-injected (the skill is content-type-agnostic). Examples are illustrative of the target English prose.

## MECE completeness (con.mece-axes · con.mece-clusters)

A roll-up document must cover its subitems with no overlap and no gaps — the MECE principle separates a set of items into subsets that are "mutually exclusive (ME) and collectively exhaustive (CE)." Group many items under 2–4 top axes, place every item under at least one axis, and put anything that fits nowhere into an explicit residual (`기타` / "other") axis. Every subunit (cluster, theme, …) must appear in the roll-up (collectively exhaustive — no subunit dropped).

## Executive Summary structure (con.scr · con.so-what · con.bold-bullet · con.numeric-precision)

The intro craft that compresses a complex domain for a decision-maker. Resists deterministic measurement (judge=M, qualitative review); the source techniques shared by author and reviewer:

- **SCR** (con.scr) — develop the intro as Situation → Complication → Resolution (McKinsey). e.g. ✅ "Market share fell 8% year over year (Situation). A competitor entered at a 15% lower price (Complication). We respond by repositioning as premium (Resolution)." / ❌ "The market environment is difficult and improvement is needed" (Situation·Complication·Resolution undifferentiated)
- **So-what upfront** (con.so-what) — lead with the conclusion (the key implication), not a long description or preamble. e.g. ✅ "We can cut indirect costs by ₩2B per year — labor, supply waste, and process inefficiency are the drivers" (conclusion first) / ❌ "We analyzed three factors affecting profitability…" (description first)
- **Bold-bullet** (con.bold-bullet) — build metric runs as a bold key-claim heading + supporting bullets, so the scannable takeaway is the bold line (BCG executive-summary standard: lead with the "so what", evidence below). e.g. ✅ "**Market consolidation drives customer acquisition cost up 34% per year** — Q2 three-way merger shrinks the vendor pool / pressure on the procurement team's volume discounts" (bold conclusion + grounds) / ❌ "The market is changing / competitors are consolidating / customers want better prices" (flat bullets, no conclusion)
- **Numeric precision** (con.numeric-precision) — support claims with concrete numbers (amount·date·%·proper noun) instead of vague quantifiers. e.g. ✅ "Revenue grows 12% through Q3 2026, adding ₩4.5B" / ❌ "Revenue will rise significantly going forward" (abstract quantifier)
- **Numeric density** (con.numeric-density) — do not overpack a paragraph with numbers; isolate key numbers in bold-bullets so they are not buried (deterministic measurement — per-paragraph number-token ceiling, threshold injected by manifest).

How each technique maps to a specific page/section is defined by the `.claude/layers/` content-type guides.

## Sources

Each URL points to the relevant page as of the last verification.

- [How to Write an Executive Summary Like McKinsey — Slideworks](https://slideworks.io/resources/how-to-write-executive-summary) — SCR (Situation-Complication-Resolution)
- [Understanding BCG's Approach to Executive Summaries — Insight7](https://insight7.io/understanding-bcgs-approach-to-executive-summaries/) — Bold-bullet·So-what upfront
- [MECE principle — Wikipedia](https://en.wikipedia.org/wiki/MECE_principle) — Barbara Minto·McKinsey Pyramid Principle (Collectively Exhaustive)
- [The FIGs: Forrester, Gartner, IDC — Starsight](https://www.starsight.biz/2023/04/20/the-figs-who-are-the-biggest-analyst-firms/) — Forrester Landscape report structure
