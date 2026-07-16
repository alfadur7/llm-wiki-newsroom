Ingest a source document into the LLM Wiki.

Usage: `/wiki-ingest <file|folder|inbox>` — required argument

**If `$ARGUMENTS` is empty**: print the usage below and **stop**.

```
Usage: /wiki-ingest <file|folder path | inbox>

Examples:
  /wiki-ingest raw/articles/my-article.md       # single md
  /wiki-ingest raw/NewsScrap                    # HTML article folder
  /wiki-ingest raw/PDF                          # PDF folder
  /wiki-ingest inbox                            # process the mobile share-sheet URL queue
```

## Traversal Pattern

L2-1 source + L2-2 stub cycle + Meta (full rebuild) — Writing-driven, tightly coupled. The Reporter performs the raw → structured conversion end to end.

| Phase | Cycle | Owner |
|---|---|---|
| Prefilter dedup | (deterministic) | Editor-in-Chief → `tools/_ingest/prefilter_ingest.py` or `_source_map.json` matching |
| Pre-fanout wiki read | GROUND common | Editor-in-Chief (Read `index.md`·`overview.md` — shared sub-agent context) |
| Source page authoring | L2-1 GROUND·APPLY | Reporter (mode=apply; read body + claim atomization + citation type prefix + grade) |
| Stub creation/update | L2-2 GROUND·APPLY | Reporter (mode=apply; auto-generate entity·concept stubs — body ≥200 chars, 2 H2 required) |
| Person incumbency check | GROUND external | Reporter (mode=ground, WebSearch) |
| Source verification (1st) | VERIFY₁ | Reporter self (right after authoring, confirm `python tools/lint.py source <slug>` PASS — self-ADAPT on FAIL) |
| Source verification (2nd, sub-trigger) | VERIFY₂ | Editor-in-Chief — invoke the Desk on sources meeting `[fact]≥7 AND citations≥3` (based on the `tools/_lint/source.py` Advisory auto-surface, batched at the post-fanout stage). SoT: [`agents/desk.md`](../agents/desk.md) L2-1 source VERIFY₂. |
| Hub verification (1st) | VERIFY | Reporter (single-source stub during fanout) · Editor-in-Chief (post-fanout cross-source stub) — `python tools/lint.py hub schema` |
| Cascade update | (deterministic) | Editor-in-Chief → `tools/build.py` (graph → clusters → contradictions → index → dependencies) + hub `sources:` sync |
| Batch verification (full) | VERIFY | Editor-in-Chief — post-fanout `python tools/build.py` + `python tools/lint.py` all groups (deterministic check, so done directly by main — the deliberate lint cycle that needs `lint-report.md` output is delegated to the Copy Editor = `/wiki-lint`) |
| Log append + defect logging | — | Editor-in-Chief (`log.md` append + batch this cycle's lint FAILs and Desk-actionable defects → `tools/log_defect.py` corpus). SoT: [`agents/editor-in-chief.md`](../agents/editor-in-chief.md) self-evolution automatic channel |

## Inbox Mode (`/wiki-ingest inbox`)

A shortcut path to fetch + ingest the URL queue accumulated in `raw/_inbox.md`. Because the mobile share-sheet, `/wiki-news` interactive, and `--gap` channels all converge on this queue, the 2-stage fetch (deterministic + WebFetch fallback) is owned solely by this mode.

1. **1st-stage deterministic fetch** — `python tools/_ingest/fetch_inbox.py`. Reads `raw/_inbox.md` line by line and (a) matches against `_source_map.json::by_url` → SKIPPED + dequeue, (b) for new ones, fetches via the `tools/_ingest/fetch_article.py` logic → `raw/NewsScrap/<slug>.md` or `raw/PDF/<slug>.pdf`, (c) failures stay in inbox + a `FAILED:<reason>` record in today's section of `raw/_archive.md`.
2. **2nd-stage WebFetch fallback** — for URLs the 1st stage left behind as `FAILED:short-content` (JS-rendered sites), the Reporter (mode=ground) fetches the body via `WebFetch` and writes `raw/NewsScrap/<slug>.md` directly. The frontmatter (`source` (URL)·`created`·`description`, etc.) must be **character-for-character identical** to the 1st-stage tool output — arbitrary changes break `_source_map.json` matching. If the body is under 100 chars, hold off on ingest. Successful URLs are removed from `_inbox.md`. (`BLOCKED`·`HTTP-4xx`·network failures are not fallback targets — they stay for retry.)
3. **Proceed in folder mode** — the 12-step procedure on the fetch outputs (`raw/NewsScrap`·`raw/PDF`). **Create source pages only after the raw has landed on disk** — because the raw tree is the dedup ground truth (`by_path`), an unfetched source bypasses duplicate detection.
4. **Pre-approved commit of system-managed files**: `raw/_inbox.md`·`raw/_archive.md` are system-managed files, so commit·push them automatically without separate approval. Other raw content files and ingest outputs (`wiki/`·`graph/`) are committed only after explicit approval from the wiki operator.

Setup guide: [`.claude/operations/mobile-inbox-setup.md`](../operations/mobile-inbox-setup.md)

## Prefilter (Folder Mode)

- **Automation first** — `python tools/_ingest/prefilter_ingest.py <raw-folder>`. by_url first + by_path second fallback + Raindrop exclusion + 0-byte skip, deterministic classification → counts and a new-candidate list of (a) URL-dup / (b) Path-dup / (c) Genuine new. **Only "Genuine new" are true candidates.**
- **Manual fallback** (when the tool is unavailable): (a) frontmatter `source:`/`url:`/`source_url:` → `by_url` match → SKIP, (b) on URL non-match, raw path (Unicode quotes normalized) → `by_path` match → SKIP, (c) only those that match neither and are not 0-byte are genuine. **No `by_path`-only prefilter** (memory `feedback_ingest_prefilter_url_first` — Obsidian re-scrape variants permanently miss).
- Scan extensions: `.md` + `.pdf`
- Exclude under `raw/NewsScrap/Raindrop/` (already-ingested legacy)
- Empty files (0-byte) auto-skipped

## Parallel Batch (Genuine new 3+)

If there are **3 or more** Genuine new candidates, branch out with the Agent tool. 12-step split:

- **Pre-fanout (main, once)**: read the wiki (`index.md`·`overview.md`) — shared sub-agent context
- **Fanout (N sub-agents in parallel)**: each sub-agent, for one candidate, (a) reads the raw, (b) matches URL/path, (c) writes `wiki/sources/<slug>.md`. It reports back to main with collected results (proposed new entities/concepts · `## Connections` links · discovered contradictions · missing quote speakers).
- **Post-fanout (main, serial)**: dedupe proposals → **re-evaluate the entire entity/concept corpus** (do not limit to reporter proposals — because adding new sources can newly push existing plain-text entities·concepts over threshold, Grep the corpus for cumulative distinct-source counts of newly appearing proper nouns·concepts and re-decide against the [`.claude/policies/naming.md`] thresholds. `hub speakers` automatically covers quote speakers only — for non-speaker entities·concepts this re-evaluation is the only safety net) → upsert entities/concepts (including person incumbency check — single-source-threshold stubs by the Reporter during fanout; for ≥3-source consolidated judgments the Editor-in-Chief judges the threshold serially and hands the approved targets to the Reporter for authoring [hand-over contract: `layers/hub.md` stub authoring]) → on new entity creation, reassign existing source claimants → cascade update (sync the `sources:` of `## Connections` target hubs) → integrate contradictions (theme JSON mapping + `contradiction.md` head stats) → log append → full rebuild + batch lint + cluster diagnosis (once) → after Desk VERIFY₂ ADAPT, batch-log this cycle's defects (`log_defect`)

Race avoidance: two sub-agents never write to the same file simultaneously. `wiki/sources/<slug>.md` is isolated per slug. `wiki/entities/`·`wiki/concepts/`·`wiki/overview.md`·`log.md` are updated serially by main.

## 12-Step Procedure (Serial or per Sub-agent)

1. **Read the source file**:
   - **md**: body via the Read tool
   - **PDF**: PDF binary directly via the Read tool (if many pages, split with `pages: "1-10"`). raw/PDF/ files stand alone — URL metadata is recorded on the wiki source page at step 4
2. **Prevent duplicate ingest** (URL first + path second):
   - **1st URL match**: raw md `source:`/`url:` or an existing source page's `source_url:` → look up `_source_map.json::by_url`. On match, use the existing slug + update the existing file
   - **2nd path match**: on URL non-match, raw path (Unicode quotes normalized) → look up `by_path`. On match, handle the same way
   - If neither matches, it is a new ingest
3. **Grasp the existing wiki state** — `wiki/index.md` (exact filename list — the basis for writing wikilinks), `wiki/overview.md` (current synthesis-analysis context)
4. **Write `wiki/sources/<slug>.md`** — body·sections in English (Korean only under `WIKI_LANG=ko`), the Phase 2 new schema is mandatory (claim atomization + citation type prefix + grade). The authoring standard is a mandatory Read of [`.claude/layers/source.md`](../layers/source.md). After writing, verify with `python tools/lint.py source <slug>`. **Preserve `source_file:`**: the raw file path character-for-character (no ASCII transliteration of typographic quotes·whitespace·special characters). If the raw has an ASCII `"`, wrap the frontmatter value in single quotes; if the raw has a `'`, wrap in double quotes.
5. **Entity/concept pages (upsert after duplicate check)**:
   - Before creating a new one, check the existing index.md list for identical·similar pages
   - If it already exists, update the existing page (add sources·strengthen facts)
   - **Person entity incumbency check (required)**: confirm the current role via `WebSearch`. On change, write the current role + "(formerly OOO)". For those who have stepped down, hold off on creation or ask the human reviewer to confirm.
6. **Cascade update** — add sources + strengthen facts + update last_updated on existing hubs linked in the source's `## Connections`. On bulk ingest, this may be skipped and post-processed by lint.
7. **Flag contradictions** — identify contradictions with existing wiki content
8. **`log.md` append**: `## [today's date] ingest | <Title>`
9. **Automatic verification** (required):
    - Check for broken wikilinks (use the canonical entity title, not a translated display name — `[[Anthropic]]` ✓)
    - Filename script: an English filename is the default; use a native-script filename only for an entity with no standard Latin form
    - Check the new hub's tags
    - **Detect missing quote-speaker stubs**: `## Key Quotes` speakers → confirm `wiki/entities/<name>.md` exists. If absent, suggest creating a stub (subject to the hub-stub-threshold policy)
    - **Strengthen in-body wikilinks**: `python tools/_ingest/suggest_links.py --file wiki/sources/<slug>.md` — surfaces existing entity/concept stems that appear as plain text
    - **Suggest tag candidates**: `python tools/_ingest/suggest_tags.py --file wiki/sources/<slug>.md` — surfaces thematic tag candidates based on `## Connections` hubs (an empty `tags: []` is blocked by the source lint T1 hard gate)
10. **Full rebuild + cluster diagnosis**:
    - `python tools/build.py` — all 5 phases (graph → clusters → contradictions → index → dependencies)
    - `python tools/lint.py graph clusters` — check isolated hubs · unnamed groups · unassigned sources
    - On finding an isolated hub, strengthen the source's `## Connections` wikilinks and rebuild
    - For unnamed groups, suggest adding a label to `cluster_labels.json` (no automatic Claude edits — human reviewer approval)
11. **Desk VERIFY₂ (stub unconditional + source sub-trigger)** — the Editor-in-Chief invokes the Desk in batch on two target sets: (a) **every L2-2 stub created or updated this cycle** (`wiki/entities·concepts·timelines/*.md` — mandatory per the Layer × Cycle matrix, format·attribution·narrative tone scope; byproduct stubs included), and (b) the source list meeting `[fact]≥7 AND citations≥3` from the `python tools/lint.py source` Advisory output. The Desk returns a defect list → Reporter ADAPT₂ → re-lint. SoT: [`agents/desk.md`](../agents/desk.md) owned cells + [`agents/README.md`](../agents/README.md) "L2-2 stub obligation".
12. **Cycle defect batch-logging** — batch-log this cycle's escaped lint FAILs and Desk-actionable defects once into the `tools/log_defect.py` corpus (`tools/_defect-log.jsonl`) (`caught_at`=`<stage>:<detail>`·`cluster` slug·`severity`·`addressable`). `mine_failures` bundles end-to-end recurrence rates and feeds them into the SoT self-evolution automatic channel. SoT: [`agents/editor-in-chief.md`](../agents/editor-in-chief.md).

## Output

Report on completion: pages added · pages created/updated · contradictions found · verification results · cluster-health impact.

## Human Reviewer Gate

- New person entity stub (memory hub-stub-threshold — only for key people cited multiple times across multiple sources)
- New cluster slug / unnamed group label (no automatic Claude edits)
- Commit·push after ingest (memory git-approval)
- A contradiction flag strongly affecting an existing theme (potential theme-MD rewrite trigger)
