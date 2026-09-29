---
title: "Meta Returns to Open Source with Muse Glimmer, an Apache 2.0 Licensed 30B Parameter LLM"
type: source
tags: [Meta, open-weights, licensing, open-source-ai, distillation, local-inference]
published: 2026-08-10
scraped: 2026-09-27
source_file: raw/NewsScrap/Meta returns to open source with Muse Glimmer, an Apache 2.0 licensed 30B parame.md
source_url: "https://venturebeat.com/technology/meta-returns-to-open-source-with-muse-glimmer-an-apache-2-0-licensed-30b-parameter-ai-model-optimized-for-agents-available-now"
last_updated: 2026-09-27
---

## Summary

VentureBeat's Carl Franzen reports that on 2026-08-10 [[Meta]] released Muse Glimmer, a 30-billion-parameter dense model for running AI agents on consumer hardware, under the Apache 2.0 license. Franzen calls it Meta's first fully open release since the proprietary Muse Spark succeeded the [[OpenWeights|open-weight]] Llama family in April 2026, and a more permissive grant than Llama's community license ever was. Meta [[Distillation|distilled]] Glimmer from Muse Spark, ships 4-bit quantized variants and a speculative-decoding drafter under the same license, and publishes the weights on [[HuggingFace|Hugging Face]], while [[MarkZuckerberg|Mark Zuckerberg]] promises to open the weights of Muse Spark 1.2 as well. Franzen notes that, as with most "open source" model releases, only the weights are open: Meta has not released the [[TrainingData|training data]] or training code. The benchmark, quantization and safety figures are Meta's own measurements, and independent assessment of them is outside this raw's scope.

## Key Claims

- [fact] [[Meta]] — released Muse Glimmer, a 30-billion-parameter open-weight model designed to run autonomous AI agents on consumer hardware, on 2026-08-10
- [fact] [[Meta]] — licenses Muse Glimmer under Apache 2.0, which permits unrestricted commercial use, modification and redistribution
- [analysis] Carl Franzen — calls Glimmer Meta's first fully open release since the proprietary Muse Spark succeeded the open-weight Llama family in April 2026
- [analysis] Carl Franzen — writes that Glimmer launches with a more permissive license than Llama ever carried, whose community license drew years of criticism for its 700-million-monthly-user cutoff
- [fact] [[MarkZuckerberg|Mark Zuckerberg]] — wrote on X that Meta will soon release the weights of Muse Spark 1.2, its latest foundation model
- [analysis] Carl Franzen — states that until the Glimmer release the entire Muse family was proprietary, and that Muse Spark 1.2 is the frontier model behind the Muse Code terminal coding agent
- [fact] [[Meta]] — publishes the Glimmer weights on Hugging Face, with support rolling out through Ollama, LM Studio, vLLM, SGLang, Together AI, Fireworks AI and OpenRouter
- [fact] [[Meta]] — reports working with AMD, Arm, Dell, Intel and Nvidia to optimize Glimmer's performance across devices
- [fact] [[Meta]] — describes Glimmer in its model card as a dense causal transformer of about 29.6 billion parameters across 52 layers, including a ~1.8B-parameter ViT-G/14 perception encoder
- [fact] [[Meta]] — states in its model card that Glimmer accepts interleaved text and images, supports more than 100 languages, and has a context length of 131,072 tokens or more
- [fact] [[Meta]] — pre-trained Glimmer on Muse Spark's outputs using logit distillation, according to its technical blog post
- [fact] [[Meta]] — post-trained Glimmer with supervised fine-tuning, on-policy distillation and reinforcement learning across general, reasoning, coding and agentic domains
- [fact] Alexandr Wang — wrote on X that Glimmer can run on 24GB of VRAM without losing agentic reliability
- [fact] [[Meta]] — states that the full-precision 30B model requires more than 55GB of memory, beyond any single consumer GPU
- [fact] [[Meta]] — developed approximately 4-bit quantized versions that shrink the language-model weights to under 20GB, fitting the full agent stack within 24GB or 32GB
- [fact] [[Meta]] — reports average accuracy degradation of 0.2% across 15 benchmarks for its 32GB K-Quant-Dynamic version and 1% for its 24GB K-Quant-17GB version
- [fact] [[Meta]] — reports that DFlash speculative decoding raises average generation speed on an Nvidia RTX 5090 from 74.9 to 233.4 tokens per second, a 3.1x increase
- [fact] [[Meta]] — reports that DFlash raises Apple M5 Max speed from 26.6 to 50.2 tokens per second and M4 Max speed from 23.7 to 37.8
- [fact] [[Meta]] — scores Glimmer at 51.2 on SWE-Bench Pro in its own evaluation, against 36.9 for Gemma4-31B and 50.2 for Qwen3.6-27B
- [fact] [[Meta]] — scores Glimmer below Qwen3.6-27B in its own comparison on OSWorld-Verified (65.9 vs. 75.6) and TerminalBench 2.1 (51.7 vs. 60.7)
- [analysis] Carl Franzen — judges that the benchmark numbers make Glimmer more interesting as a specialized local-agent model than as evidence of a universal performance lead
- [fact] [[Meta]] — reports a 28.4% prompt-injection attack-success rate for Glimmer on Siren AgentDojo, against 25.6% for Gemma and 40.3% for Qwen
- [fact] [[Meta]] — determined under its Advanced AI Scaling Framework that Glimmer does not meet the framework's definition of "Frontier AI" because it is generally less capable than Muse Spark
- [fact] [[Meta]] — assessed Glimmer at Moderate or lower risk across chemical/biological, cyber and loss-of-control categories through its Preparedness Team
- [fact] [[Meta]] — recommends deploying Glimmer within a broader system with guardrails, including human-in-the-loop confirmation for irreversible actions
- [fact] [[Meta]] — releases the full-precision BF16 weights, both 4-bit quantized variants, the DFlash drafter and the perception encoder under Apache 2.0
- [analysis] Carl Franzen — points out that, as with most "open source" model releases, only the weights are open, since Meta has not released the training data or training code
- [analysis] Carl Franzen — reports that by May 2026 Chinese open-weight models accounted for roughly 61% of all tokens consumed on OpenRouter, while Meta's Llama fell off the rankings
- [analysis] Carl Franzen — lists OpenAI's Apache 2.0 gpt-oss models, Google's Gemma family and Thinking Machines' Inkling as the few U.S. counterexamples to Chinese-led open releases
- [analysis] Carl Franzen — writes that Google's Gemma family is open-weight but ships under Google's own more restrictive custom license rather than an OSI-approved one
- [analysis] Carl Franzen — contrasts Glimmer, a dense model with native vision input, with OpenAI's gpt-oss models, which are text-only sparse mixture-of-experts designs
- [forecast] Carl Franzen — expects that opening Muse Spark 1.2's weights would put a U.S. flagship frontier model into open circulation, something no American lab has done at that tier

