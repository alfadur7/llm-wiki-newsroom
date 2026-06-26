# Archive

Accumulated results of `python tools/_ingest/fetch_inbox.py` runs. Grouped by date, with the most recent date at the end of the file.

Each line format: `- HH:MM [<source>] <URL> → <result>`
- `[<source>]` — entry channel (`mobile`/`interactive`/`auto-gap`/`cron-news`/`hook-adapt`). An entry without metadata is `[mobile]`.
- `<path> OK` — fetch succeeded
- `SKIPPED (duplicate of <slug>)` — URL already ingested
- `FAILED:<reason>` — failed (URL retained in the inbox, retried on the next run)

## 2026-06-26
- 14:16 [mobile] https://blog.mozilla.org/en/mozilla/ai/open-source-ai-definition/ → raw/NewsScrap/Celebrating An Important Step Forward For Open Source AI The Mozilla Blog.md OK
- 14:16 [mobile] https://thenewstack.io/the-case-against-osis-open-source-ai-definition/ → raw/NewsScrap/The Case Against OSI's Open Source AI Definition.md OK
- 14:16 [mobile] https://opensource.org/ai → raw/NewsScrap/Open Source AI.md OK
- 14:16 [mobile] https://www.hunton.com/insights/publications/part-1-open-source-ai-models-how-open-are-they-really → raw/NewsScrap/Part 1 – Open Source AI Models How Open Are They Really.md OK
