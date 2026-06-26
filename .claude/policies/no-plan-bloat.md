# No Plan Bloat Policy

The duty to avoid bloat and duplication when authoring `~/.claude/plans/*.md`.

## Principle

Absorb into an existing section, table, or matrix by default. Create something new only after proving no matching pattern exists.

## 5-step self-check (mandatory just before ExitPlanMode)

1. New section/table/matrix vs. a one-line absorption into an existing section — absorb by default
2. Zero copies of another SoT's table/matrix — replace with a cross-reference
3. Zero new Risk/invariant/caveat sections by default — prefer attaching a qualifier to an existing section
4. When the changed lines ≥ 50, a mandatory minimum-edit re-review
5. Read the full context of each changed file — do not call ExitPlanMode without reading it through

## 4 red flags (a single hit forces the 5-step re-review)

- ≥ 2 new sections added
- ≥ 50 changed lines
- A new table or matrix added
- The same information already exists in another SoT

## File-name explicitness (the T1 naming principle)

When naming a new memory/policy/hook file, use the **T1 prescriptive default** — an imperative form like `no_X` · `X_to_Y` · `X_not_Y`. T3 descriptive names (`*_voice` · `*_posture`) require two-step inference on recall — they match utterance patterns 1:1 weakly.

This policy itself is T1 (`no-plan-bloat`).

## Scope

`~/.claude/plans/*.md` (plan files only).

Other voice policies are in [claude-guideline-voice.md](claude-guideline-voice.md).
