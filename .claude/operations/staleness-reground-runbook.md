# Staleness Re-ground Batch Runbook

Instructions for re-grounding the stale derived narratives (L2-3 · L2-4 + L2-2 timeline) that `/wiki-lint staleness` surfaces, against the current cluster and claim state. You can open this file and start directly with "perform the staleness re-ground batch per these instructions." Run it in a local or Claude Code Web session; this file holds the re-ground-specific procedure and gates.

## Live State First

The stale list changes with every ingest and edit, so run it **live at the start of each batch** (never trust a hardcoded list):

```
PYTHONUTF8=1 python tools/lint.py staleness
```

It surfaces the derived-narrative types (overview · contradiction · synthesis · trail · timeline + the root meta `overview.md` · `contradiction.md`), grouped `by layer`. The basis is the **EDITOR-body git edit date** (`tools/_lint/_editor_date.py`), not frontmatter, so it correctly catches a page that a partial edit bumped the date on while the body stayed a draft. It is advisory (exit 0), so it only surfaces — it never blocks. Re-grounding is triggered separately by this batch (staleness has no `--fix`).

## Per-Layer Procedure

Handle each surfaced page by type. The page GROUNDs its own new source/claim context (a cluster overview's input is in its item below).

- **cluster overview**: update by zero-base rewrite (authoring standard: [`layers/overview.md`](../layers/overview.md) "Updating an existing overview"). Pages are independent, so run them in parallel. Run each round in this order.
  Every body edit is followed by a desk pass, and nothing is edited after the last pass. The Editor-in-Chief does not edit body sentences — even a deletion or a word swap that looks mechanical drops qualifiers and facts when it ships without a pass.
  1. **Prerequisites** (Editor-in-Chief): if an L2-1 source in the cluster has a critical correction in progress, start after it closes. Put into the call the axis checklist (the previous `## Overview` paragraph 4 in full and the `## Subtopics` headings) and the delta source list. Carry over no other previous sentence.
  2. **Authoring** (one Columnist): write only the EDITOR body into a scratch file the Editor-in-Chief names. The reply's first line is `done: sources_read=<N> hubs_read=<N>`. Then one line per axis, `axis: <previous axis> → keep|reorganize(<new name>)|demote(<subtopic N>)|drop — <reason>`, then the claims checked down to raw and the areas seen only at the source layer. A reply missing the first line or the axis lines is not accepted — ask again.
  3. **Merge** (Editor-in-Chief): move the draft's EDITOR body into the target file and byte-compare the moved EDITOR region against the draft. In the frontmatter change only `sources:` (refilled from the sources the body cites) and `last_updated`; leave the other fields and the `<!-- AUTO:... -->` blocks as they are. Then run `lint overview <slug>` (VERIFY₁) on the target file; on FAIL, resume the author to fix it in the target file and run it again. This fix stands in for the author's pre-hand-off check (self-VERIFY₀), so it is outside the ADAPT counter; two FAILs on the same cause go to the operator. Every later treatment happens in the target file. It is a >50% body rewrite, so commit only after operator approval (Human Reviewer Gate below).
  4. **VERIFY₂** (one fresh Desk, after step 3's lint PASS): open every citation in `## Overview` · `## Recent Changes` · `## Key Trends & Figures` and in subtopics built on delta sources, and about 30% of the citations in the other subtopics; open key figures and direct quotes down to raw. Compare the axis lines with the checklist to judge dropped axes, and the delta list to judge missing events; check that each thesis sentence has its counter-evidence in the same paragraph, and report a missing pair as a defect line. Without the reply's first line `sources_read=<N> raw_checked=<N> pairs_checked=<N>` nobody can tell whether "0 defects" was a full check — ask again.
  5. **ADAPT₁** (same author, resumed): treat every defect. Reopen the source for each defect and write the sentence yourself; on disagreement, mark `diverged` with the reason. After this and every later ADAPT, rerun self-VERIFY₀.
  6. **Re-judgment** (the VERIFY₂ Desk, resumed — it judges closure of its own findings, which needs their context): confirm closure of every defect, compare each sentence the treatment added against the source and report it by severity, and judge the facts of each `diverged` defect against raw itself. The author's "checked source/raw" report is not evidence — the report and what was actually opened can differ.
  7. **ADAPT₂** (same author): treat only step 6's unclosed defects and new highs. Skip it if there are none.
  8. **Confirmation pass** (one fresh Desk, always, whatever step 6 found): read the full text once with the VERIFY₂ lenses and no assigned axis, checking the sites step 7 fixed in context.
  9. **Termination**: no high in step 8 ends the round. Step 8's medium·low go to the ledger and the body is not edited further. A high in step 8 → ADAPT₃ (author, high only), then one fresh Desk narrowly re-checks only the fixed sites. If a high is still there, do not commit — report to the operator. The same holds if self-VERIFY₀ stays FAIL after the last ADAPT. These three (6 · 8 · the narrow re-check) cap the desk passes after VERIFY₂. If the operator wants a medium fixed, each approval extends the round by one ADAPT + narrow re-check pair.
  10. **Close and ledger** (Editor-in-Chief): before committing, refill `sources:` from the final body's citations. When closing the round, log its defects in one batch with `python tools/log_defect.py`, naming the round in `caught_at`. At the next zero-base round, look up the medium·low passed to the ledger with that overview as target and enclose them in the call.
  11. **Post-measurement** (Editor-in-Chief, after every page of the round is committed): pick one of the round's pages at random with `python -c "import secrets; print(secrets.choice([...]))"` and have one fresh Desk review it without treatment (the same open scope as VERIFY₂). Log its defects as a run separate from step 10 (`post-blind-<slug>-<date>`, `caught_at: desk:post-publish-blind`). Without it you know the gate passed but not the defect density of what shipped. No ADAPT follows, so it builds no loop and does not count toward step 9's cap. The operator decides how its defects are treated.
- **contradiction theme · synthesis · L2-4 root** (high-risk narrative): columnist rewrite → **desk qualitative gate** → 3-stage ADAPT. Run many items in parallel with a Workflow `pipeline` (each file is independent, so no worktree is needed; check progress with `tools/show_workflow.py`). The desk does a spot check against the originals to catch missing claimant attribution, figures, evidence grades, and due-weight gaps (the areas deterministic lint cannot reach).
- **timeline · trail** (low-risk, structural): a single columnist re-ground pass (new events · hops · refreshed commentary) plus a deterministic lint and a spot review in the main session. Skip the full desk gate to save cost, but cross-check each new timeline item's date and source index against the original one by one.
- **L2-4 root** (`overview.md` · `contradiction.md`): aggregate last, after the lower layers are re-grounded. Carry the lower layers' due-weight gaps and balance markers up to the root, and — since it is the reader-facing top entry point — keep internal implementation terms out of it (see [`../layers/overview.md`](../layers/overview.md) Part 2 principles).

## Deterministic Verify

Run these directly in the main session after ADAPT (don't trust an agent's self-report):

- Per-type lint (`python tools/lint.py <overview|contradiction|synthesis|timeline|trail> [<slug>]`) required metrics PASS + `python tools/lint.py graph` broken links 0 + AUTO blocks and frontmatter preserved.
- **One clean rebuild before committing** (`python tools/build.py`) — build artifacts an agent ran concurrently during re-grounding can otherwise get mixed in.
- **If the update deletes anything, pull every deleted segment with `git diff --word-diff -U0 HEAD -- <page>` and check each against that page's current body** (one page at a time — a repo-wide diff buries the page in the rebuild's churn). An author's self-report cannot close this: the set it checks is the set they remembered. Neither can the checks above — a deleted anchor leaves broken links at 0 and the AUTO blocks intact.
- After committing, re-run `python tools/lint.py staleness` to confirm resolution. The body date is git-based, so a page **stays STALE until you commit, and clears on commit** (expected behavior).

## Human Reviewer Gate

- Publishing L2-4 root content · a >50% body rewrite · a new contradiction theme slug · a new cluster slug · external commit/push.
- Desk high (blocking) defects are re-published after ADAPT. A claim-membership change (theme reassignment) requires the affected theme MD to be re-grounded too, so that is an operator-judgment area.

## Pitfalls

- **Workflow args plumbing**: a script's `args.items` may not arrive as an array — embedding the item data directly in the script is more robust.
- **Desk schema-stage failure**: a pipeline item can drop when the StructuredOutput retry limit is exceeded — re-gate any missing item with a standalone desk pass in the main session.
- **No fabricated links**: during re-grounding, demote a non-existent hub to plain text (keep broken links at 0). A new stub is a separate gate.
- **Theme JSON freshness**: if claim membership is stable (fully assigned · 0 unassigned), re-running `/wiki-lint contradiction theme --fix --yes` is just a metadata refresh that updates `derived_at` only (no theme-MD re-ground needed).

## Out of Scope

- Automatic re-grounding via staleness `--fix` (a deterministic tool cannot do cross-source synthesis or the desk gate — that is this batch's role).
- Unattended cron self-commit (the desk qualitative gate is required before commit — detection can be scheduled, but re-grounding and commit keep the gate).

## SoT

- Detection and signal definitions: [`../commands/wiki-lint.md`](../commands/wiki-lint.md) staleness row + `tools/_lint/staleness.py` · `tools/_build/dependencies.py`.
- Re-ground roles and cycle: [`../agents/README.md`](../agents/README.md) (Layer × Cycle · ADAPT chain) + the per-content-type [`../layers/`](../layers/).
