# Claude Guideline Voice Policy

The voice conventions to follow when authoring `.claude/commands/*.md` · `.claude/agents/*.md` · `CLAUDE.md` (the Claude guideline SoT). Violations fail the voice pass of `python tools/lint.py meta`.

## Principle

A guideline SoT states **only the current policy, procedure, and criteria**. The following do not belong in the body:

- **Decision rationale, option comparisons, introduction timestamps** — tracked in `log.md` (the append-only changelog)
- **External-case references, "equivalent-to," "model-of" phrasing** — absorption rationale goes in the log; the policy body states only the essence
- **Restating a policy already given in a table row as prose** — if the table is the SoT, do not add a body paragraph

The principle is self-contained meaning: a third party should be able to read it without other documents, history, or session context. Decision history accumulates over time and bloats the SoT.

## Auto-Detected Antipattern

`tools/_lint/meta_schema.py::_check_claude_voice_violations` detects these automatically on every `tools/lint.py meta` run (unconditional — not gated by WIKI_LANG). A FAIL blocks the commit. Several cells match English directly (e.g. `Reinforcement N`, `## Changelog`, the external-case `…model` pattern); the Korean-only regexes (옵션/보강/도입/재발) are carried over from the prior corpus and simply never fire on an English corpus. The "Violation example" column glosses what each one matches.

| Category | Regex | Violation example | Resolution |
|---|---|---|---|
| Decision option name | `옵션\s*[A-Z][+]?(?!\s*입장)` | "옵션 E+ 도입" ("adopt option E+") | Move to log.md |
| Reinforcement counter | `(reinforcement\|보강)\s*\d+` | "보강 1" ("reinforcement 1"), "Reinforcement 2" | Remove from body |
| Introduction timestamp | `\d{4}-\d{2}-\d{2}\s*(도입\|시점\|적용)` | "(2026-05-10 도입)" ("(adopted 2026-05-10)") | Move to log.md |
| External case reference | `(Wikipedia\|ProCon\|BERTopic\|Wikidata\|Stack Overflow\|Kialo)[^\n]{0,80}?(등가\|모델\|model)` | "ProCon 모델 등가" ("equivalent to the ProCon model") | Remove from body |
| Benchmark absorption narrative | `외부 벤치마크\s*\d+/\d+` | "외부 벤치마크 5/6 흡수" ("absorbed 5/6 of the external benchmark") | Move to log.md |
| Changelog section header | `^#{2,4}\s*(Changelog\|변경\s*이력\|변경\s*사항\|Change\s*Log)\s*$` | a `## Changelog` section | Move to log.md |
| Recurrence prevention narrative | `재발\s*(방지\|회피)` | "이전 사례 재발 방지" ("preventing a recurrence of an earlier case") | Move to log.md |

**Scope**: `.claude/commands/*.md` · `.claude/agents/*.md` · `.claude/policies/*.md` · `.claude/layers/*.md` · `.claude/operations/*.md` · `.claude/skills/*/SKILL.md` · `CLAUDE.md`. wiki/ and tools/ are out of scope.

**Self-skip**: `.claude/policies/claude-guideline-voice.md` and `.claude/policies/language.md` (they contain antipattern examples).

## Qualitative Review (Editor-in-Chief's domain)

Semantic judgments the regexes cannot catch are surfaced by the Editor-in-Chief in a read pass just before any `.claude/` change is committed. The procedure is in [.claude/agents/editor-in-chief.md](../agents/editor-in-chief.md) § Voice Pass.

Review lenses:

- **Table-row restatement paragraph**: a body paragraph re-narrates the same policy after a table has already stated it
- **Self-containment violation**: the meaning is unclear without knowing another document or the session context
- **Residual decision narrative**: body text on "why this decision was made" rather than the policy essence. Sub-patterns:
  - An explicit `## Changelog` · `## 변경 이력` ("Change History") · `### 변경 사항` ("Changes") section inside a guideline SoT (history's SoT is `log.md` alone — the regex above catches the header)
  - "Reason," "rationale," "design rationale" paragraphs (stating the policy essence in one line is fine — distinguish intent from rationale: "Cap intent — 15 themes is the recommended ceiling for single-page narrative coherence" ✓ vs. "The reason this cap was introduced is to secure persistence as data accumulates..." ✗)
  - "Recurrence-prevention case," "result of a prior cycle," "introduction rationale" narratives

## Resolution

On an auto-detection FAIL:
1. Move the offending phrasing to `log.md` as history (if it is already there, just remove it from the body)
2. Keep the guideline body to policy essence, procedure, and criteria only

`--fix` is not supported — this is a domain of semantic decisions and requires human judgment.
