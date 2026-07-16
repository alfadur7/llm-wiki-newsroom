# Language Rules

> **English-native engine.** This framework is English throughout — the documentation, the wiki page content, and the engine's fixed page-schema tokens. The schema tokens (`## Summary`, `## Connections`, `## Key Claims`, the evidence markers `[fact]`/`[analysis]`/`[forecast]`, and the relation prefixes `cites:`/`references:`/`contradicts:`/`defines:`) are the literal strings the tools grep for — they are the engine's page schema and must be written in English exactly as shown. (The engine retains a dormant Korean-filename capability for Korean-named entities — see [naming.md](naming.md) — but English is the default everywhere.) Korean **body text** is an optional mode gated behind the `WIKI_LANG=ko` environment variable; English stays the default, and the schema tokens above remain English in both modes.

## Wiki Content

- **Wiki body text is written in English.**
- Frontmatter (YAML) keys (`title`, `type`, `tags`, etc.) and values are in English.
- The `title` value is the page's plain English name (e.g., `title: "Anthropic"`).
- Proper nouns use the entity's standard English name. A non-English entity may keep its native-script filename (per [naming.md](naming.md)), but its `title`/`tags` carry the English form for discoverability.
- Industry abbreviations stay in their conventional English form (LLM, RAG, API, GPU, etc.).
- The page name inside a `[[wikilink]]` must match the filename (English TitleCase / kebab-case, or a native-script filename per the [naming.md](naming.md) convention).
- Section titles (`## Summary`, `## Key Claims`, etc.) are the English schema tokens listed above.

## Prose Style — Natural English Body

A readability discipline for wiki body text and analysis pieces. Keep prose plain and direct.

- **Write verb-first** — make a person, institution, or thing the subject and say what it did, rather than lining up abstract nouns. ✅ "Anthropic outpaced OpenAI in revenue for two straight quarters." ❌ "A continuation of revenue overtaking is observed."
- **One idea per sentence.** Don't stack modifying clauses into a long run; break them up.
- **Prefer the active voice** and plain connectives; avoid nominalizations and double passives.
- **Do not alter facts, figures, proper nouns, evidence grades (`[fact]` · `[analysis]` · `[forecast]`), or quotations** — even when you tighten a sentence, the assertion strength and attribution discipline stay intact.

The semantic judgments (verb-first, inanimate subject, sentence-breaking) are handled by the Desk's qualitative review ([../agents/desk.md](../agents/desk.md)).

## Reviewer Reference

References to the human reviewer (operator) are standardized as **"the wiki operator."** The voice used in Claude's reply is out of scope for this policy.

## Meta-Doc Language Convention

`CLAUDE.md` · `.claude/agents/*.md` · `.claude/commands/*.md` · `.claude/layers/*.md` · `.claude/policies/*.md` · `.claude/operations/*.md` (hereafter meta-docs) are written entirely in English, section headers included.

### Enforcement

`python tools/lint.py meta schema` auto-enforces English section headers on `CLAUDE.md` + `.claude/commands/*.md` — it exits non-zero on any Korean (Hangul) character in their section headers (the `[가-힣]` guard). The convention applies to the remaining meta-doc groups (agents · layers · policies · operations) by convention.

Bundled with CLAUDE.md integrity checks (anchor · file-ref · slash-cmd) and the flat-path guard in the same `meta schema` subcommand. This check is also part of `/wiki-lint`. Run it before committing any change to meta-docs.
