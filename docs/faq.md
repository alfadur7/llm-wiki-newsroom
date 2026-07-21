---
layout: default
title: FAQ
permalink: /faq/
description: >-
  Frequently asked questions about LLM Wiki Newsroom — what it is, how it differs
  from RAG, whether it needs API keys, which agents it supports, and how the
  writer-reviewer split and self-evolving guidelines work.
faq_schema: true
---

# Frequently asked questions

Common questions about **LLM Wiki Newsroom** — the multi-agent wiki framework for [Claude Code](https://www.anthropic.com/claude-code). For the full picture, see the **[README](https://github.com/alfadur7/llm-wiki-newsroom#readme)** or the **[overview]({{ '/' | relative_url }})**.

{% for item in site.data.faq %}
## {{ item.q }}

{{ item.a }}
{% endfor %}

---

Still curious? Open an issue or a discussion on **[GitHub](https://github.com/alfadur7/llm-wiki-newsroom)**.
