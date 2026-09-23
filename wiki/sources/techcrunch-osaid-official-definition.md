---
title: "We Finally Have an 'Official' Definition for Open Source AI"
type: source
tags: [OSAID, open-source-ai, OSI, open-washing, training-data]
published: 2024-10-28
scraped: 2026-09-23
source_file: "raw/NewsScrap/We finally have an 'official' definition for open source AI TechCrunch.md"
source_url: "https://techcrunch.com/2024/10/28/we-finally-have-an-official-definition-for-open-source-ai/"
last_updated: 2026-09-23
---

## Summary

TechCrunch's Kyle Wiggers reports the [[OpenSourceInitiative]]'s release of version 1.0 of the Open Source AI Definition (OSAID), which requires enough design and [[TrainingData]] information for a model to be "substantially" recreated, plus freedoms to use, modify, and build on it. OSI executive vice president Stefano Maffulli frames the definition as a way to align policymakers and developers and to call out [[OpenWashing]], while conceding OSI has no enforcement power. The article sets the definition against [[Meta]], which rejects it and defends the Llama license, and against critics such as Lightning AI CTO Luca Antiga, who says it leaves training-data licensing unaddressed.

## Key Claims

- [fact] [[OpenSourceInitiative]] — released version 1.0 of the Open Source AI Definition on 2024-10-28 after several years of collaboration with academia and industry
- [fact] [[OpenSourceInitiative]] — requires an open source AI model to provide enough information about its design that a person could "substantially" recreate it
- [fact] [[OpenSourceInitiative]] — requires disclosure of training-data provenance, processing, and how the data can be obtained or licensed
- [fact] [[OpenSourceInitiative]] — grants users the freedom to use the model for any purpose and to modify it without asking permission
- [fact] [[StefanoMaffulli]] — said a main motivation for a consensus definition is getting policymakers and AI developers on the same page, noting that regulators are already watching the space
- [fact] [[StefanoMaffulli]] — said OSI did explicit outreach to diverse stakeholders, including organizations that most often talk to regulators
- [analysis] Kyle Wiggers — reports that OSI has no enforcement mechanism but intends to flag models described as "open source" that fall short of the definition
- [fact] [[StefanoMaffulli]] — said Google and Microsoft agreed to drop the term "open source" for models that are not fully open after discussions with OSI, but Meta has not
- [fact] Kyle Wiggers — reports that Meta requires platforms with more than 700 million monthly active users to request a special license to use its Llama models
- [fact] Kyle Wiggers — reports that Stability AI requires businesses with more than $1 million in revenue to obtain an enterprise license
- [fact] Kyle Wiggers — reports that Mistral's license bars the use of certain models and outputs for commercial ventures
- [analysis] AI Now Institute — concluded, in a study with Signal Foundation and Carnegie Mellon researchers, that many "open source" models are open source in name only, with secret training data, out-of-reach compute, and complex fine-tuning techniques
- [analysis] AI Now Institute — concluded, in the same study, that these "open source" projects tend to entrench and expand centralized power rather than democratize AI
- [fact] [[Meta]] — stated through a spokesperson that it disagrees with OSI's new definition despite having participated in the drafting process
- [analysis] [[Meta]] — argues its Llama license and acceptable use policy act as guardrails against harmful deployments
- [fact] [[Meta]] — said it is taking a "cautious approach" to sharing model details, including training data, as regulations such as California's training transparency law evolve
- [fact] [[Meta]] — pointed to other efforts to codify open source AI, including the Linux Foundation's suggested definitions and the [[FreeSoftwareFoundation]]'s criteria for free machine learning applications
- [fact] Kyle Wiggers — reports that Meta, Amazon, Google, Microsoft, Cisco, Intel, and Salesforce fund OSI's work, and that OSI secured a Sloan Foundation grant to lessen its reliance on industry backers
- [analysis] Kyle Wiggers — argues that companies treat dataset assembly as a competitive advantage and that training-data disclosure can expose developers to copyright lawsuits
- [analysis] Luca Antiga — argues a model can meet all OSAID requirements even when its training data is not freely available
- [analysis] Kyle Wiggers — reports that OSAID 1.0 does not address copyright as it pertains to AI models
- [fact] [[StefanoMaffulli]] — agreed the definition will need updates, and OSI has set up a committee to monitor how the OSAID is applied and propose amendments

## Key Quotes

> "Regulators are already watching the space." — [[StefanoMaffulli]], OSI executive vice president

> "An open source AI is an AI model that allows you to fully understand how it's been built. That means that you have access to all the components, such as the complete code used for training and data filtering." — [[StefanoMaffulli]], OSI executive vice president

> "Our hope is that when someone tries to abuse the term, the AI community will say, 'We don't recognize this as open source,' and it gets corrected." — [[StefanoMaffulli]], OSI executive vice president

> "We agree with our partner the OSI on many things, but we, like others across the industry, disagree with their new definition." — [[Meta]] spokesperson

> "There is no single open source AI definition, and defining it is a challenge because previous open source definitions do not encompass the complexities of today's rapidly advancing AI models." — [[Meta]] spokesperson

> "By neglecting to deal with licensing of training data, the OSI is leaving a gaping hole that will make terms less effective in determining whether OSI-licensed AI models can be adopted in real-world situations." — Luca Antiga, Lightning AI CTO

> "This isn't the work of lone geniuses in a basement." — [[StefanoMaffulli]], OSI executive vice president

## Connections

- cites: [[OpenSourceInitiative]] — reports the OSAID 1.0 release and quotes executive vice president Stefano Maffulli
- defines: [[OpenSourceAI]] — states the OSAID's recreation, data-disclosure, and usage-freedom requirements
- references: [[osi-open-source-ai-definition|The Open Source AI Definition 1.0]] — the definition this article reports on
- contradicts: [[OpenSourceAI]] — Meta states it disagrees with OSI's new definition and defends its restrictive Llama license
- contradicts: [[osi-open-source-ai-definition|The Open Source AI Definition 1.0]] — Luca Antiga argues the definition leaves a "gaping hole" by not dealing with training-data licensing
- cites: [[Meta]] — quotes a Meta spokesperson rejecting the definition and cites the 700-million-user Llama license threshold
- references: [[OpenWashing]] — OSI intends to flag models called "open source" that fall short of the definition
- references: [[TrainingData]] — data disclosure is required, and its licensing is the gap critics raise
- references: [[ModelLicensing]] — compares the license restrictions of Meta, Stability AI, and Mistral
- references: [[FreeSoftwareFoundation]] — Meta points to its free machine learning criteria as an alternative definition
- references: [[FineTuning]] — the cited study says fine-tuning techniques are too complex for many developers
- cites: [[StefanoMaffulli]] — the OSI's main voice on the definition's release and its limits
