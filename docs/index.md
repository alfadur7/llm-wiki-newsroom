---
layout: default
title: LLM Wiki Newsroom
description: >-
  A multi-agent "newsroom" on Claude Code that turns your documents into a
  cross-linked markdown wiki — the writer never reviews their own page. Local-first,
  plain markdown + git, a structured alternative to RAG.
software_schema: true
schema_inlanguage: en
schema_url: "https://alfadur7.github.io/llm-wiki-newsroom/"
schema_description: >-
  A multi-agent "newsroom" on Claude Code that turns your documents into a
  cross-linked, human-readable markdown wiki, where the agent that writes a page
  is never the one that reviews it. Local-first, plain markdown and git, a
  structured alternative to RAG.
schema_keywords: "LLM wiki, Karpathy LLM Wiki, RAG alternative, multi-agent, Claude Code, knowledge base, second brain, Obsidian, contradiction tracking, self-evolving guidelines, local-first"
hreflang_en: "https://alfadur7.github.io/llm-wiki-newsroom/"
hreflang_ko: "https://alfadur7.github.io/llm-wiki-newsroom/ko/"
---

*Read this in [한국어]({{ '/ko/' | relative_url }}).*

**LLM Wiki Newsroom is an open-source framework that turns a folder of documents into a cross-linked, human-readable markdown wiki, maintained by an AI agent organized as a five-role newsroom.** Drop articles, notes, and PDFs into a folder, run one command, and the agent — powered by [Claude Code](https://www.anthropic.com/claude-code) — reads them, extracts entities, concepts, and relationships, and organizes everything into interlinked pages. It's a persistent, structured alternative to RAG. Unlike most takes on the idea, **the agent that _writes_ a page is never the one that _reviews_ it**, and the authoring guidelines evolve themselves over time.

[View on GitHub »](https://github.com/alfadur7/llm-wiki-newsroom){: .btn }
[Read the FAQ »]({{ '/faq/' | relative_url }}){: .btn }

## See the output before installing

The example corpus shipped in the repo — the debate over what "open source" means for AI — is published as a browsable **[GitHub Wiki](https://github.com/alfadur7/llm-wiki-newsroom/wiki)**, so you can read the generated pages without cloning. The interactive knowledge graph below runs locally after you clone.

[![The interactive knowledge graph browser — every page a node, every wikilink an edge, auto-grouped into color-coded clusters]({{ '/knowledge-graph.png' | relative_url }})](https://github.com/alfadur7/llm-wiki-newsroom/wiki)

*The interactive graph (`graph/graph.html`) — every page a node, every wikilink an edge, color-coded by auto-detected cluster, with a live physics layout and filter/search built in. Shown on a larger private deployment (~2,300 nodes) to convey how it scales; this repo ships a deliberately small 15-node example corpus you browse the exact same way.*

## What makes it different

There are plenty of takes on [Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) idea now. After reading the popular implementations, three things here are genuinely rare:

- **Authoring guidelines that evolve themselves.** When the same review failure keeps recurring, the system drafts a fix to its _own_ writing rules and keeps it only if a blind A/B against a rotating regression set shows it actually helped. So it isn't only the wiki that improves over time, but the rules that build it. *(Still experimental — the author is measuring whether it earns its keep rather than claiming it's solved.)*
- **A full newsroom, not just "an agent."** The work is split across five roles — a **reporter** drafts source pages, a **columnist** writes the deep cross-source analysis, a **desk** editor reviews it with fresh eyes against an editorial rubric, a **copy editor** runs deterministic checks, and an **editor-in-chief** gates publication. The reviewer sees only the draft and the rubric, never the writer's reasoning — the real lever is context isolation, not instance count.
- **Memex-style associative discovery.** Saved reading trails and "unexpected connection" surfacing, inspired by [Vannevar Bush's Memex (1945)](https://en.wikipedia.org/wiki/Memex), that the other implementations don't carry.

The rest — the knowledge graph, contradiction tracking, cascading updates, plain-markdown/Obsidian output — many LLM-wiki tools have in some form. The self-evolving guidelines, the five-role newsroom with its rubric, and the Memex discovery are the bet.

## How it compares to RAG

|  | RAG | LLM Wiki Newsroom |
|---|---|---|
| Knowledge state | re-extracted per query | organized once, continuously updated |
| Retrieval unit | source chunk | structured wiki page |
| Cross-reference | none | wikilinks + backlink index |
| Contradiction handling | may surface at query time | flagged at ingest time + tracked |
| Accumulation effect | none | new sources enrich existing pages |
| Exploration | keyword search | graph traversal + associative trails |

## Highlights

- **Persistent, plain-markdown knowledge base** — your "second brain" as version-controlled `.md` files, not a vendor silo. Doubles as an [Obsidian](https://obsidian.md) vault.
- **Cascading updates** — ingesting one document refreshes ~10–15 related existing pages automatically.
- **Contradiction tracking** — conflicting claims between sources are flagged at ingest time, not query time.
- **Interactive knowledge graph** — every page a node, every link an edge, auto-clustered and browsable.
- **Associative discovery (Memex)** — follow connected concepts to surface unexpected relationships.
- **Local-first** — the Python tools (graph, lint, search) run entirely on your machine with no API keys; the agent itself runs on Claude Code.

## Quick start

```bash
git clone https://github.com/alfadur7/llm-wiki-newsroom.git
cd llm-wiki-newsroom
```

Or click **["Use this template"](https://github.com/alfadur7/llm-wiki-newsroom/generate)** to scaffold your own wiki repo. Then ingest your own sources with `/wiki-ingest`. Full setup, all nine slash commands, and the architecture are in the **[README](https://github.com/alfadur7/llm-wiki-newsroom#readme)**.

## Learn more

- **[Full README](https://github.com/alfadur7/llm-wiki-newsroom#readme)** — install, commands, architecture, feature reference
- **[FAQ]({{ '/faq/' | relative_url }})** — common questions answered
- **[Browsable example wiki](https://github.com/alfadur7/llm-wiki-newsroom/wiki)** — the shipped corpus, no clone needed
- **[Karpathy's original LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)** — the design inspiration

---

*MIT-licensed. A structured, local-first take on the LLM Wiki pattern — built and maintained in the open.*
