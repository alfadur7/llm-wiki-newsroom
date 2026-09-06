# `/wiki-lint` sub-procedure — Contradiction Theme Mapping (full re-derivation)

Not a slash command — a sub-procedure of [`/wiki-lint`](wiki-lint.md), reached from `contradiction theme --fix`. Invoking it directly runs nothing.

This guide prescribes the procedure for reading all claims in `_contradictions.json` and generating `_contradictions_themes.json` (the theme ↔ claim mapping SoT). Since the output is **structured JSON, not markdown prose**, journalism · consulting form does not apply (unlike overview authoring). Schema conformance · contradiction-axis accuracy · self-validation are the core.

A Claude with no prior knowledge must be able to read this guide alone and reproduce the same quality · structure.

Read before working:
- [`wiki-lint.md` → `## Sub-procedure: Conflict Axis Sync Rule`](wiki-lint.md#sub-procedure-conflict-axis-sync-rule) (SoT hierarchy · cross-assignment principle)
- `wiki/contradictions/_contradictions.json` (main input — all claims; for structure see "Input Data Structure" below)
- For Phase 2 only, `wiki/contradictions/_contradictions_themes.json` (carrying over the Phase 1 output)
- As needed, `wiki/sources/<slug>.md` (source originals — Phase 2 Priority Read targets; for structure see "Source File Structure" below)

---

### Input Data Structure

#### `_contradictions.json` — Main Input

The top level is a JSON array, and each element is a record with the fields below. `python tools/build.py contradictions` auto-generates it by extracting `- contradicts: [[Hub]] — desc` lines from the `## Connections` section of source pages.

```json
{
  "id": "a709b575",
  "source": "sources/agentic-ai-kill-saas-debate.md",
  "claim": "[[osi-open-source-ai-definition]] requires training-data disclosure, whereas this document argues that releasing open weights alone is sufficient to count as open.",
  "status": "open",
  "type": "real",
  "type_score": 0.6,
  "evidence_strength": 0.42
}
```

| Field | Meaning | Use in theme derivation |
|---|---|---|
| `id` | First 8 chars of the SHA1 hash of the claim text. The key referenced by `claim_ids` in `_contradictions_themes.json` | **Must** use this value verbatim |
| `source` | Path of the Layer 2-1 source file this claim was extracted from (`sources/<slug>.md`) | The actual Read target during Priority Source Read |
| `claim` | The desc part of the `## Connections` `- contradicts: [[Hub]] — desc` line (after the prefix is removed). The contradiction is summarized in 1–2 sentences | The primary basis for judging the contradiction axis |
| `status` | Currently fixed at `"open"` | Unused |
| `type` | Auto-classification result — one of 4 values `real` · `superseded` · `related` · `soft` (explained below) | Priority-Read selection · auxiliary grouping judgment |
| `type_score` | Type-category keyword-match score 0.0–1.0 (sum of regex weights capped at 1.0) | Lower = weaker classification signal (re-classification candidate) |
| `evidence_strength` | Phase 2 meta-based evidence strength 0.0–1.0 — anchor presence 0.30 + source recency 0.15 + ratio of `## Key Claims` primary sources 0.40 + target hub type 0.15 | Higher = strong contradiction (priority `## Representative Evidence` candidate). Lower = weak signal (consider drop) |

**Orthogonality of the two score dimensions**:
- High `type_score` + low `evidence_strength` → clear keyword match + weak evidence (weasel risk)
- Low `type_score` + high `evidence_strength` → ambiguous classification + strong evidence (re-classification priority)
- Both ≥ 0.6 → strong-contradiction candidate
- Both ≤ 0.3 → soft signal, consider drop

**The 4 values of the `type` field**:
- **`real`**: a clear contradiction · tension — two actors/positions in opposite directions. **The primary target for preliminary theme placement**
- **`superseded`**: a past issue resolved by a timeline update — mostly fragmentary or one-off issues
- **`related`**: a reference/complement relation, not a contradiction — the claim body tends to state "not a contradiction" · "complement" · "similar case." Mostly fragmentary
- **`soft`**: auto-classification failed (the rules could not decide any of {real, superseded, related}). **Emitted with `type_score=0.0` and worth re-reviewing in Phase 2 Priority Read** — a soft claim with high `evidence_strength` is a re-classification priority

#### Source File Structure — `wiki/sources/<slug>.md`

A Phase 2 Priority Read target. Each source page consists of frontmatter + 4 H2 sections:

| Section | Content | Use in theme determination |
|---|---|---|
| `## Summary` | A 2–4-sentence summary of the article · document | The fastest entry point for grasping original-text context |
| `## Key Claims` | A bullet list of key claims | Confirm which claim a contradiction derives from |
| `## Key Quotes` | Quotations from the original text | Confirm speaker · grounds |
| `## Connections` | `cites:`/`references:`/`contradicts:`/`defines:` prefix lines. The `contradicts:` line is the extraction source for `_contradictions.json` — grasp other claim context within the same source + infer the related theme · axis |

Priority-Read priority: `## Summary` → `## Key Claims` → `## Connections`. `## Key Quotes` is auxiliary.

---

### Purpose & Scope

- **Trigger**: the Claude probabilistic-automation stage when `/wiki-lint contradiction theme --fix` runs
- **Output**: `wiki/contradictions/_contradictions_themes.json` (full overwrite every time)
- **Responsibility scope**: claim → theme derivation and mapping only. Authoring theme.md bodies · Rubric judgment are outside this guide's scope
- **Input scope**: `_contradictions.json` is the main input. Reading `wiki/sources/<slug>.md` is allowed as needed (Phase 2 Priority Read). Phase 2 carries over the Phase 1 output (`_contradictions_themes.json`)

#### Two-Phase Pipeline

Execution is a sequential pipeline of two Phases. Each Phase runs independently, and the human reviewer reviews the Phase 1 output before instructing Phase 2 to proceed.

| Phase | Purpose | Output characteristics |
|---|---|---|
| **Phase 1 — Filter & Survey** | Identify trivial fragmentary + judgment-ambiguous claims (selecting Phase 2 focused-analysis targets) | Preliminary themes (fine) + confirmed `other-fragmentary` + `unassigned` (source-Read targets) |
| **Phase 2 — Converge with Source Detail** | Derive coarse contradiction axes from Phase 1's focused claims + necessary source-detail Reads | Themes within 15 + final `other-fragmentary` |

**Phase linkage**: Phase 2 carries over Phase 1's `_contradictions_themes.json` — keeps `other-fragmentary`, resolves `unassigned` via source Reads, and reconstructs preliminary themes into coarse axes. Not strictly stateless but a **sequential pipeline** model.

---

### Output Schema (Common)

#### Field Definition

| Field | Type | Constraints |
|---|---|---|
| `derived_at` | string | `YYYY-MM-DD`. Work date (today) |
| `derived_by` | string | Always fixed at `"claude"` |
| `phase` | integer | `1` or `2`. The Phase this run performed |
| `source_count` | integer | Total record count in `_contradictions.json`. A verification reference value |
| `themes` | object | dict of `{slug: theme_obj}`. slug is `[a-z0-9-]+` (kebab-case English) |
| `themes.<slug>.name` | string | English name by default (Korean under `WIKI_LANG=ko`). A concise expression suggesting the issue's contradiction |
| `themes.<slug>.claim_ids` | array of string | References the `id` field of `_contradictions.json`. No duplicates |
| `unassigned` | array of string | **Phase 1**: claim ids that need source-detail Reads in Phase 2 because judgment is ambiguous. **Phase 2**: an empty array in principle (final output) |

#### `unassigned` Field — Phase-Specific Role

- **Phase 1**: a signal that "this claim seems contentious, but the contradiction axis cannot be judged from the claim text alone." A Phase 2 Priority Read target list.
- **Phase 2**: after resolving via source Reads, reassign those claims to a theme or `other-fragmentary`. The final `unassigned` should be an empty array.

#### Full Example — Phase 1 (Filter & Survey Output)

Phase 1 splits into three: fine-grained preliminary themes + separated `other-fragmentary` + `unassigned` (judgment-ambiguous):

```json
{
  "derived_at": "2026-04-19",
  "derived_by": "claude",
  "phase": 1,
  "source_count": 169,
  "themes": {
    "open-weights-vs-open-source": {
      "name": "Open weights alone vs full open-source AI",
      "claim_ids": ["7a2b9fd4", "c29c232f", "88600a2a"]
    },
    "training-data-disclosure-requirement": {
      "name": "Training-data disclosure required vs optional",
      "claim_ids": ["e28a00d8", "4ceaea7b"]
    },
    "other-fragmentary": {
      "name": "Residual one-off issues",
      "claim_ids": ["0aa4a179", "9bbc4946", "4a56999e"]
    }
  },
  "unassigned": ["4f618e0d", "efbcd81c", "b66b3eab"]
}
```

#### Full Example — Phase 2 (Converge with Source Detail Output)

Phase 2 produces coarse axes within 15 + `other-fragmentary`. `unassigned` must be an empty array:

```json
{
  "derived_at": "2026-04-19",
  "derived_by": "claude",
  "phase": 2,
  "source_count": 169,
  "themes": {
    "open-source-ai-definition-gap": {
      "name": "OSI open-source AI definition vs vendor open-weights claims",
      "claim_ids": ["3a7b12c4", "8e0f2901", "b42a55e1"]
    },
    "open-washing-licensing-tension": {
      "name": "Open-washing vs genuine open licensing",
      "claim_ids": ["17ab3f9d", "2c81ef44"]
    },
    "other-fragmentary": {
      "name": "Residual one-off issues",
      "claim_ids": ["9f2ac8b0"]
    }
  },
  "unassigned": []
}
```

**Full-coverage principle**: every input claim must be included in at least one theme's `claim_ids` or registered in `unassigned`.

---

### Core Principles

#### 1. Full Claim Coverage

Every claim id in the input must appear in at least one theme or `unassigned`. Count verification:
```
|{id | id ∈ themes[s].claim_ids for some s}| + |unassigned| == source_count
```
No skipping.

#### 2. Domain-Context Grouping — No Keyword Match

Group by the **issue's logical structure**, not by surface keywords in the claim text. Belonging to the same theme means:
- Contributing to the **same contradiction axis** (e.g., "vendor claim vs empirical research," "regulation tightening vs innovation hindrance")
- Even different-time statements by the **same actor/organization/person** belong to the same theme if the change of stance is the issue
- Pieces of evidence showing the **opposing perspective of the same phenomenon**

Do not group merely because "AI" is a common keyword.

#### 3. Cross-Assignment Allowed (Explicit Evidence Only)

The same id may appear in multiple themes' `claim_ids`. Multi-assign only claims that clearly span two issue axes. Do not overuse.

#### 4. Theme Granularity — Phase-Differentiated

| Criterion | Phase 1 (Filter) | Phase 2 (Converge) |
|---|---|---|
| **Preliminary/core theme lower bound** | 2 | **5** (core-issue exception — Core Principle 5) |
| **Preliminary/core theme upper bound** | No limit | **50 advisory** (single-axis exemption always active; the body's `## Representative Evidence` is a 5–7-bullet authoring target inside the lint S2 band of 3–7, upper bound strict) |
| **Total theme count upper bound** | No limit | **15 recommended (soft)** — including `other-fragmentary`. Adding a new theme slug is a dual-approval gate (Editor-in-Chief 1st + wiki operator 2nd) |
| **`other-fragmentary`** | Usable | Always exists (empty claim_ids allowed) |

`other-fragmentary` is an exception to the granularity upper/lower bounds. As a residual-absorption bucket, it has no size limit.

Cap intent — theme 15 is a narrative-coherence recommendation line for the single L2-4 aggregate page `wiki/contradiction.md`; claim 50 is a diagnostic signal for the single-axis nature of a theme MD. A theme MD body is a narrative selection, so even attempting 50+ claims has little effect on body length.

#### 5. Core-Issue Exception (Phase 2 Only)

In Phase 2, themes with fewer than 5 claims are in principle absorbed into `other-fragmentary`. However, if **one or more** of the 3 conditions below holds, keeping it as an independent theme is allowed:

- **(a) An independent actor's self-contradiction · duality**: the internal contradiction of a single organization/person is the essence of the issue. The case where merging dilutes the actor
  - Applies: `anthropic-dual-strategy` (2 claims) — Anthropic's public stance of "transparency · safety" vs the duality of its "closed · commercial strategy." Absorbing it into another theme (e.g., general AI-safety discourse) loses the **actor-specific duality**
  - Does not apply: `broadcom-vmware-licensing-tension` (2 claims) — a region-by-region pricing-strategy choice is not a self-contradiction but a **difference of business judgment**. → other-fragmentary
- **(b) Core-thesis dilution on absorption**: the case where merging into an adjacent theme makes the contradiction axis itself disappear or demotes it to residual fragmentary
  - Applies: a specific issue is a clear "A vs B" contradiction, but absorbing it into a broader theme dissolves it into "general AB discussion," losing the contradiction
  - Does not apply: merely an emotional judgment that "it'd be a shame to absorb it"
- **(c) Meta-discourse**: a meta-level dispute outside the domain, such as a methodology · governance issue of this wiki project itself
  - Applies: 3+ wiki-self disputes such as wiki-building methodology · AI-writing protocols
  - Does not apply: `karpathy-wiki-methodology` (2 claims) — an external content methodology that entered the wiki, **not the wiki's own governance**. On a borderline call, strict interpretation puts it in other

Exception application is **only when explicit argumentation is possible**. Do not overuse. When the boundary is ambiguous, absorb into `other-fragmentary`.

#### 6. Other-Fragmentary Handling Rule

- Every theme must have **contentiousness** (contradiction · opposition · tension). No mere topic groupings
- `other-fragmentary` is the **residual-absorption bucket**:
  - Phase 1: weakly-contentious one-off claims (a single event · a time difference · a simple fact check, etc.)
  - Phase 2: keep Phase 1 fragmentary + absorb themes below the lower bound of 5 that are not core-issue exceptions
- Every theme other than `other-fragmentary` has a **clear single contradiction axis**

#### 7. Slug·Name Naming Criteria

- **slug**: `[a-z0-9-]+` (kebab-case English). 2–5 words. Suggests the contradiction axis
  - Good: `ai-coding-productivity-debate`, `stablecoin-cbdc-tension`
  - Avoid: `topic-1`, `ai`, `misc-issues`
  - **Reserved word**: the bare slugs `theme` (collides with the `/wiki-lint contradiction theme` subcommand) and `aggregate` (collides with the L2-4 root target) are forbidden. `tools/_lint/contradiction_theme.py`'s `RESERVED_SLUGS` outputs FAIL on violation.
- **name**: English by default (Korean under `WIKI_LANG=ko`), concise. Make the contradiction · tension · dispute apparent
  - Good: `Open weights alone vs full open-source AI`, `Open-washing vs genuine open licensing`
  - Avoid: `AI issues`, `licensing-related`

---

### Execution Order

#### Phase 1 — Filter & Survey

**Purpose**: separate trivial fragmentary + select claims needing source-detail Reads in Phase 2.

1. **Load input**: Read `_contradictions.json` → grasp the `id`·`source`·`claim`·`type` fields of all claims

2. **First classification — 3-way decision**
   Read through all claims and classify each into one of the three:
   - **(A) Clear preliminary-theme membership**: the contradiction axis is clear from the claim text alone. Place in a preliminary theme's `claim_ids`
   - **(B) fragmentary**: weakly contentious or one-off. A time difference within a single event · a fact check · a single-actor issue, etc. Place in `other-fragmentary.claim_ids`
   - **(C) Judgment-ambiguous**: seems contentious, but which contradiction axis it contributes to is ambiguous from the claim text alone. Place in `unassigned` (a Phase 2 source-Read target)

3. **Name preliminary themes**: name slug · name for each detected contradiction axis (Core Principle 7). Fine-grained is allowed (20–30 possible).

4. **Stage 2.5 — small cleanup**: absorb single-claim preliminary themes into `other-fragmentary` or merge into a similar axis.

5. **Validate**: Self-Validation Checklist (including Phase 1 items)

6. **Output**: overwrite `_contradictions_themes.json` (`phase: 1`)

The Phase 1 output is the human reviewer's mid-review target. Claude keeps the Phase 1 output until instructed to run Phase 2.

#### Phase 2 — Converge with Source Detail

**Purpose**: from Phase 1's selected focused claims + necessary source-detail info, produce coarse contradiction axes within 15 + final `other-fragmentary`.

1. **Carry over the Phase 1 output**
   - Read `_contradictions_themes.json` (phase=1 output)
   - `other-fragmentary.claim_ids` → **keep as-is** in Phase 2 (no re-review)
   - `unassigned` → the source-Read target list
   - preliminary themes → candidates to be reconstructed into coarse axes

2. **Confirm focus targets**
   - Focused-analysis claims = `source_count` − `|other-fragmentary.claim_ids|`
   - Tally their source distribution

3. **Priority Source Read** — by classification uncertainty (in priority order)
   - If any one of the criteria below applies, perform a `wiki/sources/<slug>.md` Read:
     1. **Sources of Phase 1 `unassigned` claims** (top priority — secure original-text context for claims Phase 1 held back as judgment-ambiguous)
     2. **Sources related to a preliminary theme with an ambiguous boundary judgment** (to support merge · split · reassignment decisions)
     3. **Sources of type=soft claims among Phase 1 `other-fragmentary`** (re-review the absorption decision — check the possibility of axis inclusion)
   - **Do not use claim-density as a criterion**: multiple claims of the same source originally contribute to the same contradiction axis, so redistribution has no value (empirically confirmed). Do not perform Reads on this criterion
   - **No full Reads**: if it doesn't fit the uncertainty criteria above, judge from the claim text alone
   - For the source-file structure and the priority of sections to read, see the "Source File Structure" section at the top

4. **Derive coarse contradiction axes (Stage 1 Converge)**
   - Based on focused claims + source context, derive **within 15** coarse-axis candidates
   - Phase 1 preliminary themes are material for reconstruction, not keep-as-is targets. Free to merge · split · rename

5. **Classification (Stage 2 Converge)**
   - Assign focused claims to coarse axes. Cross-assign only with explicit evidence
   - Claims that were in `unassigned` are, per source-Read results, (i) assigned to a coarse axis or (ii) moved to `other-fragmentary`. The final Phase 2 `unassigned` should be an empty array

6. **Stage 2.7 — Convergence check**
   - (a) `len(themes) > 15` (exceeds the recommended upper bound including other) → two-way handling:
     - **Adjacent-axis merge first**: criteria for "adjacent axis" (adjacent if 2 or more of the following hold) — same domain/industry · same actor · regional category · sharing one side of the contradiction axis
     - **Dual-approval gate when a new theme branch is justified**: no adjacent axis + the separate-axis essence is clear → new-theme-slug candidate. Editor-in-Chief 1st classification agreement + wiki-operator 2nd final approval procedure. After 1st passes and 2nd rejects → 1st re-review. Twice rejected → absorb into other-fragmentary
   - (b) Inspect themes below the lower bound of 5 → keep if Core Principle 5 (a)·(b)·(c) one holds, else absorb into `other-fragmentary`
   - (c) Themes exceeding the upper bound of 50 → consider splitting into sub-axes (but keep the overall 15 recommendation). **The single-essential-contradiction-axis exemption is always active** — when the sub-axis candidates are all different facets of the same contradiction axis ("vendor claim vs empirical proof" · "layoffs vs rehiring reversal," etc. — surface facets of a single axis) so that splitting dilutes the essence, keeping it over 50 is allowed with explicit argumentation. Symmetric to Core Principle 5 "Core-Issue Exception" — an essence-preservation principle on the granularity dimension. A theme MD body is a narrative-driven selection (~7 bullets), so even attempting 50+ claims has little effect on body length.

7. **Validate**: Self-Validation Checklist (including Phase 2 items)

8. **Output**: overwrite `_contradictions_themes.json` (`phase: 2`). Key order: `derived_at` → `derived_by` → `phase` → `source_count` → `themes` → `unassigned`

---

### Formatting Rules

- **Raw JSON only** — no code fences · explanations · comments (this guide's `//` comments are for documentation and must not be put in the actual file)
- **Encoding**: UTF-8, `ensure_ascii=False` so non-ASCII names survive
- **Indentation**: 2 spaces
- **Line endings**: LF (`\n`)
- **Top-level**: exactly one object (starts with `{`, ends with `}`)
- **No trailing comma**
- **No extra fields** — do not add keys not defined in the schema. Side info such as core-issue exception rationale · source-Read logs is not written into JSON but kept only as **internal-reasoning notes during the work** (mental work records)
- **String quoting**: double quotes only
- **Slug**: `[a-z0-9-]+` only. No spaces · uppercase · Korean · underscores

---

### Self-Validation Checklist

Everything mechanical below is decided by `python tools/lint.py contradiction theme` — run it and take its verdict as the answer (schema · slug pattern · reserved slug · id validity · duplicate ids · count match · `unassigned == []` · theme count · per-theme size bounds · freshness). What remains is judgment the check cannot reach:

- [ ] **Slug · Name quality** — the slug is a 2–5-word structure naming the contradiction axis; the name is English by default (Korean under `WIKI_LANG=ko`) and makes the tension apparent (`#### 7. Slug·Name Naming Criteria`)
- [ ] **`phase` matches this run** — the field carries the Phase number actually performed (the check reads only that it is 1 or 2)
- [ ] **Grouping reasonableness** — sample one claim per theme and state why it belongs there (Core Principle 2)
- [ ] **Cross-assignment justification** — a claim carried by several themes has explicit evidence for each (Core Principle 3)
- [ ] **Phase 1 lower bound** — no preliminary theme holds a single claim
- [ ] **Phase 1 residue is deliberate** — whatever stays in `unassigned` is genuinely ambiguous and you can say why (the rationale is not written into JSON)
- [ ] **Phase 2 starts from Phase 1** — its `other-fragmentary` · `unassigned` are the starting point, and no claim leaves `other-fragmentary` on the way (Pitfall P4)
- [ ] **Exception rationale stated** — every theme leaning on a Core Principle 5 (a)·(b)·(c) exception, or on the single-axis exemption above the upper bound, says which one and why
- [ ] **Source-Read record** — you can say which source was read for which claim judgment (kept as working notes, not written into JSON)

---

### Common Pitfalls

| Symbol | Symptom | Response |
|---|---|---|
| P1 | Surface keyword matching (theme it as AI if the claim has "AI") | Judge by the issue's logical structure (Core Principle 2) |
| P2 | Overusing cross-assignment | Single theme unless there is explicit evidence |
| P3 | **Forcing a judgment-ambiguous claim into a theme in Phase 1** | If ambiguous, to `unassigned`. Resolve via source Reads in Phase 2 |
| P4 | **Ignoring the Phase 1 output and reconstructing from scratch in Phase 2** | Use Phase 1's `other-fragmentary`·`unassigned` info as the starting point. Sequential-pipeline principle |
| P5 | **Full source Reads in Phase 2** | Read only those fitting the Priority criteria (unassigned · ambiguous boundary · soft-absorption candidates in other-fragmentary). Claim density is ineffective, so do not use it |
| P6 | **Phase 2 `unassigned` is not 0** | Every unassigned must be resolved via source Reads and reassigned to a theme or other |
| P7 | Abusing the Phase 2 core-issue exception | To other unless it is **clearly argued** which of Core Principle 5 (a)·(b)·(c) holds |
| P8 | Forced merging (different-essence axes into the same theme) | If the contradiction axis differs, other is better |
| P9 | `other-fragmentary` absent (Phase 2) | Keep it present with empty claim_ids even if there is no residual |
| P10 | Korean escaped via `ensure_ascii=True` | The Write tool is natively UTF-8. `\uXXXX` output is a wrong dump |
| P11 | Excessive nesting depth | Schema fixed at 2 levels. No extra meta fields |
| P12 | Skipping some claims | Full-coverage violation. If unsure, to `unassigned` in Phase 1, `other-fragmentary` in Phase 2 |

---

### Sources (methodology references)

Originals of the JSON-generation prompt-engineering principles:

- [Claude API — Structured Outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) — schema-based output constraints
- [Claude Prompting Best Practices](https://claude.com/blog/best-practices-for-prompt-engineering) — INSTRUCTIONS/CONTEXT/TASK/OUTPUT 4-section structure
- [Text Clustering as Classification with LLMs, ACL 2024](https://arxiv.org/abs/2410.00927) — the 2-stage pattern of label generation → classification
- [Mastering JSON Prompting for LLMs](https://machinelearningmastery.com/mastering-json-prompting-for-llms/) — the 4-layer approach of schema · examples · rules · validation
- [Avoiding Hallucinations — Large JSON Data with LLMs](https://medium.com/@interview.jj.espinoza/avoiding-hallucinations-best-practices-for-handling-large-json-data-with-llms-406d9619e1ce) — nesting avoidance · field filtering

---
