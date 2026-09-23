---
title: "Anthropic"
type: entity
kind: org
tags: [Anthropic, open-weights, ai-safety, policy]
sources: [anthropic-position-open-weights-models, open-weight-models-frontier-safety-gap, senators-question-meta-llama-leak, open-weights-american-ai-leadership]
last_updated: 2026-09-23
---

## Overview

Anthropic develops the Claude models. Its CEO, Dario Amodei, stated in a post dated 2026-07-27 that "Anthropic has never advocated for a ban on open-weights models." Amodei wrote it after reports that some US officials were weighing a ban on US companies using Chinese [[OpenWeights|open-weights]] models, and after, by his account, accusations that Anthropic wanted such a ban to protect its business. He calls open-weights models without dangerous capabilities a public good, yet argues that open weights potentially carry higher misuse risk than closed models because guardrails and monitoring are hard to apply and released weights cannot be withdrawn. In place of a ban he backs three measures: no powerful chips for China, a crackdown on industrial-scale distillation, and mandatory safety testing for all sufficiently capable models, open and closed. The post states only Anthropic's own position; it carries no external assessment.

TechCrunch groups Anthropic with OpenAI as frontier developers that rely on classifiers, refusal training, and API-level controls to limit dangerous cyber and biological assistance.

## Key Facts

- **Distillation enforcement** — Amodei says Anthropic identifies and bans accounts that use its models for industrial-scale distillation, but that such accounts are often identified only after substantial distillation has occurred and that no single company can solve the problem.
- **Safety research** — Amodei cites research from AE Studio and Anthropic on modular training strategies as a possible way to improve open-weights model safety.
- **Industry letter** — in the same post, Amodei responds to an industry letter the post does not name, whose points match the 2026-07-24 open letter "Open Weights and American AI Leadership." He agrees with it that open weights expand access and competition, but rejects its claims that open weights necessarily make safeguards easier or help defenders more than attackers.
- **Claude Opus 4.7 refusals** — SaferAI reports that Z.ai's GLM-5.2 is only a few months behind OpenAI's GPT-5.5 and Anthropic's Claude Opus 4.7 on cyber and biology capabilities, and that Opus 4.7 refused so consistently that SaferAI could not complete the CyberGym benchmark on it.
- **Opus 5 system card** — per TechCrunch, Anthropic states in the Opus 5 system card that the model can search for vulnerabilities in uncompiled source code but not in compiled software.
- **2023 model-size comparison** — in coverage of the Senate letter over [[Meta]]'s LLaMA leak, Stanford's Christopher Manning put the largest models from OpenAI, Anthropic, and Google at roughly 175 billion to 512 billion parameters, larger than LLaMA.

## Connections

- [[OpenWeights]] — the release model Anthropic says it has never sought to ban while arguing it carries higher misuse risk
- [[Meta]] — the developer of LLaMA, against whose largest model Manning compared Anthropic's
