# Policies — Global Conventions & Rules

This folder gathers the project's **global conventions** — location, naming, language, platform, index/log format — in a single place. They affect every task, and violations are detected automatically by lint (`tools/lint.py meta schema`, etc.).

## File Index

| File | Sections held |
|---|---|
| [directory-layout.md](directory-layout.md) | Layout · File Naming & Location Rules · The Human-Edit Convention for `cluster_labels.json` |
| [naming.md](naming.md) | Slugs & Filenames · Avoiding Reserved Meta-Doc Names · Homonymous-Abbreviation Disambiguation · Entity Classification · Threshold for Adding an Entity · Threshold for Adding a Concept |
| [language.md](language.md) | Wiki Content · Prose Style — Natural English Body · Reviewer Reference · Meta-Doc Language Convention |
| [platform.md](platform.md) | Windows Non-Latin (e.g. Korean) Filename Handling · Windows Python UTF-8 Output · raw/ Is Not Searchable with the Grep Tool · PowerShell vs Bash · Bash-Tool Redirect/Path Arguments Must Use Forward Slashes · Hook Execution Environment |
| [index-log-format.md](index-log-format.md) | Index Format · Log Format |

Guideline-authoring voice and bloat control moved to the [`guideline-writing`](../skills/guideline-writing/SKILL.md) skill (`gdl.*`) — operative-rule voice, 5-step bloat self-check, blind review protocol, and the lint-detected antipatterns all live there.

## Invocation Convention

- Not read automatically every session — automatic lint detection is the first line of defense against violations
- Which task opens which policy: [`CLAUDE.md` § Instruction Locations](../../CLAUDE.md#instruction-locations) is the SoT — restated here, the two drift apart
- Policy changes require the explicit approval of the wiki operator (see CLAUDE.md "Human Reviewer Gate")
