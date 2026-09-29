---
title: "Apertus: a fully open, transparent, multilingual language model"
type: source
tags: [open-source-ai, training-data, open-weights]
published: 2025-09-02
scraped: 2026-09-27
source_file: raw/NewsScrap/Apertus a fully open, transparent, multilingual language model.md
source_url: "https://ethz.ch/en/news-and-events/eth-news/news/2025/09/press-release-apertus-a-fully-open-transparent-multilingual-language-model.html"
last_updated: 2026-09-27
---

## Summary

In a 2025-09-02 joint press release, EPFL, ETH Zurich and the Swiss National Supercomputing Centre (CSCS) announced Apertus, which they call Switzerland's first large-scale, open, multilingual language model. The release comes in 8B and 70B parameter sizes under what the institutions call a permissive open-source license that allows commercial use; the license is not named in the raw, which points to [[HuggingFace|Hugging Face]] for the terms. The institutions say the architecture, weights, intermediate checkpoints, [[TrainingData|training data]] and training methods are all published. They contrast this with models that open only selected components, the [[OpenWeights|open-weights]] posture. They also say the model was built with Swiss data-protection and copyright law and the [[EUAIAct|EU AI Act]]'s transparency obligations in mind. The page is the developers' own announcement, and no external assessment of its "fully open" or compliance claims is within the raw's scope.

## Key Claims

- [fact] ETH Zurich — announced that EPFL, ETH Zurich and CSCS released Apertus on 2025-09-02 as part of the Swiss AI Initiative
- [fact] ETH Zurich — stated that Apertus is freely available in two sizes, 8 billion and 70 billion parameters
- [fact] ETH Zurich — stated that both Apertus models are released under a permissive open-source license that allows use in education, research and commercial applications
- [fact] ETH Zurich — stated that the architecture, model weights, training data and training methods of Apertus are openly accessible and fully documented
- [fact] ETH Zurich — stated that the team published training source code, dataset documentation and model weights with intermediate checkpoints, with the terms and conditions available via [[HuggingFace]]
- [analysis] ETH Zurich — says full openness distinguishes Apertus from [[OpenWeights|models that make only selected components accessible]]
- [fact] ETH Zurich — stated that Apertus was trained on 15 trillion tokens across more than 1,000 languages, with 40% of the data non-English
- [fact] ETH Zurich — stated that Apertus is available through Swisscom, the [[HuggingFace]] platform and the Public AI network
- [fact] ETH Zurich — stated that the [[TrainingData|training corpus]] uses only publicly available data, filtered to respect machine-readable website opt-outs, even retroactively, and to remove personal data
- [analysis] ETH Zurich — says Apertus was developed with due consideration to Swiss data-protection and copyright laws and to the transparency obligations of the [[EUAIAct]]
- [fact] ETH Zurich — stated that development is funded by over 10 million GPU hours on CSCS's "Alps" supercomputer and by the ETH Board, with Swisscom as the main strategic partner
- [forecast] ETH Zurich — says future versions aim to expand the model family, improve efficiency and explore domain-specific adaptations in law, climate, health and education
- [analysis] Martin Jaggi — said the release aims to provide a blueprint for developing a trustworthy, sovereign and inclusive AI model [[apertus-fully-open-multilingual-llm#Key Quotes|Key Quotes]]
- [analysis] Imanol Schlag — claimed Apertus is among the few fully open LLMs at its scale and the first to treat multilingualism, transparency and compliance as foundational design principles [[apertus-fully-open-multilingual-llm#Key Quotes|Key Quotes]]
- [analysis] Thomas Schulthess — said Apertus is not a conventional research-to-product technology transfer but a driver of innovation
- [analysis] Joshua Tan — called Apertus the leading public AI model, built by public institutions for the public interest
- [fact] Daniel Dobos — said Swisscom deploys Apertus on its sovereign Swiss AI Platform and supports access during the Swiss {ai} Weeks
- [forecast] Antoine Bosselut — said the release is the beginning of a long-term commitment and that hackathon feedback will help improve future generations of the model

## Key Quotes

> "With this release, we aim to provide a blueprint for how a trustworthy, sovereign, and inclusive AI model can be developed." — Martin Jaggi, Professor of Machine Learning at EPFL and member of the Steering Committee of the Swiss AI Initiative

> "Apertus is not a conventional case of technology transfer from research to product. Instead, we see it as a driver of innovation and a means of strengthening AI expertise across research, society and industry." — Thomas Schulthess, Director of CSCS and Professor at ETH Zurich

> "Apertus is built for the public good. It stands among the few fully open LLMs at this scale and is the first of its kind to embody multilingualism, transparency, and compliance as foundational design principles." — Imanol Schlag, technical lead of the LLM project and Research Scientist at ETH Zurich

> "Swisscom is proud to be among the first to deploy this pioneering large language model on our sovereign Swiss AI Platform. As a strategic partner of the Swiss AI Initiative, we are supporting the access of Apertus during the Swiss {ai} Weeks. This underscores our commitment to shaping a secure and responsible AI ecosystem that serves the public interest and strengthens Switzerland's digital sovereignty." — Daniel Dobos, Research Director at Swisscom

> "Currently, Apertus is the leading public AI model: a model built by public institutions, for the public interest. It is our best proof yet that AI can be a form of public infrastructure like highways, water, or electricity." — Joshua Tan, Lead Maintainer of the Public AI Inference Utility

> "Apertus demonstrates that generative AI can be both powerful and open. The release of Apertus is not a final step, rather it's the beginning of a journey, a long-term commitment to open, trustworthy, and sovereign AI foundations, for the public good worldwide." — Antoine Bosselut, Professor and Head of the Natural Language Processing Laboratory at EPFL and Co-Lead of the Swiss AI Initiative

## Connections

- defines: [[OpenSourceAI]] — the institutions define "fully open" as publishing the architecture, weights, training data and methods, not selected components
- references: [[TrainingData]] — the training corpus and its opt-out and personal-data filtering are documented and released
- references: [[OpenWeights]] — the institutions contrast Apertus with models that open only selected components
- references: [[HuggingFace]] — a distribution venue for the models and the host of their license terms
- references: [[EUAIAct]] — the developers say Apertus was built with the Act's transparency obligations in mind
- references: [[ModelLicensing]] — both sizes ship under a permissive open-source license that allows commercial use
