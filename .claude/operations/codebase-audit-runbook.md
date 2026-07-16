# Codebase Audit Runbook (multi-agent ultrareview)

A multi-agent batch procedure for an ultrareview-grade, exhaustive pass over the `tools/` Python code and the `.claude/` guidelines. The operator starts it with "do a full audit / ultrareview." It uses the Workflow tool (multi-agent orchestration), so operator opt-in is a prerequisite. The two variants (code / guidelines) share one harness and differ only in group decomposition, review dimensions, and the application policy.

## When to run

- When the operator requests a full code or guideline audit
- Right after a large refactor or structural change (to catch drift)
- Periodic review

## Variant A — Python code (tools/ + hooks + graph.html)

- **Group decomposition**: just before starting, enumerate `tools/**/*.py` + `.claude/hooks/**/*.{py,sh}` + `graph/graph.html` live into ~10–12 groups by submodule, ≤~8 files per group (a size one agent can fully read). No hardcoded list — files accumulate. Exclude vendored artifacts such as the obsidian plugin `main.js`.
- **Review dimensions**: `bug` (runtime errors · wrong conditions · None/KeyError · regex · resource leaks · encoding/path · broad-except masking) · `dead-code` (unused functions/constants/imports · unreachable branches · `_lib` duplication) · `inconsistency` (not using a `_lib` helper · hand-rolled frontmatter parsing · inconsistent exit/error handling) · `over-engineering` (needless abstraction · speculative generalization · single-impl interface/factory · config for values that never change · symptom-only non-root-cause fixes — criteria SoT `.claude/skills/ponytail-coding/SKILL.md` ladder; missing reuse belongs to `inconsistency`, so it's excluded here).
- **Application**: `fix_safe=true` (a code-variant field in FINDINGS_SCHEMA — see § Harness) is fixed directly. Verification is § Verify & gate protocol item 2 (code).

## Variant B — guidelines (.claude/ + CLAUDE.md + README + skill checks.py)

- **Group decomposition**: root (CLAUDE.md + root README.md) · agents · commands · layers · policies · operations · skills-spec (SKILL.md + criteria.json) · skills-code (checks.py).
- **Review dimensions**: `drift` (a symbol/field/CLI/output the doc describes doesn't match the actual code — confirm only after reading that code) · `contradiction` (the same rule/threshold/procedure conflicts across or within files — one policy's threshold/instruction disagrees with another guide or is mutually exclusive; confirm only after reading both originals; intentional reproducibility duplication and SoT-delegation pointers are excluded) · `duplication` (intentional reproducibility duplication is excluded, per the dedupe policy) · `stale` (removed features · dead cross-links) · `misplacement` (violates the CLAUDE.md "Instruction Locations" taxonomy) · `code-bug` (checks.py).
- **Drift grounding is required**: inject the list of recent code changes into the reviewer prompt to catch code↔doc drift.
- **Contradiction grounding is required**: per-group isolated review can't see cross-file conflicts — inject the cross-cutting registries where thresholds/policies converge (`.claude/layers/_manifest.json` roster · `.claude/policies/naming.md` thresholds · `graph/cluster_labels.json`) into the reviewer prompt so it checks a group's rules against those values.
- **Exclude what lint already covers**: do not re-report what `python tools/lint.py meta` already catches (CLAUDE.md anchor/file-ref/slash-cmd/roster · voice antipattern · hook format · craft-chain closure · stale guide ref · log ordering) — the multi-agent pass owns the semantic layer lint can't reach.
- **Application**: mechanical (stale ref · counts · scope · field names · dead code) is fixed directly. **Gated** (changes to a guide/rubric/matrix skeleton — Human Reviewer Gate) is not applied; surface it to the operator.

## Harness (Workflow)

Common to both variants. `pipeline(GROUPS, review → adversarial verify)` — one reviewer reads each group and returns schema-bound findings, then a separate verifier re-checks each finding default-reject (re-reading the actual code, re-classifying). The verify stage filters false positives (e.g. write_text package conventions, intentional local regexes).

```js
// Common skeleton — only GROUPS, the review/verify prompts, and the schema's fix classification swap per variant
const verified = await pipeline(
  GROUPS,
  (g) => agent(reviewPrompt(g), { phase: 'Review', schema: FINDINGS_SCHEMA }),
  (review, g) => parallel((review.findings || []).map((f) => () =>
    agent(verifyPrompt(f), { phase: 'Verify', schema: VERDICT_SCHEMA })
      .then((v) => ({ group: g.key, finding: f, verdict: v })))),
)
const confirmed = verified.flat().filter(Boolean).filter((r) => r.verdict && r.verdict.real)
```

- **FINDINGS_SCHEMA**: `{file, line, category, severity, confidence, title, detail, proposed_fix}` (the code variant adds `fix_safe: bool` — whether a direct fix is safe; the guideline variant adds `fix_class: mechanical|gated`).
- **Verify prompt core**: "Default real=false. Re-read the actual file and suspect handled bugs, dynamic usage, intentional local definitions, and moved lines. If real, re-classify whether the fix is minimal/safe + the fix_class."
- If a reviewer fails to produce schema output (e.g. the build group), re-run only that group with a single supplementary agent and merge the result.

## Verify & gate protocol

1. Before applying, re-confirm each finding by reading it directly (don't blindly trust an agent's claim).
2. Code: byte-compile → `python -m pytest tests/` PASS → `python tools/lint.py` EXIT=0 → entry-point smoke run.
3. Guidelines: `python tools/lint.py meta` PASS (voice antipattern · craft-chain consistency · all items) → for `.claude/` and CLAUDE.md edits, present the Guideline Verification Ladder evidence (rungs 1–3).
4. Gated items are not applied — handle separately after operator approval.
5. On completion, after operator approval, commit + push to origin (split by logical unit: code / guidelines / regenerated artifacts).

## Carry-forward

- **Hoisting a shared helper closes a bug class.** If the same defect (e.g. reading a removed `date:` field) is spread across several file copies, one round misses some — consolidate into `_lib` so the class has a single fix point.
- **When adding a new operations/skills file, also update the CLAUDE.md "Instruction Locations" + directory-layout lists** — otherwise the next round flags it as misplacement/stale.
