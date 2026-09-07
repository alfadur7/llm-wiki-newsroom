# Agents — SoT for the 5 Roles

This folder consolidates, in a single location, the SoT for the project's five multi-agent roles plus the Universal Cycle skeleton. It is modeled on the role system of a Korean newspaper, and each role is self-contained in its capability boundary, I/O contract, and prompt template.

## The 5 Roles

| Role | SoT |
|---|---|
| Editor-in-Chief | [editor-in-chief.md](editor-in-chief.md) |
| Reporter | [reporter.md](reporter.md) |
| Columnist | [columnist.md](columnist.md) |
| Desk | [desk.md](desk.md) |
| Copy Editor | [copyeditor.md](copyeditor.md) |

For the one-line announce on invocation plus the role-prefix format of the `Agent` `description` argument, see [`commands/README.md` "Announce Before Delegating"](../commands/README.md#convention--announce-before-delegating).

## Layer × Cycle Matrix (design skeleton)

The project's essential design skeleton is a two-axis matrix of **content Layer × Universal Cycle**. Each cell maps to a responsible role.

| Layer | GROUND | APPLY | VERIFY | ADAPT |
|---|---|---|---|---|
| L1 raw | (external) | (external) | format integrity (manual) | re-collect |
| L2-1 source | Reporter | Reporter | Copy Editor + Desk (sub-trigger) | Reporter |
| L2-2 stub | Reporter | Reporter | Copy Editor + Desk | Reporter |
| L2-2 full hub | Columnist | Columnist | Copy Editor + **Desk** | Columnist |
| L2-2 timeline | Columnist | Columnist | Copy Editor + Desk | Columnist |
| L2-3 cluster overview | Columnist | Columnist | Copy Editor + **Desk** | Columnist |
| L2-3 theme contradiction | Columnist | Columnist | Copy Editor + **Desk** | Columnist |
| L2-3 synthesis·trail | Columnist | Columnist | Copy Editor + Desk | Columnist |
| L2-4 root overview·contradiction | Columnist | Columnist | Copy Editor + **Desk** | Columnist |
| Meta (index·log·_clusters·_graph·_backlinks) | (external) | tools/build.py | Copy Editor | tools/build.py |

**Editor-in-Chief**: the meta layer outside the matrix — oversees entry, routing, gates, escalation, and log appends across all cycles.

For Layer definitions and content formats, see [`.claude/layers/README.md`](../layers/README.md). For each content type's page format, authoring, and rubric, see [`.claude/layers/`](../layers/). L2-2 `stub` vs `full hub` is distinguished not by the shape of the output but by the **authoring act** — the definition lives in [`layers/hub.md`](../layers/hub.md) "Authoring acts — stub authoring vs full hub authoring".

The **essential definitions of the four Universal Cycle stages** (what each of GROUND·APPLY·VERIFY·ADAPT is) are the single SoT in [`CLAUDE.md` "Universal Cycle"](../../CLAUDE.md#universal-cycle). This matrix orthogonalizes those four stages against the Layer axis and shows **only the role mapping** — the fact that GROUND·APPLY·ADAPT repeat in the same role cell reflects the pattern of one role performing read·write·rewrite together within its own context (Cognition Principle 1: full context, no message-passing loss — for a content-authoring cycle, the choice of read scope is set by [§ GROUND Ladder](#ground-ladder) below). **Cognition Principle 2**: actions carry implicit decisions — when two roles act on the same area, their outputs embed conflicting implicit decisions, so every capability area has exactly one owning role and multi-role work runs as a sequential chain, not a parallel merge.

## GROUND Ladder

The GROUND column of the matrix above is instantiated as a **ladder that widens from declared grounds toward undeclared relations**. Its ordering principle differs from the VERIFY ladder's (cost↑ × determinism↓): here it is **declared → undeclared → exhaustive** (precision↓ — discovery cost generally rises with it, but cost is not what defines a rung). **Content-authoring cycles only** — guideline editing gets no ladder of its own: the instruction corpus is small (~565 KB of Markdown under `.claude/`) and built from explicit links and a controlled vocabulary, so "re-read each touched file whole + grep the defect's pattern" (the [Guideline Verification Ladder](editor-in-chief.md#guideline-verification-ladder) ADAPT duty) already approximates exhaustion, and there is no cost gradient to justify a ladder.

| Rung | Operation | What it finds | Cost |
|---|---|---|---|
| **R0 anchor** | the mandatory Read·search named by the role prompt or the layer guide (`graph/_dependencies.json` upstream is its machine index) | declared direct dependencies | low |
| **R1 index** | `wiki/index.md` · `wiki/sources/_catalog-<cluster>.md` | structural overview | low — `index.md` is ~1k tokens at this corpus size, so a whole read is affordable; partial read becomes the default once it is not |
| **R2 declared edges** | `wiki/_backlinks.json` · `python tools/query.py graph neighbors·path·explain [--edge-type]` | traversal over relations the build already computed | low |
| **R3 undeclared relations** | `mcp__qmd__query` pre-loaded via `ToolSearch` (where qmd is not installed: `python tools/query.py qmd hybrid·search·vsearch`) | connections no edge declares | medium |
| **R4 exhaustive** | read the whole corpus — 28 files today | everything | **reachable** — `wiki/**/*.md` totals ~78 KB (~20k tokens); re-derive with `python -c "import pathlib;print(sum(len(p.read_bytes()) for p in pathlib.Path('wiki').rglob('*.md')))"` |

- **Rise** — only on an insufficiency signal: a claim with no evidence span secured · an unresolved wikilink · consecutive empty searches. Go straight to the rung the signal points at (sequential exhaustion is not required — an unresolved wikilink goes to R2, a hint of an undeclared relation to R3). Rungs are counted by declaration status, not by kind of operation — a search the layer guide names as part of its GROUND procedure (qmd source identification for a full hub·timeline) is R0 anchor.
- **Stop** — when the evidence the authoring needs is sufficient, or at a cap. **Provisional caps**: 3 consecutive empty results at the same rung ends that rung · 15 total expansion operations (Read·search calls) outside R0 ends GROUND. At a cap without sufficient evidence, take R4 if it is available; otherwise author only what the evidence supports and name the shortfall in the hand-off. The caps are provisional pending measurement — recalibrate once `grounded_at` observations accumulate.
- **`grounded_at` record** — the authoring role (Reporter·Columnist) states its final rung (`grounded_at: R<n>`) in the hand-off, and the Editor-in-Chief carries it into that cycle's defect load (`tools/log_defect.py` optional field). A defect record's rung is the value at the time of authoring — it is **not** updated retroactively when ADAPT (a) later climbs higher, because stopping before that climb is precisely what the indicator measures. Without this axis every under-read defect is classified as an authoring defect, so the only prescription available is "fix the guide" and never "widen earlier".
- **Relation to ADAPT** — [§ ADAPT Escalation](#adapt-escalation) 2nd-round option (a) (widen Read scope) is the recovery-path instance of a rise on this ladder: the rung not climbed on the normal path gets climbed in ADAPT.
- **R4 ceiling** — R4 is one terminal act, not a sequence of expansion operations, so the operation cap above does not bar it. Take it when R0–R3 have not produced the evidence the authoring needs and the corpus still fits the context budget (size in the table above); once it does not fit, R3 is the ceiling.

## Content Verification Ladder

The VERIFY column of the matrix above is instantiated as a **ladder that climbs from the lowest-cost, lowest-determinism stage upward**. The principle: defects that an automated stage will catch are not pushed all the way up to a human cycle. The guideline layer has an isomorphic counterpart — [editor-in-chief.md § Guideline Verification Ladder](editor-in-chief.md#guideline-verification-ladder) — for changes to the instruction SoTs themselves. In the four-loop vocabulary ([CLAUDE.md § The Four Loops](../../CLAUDE.md#the-four-loops)): stages 0–1 are the **inner loop**, stages 2–4 the **outer loop**, and stage 5 is the escalation terminal every loop shares.

| Stage | Owner | Cost | Determinism | Hand-off on failure |
|---|---|---|---|---|
| 0. Post-edit hook | [`.claude/hooks/*.sh`](../hooks/) | 0 | deterministic | lint-chain-guard auto-block / dispatch.sh advisory |
| 1. self-VERIFY₀ (lint judged on own output) | author (Reporter·Columnist) | low | deterministic | hand off to VERIFY₁ after 2 self-attempts on the same cause |
| 2. VERIFY₁ (full deterministic lint) | Copy Editor [`tools/lint.py`](../../tools/lint.py) | low | deterministic | ADAPT₁ → back to author |
| 3. VERIFY₂ (qualitative review) | Desk (6 lenses·persona) | medium | probabilistic | ADAPT₂ → author → back to VERIFY₁ |
| 4. Publish gate | Editor-in-Chief | low | deterministic | 3rd FAIL on same cause → escalate to human |
| 5. Human reviewer gate | the wiki operator | high | — | entered under the conditions in [`CLAUDE.md` "Human Reviewer Gate"](../../CLAUDE.md#human-reviewer-gate) |

The straight-line instances of ladder stages 1·2·3 for L2-3·L2-4 content are in "Standard ADAPT chain" below. The rule for escalating stages when the same cause recurs is in "ADAPT Escalation" beneath that.

**L2-2 stub obligation**: immediately after a cycle that newly authors `wiki/entities·concepts·timelines/*.md`, a Desk VERIFY₂ call is mandatory and automatic. **This applies equally to stubs written as a side product of broken-link fixes or other cycles** — it blocks the pattern where a byproduct flow that skips the stub-authoring SoT entry omits this obligation (the 2026-05-20 incident: Desk verify was omitted for 5 byproduct stubs → 11 defects discovered after the fact). The first-line block for an unaware author is the stub advisory in [`.claude/hooks/dispatch.py`](../hooks/dispatch.py).

## Standard ADAPT chain (L2-3·L2-4 content)

```
[GROUND+APPLY] Columnist — full-context Read in own context + write EDITOR block
   ↓
[SELF-VERIFY₀] Columnist — quantitative lint judged on own output (self-invoked, outside ADAPT counter)
   ↓
Criterion met, or after ≤ 2 self-attempts on same cause → hand off to VERIFY₁
   ↓
[VERIFY₁] Copy Editor — deterministic Rubric (quantitative)
   ↓
PASS? ─ No → [ADAPT₁] Columnist (fix using only the Rubric result) → VERIFY₁
   │ Yes
   ↓
[VERIFY₂] Desk — one qualitative review pass (full-context Read, defect list)
   ↓
0 defects? ─ Yes → Editor-in-Chief gate → publish
   │ No
   ↓
[ADAPT₂] Columnist — address defects
   ↓
[VERIFY₁] Copy Editor regression check
   ↓
PASS + 0 defects → publish / otherwise ADAPT escalation +1
   ↓
3rd FAIL on same cause → Editor-in-Chief escalates to human
```

self-VERIFY₀ is outside the ADAPT counter (the author's self-check *before* hand-off). VERIFY₁ (Copy Editor) always runs regardless of whether self-VERIFY₀ passed — it is a regression safety net that catches the slight difference in check scope between mid-authoring self-lint and post-authoring batch lint.

L2-1 source applies Desk VERIFY₂ when its sub-trigger is met (`[fact] ≥ 7 AND quoted citations ≥ 3`, surfaced automatically as a lint advisory); L2-2 stubs (all 5 kinds at once) apply Desk VERIFY₂ unconditionally.

## ADAPT Escalation

When the same Rubric/lint criterion FAILs consecutively:

| Round | Action |
|---|---|
| 1st FAIL | retry the same procedure (may be transient or a surface omission) |
| 2nd FAIL on same cause | explicitly choose one of (a)/(b)/(c) below, then retry |
| 3rd FAIL on same cause | **escalate to human**, no further iteration this turn |

**2nd-round options** (to remove decision divergence across Claude instances):
- **(a) Widen Read scope** — add adjacent source·adjacent cluster overview·`_backlinks.json` to the Read.
- **(b) Temporarily concede an advisory Rubric grade** — target PASS on required criteria only, and record the advisory-grade shortfall explicitly in lint-report.
- **(c) Narrow target scope** — reduce aggregate → a single cluster/theme, and defer the aggregate to the next turn.

The ADAPT count is managed by the Editor-in-Chief within the turn — `lint-report.md` is regenerated wholesale from `lint.py` stdout on every run, so a mid-turn append to it does not survive. The point at which the report is authored is deferred until after VERIFY passes, because `.claude/hooks/lint-chain-guard.sh` auto-blocks when it detects a chain marker.

## Authoring Responsibilities (production·verification automation layers)

Wiki content is the product of **dual automation** — humans do not type it directly. Three layers each carry a different responsibility.

| Layer | Role·tool | Function | Source of Truth | Escalation |
|------|---------|------|----------------|------------|
| **Deterministic automation** | `python tools/build.py` | Generates AUTO blocks (inside `<!-- AUTO:* BEGIN/END -->`) plus the `graph/_dependencies.json` cascade upstream index (the basis for uniform staleness). Deterministic over its inputs: entity·concept ranking, source lists, backlinks, per-page upstream, etc. | `graph/_clusters.json`·`_graph.json`·`_dependencies.json`·`wiki/_backlinks.json` | script bug → fix `tools/_build/*.py` |
| **Probabilistic automation** | the 4 roles (Reporter·Columnist·Copy Editor·Desk) + Editor-in-Chief gate | Authors and reviews EDITOR blocks. Adherence to the Authoring Guide + self-verification of automated Rubric metrics + Desk qualitative review. Cycle stages are separated (GROUND·APPLY·ADAPT by Reporter·Columnist / quantitative VERIFY by Copy Editor / qualitative VERIFY by Desk) to avoid self-bias. | per-role capability·prompt: [`.claude/agents/`](./) · content standards·Rubric: [`.claude/layers/<source\|hub\|overview\|contradiction\|synthesis\|trail\|timeline>.md`](../layers/) | persistent Rubric shortfall → the Guide·Rubric itself is re-reviewed by the human reviewer |
| **Human reviewer** | the wiki operator | Direction-setting, Rubric·threshold·trade-off judgments, final acceptance. Detailed sentence-level proofreading is not the default job. | project memory·Plan files | top level |

**Key implications**:
- **Production is automated, supervision is human**. The human reviewer's work concentrates on adjusting guidance·conventions, not detailed proofreading.
- **The Authoring Guide·Rubric is the axis that determines quality**. A Claude with no prior knowledge must be able to read only the Guide·Rubric and reproduce the same quality (the Claude reproducibility principle).
- **The feedback loop is the automated Claude ↔ lint ↔ Desk loop**. Humans supervise direction from outside the loop and do not intervene in individual iterations inside it.
- **lint·Desk automated verification is the bridge**. Quantitative goes to the lint Rubric, qualitative to the Desk — the two mechanisms divide the labor and together form the self-bias-avoiding structure.
- **Derived content is a single semi-automated contract**. Every derived type shares one skeleton of scaffolding → gap detection → rewrite-block → Content Verification Ladder, and the only per-type differences are the `role·lint group·roster·enforcement` parameters.

**Scope**: Layer 2-2 full hub·timeline + Layer 2-3 cluster overview·theme contradiction·synthesis·trail + Layer 2-4 overview·contradiction. Layer 2-1 source and Layer 2-2 entity·concept stubs follow the same cycle, including Desk qualitative review — unconditional for stubs (format·attribution·narrative tone), sub-trigger for L2-1 source (Content Verification Ladder above).

## Execution Mechanism (mechanism-invariant)

The matrix and ADAPT chain above are independent of the execution mechanism — whichever mechanism you run on, you only need to preserve the 4 principles in § Change Procedure. The mechanism branch is a **single axis: whether `Agent` is called with a `name`** (resuming a call by `agentId` is a mode within the anonymous mechanism, not a third branch).

| Mechanism | When | Context | `disallowedTools` | Report delivery (measured) |
|---|---|---|---|---|
| **sub-Agent** — anonymous `Agent(subagent_type: <role>)` | **default** for every role invocation (including parallel fanout — spawn N anonymous sub-Agents concurrently) | fresh per invocation; each ADAPT is a re-invocation that re-reads its GROUND. (Resuming by `agentId` carries context forward instead — never for a call whose premise is fresh eyes or isolation, since the resumed agent keeps context that premise excludes) | **enforced** — the role frontmatter applies | the final text (`end_turn`) **reaches the caller automatically** |
| **teammate** — named `Agent(name: ..., subagent_type: <role>)` | **adversarial faction authoring only** (§ below) | persistent across turns | **NOT enforced** — the spawn brief is the only enforcement channel ([editor-in-chief.md](editor-in-chief.md) step 2) | the final text does **not** reach main — main gets only an idle notification; delivery happens only via `SendMessage(to: "main")`. `SendMessage` is a deferred tool: pre-load it via `ToolSearch` in the brief, or the teammate cannot report at all |

### Report delivery

Delivery responsibility sits with the **caller** (the Editor-in-Chief), not the callee — the caller picks the mechanism, so the caller owns the consequences of that pick.

1. **Contract** — the **Report delivery** clause in each role SoT's § I/O Contract defines *what* the reply must contain. A role SoT loads as the sub-Agent's system prompt, so it is not restated in the invocation prompt. For a teammate, the brief must additionally restate the `SendMessage(to: "main")` obligation — left to model discretion, that call is skipped non-deterministically.
2. **Recovery** — a teammate report that never arrives is unsent, not lost. It remains in the transcript: `.claude/projects/<proj>/<session>/subagents/agent-a<name>-*.jsonl` → the `text` of the last `assistant` entry.
3. **Gate** — a missing report is not an agent failure. Do not substitute author self-review — recover it via 2 above. Self-review cannot stand in for Desk VERIFY₂ because of self-preference bias (§ Content Verification Ladder).

In either mechanism, the 4 principles in § Change Procedure (one author · reviewer reads the shared FS directly · `subagent_type` boundary · Editor-in-Chief ADAPT counter) are preserved identically. For the cells the desk.md matrix marks mandatory, Desk VERIFY₂ is non-waivable under any mechanism — self-preference bias exists independent of mechanism, so an independent qualitative review is mandatory.

**Teammate lifecycle** (adversarial faction authoring only): there is **no shutdown tool** — a spawned teammate persists until session end, so spawn teammates only for the faction procedure and keep their count minimal. **Do not reuse a faction teammate for non-adversarial work** — its brief carries a camp-limited mission, and reuse leaks that framing into neutral work. **Do not hand-edit the team config** — it is harness runtime state; a stale entry blocks cleanup and causes name collisions.

### Tool permissions (X-list ↔ frontmatter parity)

**Rule**: when a role's **X — what NOT to do** list forbids using a tool and names it (e.g. "external lookup (WebSearch·WebFetch)"), the role frontmatter `disallowedTools` must list that tool, and vice versa — every `disallowedTools` entry must be justified by an X-list item that names it. `python tools/lint.py meta` checks this parity in both directions.

**Exceptions** (why parity is a rule, not a seal):
1. **Own artifacts** — a role may produce its own artifacts through a path the tool ban does not govern (the Copy Editor authors `lint-report.md` from `lint.py` stdout via the Write tool — its X-list restricts wiki-content authoring without naming Write/Edit); such X-list items state the restriction without naming tool names, so they stay outside the parity check.
2. **Editor-in-Chief dead path** — the Editor-in-Chief normally runs as the main thread, where role frontmatter is never loaded as a restriction; its `disallowedTools` is declared for parity and for the sub-Agent case, but the operative rule is the X-list itself.
3. **Name-blocking is not a seal** — `disallowedTools` blocks the named tool, not the capability (a role could still reach the same effect via Bash). The X-list prose remains the governing rule; the frontmatter is defense-in-depth, and for a **teammate** it is not enforced at all (the brief is the only channel — table above).

**Deferred tools**: some tools — MCP tools (`mcp__*`) among them — are exposed to a role's context **by name only, with no schema**; calling one directly fails. Pre-load any deferred tool an instruction names via `ToolSearch("select:<name>[,<name>…]")` before calling it. A missing pre-load is not an error — it falls back silently to a substitute tool (Grep·Glob), so the violation never surfaces; an instruction that names a deferred tool must therefore specify the pre-load too, **on the read path of the role that reads it**.

### Model routing (frontmatter `model`)

**Rule**: the authoring roles (Reporter · Columnist, `opus`) and the Desk (`fable`) sit in **different model families**, on the hypothesis that a reviewer drawn from the author's family shares its blind spots. That is unmeasured — the one run behind it had no same-family control, so the effect is not separable from "any fresh reviewer"; do not cite it as evidence the family mattered. Both sides must be pinned or the property is silent: pinning only the reviewer loses it the moment the session default moves to that same family. The Copy Editor is pinned down-family (`sonnet`) because its verdict is `lint.py`'s exit code, not the model's judgment. Use family aliases, never version ids — an alias tracks its family's current generation instead of freezing the role on one.

**The Editor-in-Chief carries no `model`** — the orchestrator must follow whatever the operator is running, in both the main-thread and sub-Agent modes of Tool permissions exception 2 above. A missing key is how that is spelled — and it is the one slot a `CLAUDE_CODE_SUBAGENT_MODEL` in the environment can reach, since frontmatter outranks it everywhere else.

**Frontmatter reaches the five named roles only.** The Guideline Verification Ladder's rung-3 reviewer is spawned ad hoc, not from this folder, so its family is set by the caller at invocation and the rule for it lives in [`editor-in-chief.md`](editor-in-chief.md) § Guideline Verification Ladder instead.

**A wrong value is otherwise silent** — it passes both YAML parsing and `claude plugin validate`, surfacing only when the role runs. `python tools/lint.py meta` is what checks this field: every value an alias, the three pinned roles carrying one, and the reviewer's family not an author's.

## Adversarial Faction Authoring

The only procedure that uses named teammates. Rationale: a single author drafting a genuinely contested topic tends to collapse one camp into the other's frame; two persistent authors, each steelmanning one camp from its own sources, keep the frames separate until a fresh synthesizer merges them.

**Activation — all 3 conditions, in order**:
1. **Contested target**: the target (theme contradiction · synthesis · a hub's tension section) has ≥ 2 camps with materially incompatible claims, each camp grounded in ≥ 2 independent sources of its own — and a single-author draft has already produced a recurring Desk lens-1 (bias) or lens-4 (argument quality) defect after ≥ 1 ADAPT round.
2. **Judge**: the **Columnist** judges condition 1 (does each camp's GROUND actually support faction authoring?). Anyone may flag a candidate (Desk defect, Columnist self-report, operator); only the Columnist's judgment counts.
3. **Entry path**: the **Editor-in-Chief activates** the procedure through its routing step — an author must not self-activate mid-cycle.

**7-step procedure**:
1. The Editor-in-Chief defines the faction split (camp A / camp B) and each camp's GROUND scope (source lists — no overlap in advocacy sources; shared factual background allowed).
2. Spawn one named teammate per camp (`Agent(name: "faction-a", subagent_type: "columnist")`), each briefed with: the reply obligation (`SendMessage(to: "main")`, pre-load via `ToolSearch`) + that role's X-list blocks verbatim (frontmatter is not enforced for teammates) + the camp-limited mission.
3. Each faction author drafts its camp's **strongest case** from that camp's own sources — self-acknowledged limitations included. Refutation of the opposing camp is allowed only when grounded, and grounding may reach down to the `raw/` originals (a wiki-page paraphrase is not sufficient ground to declare the other camp factually wrong).
4. Each faction delivers its case via `SendMessage(to: "main")`; on a missing report the Editor-in-Chief recovers it from the transcript (§ Report delivery).
5. The Editor-in-Chief hands both cases + the full GROUND to a **synthesizer** — a fresh anonymous Columnist sub-Agent, bound by 4 rules:
   - never present the factions' agreement as established fact — an agreement between two briefed advocates is still an attributed claim
   - preserve each camp's self-acknowledged limitations — do not substitute the opposing camp's criticism for them
   - a claim that survives in only one faction's case keeps single-camp attribution
   - where the factions contradict on a checkable fact, check the source (down to `raw/`) instead of averaging the two claims
6. **Desk VERIFY₂ on the synthesis — non-waivable.** The faction procedure changes who authors, not what gets verified; it does not substitute for the qualitative gate.
7. Editor-in-Chief gate + cleanup: faction teammates are not reused for other work (lifecycle above); the standard ADAPT chain resumes on the synthesis output.

## Change Procedure

When modifying these 5 SoTs, observe the following 4 principles:

1. **Sequential, NOT parallel** — a straight writer → editor chain. No parallel forking followed by merge. (Even when the execution mechanism is Teams, there is one author — parallelism is only for spawning independent reviewers.)
2. **Full context to editor** — the reviewer too reads all the GROUND material. Prevents message-passing loss. (Under Teams, reading the shared FS directly is this channel — passing a pointer does not substitute for full context.)
3. **Capability boundary explicit** — no encroaching on another role's area (overlapping roles risk hallucination·conflicting decisions).
4. **ADAPT escalation unified** — every verification rejection is also folded into the 1st·2nd·3rd count, preventing infinite loops.

A skeleton change must pass all of: alignment with the newsroom role model · the Cognition principles (full context·sequential) · breadth/depth separation · the 4 principles above.
