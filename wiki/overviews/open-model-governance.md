---
title: "Open-Model Governance"
type: overview
tags: []
cluster: open-model-governance
sources: [eleutherai-common-pile-dataset, tech-industry-open-source-ai-definition-problem, eu-ai-act-gpai-guide-open-source-developers, apertus-fully-open-multilingual-llm, open-weights-not-open-source-label-dispute, mozilla-eleutherai-hf-sb-1047-letter, lwn-openmdw-license-review, open-secret-of-open-washing, eu-gpai-provider-guidelines, euronews-meta-open-source-ai-not-all-it-seems, meta-muse-glimmer-apache-2-0, zuckerberg-superintelligence-not-all-open-source, osi-eu-code-of-practice-open-source, openmdw-1-1-nvidia-adoption, open-weights-american-ai-leadership, hello-olmo-truly-open-llm, open-future-osaid-step-forward]
last_updated: 2026-09-30
---

# Open-Model Governance

## Overview

This grouping is a bridge, not a debate of its own. Only one of the wiki's 66 sources belongs chiefly here, [[eleutherai-common-pile-dataset|TechCrunch's report on EleutherAI's Common Pile]]. Another 31 bear on it while belonging chiefly to the two larger groupings. What its eight hubs share is the power to make an "open" label count in those groupings' arguments.

The hubs fall into three kinds. The rules are the [[EUAIAct|EU AI Act]], whose exemption rewards an open license, and the [[OpenMDW]] license, which the Linux Foundation asks the OSI ([[OpenSourceInitiative|Open Source Initiative]]) to certify. The builders are [[Ai2]] and [[EleutherAI]], with [[HuggingFace|Hugging Face]] as their venue, and like the Swiss [[apertus-fully-open-multilingual-llm|Apertus]] team they publish data and code to show what a full release looks like. The label-setters are the [[LinuxFoundation|Linux Foundation]], [[MarkZuckerberg|Mark Zuckerberg]], who applies the label to [[Meta]]'s models, and [[StefanoMaffulli|Stefano Maffulli]], who led the OSI's definition drive and says where Meta's terms fall short. The sources cited here run from [[hello-olmo-truly-open-llm|Ai2's 2024-02-01 OLMo announcement]] to [[open-weights-not-open-source-label-dispute|a 2026-09-15 column in The Register]].

The evidence grade is thin where the stakes are highest. The [[eu-ai-act-gpai-guide-open-source-developers|Hugging Face–hosted guide]] to the Act states that it is not legal advice and gives its authors' personal views. The [[eu-gpai-provider-guidelines|Commission's guidelines]] call themselves not legally binding. The Common Pile's benchmark results and Apertus's "fully open" claim are their makers' own, with no outside test in the sources. The firm facts are rule texts, dates and release specifications, and attribution to a named speaker carries most of the rest.

Three tensions run through the bridge, each imported from a neighbouring grouping. On **legal payoff vs label discipline**, the EU guide's authors welcome the exemption as easing compliance, while [[open-secret-of-open-washing|Steven J. Vaughan-Nichols]] calls the reward an incentive to [[OpenWashing|open-wash]]. On **one grant for everything vs who bears the rights-clearing and litigation risk**, the Linux Foundation backs OpenMDW, and [[lwn-openmdw-license-review|OSI reviewers, as LWN reports]], say it puts that risk on recipients. On **open data suffices vs open resources fall short**, EleutherAI's own tests back openly licensed text, while Open Future's Tarkowski and Keller find open resources too thin for large models. None of the three is settled in the 2026 sources.

## Recent Changes

- 2026-09-15 — [[open-weights-not-open-source-label-dispute|A Register column]] quotes Maffulli calling the OSI's OpenMDW review "tainted by an ideological bias". [[StefanoMaffulli]]
- 2026-08-21 — [[lwn-openmdw-license-review|LWN reports]] that the OSI list discussion of OpenMDW wound down with no approval in sight. [[OpenMDW]]
- 2026-08-10 — [[meta-muse-glimmer-apache-2-0|VentureBeat reports]] that Meta released Muse Glimmer's weights under Apache 2.0, with Zuckerberg promising more. [[MarkZuckerberg]]
- 2026-07-24 — [[open-weights-american-ai-leadership|An open letter]] defending open weights lists the Linux Foundation, EleutherAI and Hugging Face among its signatories. [[LinuxFoundation]]

## Key Entities & Concepts

