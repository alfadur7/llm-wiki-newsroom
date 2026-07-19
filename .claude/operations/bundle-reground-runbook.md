# Bundle Re-ground Batch Runbook

Instructions for the **correction mode** of Reground: the Desk reads several *already-published* derived pages together as one bundle and detects the cross-page defects that only appear when two pages are laid side by side. You can open this file and start directly with "perform the bundle re-ground batch per these instructions."

This is the qualitative sibling of [`staleness-reground-runbook.md`](staleness-reground-runbook.md) (the update mode). That batch asks "did the sources move?"; this one asks "do our own pages still agree with each other?" Concept SoT: [`../../CLAUDE.md`](../../CLAUDE.md) § Reground.

## Bundle Assembly

A bundle is every published derived page of **one cluster**, read in a single Desk context:

- `wiki/overviews/<cluster>.md` — the cluster overview
- `wiki/contradictions/<theme>.md` — every theme whose claims come from that cluster's sources
- `wiki/sources/_catalog-<cluster>.md` — the generated source catalog
- the cluster's member entity·concept hubs (`graph/_clusters.json::members`)
- `wiki/timelines/<Entity>.md` and `wiki/syntheses/<slug>.md` when the cluster has any

## Target Defect Classes

| # | Class | What it looks like |
|---|---|---|
| 1 | **Coverage lag** | A theme or hub is missing recent on-topic evidence that its sister overview already synthesized |
| 2 | **Cross-file count drift** | Prose restating a generated number disagrees with the artifact (overview scale prose vs catalog header; hub chronology prose vs timeline header) |
| 3 | **Same event, differing attribution** | Two pages attribute the same figure or quote to different people or institutions |
| 4 | **Notation divergence** | The same object is named differently per page (`OSAID` vs "the Open Source AI Definition" vs `OpenSourceAI`) |
| 5 | **Matured monitoring point** | A monitoring point or forecast whose stated deadline has passed, never revisited |
| 6 | **Subject-irrelevant timeline entries** | Timeline items where the hub's subject is neither actor nor claimant *(applies once the corpus has timelines)* |

## Procedure

1. **Assemble** the bundle as above.
2. **Invoke the Desk** on the whole bundle. It returns a cross-page defect list and makes no edits (standard I/O contract, `.claude/agents/desk.md`). **Batch-only extra field**: tag each defect `[single-review catchable]` or `[bundle-only]`. This is an extension for this batch, not a contract change — it measures what the channel adds over the pre-publish baseline.
3. **Route by defect kind**:
   - coverage lag → Columnist re-ground of the lagging page → Desk VERIFY₂ → deterministic lint
   - count drift → check first whether **both** sides are machine-written; if so it is a build defect, not a page defect ([`../agents/copyeditor.md`](../agents/copyeditor.md) § Risk Mitigation Design). Only author-editable prose is fixed on the page.
   - notation → fix on the affected pages; recurring cases are promotion candidates
   - differing attribution → **not the Desk's authority to settle** (it cannot verify new facts). Hand to the Reporter for a raw-source comparison.
4. **Gate** — see below, then re-publish.

## Deterministic Verify

Run in the main session after fixes (don't trust an agent's self-report):

- Per-type lint for each touched page (`python tools/lint.py <overview|contradiction|hub|synthesis> [<slug>]`) + `python tools/lint.py graph` broken links 0.
- One clean `python tools/build.py` before committing.
- `python -m pytest tests/` when the batch touched `tools/`.

## Human Reviewer Gate

- L2-4 root content · >50% body rewrite · a new stub · a new theme or cluster slug · external commit/push.
- Desk `high` defects are treated via ADAPT and re-published.
- Promoting an observed defect class into a deterministic check is an **operator decision** (below).

## Cadence & Exit

No new ritual: this rides along the periodic review, **one cluster per batch**. Coverage comes from rotation, not exhaustive sweeps.

**Exit condition**: zero `[bundle-only]` defects across 5 consecutive bundles → demote the channel to on-demand ([`../agents/desk.md`](../agents/desk.md) § The Promotion Loop, burn criteria).

## Deterministic Promotion Candidates

A defect class observed repeatedly across bundles becomes a candidate for a deterministic check, narrowed to explicit-integer or explicit-string parsing so the check stays mechanical. This is the existing promotion loop in [`../agents/desk.md`](../agents/desk.md) § The Promotion Loop — thresholds, the 1-line ROI, soft caps, and burn criteria all apply unchanged.

## Out of Scope

- Auto-fixing anything found here (cross-page synthesis and attribution judgment are not deterministic).
- Unattended cron self-commit — detection may be scheduled; the Desk gate stays before commit.
- Re-litigating defects the pre-publish gate already owns (single-page bias·density·flow) — those belong to `desk.md` timings 1–3.

## SoT

- Reground concept + the three triggers: [`../../CLAUDE.md`](../../CLAUDE.md) § Reground.
- Desk lenses·personas·I/O contract·promotion loop: [`../agents/desk.md`](../agents/desk.md) (this batch is application timing 4).
- Deterministic check design (zero-FP rule, machine-written drift): [`../agents/copyeditor.md`](../agents/copyeditor.md) § Risk Mitigation Design.
- Update mode: [`staleness-reground-runbook.md`](staleness-reground-runbook.md).
