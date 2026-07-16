# LLM Wiki Newsroom

This wiki is an English-native knowledge base maintained by Claude Code; the example corpus shipped here maps the debate over what "open source" means for AI, but the framework is domain-agnostic. It requires no external API keys — the Python scripts under `tools/` run entirely locally. When the user makes a request in natural language or runs a slash command, these instructions route the work to the appropriate one of the five roles.

---

## Roles

This project operates as a five-role multi-agent system modeled on the staff of a Korean newsroom.

| Role | Essence |
|---|---|
| **Editor-in-Chief** | Meta layer outside the matrix — entry, routing, gating, escalation, logging |
| **Reporter** | Writes L2-1 / L2-2 stubs + broad external exploration (breadth-first parallel) |
| **Columnist** | Writes L2-2 full / L2-3 / L2-4 (integrating its own GROUND, deep sequential) |
| **Desk**[^desk] | Qualitative review of L2-2 full hub·stub / L2-3 / L2-4, plus L2-1 on its sub-trigger (the areas the Rubric does not capture — scope per `desk.md`) — the pre-publish gate |
| **Copy Editor** | Deterministic quantitative checks across all Layers (`tools/lint.py`) |

[^desk]: "Desk" is the newsroom desk — the senior editor who reviews a piece for quality and judgment before it runs (as in "copy desk" / "news desk"). Here it is the pre-publish qualitative-review gate. The five roles are modeled on a newspaper newsroom; the agent and its SoT file are both named `desk`.

Per-role capabilities, prompts, and risk mitigations: [`.claude/agents/`](.claude/agents/) is the SoT.

---

## Universal Cycle

Every workflow in this project maps onto a four-stage cycle — ingest, query, lint, and overview/contradiction rewrite all share the same skeleton.

| Stage | Essence | Owner |
|---|---|---|
| **GROUND** | Read the relevant SoT (observe) | Reporter / Columnist read directly from their own context (avoiding the telephone game) |
| **APPLY** | Write/edit following the observed pattern | Reporter / Columnist write the EDITOR block (preserving the AUTO block) |
| **VERIFY** | Confirm lint/tools PASS (verification) | Copy Editor (quantitative) → Desk (qualitative — scope per the `desk.md` matrix), divided |
| **ADAPT** | On VERIFY failure, return to GROUND | Reporter / Columnist (no qualitative self-review) |

**The 5 invariants** (APPLY stage): read first, follow the pattern, preserve policy, minimal change, stay in scope.

The Layer × Cycle matrix (which role sits in which cell), the Standard ADAPT chain, the escalation procedure, and the Authoring Responsibilities tiering: [`.claude/agents/README.md`](.claude/agents/README.md) is the SoT. The authoring standards per content type and the Evaluation Rubric: [`.claude/layers/`](.claude/layers/) is the SoT (read by Reporter / Columnist on entering the cycle).

---

## Self-Evolution

The guideline layer improves through the same four-stage cycle as content — the loop that proposes, measures, and adopts changes to the instruction SoTs themselves:

| Stage | Content cycle | Guideline self-evolution |
|---|---|---|
| **GROUND** | read the relevant SoT | `mine_feedback` (operator utterances) + `mine_failures` (verifier-grounded defect corpus) |
| **APPLY** | write the EDITOR block | edit the responsible instruction SoT (absorb-by-default) |
| **VERIFY** | Copy Editor (lint) + Desk (qualitative) | Guideline Verification Ladder — lint meta → minimal-edit check → blind review → effect-measurement gate |
| **ADAPT** | fix on defects | severity-ruled re-pass; 3rd same-cause FAIL escalates to the operator |

SoT: workflow + acceptance rule = [`agents/editor-in-chief.md`](.claude/agents/editor-in-chief.md) (§ SoT Self-Evolution Workflow · § Guideline Verification Ladder) · measurement variants = [`operations/proposal-validation-runbook.md`](.claude/operations/proposal-validation-runbook.md) · authoring craft = [`skills/guideline-writing/`](.claude/skills/guideline-writing/SKILL.md). Standing artifacts: the operator-local defect corpus (written by `tools/log_defect.py`, gitignored) · transition records (the accept/reject ledger) · `.claude/memory/` rejected directions. **Adoption always passes the operator gate** — the loop proposes and measures; it never self-adopts.

