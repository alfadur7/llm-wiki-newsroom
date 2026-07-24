---
layout: default
title: "The Knowledge Factory: Agents Write the Wiki, Humans Design the Newsroom"
permalink: /knowledge-factory/
description: >-
  The software factory's three loops, plus a fourth that knowledge work needs.
article_schema: true
schema_inlanguage: en
schema_url: "https://alfadur7.github.io/llm-wiki-newsroom/knowledge-factory/"
schema_keywords: "knowledge factory, harness engineering, software factory, inner loop, outer loop, meta loop, reground loop, four loops, agentic workflow, AI agent harness, LLM wiki, Karpathy LLM Wiki, writer reviewer separation, context isolation, self-evolving guidelines, human in the loop, knowledge staleness, Claude Code, multi-agent"
hreflang_en: "https://alfadur7.github.io/llm-wiki-newsroom/knowledge-factory/"
hreflang_ko: "https://alfadur7.github.io/llm-wiki-newsroom/ko/knowledge-factory/"
---

<style>
.kf-fig { margin: 1.7rem 0; }
.kf-fig .kf-cap { margin: .7rem 0 0; font-size: .85rem; color: #8b949e; text-align: center; }
.kf-flow { display: flex; flex-wrap: wrap; align-items: stretch; justify-content: center; gap: .5rem; }
.kf-node { flex: 1 1 11rem; min-width: 9rem; border: 1px solid #30363d; border-radius: 6px;
           background: #161b22; padding: .75rem .8rem; text-align: center; }
.kf-node b { display: block; color: #e6edf3; font-size: .95rem; }
.kf-node span { display: block; margin-top: .25rem; font-size: .8rem; color: #8b949e; }
.kf-node-core { border-color: #58a6ff; }
.kf-arrow { display: flex; align-items: center; justify-content: center; color: #58a6ff; font-size: .9rem; }
.kf-loop { border: 1px solid; border-radius: 8px; padding: .85rem; }
.kf-meta  { border-color: #58a6ff; background: rgba(88,166,255,.06); }
.kf-outer { border-color: #3fb950; background: rgba(63,185,80,.06); margin-top: .75rem; }
.kf-inner { border-color: #d29922; background: rgba(210,153,34,.06); margin-top: .75rem; }
.kf-reground { border: 1px dashed #bc8cff; border-radius: 8px; padding: .85rem;
               margin-top: .35rem; background: rgba(188,140,255,.06); }
.kf-feedback { text-align: center; color: #bc8cff; font-size: 1.15rem; line-height: 1; margin-top: .5rem; }
.kf-tag { font-weight: 700; color: #e6edf3; font-size: .92rem; margin-right: .45rem; }
.kf-desc { font-size: .85rem; color: #8b949e; }
@media (max-width: 520px) {
  .kf-flow { flex-direction: column; }
  .kf-arrow { transform: rotate(90deg); }
  .kf-desc { display: block; margin-top: .3rem; }
  .kf-loop, .kf-reground { padding: .7rem; }
}
</style>

*Read this in [한국어]({{ '/ko/knowledge-factory/' | relative_url }}).*

"Software factory" has become one of the more useful phrases in this wave of AI-assisted development. The premise: AI agents write essentially all of the shipped code, and developers stop building features by hand and start building — and improving — the system that produces them. [Dru Knox](https://www.youtube.com/watch?v=D_cw-k0F1DM&t=2400) of Tessl, an AI developer-tooling company, gave the discipline a name: **harness engineering**. The harness is everything that steers and drives the agent, the way a harness steers a horse, and at the center of it sit three loops.

This article asks the same question of knowledge work. What should the factory look like when the product isn't source code but a wiki of cross-linked pages? The short answer is that all three loops transfer cleanly. But knowledge has one property code doesn't: it keeps decaying after you ship it. That gap needs a fourth loop. What follows defines that four-loop production system as a **knowledge factory**, then works top-down from the concept to a running implementation: [LLM Wiki Newsroom](https://github.com/alfadur7/llm-wiki-newsroom), an open-source framework where a five-role crew of [Claude Code](https://www.anthropic.com/claude-code) agents turns a folder of documents into a cross-linked markdown wiki.

## Key takeaways

- **The shift.** In a knowledge factory, agents write every wiki page and the human designs and runs the newsroom that produces them. The operator never writes an article; they maintain the authoring guidelines and the automated review machinery.
- **Three axes of maturity.** Autonomy (does a page finish without human intervention?), automation (how much ships without human review?), and quality (how good the resulting knowledge is). What connects the three is trust.
- **Four loops build that trust.**
  - Inner loop: self-checks that run while a draft is being written
  - Outer loop: a two-gate review right before publication
  - Meta loop: turning repeat mistakes into permanent rules
  - Reground loop: re-verifying and rewriting knowledge that has gone stale
- **Human-in-the-loop by checklist, not by gut feeling.** The situations that require operator approval are enumerated rather than judged case by case.
- **Stated limits.** What the deterministic checks can't reach, follow-up items that never close, review history spread across several files, and the fact that the design's advantage is still a hypothesis under test.

## 1. What a knowledge factory is

The "factory" part is literal. Agents produce the output — the wiki pages themselves — and the human builds the plant that produces them.

The finished product is a wiki of cross-linked markdown pages: source pages summarizing each original document, entity and concept pages, hub pages and timelines that tie related threads together, contradiction pages recording where sources disagree, and synthesis pages that draw the whole picture. Not one of them is written by hand. The operator does exactly two things: feed in source documents, and improve the factory.

<div class="kf-fig">
  <div class="kf-flow">
    <div class="kf-node"><b>Source documents in</b><span>articles · notes · PDFs</span></div>
    <div class="kf-arrow" aria-hidden="true">▶</div>
    <div class="kf-node kf-node-core"><b>Knowledge factory</b><span>five agent roles + Python checks</span></div>
    <div class="kf-arrow" aria-hidden="true">▶</div>
    <div class="kf-node"><b>Markdown wiki</b><span>cross-linked pages</span></div>
  </div>
  <p class="kf-cap">The operator writes nothing inside this flow — they build and improve the factory in the middle.</p>
</div>

The shop floor is modeled on a newspaper newsroom, with five roles:

1. **Reporter** — gathers external material and writes source pages.
2. **Columnist** — synthesizes across many sources into deep analysis pages.
3. **Copy Editor** — verifies drafts mechanically against fixed rules.
4. **Desk** — re-reads the finished draft for logic and flow the way a section editor would, before anything publishes.
5. **Editor-in-Chief** — the orchestrator that routes work, assigns it to the right role, and gates publication.

The important part is that these five are not five models exercising judgment. The Copy Editor isn't an LLM at all; it's rule-based Python. The Editor-in-Chief is orchestration, not evaluation. **The Desk holds the only independent evaluative judgment in the system.** Designing the factory well isn't a matter of adding more agents — it's deciding where judgment belongs and, just as deliberately, where it doesn't.

> **Note:** this project wasn't designed from the software factory playbook. It started as an implementation of the [LLM Wiki idea Andrej Karpathy sketched](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), and the structure fell out of working through a single question: how far can you trust knowledge an AI wrote? Two designs converging is suggestive — it hints that an autonomous production system needs roughly this skeleton — but it's two data points, not a proven answer.

## 2. Three axes of maturity, and trust

Applying the software factory's maturity measures to knowledge production gives three axes.

- **Autonomy.** How far a page gets without human intervention. Feed in one document and the question is whether the agent can carry it all the way — writing the source page, updating the ten or so related pages it touches, extracting new concepts — without someone stepping in to redirect it.
- **Automation.** How much is allowed to publish without a human reviewing it first. It sounds like autonomy but it's a separate axis. An agent can land good work unaided (high autonomy) while the operator still reads every page before it ships (low automation). What closes that gap is **trust**.
- **Quality.** The most familiar axis: check pass rates, defects the Desk catches, how often pages contradict each other.

The order matters. Establish autonomy first, widen the automated zone only as far as trust has actually accumulated, and hold quality steady while you do. And the mechanism that earns that trust is the loop.

## 3. The four loops

The first three loops nest inside one another. Only the fourth sits outside, pushing already-published pages back in.

<div class="kf-fig">
  <div class="kf-loop kf-meta">
    <span class="kf-tag">Meta loop</span><span class="kf-desc">promotes errors that recur in the two inner loops into rules</span>
    <div class="kf-loop kf-outer">
      <span class="kf-tag">Outer loop</span><span class="kf-desc">at publication · Gate 1 Copy Editor (rules) → Gate 2 Desk (AI)</span>
      <div class="kf-loop kf-inner">
        <span class="kf-tag">Inner loop</span><span class="kf-desc">self-checks running throughout drafting</span>
      </div>
    </div>
  </div>
  <div class="kf-feedback" aria-hidden="true">↑</div>
  <div class="kf-reground">
    <span class="kf-tag">Reground loop</span><span class="kf-desc">stale published pages are fed back in as new input</span>
  </div>
</div>

### 3-1. Inner loop: checking your own work as you go

The inner loop is everything an agent runs on itself while drafting, before submitting anything. It has to be fast and cheap, because it runs constantly. The better it gets, the more often the agent lands on the right answer without anyone stepping in — which is to say, improving the inner loop is how you raise **autonomy**.

- **Standards on entry.** Reporter and Columnist agents load the format and authoring standard for the page type they're about to write, plus five authoring skills — packaged instruction modules the agent pulls in on demand — covering journalism, consulting-report structure, encyclopedic neutrality, citation discipline, and guideline writing.
- **Self-verification.** Each skill ships with its criteria and its check code, so the agent measures itself against the same yardstick the review stage will use later. While drafting it runs the Python checker (`tools/lint.py`) scoped to just its own output. If the same error survives two attempts, it hands off rather than grinding — the inner loop is only worth having while it stays fast.

### 3-2. Outer loop: two gates before publication

The outer loop is the heavier, slower pass that runs once a draft is done, at the publication boundary. In software terms it maps to pull-request review and the CI pipeline. Here it's built as **two gates**.

| Gate | Owner | What it does |
|---|---|---|
| Gate 1 | Copy Editor (rule-based) | Python (`tools/lint.py`) runs deterministic checks across ten groups — links, citations, page structure, cross-page conflicts, and more. Pass or fail is unambiguous, and the result is written to a report. |
| Gate 2 | Desk (AI) | Reads the draft through six lenses — bias, information density, repetition, argument quality, narrative flow, and fine readability — with fresh eyes. Returns a defect list; it never edits the page itself. |

This is the same two-layer shape as the software factory's **Verifier** and **Change Review**. A verifier is a narrow, binary check that runs every single time — Knox's example is "does this JSX element have an ARIA attribute?" — while change review is a general agent pass that reads the diff through several lenses looking for whatever nobody anticipated. Gate 1 is the verifier layer, Gate 2 is change review: the Copy Editor stops known mistakes from recurring, and the Desk catches the quality problems nobody has written a rule for yet.

One design choice does most of the work here. **The Desk receives the finished draft and the rubric — never the writer's reasoning about why it was written that way.** Reviewing your own work inside the same context makes you generous with yourself, so the fix is to cut the information off entirely. The real lever in this system isn't how many agents are running; it's that isolation. Drafts that fail either gate go back to their author; three rejections for the same cause halt automatic progress and hand the decision to the operator.

### 3-3. Meta loop: every mistake happens only once

The meta loop wraps both loops below it, watches how they perform, and then improves the system itself. The rule it follows: don't teach an agent the same thing twice — once you've said it, encode it somewhere as a rule.

- **A defect ledger.** Defects caught in review and corrections from the operator accumulate through a logging tool (`tools/log_defect.py`), and mining scripts trace the recurring failure patterns.
- **Proposals, then measurement.** When the same defect keeps surfacing, the system drafts an amendment to its own authoring guidelines. Each proposal goes through a **blind comparison — which draft came from the amended rule is hidden from the judge** — plus a test on held-out failures never used in validation before. It's adopted only if the score actually improves, and only with **the operator's final approval**. The loop proposes and measures; it never adopts on its own.
- **Hardening into code.** Recurring findings get promoted into a Python hook or a Gate 1 rule, which moves the problem out of the judgment layer and into the deterministic one. The point is to keep the Desk permanently pointed at problems nobody has seen before.

### 3-4. Reground loop: the fourth loop knowledge work needs

Once code is built and shipped, it stays put until the spec changes. **Knowledge doesn't. It drifts away from reality as the world moves.** So this system adds a loop the other three don't cover: published pages are fed back in as factory input. It's called **reground** — the wiki re-grounding its own claims in the evidence. Three triggers fire it, and all three are things newsrooms have always done.

- **Update** — an upstream source changed. The checker surfaces the stale page; a Columnist re-reads the sources and rewrites it. *(A follow-up story.)*
- **Follow-up** — one of our own claims carries an unresolved marker or a deadline that has now passed. The Desk re-adjudicates and the operator confirms. *(Circling back to a story you promised to follow.)*
- **Correction** — our own pages disagree with each other. The Desk re-reads a published cluster as a bundle, catching the mismatches that reading one page at a time can't reveal. *(A correction notice.)*

## 4. Control plane: keeping the trail legible

Improving a factory requires that every trace of its work be recorded somewhere the meta loop can actually read. The software factory calls this the **control plane**.

Here, the entire workflow lives in files inside the repository:

- the input queue
- the work log and review reports
- the defect ledger

Role definitions, per-type authoring standards, naming policy — every operating rule is a committed file, and **configuration that exists only on someone's machine is ruled out on purpose**. An improvement has to land somewhere durable for the next one to build on.

## 5. Human-in-the-loop: standardizing approval

Leave the boundary of automation to intuition and it fails in one of two directions: a human becomes a bottleneck on work that never needed them, or **high-risk work slips through unchecked**. So the conditions requiring human approval are written down as an explicit list.

**Seven situations that require operator approval**

1. A third consecutive review failure for the same cause
2. Creating a new topic-cluster category
3. Creating a new entity or concept page once its citation count passes a set threshold
4. Publishing the top-level synthesis that spans the whole wiki
5. Changing the skeleton of an authoring guideline or evaluation rubric
6. Committing and pushing to the repository — the step that makes results public
7. Rewriting more than 50% of an existing page

Today the factory runs at **high autonomy with deliberately restrained automation**: agents finish pages on their own, but the last hand on publication and on rule changes is still human. That's the stable way through the transition, and the list above is the map: as trust is demonstrated, the constraints come off one line at a time.

## 6. Limits and open work

For transparency, the structural limits as they currently stand:

- **What rule checks can't reach.** Gate 1 is pure Python with no AI calls at all. That makes it cheap and fast enough to run on everything, but any check that requires reading for meaning and intent can't be automated there, so it falls to the Desk. That makes the Desk's load wider here than in Knox's version, where the verifier layer is itself LLM-driven.
- **Follow-up items that never close.** There's no procedure yet for marking a surfaced follow-up as resolved, so once an item is flagged it comes back on every run. The plan is to build an adjudication ledger once items actually start accumulating.
- **Review history is scattered.** Unlike a pull request, where every review comment stays attached to one object, the history here is spread across the work log, the reports, and the defect ledger.
- **Still a hypothesis.** Whether the four loops and the separate qualitative review actually produce better knowledge is still under test, through blind comparisons and operational data. It's a design argument, not a measured result.

## Closing: what actually changes is the human role

The message at the center of the software factory story is that a developer's job shifts from writing code to designing the system that writes it. The knowledge factory is the same. The operator isn't the person writing the content; they're the architect of the newsroom that writes it.

Fixing a page by hand improves one page. Converting a defect the Desk keeps flagging into a rule improves **every page the system will ever produce**.

And the most valuable thing the knowledge factory takes from the software factory isn't throughput. It's the meta loop that stops a mistake from happening twice, and the reground loop that stops published knowledge from quietly rotting — **rules that improve themselves, and pages that rewrite themselves when they go stale**. That is what this factory is really built to produce.

---

*The software factory and its three loops come from Dru Knox's AI Engineer SF talk, carried in Tessl's video [Harness Engineering: The New Discipline of Agentic Dev](https://www.youtube.com/watch?v=D_cw-k0F1DM&t=2400) — his talk begins at 28:50 and lays out the three layers at 40:00; the loops are also walked through in the interview segment at 3:56. For the implementation this article describes, see the [README](https://github.com/alfadur7/llm-wiki-newsroom#readme) and the [overview]({{ '/' | relative_url }}).*
