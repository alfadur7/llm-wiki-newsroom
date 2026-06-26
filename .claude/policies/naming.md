# Naming Conventions

## Slugs & Filenames

- **Source slugs**: lowercase `kebab-case` (`[a-z0-9-]`) matching the source filename (e.g., `anthropic-mythos-overhyped-debate.md`) — any uppercase mixed in is a hard fail in `python tools/lint.py source`.
- **Source pages** (`wiki/sources/*.md`): `kebab-case.md`
- **Concept pages** (`wiki/concepts/*.md`): `TitleCase.md` (e.g., `ReinforcementLearning.md`, `RAG.md`)
- **Entity pages** (`wiki/entities/*.md`):
  - **Default — entities** (companies, people, products): English `TitleCase.md` (e.g., `OpenAI.md`, `Microsoft.md`, `OpenSourceInitiative.md`). An English abbreviation/brand name that is the industry standard is used as-is (e.g., `AWS.md`, `CNCF.md`)
  - **Non-Latin-script entity (exception)**: an entity commonly known only by a non-Latin name uses a **native-script filename** (e.g., `신한은행.md` Shinhan Bank). This is the exception, not a co-primary default; English `TitleCase` is preferred whenever a standard Latin-script name exists.

## Avoiding Reserved Meta-Doc Names

A `wiki/**/*.md` filename must not case-fold to `CLAUDE.md` or `README.md`. Windows NTFS and default macOS are case-insensitive, so `Claude.md`, `claude.md`, `README.md`, etc. all resolve to the same file, and the Claude Code harness mistakes these for project-instruction files, injecting the entity content as a system-reminder every session.

**Collision avoidance**: add a suffix, e.g., the `Claude` entity → `ClaudeLLM.md`.

`python tools/lint.py meta schema` detects violations automatically.

**Discoverability of suffixed hubs**: a hub whose filename diverges from its common name (such as one with the collision-avoidance suffix above) includes the common name in its frontmatter `title` and `tags` (e.g., `ClaudeLLM.md` → `title: "Claude"` · `tags: [Claude, …]`). Bilingual title/tags (e.g., `title: "클로드 (Claude)"` · `tags: [클로드, Claude, …]`) are added only under WIKI_LANG=ko or for a native-script entity. The ingest existence-check finds variant-slug hubs by content-grepping the title and tags rather than the filename, preventing duplicate creation.

## Homonymous-Abbreviation Disambiguation

When the same abbreviation refers to different entities, give each meaning a distinct filename, and link the non-default meaning with a `[[canonical-slug|abbrev]]` alias (the referent is decided from body context).

- **IDC**: `IDC` (internet data center) / `IDCResearch` (the market-research firm — source of forecasts, statistics, and market share)

## Entity Classification (`kind`)

Entity frontmatter is required to carry `kind: person | org | product`. This is because the hub-promotion policy treats people (`person`) differently from organizations and products — for a person, absorption into the affiliated organization's hub is the default, and a full hub is reserved for the cross-cluster independent-actor exception (`.claude/layers/hub.md` ②′).

- **person** — an individual (executive, researcher, official, founder, etc.)
- **org** — a company, institution, group, or government department
- **product** — a product, software, solution, or model

`python tools/lint.py hub schema` detects a missing or invalid `kind` on an entity, and `hub promotion` applies the absorption-default branch to `kind: person`. Concepts and timelines are a single kind, so they do not carry `kind`.

## Threshold for Adding an Entity (people, companies, SW solutions)

An entity stub is created **only for a core entity that is cited multiple times and appears across multiple clusters**. The same threshold applies to people, company, and SW-solution entities alike. Do not propose a stub swayed by the nominal authority of a title (CEO, lawmaker, professor) or the nominal brand recognition of a company (a global IT firm, an SK Group subsidiary, etc.). A new entity requires the explicit approval of the wiki operator.

**Threshold conditions** (all must be met to create a stub):
- **≥3 distinct source citations** (multiple citations within a single source do not count toward the threshold — a hub is a multi-source synthesis anchor)
- Appears in multiple clusters ≥ 2 clusters (natural appearance, not via paired_with)
- A core narrative role — mere enumeration or a peripheral-layer citation does not qualify; it must be a functional anchor such as a consortium leader, an SI mainstay, or a dominant claimant

**Demotion conditions** (plain text on one-off appearance):
- Appears one or two times in the body, isolated
- In a position of mere enumeration or a brand list (no role exposition)
- Only on the peripheral layer / citing side (not the narrative mainstay)

**Verification procedure** (spot-check before proposing a new stub):
- **Confirm frequency and cluster with `python tools/count_mentions.py <name>`** — it excludes auto-generated files (`_catalog` · `_source_map`) and has the threshold judgment built in. A raw `grep wiki/sources/` is forbidden because it over-counts catalog `.md` files (historical example from the prior Korean corpus: the Kim Tae-su case).
- Judge from the body whether it is a narrative mainstay or a peripheral layer.
- A Desk recommendation can mis-count appearances, so the main session spot-checks directly.
- Trigger the wiki-operator gate and create the stub only when the threshold is met.

**Applied cases** (historical examples from the prior Korean corpus, retained as illustrations of the threshold judgment):
- Accepted: SK Shieldus (3 citations + ZETIA consortium leader) · Kim Yong-beom (5 sources accumulated) · AhnLab (multiple citations + the CloudMate acquisition narrative mainstay)
- Rejected: TmaxCloud (1 one-off citation) · Webcash (1–2 citations, mere enumeration) · M-DAQ Global (1 citation, peripheral layer) · one-off people · one-off companies/outlets

The operational-policy SoT is kept consistent with `.claude/projects/.../memory/feedback_no_single_source_stub.md` (local memory) — when this policy changes, update that memory too.

## Threshold for Adding a Concept (concepts, techniques, phenomena, standards)

A concept hub is created for an **analytical axis that ties multiple sources together**. Its nature differs from an entity — an entity is measured by appearance frequency and demotes to plain text, whereas a concept is measured by conceptual independence and, on demotion, is **absorbed into a higher-level existing concept** (concepts are hierarchical). A new concept also requires the explicit approval of the wiki operator.

**Threshold conditions**:
- **Recommended: functions as an analytical axis in ≥3 distinct sources** — a conceptual anchor that ties multiple sources together, not mere term appearance (consistent with the entity threshold)
- **Cannot be absorbed into a higher-level existing concept hub** — if a higher-level one subsumes it, absorption is the default. Descriptive neologisms ("renaissance developer," "verification debt") are almost always absorption candidates.
- **Prefer pull signals** — a cross-cutting concept candidate in `hub suggestions` (an un-created concept that ≥2 seeds already point to via `[[wikilink]]`) is strong grounds for creation.

**Named-concept exception**: if it is a uniquely named technique, phenomenon, pattern, standard, or attack technique with independent value as a cross-cutting analytical axis, it is allowed even with ≤2 sources (e.g., [[VendorLockIn]] · [[OversightParadox]] · [[StranglerFig]] · [[CognitiveDebt]]). But descriptive neologisms and mere terms are absorbed upward; even a named one with only 1 source may be held as plain text (editor's judgment).

**Absorption examples**: AP2 → [[AIAgentPayment]] · GraphRAG → [[RAG]] · hyperscaler → [[CSP]] · colocation → [[DataCenter]].
