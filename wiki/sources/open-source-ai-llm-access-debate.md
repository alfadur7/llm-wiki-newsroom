---
title: "Open-Source AI's Role in the LLM Access Debate"
type: source
tags: [open-source-ai, open-weights, ai-safety, model-licensing, Meta, OpenAI]
published: 2023-04-10
scraped: 2026-09-27
source_file: "raw/NewsScrap/Open-source AI's role in LLM access debate VentureBeat.md"
source_url: "https://venturebeat.com/ai/with-a-wave-of-new-llms-open-source-ai-is-having-a-moment-and-a-red-hot-debate"
last_updated: 2026-09-27
---

## Summary

A VentureBeat report by Sharon Goldman, dated 2023-04-10, describes a wave of open LLM releases built on [[Meta]]'s LLaMA — Stanford's Alpaca, Databricks' Dolly, Vicuna, Koala and ColossalChat — after LLaMA's weights, shared with researchers case by case, leaked on 4chan. It sets that wave against a shift toward closed models, sharpened by [[OpenAI]]'s GPT-4 technical report, which withheld architecture, dataset and training details. Quoted voices from [[HuggingFace|Hugging Face]], Meta, OpenAI, Lightning AI, [[EleutherAI]] and elsewhere debate how open models should be, and most call for a balance between open and closed release. Meta's Joelle Pineau defends LLaMA's "gated" release as a middle path, while Simon Willison leans toward open source but names misuse risks such as romance scams at scale.

## Key Claims

- [fact] Sharon Goldman — reports that OpenAI reportedly used 10,000 Nvidia GPUs to train ChatGPT
- [fact] Sharon Goldman — reports that Databricks announced the ChatGPT-like Dolly, inspired by Stanford's Alpaca, which used the weights of Meta's LLaMA model released in late February 2023
- [fact] Sharon Goldman — reports that Meta made LLaMA's weights available to academics and researchers case by case and that the weights subsequently leaked on 4chan
- [fact] Sharon Goldman — reports that none of the LLaMA-based open LLMs was yet available for commercial use, because LLaMA is not licensed for commercial use and OpenAI's GPT-3.5 terms bar building competing models
- [fact] Sharon Goldman — reports that the German nonprofit LAION proposed a publicly funded supercomputer with 100,000 accelerators to build open-source replicas of models as large as GPT-4
- [fact] [[Mozilla]] — announced an open-source AI initiative intended to create a decentralized AI community as a "counterweight" to large profit-focused companies
- [analysis] Clement Delangue — says most AI progress in the past five years came from open science and open source, citing the openly shared Transformer architecture
- [analysis] Clement Delangue — says companies have moved to proprietary models that may lack even a research paper, leaving researchers to speculate and reducing transparency
- [analysis] Moses Guttmann — describes open-source AI as a spectrum on which a company unwilling to share source code can still share anonymized or sampled training data
- [forecast] Sundar Pichai — expects a diverse ecosystem in which open-source models, on-device models, companies' own models and cloud-hosted models coexist
- [analysis] Joelle Pineau — says accountability and transparency in AI models are essential and that open- and closed-source AI will always coexist
- [analysis] Joelle Pineau — calls safety concerns cited for keeping models closed valid but says progress requires some level of transparency
- [fact] Joelle Pineau — cites Stanford's Alpaca as an example of "gated access," in which Meta gave academic researchers LLaMA weights that they fine-tuned into a different model
- [fact] Joelle Pineau — states that Meta withheld commercial use of LLaMA because the data it was trained on does not allow commercial usage
- [analysis] Joelle Pineau — says Meta received complaints both that LLaMA was not open enough and that it was too open
- [analysis] Joelle Pineau — says releasing LLaMA fully openly would not be responsible today, which is why it had a gated release
- [fact] Sharon Goldman — reports that OpenAI's GPT-4 technical report of about 98 pages omitted details of architecture, model size, hardware, training compute, dataset construction and training method
- [analysis] William Falcon — argues that OpenAI's long GPT-4 paper makes the release feel open-source and academic when it is not
- [analysis] William Falcon — argues that monetization pressure has led OpenAI to divorce itself from the open-source community
- [fact] Ilya Sutskever — told The Verge that sharing research so openly had been "wrong" and that OpenAI's reasons for withholding GPT-4 details, competition and safety, were "self-evident"
- [fact] Sandhini Agarwal — states that OpenAI makes its technology available to external researchers who work closely with it and that it could not have scaled ChatGPT without open-source software
- [analysis] Stella Biderman — says most people agree there should be a balance between open and closed AI
- [analysis] Stella Biderman — points to a disconnect between saying information cannot be shown and offering to sell the same model
- [analysis] Stella Biderman — says some models, such as national-security models, should not be released, but that open-source research is essential for studying models outside the companies with a financial interest in them
- [analysis] Simon Willison — says LLaMA showed that useful language models can run on a laptop rather than requiring access through OpenAI or other organizations
- [analysis] Simon Willison — warns that locally run and retrained models can bypass filters, citing 4chan projects to train "anti-woke" language models
- [forecast] Simon Willison — warns that scammers could use language models to run romance scams at a massive scale
- [analysis] Simon Willison — says he leans toward open-source AI because he does not want the technology controlled by a few giant companies, while conceding the risks of misuse could outweigh the benefits
- [analysis] Alex Engler — wrote in 2021 that open-source AI is so easy to use that almost anyone with a programming background can deploy it without understanding it
- [analysis] Joelle Pineau — argues that the level of access to a model should depend on its potential for harm, with transparency for verifiability audits

