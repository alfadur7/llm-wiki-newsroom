# Proposal Validation Batch Runbook

Instructions for measuring whether a guideline edit actually reduces defects, using verifier evidence, when the SoT self-evolution loop proposes one. Open this file and start with "perform proposal validation per these instructions." The acceptance rule and transition logging have their single SoT in [`../agents/editor-in-chief.md`](../agents/editor-in-chief.md) self-evolution workflow steps 6–7 — this file holds the *measurement procedure*, in **three variants by guideline type**:

| Guideline type | Variant | Sections |
|---|---|---|
| desk-judged content craft (layers prose·desk lenses·reporter/columnist authoring craft) | blind rewrite × blind desk | Held-in · Held-out · Desk Scoring below |
| behavioral guideline (procedure·routing·contract rules whose effect shows in agent behavior, not page prose) | probe task | § Variant — Behavioral Guideline |
| lint-scored rule (`criteria.json` judge:A·quantitative rubric·lint logic) | deterministic before/after | § Variant — Lint-Scored |

## When to Run

**Always before adoption** of a substantive change of one of the three types above — regardless of origin. It fires not only in an evolve session (editor-in-chief stage 1 proposal) but equally for a strengthening the desk surfaces mid-cycle or a self-proposal, as a self-harness reflex without an explicit instruction (editing `.claude/layers/*.md`·`agents/{desk,reporter,columnist}.md` triggers the `dispatch.py` proposal-validation advisory as a file-event reminder; behavioral/lint-scored surfaces are classified by the ladder's blind-review rung, not by file event). The held-in target is the defect pages where that mechanism manifested, drawn from the corpus (`tools/_defect-log.jsonl`, written locally by `tools/log_defect.py`). The exception is § Out of Scope (typo·slimming·structural/editorial·cross-reference fixes — no measurement obligation).

## Measure Without Editing the File (injection variants)

For the desk-judged and behavioral variants, do not modify the guideline file during measurement — separate the conditions by **injecting the Control (current passage) and Treatment (proposed strengthening) text into the agent prompt** instead. Edit the file only after adoption is confirmed (this avoids SoT contamination and re-diagnosis confusion mid-measurement). The lint-scored variant is exempt — a deterministic revert is exact, so direct edit + before/after runs are fine.

## Held-in — Blind Re-author

A held-in defect page is already ADAPT-complete, so measuring its current state is a null signal. **Re-author it blind from raw** to see the guideline's *preventive* effect:

- For each target, two agents (reporter or columnist) — one with the Control prompt, one with the Treatment prompt. **Reading the current page file is forbidden** (blind); restrict the GROUND sources to the core source(s) that caused the original defect (preserving the defect-reproduction conditions).
- Same authoring task, same sources, **only the guideline block differs** (removes confounding variables).
- Recover the produced stub as text; do not write it to a file.
- **Generalization sampling** (auditable·anti-cherry-pick): beyond the proposal's motivating target, sample **one** already-treated defect of the same mechanism to see whether the effect generalizes to its kind. "Same mechanism" is judged semantically from the shared `cluster` slug·the free-text `mechanism` label (not forced by a single `caught_at` code — one cluster is logged under several codes). Log **which defect, why it was judged the same kind, and the candidate-pool size** in the transition so the human gate can audit it (prefer a defect not sampled in the previous transition where possible).
- **Sparse corpus**: if there are no already-treated defects of that mechanism, proceed with the motivating target alone + leave generalization unverified (downgrade adoption confidence)·note `held_in_sampled:[]` in the transition.

## Held-out — Canary

On top of the fixed set of that content type in `tools/regression_set.json` (not used as the proposal's motivation — anti-gaming), **sample 2 stable pages** of the edit type (allocation: held-in 1 + held-out 2 = a load cap of 3). The population = lint PASS ∧ outside the fixed set ∧ not the motivation (the churn·staleness predicates are vacuous/non-deterministic for the source type, so they go unused — stability is reinforced by lint PASS·the fixed-set split·the human gate). Pick the 2 so they **include the structure in which the measured mechanism manifests** (e.g. for concept-as-claimant, ≥1 normal concept-fallback page — a mechanism-blind sample can't catch over-fire). If the population < 2, take all that are available. Instead of a deterministic selection algorithm, log the **sampling rule·population (candidate-pool) size·selected pages·selection rationale·1–2 examples of un-selected borderline candidates** in the transition `held_out_sampled` so the human gate can audit cherry-picking·representativeness (prefer pages not sampled in the previous transition where possible). Put both the fixed set and the samples through the desk under both Control·Treatment conditions to check for **over-fire** (mis-flagging normal content) — 0 is the expected value, but measure against the Control baseline (do not drop the Control on the assumption that the expected value is 0).

## Desk Scoring — Blind, N≥2

A desk agent scores the held-in and held-out outputs:

- **Blind labels** (Stub-A/B, etc. — the judge does not know which is Control/Treatment) and the **same prompt per condition**.
- **State the defect taxonomy** limited to the measured mechanism and forbid counting anything else (prevents signal dilution). The desk Reads the GROUND sources directly and compares item by item.
- The desk is probabilistic, so **aggregate N≥2 per target**. Return integer counts + severity.
- **Fresh-sample load cap**: desk-judged fresh samples = held-in 1 + held-out 2 = a fixed total of 3 (the motivating target is outside the cap·separate), so the desk's N≥2 multiplier does not hollow out the gate. The lint-scored path has no cap (deterministic lint, measured once).

## Variant — Behavioral Guideline (Probe Task)

For a rule whose effect shows in **agent behavior** (a routing step, a hand-over contract, a gate ordering), a page rewrite measures nothing — reproduce the behavior instead:

- **Probe task**: reconstruct the failure scenario that motivated the rule (the task where the old behavior went wrong) and run it once under the Control prompt and once under the Treatment prompt — injection, not file edits, same as the desk-judged variant.
- **Adjacent-normal held-out**: run one adjacent task where the OLD behavior was already correct, under both conditions — catches a rule that fixes the failure by over-firing on normal flow.
- **Blind judging, N≥2**: judges receive the two transcripts under blind labels and a verdict taxonomy limited to the measured behavior (did the failure reproduce? did the normal flow regress?). Aggregate as with desk scoring.
- Acceptance: the step 6 rule, with "defect count" read as "failure reproductions."

## Variant — Lint-Scored (Deterministic)

For a rule `lint.py` scores (a `criteria.json` judge:A threshold, a quantitative rubric line, lint logic itself), the verifier is deterministic — no injection, no blind desk:

- Run the affected lint group over held-in (motivating + fresh same-mechanism) and held-out (fixed set + fresh stable samples) **before and after the edit** — the file may be edited directly here, since a revert is exact.
- Measured once (same input → same output); over-fire on held-out = any stable page newly FAILing.
- Acceptance: the step 6 rule, applied to the deterministic score deltas.

## Tally & Accept

Tally the average defect count for Control vs Treatment per target. **The acceptance rule's SoT is editor-in-chief step 6** — **≥1 improvement on the motivating held-in** ∧ **non-regression** across every slice (motivating·fresh held-in·fixed/fresh held-out) ∧ no page going PASS→FAIL·over-fire. The fresh samples count only as non-regression guards (the improvement verdict is judged on the motivating target). On acceptance, edit the guideline file → [`../agents/editor-in-chief.md`](../agents/editor-in-chief.md) § Guideline Verification Ladder → record `log_defect` `kind:transition` (surface · held-in/out delta · decision) per step 7.

## Pitfalls

- **Measuring the fixed target**: re-measuring held-in against the current file converges to 0 (null signal) — always re-author blind from raw.
- **Confounding variables**: if sources or the task differ between Control/Treatment, the guideline effect can't be isolated — vary only the guideline block.
- **Taxonomy leakage**: counting defects outside the measured mechanism buries the signal — limit the count scope in the desk prompt.
- **Injection residue in agent replies**: if a tool result carries follow-up instructions outside the task, void it as experiment data (tally only controlled output).
- **Over-trusting a single target**: a one-target signal is a pilot — base the adoption decision on multiple targets plus the held-out check.
- **Fixed-set overfit**: measuring only against the fixed set·the single motivating target repeatedly tilts the guidance toward passing that set (eval rot) — add a fresh sample each cycle (prefer un-sampled·include the manifesting structure·audit-logged) to test generalization.

## Out of Scope

- Typo·slimming·structural/editorial·cross-reference fixes, routing/gate wording with no behavioral change: no measurement obligation (the ladder's blind-review rung classifies these invariant).
- Unattended self-adoption: the qualitative scoring and operator gate are required before adoption — only the measurement is batched; adoption keeps the gate.

## SoT

- Acceptance rule · held-in/held-out definitions · transition logging: [`../agents/editor-in-chief.md`](../agents/editor-in-chief.md) self-evolution workflow steps 6–7.
- Held-out fixed set: `tools/regression_set.json` (human-edited).
- Roles and cycle: [`../agents/README.md`](../agents/README.md) + the per-content-type [`../layers/`](../layers/).
