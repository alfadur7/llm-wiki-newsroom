Health-check the LLM Wiki for issues.

Usage: `/wiki-lint [<group>] [<subcmd|target>] [--fix]`

`$ARGUMENTS` is optional. With no arguments, the full suite (= the `all` group) runs; specifying a group or subcommand runs only that scope.

```
Usage: /wiki-lint [<group>] [<subcmd|target>] [--fix]

Examples:
  /wiki-lint                                        # full suite (all groups below + suggestions·promotion·demotion·staleness informational)
  /wiki-lint --fix                                  # full suite + each group's supported --fix in one pass
  /wiki-lint graph                                  # structure · orphans · clusters · raw-files · internal-refs in one pass
  /wiki-lint graph orphans --fix                    # single subcommand
  /wiki-lint graph gaps [--gap-type <slug>] [--top 5]   # gap diagnostic (informational in `all`)
  /wiki-lint hub schema                             # L2-2 hub frontmatter check
  /wiki-lint meta schema                            # meta-doc integrity · drift · language convention
  /wiki-lint overview open-source-ai-definition     # single cluster overview
  /wiki-lint overview aggregate                     # L2-4 overview.md
  /wiki-lint overview <target> --fix                # diagnosis + Claude rewrite instruction
  /wiki-lint contradiction <theme>                  # single theme MD diagnosis
  /wiki-lint contradiction theme                    # _contradictions_themes.json ↔ MD consistency
  /wiki-lint contradiction theme --fix              # JSON regeneration — emits Claude instruction block
  /wiki-lint source                                 # all-source new-schema diagnosis (Phase 2)
  /wiki-lint source <slug>                          # single-source new-schema Rubric diagnosis
  /wiki-lint overview --fix --yes                   # bypass confirmation prompt (use only after prior review)
  /wiki-lint contradiction --fix --yes              # bypass confirmation prompt
```

`--yes` (`-y`) bypasses the file create/delete confirmation prompt of `overview --fix`·`contradiction --fix`. In a non-TTY environment (Claude Code Bash·CI) the prompt cannot be answered, so the command aborts; add `--yes` only when you intend deliberate execution after review. `--yes` itself has no effect in other groups (`graph`·`hub`, etc.) — those perform only content edits and auto-enrichment, with no file creation or deletion.

## Traversal Pattern

A verify-and-fix cycle. The Copy Editor is the lead; when `--fix` is set, the Columnist and Desk chain is entered.

| Mode | Cycle | Owner |
|---|---|---|
| **Check only** (no `--fix`) | VERIFY | Copy Editor (`tools/lint.py`) — exit code + lint-report.md |
| **`overview/contradiction <target> --fix`** (L2-3·L2-4 rewrite) | VERIFY → ADAPT → APPLY → VERIFY | Copy Editor (VERIFY₁) → Columnist (ADAPT) → Copy Editor → Desk (VERIFY₂) → Editor-in-Chief gate |
| **Other group `--fix`** (`graph`·`hub`, etc. — auto-enrich/correct) | (deterministic) | Copy Editor (formattable-area auto-fix only; no meaning-affecting changes) |

In this chain, `--yes` is **Claude's explicit opt-in to executing the chain** — deferring to `lint-report.md` violates the opt-in intent (`.claude/hooks/lint-chain-guard.sh` enforces this at the system level).

## Sub-procedure (Owned by This Folder)