- **The rulebook** — the [[EUAIAct|EU AI Act]] sets GPAI (general-purpose AI) duties and a partial exemption for openly licensed models. The Commission's guidelines and the voluntary Code of Practice interpret it.
- **A license seeking a stamp** — [[OpenMDW]] is the permissive model license that the [[LinuxFoundation|Linux Foundation]] launched with the PyTorch Foundation and sent to the OSI for approval. The foundation also maintains the tiered [[ModelOpennessFramework|Model Openness Framework]].
- **Fully open builders** — [[Ai2]] released OLMo with its Dolma corpus, and [[EleutherAI]] released the Common Pile and argued for open research in policy fights. A third fully open release, Apertus, comes from the Swiss federal institutes of technology in Lausanne and Zurich and the Swiss National Supercomputing Centre.
- **Venue and co-author** — [[HuggingFace|Hugging Face]] hosts the models and datasets. Its researchers co-wrote the EU guide and co-signed a letter on California's Senate Bill 1047.
- **Label-setters** — [[MarkZuckerberg|Mark Zuckerberg]] makes Meta's case for calling its models open source. [[StefanoMaffulli|Stefano Maffulli]] led the OSI's definition drive and, as its former executive director, charged that the OSI's OpenMDW review is biased.
- **Borrowed anchors** — the concepts these actors argue over, such as [[OpenSourceAI|open-source AI]], [[TrainingData|training data]] and [[ModelLicensing|model licensing]], are anchored in the two neighbouring groupings, not here.

## Subtopics

The **EU exemption as a payoff** is the bridge's clearest rule. The [[eu-ai-act-gpai-guide-open-source-developers|guide by Cailean Osborne and co-authors]] lists three conditions: a free and open-source license, public weights and architecture, and no monetization. A qualifying model is spared the documentation and EU-representative duties, but still owes a copyright policy and a public training-data summary. The guide gives Ai2's OLMo 2 as partially exempt and Meta's Llama 3-8B as outside the exemption. [[tech-industry-open-source-ai-definition-problem|Zuzanna Warso of Open Future]] names the exemption as a regulatory benefit of the label. The guide's authors call it good news that the Act "is designed to facilitate or automate compliance for researchers and open-source developers." Vaughan-Nichols calls the same reward an incentive to open-wash.

The **use-restriction question** is where the rule and the OSI's test meet. The [[osi-eu-code-of-practice-open-source|OSI reports]] that early drafts of the Code of Practice mandated acceptable use policies, which it says conflict with rule 6 of the [[OpenSourceDefinition|Open Source Definition]]. After the OSI and allies wrote to the drafting chairs, the third draft of 2025-03-11 made such policies optional. The Hugging Face guide reads the Commission's guidelines as still allowing narrow, safety-oriented use limits inside a qualifying license. The two readings are filed among the [[other-fragmentary|residual disputes]], since they fit no single theme.

