---
layout: default
title: LLM Wiki Newsroom
description: >-
  A multi-agent "newsroom" on Claude Code that turns your documents into a
  cross-linked markdown wiki.
software_schema: true
schema_inlanguage: en
schema_url: "https://alfadur7.github.io/llm-wiki-newsroom/"
schema_description: >-
  Harness engineering applied to knowledge production: a self-evolving
  multi-agent "newsroom" on Claude Code that turns your documents into a
  cross-linked, human-readable markdown wiki, where the agent that writes a page
  is never the one that reviews it. Four loops hold it together, including a
  reground loop that pulls published pages back in before they go stale.
  Local-first, plain markdown and git, a structured alternative to RAG.
schema_keywords: "LLM wiki, Karpathy LLM Wiki, RAG alternative, harness engineering, knowledge factory, software factory, four loops, reground loop, inner loop, outer loop, meta loop, multi-agent, AI agents, agentic AI, Claude Code, Claude skills, knowledge base, knowledge graph, second brain, personal knowledge management, PKM, digital garden, Obsidian, semantic search, Memex, contradiction tracking, self-evolving guidelines, writer reviewer separation, context isolation, local-first"
hreflang_en: "https://alfadur7.github.io/llm-wiki-newsroom/"
hreflang_ko: "https://alfadur7.github.io/llm-wiki-newsroom/ko/"
---

*Read this in [한국어]({{ '/ko/' | relative_url }}).*