Three sub-procedures are the sole responsibility of this command, one of them in a sibling file:
- [`wiki-lint-theme-mapping.md`](wiki-lint-theme-mapping.md) — the raw DB → JSON re-derivation procedure for `contradiction theme --fix`
- [`## Sub-procedure: Contradiction Theme Mapping Procedure`](#sub-procedure-contradiction-theme-mapping-procedure) — a theme's life after derivation: lifecycle invariants, burn criteria, and the new-slug gate
- [`## Sub-procedure: Conflict Axis Sync Rule`](#sub-procedure-conflict-axis-sync-rule) — the 4-tier bottom-up synchronization rule for `contradiction --fix`

The [A]–[G] code definitions and the diagnostic output format for the Cluster Health Diagnostic are not a separate sub-procedure; the per-code definitions · action guides are SoT in `tools/_lint/graph_clusters.py` (module docstring + report output), while the `graph clusters` row of the [`## Group Structure`](#group-structure) table records only the codes' pass/fail posture.

### Chain Execution Obligation

#### Chain Markers (Single SoT)

If any one of the following markers appears in lint stdout, a downstream chain obligation arises:

- `CHAIN-REQUIRED`
- `STALE --fix chain`
- `⚡ ACTION REQUIRED`
- `Claude rewrite instruction block`

These 4 markers are the single SoT for chain detection — both the emit sites in `tools/lint.py` and the grep patterns in [`.claude/hooks/lint-chain-guard.sh`](../hooks/lint-chain-guard.sh) reference this list.

#### Claude Behavior Protocol

`--yes` or `-y` is **Claude's explicit opt-in to executing the chain**. On marker detection, perform the downstream chain immediately — deferring it to "Remaining work" in `lint-report.md` violates the opt-in intent. Task size is not grounds for non-execution (even large-scale work like classifying 250 claims across Phase 1·2 is intended at the moment `--yes` is given).

**No requesting user approval (limited to the `--yes` context)**: Only in calls that include the `--yes` token, before entering the chain, do not produce wait-for-user-input utterances such as "I request the wiki operator's approval," "please instruct me to proceed to the next step," or "awaiting the chain-entry gate" — because the `--yes` token is itself the chain-entry approval. A `--fix`-only call without `--yes` is the exact opposite — it corresponds to the "only correct case for non-execution" above, where waiting for user confirmation is the SoT-correct answer. The human-reviewer gate is not a chain-**entry** gate but fires at chain-**mid** triggers — see [`CLAUDE.md` "Human Reviewer Gate"](../../CLAUDE.md#human-reviewer-gate) as the single SoT for which those are.

**The only correct case for non-execution**: the user ran lint without `--yes` = explicitly declining chain opt-in. Only then do you write the rewrite block into the report and wait for user confirmation.

#### System Enforcement (hook)

[`.claude/hooks/lint-chain-guard.sh`](../hooks/lint-chain-guard.sh) (PostToolUse Bash) detects chain markers in lint stdout and sends blocking feedback via exit 2. This convention is hook-enforced, not a natural-language request — on marker detection, report authoring and `Remaining work` classification are automatically deferred until after the chain completes and re-diagnosis PASSes.

The backend diagnostic tool is `tools/lint.py`, and you can call the same group/subcommand directly in the form `python tools/lint.py <group> [<sub|target>]`.

## Group Structure

| Group | Subcommand | Check target | `--fix` behavior |
|------|-----------|---------|-------------|
| `graph` | `structure` | Page structure (broken link · orphan hub · missing entity · Korean entity with English filename). **`log.md` is excluded from the source scan** — being an append-only operational record, it permanently retains past cluster slugs and dissolved concepts, structurally producing perma-broken-link false positives. `log.md` is valid as a wikilink target from other pages, but its own body is out of scan scope | **Auto-reconnect hubs** (for orphan hubs + hubs with empty `sources:`, match the stem/Korean title alias against `wiki/sources/*.md` raw text, and on a match add `[[<hub>]]` or `[[<hub>\|<Korean alias>]]` to the matched source's `## Connections`; Latin stems <3 chars or 0 matches are deferred as a separate stub-body-expansion task) |
| `graph` | `orphans` | Source↔hub reference integrity (sources frontmatter ↔ source `## Connections`) + classifies declared-but-fileless slugs by token-set Jaccard (HIGH ≥0.5 → auto-correction candidate · LOW-HIGH 0.25-0.5 → SUGGESTION · < LOW → NO MATCH) | (1) auto-backfill source `## Connections` → hub `sources:` (2) auto-rename HIGH candidates (if the target already exists in the same hub, just remove the typo — a correct/incorrect duplicate pattern). SUGGESTION·NO MATCH go to human review |
| `graph` | `clusters` | Leiden community health codes [A]–[G]. [A]·[B]·[D]·[E] are pass/fail targets, **[C] mixed cluster is informational** (accepted as a natural result of cross-cutting themes) + emits anchor_members realignment suggestions | **Auto-regenerate SoT JSON** — deterministic Leiden rebuild of `_graph.json` + `_clusters.json` against the current wiki state. Downstream MD edits (catalogs·overview AUTO blocks) are intentionally excluded — run `python tools/build.py clusters` separately if needed |
| `graph` | `raw-files` | Verifies that a source page's `source_file:` value points to an actual raw file (detects references broken by smart-quote auto-conversion · missing quotes · backslash escapes, etc.). A broken reference nullifies `_source_map.json::by_path` matching, bypassing ingest duplicate detection | **Auto-correct** — if quote-normalize or quote-strip matching finds a single candidate in the raw tree, replace the `source_file:` value with the exact raw path. Multiple candidates (AMBIGUOUS) · no candidate (NO MATCH) go to human review |
| `graph` | `internal-refs` | Detects **markdown links** from published content (root meta + entities·concepts·overviews·contradictions·syntheses·timelines·trails) into the build/governance tree (`.claude/`·`tools/`·`CLAUDE.md`·`raw/`·`log.md`). A RAG reader cannot open these, and they pollute the corpus with self-meta. **Link-based, so no false positives** — plain-text topic mentions like Claude Code's `CLAUDE.md`·`.claude/` are not links and are not detected. Symmetric check to `hub voice`·the guideline-writing voice pass (sources are out of scope since their bodies aren't exported) | Unsupported — removal/rephrasing is the author's call (same as `hub voice`) |
| `graph` | `gaps` | 10-type deterministic gap diagnostic. Output is split by Track A (sparse-cluster·single-source·stale-hub — auto-enrich targets) · Track B (bridge — surfaced for wiki-operator decision) · Track C (orphan-claims·cap-theme·stale-theme — separate cycle) · Track D (synthesis·trail·timeline — Columnist-derived authoring). **Informational in `lint all`** — the total and the exit code count the backlog only, holding the standing bridge top-N ranking apart (working one candidate just promotes the next). Definitions·thresholds are SoT in [`.claude/operations/gap-detection-rollout.md`](../operations/gap-detection-rollout.md) | Unsupported — enrichment triggers are `/wiki-news --gap`, theme rewrite is `/wiki-lint contradiction theme --fix` |
| `graph` | `drift` | Compares warm↔cold Leiden partition quality (modularity) — detects cluster-stability drift. **OPT-IN — not auto-run by `lint all`** (cost of cold Leiden recomputation) | Unsupported |
| `hub` | `speakers` | **WIKI_LANG=ko only** (the byline matcher keys on Hangul names + Korean role nouns; a no-op on the English-native default — English attribution is covered by `cit.A2` + `count_mentions.py`). Among quoted speakers (the `> "..." — Name (role)` pattern), those that meet **both** conditions of **multiple quotes (≥3 total) AND appearing in multiple sources (≥3 distinct files)** while `entities/<name>.md` is missing. Thresholds adjustable via `--min-quotes`·`--min-sources` flags | Unsupported (current-role verification required; Claude must not auto-stub) |
| `hub` | `suggestions` | Commonly-referenced but not-yet-created links + frequently-mentioned terms with no page (informational — no pass/fail impact) | Unsupported |
| `hub` | `schema` | L2-2 hub frontmatter + body structure — entities require `title·type·kind·tags·sources·last_updated`, concepts `title·type·tags·sources·last_updated`, timelines `title·type·tags·last_updated` (no `sources`) + `type` value matches the directory + the `## Overview`/`## Connections` required-section + ≥200-char body check | **Auto-fill type + last_updated** (deterministic, based on directory · git log). title/tags/sources need semantic inference → report only |
| `hub` | `voice` | L2-2 hub body self-meta voice antipatterns (violations of encyclopedic neutrality). The automated regex detection runs **only under `WIKI_LANG=ko`** (the tokens `본 hub는`·`별도 정리한다`, etc.); on the English-native default the scan returns early, so the English self-meta ban (`this hub …`·`covered separately`) is enforced editorially by author/Desk (SoT: `.claude/layers/hub.md`). When it fires (ko-mode), FAIL → exit 1. Fenced code blocks are excluded from the check | Unsupported (rephrasing is the author's call; symmetric to `internal-refs`) |
| `hub` | `body` | L2-2 hub body density advisory (body length · number of `## Connections` links — detects nav-anchor bloat; thresholds injected via `_manifest.json`). **Gating — any advisory exits 1** | Unsupported (delegating to a sub-hub is a semantic judgment) |
| `hub` | `timeline` | L2-2 hub `## Timeline` narrative (item count ≥30 · strict date ordering · pointer coverage <50% · quantitative-figure restatement). **Gating — any issue exits 1** | Unsupported |
| `hub` | `promotion` | L2-2 hub promotion-candidate triage (stub → full hub, informational) | Unsupported (promotion is a Desk gate) |
| `hub` | `demotion` | L2-2 hub demotion/deletion-candidate triage (one-off·isolated stub, informational) | Unsupported (demotion is a Desk gate + graph integrity) |
| `meta` | `schema` | CLAUDE.md integrity (anchor·file-ref·slash-cmd·roster completeness) + craft-skill referential integrity (`_manifest.json`·`criteria.json`·`checks.py`) + stale cluster-slug literal guard + English-header section convention + flat-lint-path recurrence guard + agent tool-permission parity (role X-list ↔ frontmatter `disallowedTools`, both directions) + defect-ledger vocabulary (every `tools/_defect-log.jsonl` record passes `log_defect.validate()` — a direct append bypasses the validating entrance) | **Unsupported** — substituting a non-English header → English is not a 1:1 deterministic mapping but requires a meaning-preserving wording decision (e.g., `## Mode Routing (query type → mode dispatch)` → deciding between `Mode Routing by Query Type` vs `Routing by Type`). Same semantic-inference area as graph structure broken links — the `## --fix Mode (2) Claude` area branch |
| `overview` | — | `wiki/overviews/<cluster>.md` + `wiki/overview.md` — completeness · schema · Rubric metrics · Freshness + JSON↔MD slug 1:1 mapping (SoT is `graph/_clusters.json`) + **cluster name drift** (frontmatter `title`·body H1 vs `_clusters.json::clusters[].name`) + **frontmatter `cluster:` slug ↔ filename stem consistency** | **MD↔JSON sync** — JSON-only cluster slug → auto-generate skeleton, MD-only slug (orphan overview) → auto-delete. Both actions **run only after passing the confirmation prompt** (bypassable with `--yes`). Non-destructive repairs (alias-correcting un-aliased cluster links · inserting AUTO markers · **auto-syncing cluster name drift** — after a rename, batch-update frontmatter `title`·body H1 following the `cluster_labels.json` SoT · **correcting frontmatter `cluster:` slug** — in-place replacement based on filename stem) proceed without a prompt. **When a target is specified (=`<slug>` or `aggregate`)**: the above + an added Claude rewrite instruction block (no rewrite block is emitted on a target-less `all` call — explicit invocation via `/wiki-lint overview <target> --fix` is required) |
| `contradiction` | — (target=theme slug) | `wiki/contradictions/<theme>.md` — frontmatter · 4 H2 sections (no AUTO block — by design) + JSON↔MD slug 1:1 mapping (SoT is `_contradictions_themes.json`) + frontmatter `sources:` ↔ JSON-implied sources drift (informational) + **detection of residual legacy AUTO blocks** (artifacts of a past build pipeline) | **MD↔JSON sync** — JSON-only slug → auto-generate skeleton (using JSON `name`), MD-only slug (orphan MD) → auto-delete. Both actions **run only after passing the confirmation prompt** (bypassable with `--yes`). Non-destructive repairs (inserting missing-H2 `_TODO` placeholders + **removing legacy AUTO blocks** — deleting `<!-- AUTO:CLAIMS/SOURCES BEGIN/END -->` and the inner/preceding `## Sources` header) proceed without a prompt. **SoT freshness chain** — when `_contradictions_themes.json` is stale (any one of: ① the `source_count` snapshot differs from `_contradictions.json`'s current record count — record-count drift, the most direct signal / ② `_contradictions.json` has uncommitted edits AND `derived_at < today` / ③ `_contradictions.json`'s last commit date > `derived_at`), this pass's MD mutation is skipped (preventing propagation of stale theme boundaries) and a theme rewrite block (Phase 1·2 instructions) is auto-emitted so Claude performs the chain: regenerate JSON → `python tools/build.py contradictions` → re-run `/wiki-lint contradiction --fix --yes` |
| `contradiction` | `theme` | `wiki/contradictions/_contradictions_themes.json` integrity itself — JSON schema · claim-id validity · full coverage · Phase 2 conditions · Freshness against `_contradictions.json` | **Does not edit the JSON directly.** Emits only a Claude regeneration instruction block (the Guide's Phase 1→2 procedure) — the same block is emitted on the `contradiction --fix` stale gate to carry out the chain |
| `source` | — (target=source slug) | `wiki/sources/<slug>.md` Phase 2 new schema (claim atomization · citation type · evidence grade) — the automatic metrics of `.claude/layers/source.md` § Evaluation Rubric | Unsupported — schema conversion needs semantic analysis, so it is out of deterministic `--fix` scope (authoring is in `.claude/layers/source.md` § Authoring) |
| `synthesis` | — (target=synthesis slug) | `wiki/syntheses/<slug>.md` — S1 required sections · source coverage · source existence · slug-alias (L2-3 Q&A synthesis schema). Included in `all` | **Generate skeleton** (if missing) + Claude rewrite instruction block — explicit invocation via `/wiki-lint synthesis <slug> --fix` |
| `trail` | — (target=trail slug) | `wiki/trails/<slug>.md` — S1 required sections · `## Path` links · path length 4-12 (a deliberate buffer below the authoring SoT's 5–12 in `.claude/layers/trail.md`) · slug-alias (L2-3 associative-trail schema). Included in `all` | **Generate skeleton** (if missing) + Claude rewrite instruction block — explicit invocation via `/wiki-lint trail <slug> --fix` |
| `timeline` | — (target=timeline slug) | `wiki/timelines/<slug>.md` — S1 required sections (`## Flow Summary` + `### YYYY`) · source-indexed path classification (L2-2 standalone-timeline schema — separate from the hub-embedded `hub timeline` `## Timeline` advisory). Included in `all` (advisory mode) | **Generate skeleton** (if missing) + Claude rewrite instruction block — explicit invocation via `/wiki-lint timeline <slug> --fix` |
| `staleness` | — (target) | Layer-cascade staleness — diagnoses pages whose upstream is newer than the page's authored date. For derived-narrative types (overview·contradiction·synthesis·trail·timeline + root meta), the basis is the **EDITOR-body git edit date** rather than frontmatter `last_updated`, preventing a partial edit from bumping only the date and masking body staleness (when inflated, marked as `body=…`). **Informational** (surfaced outside pass/fail in `all`) | Unsupported — re-grounding cannot be a deterministic `--fix` (needs cross-source synthesis · Desk gate). Surfaced pages are handled via Columnist→Desk→ADAPT (procedure: [`operations/staleness-reground-runbook.md`](../operations/staleness-reground-runbook.md)) |
| `all` | — | Sequentially runs all groups above + gaps·suggestions·promotion·demotion·staleness informational | Runs every group's supported `--fix` (overview Claude EDITOR rewrite is **excluded** — invoke explicitly via `/wiki-lint overview <target> --fix`). `contradiction theme` JSON regeneration is included as a chain on stale detection — `--yes` acts as the explicit opt-in |

For target-based groups (`overview`·`contradiction`), the second positional argument is not a subcommand but a target file slug. For overview it is a cluster slug (one of `_clusters.json`'s `clusters[].slug`) or `aggregate`; for contradiction it is a theme slug (regardless of MD existence — even a declaration in JSON makes it a valid target). **The `contradiction` group is a hybrid** — the single word `theme` dispatches first as a reserved subcommand (defined above), while any other second argument is interpreted as a theme-slug target. Using `theme` as a theme slug is forbidden (see [`wiki-lint-theme-mapping.md`](wiki-lint-theme-mapping.md) § Slug·Name Naming Criteria).

**Responsibility-separation principle**: the JSON↔MD mapping check lives on the `contradiction` (MD) side — the cause of a mapping mismatch is that the JSON was re-derived but the MD has not yet reflected it, and the fix is an MD-side action (skeleton generation · orphan-MD deletion). The internal integrity of the JSON itself is the sole responsibility of `contradiction theme`.

## Check Items (full suite layout)

The [`## Group Structure`](#group-structure) table is the single SoT for what each group checks. Only the detail that does not fit a table cell lives here:

1-A. **Orphan-hub scope** (`graph structure`) — among entities/concepts only; trails and syntheses are independent documents and are excluded.
2. **Orphan sources, two kinds** (`graph orphans`) — *recoverable*, where the source's `## Connections` holds a valid hub `[[wikilink]]`, is auto-recovered by `/wiki-lint graph orphans --fix`; an *unconnected source*, whose `## Connections` is itself empty, needs manual review.
2-B. **Hub `## Connections` source link ↔ own frontmatter consistency** (`graph orphans`) — checks whether a source slug linked in a hub's own `## Connections` is registered in that hub's own frontmatter `sources:`. The `## Connections` section allows source links (`.claude/layers/hub.md` "list of related hub·source links"), but a linked source must also be registered in frontmatter sources to keep backlink·graph-edge consistency (hub.md "Source consistency"). Unregistered ones are auto-registered with `--fix` (backfill the hub's own `## Connections` → frontmatter `sources:`).
4-A. **Missing-entity threshold** (`graph structure`) — a name referenced by 3+ pages and lacking its own page.
5-A. **Uncovered cited speakers** (`hub speakers`) — `> "..." — Name (role)` quoted speakers who meet **both** conditions of **≥3 total quotes + ≥3 distinct source files** while lacking an `entities/<name>.md` page. These two counts are all this check measures; whether a stub is warranted is decided against the [`policies/naming.md`](../policies/naming.md) entity-stub threshold, which counts differently and adds conditions no deterministic check reads. single-source · 1–2-quote one-off citations are not actionable stub candidates. Single-file detection is handled by `/wiki-ingest` workflow step 9. **When creating a stub, current-role verification via `WebSearch` is mandatory** — between the article's writing date and now, the person may have changed jobs, retired, or been promoted. For people no longer in their role due to retirement · resignation, hold off on creation or request human-reviewer confirmation.

New-page candidates (`hub suggestions` — informational, no pass/fail impact):
- **Commonly-referenced but not-yet-created links** — pages commonly referenced from several pages but not yet created (0 of these is a wiki-health signal)
- **Frequently mentioned but page-less terms** — noun phrases that appear often in bodies but have no wiki page (precision ~40-50%, **auto-stub creation forbidden**, human-reviewer review required)
- Noise guards are maintained cumulatively via the internal BLOCKLIST + KOREAN_ALIAS of `tools/_lint/text_candidates.py`

Semantic checks (read and reason over page content):

- **Contradictions** — claims that conflict between pages
- **Stale summaries** — pages not updated after newer sources changed the picture
- **Data gaps** — important questions the wiki cannot answer; name specific sources to find

Output a structured markdown lint report — per-group detail sections first, then a one-line summary of every group in an **`## Action Items`** table. At the end, ask whether to save it to `lint-report.md`.

## `--fix` Mode

`--fix` is classified by group into three kinds of action. **The detail of each action is SoT in the `--fix behavior` column of the Group Structure table** — this section covers only the classification hierarchy and cross-group notes outside the table (on re-entry, consult the table first).

**(1) Mechanical auto-fix (script, deterministic)** — supported groups: `graph structure`·`graph orphans`·`graph clusters`·`graph raw-files`·`hub schema`·`overview`·`contradiction`. For the detail of repair actions · confirmation prompts · post-delete advisories, see the Group Structure table + per-group sections (`overview Group`·`contradiction Group`).

**(2) Agent-judgment fix (Claude)** — needs semantic inference, so the script does not perform it:
- **Broken links** — convert non-existent [[wikilink]]s to plain text or correct them per the filename convention (correction first when the filename mapping is clear)
- **Missing entities/concepts** — create stubs for names referenced by 3+ pages (follow Naming Conventions; people require **mandatory current-role verification via `WebSearch`**)
- **Orphan hubs** — add [[wikilink]]s to the relevant sources' `## Connections`
- **Korean entity with English filename** — rename to a Korean filename + batch-fix all wiki-wide links
- **Untagged pages** — enrich based on cluster membership · body context
- **Korean section headers** (`meta schema` Korean header violations) — decide and substitute English wording for Korean H2–H4 headers that violate the English convention. No 1:1 dictionary mapping is possible — selecting the wording requires considering both the header's meaning and this SoT's English-vocabulary convention

**(3) Suggest/report only (Claude auto-edit forbidden)** — needs domain judgment:
- **Unnamed group labels** — suggest `graph/cluster_labels.json` entries only, human approval required
- **[C] mixed cluster anchor_members realignment** — output candidate members only
- **Cited-speaker stubs** — auto-creation forbidden, since `WebSearch` current-role verification is needed

### Cross-group Notes

- **`all --fix` scope limit**: overview Claude EDITOR rewrite is **excluded** — explicit invocation via `/wiki-lint overview <target> --fix` is required (guarantees per-target-file reasoning). `contradiction theme` JSON regeneration is included as a chain on stale detection, and `--yes` is the explicit opt-in to the probabilistic-inference chain.
- **`contradiction theme --fix` (JSON regeneration)**: the script does not edit JSON directly. It outputs only the Claude rewrite instruction block of the [`wiki-lint-theme-mapping.md`](wiki-lint-theme-mapping.md) Phase 1·2 procedure. The same block is emitted on the `contradiction --fix` stale gate → Claude catches the chain even mid-`all --fix --yes`.
- **`python tools/build.py` after fixes complete** — the full 5 phases (graph → clusters → contradictions → index → dependencies). When stub creation · [[wikilink]] addition · AUTO-marker insertion is involved, this guarantees downstream updates.

Reflect each fix in the report. Append to `log.md`: `## [today's date] lint | Wiki health check`

## Lint Report Output Format Requirements

Per-target detail requirements to follow when authoring `/wiki-lint [--fix]` results into `lint-report.md`. The purpose of this convention is to **force the overview and contradiction group report sections to maintain symmetric depth** — because the script (`tools/lint.py`) emits symmetric per-target metrics (Rubric + drift tier + rewrite recommendation) to stdout for both groups, summarizing only one side when Claude authors the report creates an asymmetry that forces the human reviewer to re-confirm via a separate run. The requirements below catch that authoring drift.

### Target Groups

These requirements apply only to the **two groups that emit symmetric per-target metrics (`overview`·`contradiction`)** — several other groups also take a target, but none pairs off against another this way. The rest (`graph`·`hub`·`meta`·`source`·`synthesis`·`trail`·`timeline`·`staleness`) have few files or their own structure, and are outside these requirements.

### Required per-target Drift Block

Both groups must include the following 3 elements **one block per file** — do not detail one group while summarizing the other as `"N drifts"`.

1. **Target identifier**: `<cluster-slug>` or `<theme-slug>` (slug only allowed instead of the full file path)
2. **Drift tier + one-line figures** (recommended to re-quote the `python tools/lint.py` stdout output verbatim):
   - overview: `🔴/🟡/🟢 member_jaccard=X source_delta=±Y% (srcs A→B) top10_new=N`
   - contradiction: `🔴/🟡/🟢 claim_jaccard=X source_delta=±Y% (srcs A→B) top5_new=N`
   - **Unit caution**: `*_jaccard` is on the claim_id or cluster-member-ID set basis, while `source_delta`·`top*_new` are on the source-file set basis. The two layers are different dimensions, so do not sum or directly compare them. Do not interpret drift figures as claim counts — the `(srcs A→B)` label makes the unit explicit.
3. **Rewrite recommendation command**: when 🔴, specify `/wiki-lint <group> <target> --fix` (🟡 is "drift re-review recommended," 🟢 is briefly "drift stable")

**Example (overview)**:
```
- 🔴 licensing-open-washing — member_jaccard=0.64 source_delta=+98% (srcs 50→99) top10_new=6 → `/wiki-lint overview licensing-open-washing --fix`
- 🟡 open-weights — member_jaccard=0.82 source_delta=-10% (srcs 40→36) top10_new=6 → drift re-review recommended
- 🟢 open-source-ai-definition — drift stable
```

**Example (contradiction)**:
```
- 🔴 other-fragmentary — claim_jaccard=0.52 source_delta=+58% (srcs 24→38) top5_new=5 → `/wiki-lint contradiction other-fragmentary --fix`
- 🟡 open-weights-vs-open-source — claim_jaccard=0.77 source_delta=+13% (srcs 23→26) top5_new=3 → drift re-review recommended
```

### Rubric Required-Criterion Summary (one per group)

Per-file Rubric metrics may be compressed into a **required-criterion roll-up** at the bottom of the group instead of repeated per target:
- overview: W4 broken links (`=0`) · X1 tension-axis crossing · X3 AUTO-EDITOR separation — mention only the list of FAIL files among the automatic metrics
- contradiction: S1 sections · S2 evidence · W4 broken links · L2 cite-consistency — same rule

Rubric detail figures are advisory, so files passing required criteria need not be listed — only FAIL·⚠️ items are worth reporting.

### L2-4 Aggregate Block (separate)

`wiki/overview.md`·`wiki/contradiction.md` report **L2-4-specific metrics** in their own block:
- `wiki/overview.md`: D1 clusters (completeness) · D2 drilldowns · D3 balance · F1 theme_refs
- `wiki/contradiction.md`: F2 stats (claims declared vs actual) · D1 axes · D2 alias · D3 balance · X1 theme_coverage

Recommended to separate from the L2-3 cluster/theme drift block under a distinct `### L2-4 aggregate` subheading.

### Remaining Work List — Pipeline Order

Based on the drift blocks, list in the following order (do not list filenames only · provide the drift tier · supporting figures together so priority can be judged):
1. **JSON regen** — on theme stale detection, `/wiki-lint contradiction theme --fix` (chain auto or manual)
2. **MD↔JSON sync** — `/wiki-lint <group> --fix --yes` (skeleton creation · orphan deletion)
3. **target EDITOR rewrite** — `/wiki-lint <group> <target> --fix` (🔴 first, 🟡 later)
4. **aggregate rewrite** — `/wiki-lint <group> aggregate --fix`

### Asymmetry Enforcement

The lint-report guard in `.claude/hooks/dispatch.py` (PreToolUse Write|Edit on `lint-report.md`) blocks with exit 2 if only one group has per-target drift blocks (member_jaccard or claim_jaccard). That is, the symmetry of the two groups is system-enforced, and **the hook verifies directly at authoring time** instead of a self-checklist — to pass, you must add a drift block for every cluster slug (`graph/_clusters.json`) or theme slug (`_contradictions_themes.json::themes`) of the missing group.

## overview Group (`/wiki-lint overview [<target>] [--fix]`)

A routine dedicated to landscape-axis overview files. Integrates diagnosis and Claude rewrite instruction into one command.

**Target files**: `wiki/overviews/<cluster>.md` (L2-3, number of clusters = length of `graph/_clusters.json::clusters`) + `wiki/overview.md` (L2-4).

**target argument interpretation**:

| Argument | Scope | `--fix` behavior |
|------|--------|-------------|
| (none) | Diagnose all L2-3 clusters + all of L2-4 | ✅ MD↔JSON sync (skeleton create / orphan delete after the confirmation prompt, `--yes` bypass) + non-destructive repairs; no Claude rewrite block (a target is required for that) |
| `<cluster-slug>` | That single L2-3 file | ✅ Output Part 1 rewrite instruction block |
| `aggregate` | `wiki/overview.md` only | ✅ Output Part 2 rewrite instruction block |

A cluster slug is one of `graph/_clusters.json`'s `clusters[].slug` list. No enumeration literals are kept (cluster composition shifts with ingest accumulation) — always reference the SoT JSON directly.

### Diagnosis Mode (no `--fix`)

Calls `python tools/lint.py overview [<target>]` to output:
- **Rubric metrics (automatic)**: each L2-3 file's `[Rubric] W1·W2·W3·X2` + L2-4's `[Rubric L2-4] W1·W2·W3·D1·D2·D3·F1`
- **Freshness warning**: a `[Freshness]` line when frontmatter `last_updated` lags behind a git commit or uncommitted edit
- **Schema issues**: missing H2 sections · frontmatter fields · alias not applied, etc.

Exit code 0 means required criteria within scope pass. 1 means schema issues remain.

### Rewrite Mode (`--fix` + target required)

The script **does not edit the EDITOR area directly**. Instead, at the end of the diagnostic output it emits a "Claude rewrite instruction block," handing the execution order to Claude. Claude follows this procedure:

**Common procedure**:

1. **Read `.claude/layers/overview.md`** — the Part matching the target scope (L2-3=Part 1, L2-4=Part 2).
2. **Read `.claude/layers/overview.md`** — the same Part's `## Evaluation Rubric`.
3. **Read the target file(s)**: for a single cluster, `wiki/overviews/<slug>.md`; for aggregate, `wiki/overview.md` + all cluster overviews (`graph/_clusters.json::clusters[]` SoT) in full.
4. **Rewrite the EDITOR area following the Authoring Guide "execution order."** Never modify AUTO blocks (`<!-- AUTO:... BEGIN/END -->` and their contents).
5. **Re-diagnose**: re-run `python tools/lint.py overview <target>` → confirm Rubric metrics · Freshness.
6. **Rubric completion condition**: follow the relevant Part's "completion condition" block in `.claude/layers/overview.md` as SoT (the required criteria + overall PASS ratio are the single SoT in the guide — do not enumerate figures in this command file).
7. **On completion, update frontmatter `last_updated` to today's date** (L2-4 aggregate has no frontmatter, so skip this step — instead record the re-aggregation event in `log.md`).

**No iteration cap**. Repeat until required criteria PASS. If the same criterion FAILs twice in a row, the Guide's "safeguard" clause fires.

### Relation to Adjacent Routines

- **`/wiki-lint --fix` (= `all --fix`)**: performs mechanical repair only. Does not do EDITOR rewrite.
- **`/wiki-lint overview <target> --fix`**: the above mechanical repair limited to the target file + a Claude EDITOR rewrite instruction.
- **`python tools/build.py clusters`** (independent pipeline): regenerates AUTO:MEMBERS·AUTO:SOURCES·AUTO:STATS blocks. Auto-called by `/wiki-ingest`·`/wiki-lint --fix`; the overview subcommand does not trigger this build separately (since only EDITOR changes, AUTO regeneration is unnecessary).

Append to log.md: `## [today's date] lint | overview <target> rewrite` (on Claude rewrite completion) + load this rewrite cycle's Desk VERIFY₂ actionable defects into the corpus via `log_defect` (bare diagnosis · mechanical `--fix` are excluded, being standing state — SoT: [`agents/editor-in-chief.md`](../agents/editor-in-chief.md) automatic channel).

## contradiction Group (`/wiki-lint contradiction [<target>] [--fix]`)

A routine dedicated to conflict-axis issue files. Integrates diagnosis · MD↔JSON sync · (future) Claude rewrite instruction into one command. Symmetric structure to the overview group.

**Target files**: `wiki/contradictions/<theme>.md` (L2-3, number of themes = number of keys in `wiki/contradictions/_contradictions_themes.json::themes`) + `wiki/contradiction.md` (L2-4 aggregate).

**target argument interpretation**:

| Argument | Scope | `--fix` behavior |
|------|--------|-------------|
| (none) | Diagnose all theme MDs + JSON↔MD mapping + L2-4 aggregate | ✅ MD↔JSON sync + schema repair (create/delete after passing the confirmation prompt) |
| `theme` (reserved subcommand) | `_contradictions_themes.json` integrity itself | ✅ Output Claude JSON re-derivation instruction block (Phase 1·2 guide) |
| `<theme-slug>` | That single theme MD | ✅ The above sync + **output Part 1 rewrite instruction block** |
| `aggregate` | `wiki/contradiction.md` only | ✅ **Output Part 2 rewrite instruction block** |

A theme slug is one of the `themes` keys of `_contradictions_themes.json` or a file stem of `wiki/contradictions/*.md` (regardless of MD existence). The reserved words `theme` (subcommand) and `aggregate` (L2-4 root target) both dispatch to non-theme branches, so neither may be used as a theme slug.

### Diagnosis Mode (no `--fix`)

Calls `python tools/lint.py contradiction [<target>]` to output:
- **Schema issues**: missing H2 sections · frontmatter fields · missing AUTO markers, etc.
- **JSON↔MD mapping**: JSON-only slug (MD not created) · MD-only slug (orphan MD)
- **frontmatter `sources:` ↔ JSON-implied sources drift** (informational)
- **Rubric metrics**: each theme file's `[Rubric]` (Part 1 automatic metrics) + aggregate's `[Rubric L2-4]` (Part 2 automatic metrics). The automatic-metric count · number of output lines are SoT in the relevant Part of `.claude/layers/contradiction.md`
- **`[Reground status]`** (advisory, aggregate scope): claims auto-classified `type: superseded` yet still `status: open`. Never affects the exit code, never auto-closes; re-adjudication is a Desk judgment ending at the operator gate (SoT: CLAUDE.md § Reground)

F2 checks the canonical claim total at **every** occurrence in `wiki/contradiction.md`, not only the head sentence — a delta-only re-ground leaves stale copies mid-body.

Exit code 0 means schema · mapping within scope pass. 1 means issues remain.

### Rewrite Mode (`--fix` + target=theme-slug or aggregate)

In the same pattern as overview, the script **does not edit the EDITOR area directly**. At the end of the diagnostic output it emits a "Claude rewrite instruction block," handing the execution order to Claude. `tools/_lint/contradiction.py`'s `_emit_rewrite_block` (theme) · `_emit_rewrite_block_aggregate` (aggregate) auto-output the Part 1 · Part 2 guide procedures respectively.

**Common procedure** (the order the rewrite block outputs):

1. **Read `.claude/layers/contradiction.md`** — the Part matching the target scope (L2-3=Part 1, L2-4=Part 2).
2. **Read `.claude/layers/contradiction.md`** — the same Part's `## Evaluation Rubric`.
3. **Read the target file(s)**: for a theme slug, `wiki/contradictions/<theme>.md` + resolve the `_contradictions.json` records via that theme's `claim_ids` in `_contradictions_themes.json` + the key source files. For aggregate, `wiki/contradiction.md` + all theme files in full (by `_contradictions_themes.json` keys).
4. **Rewrite following the Authoring Guide "execution order."** A theme MD has 4 H2 sections; the aggregate has the `# Contradictions by Theme` root + 4 required sections. All are EDITOR area in their entirety, with no AUTO blocks.
5. **Re-diagnose**: re-run `python tools/lint.py contradiction <target>` → schema · mapping · Rubric metrics all auto-output.
6. **Rubric completion condition**: follow the relevant Part's "completion condition" block in `.claude/layers/contradiction.md` as SoT (the required criteria + overall PASS ratio + per-theme exemption rules are the single SoT in the guide — do not enumerate figures in this command file).
7. **On completion, update frontmatter `last_updated` to today's date** (theme files only). The aggregate has no frontmatter, so skip this step — instead record the re-aggregation event in `log.md`.

**No iteration cap**. Repeat until required criteria PASS. If the same criterion FAILs twice in a row, the Guide's "safeguard" clause fires.

### Relation to Adjacent Routines

- **`/wiki-lint --fix` (= `all --fix`)**: performs mechanical repair (MD↔JSON sync · schema `_TODO` placeholder insertion), and on theme-JSON stale detection emits a rewrite block instructing Claude to carry out the JSON-regeneration chain. EDITOR-body rewrite is not included — for per-target-file reasoning, invoke explicitly via `/wiki-lint overview <target> --fix`·`/wiki-lint contradiction <target> --fix`.
- **`/wiki-lint contradiction theme --fix`**: Claude instruction to re-derive `_contradictions_themes.json` (Phase 1·2). See [`wiki-lint-theme-mapping.md`](wiki-lint-theme-mapping.md).
- **`/wiki-lint contradiction <theme-slug> --fix`**: the above mechanical repair limited to the target file + a Claude EDITOR rewrite instruction (Part 1 Rubric is SoT at [`.claude/layers/contradiction.md` → `## Evaluation Rubric`](../layers/contradiction.md#evaluation-rubric) Part 1).
- **`/wiki-lint contradiction aggregate --fix`**: diagnoses `wiki/contradiction.md` against the L2-4 Rubric (19 criteria per `contradiction-aggregate.roster`) + a Claude rewrite instruction (Part 2). This aggregate path has N/A mechanical repair — the aggregate file has no skeleton · AUTO block.
- **`python tools/build.py contradictions`** (independent pipeline): re-extracts the `_contradictions.json` raw DB (collects source `## Connections` `contradicts:` lines · classifies type). The build does not touch theme MDs (by-design no AUTO blocks). Auto-called by `/wiki-ingest`·`/wiki-lint --fix`.

Append to log.md: `## [today's date] lint | contradiction <target> rewrite` (on Claude rewrite completion) + load this rewrite cycle's Desk VERIFY₂ actionable defects into the corpus via `log_defect` (bare diagnosis · mechanical `--fix` are excluded, being standing state — SoT: [`agents/editor-in-chief.md`](../agents/editor-in-chief.md) automatic channel).

## source Group (`/wiki-lint source [<target>]`)

A routine dedicated to diagnosing conformance to the Phase 2 new schema (claim atomization · citation type · evidence grade). It targets Layer 2-1 source reflection files (introduction date · migration history are in `log.md`).

**Target files**: all of `wiki/sources/*.md`.

**target argument interpretation**:

| Argument | Scope | `--fix` behavior |
|------|--------|-------------|
| (none) | Diagnose all sources — output only the count of Phase 2 schema conformance (per-file detail is advisory) | Unsupported (schema conversion needs semantic analysis — authoring is in source.md § Authoring) |
| `<source-slug>` | That single source MD — output the automatic metrics of `.claude/layers/source.md` § Evaluation Rubric per-file | Unsupported |

A slug is a file stem of `wiki/sources/*.md`.

### Diagnosis Mode

Calls `python tools/lint.py source [<target>]` to output:
- **When a target is specified**: that source's `[Rubric] G1~G5` + `[Rubric] C1~C3` + `[Rubric] A1~A3·S1·W1·L1·F1·T1·Sc1`, three lines (Rubric automatic metrics).
- **No target**: diagnose all sources — a one-line summary of Phase 2 schema conformance counts (number of sources with the G1 grade marker / total · number of sources with the C1 prefix / total, etc.) + a top-20 list of non-conformant source slugs.

Required-criterion FAIL = exit 1 (hard mode).

### Why no `--fix`

Source schema conversion needs semantic analysis (claim atomization · citation-type classification · evidence-grade determination), so it is out of deterministic lint `--fix` scope. The SoT for authoring · conversion is [`.claude/layers/source.md`](../layers/source.md) § Authoring / Decision Trees.

### Relation to Adjacent Routines

- **`/wiki-lint --fix` (= `all --fix`)**: performs mechanical repair only. Does not include source schema conversion.
- **`/wiki-ingest`**: new ingest enforces the new schema at step 4 — auto-calls `python tools/lint.py source <slug>`.

Append to log.md: `## [today's date] lint | source schema diagnosis` (on full diagnosis).

---

## Sub-procedure: Contradiction Theme Mapping Procedure

Re-deriving `_contradictions_themes.json` in full — the two-phase procedure, input structure, output schema, core principles, formatting, and self-validation — is in [`wiki-lint-theme-mapping.md`](wiki-lint-theme-mapping.md); it runs on the `contradiction theme --fix` path. Claims added by ingest take the incremental route below instead. What stays here governs a theme's life after derivation.

### Theme Lifecycle Invariants

lint auto-verified invariants:

- **claim-id permanence**: the SHA1 is a deterministic function of **the claim text alone**, so renaming a source leaves its ids untouched. Rewording a claim re-keys it and orphans whatever pointed at the old id — the re-judgment a rewrite deserves
- **No collision**: byte-identical claim text in two sources collapses to one id and fails theme coverage on `source_count` — build surfaces the colliding id; reword the less central claim and move its `claim_ids` entry in the same edit
- **No reuse**: do not reassign a deprecated/archived id to a new claim
- **No orphans**: every claim_id reaches exactly 1 theme or `unassigned` (Phase 1 only). On theme deprecation · merge · split, child claims are reassigned to another theme or `other-fragmentary`. Disappearing from JSON is a lint FAIL
- **Incremental update**: claims added by ingest are mapped incrementally in principle. On source +30% or a new cluster appearing, a fresh derivation via `--fix --yes` is recommended

### Theme Burn Criteria

A theme becomes a deprecation candidate if one or more of the 4 criteria below holds. lint surfaces it as advisory; it is executed after passing the periodic-review gate (Editor-in-Chief 1st proposal + wiki-operator 2nd approval).

- **(a) Persistent undersize**: `len(claim_ids) < 5` AND none of [`wiki-lint-theme-mapping.md`](wiki-lint-theme-mapping.md) Core Principle 5 (a)·(b)·(c) holds + the same for 3+ cycles (a signal that growth potential is exhausted) → absorb into `other-fragmentary`
- **(b) Axis ambiguity (claim_jaccard ≥ 0.5)**: 50%+ claim overlap with another theme → absorb/merge recommended. Auto-surfaced via the lint `claim_jaccard` metric
- **(c) Multi-axis mixing**: the `## Opposing Positions` narrative is not single-axis (explicit sub-axis branching) → split recommended. Triggers at claim 50+ if the [`wiki-lint-theme-mapping.md`](wiki-lint-theme-mapping.md) single-axis exemption does not apply
- **(d) Informational only**: a simple fact bundle, not a contradiction (type=related ratio 70%+, etc.) → absorb into other-fragmentary

### Dual Approval Gate for New Theme Slug

Adding a new theme slug is not a single decision but a 2-stage gate:

1. **1st gate — Editor-in-Chief classification agreement** (`.claude/agents/editor-in-chief.md`):
   - Stage 2.7 (a) review ([`wiki-lint-theme-mapping.md`](wiki-lint-theme-mapping.md)): evaluate the possibility of an adjacent-axis merge first
   - If no adjacent axis + the separate-axis essence is clear, 1st-approve the new theme slug + escalate to the wiki-operator gate
   - The 1st review is a routing · consistency check (the first-checker role of the dual authority)

2. **2nd gate — wiki-operator final approval** (Human Reviewer Gate, `CLAUDE.md` § Human Reviewer Gate):
   - 1st-pass case → wiki operator final approve/reject
   - On rejection → 1st re-review (alternative theme or adjacent-axis absorption)
   - Twice rejected → absorb into other-fragmentary

The theme slug is a permanent-decision area, so a dual gate rather than a single decision-maker secures prudence.

---

## Sub-procedure: Conflict Axis Sync Rule

The synchronization rule for the conflict-axis 4 tiers — raw DB `_contradictions.json` → theme mapping `_contradictions_themes.json` → theme MD `<theme>.md` → aggregate `wiki/contradiction.md`.

**The theme MD is the Source of Truth for conflict-axis analysis**, and the aggregate is a product that rolls it up. Synchronization is **bottom-up, single-direction**.

### Sync Procedure (3 Steps)

1. **When the L2-2 raw DB is updated** — `/wiki-lint contradiction theme --fix` — instruction to re-derive `_contradictions_themes.json` (procedure: [`wiki-lint-theme-mapping.md`](wiki-lint-theme-mapping.md))
2. **JSON ↔ MD consistency** — `/wiki-lint contradiction --fix` — JSON-only slug → MD skeleton creation, MD-only slug (orphan MD) deletion. **Both actions require passing the confirmation prompt**, bypassable with `--yes`
3. **MD body authoring** → L2-4 re-aggregation

### Responsibility Split

| Check target | Owning lint group | Responsibility location |
|---|---|---|
| JSON ↔ MD mapping consistency | `contradiction` (MD side) | A mapping mismatch is a state where MD has not reflected a re-derived JSON, so the fix responsibility is on the MD side |
| JSON integrity itself | `contradiction theme` | Sole owner |

### Unidirectional Principle

The above synchronization is raw DB → theme MD → aggregate, **bottom-up single-direction**. Reverse updates from the aggregate (`wiki/contradiction.md`) to a theme MD are forbidden — the aggregate is a roll-up product, not the source of truth.

## Human Reviewer Gate

The global gate is SoT at [`CLAUDE.md` "Human Reviewer Gate"](../../CLAUDE.md#human-reviewer-gate). Gates specific to this command:

- A same-reason FAIL on the 3rd ADAPT of an `overview <target> --fix` or `contradiction <theme> --fix` chain → escalate to a human
- A new contradiction theme slug derived as a result of `contradiction theme --fix` (a new theme branch in the Phase 2 re-derivation)
- Critical/high defects remaining in the Desk qualitative review (limited to chain mode where the lint body invokes the qualitative review)