## Key Quotes

> "Today we're also opening the weights for Muse Glimmer, a great 30B parameter dense model that can run locally." — [[MarkZuckerberg|Mark Zuckerberg]], Meta co-founder and CEO

> "Soon we'll also release the weights for Muse Spark 1.2, our latest foundation model. Meta is a strong supporter of open source and I'm proud of these releases." — [[MarkZuckerberg|Mark Zuckerberg]], Meta co-founder and CEO

> "Just like much larger models, muse glimmer can operate as a fully capable agent via planning, tool calls, checking its own results, and failure recovery." — Alexandr Wang, Meta chief AI officer

> "can run on 24GB of VRAM without losing agentic reliability." — Alexandr Wang, Meta chief AI officer

## Connections

- cites: [[Meta]] — the releasing company; source of the model card specs, quantization and speed figures, benchmark and safety results, and Zuckerberg's open-weights pledge
- cites: [[MarkZuckerberg]] — quotes his X posts opening Glimmer's weights, promising Muse Spark 1.2's, and calling Meta "a strong supporter of open source"
- references: [[OpenWeights]] — Glimmer ships full weights, quantizations and drafter while training data and code stay private
- references: [[ModelLicensing]] — Apache 2.0 grant set against Llama's community license and its 700-million-user cutoff
- references: [[OpenSourceAI]] — the release is headlined as open source, while the body notes that only the weights are open
- references: [[TrainingData]] — Meta has not released Glimmer's training data or training code
- references: [[Distillation]] — Glimmer was pre-trained on Muse Spark's outputs through logit distillation
- references: [[AISafety]] — Meta's own prompt-injection, privacy and Preparedness results, and its guardrail recommendation
- references: [[HuggingFace]] — the venue where Glimmer's weights are published
- references: [[OpenAI]] — gpt-oss is the closest comparison, both Apache 2.0 and aimed at self-hosted deployment
- references: [[welcome-gpt-oss-openai|Welcome GPT OSS]] — the earlier Apache 2.0 open-weights release the article compares Glimmer against
