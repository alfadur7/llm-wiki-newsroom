---
title: "OpenAI's New Model Challenges Meta's Open-Source Dominance"
type: source
tags: [OpenAI, Meta, open-weights, open-source-ai, licensing]
published: 2025-08-14
scraped: 2026-09-27
source_file: "raw/NewsScrap/OpenAI’s New Model Challenges Meta’s Open-Source Dominance.md"
source_url: "https://spectrum.ieee.org/open-ai-models"
last_updated: 2026-09-27
---

## Summary

An IEEE Spectrum news piece by contributing editor Matthew S. Smith, dated 2025-08-14, reports on [[OpenAI]]'s GPT-OSS release of 2025-08-05. It describes GPT-OSS as OpenAI's first open large language model since GPT-2 in 2019, shipped under the Apache 2.0 license, which it contrasts with the attached conditions of [[Meta]]'s Llama and Alibaba's Qwen [[ModelLicensing|licenses]]. The article sets out the divide between [[OpenWeights|open-weight]] and fully [[OpenSourceAI|open-source]] releases, stating that GPT-OSS does not meet the [[OpenSourceInitiative|OSI]]'s Open Source AI Definition 1.0 because it lacks training code and [[TrainingData|training-data]] details. Developers quoted in the piece value the model's permissive license, day-one availability, and speed, and one of them calls the full open-source bar too high. The article closes by suggesting the reception could pressure Meta and Alibaba to loosen their license terms; OpenAI, Meta, and Alibaba give no direct comment in the raw.

## Key Claims

- [fact] Matthew S. Smith — reports that OpenAI released GPT-OSS on August 5, 2025, and followed it shortly afterward with GPT-5
- [fact] Matthew S. Smith — reports that GPT-OSS comes in two versions, GPT-OSS-20b and GPT-OSS-120b
- [fact] Matthew S. Smith — reports that GPT-OSS is OpenAI's first open large language model since GPT-2's launch in 2019
- [fact] Matthew S. Smith — reports that GPT-OSS is released under the Apache 2.0 license
- [analysis] Matthew S. Smith — explains that Apache 2.0 imposes no limits on commercial use and allows derivative works to be released under a different license
- [analysis] Matthew S. Smith — explains that the Apache 2.0 patent grant helps shield those building on GPT-OSS from future infringement claims by the model's contributors
- [analysis] Dustin Carr — calls the Apache 2.0 license a "maximally permissive license" and the release a "very positive, very surprising development" [[gpt-oss-challenges-meta-open-weight#Key Quotes]]
- [fact] Matthew S. Smith — reports that Meta's Llama license requires derivative models to include the Llama name and comply with Meta's brand guidelines
- [fact] Matthew S. Smith — reports that most Alibaba Qwen 2.5 models use Apache 2.0, while the largest variant carries a research license restricting commercial use by large organizations
- [fact] Matthew S. Smith — reports that GPT-OSS was available at launch on Hugging Face and in the Ollama and LM Studio front-ends
- [fact] Matthew S. Smith — reports day-one support for GPT-OSS from Nvidia and AMD and from the cloud providers Microsoft Azure and Amazon AWS
- [analysis] Dustin Carr — describes the launch as an impressive execution because the models were usable immediately in tools such as LM Studio [[gpt-oss-challenges-meta-open-weight#Key Quotes]]
- [analysis] Hanna Hajishirzi — argues that meaningful AI progress requires open data, transparent training methods, intermediate checkpoints, and shared evaluations, not just open weights [[gpt-oss-challenges-meta-open-weight#Key Quotes]]
- [fact] Matthew S. Smith — reports that the Open Source Initiative responded to the GPT-OSS release with a tweet linking to its Open Source AI Definition
- [analysis] Matthew S. Smith — explains that open weights allow use and fine-tuning but do not include the training data needed to rebuild a model from scratch
- [fact] Matthew S. Smith — states that OSI's Open Source AI Definition 1.0 requires model releases to include all training code and details on the training data
- [analysis] Matthew S. Smith — states that the GPT-OSS release does not fulfill the Open Source AI Definition's requirements
- [fact] Dustin Carr — reported that the 20B variant ran at 45 to 50 tokens per second on his M4 MacBook
- [analysis] Dustin Carr — says that no model of GPT-OSS-20B's quality has come close to that speed [[gpt-oss-challenges-meta-open-weight#Key Quotes]]
- [analysis] Brendan Ashworth — argues that criticizing GPT-OSS for not meeting full open-source standards sets the bar too high, given its free availability and permissive license [[gpt-oss-challenges-meta-open-weight#Key Quotes]]
- [analysis] Brendan Ashworth — acknowledges a fully open-source GPT-OSS would be preferable but calls OpenAI's return to open weights a win for developers
- [forecast] Matthew S. Smith — expects the enthusiastic reaction to GPT-OSS could pressure Meta and Alibaba to loosen their license terms
- [analysis] Matthew S. Smith — assesses that Meta, previously regarded as the U.S. leader in open-weight models, faces its most serious threat yet from GPT-OSS after the rocky Llama 4 launch

## Key Quotes

> "maximally permissive license" — Dustin Carr, co-founder and CTO of Darkviolet.ai

> "You had the models instantly. You didn't have to wait a week for the models to get ready for LM Studio, and so on. It was an impressive execution." — Dustin Carr, co-founder and CTO of Darkviolet.ai

> "Nothing of this quality has come close to that speed." — Dustin Carr, co-founder and CTO of Darkviolet.ai

> "meaningful progress in AI is best achieved in the open—not just with open weights, but with open data, transparent training methods, intermediate checkpoints from pre-training and mid-training, and shared evaluations." — Hanna Hajishirzi, senior research director at [[Ai2|AI2]] and professor at the University of Washington

> "Expecting them to open source more is kind of a weird thing to complain about." — Brendan Ashworth, co-founder of Bunting Labs

## Connections

- references: [[OpenAI]] — the releasing company whose GPT-OSS launch, licensing, and distribution the article reports; no OpenAI comment is quoted
- references: [[Meta]] — its Llama license's naming and brand requirements are the contrast case, and its U.S. open-weight lead is called threatened
- references: [[HuggingFace]] — named as a model repository where GPT-OSS was available at launch
- cites: [[OpenSourceInitiative]] — the article reports its tweet response and states the OSAID 1.0 training-code and data requirements
- contradicts: [[OpenSourceInitiative]] — Brendan Ashworth argues that holding GPT-OSS to the full open-source standard sets the bar too high
- references: [[OpenWeights]] — the article separates open-weight releases such as GPT-OSS from fully open-source ones
- references: [[OpenSourceAI]] — GPT-OSS is stated not to meet the Open Source AI Definition 1.0
- references: [[ModelLicensing]] — compares Apache 2.0 with the Llama and Qwen license terms
- references: [[TrainingData]] — withheld training data is what prevents rebuilding the model from scratch
- references: [[FineTuning]] — open weights are described as allowing modification through fine-tuning
- contradicts: [[welcome-gpt-oss-openai|Welcome GPT OSS]] — the Hugging Face post headlines the family as "open-source," while this article states it fails the OSAID's requirements
