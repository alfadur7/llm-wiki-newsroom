# Codebase Audit Runbook (multi-agent ultrareview)

A multi-agent batch procedure for an ultrareview-grade, exhaustive pass over the `tools/` Python code and the `.claude/` guidelines. The operator starts it with "do a full audit / ultrareview." It uses the Workflow tool (multi-agent orchestration), so operator opt-in is a prerequisite. The two variants (code / guidelines) share one harness and differ only in group decomposition, review dimensions, and the application policy.

## When to run

- When the operator requests a full code or guideline audit
- Right after a large refactor or structural change (to catch drift)
- Periodic review

## Variant A — Python code (tools/ + hooks + graph.html)

- **Group decomposition**: just before starting, enumerate `tools/**/*.py` + `.claude/hooks/**/*.{py,sh}` + `graph/graph.html` live into ~10–12 groups by submodule, ≤~8 files per group. No hardcoded list — files accumulate. Exclude vendored artifacts such as the obsidian plugin `main.js`.
- **Review dimensions**: `bug` (runtime errors · wrong conditions · None/KeyError · regex · resource leaks · encoding/path · broad-except masking) · `dead-code` (unused functions/constants/imports · unreachable branches · `_lib` duplication) · `inconsistency` (not using a `_lib` helper · hand-rolled frontmatter parsing · inconsistent exit/error handling) · `over-engineering` (needless abstraction · speculative generalization · single-impl interface/factory · config for values that never change · symptom-only non-root-cause fixes — criteria SoT `.claude/skills/ponytail-coding/SKILL.md` ladder; missing reuse belongs to `inconsistency`, so it's excluded here).
- **Application**: `fix_safe=true` (a code-variant field in FINDINGS_SCHEMA — see § Harness) is fixed directly. Verification is § Verify & gate protocol item 2 (code).

## Variant B — guidelines (.claude/ + CLAUDE.md + README + skill checks.py)

- **Group decomposition**: by review dimension, not by file — every reviewer reads the whole corpus (tracked files under `.claude/**` + `CLAUDE.md` + root `README.md`) plus the registries its rules resolve against from outside it (e.g. `graph/cluster_labels.json`), and the 2–3 groups split the dimensions (e.g. `drift` · `contradiction`+`misplacement` · `stale`+`duplication`+`code-bug`).
- **Review dimensions**: `drift` (a symbol/field/CLI/output the doc describes doesn't match the actual code — confirm only after reading that code) · `contradiction` (the same rule/threshold/procedure conflicts across or within files — one policy's threshold/instruction disagrees with another guide or is mutually exclusive; confirm only after reading both originals; intentional reproducibility duplication and SoT-delegation pointers are excluded) · `duplication` (intentional reproducibility duplication and SoT-delegation pointers are excluded, as under `contradiction` above) · `stale` (removed features · dead cross-links — when a section has moved, search for the name each caller actually uses, often a step number or label rather than the heading) · `misplacement` (violates the CLAUDE.md "Instruction Locations" taxonomy) · `code-bug` (checks.py).
- **Drift input is the code**: the `drift` reviewer reads the implementation behind each documented symbol/field/CLI/output — a pass that opened no code and reported no drift has not run the dimension.
- **Exclude what lint already covers**: do not re-report what `python tools/lint.py meta` already catches (CLAUDE.md anchor/file-ref/slash-cmd/roster · voice antipattern · hook format · craft-chain closure · stale guide ref · log ordering) — the multi-agent pass owns the semantic layer lint can't reach.
- **Application**: mechanical (stale ref · counts · scope · field names · dead code) is fixed directly. **Gated** (changes to a guide/rubric/matrix skeleton — Human Reviewer Gate) is not applied; surface it to the operator.

## Harness (Workflow)

Common to both variants. `pipeline(GROUPS, review → adversarial verify)` — one reviewer reads each group and returns schema-bound findings, then a separate verifier re-checks each finding default-reject (re-reading the actual code, re-classifying). The verify stage filters false positives (e.g. write_text package conventions, intentional local regexes).

```js
// Common skeleton — only GROUPS, the review/verify prompts, and the schema's fix classification swap per variant
const REVIEW_MODEL = 'opus', VERIFY_MODEL = 'opus'  // one decision point — see § Model routing
const dead = []
const verified = await pipeline(
  GROUPS,
  (g) => agent(reviewPrompt(g), { phase: 'Review', model: REVIEW_MODEL, schema: FINDINGS_SCHEMA }).catch(() => null),
  (review, g) => {
    if (!review) { dead.push(`review:${g.key}`); return [] }   // a dead agent is not zero findings
    return parallel(review.findings.map((f) => () =>
      agent(verifyPrompt(f), { phase: 'Verify', model: VERIFY_MODEL, schema: VERDICT_SCHEMA }).catch(() => null)
        .then((v) => { if (!v) dead.push(`verify:${g.key}`); return { group: g.key, finding: f, verdict: v } })))
  },
)
const confirmed = verified.flat().filter(Boolean).filter((r) => r.verdict && r.verdict.real)
return { confirmed, failed_groups: dead, audit_complete: dead.length === 0 }
```

- **Context precondition**: a group's stated input must fit the reviewer's context — the guideline corpus is ~800 KB, and a `drift` reviewer that also opens `tools/**` reads ~1.8 MB (~450K tokens). Confirm that fit before the run; where no available window covers it, narrow the group rather than silently dropping the inputs its dimension names. This sizes the group, it does not pick the model: most current families carry a 1M window, so the check clears every candidate but the smallest.
- **Model routing**: these agents are spawned by the script, so the frontmatter pins in [`agents/README.md` § Model routing](../agents/README.md#model-routing-frontmatter-model) never reach them — pass `model` on every `agent()` call or each stage silently takes the session default. That section's family split is not carried here as a rule; default to the skeleton's constants and deviate on capability or cost with the reason recorded in the run.
- **An empty result is not a pass**: a reviewer killed by a run limit returns nothing, and a lenient per-agent fallback turns that into `confirmed: 0` — indistinguishable from a clean audit. The script must record every dead agent — reviewers **and** verifiers, the stage with the most of them — and return `failed_groups` + `audit_complete`, and recover by resuming the run (`resumeFromRunId`), which replays completed agents from cache and re-runs only the dead. `audit_complete: false` blocks § Verify & gate protocol item 5.
- **FINDINGS_SCHEMA**: `{file, line, category, severity, confidence, title, detail, proposed_fix}` (the code variant adds `fix_safe: bool` — true only when the change cannot alter behaviour outside the edited expression **and** does not reverse a decision the code documents on purpose; the guideline variant adds `fix_class: mechanical|gated`).
- **Verify prompt core**: "Default real=false. Re-read the actual file and suspect handled bugs, dynamic usage, intentional local definitions, and moved lines. If real, re-classify whether the fix is minimal/safe + the fix_class."
- If a reviewer produces malformed schema output (e.g. the build group), re-run only that group with a single supplementary agent and merge the result — a resume replays that agent as-is, so this case needs a fresh one.

## Verify & gate protocol

1. Before applying, re-confirm each finding by reading it directly (don't blindly trust an agent's claim) — after a mid-batch death this is also what skips a fix already present in the file.
   - **A withheld finding gets a second reader.** Where the re-read withholds a finding the verifier passed, that withholding is one actor's judgment and item 2 checks the code rather than the judgment. Give a reader from a different family than the actor who applied the batch the applied diff and the withheld list, without the deliberation behind them; it rules per item whether the withholding stands and whether each applied fix does what its finding asked. What it overturns returns to the batch, and item 5 waits. Borrow the Ladder's rung-3 blindness discipline ([`agents/editor-in-chief.md`](../agents/editor-in-chief.md#guideline-verification-ladder)) but not its per-hunk verdict contract, which is for guideline text; under Variant B this is item 3's rung-3 reader with the withheld list added.
2. Code: byte-compile → `python -m pytest tests/` PASS → `python tools/lint.py` EXIT=0 → entry-point smoke run.
3. Guidelines: `python tools/lint.py meta` PASS (voice antipattern · craft-chain consistency · all items) → for `.claude/` and CLAUDE.md edits, present the Guideline Verification Ladder evidence (rungs 1–3).
4. Gated items are not applied — handle separately after operator approval.
5. On completion (`audit_complete: true` — an incomplete run is not a completion), file the findings item 1 confirmed through `log_defect` with `caught_at` stage `audit`, one record per finding; then, after operator approval, commit + push to origin (split by logical unit: code / guidelines / corpus / regenerated artifacts).

## Carry-forward

- **Hoisting a shared helper closes a bug class.** If the same defect (e.g. reading a removed `date:` field) is spread across several file copies, one round misses some — consolidate into `_lib` so the class has a single fix point.
- **When adding a new operations/skills file, also update the CLAUDE.md "Instruction Locations" + directory-layout lists** — otherwise the next round flags it as misplacement/stale.
