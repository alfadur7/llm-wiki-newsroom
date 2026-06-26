Health-check the LLM Wiki for issues.

Usage: `/wiki-lint [<group>] [<subcmd|target>] [--fix]`

## Traversal Pattern

A verify-and-fix cycle. The Copy Editor is the lead; when `--fix` is set, the Columnist and Desk chain is entered.

| Mode | Cycle | Owner |
|---|---|---|
| **Check only** (no `--fix`) | VERIFY | Copy Editor (`tools/lint.py`) — exit code + lint-report.md |
| **`overview/contradiction <target> --fix`** (L2-3·L2-4 rewrite) | VERIFY → ADAPT → APPLY → VERIFY | Copy Editor (VERIFY₁) → Columnist (ADAPT) → Copy Editor → Desk (VERIFY₂) → Editor-in-Chief gate |
| **Other group `--fix`** (`graph`·`hub`, etc. — auto-enrich/correct) | (deterministic) | Copy Editor (formattable-area auto-fix only; no meaning-affecting changes) |

In this chain, `--yes` is **Claude's explicit opt-in to executing the chain** — deferring to `lint-report.md` violates the opt-in intent (`.claude/hooks/lint-chain-guard.sh` enforces this at the system level).

## Sub-procedure (Owned by This Folder)

