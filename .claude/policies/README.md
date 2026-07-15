# Policies — Global Conventions & Rules

This folder gathers the project's **global conventions** — location, naming, language, platform, index/log format — in a single place. They affect every task, and violations are detected automatically by lint (`tools/lint.py meta schema`, etc.).

## File Index

| File | Contents |
|---|---|
| [directory-layout.md](directory-layout.md) | Project directory structure + separation of auto-generated vs. human-edited files + location rules + the human-edit convention for `cluster_labels.json` |
| [naming.md](naming.md) | Slug/filename conventions (English TitleCase by default, native-script filenames only for non-Latin-script entities, etc.) + avoiding reserved meta-doc names |
| [language.md](language.md) | English body text · English frontmatter keys + the Meta-Doc Language Convention (English headers) |
| [platform.md](platform.md) | Platform conventions such as working around Windows Korean-filename encoding |
| [index-log-format.md](index-log-format.md) | The two-tier structure of `wiki/index.md` + the append-at-bottom convention for `log.md` |

Guideline-authoring voice and bloat control moved to the [`guideline-writing`](../skills/guideline-writing/SKILL.md) skill (`gdl.*`) — operative-rule voice, 5-step bloat self-check, blind review protocol, and the lint-detected antipatterns all live there.

## Invocation Convention

- Not read automatically every session — automatic lint detection is the first line of defense against violations
- Read the relevant policy when creating or renaming a file, or making a language decision
- Policy changes require the explicit approval of the wiki operator (see CLAUDE.md "Human Reviewer Gate")