## Key Quotes

> "Most of the progress in the past five years in AI came from open science and open source." — Clement Delangue, Hugging Face CEO

> "Now, we don't know if [a model] is 200 billion or 10 billion parameters. The research community is left speculating about the details, and it creates less transparency." — Clement Delangue, Hugging Face CEO

> "On the one hand, we have many people who are complaining it's not nearly open enough, they wish we would have enabled commercial use for these models. But the data we train on doesn't allow commercial usage of this data. We are respecting the data." — Joelle Pineau, VP of AI research at Meta

> "That's why the LLaMA model had a gated release. Many people would have been very happy to go totally open. I don't think that's the responsible thing to do today." — Joelle Pineau, VP of AI research at Meta

> "That makes it feel like it's open-source and academic, but it's not." — William Falcon, CEO of Lightning AI

> "At some point it will be quite easy, if one wanted, to cause a great deal of harm with those models. And as the capabilities get higher it makes sense that you don't want to disclose them." — Ilya Sutskever, OpenAI chief scientist and co-founder

> "But I'm sympathetic to the concern that there is a disconnect in rhetoric between, we can't show this information and also we can sell it to you." — Stella Biderman, AI researcher at Booz Allen Hamilton and [[EleutherAI]]

> "I don't want this technology to be controlled by just a few giant companies; [that] feels inherently wrong to me given its impact." — Simon Willison, co-creator of Django

> "What if I'm wrong? What if the risks of misuse outweigh the benefits of openness? It's difficult to balance the pros and cons." — Simon Willison, co-creator of Django

## Connections

- cites: [[Meta]] — quotes Pineau on LLaMA's gated release, its non-commercial terms and the weight leak on 4chan
- cites: [[OpenAI]] — quotes Sutskever and Agarwal on OpenAI's reasons for withholding GPT-4 details and its use of open-source software
- contradicts: [[OpenAI]] — Falcon says OpenAI's closed GPT-4 release divorced it from the open-source community, and Pineau does not accept safety as a reason to keep models closed without transparency
- cites: [[HuggingFace]] — its CEO Delangue attributes most recent AI progress to open science and open source
- references: [[EleutherAI]] — Stella Biderman, quoted as an AI researcher at Booz Allen Hamilton and EleutherAI, calls open-source research essential for studying models
- cites: [[Mozilla]] — announced an open-source AI initiative as a counterweight to profit-focused companies
- references: [[OpenWeights]] — LLaMA's weights, shared with researchers and then leaked, seeded Alpaca, Vicuna and other derivatives
- references: [[OpenSourceAI]] — the report frames the debate over whether AI models should be freely modifiable and distributable
- references: [[ModelLicensing]] — LLaMA's non-commercial license and OpenAI's GPT-3.5 terms kept the derivative models out of commercial use
- references: [[TrainingData]] — Pineau ties LLaMA's non-commercial terms to the licensing of its training data
- references: [[FineTuning]] — Alpaca and Vicuna are fine-tuned versions of LLaMA's weights
- references: [[AISafety]] — Sutskever, Willison and Engler raise misuse risks as grounds for caution about open release
- contradicts: [[open-source-ai-uniquely-dangerous|Open-Source AI Is Uniquely Dangerous]] — Harris calls for pausing unsecured releases, while Willison leans toward open models and Biderman calls open-source research essential
