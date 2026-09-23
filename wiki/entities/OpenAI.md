---
title: "OpenAI"
type: entity
kind: org
tags: [OpenAI, open-weights, open-source-ai, ai-safety, licensing]
sources: [welcome-gpt-oss-openai, open-source-ai-uniquely-dangerous, open-future-osaid-step-forward, osaid-take-it-or-leave-it, rethinking-open-source-generative-ai, senators-question-meta-llama-leak, open-weights-american-ai-leadership, open-weight-models-frontier-safety-gap, deepseek-r1-release]
last_updated: 2026-09-23
---

## Overview

OpenAI is the developer of the GPT model line. On 2025-08-05 a Hugging Face blog post welcomed its GPT OSS family as "a hugely anticipated open-weights release": two mixture-of-experts reasoning models, gpt-oss-120b (117B total parameters) and gpt-oss-20b (21B), shipped under the Apache 2.0 license with a short usage policy. The post's headline calls the family "open-source," while commenters on the page dispute the label, one writing that OpenAI "won't even share the code for us to train our own." The post is a partner welcome with no independent assessment of the release's openness.

OpenAI's own voice in the corpus is thin and mostly relayed by others. Its gpt-oss usage policy states, "By using gpt-oss, you agree to comply with all applicable law." Hugging Face reports that OpenAI presents the release as a meaningful step in its commitment to the open-source ecosystem. VentureBeat reports CEO Sam Altman's 2023 Senate testimony, and OpenAI co-signs a 2026 open letter on open weights. Otherwise OpenAI appears as a reference point in the [[OpenWeights|open-weights]] debate rather than as a speaker.

Two sources describe an earlier retreat from openness. IEEE Spectrum guest author David Evan Harris presents it as a safety decision: OpenAI's leaders decided in 2019 that releasing its GPT systems' source code and model weights was too dangerous to continue, a course he sets against [[Meta]]'s opposite one. Alek Tarkowski and Paul Keller of Open Future instead criticize it, saying OpenAI first committed to openness and then moved toward increasing closure. Separately, Yaniv Benhamou and Michel Reymond report that open source experts have criticized self-certified "open" releases by Meta and OpenAI as [[OpenWashing|open-washing]].

## Key Facts

- **Closed reference point** — Andreas Liesenfeld and Mark Dingemanse's peer-reviewed 2024 openness survey uses OpenAI's ChatGPT and DALL-E as closed reference points, and judges DALL-E completely closed.
- **2023 Senate context** — VentureBeat's Sharon Goldman reports that OpenAI CEO Sam Altman testified before the Senate Subcommittee on Privacy, Technology & the Law three weeks before its letter on Meta's LLaMA leak, agreeing with calls for a new AI regulatory agency; William Falcon of Lightning AI said the letter "almost feels like OpenAI and Congress are working together now," and Steven Weber argued that Microsoft, operating through OpenAI, is "running scared" of open-source AI. The article quotes no one who supports the letter.
- **2026 open-weights letter** — OpenAI appears in the published signatory list of a 2026-07-24 open letter, hosted on a Microsoft page, that asks policymakers not to prohibit open weights or restrict distillation.
- **Benchmark comparisons** — [[DeepSeek]] claims its R1 model performs on par with OpenAI-o1 on math, code, and reasoning tasks; a SaferAI evaluation reported by TechCrunch places Z.ai's open-weight GLM-5.2 only a few months behind OpenAI's GPT-5.5 on cyber and biology capabilities. TechCrunch reports that frontier developers such as OpenAI rely on classifiers, refusal training, and API-level controls to limit dangerous assistance.
- **GPT OSS details** — per Hugging Face, the models use the same tokenizer as GPT-4o, support a 128K context, and integrate with the trl library for [[FineTuning|fine-tuning]]; the post never mentions [[TrainingData|training data]] or training code.

## Connections
- [[OpenWeights]] — GPT OSS is described as an open-weights release; OpenAI signs the 2026 open-weights letter
- [[OpenSourceAI]] — the "open-source" headline for GPT OSS is disputed by commenters
- [[OpenWashing]] — critics name OpenAI's self-certified "open" releases as open-washing
- [[ModelLicensing]] — GPT OSS ships under Apache 2.0 with a complementary usage policy
- [[FineTuning]] — GPT OSS fine-tuning support through trl
- [[TrainingData]] — the component the GPT OSS post never addresses
- [[Meta]] — named alongside OpenAI in the open-washing critique; the 2023 Senate letter targeted Meta's LLaMA
- [[DeepSeek]] — benchmarks DeepSeek-R1 against OpenAI-o1
