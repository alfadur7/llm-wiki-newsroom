Create, follow, or list associative trails in the LLM Wiki (Memex trail-blazing).

Usage: `/wiki-trail <create|follow|list> [args]`

**If `$ARGUMENTS` is empty**: print the usage below and **stop**.

```
Usage: /wiki-trail <mode> [args]

Modes:
  create <topic>     auto-generate an associative trail for a topic
  follow <trail>     follow an existing trail in order, with commentary
  list               show the list of all trails

Examples:
  /wiki-trail create open source AI definition debate
  /wiki-trail follow ai-coding-rapid-evolution
  /wiki-trail list
```

## Traversal Pattern

L2-3 trail content. The page format, authoring standard, and Evaluation Rubric have their SoT in [`layers/trail.md`](../layers/trail.md); this command covers the create/follow/list mode routing.

| Mode | Cycle | Owner |
|---|---|---|
| **create** | GROUND·APPLY·VERIFY·ADAPT | Columnist (own-context read + trail narrative authoring) → Copy Editor → Desk (qualitative review) |
| **follow** | Reading | Reporter (mode=ground — read through and explain an existing trail page) |
| **list** | Reading | Reporter (mode=ground — directory enumeration) |

## Trail Page Format

The frontmatter, `## Path`, and `## Commentary` format is the SoT in [`layers/trail.md`](../layers/trail.md) → `## Page Format`. Author against that guide.

## Create Mode

Columnist cycle:
1. Explore `wiki/index.md` + `wiki/_backlinks.json` by topic keyword (own GROUND)
2. Select a seed page + build a 5-12 page trail following the connections
3. Write the commentary on why each step connects
4. Save `wiki/trails/<slug>.md`
5. `log.md` append: `## [YYYY-MM-DD] trail | <title>`

## Follow Mode

Reporter cycle:
1. Read `wiki/trails/<trail>.md`
2. Read each page on the trail in order, with key content + the connection to the next step
3. End with a summary of the insight running through the whole trail

## List Mode

All `.md` files in the `wiki/trails/` folder — show title·creation date·page count.

## Human Reviewer Gate

- A create-mode trail that falls outside the 5-12 step range (too short or too long)
- Desk qualitative-review defects of critical/high
