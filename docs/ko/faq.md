---
layout: default
title: 자주 묻는 질문
permalink: /ko/faq/
lang: ko
description: >-
  LLM Wiki Newsroom 자주 묻는 질문. 무엇인지, RAG와 어떻게 다른지, API 키가 필요한지,
  어떤 에이전트를 지원하는지, 쓰는 쪽과 검수하는 쪽을 나눈 설계와 자기진화 지침이 어떻게
  동작하는지 다룹니다.
faq_schema: true
faq_data: faq_ko
schema_inlanguage: ko
hreflang_en: "https://alfadur7.github.io/llm-wiki-newsroom/faq/"
hreflang_ko: "https://alfadur7.github.io/llm-wiki-newsroom/ko/faq/"
---

*In [English]({{ '/faq/' | relative_url }}).*

# 자주 묻는 질문

**LLM Wiki Newsroom**에 대해 자주 묻는 질문입니다. [Claude Code](https://www.anthropic.com/claude-code)용 멀티에이전트 위키 프레임워크죠. 전체 그림은 **[README(영문)](https://github.com/alfadur7/llm-wiki-newsroom#readme)** 나 **[소개 페이지]({{ '/ko/' | relative_url }})** 를 보세요.

{% for item in site.data.faq_ko %}
## {{ item.q }}

{{ item.a }}
{% endfor %}

---

더 궁금한 점이 있으면 **[GitHub](https://github.com/alfadur7/llm-wiki-newsroom)** 에서 이슈나 디스커션을 남겨 주세요.