The **OpenMDW review** shows a license that may clear the EU bar while stalling at the OSI. The [[openmdw-1-1-nvidia-adoption|Linux Foundation's announcement]] of version 1.1 says NVIDIA will adopt it for four model families. On the OSI list, Pamela Chestek called its rights-clearing duty "an impossibility generally," and Richard Fontana judged its termination clause too broad. The Linux Foundation's Mike Dolan defended that clause as symmetry. Jonathan Corbet concludes that the OSI does not appear ready to approve it, and the EU guide's authors judge that the Act's license definition likely covers it.

The **fully open builders** supply the counter-example to weights-only releases. [[hello-olmo-truly-open-llm|Ai2's OLMo 7B]] shipped with its pretraining data, training code and evaluation suite. EleutherAI offers its Comma models as evidence for the Common Pile, and executive director Stella Biderman calls "the common idea that unlicensed text drives performance" unjustified. [[open-future-osaid-step-forward|Open Future's Alek Tarkowski and Paul Keller]] argue instead that open resources lack the volume and diversity to train large models. That exchange feeds [[open-training-data-requirement|the training-data dispute]].

- **The label-setter's latitude** — Luis Villa warned in 2024 that Zuckerberg "is going to tell us all what he thinks 'open' means." Zuckerberg's [[zuckerberg-superintelligence-not-all-open-source|2025 "personal superintelligence" letter]] warned that Meta must be "careful about what we choose to open source," and a Meta spokesperson said its stance on open source was unchanged while it would train both open and closed models. Releasing [[meta-muse-glimmer-apache-2-0|Muse Glimmer]] under Apache 2.0 in 2026, Zuckerberg wrote that "Meta is a strong supporter of open source." VentureBeat notes that Meta did not release the model's training data or training code. The clash is traced at [[llama-open-source-label|the Llama label dispute]].
- **A judge without enforcement** — [[euronews-meta-open-source-ai-not-all-it-seems|Maffulli told Euronews]] that Meta's terms of use and distribution fail open source principles. Euronews also reports that the OSI has no strong power to enforce its definition. Critics who want that definition repealed are gathered at [[osaid-form-and-legitimacy|the definition-legitimacy dispute]].
- **Advocacy coalitions** — [[Mozilla]], EleutherAI and Hugging Face asked California legislators in [[mozilla-eleutherai-hf-sb-1047-letter|their Senate Bill 1047 letter]] to widen the bill's open-source definition to take in "the spectrum of openly available AI." In 2026 all three signed the letter defending [[OpenWeights|open weights]].
- **License proliferation** — Danish Contractor and colleagues found that 28% of models on Hugging Face use RAIL (Responsible AI Licenses), which restrict specific uses. Ai2 developed ImpACT Licenses that limit redistribution by risk. Villa warned that incompatible "open-ish" licenses could undo open source's frictionless collaboration.

## Key Trends & Figures

**The EU rules run on a fixed timetable**
- 2025-07-31: the Commission announces its GPAI guidelines, with an indicative threshold of 10^23 FLOPs (floating-point operations) of training compute.
- 2025-08-02: GPAI obligations apply; models already on the market have until 2027-08-02.
- The guide puts the systemic-risk presumption at 10^25 FLOPs and says no open-source model yet sits above it.
- A modifier becomes a provider once its modification compute exceeds one-third of the original training compute, a rule that reaches [[FineTuning|fine-tuning]].
- 2026-08-02: the Commission's enforcement powers over GPAI providers enter into application, on the date its 2025 announcement set.

**The EU guide backed OpenMDW before version 1.1 shipped**
- 2025: the Linux Foundation and the PyTorch Foundation launch OpenMDW, whose contributors include Amazon, Meta, IBM, Microsoft and Nvidia.
- 2025-08-04: the EU guide expects OpenMDW to qualify as free and open-source, alongside Apache 2.0 and MIT.
- 2026-05-28: OpenMDW-1.1 covers architecture, weights, code, documentation and data under one permissive grant.

**Fully open releases now reach 70B parameters**
- 2024-02-01: Ai2 releases four 7B-scale OLMo variants, each trained to at least 2T tokens.
- 2025-06-06: EleutherAI's Common Pile v0.1 reaches 8 terabytes after about two years of work; two 7-billion-parameter Comma models trained on part of it.
- 2025-09-02: Apertus ships in 8B and 70B sizes, trained on 15 trillion tokens across more than 1,000 languages.

**Coalitions and license counts**
- 2024-03: the OSI's definition group numbers about 70 researchers, lawyers, policymakers, activists and company representatives.
- 2024-08-08: Mozilla, EleutherAI and Hugging Face send their letter on Senate Bill 1047; the bill passes the California legislature on 2024-08-29.
- 2026-08-03: the [[open-weights-american-ai-leadership|open weights letter]] counts more than 270 signing organizations.

## Adjacent Domains & Scope

- [[open-source-ai-definition|Open-Source AI Definition]] — holds the OSI's definition, its training-data and legitimacy disputes, and the open-washing charge. This grouping covers only the rules and institutions that give the definition force, such as the EU exemption and the OSI's license review.
- [[open-weights|Open Weights]] — holds the vendor releases, their licenses and the safety fight over published weights. This grouping covers the fully open builders set against those releases and the licenses offered to replace custom terms.

<!-- AUTO:MEMBERS BEGIN -->
## Key Members (auto-extracted, top 15 by intra-cluster connectivity)

**Entities** (6)
- [[LinuxFoundation]]
- [[Ai2]]
- [[MarkZuckerberg]]
- [[EleutherAI]]
- [[HuggingFace]]
- [[StefanoMaffulli]]

**Concepts** (2)
- [[OpenMDW]]
- [[EUAIAct]]
<!-- AUTO:MEMBERS END -->

<!-- AUTO:SOURCES BEGIN -->
## Sources

5 total — see [Open-Model Governance catalog](../sources/_catalog-open-model-governance.md).

Top 5 by weight:
- [[eleutherai-common-pile-dataset]] _(w=0.40)_
- [[tech-industry-open-source-ai-definition-problem]] _(w=0.36)_
- [[apertus-fully-open-multilingual-llm]] _(w=0.33)_
- [[eu-ai-act-gpai-guide-open-source-developers]] _(w=0.33)_
- [[open-weights-not-open-source-label-dispute]] _(w=0.31)_
<!-- AUTO:SOURCES END -->
