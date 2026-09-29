# Pre-registration — judge-model (Jev) measurement on the public corpus

Written 2026-09-24, before any label or score exists. Population frozen in `freeze-2026-09-24.json` (34 L2-1 source pages + their raw originals, HEAD 2fda6f7; no page changed since 38737c4).

## Labels (ground truth)
- Every page reviewed blind by two Desk labellers (A, B), each running the desk.md L2-1 source VERIFY₂ procedure against the raw original, one pass, no cap on defects, identical prompt wording on every call, 4 pages per call, JSON-lines reply. A and B see different page groupings.
- Labellers are not told about the measurement, the judge model, the known-issue list, or that L2-1 review was withheld; they are told not to read log.md, git history, or anything under tools/.
- **Primary endpoint:** a page is *defective* if it has ≥1 defect rated critical or high.
- Agreement: if A and B agree on the endpoint, that is the label. If they disagree, a third labeller (C) reviews the page alone, and C decides.
- Secondary endpoint: count of critical+high defects per page (union of A and B, not deduplicated beyond exact duplicates).

## Scores
- Cap calibration first (separate from the ledger): 2–3 English pages sent once through the client to read input_tokens; MAX_STATE reset from the measured chars/token with a 3% margin. Raw originals are sent as-is (LWN reader comments included); no manual trimming.
- Then `probe_score.py` over all 34 pages, one draw per (page, criterion), only after every label is in.
- Page score: sum of per-criterion percentile ranks (low p = likely defect), over the criteria a page has. `cit.claimant-speaker` folds to the page's minimum claim p; pages without entity claimants get the two page criteria only (percentile sum rescaled by criteria count).
- Unscoreable pages (cap, PDF failure) are reported and excluded from the AUC; no imputation.

## Comparisons
- AUC of the Jev page score vs the primary endpoint, with a 95% CI (Hanley–McNeil and bootstrap, 2,000 resamples).
- Same for: the current sub-trigger (`[fact]≥7 AND quotes≥3` as a binary selector), and page length (body characters) as a free proxy.
- Paired difference Jev − sub-trigger and Jev − length (bootstrap CI).
- Per-criterion AUCs as secondary only.

## Decision rule (agreed with operator 2026-09-23)
- ≥12 defective pages AND Jev AUC lower 95% bound > 0.5 → no second expansion; report as directional.
- Otherwise → ingest ~25 more sources and re-measure.
- Publishing the scorer and changing the "no API keys" wording is decided by the operator after the result.

## Amendment 1 — measurement 2 (written 2026-09-27, after measurement 1, before any source for measurement 2 is chosen)
Measurement 1: 6/34 defective; judge AUC 0.685 (lower bound 0.38) → rule said expand. Exploratory finding: 3/6 defective pages are the original-4 cohort (older pipeline, short); judge AUC within the new 30 was 0.43.
- **Population:** the 34 pages (labels reused as-is; page text must stay byte-identical to the freeze) + ~25 new source pages ingested by the current pipeline.
- **Primary analysis population:** current-pipeline pages only (the 30 from 38737c4 + the new ones). The original-4 cohort is reported separately and in an all-pages secondary analysis. Fixed now because measurement 1 motivated it.
- **Selection:** sources chosen on topic and source type only (multi-speaker reporting, round-ups, interviews and policy pieces quoting several parties are favoured, since they carry more attribution surface). No judge score is consulted during selection. Authoring Reporters are not told about the measurement.
- **Labels:** the same protocol and prompt as measurement 1 (A/B blind, 4 pages per call, C on disagreement). L2-1 Desk withheld on the new pages.
- **Scores:** re-run `probe_score.py --yes`; the ledger re-sends only changed state (new pages, or old pages whose claim questions change because a new entity stub appeared — page text itself unchanged). One draw per (page, criterion), latest row wins.
- **Decision rule unchanged**, applied to the primary population: ≥12 defective AND judge AUC lower 95% bound (min of Hanley–McNeil and bootstrap) > 0.5.
- **Also reported:** judge AUC with page length and cohort as covariates (stratified), so a length or cohort proxy cannot pass as a defect signal.
