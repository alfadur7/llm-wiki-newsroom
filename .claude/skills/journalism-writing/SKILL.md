---
name: journalism-writing
description: Journalism and argumentation writing craft — inverted pyramid, lede, nut graph, kicker, explainer framing, PAGE frames, Toulmin argument (claim/rebuttal/qualifier), Hegelian dialectic, BBC due impartiality. Use when writing or reviewing news/explainer pieces, landscape overviews, or issue analyses that fairly juxtapose opposing views, or when a strong lede, sound argument structure, or balanced conclusion is needed.
---

# journalism-writing

Writing craft drawn from news/explanatory journalism and argumentation traditions — narrative lead (Lede→Nut graph→Kicker), dialectical structure (thesis·antithesis·synthesis), argument quality (Toulmin), and fairness (BBC due impartiality). `criteria.json` is the SoT for each criterion's definition, comparator, and source. The shared parsing and wiki-global state that the deterministic checks (judge=A) rely on are injected by the orchestrator (the skill is content-type-agnostic). Examples are illustrative of the target English prose.

## Dialectic structure (jrn.thesis-antithesis · jrn.c-section-size · jrn.c-stance-naming · jrn.monitoring-balance)

Develop an issue as Hegelian thesis → antithesis → synthesis. State thesis and antithesis with explicit **Position A / Position B** bold labels (ko rendering: **A 입장 / B 입장**); add a **C — Mediation** label (ko: **C 중재**) only when a genuine convergence exists. The C paragraph must not run longer than A or B, so the convergence is not mistaken for the main clash. If C is not a synthesis but a meta-critique (weakening both sides at once, flagging interest bias), move it out of the dialectic frame — a meta-critique in the C slot breaks the three-part structure.

Synthesis does not pick a winner. In Hegel's terms it *sublates* — cancels and preserves — identifying what each side correctly grasps. Concretely, place each side's **monitoring point** (what one would observe if that side were right) symmetrically (jrn.monitoring-balance); a monitor skewed to one side hides an editorial verdict under hedged wording (combine with BBC due impartiality). e.g. ✅ "If tighter regulation is right, we would observe reduced consumer harm; if looser regulation is right, increased new entry" (winning conditions symmetric on both sides) / ❌ "Regulation blocks innovation, so abolishing it is right" (one-sided verdict).

## Argument quality (jrn.toulmin-claim · jrn.rebuttal · jrn.qualifier)

Check each side's support structure with the Toulmin model (claim · grounds/data · warrant · qualifier · rebuttal · backing).