Two sub-procedures are the sole responsibility of this command:
- [`## Sub-procedure: Contradiction Theme Mapping Procedure`](#sub-procedure-contradiction-theme-mapping-procedure) — the raw DB → JSON mapping procedure for `contradiction theme --fix`
- [`## Sub-procedure: Conflict Axis Sync Rule`](#sub-procedure-conflict-axis-sync-rule) — the 4-tier bottom-up synchronization rule for `contradiction --fix`

The [A]–[G] code definitions and the diagnostic output format for the Cluster Health Diagnostic are not a separate sub-procedure; they are defined inline in the `graph clusters` row of the [`## Group Structure`](#group-structure) table plus the `Cluster health` item under [`## Check Items`](#check-items-full-suite-layout).



`$ARGUMENTS` is optional. With no arguments, the full suite (= the `all` group) runs; specifying a group or subcommand runs only that scope.

```
Usage: /wiki-lint [<group>] [<subcmd|target>] [--fix]

Examples:
  /wiki-lint                                        # full suite (graph · hub · meta · overview · contradiction + suggestions)
  /wiki-lint --fix                                  # full suite + each group's supported --fix in one pass
  /wiki-lint graph                                  # structure · orphans · clusters · raw-files · internal-refs in one pass
  /wiki-lint graph orphans --fix                    # single subcommand
  /wiki-lint graph gaps [--gap-type <slug>] [--top 5]   # gap diagnostic (OPT-IN, not auto-run by `all`)
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

`--yes` (`-y`) bypasses the file create/delete confirmation prompt of `overview --fix`·`contradiction --fix`. In a non-TTY environment (Claude Code Bash·CI) the prompt cannot be answered, so the command aborts; add `--yes` only when you intend deliberate execution after review. The `--fix` body itself has no effect in other groups (`graph`·`hub`, etc.) — those perform only content edits and auto-enrichment, with no file creation or deletion.

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

**No requesting user approval (limited to the `--yes` context)**: Only in calls that include the `--yes` token, before entering the chain, do not produce wait-for-user-input utterances such as "I request the wiki operator's approval," "please instruct me to proceed to the next step," or "awaiting the chain-entry gate" — because the `--yes` token is itself the chain-entry approval. A `--fix`-only call without `--yes` is the exact opposite — it corresponds to the "only correct case for non-execution" above, where waiting for user confirmation is the SoT-correct answer. The human-reviewer gate is not a chain-**entry** gate but fires at chain-**mid** triggers (branching to a new contradiction theme slug · adding a new cluster slug · large-scale body rewrite >50% · a same-reason FAIL on the 3rd ADAPT · publishing L2-4 root content) — see [`CLAUDE.md` "Human Reviewer Gate"](../../CLAUDE.md#human-reviewer-gate) as the single SoT.

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
| `graph` | `internal-refs` | Detects **markdown links** from published content (root meta + entities·concepts·overviews·contradictions·syntheses·timelines·trails) into the build/governance tree (`.claude/`·`tools/`·`CLAUDE.md`·`raw/`·`log.md`). A RAG reader cannot open these, and they pollute the corpus with self-meta. **Link-based, so no false positives** — plain-text topic mentions like Claude Code's `CLAUDE.md`·`.claude/` are not links and are not detected. Symmetric check to `hub voice`·claude-guideline-voice (sources are out of scope since their bodies aren't exported) | Unsupported — removal/rephrasing is the author's call (same as `hub voice`) |
| `graph` | `gaps` | 10-type deterministic gap diagnostic. Output is split by Track A (sparse-cluster·single-source·stale-hub — auto-enrich targets) · Track B (bridge — surfaced for wiki-operator decision) · Track C (orphan-claims·cap-theme·stale-theme — separate cycle) · Track D (synthesis·trail·timeline — Columnist-derived authoring). **OPT-IN — not auto-run by `lint all`** (betweenness sampling + a full hub-frontmatter scan is heavy). Definitions·thresholds are SoT in [`.claude/operations/gap-detection-rollout.md`](../operations/gap-detection-rollout.md) | Unsupported — enrichment triggers are `/wiki-news --gap`, theme rewrite is `/wiki-lint contradiction theme --fix` |
| `graph` | `drift` | Compares warm↔cold Leiden partition quality (modularity) — detects cluster-stability drift. **OPT-IN — not auto-run by `lint all`** (cost of cold Leiden recomputation) | Unsupported |
| `hub` | `speakers` | Among quoted speakers (the `> "..." — Name (role)` pattern), those that meet **both** conditions of **multiple quotes (≥3 total) AND appearing in multiple sources (≥3 distinct files)** while `entities/<name>.md` is missing. Thresholds adjustable via `--min-quotes`·`--min-sources` flags | Unsupported (current-role verification required; Claude must not auto-stub) |
| `hub` | `suggestions` | Commonly-referenced but not-yet-created links + frequently-mentioned terms with no page (informational — no pass/fail impact) | Unsupported |
| `hub` | `schema` | L2-2 hub frontmatter (entities/concepts/timelines all require `title·type·tags·sources·last_updated` + `type` value matches the directory) | **Auto-fill type + last_updated** (deterministic, based on directory · git log). title/tags/sources need semantic inference → report only |
| `hub` | `voice` | L2-2 hub body self-meta voice antipatterns (`this hub …`·`covered separately`, etc. — and the ko-mode antipattern tokens `본 hub는`·`별도 정리한다` — violations of encyclopedic neutrality). FAIL → exit 1. Fenced code blocks are excluded from the check | Unsupported (rephrasing is the author's call; symmetric to `internal-refs`) |
| `hub` | `body` | L2-2 hub body density advisory (body length · number of `## Connections` links — detects nav-anchor bloat; thresholds injected via `_manifest.json`). No pass/fail impact | Unsupported (delegating to a sub-hub is a semantic judgment) |
| `hub` | `timeline` | L2-2 timeline `## Timeline` narrative advisory (quantitative-figure restatement · item formatting). No pass/fail impact | Unsupported |
| `hub` | `promotion` | L2-2 hub promotion-candidate triage (stub → full hub, informational) | Unsupported (promotion is a Desk gate) |
| `hub` | `demotion` | L2-2 hub demotion/deletion-candidate triage (one-off·isolated stub, informational) | Unsupported (demotion is a Desk gate + graph integrity) |
| `meta` | `schema` | CLAUDE.md integrity (anchor·file-ref·slash-cmd) + L2-3 ↔ L2-4 Rubric drift + English-header section convention + flat-lint-path recurrence guard | **Unsupported** — substituting a non-English header → English is not a 1:1 deterministic mapping but requires a meaning-preserving wording decision (e.g., `## Mode Routing (query type → mode dispatch)` → deciding between `Mode Routing by Query Type` vs `Routing by Type`). Same semantic-inference area as graph structure broken links — the `## --fix Mode (2) Claude` area branch |
| `overview` | — | `wiki/overviews/<cluster>.md` + `wiki/overview.md` — completeness · schema · Rubric metrics · Freshness + JSON↔MD slug 1:1 mapping (SoT is `graph/_clusters.json`) + **cluster name drift** (frontmatter `title`·body H1 vs `_clusters.json::clusters[].name`) + **frontmatter `cluster:` slug ↔ filename stem consistency** | **MD↔JSON sync** — JSON-only cluster slug → auto-generate skeleton, MD-only slug (orphan overview) → auto-delete. Both actions **run only after passing the confirmation prompt** (bypassable with `--yes`). Non-destructive repairs (alias-correcting un-aliased cluster links · inserting AUTO markers · **auto-syncing cluster name drift** — after a rename, batch-update frontmatter `title`·body H1 following the `cluster_labels.json` SoT · **correcting frontmatter `cluster:` slug** — in-place replacement based on filename stem) proceed without a prompt. **When a target is specified (=`<slug>` or `aggregate`)**: the above + an added Claude rewrite instruction block (no rewrite block is emitted on a target-less `all` call — explicit invocation via `/wiki-lint overview <target> --fix` is required) |
| `contradiction` | — (target=theme slug) | `wiki/contradictions/<theme>.md` — frontmatter · 4 H2 sections (no AUTO block — by design) + JSON↔MD slug 1:1 mapping (SoT is `_contradictions_themes.json`) + frontmatter `sources:` ↔ JSON-implied sources drift (informational) + **detection of residual legacy AUTO blocks** (artifacts of a past build pipeline) | **MD↔JSON sync** — JSON-only slug → auto-generate skeleton (using JSON `name`), MD-only slug (orphan MD) → auto-delete. Both actions **run only after passing the confirmation prompt** (bypassable with `--yes`). Non-destructive repairs (inserting missing-H2 `_TODO` placeholders + **removing legacy AUTO blocks** — deleting `<!-- AUTO:CLAIMS/SOURCES BEGIN/END -->` and the inner/preceding `## Sources` header) proceed without a prompt. **SoT freshness chain** — when `_contradictions_themes.json` is stale (any one of: ① the `source_count` snapshot differs from `_contradictions.json`'s current record count — record-count drift, the most direct signal / ② `_contradictions.json` has uncommitted edits AND `derived_at < today` / ③ `_contradictions.json`'s last commit date > `derived_at`), this pass's MD mutation is skipped (preventing propagation of stale theme boundaries) and a theme rewrite block (Phase 1·2 instructions) is auto-emitted so Claude performs the chain: regenerate JSON → `python tools/build.py contradictions` → re-run `/wiki-lint contradiction --fix --yes` |
| `contradiction` | `theme` | `wiki/contradictions/_contradictions_themes.json` integrity itself — JSON schema · claim-id validity · full coverage · Phase 2 conditions · Freshness against `_contradictions.json` | **Does not edit the JSON directly.** Emits only a Claude regeneration instruction block (the Guide's Phase 1→2 procedure) — the same block is emitted on the `contradiction --fix` stale gate to carry out the chain |
| `source` | — (target=source slug) | `wiki/sources/<slug>.md` Phase 2 new schema (claim atomization · citation type · evidence grade) — the 10 automatic metrics of `.claude/layers/source.md` | Unsupported — schema conversion needs semantic analysis, so it is out of deterministic `--fix` scope (authoring is in `.claude/layers/source.md` § Authoring) |
| `synthesis` | — (target=synthesis slug) | `wiki/syntheses/<slug>.md` — S1 required sections · source coverage · source existence · slug-alias (L2-3 Q&A synthesis schema). Included in `all` | **Generate skeleton** (if missing) + Claude rewrite instruction block — explicit invocation via `/wiki-lint synthesis <slug> --fix` |
| `trail` | — (target=trail slug) | `wiki/trails/<slug>.md` — S1 required sections · `## Path` links · path length 4-12 · slug-alias (L2-3 associative-trail schema). Included in `all` | **Generate skeleton** (if missing) + Claude rewrite instruction block — explicit invocation via `/wiki-lint trail <slug> --fix` |
| `staleness` | — (target) | Layer-cascade staleness — diagnoses pages whose upstream is newer than the page's authored date. For derived-narrative types (overview·contradiction·synthesis·trail·timeline + root meta), the basis is the **EDITOR-body git edit date** rather than frontmatter `last_updated`, preventing a partial edit from bumping only the date and masking body staleness (when inflated, marked as `body=…`). **Informational** (surfaced outside pass/fail in `all`) | Unsupported — re-grounding cannot be a deterministic `--fix` (needs cross-source synthesis · Desk gate). Surfaced pages are handled via Columnist→Desk→ADAPT (procedure: [`operations/staleness-reground-runbook.md`](../operations/staleness-reground-runbook.md)) |
| `all` | — | Sequentially runs all groups above + suggestions·promotion·demotion·staleness informational | Runs every group's supported `--fix` (overview Claude EDITOR rewrite is **excluded** — invoke explicitly via `/wiki-lint overview <target> --fix`). `contradiction theme` JSON regeneration is included as a chain on stale detection — `--yes` acts as the explicit opt-in |

For target-based groups (`overview`·`contradiction`), the second positional argument is not a subcommand but a target file slug. For overview it is a cluster slug (one of `_clusters.json`'s `clusters[].slug`) or `aggregate`; for contradiction it is a theme slug (regardless of MD existence — even a declaration in JSON makes it a valid target). **The `contradiction` group is a hybrid** — the single word `theme` dispatches first as a reserved subcommand (defined above), while any other second argument is interpreted as a theme-slug target. Using `theme` as a theme slug is forbidden (see `.claude/commands/wiki-lint.md` § Slug·Name Naming Criteria).

**Responsibility-separation principle**: the JSON↔MD mapping check lives on the `contradiction` (MD) side — the cause of a mapping mismatch is that the JSON was re-derived but the MD has not yet reflected it, and the fix is an MD-side action (skeleton generation · orphan-MD deletion). The internal integrity of the JSON itself is the sole responsibility of `contradiction theme`.

## Check Items (full suite layout)

1. **Orphan hubs** (`graph structure`) — among entities/concepts, pages not referenced by any other page via [[wikilink]] (trails, syntheses are independent documents and excluded)
2. **Orphan sources** (`graph orphans`) — sources in no hub's `sources:` frontmatter and not referenced by any `[[wikilink]]`. Two kinds:
   - Recoverable: the source's `## Connections` section has a valid hub [[wikilink]] → auto-recovered by `/wiki-lint graph orphans --fix`
   - Unconnected source: the `## Connections` itself is empty → manual review needed
2-A. **Declared-but-fileless sources** (`graph orphans`) — slugs present in a hub's frontmatter `sources:` but with no actual `wiki/sources/<slug>.md` file. Uses token-set Jaccard against existing source slugs to find the best match, in a 3-tier classification:
   - **AUTO-FIXABLE** (Jaccard ≥0.5) — many shared same-domain tokens. `--fix` auto-renames in the hub frontmatter `sources:`. If the target slug already exists in the same hub (correct/incorrect duplicate pattern), just remove the typo.
   - **SUGGESTION** (0.25 ≤ Jaccard < 0.5) — weak signal. Synonyms · transliteration typos (e.g., `cluster-a-open-weights` ↔ `open-weights-cluster-b`) may match tokens by coincidence, so human review is required.
   - **NO MATCH** (< 0.25) — no plausible candidate. Either an un-ingested plan or a phantom reference — not auto-removed (editor's judgment).
2-B. **Hub `## Connections` source link ↔ own frontmatter consistency** (`graph orphans`) — checks whether a source slug linked in a hub's own `## Connections` is registered in that hub's own frontmatter `sources:`. The `## Connections` section allows source links (`.claude/layers/hub.md` "list of related hub·source links"), but a linked source must also be registered in frontmatter sources to keep backlink·graph-edge consistency (hub.md "Source consistency"). Unregistered ones are auto-registered with `--fix` (backfill the hub's own `## Connections` → frontmatter `sources:`).
3. **Broken links** (`graph structure`) — [[wikilink]]s pointing to non-existent pages. Root meta files (overview, contradiction, index, log, lint-report) are also valid targets. Code blocks · inline code are auto-excluded. **`log.md` is excluded from the source scan** — being an append-only operational record, past cluster slugs · dissolved concepts permanently linger and surface as broken links every time, burying real regressions.
4. **Missing entity pages** (`graph structure`) — names referenced by 3+ pages but lacking their own page.
5. **Korean entity with English filename** (`graph structure`) — entities that are Korean companies · institutions · people but have an English filename (industry-standard English brands are excluded via the `ENGLISH_STANDARD` whitelist).
5-A. **Uncovered cited speakers** (`hub speakers`) — `> "..." — Name (role)` quoted speakers who meet **both** conditions of **≥3 total quotes + ≥3 distinct source files** while lacking an `entities/<name>.md` page. The two conditions are the operational threshold of the memory policy `feedback_no_single_source_stub` ("stub only for core figures who are quoted multiple times and appear across several sources"); single-source · 1–2-quote one-off citations are not actionable stub candidates. Single-file detection is handled by `/wiki-ingest` workflow step 10. **When creating a stub, current-role verification via `WebSearch` is mandatory** — between the article's writing date and now, the person may have changed jobs, retired, or been promoted. For people no longer in their role due to retirement · resignation, hold off on creation or request human-reviewer confirmation.
6. **Cluster health** (`graph clusters`) — reports Leiden codes [A]–[G]. Code definitions · Korean display names · action guides are defined inline in the `graph clusters` row of the [`## Group Structure`](#group-structure) table above (single SoT — drift prevention).
7. **Meta-doc schema** (`meta schema`) — a 4-axis bundle for meta documents:
   - **Integrity**: CLAUDE.md self-consistency — anchor-link targets exist, backtick file-path files exist, `/wiki-*` slash commands' definition files exist
   - **Rubric drift**: L2-3 Rubric ↔ L2-4 Rubric common-criterion-row sync (`.claude/layers/overview.md`·`.claude/layers/contradiction.md` `## Evaluation Rubric` sections are SoT; the row count's single SoT is the guide table)
   - **Language Convention**: no Korean in CLAUDE.md + `.claude/commands/*.md` section headers
   - **Flat-path guard**: blocks the `python tools/lint.py <flat-subcmd>` form — enforces the group form (`python tools/lint.py <group> [<sub>]`)
8. **L2-2 hub frontmatter** (`hub schema`) — every file in entities/ · concepts/ · timelines/ requires `title · type · tags · sources · last_updated` + `type` value matches the directory name (entity/concept/timeline).
9. **L2-3/L2-4 overview schema·Rubric** (`overview`) — `wiki/overviews/<slug>.md` completeness · frontmatter · H2 sections · AUTO markers · Rubric metrics (W1·W2·W3·X2) · Freshness + **cluster name drift** (frontmatter `title`·body H1 matches `_clusters.json::clusters[].name` SoT) + `wiki/overview.md` Rubric L2-4 (W1·W2·W3·D1·D2·D3·F1).
10. **Theme contradiction MD schema·mapping** (`contradiction`) — `wiki/contradictions/<theme>.md` frontmatter · H2 sections (`## Opposing Positions`·`## Representative Evidence`·`## Derived Tensions & Generational Readings`·`## Interpretive Direction`) + slug 1:1 mapping with the `_contradictions_themes.json` SoT (JSON-only → MD not created / MD-only → orphan MD) + detection of residual legacy AUTO blocks (CLAIMS/SOURCES) and their removal via `--fix`.
11. **Theme derivation JSON integrity** (`contradiction theme`) — `wiki/contradictions/_contradictions_themes.json` conforms to the `.claude/commands/wiki-lint.md` Output Schema, claim ids actually exist in `_contradictions.json`, full coverage (claim_ids ∪ unassigned == source_count), Phase 2 conditions (unassigned empty · theme ≤15 recommended — exceeding it enters the dual-approval gate for a new theme slug), claim-id lifecycle invariant (permanent · no reuse · no orphans), Freshness (whether re-derived after `_contradictions.json` was updated).

New-page candidates (`hub suggestions` — informational, no pass/fail impact):
- **Commonly-referenced but not-yet-created links** — pages commonly referenced from several pages but not yet created (0 of these is a wiki-health signal)
- **Frequently mentioned but page-less terms** — noun phrases that appear often in bodies but have no wiki page (precision ~40-50%, **auto-stub creation forbidden**, human-reviewer review required)
- Noise guards are maintained cumulatively via the internal BLOCKLIST + KOREAN_ALIAS of `tools/_lint/text_candidates.py`

Semantic checks (read and reason over page content):
11. **Contradictions** — claims that conflict between pages
12. **Stale summaries** — pages not updated after newer sources changed the picture
13. **Data gaps** — important questions the wiki can't answer; suggest specific sources to find

Output a structured markdown lint report. Output the per-group detail sections first, and at the end include only a one-line summary of every group in an **"## Action Items"** table. At the end, ask if the user wants it saved to lint-report.md.

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
- **`contradiction theme --fix` (JSON regeneration)**: the script does not edit JSON directly. It outputs only the Claude rewrite instruction block of the `.claude/commands/wiki-lint.md` Phase 1·2 procedure. The same block is emitted on the `contradiction --fix` stale gate → Claude catches the chain even mid-`all --fix --yes`.
- **`python tools/build.py` after fixes complete** — the full 5 phases (graph → clusters → contradictions → index → dependencies). When stub creation · [[wikilink]] addition · AUTO-marker insertion is involved, this guarantees downstream updates.

Reflect each fix in the report. Append to `log.md`: `## [today's date] lint | Wiki health check`

## Lint Report Output Format Requirements

Per-target detail requirements to follow when authoring `/wiki-lint [--fix]` results into `lint-report.md`. The purpose of this convention is to **force the overview and contradiction group report sections to maintain symmetric depth** — because the script (`tools/lint.py`) emits symmetric per-target metrics (Rubric + drift tier + rewrite recommendation) to stdout for both groups, summarizing only one side when Claude authors the report creates an asymmetry that forces the human reviewer to re-confirm via a separate run. The requirements below catch that authoring drift.

### Target Groups

These requirements apply only to the **two target-based groups (`overview`·`contradiction`)**. Other groups (`graph`·`hub`·`meta`·`theme`) have few files or their own structure, and are outside these requirements.

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
| (none) | Diagnose all L2-3 clusters + all of L2-4 | ❌ `--fix` rejected (target-not-specified error) |
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
2. **Read `.claude/layers/overview.md`** — the same Part.
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

A theme slug is one of the `themes` keys of `_contradictions_themes.json` or a file stem of `wiki/contradictions/*.md` (regardless of MD existence). The reserved word `theme` dispatches first as a subcommand, so it must not be used as a theme slug.

### Diagnosis Mode (no `--fix`)

Calls `python tools/lint.py contradiction [<target>]` to output:
- **Schema issues**: missing H2 sections · frontmatter fields · missing AUTO markers, etc.
- **JSON↔MD mapping**: JSON-only slug (MD not created) · MD-only slug (orphan MD)
- **frontmatter `sources:` ↔ JSON-implied sources drift** (informational)
- **Rubric metrics**: each theme file's `[Rubric]` (Part 1 automatic metrics) + aggregate's `[Rubric L2-4]` (Part 2 automatic metrics). The automatic-metric count · number of output lines are SoT in the relevant Part of `.claude/layers/contradiction.md`

Exit code 0 means schema · mapping within scope pass. 1 means issues remain.

### Rewrite Mode (`--fix` + target=theme-slug or aggregate)

In the same pattern as overview, the script **does not edit the EDITOR area directly**. At the end of the diagnostic output it emits a "Claude rewrite instruction block," handing the execution order to Claude. `tools/_lint/contradiction.py`'s `_emit_rewrite_block` (theme) · `_emit_rewrite_block_aggregate` (aggregate) auto-output the Part 1 · Part 2 guide procedures respectively.

**Common procedure** (the order the rewrite block outputs):

1. **Read `.claude/layers/contradiction.md`** — the Part matching the target scope (L2-3=Part 1, L2-4=Part 2).
2. **Read `.claude/layers/contradiction.md`** — the same Part.
3. **Read the target file(s)**: for a theme slug, `wiki/contradictions/<theme>.md` + resolve the `_contradictions.json` records via that theme's `claim_ids` in `_contradictions_themes.json` + the key source files. For aggregate, `wiki/contradiction.md` + all theme files in full (by `_contradictions_themes.json` keys).
4. **Rewrite following the Authoring Guide "execution order."** A theme MD has 4 H2 sections; the aggregate has the `# Contradictions by Theme` root + 4 required sections. All are EDITOR area in their entirety, with no AUTO blocks.
5. **Re-diagnose**: re-run `python tools/lint.py contradiction <target>` → schema · mapping · Rubric metrics all auto-output.
6. **Rubric completion condition**: follow the relevant Part's "completion condition" block in `.claude/layers/contradiction.md` as SoT (the required criteria + overall PASS ratio + per-theme exemption rules are the single SoT in the guide — do not enumerate figures in this command file).
7. **On completion, update frontmatter `last_updated` to today's date** (theme files only). The aggregate has no frontmatter, so skip this step — instead record the re-aggregation event in `log.md`.

**No iteration cap**. Repeat until required criteria PASS. If the same criterion FAILs twice in a row, the Guide's "safeguard" clause fires.

### Relation to Adjacent Routines

- **`/wiki-lint --fix` (= `all --fix`)**: performs mechanical repair (MD↔JSON sync · schema `_TODO` placeholder insertion), and on theme-JSON stale detection emits a rewrite block instructing Claude to carry out the JSON-regeneration chain. EDITOR-body rewrite is not included — for per-target-file reasoning, invoke explicitly via `/wiki-lint overview <target> --fix`·`/wiki-lint contradiction <target> --fix`.
- **`/wiki-lint contradiction theme --fix`**: Claude instruction to re-derive `_contradictions_themes.json` (Phase 1·2). See `.claude/commands/wiki-lint.md`.
- **`/wiki-lint contradiction <theme-slug> --fix`**: the above mechanical repair limited to the target file + a Claude EDITOR rewrite instruction (Part 1 Rubric is SoT at [`.claude/layers/contradiction.md` → `## Evaluation Rubric`](../layers/contradiction.md#evaluation-rubric) Part 1).
- **`/wiki-lint contradiction aggregate --fix`**: diagnoses `wiki/contradiction.md` against the L2-4 Rubric 15 criteria + a Claude rewrite instruction (Part 2). This aggregate path has N/A mechanical repair — the aggregate file has no skeleton · AUTO block.
- **`python tools/build.py contradictions`** (independent pipeline): re-extracts the `_contradictions.json` raw DB (collects source `## Connections` `contradicts:` lines · classifies type). The build does not touch theme MDs (by-design no AUTO blocks). Auto-called by `/wiki-ingest`·`/wiki-lint --fix`.

Append to log.md: `## [today's date] lint | contradiction <target> rewrite` (on Claude rewrite completion) + load this rewrite cycle's Desk VERIFY₂ actionable defects into the corpus via `log_defect` (bare diagnosis · mechanical `--fix` are excluded, being standing state — SoT: [`agents/editor-in-chief.md`](../agents/editor-in-chief.md) automatic channel).

## source Group (`/wiki-lint source [<target>]`)

A routine dedicated to diagnosing conformance to the Phase 2 new schema (claim atomization · citation type · evidence grade). It targets Layer 2-1 source reflection files (introduction date · migration history are in `log.md`).

**Target files**: all of `wiki/sources/*.md`.

**target argument interpretation**:

| Argument | Scope | `--fix` behavior |
|------|--------|-------------|
| (none) | Diagnose all sources — output only the count of Phase 2 schema conformance (per-file detail is advisory) | Unsupported (schema conversion needs semantic analysis — authoring is in source.md § Authoring) |
| `<source-slug>` | That single source MD — output the 10 automatic metrics of `.claude/layers/source.md` per-file | Unsupported |

A slug is a file stem of `wiki/sources/*.md`.

### Diagnosis Mode

Calls `python tools/lint.py source [<target>]` to output:
- **When a target is specified**: that source's `[Rubric] G1·G2·G3·C1·C2 ...` + `[Rubric] A1·A2·S1·W1·L1`, two lines (Rubric automatic metrics).
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

This guide prescribes the procedure for reading all claims in `_contradictions.json` and generating `_contradictions_themes.json` (the theme ↔ claim mapping SoT). Since the output is **structured JSON, not markdown prose**, journalism · consulting form does not apply (unlike overview authoring). Schema conformance · contradiction-axis accuracy · self-validation are the core.

A Claude with no prior knowledge must be able to read this guide alone and reproduce the same quality · structure.

Read before working:
- `CLAUDE.md` → "Contradictions Sync Rule" (SoT hierarchy · cross-assignment principle)
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
| `id` | First 8 chars of the SHA1 hash. The key referenced by `claim_ids` in `_contradictions_themes.json` | **Must** use this value verbatim |
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

A Phase 2 Priority Read target. Each source page consists of frontmatter + 5 H2 sections:

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
| **Preliminary/core theme upper bound** | No limit | **50 advisory** (single-axis exemption always active; the body is a 7–13-bullet selection) |
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
  - **Reserved word**: the bare slug `theme` is forbidden — it collides with the `/wiki-lint contradiction theme` subcommand. `tools/_lint/contradiction_theme.py`'s `RESERVED_SLUGS` outputs FAIL on violation.
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

Before output, you must pass all of the below. If any one is short, fix and re-validate.

#### Common (Phase 1·2)

- [ ] **Count match**: dedup count of all `claim_ids` across `themes` + count of `unassigned` == `source_count`
- [ ] **id validity**: every element of `claim_ids`·`unassigned` is an id that actually exists in `_contradictions.json`
- [ ] **Slug format**: every slug matches the `[a-z0-9-]+` pattern (kebab-case English)
- [ ] **Slug reserved word**: no theme uses the bare slug `theme` (lint collision)
- [ ] **Slug quality**: each slug is a 2–5-word structure suggesting the contradiction axis
- [ ] **Name quality**: Korean, and whether the contradiction · tension · dispute is apparent
- [ ] **Grouping reasonableness**: sample 1 claim from each theme and self-question its membership rationale — Core Principle 2 satisfied
- [ ] **Cross-assignment justification**: a claim assigned to multiple themes has explicit evidence for each membership
- [ ] **phase field accurate**: matches the Phase number this run performed
- [ ] **JSON validity**: right before Write, mentally `json.loads()`-parse the entire output to confirm no syntax errors
- [ ] **Full conformance to Formatting Rules**

#### Phase 1 Only

- [ ] No single-claim preliminary theme (lower bound 2)
- [ ] `other-fragmentary` exists and trivial claims are clearly separated
- [ ] For claims placed in `unassigned`, the worker (Claude) can internally explain "why they are ambiguous" (the rationale is not written into JSON)

#### Phase 2 Only

- [ ] **Confirm the Phase 1 output was read** (secured fragmentary · unassigned from `_contradictions_themes.json`)
- [ ] **`other-fragmentary` claim_ids are not reduced vs Phase 1** (claims placed in `other-fragmentary` in Phase 1 are kept in full in Phase 2. Pipeline principle — Phase 2 does not overturn Phase 1 decisions, securing consistency · efficiency)
- [ ] **`unassigned` == []** (resolution via source Reads complete)
- [ ] **`len(themes) <= 15` recommended** (including other-fragmentary). On exceeding, the worker internally states the rationale for entering the dual-approval gate for a new theme slug (lint advisory)
- [ ] **Every theme other than `other-fragmentary` has `len(claim_ids) >= 5`** or clearly meets one of the core-issue exceptions (a)·(b)·(c)
- [ ] No theme exceeds the upper bound of 50 — or the Stage 2.7 (c) single-essential-contradiction-axis exemption rationale is stated (when the sub-axis candidates are all different facets of the same axis, the single-axis exemption is always active)
- [ ] **claim-id lifecycle invariant** — an id once assigned is permanent · no reuse. On theme deprecation, forced re-assignment of child claims (move to another theme or other-fragmentary, no orphans)
- [ ] Source-Read record: the worker can internally track which source was read for which claim-judgment purpose (not written into JSON)

---

### Theme Lifecycle Invariants

lint auto-verified invariants:

- **claim-id permanence**: when regenerated by `tools/build.py contradictions`, the SHA1 hash is a deterministic function of source slug + claim body. The id is identical while the source body is unchanged
- **No reuse**: do not reassign a deprecated/archived id to a new claim
- **No orphans**: every claim_id reaches exactly 1 theme or `unassigned` (Phase 1 only). On theme deprecation · merge · split, child claims are reassigned to another theme or `other-fragmentary`. Disappearing from JSON is a lint FAIL
- **Incremental update**: claims added by ingest are mapped incrementally in principle. On source +30% or a new cluster appearing, a fresh derivation via `--fix --yes` is recommended

### Theme Burn Criteria

A theme becomes a deprecation candidate if one or more of the 4 criteria below holds. lint surfaces it as advisory; it is executed after passing the periodic-review gate (Editor-in-Chief 1st proposal + wiki-operator 2nd approval).

- **(a) Persistent undersize**: `len(claim_ids) < 5` AND none of Core Principle 5 (a)·(b)·(c) holds + the same for 3+ cycles (a signal that growth potential is exhausted) → absorb into `other-fragmentary`
- **(b) Axis ambiguity (claim_jaccard ≥ 0.5)**: 50%+ claim overlap with another theme → absorb/merge recommended. Auto-surfaced via the lint `claim_jaccard` metric
- **(c) Multi-axis mixing**: the `## Opposing Positions` narrative is not single-axis (explicit sub-axis branching) → split recommended. Triggers at claim 50+ if the single-axis exemption does not apply
- **(d) Informational only**: a simple fact bundle, not a contradiction (type=related ratio 70%+, etc.) → absorb into other-fragmentary

### Dual Approval Gate for New Theme Slug

Adding a new theme slug is not a single decision but a 2-stage gate:

1. **1st gate — Editor-in-Chief classification agreement** (`.claude/agents/editor-in-chief.md`):
   - Stage 2.7 (a) review: evaluate the possibility of an adjacent-axis merge first
   - If no adjacent axis + the separate-axis essence is clear, 1st-approve the new theme slug + escalate to the wiki-operator gate
   - The 1st review is a routing · consistency check (the first-checker role of the dual authority)

2. **2nd gate — wiki-operator final approval** (Human Reviewer Gate, `CLAUDE.md` § Human Reviewer Gate):
   - 1st-pass case → wiki operator final approve/reject
   - On rejection → 1st re-review (alternative theme or adjacent-axis absorption)
   - Twice rejected → absorb into other-fragmentary

The theme slug is a permanent-decision area, so a dual gate rather than a single decision-maker secures prudence.

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

## Sub-procedure: Conflict Axis Sync Rule

The synchronization rule for the conflict-axis 4 tiers — raw DB `_contradictions.json` → theme mapping `_contradictions_themes.json` → theme MD `<theme>.md` → aggregate `wiki/contradiction.md`.

**The theme MD is the Source of Truth for conflict-axis analysis**, and the aggregate is a product that rolls it up. Synchronization is **bottom-up, single-direction**.

### Sync Procedure (3 Steps)

1. **When the L2-2 raw DB is updated** — `/wiki-lint contradiction theme --fix` — instruction to re-derive `_contradictions_themes.json` (procedure is in this file's [`## Sub-procedure: Contradiction Theme Mapping Procedure`](#sub-procedure-contradiction-theme-mapping-procedure))
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
