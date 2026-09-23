---
title: "Open Weights Are Good. Open Source Is Better."
type: source
tags: [open-weights, open-source-ai, OSAID, training-data]
published: 2026-09-16
scraped: 2026-09-23
source_file: raw/NewsScrap/Open Weights Are Good. Open Source Is Better.md
source_url: "https://opensource.org/blog/open-weights-are-good-open-source-is-better"
last_updated: 2026-09-23
---

## Summary

In a 2026-09-16 post on the [[OpenSourceInitiative]] blog, Katie Steen-James argues that [[OpenWeights]] models are a real improvement over closed models but still fall short of [[OpenSourceAI]]. Open weights let users run a model locally, host it with a third party, or [[FineTuning|fine-tune]] it on their own data, yet without the training code and [[TrainingData]] they cannot fully study or modify it. The post holds that only Open Source AI as defined by the OSI grants all four freedoms, and it cites a study built on Ai2's Olmo as research that full openness makes possible.

## Key Claims

- [analysis] [[OpenSourceInitiative]] — states that the four software freedoms are the freedoms to use, study, modify, and share without asking permission from the rights holder
- [fact] [[OpenSourceInitiative]] — puts the demand-side value of the Open Source ecosystem at $8.8 trillion
- [analysis] [[OpenSourceInitiative]] — describes an AI model as three main components: training data, weights/parameters, and code for data preparation and training
- [analysis] [[OpenSourceInitiative]] — holds that a user's access to those components determines whether an AI system is closed, open-weight, or Open Source
- [analysis] [[OpenSourceInitiative]] — says [[OpenWeights]] models let users run the model locally, paying only for electricity and hardware, or host it through a third-party provider
- [analysis] [[OpenSourceInitiative]] — says open weights let users [[FineTuning|fine-tune]] a model on their own data, keeping control of that data
- [analysis] [[OpenSourceInitiative]] — names ChatGPT, Claude, and many autonomous driving systems as examples of fully closed models
- [analysis] [[OpenSourceInitiative]] — argues that open-weight models limit the freedom to modify a model and prevent users from fully studying it
- [analysis] [[OpenSourceInitiative]] — argues that without the code and [[TrainingData]], a user cannot fully inspect why a model gives an output or whether that output can be trusted
- [analysis] [[OpenSourceInitiative]] — states that [[OpenSourceAI]] under its definition releases the weights, the training code, and either the training data or a detailed account of how the data was built
- [fact] [[OpenSourceInitiative]] — reports that researchers used Ai2's Olmo, with its full training dataset and model checkpoints, to inject new information into training data and observe how the model memorized or forgot it
- [analysis] [[OpenSourceInitiative]] — argues that the Olmo study was only possible because Olmo is released as Open Source AI (compare [[hello-olmo-truly-open-llm|Hello OLMo]])
- [forecast] [[OpenSourceInitiative]] — expects the next phase of AI development to depend on recognizing that Open Source AI is "where the real innovation lies"

## Key Quotes

> "Open-weights allow you to exercise some freedoms, but not all, and only to a certain degree. True Open Source AI allows you to exercise all four without restriction." — Katie Steen-James, author of the OSI blog post

> "The case for open-weights has been made and its benefits over closed models are clear. This next phase of technological development will depend on our realization that Open Source AI is where the real innovation lies." — Katie Steen-James, author of the OSI blog post

## Connections

- cites: [[OpenSourceInitiative]] — the post is published on the OSI blog and restates the OSI's Open Source AI definition
- defines: [[OpenWeights]] — defines open-weight models as releasing weights but no other model components
- defines: [[OpenSourceAI]] — sets out the components an OSI-defined Open Source AI system must release and the four freedoms it grants
- references: [[TrainingData]] — the withheld component that blocks full study of open-weight models
- references: [[FineTuning]] — one of the customizations open weights make possible
- references: [[hello-olmo-truly-open-llm|Hello OLMo]] — Ai2's Olmo release, cited as the model that enabled the memorization study
