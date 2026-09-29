---
title: "Mistral Small 3"
type: source
tags: [Mistral AI, licensing, open-weights, open-source-ai]
published: 2025-01-30
scraped: 2026-09-27
source_file: raw/NewsScrap/Mistral Small 3 Mistral AI.md
source_url: "https://mistral.ai/news/mistral-small-3/"
last_updated: 2026-09-27
---

## Summary

In this January 30, 2025 blog post, the [[MistralAI|Mistral AI]] team introduces Mistral Small 3, a 24B-parameter model tuned for low latency. The company releases both a pretrained and an instruction-tuned checkpoint under the Apache 2.0 license and says the weights are free to download, modify, and use in any capacity. It also says it is renewing its commitment to Apache 2.0 for its general-purpose models as it progressively moves away from models under the MRL license. The benchmark and speed figures are the company's own, measured through its internal evaluation pipeline and a vendor-run human evaluation. The post does not say whether the training data will be released, and external assessment is outside the raw's scope.

## Key Claims

- [fact] [[MistralAI]] — introduced Mistral Small 3, a latency-optimized 24B-parameter model, in a blog post dated January 30, 2025
- [fact] [[MistralAI]] — released both a pretrained and an instruction-tuned checkpoint of Mistral Small 3 under the Apache 2.0 license [[mistral-small-3#Key Quotes|self]]
- [fact] [[MistralAI]] — reports that Mistral Small 3 scores over 81% accuracy on MMLU and runs at 150 tokens per second
- [analysis] [[MistralAI]] — claims that Mistral Small 3 is on par with the Llama 3.3 70B instruct model from [[Meta]] while running more than 3x faster on the same hardware
- [analysis] [[MistralAI]] — presents Mistral Small 3 as an open replacement for opaque proprietary models such as GPT4o-mini from [[OpenAI]] [[mistral-small-3#Key Quotes|self]]
- [fact] [[MistralAI]] — states that Mistral Small 3 was trained with neither reinforcement learning nor synthetic data
- [analysis] [[MistralAI]] — describes [[DeepSeek]] R1 as "a great and complementary piece of open-source technology" and positions Mistral Small 3 as a base model for building reasoning capabilities [[mistral-small-3#Key Quotes|self]]
- [fact] [[MistralAI]] — says it ran side-by-side human evaluations with an external third-party vendor on over 1,000 proprietary coding and generalist prompts
- [fact] [[MistralAI]] — says that, when quantized, Mistral Small 3 can run privately on a single RTX 4090 or a MacBook with 32GB of RAM
- [analysis] [[MistralAI]] — says Mistral Small 3 can be [[FineTuning|fine-tuned]] into subject-matter experts for fields such as legal advice, medical diagnostics, and technical support
- [fact] [[MistralAI]] — made Mistral Small 3 available on [[HuggingFace|Hugging Face]], Ollama, Kaggle, Together AI, Fireworks AI, and IBM Watson X on the day of the announcement
- [fact] [[MistralAI]] — renews its commitment to the Apache 2.0 license for its general-purpose models as it progressively moves away from MRL-licensed models [[mistral-small-3#Key Quotes|self]]
- [analysis] [[MistralAI]] — says enterprises needing specialized capabilities can rely on additional commercial models that complement its community releases
- [forecast] [[MistralAI]] — expects to release small and large Mistral models with boosted reasoning capabilities in the coming weeks

## Key Quotes

> "Today we're introducing Mistral Small 3, a latency-optimized 24B-parameter model released under the Apache 2.0 license." — [[MistralAI]] team

> "Mistral Small 3 is competitive with larger models such as Llama 3.3 70B or Qwen 32B, and is an excellent open replacement for opaque proprietary models like GPT4o-mini." — [[MistralAI]] team

> "Note that Mistral Small 3 is neither trained with RL nor synthetic data, so is earlier in the model production pipeline than models like Deepseek R1 (a great and complementary piece of open-source technology!)." — [[MistralAI]] team

> "We're renewing our commitment to using Apache 2.0 license for our general purpose models, as we progressively move away from MRL-licensed models. As with Mistral Small 3, model weights will be available to download and deploy locally, and free to modify and use in any capacity." — [[MistralAI]] team

## Connections

- cites: [[MistralAI]] — the announcing company; source of the model, benchmark, license, and availability claims
- references: [[ModelLicensing]] — Apache 2.0 checkpoints and a stated move away from MRL-licensed models for general-purpose releases
- references: [[OpenWeights]] — the weights are downloadable and free to modify, while training-data release goes unmentioned
- references: [[OpenSourceAI]] — the post frames the release and DeepSeek R1 as open-source technology for the community
- references: [[FineTuning]] — fine-tuning into domain subject-matter experts is named as a use case
- references: [[DeepSeek]] — R1 is cited as complementary open-source reasoning technology
- references: [[Meta]] — Llama 3.3 70B is the main benchmark comparison
- references: [[OpenAI]] — GPT4o-mini is named as the proprietary model Small 3 can replace
- references: [[HuggingFace]] — one of the launch distribution platforms
