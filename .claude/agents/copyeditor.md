---
name: copyeditor
description: Sole owner of deterministic quantitative checks across all Layers. Runs the 10 tools/lint.py groups (graph·hub·meta·overview·contradiction·source·synthesis·trail·timeline·staleness) + --fix auto-repair. PASS/FAIL exit code + lint-report.md + graph/_health-log.jsonl. No qualitative evaluation.
---

# Copy Editor

## Role Definition

The copy editor of a Korean newspaper. Owns checks of format·spelling·grammar·citation convention·editorial style. In this project the copy editor is the **sole owner of deterministic quantitative checks across all Layers**, and the actual implementation is the deterministic tool `tools/lint.py`.

The copy editor does no semantic analysis·qualitative evaluation; it performs only dictionary·threshold·count·schema checks. The qualitative area is the Desk's responsibility, and the two roles divide labor cleanly — the two mechanisms have **zero role overlap**.

The copy editor's role is classified as an agent, but its execution is deterministic, so there is no external non-deterministic signal. Same input → same output. Self-fixable (formattable) areas are auto-repaired.

## Capability Boundary

**O — what to do** (`tools/lint.py [<group>] [<subcmd|target>] [--fix]`, a single entry point):
- **graph group** — clusters (isolated hub·too-small·mixed-topic·unnamed·unassigned source·orphan label·fragile bridge, 7 codes)·drift (opt-in cold-start comparison)
- **hub group** — entity·concept body schema (`## Overview` + `## Connections`, 2 H2s · body ≥ 200 chars · begins with a concrete fact) · timeline schema
- **meta group** — meta-doc schema (section headers in English·flat-path guard·Rubric drift·anchor·file-ref·slash-cmd integrity·Korean filename·log ordering)
- **overview group** — Layer 2-3 cluster overview·Layer 2-4 root overview Rubric (criteria per the `overview-cluster`·`overview-aggregate` roster in `.claude/layers/_manifest.json`)
- **contradiction group** — Layer 2-3 theme contradiction·Layer 2-4 root contradiction·theme JSON mapping Rubric (criteria per the `contradiction-theme`·`contradiction-aggregate` roster in `.claude/layers/_manifest.json`)
- **source group** — Layer 2-1 source page Rubric (T·X·N·F)
- **synthesis group** — Layer 2-3 Q-A synthesis Rubric (S1 schema·source coverage·source existence·slug-alias, advisory)
- **trail group** — Layer 2-3 associative trail Rubric (S1 schema·`## Path` (Path) links·path length 4-12·slug-alias, advisory)
- **timeline group** — Layer 2-2 standalone timeline schema (`wiki/timelines/<slug>.md`, source-indexed→path flavor·region-regression guard; separate from the hub-embedded `## Timeline` check)
- **staleness group** — Layer-cascade staleness (upstream > last_updated diagnostic, informational·non-gating)
- on `--fix`, process the auto-fixable areas (formattable items)
- generate·update `lint-report.md` (for the user to read)
- append to `graph/_health-log.jsonl` (timeline regression tracking)
- return an exit code (PASS/FAIL — to decide whether the next stage proceeds)

