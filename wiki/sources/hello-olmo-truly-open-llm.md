---
title: "Hello OLMo: A Truly Open LLM"
type: source
tags: [open-source-ai, training-data, open-weights]
published: 2024-02-01
scraped: 2026-09-23
source_file: raw/NewsScrap/Hello OLMo A truly open LLM Ai2.md
source_url: "https://allenai.org/blog/hello-olmo-a-truly-open-llm-43f7e7359222"
last_updated: 2026-09-23
---

## Summary

In this 2024-02-01 announcement, the Allen Institute for AI (Ai2) released OLMo 7B. Ai2 calls it a "truly open" large language model because it ships with its pretraining data, training code, model weights, and evaluation suite, not just the weights. Ai2 presents the full release of [[TrainingData]] and training code as what separates OLMo from the [[OpenWeights]] releases it describes as having "limited transparency." Its research leads and compute partners (AMD, CSC, Databricks), along with executives at Meta and Microsoft, are quoted endorsing the release. The page is Ai2's own announcement, and no external assessment of its "truly open" claim is within the raw's scope.

## Key Claims

- [fact] Ai2 — released OLMo 7B alongside its pretraining data and training code on 2024-02-01, making it available on Hugging Face and GitHub
- [fact] Ai2 — built OLMo on its Dolma corpus, a three-trillion-token open pretraining dataset released together with the code that produces the data
- [fact] Ai2 — released full model weights for four OLMo variants at the 7B scale, each trained to at least 2T tokens, with inference code, training metrics, and training logs
- [fact] Ai2 — released its evaluation suite with 500+ checkpoints per model, taken every 1000 training steps, plus evaluation code under the Catwalk project
- [fact] Ai2 — credited a collaboration with Harvard's Kempner Institute and partners AMD, CSC (LUMI supercomputer), the University of Washington's Allen School, and Databricks
- [forecast] Ai2 — says it will add different model sizes, modalities, datasets, and capabilities to the OLMo family in the coming months
- [analysis] Ai2 — argues that opening the full training and evaluation ecosystem reduces developmental redundancy, which it calls critical to decarbonizing AI, citing a single training run as equivalent to the annual emissions of nine US homes
- [analysis] Ai2 — argues that keeping models and datasets in the open rather than behind APIs lets researchers build on previous models and work
- [analysis] Hanna Hajishirzi — argues that without access to [[TrainingData]] researchers cannot scientifically understand how a model works [[hello-olmo-truly-open-llm#Key Quotes|Key Quotes]]
- [analysis] Noah Smith — states that with OLMo "open" covers all aspects of model creation, including training code, evaluation methods, and data, which is the fuller reading of [[OpenSourceAI]] [[hello-olmo-truly-open-llm#Key Quotes|Key Quotes]]
- [analysis] Noah Smith — says AI work moved behind closed doors as models grew costlier and commercial, and that OLMo is meant to work against that trend
- [analysis] Yann LeCun — said, as [[Meta]]'s Chief AI Scientist, that open foundation models have been critical in driving generative-AI innovation
- [fact] Pekka Manninen — said CSC contributed compute capacity from the LUMI supercomputer, which Ai2 says supported the OLMo pretraining work
- [analysis] Jonathan Frankle — said, as Databricks chief scientist, that OLMo "sets the standard for what it means to be open" because it releases data, code, and intermediate checkpoints

## Key Quotes

> "Many language models today are published with limited transparency. Without having access to training data, researchers cannot scientifically understand how a model is working. It's the equivalent of drug discovery without clinical trials or studying the solar system without a telescope." — Hanna Hajishirzi, OLMo project lead and senior director of NLP Research, Ai2

> "With OLMo, open actually means 'open' and everyone in the AI research community will have access to all aspects of model creation, including training code, evaluation methods, data, and so on." — Noah Smith, OLMo project lead and senior director of NLP Research, Ai2

> "AI was once an open field centered on an active research community, but as models grew, became more expensive, and started turning into commercial products, AI work started to happen behind closed doors." — Noah Smith, OLMo project lead, Ai2

> "Open foundation models have been critical in driving a burst of innovation and development around generative AI. The vibrant community that comes from open source is the fastest and most effective way to build the future of AI." — Yann LeCun, Chief AI Scientist, Meta

> "I'm enthusiastic about getting OLMo into the hands of AI researchers." — Eric Horvitz, Chief Scientific Officer, Microsoft

> "Public supercomputers like LUMI play a vital role in the infrastructure for open and transparent AI." — Pekka Manninen, Director of Science and Technology, CSC

> "OLMo sets the standard for what it means to be open. Everyone in academia, industry, and the broader community will benefit enormously from access to not only the model but all of the training details, including the data, code, and intermediate checkpoints." — Jonathan Frankle, Chief Scientist (Neural Networks), Databricks

## Connections

- defines: [[OpenSourceAI]] — Ai2's leads define "truly open" as releasing data, training code, weights, and evaluation, not weights alone
- references: [[TrainingData]] — the Dolma pretraining corpus is released in full, the component Ai2 says is needed to study a model
- references: [[OpenWeights]] — the weights-only posture that Ai2 contrasts with OLMo's full release
- cites: [[Meta]] — quotes Meta's Chief AI Scientist Yann LeCun endorsing open foundation models
