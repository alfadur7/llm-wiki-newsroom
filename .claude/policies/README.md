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
| [claude-guideline-voice.md](claude-guideline-voice.md) | Voice conventions for authoring `.claude/commands/*.md` · `.claude/agents/*.md` · `CLAUDE.md` (no decision rationale, external references, or timestamps in the body) + automatic antipattern detection |
| [no-plan-bloat.md](no-plan-bloat.md) | The duty to avoid bloat and duplication in plan files — absorb into existing sections by default · 5-step self-check · red flags |

## Invocation Convention

- Not read automatically every session — automatic lint detection is the first line of defense against violations
- Read the relevant policy when creating or renaming a file, or making a language decision
- Policy changes require the explicit approval of the wiki operator (see CLAUDE.md "Human Reviewer Gate")
