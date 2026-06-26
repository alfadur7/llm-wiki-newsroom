# Staleness Re-ground Batch Runbook

Instructions for re-grounding the stale derived narratives (L2-3 · L2-4) that `/wiki-lint staleness` surfaces, against the current cluster and claim state. You can open this file and start directly with "perform the staleness re-ground batch per these instructions." Run it in a local or Claude Code Web session; this file holds the re-ground-specific procedure and gates.

## Live State First

The stale list changes with every ingest and edit, so run it **live at the start of each batch** (never trust a hardcoded list):

```
PYTHONUTF8=1 python tools/lint.py staleness
```

It surfaces the derived-narrative types (overview · contradiction · synthesis · trail · timeline + the root meta `overview.md` · `contradiction.md`), grouped `by layer`. The basis is the **EDITOR-body git edit date** (`tools/_lint/_editor_date.py`), not frontmatter, so it correctly catches a page that a partial edit bumped the date on while the body stayed a draft. It is advisory (exit 0), so it only surfaces — it never blocks. Re-grounding is triggered separately by this batch (staleness has no `--fix`).

## Per-Layer Procedure

Handle each surfaced page by type. The page GROUNDs its own new source/claim context; for a cluster overview, narrow it to the primary-source delta in `graph/_clusters.json::source_assignments` that was `scraped` after the page's body edit date.

- **cluster overview · contradiction theme · L2-4 root** (high-risk narrative): columnist rewrite → **desk qualitative gate** → 3-stage ADAPT. Run many items in parallel with a Workflow `pipeline` (each file is independent, so no worktree is needed; check progress with `tools/show_workflow.py`). The desk does a spot check against the originals to catch missing claimant attribution, figures, evidence grades, and due-weight gaps (the areas deterministic lint cannot reach).
- **timeline · trail** (low-risk, structural): a single columnist re-ground pass (new events · hops · refreshed commentary) plus a deterministic lint and a spot review in the main session. Skip the full desk gate to save cost, but cross-check each new timeline item's date and source index against the original one by one.
- **L2-4 root** (`overview.md` · `contradiction.md`): aggregate last, after the lower layers are re-grounded. Carry the lower layers' due-weight gaps and balance markers up to the root, and — since it is the reader-facing top entry point — keep internal implementation terms out of it (see [`../layers/overview.md`](../layers/overview.md) Part 2 principles).

## Deterministic Verify

Run these directly in the main session after ADAPT (don't trust an agent's self-report):

- Per-type lint (`python tools/lint.py <overview|contradiction|timeline|trail> [<slug>]`) required metrics PASS + `python tools/lint.py graph` broken links 0 + AUTO blocks and frontmatter preserved.
- **One clean rebuild before committing** (`python tools/build.py`) — build artifacts an agent ran concurrently during re-grounding can otherwise get mixed in.
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
