---
title: "What Open-Source Developers Need to Know about the EU AI Act's Rules for GPAI Models"
type: source
tags: [regulation, ai-act, general-purpose-ai, open-source-ai, licensing, training-data]
published: 2025-08-04
scraped: 2026-09-27
source_file: raw/NewsScrap/What Open-Source Developers Need to Know about the EU AI Act's Rules for GPAI Mo.md
source_url: "https://huggingface.co/blog/yjernite/eu-act-os-guideai"
last_updated: 2026-09-27
---

## Summary

A guide posted on [[HuggingFace|Hugging Face]] on 2025-08-04 by Cailean Osborne, Maximilian Gahntz, Lucie-Aimée Kaffee, Bruna Trevelin, Brigitte Tousignant and Yacine Jernite walks open-source developers through the [[EUAIAct|EU AI Act]]'s obligations for providers of general-purpose AI (GPAI) models, which apply from 2 August 2025. Drawing on the Act, the European Commission's GPAI guidelines, the Code of Practice and the training-data summary template, the authors explain that models released under a free and open-source license, with public weights and no monetization, are exempt from the documentation duties and the EU-representative duty. Such models still owe a copyright policy and a public training-data summary, and the exemptions do not reach models with systemic risk. The guide is a collaboration of researchers at Hugging Face, [[Mozilla]] and the [[LinuxFoundation|Linux Foundation]], states that it is not legal advice, and gives the authors' personal views rather than their organizations' positions.

## Key Claims

- [fact] Cailean Osborne et al. — state that from 2 August 2025 providers of GPAI models must meet the Act's obligations when placing models on the EU market, whether or not they are established in the EU
- [fact] Cailean Osborne et al. — state that providers of GPAI models placed on the EU market before 2 August 2025 have until 2 August 2027 to comply
- [analysis] Cailean Osborne et al. — describe the Act as designed to facilitate or automate compliance for researchers and open-source developers
- [analysis] Cailean Osborne et al. — liken the Act's "GPAI model" to what is often called a foundation model
- [fact] European Commission — gives as an indicative GPAI criterion training compute greater than 10^23 FLOPs plus the ability to generate language, text-to-image or text-to-video, according to the guide's quotation of its GPAI guidelines
- [fact] European Commission — lists a speech-to-text model, a chess or video-game model and a weather-modelling model, each trained with 10^24 FLOPs, as examples of models that are not GPAI models
- [fact] Cailean Osborne et al. — state that the Act presumes high-impact capabilities, and so systemic risk, when cumulative training compute exceeds 10^25 FLOPs
- [analysis] Cailean Osborne et al. — say the 10^25 FLOPs threshold currently captures only frontier models such as [[OpenAI]]'s GPT-4o, xAI's Grok 4 and [[MistralAI|Mistral]] 2 Large
- [analysis] Cailean Osborne et al. — note that developers may submit evidence that a model crossing the threshold exceptionally does not present systemic risk, an option they call useful for very large research models
- [fact] Cailean Osborne et al. — state that a developer is a GPAI provider only if it develops a GPAI model and places it on the EU market in the course of a commercial activity, paid or free of charge
- [analysis] Cailean Osborne et al. — say the bounds of "commercial activity" remain an open question and will likely be decided case by case
- [analysis] Cailean Osborne et al. — judge that related EU rules make it unlikely hobbyist developers, or unmonetized FOSS-licensed artifacts shared on GitHub or Hugging Face, count as commercial activity automatically
- [analysis] Cailean Osborne et al. — read Recital 18 of the Cyber Resilience Act, which excludes unmonetized free and open-source software from commercial activity, as pointing to a similar approach under the AI Act, while calling it probably not binding
- [fact] Cailean Osborne et al. — cite Article 2(6) as excluding AI models developed for the sole purpose of scientific research and development from the Act entirely
- [fact] European Commission — sets the threshold at which a modifier becomes a provider as modification compute exceeding one-third of the original model's training compute, according to the guide
- [fact] Cailean Osborne et al. — state that a modifier who becomes a provider has Article 53 duties limited to documenting its own modifications, a rule relevant to [[FineTuning]]
- [fact] Cailean Osborne et al. — list three conditions for the open-source exemption: a free and open-source license, publicly available parameters including weights, architecture and usage information, and no monetization
- [fact] European Commission — requires a qualifying license to uphold access, usage, modification and distribution rights and excludes licenses with research-only, acceptable-use or commercial restrictions, according to the guide's reading of paragraphs 78 and 83 of the guidelines
- [fact] European Commission — allows specific, proportionate, safety-oriented usage restrictions where the licensor sees a significant risk to public safety, security or fundamental rights, according to the guide's reading of paragraph 84 of the guidelines
- [analysis] Cailean Osborne et al. — judge that the Act's free and open-source license definition likely covers Apache 2.0, MIT and the permissive OpenMDW model license
- [fact] European Commission — counts as monetization making a model contingent on payment, on buying another product or service, on viewing ads on a developer-hosted platform, or on the provider receiving or processing personal data
- [fact] Cailean Osborne et al. — state that open-source GPAI providers are exempt from the Article 53(1)(a-b) documentation duties and the Article 54 EU-representative duty
- [fact] Cailean Osborne et al. — state that open-source GPAI providers are not exempt from the Article 53(1)(c) copyright policy or the Article 53(1)(d) public [[TrainingData|training data]] summary
- [fact] Cailean Osborne et al. — state that none of the open-source exemptions apply to GPAI models with systemic risk, which must meet Articles 53, 54 and 55 in full
- [fact] Cailean Osborne et al. — give Ai2's OLMo 2 as an example of a partially exempt open-source GPAI model and [[Meta]]'s Llama 3-8B as an example of a model that does not use a free and open-source license
- [fact] Cailean Osborne et al. — state that there are currently no open-source GPAI models with systemic risk
- [fact] Cailean Osborne et al. — describe the Code of Practice as voluntary, so providers who do not sign it must still show compliance in another way
- [fact] Cailean Osborne et al. — summarize the Code's copyright chapter as five measures, including respecting robots.txt and machine-readable rights reservations and designating a contact point for rightsholders
- [fact] Cailean Osborne et al. — state that the AI Office template for the training data summary has three sections: general model information, main datasets used and relevant data processing
- [fact] Cailean Osborne et al. — state that a provider that keeps training an already marketed model must update its training data summary every six months, or sooner after a materially significant change
- [fact] Cailean Osborne et al. — state that the Code's safety and security chapter sets 10 commitments for systemic-risk providers, with simplified pathways for small and medium-sized and small mid-cap enterprises, as part of [[AISafety|safety]] duties under Article 55
- [analysis] Cailean Osborne et al. — call it urgent to raise the open-source community's readiness for the GPAI obligations