---

## Directory Structure

```
raw/                    # Immutable source documents (ingest input)
wiki/                   # The content layer Claude maintains · Obsidian vault root
  index·overview·contradiction  (root meta — no frontmatter)
  sources/·entities/·concepts/·timelines/·overviews/·contradictions/·syntheses/·trails/
graph/                  # Graph/cluster artifacts + cluster_labels.json (human-edited)
wiki-export/            # Merged files for Claude.ai Project Knowledge
tools/                  # Python scripts
tests/                  # Regression tests for tools/ and hooks (pytest)
.claude/                # These instructions
  agents/   commands/   layers/   skills/   policies/   operations/   hooks/   memory/
```

The detailed directory layout + the auto-generated vs. human-edited split + placement rules: [`.claude/policies/directory-layout.md`](.claude/policies/directory-layout.md) is the SoT.

---

## Instruction Locations

Each folder has a **single responsibility**; when adding a new instruction, use this taxonomy to decide its exact location. If the classification is ambiguous, explicit approval from the wiki operator is required.

### `.claude/agents/` — 5 Role SoT + Universal Cycle Framework

**Responsibility**: each role's capability boundary, I/O contract, prompt template, and risk-mitigation design + the Layer × Cycle matrix, Universal Cycle, Standard ADAPT chain, and Authoring Responsibilities (README.md).

**When read**: when the corresponding role is invoked (Cognition principle 1 — full-context Read).

**Instructions located here**:
- `editor-in-chief.md` · `reporter.md` · `columnist.md` · `desk.md` · `copyeditor.md` (per-role SoT)
- `README.md` (Layer × Cycle matrix, the four-stage definitions, the standard ADAPT chain, escalation, Authoring Responsibilities)

### `.claude/commands/` — 9 Slash Command SoT + Task Index

**Responsibility**: each slash command's procedure, arguments, output, and per-subcommand sub-procedures (including command-specific sync procedures and mapping rules). README.md holds the Task Index + Convention.

**When read**: when the corresponding command is triggered.

**Instructions located here**:
- `wiki-ingest.md` · `wiki-query.md` · `wiki-lint.md` · `wiki-graph.md` · `wiki-news.md` · `wiki-discover.md` · `wiki-trail.md` · `wiki-timeline.md` · `wiki-export.md`
- `README.md` (Task Index, the "Extend Before Adding" Convention, natural-language usage examples, sub-procedure locations)
- Command sub-procedures (e.g. the contradiction theme mapping and conflict-axis sync rule in `wiki-lint.md`) are the sole responsibility of this folder.

### `.claude/layers/` — Content-Type Authoring & Review SoT

**Responsibility**: the instructions needed to **write and review** each wiki content type (L2-1 / L2-2 / L2-3 / L2-4) at high quality against its prescribed format. Page Format + Authoring + Evaluation Rubric are consolidated into one file per content type.

**When read**: when the Reporter / Columnist enters the cycle + during Desk review.

**Instructions located here**:
- `source.md` (L2-1) · `hub.md` (L2-2) · `timeline.md` (L2-2 standalone timeline) · `overview.md` (L2-3 cluster + L2-4 root) · `contradiction.md` (L2-3 theme + L2-4 aggregate) · `synthesis.md` (L2-3 synthesis) · `trail.md` (L2-3 trail)
- `README.md` (Layer definitions, axis structure, common frontmatter, Root Meta Files Exception)

**What does NOT belong here**:
- Qualitative review procedures (the 6 lenses, personas) — the Desk's sole domain, so [`.claude/agents/desk.md`](.claude/agents/desk.md).
- Command sub-procedures (theme mapping, sync rule) — [`.claude/commands/wiki-lint.md`](.claude/commands/wiki-lint.md).

