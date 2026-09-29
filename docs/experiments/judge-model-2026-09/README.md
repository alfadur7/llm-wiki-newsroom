# Judge-model experiment, September 2026

Data behind [Scooping the Rice, Leaving the Stones](https://alfadur7.github.io/llm-wiki-newsroom/scooping-stones/) ([한국어](https://alfadur7.github.io/llm-wiki-newsroom/ko/scooping-stones/)): does an external judge model (Jev) rank this wiki's defective source pages above the rest?

| File | What it is |
|---|---|
| `preregistration.md` | The analysis plan, written before any label or score, plus Amendment 1 (written after round one, before any round-two source was chosen) |
| `freeze-2026-09-24.json`, `freeze-2026-09-28.json` | SHA-256 prefixes of every labeled page and its original at each freeze. The 34 round-one pages are identical in both |
| `labels/labeler-prompt.md` | The labeling prompt, verbatim; the page list at the end changed per call |
| `labels/batches.json`, `labels/batches-2.json` | Which pages each A and B labeler saw, per round |
| `labels/A*.jsonl`, `B*.jsonl`, `C_*.jsonl` | Round-one labels: one row per defect (page, severity, lens, issue) and one `reviewed` row per page |
| `labels/m2-*.jsonl` | Round-two labels, same format |
| `scores.jsonl` | The judge's answers: one row per page, criterion and (for the claimant question) claim. `model_version` is an opaque tag |
| `page_features.json` | Each page's sub-trigger status and body length at the freeze |
| `analyze.py` | Recomputes the article's public-corpus numbers: `python analyze.py 1` (round one), `2` (round two), `labels` (severity table, review and request counts). The private-corpus figures and the per-page reviewer token estimate are not reproducible from this folder |

Labels come from AI reviewers (the wiki's Desk role) working blind, two per page, with a third on disagreement. Round-one batch A2 keeps the reviewer's full wording (location and evidence); the rest were recorded as a short issue summary. Severity is always as the reviewer gave it. The judge's question wording is not included; the scorer stays unpublished.
