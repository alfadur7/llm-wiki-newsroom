---
title: "DeepSeek-R1 Release"
type: source
tags: [DeepSeek, open-weights, open-source-ai, licensing, fine-tuning, distillation]
published:
scraped: 2026-09-23
source_file: raw/NewsScrap/DeepSeek-R1 Release.md
source_url: "https://www.deepseek.com/en/news/deepseek-r1/"
last_updated: 2026-09-23
---

## Summary

In its own release announcement, [[DeepSeek]] presents DeepSeek-R1 as a "fully open-source" reasoning model whose code and weights are released under the MIT License, and claims performance on par with OpenAI-o1 on math, code, and reasoning tasks. The announcement also releases six smaller models distilled from R1 and states that R1's API outputs may now be used for [[FineTuning|fine-tuning]] and distillation. It lists API pricing and credits large-scale reinforcement learning in post-training for the performance gains. The page is a vendor announcement: it does not say whether the training data is released, and external assessment of its "open-source" label — the wiki's [[open-source-ai-models-how-open|Hunton primer]] classifies R1 as [[OpenWeights|open weights]] — is outside this raw's scope.

## Key Claims

- [fact] [[DeepSeek]] — announced that DeepSeek-R1's code and models are released under the MIT License, permitting free distillation and commercialization
- [fact] [[DeepSeek]] — describes DeepSeek-R1 as a "fully open-source model" accompanied by a technical report
- [fact] [[DeepSeek]] — announced a license update making DeepSeek-R1 MIT licensed so the community can leverage its model weights and outputs
- [fact] [[DeepSeek]] — announced that DeepSeek-R1 API outputs can now be used for fine-tuning and distillation
- [fact] [[DeepSeek]] — released 6 small models distilled from DeepSeek-R1 as fully open-sourced models
- [analysis] [[DeepSeek]] — claims DeepSeek-R1 performs on par with OpenAI-o1 on math, code, and reasoning tasks
- [analysis] [[DeepSeek]] — claims its distilled 32B and 70B models perform on par with OpenAI-o1-mini
- [analysis] [[DeepSeek]] — attributes R1's performance boost to large-scale reinforcement learning in post-training that needed minimal labeled data
- [fact] [[DeepSeek]] — prices DeepSeek-R1 API access at $0.14 per million input tokens on a cache hit, $0.55 per million input tokens on a cache miss, and $2.19 per million output tokens
- [fact] [[DeepSeek]] — made DeepSeek-R1 available on its website and through its API under the model name `deepseek-reasoner`

## Key Quotes

> "Code and models are released under the MIT License: Distill & commercialize freely!" — [[DeepSeek]]

> "DeepSeek-R1 is now MIT licensed for clear open access" — [[DeepSeek]]

> "API outputs can now be used for fine-tuning & distillation" — [[DeepSeek]]

## Connections

- cites: [[DeepSeek]] — the announcing company; source of the MIT-license, distillation, benchmark, and pricing claims
- references: [[ModelLicensing]] — R1's code and weights move to the permissive MIT License
- references: [[OpenSourceAI]] — DeepSeek applies the "fully open-source" label to R1 without addressing training data
- references: [[OpenWeights]] — the announcement opens R1's model weights and outputs to the community
- references: [[FineTuning]] — R1's API outputs are licensed for fine-tuning and distillation
- references: [[open-source-ai-models-how-open|Open Source AI Models: How Open Are They Really?]] — the third-party primer that classifies the same R1 release as open weights
- references: [[OpenAI]] — the benchmark comparison target: R1 is claimed on par with OpenAI-o1, the distilled 32B and 70B models with o1-mini
- references: [[Distillation]] — releases six models distilled from R1 and licenses R1's API outputs for distillation

