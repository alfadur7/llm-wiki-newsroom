---
title: "Open Source AI: Red Hat's Point-of-View"
type: source
tags: [Red Hat, open-source-ai, open-weights, model-weights, training-data, licensing]
published: 2025-02-03
scraped: 2026-09-23
source_file: "raw/NewsScrap/Open source AI Red Hat’s point-of-view.md"
source_url: "https://www.redhat.com/en/blog/open-source-ai-red-hats-point-view"
last_updated: 2026-09-23
---

## Summary

In a February 3, 2025 blog post, Red Hat CTO Chris Wright sets out Red Hat's minimum threshold for [[OpenSourceAI]]: open source-licensed model weights combined with open source software components. Wright argues that [[TrainingData]] alone does not fit the open-source "preferred form" for modification, since most community improvements come from modifying weights or [[FineTuning]] rather than touching the original data. He presents the threshold as a practical starting point, not a formal definition like the [[OpenSourceInitiative]]'s OSAID, and ties it to Red Hat's InstructLab, IBM Granite, and hybrid-cloud products. The post is a vendor's own statement; external assessment of the threshold is outside the raw's scope.

## Key Claims

- [fact] Red Hat — states that its minimum threshold for open source AI is open source-licensed model weights combined with open source software components
- [analysis] Red Hat — calls this threshold a starting point of open source AI rather than the final destination
- [analysis] Red Hat — says its view is not an attempt at a formal definition like the one the [[OpenSourceInitiative]] is undertaking with the Open Source AI Definition (OSAID)
- [analysis] Chris Wright — argues that AI models, especially LLMs, cannot be viewed in quite the same way as open source software because they principally consist of model weights
- [analysis] Chris Wright — argues that model weights are not software but in some respects serve a function similar to code
- [analysis] Chris Wright — argues that [[TrainingData]] alone does not fit the open-source role of the "preferred form" for modification, given its vast size and its tenuous, indirect connection to the trained weights
- [analysis] Chris Wright — states that most community improvements to AI models come from modifying weights or [[FineTuning]] rather than from access to the original training data
- [analysis] Chris Wright — argues that the freedom to improve models requires weights released with all the permissions users receive under open source licenses
- [analysis] Red Hat — encourages the open source community, regulators, and industry to keep striving for greater transparency when training and fine-tuning AI models
- [fact] Red Hat — says it leads the InstructLab project, which lets domain experts who are not data scientists contribute skills and knowledge to AI models
- [fact] Red Hat — states that it works with IBM Research on the Granite family of open source-licensed models
- [fact] Red Hat — states that the Granite 3.0 model family is released under a permissive open source license
- [analysis] Chris Wright — says the recent [[DeepSeek]] announcements show how open source innovation can affect AI at the model level and beyond
- [analysis] Chris Wright — notes concerns that the [[DeepSeek]] model's license does not clarify how the model was produced, which he says reinforces the need for transparency
- [forecast] Chris Wright — expects an open AI future centered on smaller, optimized, open models customized to enterprise data across the hybrid cloud
- [fact] Red Hat — states that Red Hat OpenShift AI builds on Kubernetes, KubeFlow, and OCI-compliant containers
- [fact] Red Hat — states that Red Hat Enterprise Linux AI (RHEL AI) incorporates the Granite LLM family and the InstructLab project
- [fact] Red Hat — lists upstream projects it has initiated, including RamaLama, TrustyAI, Climatik, and Podman AI Lab
- [fact] Red Hat — says its Neural Magic announcement lets organizations align smaller, optimized models with their data, served by the vLLM inference server
- [forecast] Red Hat — says it will continue to endorse efforts toward transparent work on models and their training

## Key Quotes

> "Red Hat sees the minimum threshold for open source AI as open source-licensed model weights combined with open source software components." — Chris Wright, Red Hat CTO

> "This is a starting point of open source AI, not the final destination." — Chris Wright, Red Hat CTO

> "Training data alone does not fit this role, given its typically vast size and the complicated pre-training process that results in a tenuous and indirect connection any one item of training data has to the trained weights and the resulting behavior of the model." — Chris Wright, Red Hat CTO

> "Freedom to make those model improvements requires that the weights be released with all the permissions users receive under open source licenses." — Chris Wright, Red Hat CTO

> "There are obviously concerns around DeepSeek's approach, namely that the model's license doesn't clarify how it was produced, which further reinforces the need for transparency." — Chris Wright, Red Hat CTO

## Connections

- defines: [[OpenSourceAI]] — sets Red Hat's minimum threshold of open-licensed weights plus open software components
- references: [[OpenWeights]] — treats openly licensed weights, not training data, as the core of an open model
- references: [[TrainingData]] — argues training data alone does not fit the "preferred form" role of source code
- references: [[FineTuning]] — cites weight modification and fine-tuning as where most community improvements happen
- references: [[ModelLicensing]] — requires weights released with the full permissions of open source licenses
- references: [[OpenSourceInitiative]] — distinguishes Red Hat's practical view from the OSI's formal OSAID
- references: [[DeepSeek]] — cites the DeepSeek announcements and concerns that its license does not clarify how the model was produced
- contradicts: [[case-against-osaid|The Case Against OSI's Open Source AI Definition]] — rejects the critics' premise that training data is the equivalent of a model's source code
