---
name: guideline-writing
description: Guideline-authoring craft for instruction SoTs (.claude/ guides, CLAUDE.md, plan files) — operative rules vs recital, MUST/SHOULD/MAY force tiers, pruning, bloat control, blind review protocol, deliberation-narrative ban. Use when writing, editing, or reviewing an agent instruction file, policy, runbook, command SoT, or plan file, or when a guideline change needs a minimal-edit or blind review.
---

# Guideline Writing

Craft for authoring the instruction layer itself — the `.claude/` guide SoTs, `CLAUDE.md`, and plan files. Content pages have the four content-craft skills (jrn·con·enc·cit); this skill is their counterpart for the meta layer. Dotted IDs: `gdl.*` ([criteria.json](criteria.json)); the deterministic detectors live in [checks.py](checks.py) and run inside `python tools/lint.py meta`.

## Operative Rule vs Recital

Every sentence in a guideline is one of two kinds, and only the first belongs in the body:

- **Operative rule** — tells the reader what to do, when, and how to tell they did it right. Test: delete the sentence; if an executor could now act differently and still believe they complied, the sentence was operative.
- **Recital** — explains how the rule came to be: options weighed, benchmarks absorbed, incidents survived, dates adopted. Recitals are history; history's SoT is `log.md` (append-only). A recital in the body is **deliberation narrative** — the central antipattern this skill exists to prevent.

A failure mode earns **at most one line in the body** — the concrete trigger the rule guards against, stated as a present-tense condition ("a partial edit bumps only the date and masks body staleness"), never as a war story ("after the 05-20 incident we decided…"). The story goes to `log.md`.

## Force Tiers — MUST / SHOULD / MAY

State every rule at exactly one force tier, and make the tier visible in the wording:

| Tier | Wording | Reader's obligation | Verification |
|---|---|---|---|
| **MUST** | "is mandatory" · "never" · imperative | no discretion; violating it is a defect | lint-gate or blocking hook where possible |
| **SHOULD** | "by default" · "prefer" · "unless" | may deviate with a stated reason | advisory hook · review lens |
| **MAY** | "can" · "optionally" | pure permission | none |

Antipattern: hedged MUSTs ("should generally always…") and decorated MAYs ("it is strongly recommended to consider…"). If you cannot pick the tier, you have not finished deciding the rule — finish deciding before writing.

## Pruning

A guideline corpus only stays executable if rules leave at the same rate reality invalidates them:

- **Prune-or-enforce**: a rule that is neither checked (lint·hook·review lens) nor followed is dead weight — either wire an enforcement surface or delete it. Keeping it "as documentation" is the recital antipattern wearing a rule's clothes.
- **Deprecation signal**: a detector or lens with 0 surfacings across 5 consecutive batches is a deletion candidate (mirrors the desk promotion loop's burn criteria).
- **Delete whole units**: prune at the bullet/section level, not by shaving words — a half-pruned rule reads as a weaker rule, not a shorter one.

## Bloat Control

Absorb into an existing section, table, or matrix by default; create something new only after proving no matching pattern exists.

**5-step self-check** (mandatory just before finishing a guideline or plan edit):
1. New section/table/matrix vs a one-line absorption into an existing section — absorb by default
2. Zero copies of another SoT's table/matrix — replace with a cross-reference
3. Zero new Risk/invariant/caveat sections by default — prefer attaching a qualifier to an existing section
4. When the changed lines ≥ 50, a mandatory minimum-edit re-review
5. Read the full context of each changed file before declaring the edit done

**4 red flags** (a single hit forces the 5-step re-review):
- ≥ 2 new sections added
- ≥ 50 changed lines
- a new table or matrix added
- the same information already exists in another SoT

**File naming (T1 prescriptive default)**: a new memory/policy/hook file takes an imperative form — `no_X` · `X_to_Y` · `X_not_Y`. Descriptive names (`*_voice` · `*_posture`) require two-step inference on recall and match utterance patterns weakly.

## Blind Review Protocol

A guideline edit is reviewed by a reader who did not write it and does not know the deliberation behind it:

1. **Input = the diff only** — no chat context, no rationale memo. The reviewer sees exactly what a future executor will see.
2. **Classification reply is mandatory**: the reviewer returns, per hunk, a two-way verdict — **substantive** (an executor would act differently after this change) or **invariant** (wording/structure only, behavior unchanged) — plus any defects found against this skill's criteria.
3. **Defect form**: criterion id (`gdl.*`) · location · one-sentence issue · one-sentence fix. Abstract criticism ("feels verbose") is not a defect.
4. **Self-containment probe**: the reviewer must be able to state what the rule obliges without opening another document; if they cannot, flag `gdl.self-contained`.

## Worked Examples

1. **Recital → operative** — ✗ "After comparing per-event shell hooks with a unified dispatcher, we consolidated to dispatch.py, which reduced JSON parses." ✓ "All Write|Edit hook logic lives in `dispatch.py`; add new advisories there, not as new shell hooks." (The comparison story goes to `log.md`.)
2. **Failure mode in one line** — ✗ a paragraph recounting how five byproduct stubs once skipped review and eleven defects surfaced. ✓ "Byproduct stubs get the same Desk VERIFY₂ — a flow that skips the stub-authoring entry point otherwise omits the gate."
3. **Force tier made visible** — ✗ "It is usually best to run the linter before handing off." ✓ "Run target-scope lint before hand-off (self-VERIFY₀); after 2 self-attempts on the same cause, hand off as-is."
4. **Absorb, don't add** — asked to document that contradiction pages need a per-theme drift block: ✗ a new "Drift Requirements" section in a second file. ✓ one row added to the existing per-target drift-block table in `wiki-lint.md`, other docs cross-reference it.
5. **Pointer, not restatement** — ✗ copying the open-source-AI license spectrum table from `overview.md` into a command SoT "for convenience." ✓ "License-spectrum definitions: see the cluster overview (single SoT)."

## Antipatterns

| # | Antipattern | Detection | Resolution |
|---|---|---|---|
| 1 | Decision option name in body ("Option E+") | `checks.py` (auto) | move to log.md |
| 2 | Reinforcement counter ("Reinforcement 2") | `checks.py` (auto) | remove from body |
| 3 | Introduction timestamp ("adopted 2026-05-10") | `checks.py` (auto) | move to log.md |
| 4 | Changelog/Change History section in a guide | `checks.py` (auto) | move to log.md |
| 5 | Recurrence-prevention narrative ("prevents a recurrence of…") | `checks.py` (auto) | one-line failure mode; story to log.md |
| 6 | External-precedent equivalence ("equivalent to the ProCon model") | project lint (`meta_schema`) | absorb the essence; drop the name |
| 7 | Benchmark absorption tally ("external benchmark 5/6") | project lint (`meta_schema`) | move to log.md |
| 8 | Table-row restatement paragraph | blind review (`gdl.sot-link-not-restate`) | keep the table; delete the prose |
| 9 | Rule stated as its own justification ("because this is important") | blind review (`gdl.rule-not-reason`) | state the trigger condition or nothing |
| 10 | Pointer-only rule ("see other doc" with no local obligation) | blind review (`gdl.reason-not-pointer`) | state the obligation locally, link for depth |
| 11 | Unreasoned exception ("except X" with no condition) | blind review (`gdl.exception-reasoned`) | attach the condition that licenses the exception |
| 12 | Unverified universal claim ("always fails", "never fires") | blind review (`gdl.universal-claim-verified`) | verify, qualify, or delete |
| 13 | Hedged force tier ("should generally always") | blind review (`gdl.normative-restraint`) | pick MUST/SHOULD/MAY |
| 14 | Dead rule kept as documentation | review (`gdl.prune-or-enforce`) | wire enforcement or delete |
| 15 | New section where absorption fits | review (`gdl.absorb-before-adding`) | fold into the existing section |

## Sources

- [RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels](https://www.rfc-editor.org/rfc/rfc2119) — the MUST/SHOULD/MAY force tiers.
- [Plain language act & operative clauses — U.S. Federal Plain Language Guidelines](https://www.plainlanguage.gov/guidelines/) — operative wording, one-obligation-per-sentence.
- [Recitals vs operative provisions — EU legislative drafting guide](https://eur-lex.europa.eu/content/techleg/EN-legislative-drafting-guide.pdf) — recitals carry motive and are non-binding; operative articles carry obligations.
- [Fresh Eyes Editing — Harvard Writing Center](https://writingcenter.fas.harvard.edu/revising-draft) — review by a reader without the author's context (blind review).
