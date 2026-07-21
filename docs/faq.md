---
layout: default
title: FAQ
permalink: /faq/
description: >-
  Frequently asked questions about LLM Wiki Newsroom.
faq_schema: true
faq_data: faq
schema_inlanguage: en
hreflang_en: "https://alfadur7.github.io/llm-wiki-newsroom/faq/"
hreflang_ko: "https://alfadur7.github.io/llm-wiki-newsroom/ko/faq/"
---

*Read this in [한국어]({{ '/ko/faq/' | relative_url }}).*

# Frequently asked questions

Common questions about **LLM Wiki Newsroom** — the multi-agent wiki framework for [Claude Code](https://www.anthropic.com/claude-code). For the full picture, see the **[README](https://github.com/alfadur7/llm-wiki-newsroom#readme)** or the **[overview]({{ '/' | relative_url }})**.

{% for item in site.data.faq %}
## {{ item.q }}

{{ item.a }}
{% endfor %}

---

Still curious? Open an issue or a discussion on **[GitHub](https://github.com/alfadur7/llm-wiki-newsroom)**.
