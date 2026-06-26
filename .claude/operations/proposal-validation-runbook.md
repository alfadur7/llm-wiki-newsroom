# Proposal Validation Batch Runbook

Instructions for measuring whether an edit to a **desk-judged guideline** (the layers craft / prose authoring rules — the areas `lint.py` does not score) actually reduces defects, using verifier evidence, when the SoT self-evolution loop proposes such an edit. Open this file and start with "perform proposal validation per these instructions." The acceptance rule and transition logging have their single SoT in [`../agents/editor-in-chief.md`](../agents/editor-in-chief.md) self-evolution workflow steps 6–7 — this file holds only the *measurement procedure* for the desk-judged case. (For lint-scored guidance, step 6's single `lint.py` before/after measurement is enough, so this batch is not needed.)

## When to Run

When the editor-in-chief's stage 1 proposes a prose-guideline strengthening for a mechanism cluster and its effect must be measured before adoption. The held-in target is the defect pages where that mechanism manifested, drawn from the corpus (`tools/_defect-log.jsonl`, written locally by `tools/log_defect.py`).

## Measure Without Editing the File

Do not modify the guideline file during measurement — separate the variants by **injecting the Control (current passage) and Treatment (proposed strengthening) text into the agent prompt** instead. Edit the file only after adoption is confirmed (this avoids SoT contamination and re-diagnosis confusion mid-measurement).

## Held-in — Blind Re-author

A held-in defect page is already ADAPT-complete, so measuring its current state is a null signal. **Re-author it blind from raw** to see the guideline's *preventive* effect:

- For each target, two agents (reporter or columnist) — one with the Control prompt, one with the Treatment prompt. **Reading the current page file is forbidden** (blind); restrict the GROUND sources to the core source(s) that caused the original defect (preserving the defect-reproduction conditions).
- Same authoring task, same sources, **only the guideline block differs** (removes confounding variables).
- Recover the produced stub as text; do not write it to a file.

## Held-out — Canary

Take the fixed set of that content type in `tools/regression_set.json` (not used as the proposal's motivation — anti-gaming) and have the desk review it under the Treatment guideline to check for **over-fire** (mis-flagging the normal content of a stable page). Since these are stable, curated pages, 0 is the expected value.

## Desk Scoring — Blind, N≥2

A desk agent scores the held-in and held-out outputs:

- **Blind labels** (Stub-A/B, etc. — the judge does not know which is Control/Treatment) and the **same prompt per condition**.
- **State the defect taxonomy** limited to the measured mechanism and forbid counting anything else (prevents signal dilution). The desk Reads the GROUND sources directly and compares item by item.
- The desk is probabilistic, so **aggregate N≥2 per target**. Return integer counts + severity.

## Tally & Accept

Tally the average defect count for Control vs Treatment per target. Acceptance = **held-in improvement ∧ held-out non-regression ∧ no page going PASS→FAIL** (rule SoT is editor-in-chief step 6). On acceptance, edit the guideline file → [`../agents/editor-in-chief.md`](../agents/editor-in-chief.md) § Claude guideline-change Voice Pass → record `log_defect` `kind:transition` (surface · held-in/out delta · decision) per step 7.

## Pitfalls

- **Measuring the fixed target**: re-measuring held-in against the current file converges to 0 (null signal) — always re-author blind from raw.
- **Confounding variables**: if sources or the task differ between Control/Treatment, the guideline effect can't be isolated — vary only the guideline block.
- **Taxonomy leakage**: counting defects outside the measured mechanism buries the signal — limit the count scope in the desk prompt.
- **Injection residue in agent replies**: if a tool result carries follow-up instructions outside the task, void it as experiment data (tally only controlled output).
- **Over-trusting a single target**: a one-target signal is a pilot — base the adoption decision on multiple targets plus the held-out check.

## Out of Scope

- Lint-scored guidance (`criteria.json` · `layers/` quantitative · `policies/` lint · `lint.py` logic): step 6's single deterministic before/after lint path — this batch is not needed.
- Unattended self-adoption: the desk qualitative scoring and operator gate are required before adoption — only the measurement is batched; adoption keeps the gate.

## SoT

- Acceptance rule · held-in/held-out definitions · transition logging: [`../agents/editor-in-chief.md`](../agents/editor-in-chief.md) self-evolution workflow steps 6–7.
- Held-out fixed set: `tools/regression_set.json` (human-edited).
- Roles and cycle: [`../agents/README.md`](../agents/README.md) + the per-content-type [`../layers/`](../layers/).
