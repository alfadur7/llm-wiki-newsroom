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

The **essential definitions of the four Universal Cycle stages** (what each of GROUND·APPLY·VERIFY·ADAPT is) are the single SoT in [`CLAUDE.md` "Universal Cycle"](../../CLAUDE.md#universal-cycle). This matrix orthogonalizes those four stages against the Layer axis and shows **only the role mapping** — the fact that GROUND·APPLY·ADAPT repeat in the same role cell reflects the pattern of one role performing read·write·rewrite together within its own context (Cognition Principle 1: full context, no message-passing loss). **Cognition Principle 2**: actions carry implicit decisions — when two roles act on the same area, their outputs embed conflicting implicit decisions, so every capability area has exactly one owning role and multi-role work runs as a sequential chain, not a parallel merge.

## Content Verification Ladder

The VERIFY column of the matrix above is instantiated as a **ladder that climbs from the lowest-cost, lowest-determinism stage upward**. The principle: defects that an automated stage will catch are not pushed all the way up to a human cycle. The guideline layer has an isomorphic counterpart — [editor-in-chief.md § Guideline Verification Ladder](editor-in-chief.md#guideline-verification-ladder) — for changes to the instruction SoTs themselves.

| Stage | Owner | Cost | Determinism | Hand-off on failure |
|---|---|---|---|---|
| 0. Post-edit hook | [`.claude/hooks/*.sh`](../hooks/) | 0 | deterministic | lint-chain-guard auto-block / dispatch.sh advisory |
| 1. self-VERIFY₀ (target-scope lint) | author (Reporter·Columnist) | low | deterministic | hand off to VERIFY₁ after 2 self-attempts on the same cause |
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
[SELF-VERIFY₀] Columnist — target-scope quantitative lint (self-invoked, outside ADAPT counter)
   ↓
PASS, or FAIL after ≤ 2 self-attempts on same cause → hand off to VERIFY₁
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

The ADAPT count is appended per-turn to the "Iteration log" section of `lint-report.md`. The point at which the report is authored is deferred until after VERIFY passes, because `.claude/hooks/lint-chain-guard.sh` auto-blocks when it detects a chain marker.

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
