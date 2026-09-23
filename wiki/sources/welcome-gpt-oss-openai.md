---
title: "Welcome GPT OSS, the New Open-Source Model Family from OpenAI"
type: source
tags: [OpenAI, open-weights, open-source-ai, licensing, fine-tuning, reasoning-models]
published: 2025-08-05
scraped: 2026-09-23
source_file: raw/NewsScrap/Welcome GPT OSS, the new open-source model family from OpenAI!.md
source_url: "https://huggingface.co/blog/welcome-openai-gpt-oss"
last_updated: 2026-09-23
---

## Summary

A Hugging Face blog post dated 2025-08-05 welcomes GPT OSS, which it calls "a hugely anticipated [[OpenWeights|open-weights]] release by OpenAI." The family has two mixture-of-experts reasoning models, gpt-oss-120b (117B parameters) and gpt-oss-20b (21B), both released under the Apache 2.0 license with a short usage policy. The post's headline calls the family "open-source," but its body describes only the released weights and never mentions training data or training code. Most of the post is an integration guide covering Hugging Face tooling, inference kernels, [[FineTuning|fine-tuning]], evaluation, and chat templates. In the page comments, several readers dispute the "open" label: one says the release will not "share the code for us to train our own," and another asks for "a new acronym for open source software." The post is a partner welcome, and no independent assessment of the release's openness is within this raw's scope.

## Key Claims

- [fact] [[HuggingFace]] — describes GPT OSS as an open-weights release by OpenAI designed for reasoning, agentic tasks, and developer use cases
- [fact] [[HuggingFace]] — reports that GPT OSS comprises gpt-oss-120b with 117B total parameters and gpt-oss-20b with 21B total parameters
- [fact] [[HuggingFace]] — reports that the 20B and 117B models have 3.6B and 5.1B active parameters respectively
- [fact] [[HuggingFace]] — states that both models are mixture-of-experts models whose MoE weights use the 4-bit MXFP4 quantization format
- [fact] [[HuggingFace]] — states that the 120B model fits on a single 80 GB GPU such as an H100
- [fact] [[HuggingFace]] — states that the 20B model runs within 16 GB of memory, including consumer GPUs such as the 3090, 4090, and 5080
- [fact] [[HuggingFace]] — states that the models are licensed under Apache 2.0 with a minimal complementary usage policy
- [fact] [[OpenAI]] — requires in its gpt-oss usage policy that users comply with all applicable law
- [analysis] [[OpenAI]] — presents the release as a meaningful step in its commitment to the open-source ecosystem, according to Hugging Face
- [fact] [[HuggingFace]] — describes the models as text-only reasoning models with chain-of-thought and adjustable reasoning-effort levels
- [fact] [[HuggingFace]] — reports that the models use the same tokenizer as GPT-4o and other OpenAI API models
- [fact] [[HuggingFace]] — states that the models support a 128K context through RoPE, alternating full-context and 128-token sliding-window attention layers
- [fact] [[HuggingFace]] — reports that GPT OSS is available through its Inference Providers service, the infrastructure behind OpenAI's official gpt-oss.com demo
- [fact] [[HuggingFace]] — states that the models are supported in transformers, vLLM, llama.cpp, and ollama from release
- [fact] [[HuggingFace]] — reports that GPT OSS has been verified on AMD Instinct hardware and that its kernels library adds initial ROCm support
- [fact] [[HuggingFace]] — states that GPT OSS models are fully integrated with the trl library for fine-tuning, with a LoRA example in the OpenAI cookbook
- [fact] [[HuggingFace]] — reports that the models are available on the Azure AI Model Catalog and the Dell Enterprise Hub
- [fact] [[HuggingFace]] — reports that the 20B model scores 69.5 (±1.9) on IFEval strict prompt and 63.3 (±8.9) on AIME25 pass@1 under its lighteval setup
- [analysis] [[HuggingFace]] — explains that the models were trained on multi-turn data in which all but the final chain of thought was dropped, so fine-tuning should mask all but the final assistant turn
- [forecast] [[HuggingFace]] — expects GPT OSS to be long-lived, inspiring, and impactful models
- [analysis] User8213 — argues in a page comment that the "open" model is sanitized and that OpenAI does not share the code needed to train one's own
- [fact] User8213 — reported in a follow-up comment on 2025-08-07 that an abliterated version of GPT-OSS 20B had been published
- [analysis] scaldingGazpacho — questions in a page comment whether the release should be called open source and calls for a new acronym for open source software
- [analysis] Zoey1 — notes in a page comment that many models do not open their data even when the model itself is open
- [fact] renaudrenaud — reported in a page comment running the 120B model at 16 tokens per second on a roughly 2000-euro computer drawing under 200W

## Key Quotes

> "We aim for our tools to be used safely, responsibly, and democratically, while maximizing your control over how you use them. By using gpt-oss, you agree to comply with all applicable law." — [[OpenAI]], gpt-oss usage policy

> "GPT OSS is a hugely anticipated open-weights release by OpenAI, designed for powerful reasoning, agentic tasks, and versatile developer use cases." — [[HuggingFace]] blog authors

> "We believe these will be long-lived, inspiring and impactful models." — [[HuggingFace]] blog authors

> "Won't even share the code for us to train our own. Thanks for nothing, \"Open\" AI." — User8213, Hugging Face commenter

> "We really need a new acronym for open source software." — scaldingGazpacho, Hugging Face commenter

## Connections

- references: [[OpenWeights]] — the post itself calls GPT OSS an open-weights release of two MoE models
- references: [[OpenSourceAI]] — the headline labels the family "open-source," and the body never addresses training data or code
- references: [[ModelLicensing]] — the weights ship under Apache 2.0 with a short complementary usage policy
- references: [[FineTuning]] — the post documents trl-based fine-tuning and chain-of-thought masking for the models
- references: [[OpenWashing]] — commenters dispute the "open" label and mock the name "Open" AI
- references: [[TrainingData]] — a commenter notes that the model is open while its data stays closed
- cites: [[HuggingFace]] — the post's publisher; source of the model specs, licensing, integration, and evaluation claims
- cites: [[OpenAI]] — the releasing company; its usage policy is quoted and its "open" label is disputed in the comments

