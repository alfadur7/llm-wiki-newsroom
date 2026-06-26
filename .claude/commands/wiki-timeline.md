Generate a chronological timeline for an entity or concept in the LLM Wiki.

Usage: `/wiki-timeline <entity|concept> [year]`

**If `$ARGUMENTS` is empty**: print the usage below and **stop**.

```
Usage: /wiki-timeline <entity|concept> [year]

Examples:
  /wiki-timeline Meta              # full chronological storyline for Meta
  /wiki-timeline DeepSeek 2025     # only DeepSeek's 2025 events
  /wiki-timeline OpenWeights       # a concept page works too

Without a target entity/concept, backlinks cannot be collected, so it stops.
```

## Traversal Pattern

L2-2 timeline content. The page format·authoring standard·Rubric have their SoT in [`layers/timeline.md`](../layers/timeline.md); this command is the procedure that fills that standard by traversing `_backlinks.json` backlinks.

| Cycle | Owner |
|---|---|
| GROUND | Columnist (`_backlinks.json` + backlink source read) |
| APPLY | Columnist (reverse-chronological narrative authoring) |
| VERIFY₁ | Copy Editor (`lint.py timeline` schema) |
| VERIFY₂ | Desk (qualitative — timeline mixing·narrative flow) |
| Save | Editor-in-Chief gate + log append |

## Authoring Procedure (Columnist Cycle)

1. Source pool extraction = `wiki/_backlinks.json` backlinks **∪ the target hub's frontmatter `sources:`**. Backlinks catch only in-body `[[links]]` and would miss primary events linked solely via frontmatter, so the union secures them losslessly.
2. Sort reverse-chronologically by each source's `published:` (or `scraped:` if absent). If a year argument is given, that year only.
3. Read each source → 1-2 lines of key facts. **entry-date guard**: the entry date must be directly backed by the source's `published` (or an occurrence date stated in the body) — it cannot be later than `scraped` (year typo), and when splitting one source across multiple points in time, each point must be stated in the body (otherwise demote to the hub `## Timeline`, no standalone timeline exposure).
4. **History·future anchors** (mature topics): include pre-ingest events·future roadmaps not in the backlinks as `- **YYYY** — [[Entity]] description` / `- **YYYY (planned)** —`. No drops (lossless).
5. **Flow summary** (required, at top) — structure per [`layers/timeline.md`](../layers/timeline.md).
6. Output grouped by year (newest→oldest, reverse), with each dated item's **first link = `[[source-id]]`** (entity-first only for history anchors).
7. self-VERIFY₀: `python tools/lint.py timeline <slug>` → confirm `→ path`.
8. Save (when the gate is passed): `wiki/timelines/<slug>.md` + `log.md` append `## [YYYY-MM-DD] timeline | <entity name>`.

## Human Reviewer Gate

- New person entity stub (only for key people cited multiple times — hub-stub-threshold).
- Desk qualitative defects of critical/high.