- **Claim-Warrant** (jrn.toulmin-claim) — every side pairs its claim with the grounds (data) that support it; no side asserts a claim with no grounds. e.g. ✅ "Regulation slows innovation — the grounds: new licensing waits average 18 months" (claim + grounds) / ❌ "Regulation slows innovation" (ungrounded assertion)
- **Rebuttal acknowledgment** (jrn.rebuttal) — concede a real weakness for each side, grounded in one of: (i) a limit the side itself admits, (ii) an internal contradiction in its logic, (iii) a design limit of its evidence (sample/timing/method). Re-citing the opposing side's evidence is NOT a rebuttal — it merely repeats the clash and loses the Toulmin value of a flaw seen from within the side. No side may be left perfectly defended. e.g. ✅ "However, this measurement is a first-generation adoption sample, so whether the same result holds at maturity is untested" (a design limit of one's own side) / ❌ "The opposing side also has many failure cases" (re-citing the opponent's evidence — not a rebuttal)
- **Qualifier** (jrn.qualifier) — every claim holds only conditionally; include at least one scope qualifier ("in the short term"·"on this metric"·"within 5 years"·"under this study design") so the claim is not over-generalized.

## Fairness (jrn.due-impartiality)

When aggregating many topics/sides into one piece, keep length and references from skewing to one side — BBC due impartiality is proportionate to weight, not a mechanical 50:50, and privileges no side. The deterministic check signals via a max/min reference-ratio ceiling (default 3.0, see criteria.json), but a hub that is intrinsically more referenced can be normal, so human review accompanies it.

## Narrative lead (jrn.lede · jrn.nutgraf · jrn.kicker · jrn.page · jrn.explainer · jrn.inverted-pyramid)

News/explanatory journalism front-loads the point and descends into detail — in the inverted pyramid, "the most important information (or what might even be considered the conclusion) is presented first." These resist deterministic measurement (judge=M, qualitative review); the source techniques shared by author and reviewer:

- **Lede** (jrn.lede) — open with the concrete conclusion (specific numbers/proper nouns), not an abstract summary ("so-what upfront"); compress into 2–4 sentences rather than one overloaded sentence. e.g. ✅ "Flexible work raised team productivity 30% — the result of a six-month study of work arrangements" / ❌ "Many factors affect productivity, and the analysis found scheduling mattered" (abstract intro)
- **Nut graph** (jrn.nutgraf) — the paragraph after the lede that states why the story matters, with 4W1H (scope·time·who·why). e.g. ✅ "This decision splits the field of three camps that have competed for three years — who rises and who is eliminated is decided here" (why it matters) / ❌ "The event was held yesterday with many participants" (facts only, no so-what)
- **Kicker** (jrn.kicker) — close the intro with a forward-looking sentence that signals the tension to track. e.g. ✅ "Whether next quarter's metrics will reverse this trend is the question" / ❌ "Various things followed afterward" (no direction)
- **PAGE framing** (jrn.page) — frame an issue across Problem → Analyze cause → Gauge responsibility → Examine solutions, covering at least 2 of the 4 per axis to avoid one-dimensional reporting. e.g. ✅ frame a cost increase along two axes, "market-structure cause (Analyze) + policy-intervention responsibility (Gauge responsibility)" / ❌ "costs rose" — a single-angle account
- **Explainer** (jrn.explainer) — compose body units that answer How/Why (greater context to understand a complicated topic), not a bare list of facts (Vox-style). e.g. ✅ "Why this bill was needed now and how it affects ordinary users" (How·Why) / ❌ "Congress passed the bill 52 votes" (fact listing)
- **Inverted pyramid** (jrn.inverted-pyramid) — order lists/sections by descending importance, most important metric first. e.g. ✅ put "share up 30%" at the front, with background·methodology after / ❌ start with background·methodology and put the conclusion at the very end

How each technique maps to a specific page/section/paragraph is defined by the `.claude/layers/` content-type guides.

## Beat reporting framing (judge=M — beat reporting · stakeholder map)

Follow beat-reporting practice: an overview is not a one-off article but the product of sustained, cumulative coverage of a field. Present the actors not as a flat list but grouped by role (principal · partner · regulator — a stakeholder map). Resists deterministic measurement; judged qualitatively.

## Sources

Each URL points to the relevant page as of the last verification.

- [Inverted Pyramid — Nielsen Norman Group](https://www.nngroup.com/articles/inverted-pyramid/) — inverted pyramid·readability
- [Nut graph — Wikipedia](https://en.wikipedia.org/wiki/Nut_graph) · [Nailing the Nut Graf — The Open Notebook](https://www.theopennotebook.com/2014/04/29/nailing-the-nut-graf/) · [Nieman Storyboard](https://niemanstoryboard.org/2021/10/26/nut-grafs-seven-steps-to-score-a-winning-story-structure/) — Lede→Nut graph→Kicker
- [The Power of News Frames (PAGE model) — Project Censored](https://www.projectcensored.org/the-power-of-news-frames/) — four-stage framing
- [Explanatory journalism — Wikipedia](https://en.wikipedia.org/wiki/Explanatory_journalism) — explainer (Vox)
- [Beat reporting — Wikipedia](https://en.wikipedia.org/wiki/Beat_reporting) — beat reporting·stakeholder map
- [Toulmin Argument — Purdue OWL](https://owl.purdue.edu/owl/general_writing/academic_writing/historical_perspectives_on_argumentation/toulmin_argument.html) — Claim·Data·Warrant·Rebuttal·Qualifier
- [Hegel's Dialectics — Stanford Encyclopedia of Philosophy](https://plato.stanford.edu/entries/hegel-dialectics/) — thesis·antithesis·synthesis three-part structure
- [Rethinking balance and impartiality in journalism — PMC (BBC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5732589/) — due impartiality
