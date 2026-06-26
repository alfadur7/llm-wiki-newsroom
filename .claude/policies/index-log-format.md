# Index & Log Format

## Index Format (`wiki/index.md`)

`index.md` is managed as a two-tier structure:
- **`wiki/index.md`**: lists entities, concepts, analyses, associative trails, and timelines directly. Sources are split out into per-cluster sub-catalogs.
- **`wiki/sources/_catalog-{cluster-slug}.md`**: per-cluster source list (with one-line summaries). If a source belongs to several clusters, it is listed in each catalog.

**Fully auto-generated — do not edit by hand.** `python tools/build.py index` regenerates it each time from across the wiki (source frontmatter · `wiki/entities/` · `wiki/concepts/` · `wiki/syntheses/` · `wiki/trails/` · `wiki/timelines/` · `graph/_clusters.json`). Any manual edits are overwritten on the next build. It carries no frontmatter (Root Meta Files Exception), and starts with the `# Wiki Index` H1 and an auto-update notice.

```markdown
# Wiki Index

This file is auto-generated and refreshed.

## Overview
- [Overview](overview.md) — global view along the landscape axis
- [Contradiction Analysis](contradiction.md) — global view along the conflict axis (N contradictions, per-theme drill-down)

## Recent Developments (N)            # only when there is at least 1 weekly-briefing-* (latest week first, max 8)
- [Weekly briefing title](syntheses/weekly-briefing-slug.md) — description
- _For the N earlier weekly briefings, see `wiki/syntheses/weekly-briefing-*`_  # only when N>8

## Sources (N)
For the full source list, see the [source catalog](sources/_catalog.md), or browse per cluster:

| Cluster | Count | Catalog |
|----------|------|---------|
| <cluster-name> | N | [<cluster-name> catalog](sources/_catalog-<cluster-slug>.md) |
| ... | ... | ... |

## Entities (N)
- [Entity name](entities/filename.md) — first-sentence description

## Concepts (N)
- [Concept name](concepts/filename.md) — first-sentence description

## Analyses (N)
- [Analysis title](syntheses/slug.md) — the question it answers

## Associative Trails (N)           # section created only when there is at least 1 file in trails/
- [Trail title](trails/slug.md) — trail description

## Timelines (N)            # section created only when there is at least 1 file in timelines/
- [Entity name](timelines/name.md) — chronological storyline description
```

## Log Format (`log.md`)

Each entry starts in the form `## [YYYY-MM-DD] <operation> | <title>`, so it can be parsed with grep:

```bash
grep "^## \[" log.md | tail -10
```

**Operations** (free tokens): use both slash-command operations (`ingest` · `query` · `lint` · `graph`) and operational ones (`policy` · `refactor` · `content` · `export`, etc.). Lint does not enforce a whitelist of tokens (it only validates date ordering), so use freely any label with a clear meaning.

### Append-at-bottom rule

A new entry is **appended at the end of the file**, and its date must be **equal to or greater than** the previous entry's. This ordering is the premise that lets `tail -10` return "the 10 most recent entries."

The "Log ordering" check in `python tools/lint.py meta schema` validates this automatically; when a violation is found, restore it manually by moving the offending entry block (from its header up to just before the next header) to the correct date position.