### `.claude/skills/` — Agent Skills SoT (project-agnostic)

**Responsibility**: Claude Code Agent Skills (each one folder with a `SKILL.md`) — project-independent modules unrelated to any particular content or task type. Two branches coexist: (a) **writing craft** — referenced by the layers via dotted IDs and measured by `tools/lint.py` (accompanied by `criteria.json` + `checks.py`). (b) **coding discipline** — a behavioral skill that fires at authoring time when writing `tools/` Python (not lint-measured; `SKILL.md` only).

**When read**:
- **Explicit Read** (in-project, primary): the layers' mapping table and the craft skill specified by the agent prompt, on the Columnist / Desk entering the cycle.
- **Auto-fire**: any other writing/coding/review task that matches a skill's `description` (the description follows the auto-discovery format, so both paths coexist).

**Instructions located here**:

*Writing craft* (each skill = one folder of `SKILL.md` + `criteria.json` + `checks.py`, referenced by layers' dotted IDs, lint-measured):
- `journalism-writing` (`jrn.*`) — journalism and argumentation (inverted pyramid, Toulmin, Hegelian dialectic, BBC impartiality)
- `consulting-writing` (`con.*`) — management consulting (McKinsey SCR, MECE, BCG bold-bullet)
- `encyclopedia-writing` (`enc.*`) — encyclopedic neutrality (NPOV, summary style, wikilink conventions)
- `scholarly-citation` (`cit.*`) — verifiable attribution and citation (claim atomization, evidence grading, citation typing, anchoring)
- `guideline-writing` (`gdl.*`) — guideline-authoring craft for the instruction layer itself (operative rule vs recital, MUST/SHOULD/MAY, pruning, bloat control, blind review; the deliberation-narrative detectors run in `lint.py meta`)

*Coding discipline* (`SKILL.md` only, not lint-measured):
- `ponytail-coding` — lazy-senior code restraint (the YAGNI ladder, reuse first, root-cause fixes). Divides labor with karpathy-guidelines (assumptions, success criteria) and `/simplify` (after-the-fact cleanup).

**What does NOT belong here**:
- Content-type page formats, section names, execution order — [`.claude/layers/`](.claude/layers/) (skills cover craft only; the layers apply it to this project).

### `.claude/policies/` — Global Policies

**Responsibility**: conventions affecting the **whole wiki** — directory, naming, language, platform, index/log format, and so on. On a violation, automatic lint detection is the first line of defense.

**When read**: when creating a new file, renaming, or making a language decision (policy changes require explicit approval from the wiki operator).

**Instructions located here**:
- `directory-layout.md` (directory structure + the `_` prefix and placement rules + the `cluster_labels.json` human-edit convention)
- `naming.md` (slug and filename conventions + Reserved meta-doc names + the person-stub threshold)
- `language.md` (English body text + English frontmatter keys + Meta-Doc English headers + Prose Style avoidance of translationese; Korean body text is an optional `WIKI_LANG=ko` mode)
- `platform.md` (Windows non-Latin filename encoding workaround)
- `index-log-format.md` (the two-tier structure of `wiki/index.md` + `log.md` append-at-bottom)
- `README.md` (file index + invocation convention)

Guideline-authoring voice and plan-bloat control are craft, not policy — they live in the `guideline-writing` skill (`gdl.*`).

### `.claude/operations/` — One-Time Procedures & Infra Setup

**Responsibility**: new-device setup, infra-token renewal, and one-off migration procedures. Rarely read, but the sole SoT when needed.

**When read**: on infra changes (adding a device, renewing a token, etc.).

**Instructions located here**:
- `mobile-inbox-setup.md` (one-time setup for mobile share-sheet → GitHub Contents API)
- `gap-detection-rollout.md` (the rollout plan for gap diagnosis, automatic backfill, and separating the operator surface + the SoT for thresholds, priorities, and the domain set)
- `graph-hosting-setup.md` (setup for publicly deploying the graph browser's `_site/` artifact to Cloudflare Pages)
- `codebase-audit-runbook.md` (the multi-agent batch procedure for ultrareviewing tools/ code and .claude/ instructions — group decomposition, review dimensions, adversarial verify, the mechanical/gated application policy)
- `staleness-reground-runbook.md` (the batch procedure for re-grounding stale derived narratives surfaced by `/wiki-lint staleness` — per-type pipeline, Desk gate, verification, recurrence pitfalls)
- `proposal-validation-runbook.md` (the batch procedure for measuring the effect of self-evolved guideline changes — three variants by type (desk-judged blind rewrite × blind desk, behavioral probe task, lint-scored before/after); the acceptance rule lives in `agents/editor-in-chief.md` step 6)

### `.claude/hooks/` — Auto-Block & Guard Shell

**Responsibility**: detect harness events and automatically block or give feedback. The user of this folder (Claude) never reads it directly — the harness invokes it automatically.

**Activation**: in `.claude/settings.json`, the hook `command` must be of the form `bash .claude/hooks/<name>.sh` (the `bash` prefix is mandatory). The Windows shell cannot run a bare `.sh` directly, so without the prefix every hook is silently disabled.

**Instructions located here**:
- `lint-chain-guard.sh` (detects the lint stdout chain marker → blocks writing the report)
- `dispatch.sh` + `dispatch.py` (the single Write|Edit pre/post dispatcher — parses stdin once, merges simultaneously-firing advisories into a single payload, with a shell fallback when python3 is absent. Consolidated responsibilities:)
  - guard: exit-2 block when the per-target drift blocks in `lint-report.md` are asymmetric
  - guard: exit-2 block on direct Write|Edit of auto-generated build artifacts (`wiki/index.md`, `graph/_*.json`, etc.) or `raw/` originals — steering you to fix the input and regenerate (re-derivation, human-edited files, and queue files are exceptions; the full list is in `dispatch.py`)
  - advisory: after writing a stub, recommend `python tools/build.py` reconciliation + Desk VERIFY₂ (`wiki/entities·concepts·timelines/*.md` — structural prevention of the 2026-05-09 / 05-20 incidents)
  - advisory: after editing L2-2 full hub, timeline, L2-3, or L2-4, recommend target-scope `python tools/lint.py <group> <target>` self-VERIFY₀
  - advisory: for `*/plans/*.md`, the 5-step self-check, the 4 red-flag types + for `.claude/{agents,commands,layers,policies,operations}/` SoTs and CLAUDE.md (skills·hooks·memory excluded), the Guideline Verification Ladder + a diff bullet-depth check (helper `check_bullet_depth.py`)
  - advisory: on editing a desk-judged prose-craft SoT (`.claude/layers/*.md`, `agents/desk|reporter|columnist.md`), recommend the proposal-validation measurement before adoption (SoT: `operations/proposal-validation-runbook.md` + `agents/editor-in-chief.md` step 6)
  - advisory: on Write of a script-like temporary file directly under the project root, recommend a temp directory (structural prevention of the 2026-05-08 incident)
  - advisory: on writing or modifying `tools/**/*.py` or `.claude/hooks/*.py|sh`, recommend loading and applying the `ponytail-coding` skill (the authoring-time code-restraint reflex — the SoT is `skills/ponytail-coding/SKILL.md`; the rule body is not duplicated here)

### `.claude/memory/` — Local Memory

**Responsibility**: project-specific local records of feedback and decisions (separate from the system auto-memory).

**When read**: on entering related work.

> **Note:** local memory is gitignored and created on first use; notes accumulate here as you operate the wiki.

**Instructions located here**:
- Local notes such as `feedback_*.md`

---

## Human Reviewer Gate

In the following situations, do not proceed automatically:
- A 3rd ADAPT FAIL for the same reason
- A new cluster slug (`graph/cluster_labels.json`) / a new contradiction theme slug
- A new person entity stub (only for core figures cited many times and appearing across multiple sources — `.claude/policies/naming.md` person-stub threshold)
- Publishing L2-4 root content
- Changes to the skeleton of a guide, rubric, or matrix
- External commit / push
- A large body rewrite (>50% changed)
