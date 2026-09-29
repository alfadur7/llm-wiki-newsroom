---
title: "Ai2 (Allen Institute for AI)"
type: entity
kind: org
tags: [Ai2, OLMo, open-source-ai, training-data, research-institute]
sources: [hello-olmo-truly-open-llm, osi-open-source-ai-definition, osi-open-weights-good-open-source-better, case-against-osaid, eu-ai-act-gpai-guide-open-source-developers, gpt-oss-challenges-meta-open-weight, rethinking-open-source-generative-ai, open-secret-of-open-washing, open-washing-four-criteria, tech-industry-open-source-ai-definition-problem]
last_updated: 2026-09-27
---

## Overview

Ai2, the Allen Institute for AI, is the research institute behind the OLMo language models. It announced OLMo 7B on 2024-02-01 as a "truly open" large language model, released with its pretraining data, training code, model weights, and evaluation suite rather than weights alone. Ai2 is also written AI2, AllenAI, or the Allen Institute in the sources.

In the wiki's corpus, OLMo is cited as an example of a fully open model against which weights-only [[OpenWeights]] releases are measured. The [[OpenSourceInitiative]] lists OLMo among the models validated as compliant with its [[OpenSourceAI]] Definition. The "truly open" label is Ai2's own, from its announcement, which carries no external assessment; outside assessments come from openness surveys, the OSI, and policy commentary.

## Key Facts

- **OLMo 7B release (2024-02-01)** — Ai2 released full weights for four 7B-scale OLMo variants, each trained to at least 2T tokens, with inference code, training metrics, and training logs. It released its evaluation suite with 500+ checkpoints per model. Pretraining ran on Dolma, which Ai2 describes as a three-trillion-token open [[TrainingData]] corpus released with the code that produces it.
- **Partners** — Ai2's announcement credits Harvard's Kempner Institute, AMD, CSC (the LUMI supercomputer), the University of Washington's Allen School, and Databricks.
- **Openness rankings** — Andreas Liesenfeld and Mark Dingemanse, in their openness survey, place AllenAI's OLMo Instruct, with BloomZ and LLM360's AmberChat, at the top of their openness ranking, though the same paper reserves the phrase "substantially claim open source status" for BloomZ alone. The Register's Steven J. Vaughan-Nichols, drawing on the same survey, reports OLMo among a handful of lesser-known LLMs that could be considered open. In Tech Policy Press, JJ Jasser names the Allen Institute's OLMo, [[EleutherAI]]'s GPT-NeoX, and LLM360's K2 among the few models meeting all four of his openness criteria.
- **Open training data** — The New Stack's David Cassel reports that Ai2 has been releasing LLMs with open training data, without naming the releases.
- **Regulatory example** — a [[HuggingFace|Hugging Face]]–hosted guide by Cailean Osborne and co-authors gives Ai2's OLMo 2 as an example of a partially exempt open-source general-purpose AI model under the [[EUAIAct|EU AI Act]].
- **Research use** — the OSI reports that researchers used OLMo's full training dataset and checkpoints to study how the model memorized or forgot injected information, and argues this was possible only because OLMo is fully open.
- **ImpACT Licenses** — MIT Technology Review reports that the Allen Institute for AI developed ImpACT Licenses, which restrict redistribution of models and data based on their potential risks.
- **Spokespeople** — at the 2024 launch, OLMo project leads Hanna Hajishirzi and Noah Smith spoke for the release: Hajishirzi argued that researchers cannot understand a model without its training data, and Smith said that with OLMo "open actually means 'open'", covering training code, evaluation methods, and data. In 2025 Hajishirzi told IEEE Spectrum that progress needs open data, transparent training methods, intermediate checkpoints, and shared evaluations — "not just with open weights".

## Connections
- [[OpenSourceInitiative]] — validated OLMo as compliant with its Open Source AI Definition and cites OLMo research
- [[OpenSourceAI]] — the definition OLMo is validated against; Ai2's leads describe OLMo as meeting its fuller reading
- [[OpenWeights]] — the weights-only posture Ai2 contrasts with OLMo's full release
- [[TrainingData]] — the Dolma corpus that Ai2 released in full
- [[EUAIAct]] — the regulation under which OLMo 2 is given as a partially exempt example
- [[ModelLicensing]] — the ImpACT Licenses Ai2 developed
- [[EleutherAI]] — its GPT-NeoX is named beside OLMo among models meeting all four openness criteria
- [[HuggingFace]] — hosts the EU AI Act guide that cites OLMo 2
- [[hello-olmo-truly-open-llm|Ai2's OLMo 7B announcement]] — the release, its partners, and the project leads' remarks
- [[osi-open-source-ai-definition|OSI's Open Source AI Definition]] — the OSI list of validated models including OLMo
- [[osi-open-weights-good-open-source-better|OSI on open weights vs open source]] — the OSI post citing the OLMo memorization study
- [[rethinking-open-source-generative-ai|Liesenfeld and Dingemanse's openness survey]] — ranks OLMo Instruct at the top
- [[open-secret-of-open-washing|The Register on open washing]] — reports AllenAI's OLMo among the few models that could be considered open
- [[open-washing-four-criteria|Tech Policy Press on four openness criteria]] — lists OLMo among models meeting all four criteria
- [[eu-ai-act-gpai-guide-open-source-developers|EU AI Act guide for open-source developers]] — the guide citing OLMo 2
- [[tech-industry-open-source-ai-definition-problem|MIT Technology Review on the definition problem]] — reports the ImpACT Licenses
- [[gpt-oss-challenges-meta-open-weight|IEEE Spectrum on GPT-OSS]] — carries Hajishirzi's remarks on open weights
- [[case-against-osaid|The New Stack on the case against the OSAID]] — reports that Ai2 has been releasing LLMs with open training data