## Key Quotes

> "The good news for the open-source community is that the AI Act is designed to facilitate or automate compliance for researchers and open-source developers." — Cailean Osborne et al., guide authors

> "These exemptions are designed to reflect a recognition of the value and potential of open development, while still ensuring accountability. However, it can be difficult to know when and to what extent they apply." — Cailean Osborne et al., guide authors

> "an indicative criterion for a model to be considered a GPAI model is that its training compute is greater than 10^23 FLOPs and it can generate language (whether in the form of text or audio), text-to-image or text-to-video." — European Commission, GPAI guidelines (as quoted in the guide)

> "making AI components available through open repositories should not, in itself, constitute a monetisation" — EU AI Act, Recital 103 (as quoted in the guide)

## Connections

- defines: [[EUAIAct]] — sets out the Act's GPAI and systemic-risk thresholds, the provider test and the open-source exemption scope
- references: [[OpenSourceAI]] — the three conditions under which a free and open-source release earns the Act's partial exemption
- references: [[ModelLicensing]] — the guidelines' rules on which licenses qualify, including the paragraph 84 safety carve-out and the likely status of Apache 2.0, MIT and OpenMDW
- references: [[OpenWeights]] — public weights, architecture and usage information are one of the three exemption conditions
- references: [[TrainingData]] — open-source providers still owe the Article 53(1)(d) public training data summary
- references: [[FineTuning]] — the one-third compute threshold at which a modifier becomes a provider
- references: [[AISafety]] — the Article 55 safety and security duties that no open-source exemption reaches
- references: [[HuggingFace]] — the guide's publisher and the platform whose unmonetized FOSS sharing the authors think is not automatically commercial
- references: [[Mozilla]] — the Mozilla Foundation is one of the three organizations whose researchers wrote the guide
- references: [[LinuxFoundation]] — one of the three organizations whose researchers wrote the guide
- references: [[OpenMDW]] — the permissive model license the authors judge likely covered by the Act's free and open-source license definition
- references: [[Ai2]] — Ai2's OLMo 2 is the guide's example of a partially exempt open-source GPAI model
- references: [[Meta]] — Llama 3-8B is the guide's example of a model outside the free and open-source license exemption
- references: [[OpenAI]] — GPT-4o and GPT-4.5 are the guide's examples of systemic-risk models
- references: [[MistralAI]] — Mistral 2 Large is named among the frontier models above the 10^25 FLOPs threshold
- references: [[eu-gpai-provider-guidelines|Commission GPAI guidelines announcement]] — the guidelines whose thresholds and license conditions the guide explains
- references: [[openmdw-1-1-nvidia-adoption|OpenMDW-1.1 adoption]] — OpenMDW is one of the licenses the authors expect to qualify as free and open-source
- contradicts: [[osi-eu-code-of-practice-open-source|OSI on the EU Code of Practice]] — the guidelines, as the guide reads them, let proportionate safety-related use restrictions sit inside a free and open-source license, while the OSI argues use restrictions conflict with rule 6 of the Open Source Definition