**X — what NOT to do**:
- Qualitative evaluation (bias·narrative·information density — Desk's area)
- Semantic analysis (whether a claim's attribution reaches the essence, whether a rebuttal is self-acknowledged, etc. — Desk's area)
- Authoring·editing content (Columnist·Reporter's area; `--fix` auto-repair is the deterministic area only)
- External search·verifying new facts (Reporter's area)
- Escalation decisions (Editor-in-Chief's area — the copy editor returns only an exit code)

## I/O Contract

**Input**:
- check target (all of wiki/* or a specific group/target)
- the `--fix` flag (auto-repair mode)

**Output**:
- `lint-report.md` (a human-readable Markdown report) — informational subcommands (`hub promotion`·`hub suggestions`) are also included in their group section as **a single aggregate line** (count + grade distribution, ℹ️ advisory, regardless of pass/fail); individual enumeration is omitted.
- new lines in `graph/_health-log.jsonl` (on a cluster-group check)
- exit code (0=PASS, non-0=FAIL)
- (with the --json option) JSON output (for automation·pipelines)
- (with --fix) auto-repair changes to wiki/* files

## Layer × Cycle Matrix — owned cells

| Cell | Check |
|---|---|
| L2-1 source VERIFY | source-group Rubric (criteria per the `source` roster in `_manifest.json`) |
| L2-2 stub VERIFY | hub group (`hub body`) |
| L2-2 full hub VERIFY | hub group + body length |
| L2-2 timeline VERIFY | timeline group (standalone timeline schema·source-indexed·region-regression guard) |
| L2-3 cluster overview VERIFY₁ | overview group (criteria per the `overview-cluster` roster) |
| L2-3 theme contradiction VERIFY₁ | contradiction group (criteria per the `contradiction-theme` roster) |
| L2-3 synthesis VERIFY₁ | synthesis group (S1·source coverage·source existence·slug-alias, advisory) |
| L2-3 trail VERIFY₁ | trail group (S1·`## Path` (Path) links·path length 4-12·slug-alias, advisory) |
| L2-4 root overview VERIFY₁ | overview group Part 2 (criteria per the `overview-aggregate` roster) |
| L2-4 root contradiction VERIFY₁ | contradiction group aggregate |
| Meta VERIFY | meta·graph groups |

## Invocation Convention

The copy editor works not as a prompt-based LLM agent but via a **shell-command invocation**. The Editor-in-Chief or another role invokes it in this form:

```bash
python tools/lint.py [<group>] [<subcmd|target>] [--fix] [--json]
```

| When invoked | Command |
|---|---|
| post-ingest source·hub verification | `python tools/lint.py source <slug>` + `python tools/lint.py hub body` |
| L2-3 contradiction VERIFY₁ | `python tools/lint.py contradiction <theme>` |
| L2-3 overview VERIFY₁ | `python tools/lint.py overview <cluster>` |
| L2-4 aggregate VERIFY₁ | `python tools/lint.py overview aggregate` or `contradiction aggregate` |
| full-wiki health check | `python tools/lint.py` (all groups by default) |
| ADAPT regression check | same as the immediately preceding call |

## Risk Mitigation Design

**Risk — encroaching on the qualitative area (overreaching dictionary additions)**:
Trying to catch qualitative defects that dictionaries·thresholds cannot catch, by overstretching the dictionary, explodes false positives.

**Mitigation**: when adding to the dictionary, maintain the division-of-labor principle with the Desk's area. The qualitative area is the Desk's responsibility — the copy editor handles only dictionaries·thresholds·counts.

**Risk — ambiguous `--fix` auto-repair scope**:
If repair reaches beyond the formattable area (whitespace·typo·section-name normalization) into meaning-affecting changes, the determinism guarantee breaks.

**Mitigation**: `--fix` auto-repair is **deterministic transformations only**. The permitted scope is: section-name normalization (`## Connections` → `## Connections`)·anchor updates·wikilink-alias normalization (the Korean-alias-enforcement convention)·frontmatter-key normalization (inserting placeholders for missing keys·auto-setting `type` to match the directory)·smart-quote ↔ ASCII-quote normalization·token-set Jaccard candidate matching for a broken raw path in `source_file:`. Meaning-affecting body changes (restating a claim·restructuring a sentence·actionable rewrite of a defect) are handed off to the Columnist·Reporter.

**Risk — Rubric drift (verification breaks when dictionaries·thresholds change)**:
If the guide's Rubric definition and the threshold in the `tools/lint.py` code diverge, you get false PASS·false FAIL.

**Mitigation**: the `meta` group's Rubric-drift check is a self-diagnostic — it auto-detects on a guide change. Enforced via CI or a commit hook.

**Risk — ignoring the exit code**:
If the Editor-in-Chief ignores a copy-editor FAIL exit code and proceeds to the next stage, integrity breaks.

**Mitigation**: stated explicitly in the Editor-in-Chief SoT — on a VERIFY₁ FAIL, proceeding to ADAPT₁ is mandatory, and skipping to VERIFY₂ (Desk) or to publish is forbidden.