**LLM Wiki Newsroom is an open-source framework that turns a folder of documents into a cross-linked, human-readable markdown wiki, maintained by an AI agent organized as a five-role newsroom.** Drop articles, notes, and PDFs into a folder, run one command, and the agent — powered by [Claude Code](https://www.anthropic.com/claude-code) — reads them, extracts entities, concepts, and relationships, and organizes everything into interlinked pages. It's a persistent, structured alternative to RAG. Unlike most takes on the idea, **the agent that _writes_ a page is never the one that _reviews_ it**, and the authoring guidelines evolve themselves over time. It's [harness engineering]({{ '/knowledge-factory/' | relative_url }}) applied to knowledge production rather than code — with one more loop than the coding version needs, because a wiki page goes stale on its own.

[View on GitHub »](https://github.com/alfadur7/llm-wiki-newsroom){: .btn }
[Read the FAQ »]({{ '/faq/' | relative_url }}){: .btn }

## See the output before installing

The example corpus shipped in the repo — the debate over what "open source" means for AI — is published as a browsable **[GitHub Wiki](https://github.com/alfadur7/llm-wiki-newsroom/wiki)**, so you can read the generated pages without cloning. The interactive knowledge graph below runs locally after you clone.

[![The interactive knowledge graph browser — every page a node, every wikilink an edge, auto-grouped into color-coded clusters]({{ '/knowledge-graph.png' | relative_url }})](https://github.com/alfadur7/llm-wiki-newsroom/wiki)

*The interactive graph (`graph/graph.html`) — every page a node, every wikilink an edge, color-coded by auto-detected cluster, with a live physics layout and filter/search built in. Shown on a larger private deployment (~2,300 nodes) to convey how it scales; this repo ships a deliberately small 15-node example corpus you browse the exact same way.*

## What makes it different

It keeps the three-layer shape of [Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — `raw/` for untouched sources, `wiki/` for the pages the agent maintains, and a schema layer holding the operating rules — plus the same three operations: ingest, query, and lint. There are plenty of takes on that idea now; after reading the popular implementations, four things here are genuinely rare:

- **Authoring guidelines that evolve themselves.** When the same review failure keeps recurring, the system drafts a fix to its _own_ writing rules and keeps it only if a blind A/B against a rotating regression set shows it actually helped. So it isn't only the wiki that improves over time, but the rules that build it. *(Still experimental — the author is measuring whether it earns its keep rather than claiming it's solved.)*
- **A full newsroom, not just "an agent."** The work is split across five roles — a **reporter** drafts source pages, a **columnist** writes the deep cross-source analysis, a **desk** editor re-reads it for bias, argument quality, and narrative flow, a **copy editor** runs deterministic checks, and an **editor-in-chief** routes work and gates publication. Not every seat is a model passing judgment: the desk holds the only independent LLM verdict, the copy editor is a Python script, and the rest is writing work or orchestration. The reviewer sees only the draft and the rubric, never the writer's reasoning — the real lever is context isolation, not instance count.
- **Memex-style associative discovery.** Saved reading trails and "unexpected connection" surfacing, inspired by [Vannevar Bush's Memex (1945)](https://en.wikipedia.org/wiki/Memex), that the other implementations don't carry.
- **A loop for knowledge going stale.** Shipped code stays correct until the spec changes; a wiki page goes wrong on its own as the world moves on. So published pages come back around as input — when their sources change, when a claim's own deadline matures, or when two pages start contradicting each other. The three loops an AI-coding harness runs on don't cover that, which is why there's a fourth here. *(The full argument is in **[The Knowledge Factory]({{ '/knowledge-factory/' | relative_url }})**.)*

Nothing reaches the wiki until it clears both gates:

| Gate | Who | What it checks | How |
|---|---|---|---|
| 1 | copy editor | links, citations, structure | deterministic — `tools/lint.py`, a Python script, not a model |
| 2 | desk | bias, argument quality, narrative flow | qualitative — a fresh-context review against an editorial rubric |

Machine-checkable things are checked by machine; only what needs judgment costs a model call.

The rest — the knowledge graph, contradiction tracking, cascading updates, plain-markdown/Obsidian output — many LLM-wiki tools have in some form. The self-evolving guidelines, the five-role newsroom with its rubric, the Memex discovery, and the reground loop are the bet.

## How it compares to RAG

|  | RAG | LLM Wiki Newsroom |
|---|---|---|
| Knowledge state | re-extracted per query | organized once, continuously updated |
| Retrieval unit | source chunk | structured wiki page |
| Cross-reference | none | wikilinks + backlink index |
| Contradiction handling | may surface at query time | flagged at ingest time + tracked |
| Accumulation effect | none | new sources enrich existing pages |
| Exploration | keyword search | graph traversal + associative trails |

To be precise, this doesn't do away with retrieval. Karpathy framed the wiki as a compile step for knowledge, not as a replacement for search, and the optional local search used here is itself a BM25 + vector hybrid. What changes is *what* gets retrieved: a few already-structured, cross-referenced pages instead of raw chunks reassembled from scratch on every query.

## Highlights

- **Persistent, plain-markdown knowledge base** — your "second brain" as version-controlled `.md` files, not a vendor silo. Doubles as an [Obsidian](https://obsidian.md) vault.
- **Cascading updates** — ingesting one document refreshes ~10–15 related existing pages automatically.
- **Contradiction tracking** — conflicting claims between sources are flagged at ingest time, not query time.
- **Interactive knowledge graph** — every page a node, every link an edge, auto-clustered and browsable.
- **Associative discovery (Memex)** — follow connected concepts to surface unexpected relationships.
- **Local-first** — the Python tools (graph, lint, search) run entirely on your machine with no API keys; the agent itself runs on Claude Code.

## When the split earns its cost

A separate reviewer costs more tokens and more wall-clock than letting one agent grade its own draft. That trade isn't always worth it:

- **One agent is enough** when the output is quick and disposable, and a mistake costs nothing to throw away — a scratch summary, a one-off answer. Self-critique in the same context will do.
- **Separate the writer from the reviewer** when the output is published, accumulates, and gets built on later — where a plausible-but-wrong page quietly hardens into the thing everything else cites.

A wiki is the second case by construction: today's page is tomorrow's input, so an error doesn't stay one error. That's the bet here, and why this spends the extra tokens.

## Where it stands

- **New.** The repository went public on 2026-06-26. Treat it as the idea plus a small reproducible example, not a battle-tested product.
- **The shipped corpus is deliberately small** — 15 pages on the open-source-AI debate. The graph screenshot above comes from a larger private instance (~2,300 nodes), shown for scale; that one you can't verify from the repo.
- **The differentiators are hypotheses.** Writer–reviewer separation and the self-evolving loop are argued from design, not from published A/B numbers. They're being measured, not claimed as settled.
- **"No API keys" covers the tooling, not the agent.** Build, lint, and search are local Python; the reading and writing happen through your own Claude Code access.
- **Korean mode localizes prose, not schema.** `WIKI_LANG=ko` translates body text and field values; the frontmatter keys and section headers the tools parse stay English, and the shipped example corpus is English throughout.

## Quick start

```bash
git clone https://github.com/alfadur7/llm-wiki-newsroom.git
cd llm-wiki-newsroom
```

Or click **["Use this template"](https://github.com/alfadur7/llm-wiki-newsroom/generate)** to scaffold your own wiki repo. Then ingest your own sources with `/wiki-ingest`. Full setup, all nine slash commands, and the architecture are in the **[README](https://github.com/alfadur7/llm-wiki-newsroom#readme)**.

## Learn more

- **[Full README](https://github.com/alfadur7/llm-wiki-newsroom#readme)** — install, commands, architecture, feature reference
- **[FAQ]({{ '/faq/' | relative_url }})** — common questions answered
- **[The Knowledge Factory]({{ '/knowledge-factory/' | relative_url }})** — the four-loop production system behind the newsroom, from the concept down to the implementation
- **[Browsable example wiki](https://github.com/alfadur7/llm-wiki-newsroom/wiki)** — the shipped corpus, no clone needed
- **[Karpathy's original LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)** — the design inspiration

---

*MIT-licensed. A structured, local-first take on the LLM Wiki pattern — built and maintained in the open.*
