# Agents — SoT for the 5 Roles

This folder consolidates, in a single location, the SoT for the project's five multi-agent roles plus the Universal Cycle skeleton. It is modeled on the role system of a Korean newspaper, and each role is self-contained in its capability boundary, I/O contract, and prompt template.

## The 5 Roles

| Role | Korean newsroom title | SoT |
|---|---|---|
| Editor-in-Chief | pyeonjipgukjang | [editor-in-chief.md](editor-in-chief.md) |
| Reporter | chwijaegija | [reporter.md](reporter.md) |
| Columnist | nonseolwiwon | [columnist.md](columnist.md) |
| Section Editor | deseukeu (desk) | [desk.md](desk.md) |
| Copy Editor | gyoyeolgija | [copyeditor.md](copyeditor.md) |

For the one-line announce on invocation plus the role-prefix format of the `Agent` `description` argument, see [`commands/README.md` "Announce Before Delegating"](../commands/README.md#convention--announce-before-delegating).

## Layer × Cycle Matrix (design skeleton)

The project's essential design skeleton is a two-axis matrix of **content Layer × Universal Cycle**. Each cell maps to a responsible role.

| Layer | GROUND | APPLY | VERIFY | ADAPT |
|---|---|---|---|---|
| L1 raw | (external) | (external) | format integrity (manual) | re-collect |
| L2-1 source | Reporter | Reporter | Copy Editor + Desk (sub-trigger) | Reporter |
| L2-2 stub | Reporter | Reporter | Copy Editor + Desk | Reporter |
| L2-2 full hub | Columnist | Columnist | Copy Editor + Desk | Columnist |
| L2-2 timeline | Columnist | Columnist | Copy Editor + Desk | Columnist |
| L2-3 cluster overview | Columnist | Columnist | Copy Editor + **Desk** | Columnist |
| L2-3 theme contradiction | Columnist | Columnist | Copy Editor + **Desk** | Columnist |
| L2-3 synthesis·trail | Columnist | Columnist | Copy Editor + Desk | Columnist |
| L2-4 root overview·contradiction | Columnist | Columnist | Copy Editor + **Desk** | Columnist |
| Meta (index·log·_clusters·_graph·_backlinks) | (external) | tools/build.py | Copy Editor | tools/build.py |

**Editor-in-Chief**: the meta layer outside the matrix — oversees entry, routing, gates, escalation, and log appends across all cycles.

For Layer definitions and content formats, see [`.claude/layers/README.md`](../layers/README.md). For each content type's page format, authoring, and rubric, see [`.claude/layers/`](../layers/). L2-2 `stub` vs `full hub` is distinguished not by the shape of the output but by the **authoring act** — the definition lives in [`layers/hub.md`](../layers/hub.md) "Authoring acts — stub authoring vs full hub authoring".

The **essential definitions of the four Universal Cycle stages** (what each of GROUND·APPLY·VERIFY·ADAPT is) are the single SoT in [`CLAUDE.md` "Universal Cycle"](../../CLAUDE.md#universal-cycle). This matrix orthogonalizes those four stages against the Layer axis and shows **only the role mapping** — the fact that GROUND·APPLY·ADAPT repeat in the same role cell reflects the pattern of one role performing read·write·rewrite together within its own context (Cognition Principle 1: full context, no message-passing loss).

## Verification Ladder

The VERIFY column of the matrix above is instantiated as a **ladder that climbs from the lowest-cost, lowest-determinism stage upward**. The principle: defects that an automated stage will catch are not pushed all the way up to a human cycle.

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
| **Probabilistic automation** | the 4 roles (Reporter·Columnist·Copy Editor·Desk) + Editor-in-Chief gate | Authors and reviews EDITOR blocks. Adherence to the Authoring Guide + self-verification of automated Rubric metrics + Desk qualitative review. Cycle stages are separated (GROUND·APPLY·ADAPT by Reporter·Columnist / quantitative VERIFY by Copy Editor / qualitative VERIFY by Desk) to avoid self-bias. | per-role capability·prompt: [`.claude/agents/`](./) · content standards·Rubric: [`.claude/layers/<source\|hub\|overview\|contradiction>.md`](../layers/) | persistent Rubric shortfall → the Guide·Rubric itself is re-reviewed by the human reviewer |
| **Human reviewer** | the wiki operator | Direction-setting, Rubric·threshold·trade-off judgments, final acceptance. Detailed sentence-level proofreading is not the default job. | project memory·Plan files | top level |

**Key implications**:
- **Production is automated, supervision is human**. The human reviewer's work concentrates on adjusting guidance·conventions, not detailed proofreading.
- **The Authoring Guide·Rubric is the axis that determines quality**. A Claude with no prior knowledge must be able to read only the Guide·Rubric and reproduce the same quality (the Claude reproducibility principle).
- **The feedback loop is the automated Claude ↔ lint ↔ Desk loop**. Humans supervise direction from outside the loop and do not intervene in individual iterations inside it.
- **lint·Desk automated verification is the bridge**. Quantitative goes to the lint Rubric, qualitative to the Desk — the two mechanisms divide the labor and together form the self-bias-avoiding structure.
- **Derived content is a single semi-automated contract**. Every derived type shares one skeleton of scaffolding → gap detection → rewrite-block → Verification Ladder, and the only per-type differences are the `role·lint group·roster·enforcement` parameters.

**Scope**: Layer 2-2 full hub·timeline + Layer 2-3 cluster overview·theme contradiction·synthesis·trail + Layer 2-4 overview·contradiction. Layer 2-1 source and Layer 2-2 entity·concept stubs follow the same cycle, but Desk qualitative review is currently a held area for them (its introduction is to be decided after a separate PoC cycle).

## Execution Mechanism (mechanism-invariant)

The matrix and ADAPT chain above are independent of the execution mechanism — whichever mechanism you run on, you only need to preserve the 4 principles in § Change Procedure. **Multi-stage·multi-unit work** (write-chains · multi-source ingest·news fanout · bulk completion of many hubs · bulk defect fixes, etc. — where two or more role stages, or two or more independent units, are involved) uses **Agent Teams (in-process) as the default execution mechanism**, and **falls back to single-session sub-Agents under an infrastructure gate**. **Excluded** (Teams not applied — overhead only): single-unit one-off work · deterministic tool calls (`build`·`export`·`graph`·`lint` checks) · simple one-off reads.

| Mechanism | Status | Behavior |
|---|---|---|
| Agent Teams (in-process) | **default (primary)** | The Editor-in-Chief runs `TeamCreate`, spawns persistent teammates, and orchestrates serially via `SendMessage`. Reviewers read files directly from the shared FS. The author keeps context across ADAPT (minimal re-reads); reviewers are spawned in parallel. |
| Single-session sub-Agent | **fallback** | The parent session invokes a role once via `Agent` and reports back via the final message. Each ADAPT is a fresh re-invocation (re-reading context). |

**Fallback triggers** (automatic switch — any one of): teammate spawn fails · `SendMessage` fails to resolve · the Teams tools (`TeamCreate`/`SendMessage`) are not loaded. If an infrastructure gate blocks Teams from coming up, the same chain runs as single-session sub-Agents unchanged (identical content quality — only the token savings from the author keeping context are not realized).

In either the default or the fallback, the 4 principles in § Change Procedure (one author · reviewer reads the shared FS directly · `subagent_type` boundary · Editor-in-Chief ADAPT counter) are preserved identically. Desk VERIFY₂ is non-waivable under any mechanism — self-preference bias exists independent of mechanism, so an independent qualitative review is mandatory.

**Team lifecycle** (5 roles fixed): the team is **created once per session and reused** — do not repeat `TeamCreate`/`TeamDelete` for every task within a session. The team name (`wiki-newsroom`) and description are fixed values. **Role identity is determined by `subagent_type`**, and the **specific mission is briefed via `SendMessage`** (include the change SoT in GROUND) — do not bake the task into the spawn prompt. config.json is a session runtime product, so **do not reuse it across sessions or pre-populate members** (a non-surviving member becomes a phantom that blocks `TeamDelete` and causes name collisions) — a new session does a fresh `TeamCreate`. **Per-member decision**: **reusing an idle member is the default** (re-brief via `SendMessage`). **A new spawn** is limited to ① **parallel processing** of independent units, ② **independent qualitative review** that needs fresh eyes (to avoid self-bias·anchoring), and ③ **refresh** (accumulated context bloat·changed role guidance). A temporary parallel member whose role is done is cleaned up via **shutdown** to clear overhead. `TeamDelete` runs once, at session end.

## Change Procedure

When modifying these 5 SoTs, observe the following 4 principles:

1. **Sequential, NOT parallel** — a straight writer → editor chain. No parallel forking followed by merge. (Even when the execution mechanism is Teams, there is one author — parallelism is only for spawning independent reviewers.)
2. **Full context to editor** — the reviewer too reads all the GROUND material. Prevents message-passing loss. (Under Teams, reading the shared FS directly is this channel — passing a pointer does not substitute for full context.)
3. **Capability boundary explicit** — no encroaching on another role's area (overlapping roles risk hallucination·conflicting decisions).
4. **ADAPT escalation unified** — every verification rejection is also folded into the 1st·2nd·3rd count, preventing infinite loops.

A skeleton change must pass all of: alignment with the newsroom role model · the Cognition principles (full context·sequential) · breadth/depth separation · the 4 principles above.
