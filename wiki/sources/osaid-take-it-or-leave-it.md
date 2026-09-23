---
title: "Open Source Artificial Intelligence Definition 1.0 - A \"take it or leave it\" approach for open source AI systems?"
type: source
tags: [OSAID, open-source-ai, ai-act, training-data, licensing]
published: 2025-03-04
scraped: 2026-09-23
source_file: raw/NewsScrap/Open Source Artificial Intelligence Definition 1.0 - A “take it or leave it” app.md
source_url: "https://legalblogs.wolterskluwer.com/copyright-blog/open-source-artificial-intelligence-definition-10-a-take-it-or-leave-it-approach-for-open-source-ai-systems/"
last_updated: 2026-09-23
---

## Summary

Yaniv Benhamou and Michel Reymond of the University of Geneva, writing on the Kluwer Copyright Blog, assess the [[OpenSourceInitiative]]'s Open Source AI Definition (OSAID) 1.0 against the EU AI Act. They call the OSAID's requirement that every component grant the four freedoms a "take it or leave it" approach, and they contrast it with the tiered Model Openness Framework from the Linux Foundation. The authors judge the OSAID's training-data disclosure rule stricter than the AI Act's training-content summary, but they see no friction between the two, because the instruments pursue different goals. They welcome the definition as a curb on [[OpenWashing]], yet they state a preference for a more flexible, tiered notion of openness.

## Key Claims

- [analysis] Yaniv Benhamou and Michel Reymond — state that open source experts have criticized self-certified "open" model releases by tech giants such as [[Meta]] and OpenAI as [[OpenWashing]]
- [analysis] Yaniv Benhamou and Michel Reymond — attribute the open-washing charge to two traits: selective release of model components and documentation, and restrictive license terms
- [analysis] Yaniv Benhamou and Michel Reymond — report the open source specialists' argument that releasing a trained model alone fails the open source test, because the model's behavior cannot be reproduced, analyzed, or modified without the other components
- [analysis] Yaniv Benhamou and Michel Reymond — cite a report finding that several self-described "open" releases withhold training and evaluation datasets and lack documentation
- [analysis] Yaniv Benhamou and Michel Reymond — say the downloadable [[DeepSeek]] model is not exempt from this problem, citing its training datasets and training code (the raw reads "does include," which the argument's context suggests is a dropped "not")
- [fact] Yaniv Benhamou and Michel Reymond — report that [[Meta]]'s July 2023 Llama 2 license barred reuse by licensees with more than 700 million monthly active users
- [fact] Yaniv Benhamou and Michel Reymond — report that the Llama 2 license also excluded using the model to improve or fine-tune other large language models
- [analysis] Yaniv Benhamou and Michel Reymond — argue that Responsible AI Licenses (RAIL), which exclude uses such as discrimination or defamation, are at odds with accepted definitions of open source
- [fact] Yaniv Benhamou and Michel Reymond — report that Google advertised its 2024 Gemma 2 model as an open model while attaching a Prohibited Use Policy that bars uses such as spam and sexually explicit content
- [fact] Yaniv Benhamou and Michel Reymond — report that the Linux Foundation's Model Openness Framework grades the openness of AI systems in three tiers
- [fact] [[OpenSourceInitiative]] — published the first version of the OSAID on 2024-10-28
- [fact] [[OpenSourceInitiative]] — defines an [[OpenSourceAI]] system as one made available under terms that grant the freedom to use, study, modify, and share it
- [fact] [[OpenSourceInitiative]] — requires the "complete source code used to train and run the system" but not the [[TrainingData]] itself
- [fact] [[OpenSourceInitiative]] — requires data information that must list all publicly available training data and all third-party training data, and where to obtain each
- [analysis] Yaniv Benhamou and Michel Reymond — characterize the OSAID as a "take it or leave it" approach, because it requires every component except training data to grant the four freedoms
- [analysis] Yaniv Benhamou and Michel Reymond — argue that the OSAID tracks the open source definition in Article 53(2) of the EU AI Act closely
- [analysis] Yaniv Benhamou and Michel Reymond — conclude that the OSAID is incompatible with RAIL terms and other restrictive [[ModelLicensing]] terms
- [analysis] Yaniv Benhamou and Michel Reymond — argue that requiring all training data would be too restrictive, since copyright, trade secrets, and anti-scraping terms often limit that data
- [analysis] Yaniv Benhamou and Michel Reymond — judge the OSAID's data-information requirement "rather expansive," because it demands disclosure of training use and offers no trade-secret exception
- [fact] EU AI Office — presented a template on 2025-01-17 for the training-content summary that Article 53(1)(d) of the AI Act requires from general-purpose AI providers
- [analysis] Yaniv Benhamou and Michel Reymond — report that the AI Office template drew mixed reactions from the OSI community over its lack of granularity on training-data disclosure
- [analysis] Yaniv Benhamou and Michel Reymond — argue that the OSAID's stricter disclosure rule is justified, because the AI Act governs EU market access while the OSAID certifies releases as open source
- [analysis] Yaniv Benhamou and Michel Reymond — conclude that the OSAID and the AI Act should not in principle conflict
- [forecast] Yaniv Benhamou and Michel Reymond — expect the OSAID's approach to leave only a subset of AI projects compatible with its requirements
- [analysis] Yaniv Benhamou and Michel Reymond — argue that a tiered notion of openness, as in the Model Openness Framework, may be preferable to the OSAID's binary test
- [forecast] Yaniv Benhamou and Michel Reymond — expect the definition of open source in AI to remain narrowly framed, since the OSAID and the AI Act take similar approaches

## Key Quotes

> "sufficiently detail(ed) information about the data used to train the system so that a skilled person can build a substantially equivalent system" — [[OpenSourceInitiative]]

> "the complete description of all data used for training, including (if used) of unshareable data, disclosing the provenance of the data, its scope and characteristics, how the data was obtained and selected, the labeling procedures, and data processing and filtering methodologies" — [[OpenSourceInitiative]]

> "draw up and make publicly available a sufficiently detailed summary about the content used for training of the general-purpose AI model" — EU AI Act, Article 53(1)(d)

## Connections

- cites: [[OpenSourceInitiative]] — quotes the OSAID's four freedoms, source-code requirement, and data-information text
- contradicts: [[OpenSourceAI]] — argues a tiered notion of openness may be preferable to the OSAID's binary "take it or leave it" test
- cites: [[Meta]] — cites the Llama 2 license's 700-million-user clause and its ban on improving other LLMs
- references: [[DeepSeek]] — named as a recent "open" release that still leaves components out
- references: [[OpenWashing]] — frames the self-certified "open" releases the OSAID is meant to curb
- references: [[TrainingData]] — the one component the OSAID exempts, and the focus of its disclosure rule
- references: [[ModelLicensing]] — RAIL terms and restrictive licenses fall outside the OSAID
- references: [[OpenAI]] — named with Meta as a tech giant whose self-certified "open" releases experts call open-washing
- references: [[EUAIAct]] — compares the OSAID with the Act's Article 53(2) open source definition and Article 53(1)(d) training-content summary, finding no conflict
- references: [[ModelOpennessFramework]] — the Linux Foundation's three-tier grading, which the authors say may be preferable to the OSAID's binary test

