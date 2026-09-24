---
title: "Open Weights"
type: overview
tags: []
cluster: open-weights
sources: [anthropic-position-open-weights-models, deepseek-r1-release, joint-statement-ai-safety-openness, llama-2-meta-microsoft, llama-3-1-community-license, mistral-ai-non-production-license, ntia-open-model-weights-report, open-source-ai-models-how-open, open-source-ai-path-forward, open-source-ai-uniquely-dangerous, open-weight-models-frontier-safety-gap, open-weights-american-ai-leadership, openmdw-1-1-nvidia-adoption, red-hat-open-source-ai-point-of-view, rethinking-open-source-generative-ai, senators-question-meta-llama-leak, societal-impact-open-foundation-models, welcome-gpt-oss-openai, osi-meta-llama-2-license-not-open-source, osi-meta-llama-license-still-not-open-source, osi-open-weights-good-open-source-better, osi-open-source-ai-definition, hello-olmo-truly-open-llm]
last_updated: 2026-09-24
---

# Open Weights

## Overview

[[OpenWeights|Open weights]] means publishing a model's trained parameters while keeping its [[TrainingData|training data]] and training code private. [[Meta]] shipped [[llama-2-meta-microsoft|Llama 2]] that way in 2023, and [[DeepSeek]] put [[deepseek-r1-release|R1]] under the MIT License in 2025-01. [[OpenAI]]'s [[welcome-gpt-oss-openai|gpt-oss family]] followed in 2025-08 under Apache 2.0. Meta and DeepSeek call such releases open source, while the OSI ([[OpenSourceInitiative|Open Source Initiative]]) files open weights as a separate category that falls short of it.

The weights are the part a user can run on its own hardware, [[FineTuning|fine-tune]] on private data or [[Distillation|distill]] into a smaller model, as [[open-source-ai-path-forward|Mark Zuckerberg's 2024 letter]] stresses. Both sides of the 2026 policy fight over open weights also accept that released weights cannot be recalled. The cluster pairs releasers such as Meta, DeepSeek, OpenAI and [[MistralAI|Mistral AI]] with [[HuggingFace|Hugging Face]], the hosting venue that recurs across the sources. [[Anthropic]] enters as the frontier lab arguing the risk side. The sources run from [[senators-question-meta-llama-leak|a 2023 report on a Senate letter]] over the LLaMA leak to [[osi-open-weights-good-open-source-better|a 2026 OSI blog post]].

18 of the 27 sources in this cluster's catalog are grouped primarily here. Half of those 18 are statements by model developers or their partners, and only two are academic papers. The evidence base is therefore mostly `[analysis]`-grade, and its `[fact]`-grade claims rest on license texts, release specifications and a few measured evaluations. Two layers sit under every release. The first is component completeness. The [[open-source-ai-models-how-open|Hunton legal primer]] notes that users can fine-tune an open-weights model, but without its training data and algorithms they cannot fully understand or reproduce it, biases included. The second is the license, which runs from MIT and Apache 2.0 grants to custom terms such as the [[llama-3-1-community-license|Llama 3.1 Community License]] and Mistral AI's [[mistral-ai-non-production-license|non-commercial license]]. [[ModelLicensing|Model licensing]] is where this cluster meets the [[OpenSourceAI|open-source AI]] definition fight and its [[OpenWashing|open-washing]] charges.

The first of two tension axes is **openness as a safeguard vs release as an irreversible risk**. The [[open-weights-american-ai-leadership|open weights letter]] concedes that released weights leave the developer's control, yet answers with broad outside scrutiny. [[anthropic-position-open-weights-models|Anthropic CEO Dario Amodei]] asks instead that every sufficiently capable model, open or closed, be [[AISafety|safety]]-tested before release. [[open-weight-models-frontier-safety-gap|TechCrunch reports]] that safeguards Z.ai applies at its API do not travel with downloaded weights. The second axis is **the vendor's release label vs a license-and-completeness test**. Meta applies "open source" to weights-only releases, and Zuckerberg's letter claims Llama is "leading on openness, modifiability, and cost efficiency," which is Meta's ground for the label. The OSI and [[rethinking-open-source-generative-ai|the FAccT (ACM Conference on Fairness, Accountability, and Transparency) openness survey]] instead measure licenses and withheld components. Meta's reply to the OSI, that "There is no single open source AI definition," is traced at [[llama-open-source-label|the Llama label dispute]]. Whether mandatory testing or [[openmdw-1-1-nvidia-adoption|permissive model licenses]] settle either axis is the question the 2026 sources leave open.

## Recent Changes

- 2026-09-16 — [[osi-open-weights-good-open-source-better|An OSI blog post]] argues that open weights beat closed models but still fall short of open-source AI, since users cannot fully study them. [[OpenSourceInitiative]]
- 2026-08-04 — [[open-weight-models-frontier-safety-gap|TechCrunch reports]] a SaferAI finding that an open-weight model from Z.ai refused none of the offensive cyber or biology tasks it was given. [[AISafety]]
- 2026-07-27 — [[anthropic-position-open-weights-models|Dario Amodei writes]] that Anthropic has never advocated a ban on open-weights models, while calling for mandatory pre-release safety testing. [[Anthropic]]
- 2026-07-24 — [[open-weights-american-ai-leadership|An open letter]] on a Microsoft page asks policymakers not to prohibit open weights or restrict distillation; Meta, OpenAI and Mistral are among its signatories. [[Distillation]]

## Key Entities & Concepts

- **Releasers** — [[Meta]] bills Llama as open source, and [[DeepSeek]] calls R1 a "fully open-source model." [[OpenAI]]'s gpt-oss arrives under an "open-source" headline on its partner's blog, whose body calls it an open-weights release. [[MistralAI|Mistral AI]] splits its catalog between Apache 2.0 releases and the non-commercial MNPL ([[mistral-ai-non-production-license|Mistral AI Non-Production License]]), and says the openness debate is being used to entrench incumbents.
- **Distribution venue** — [[HuggingFace|Hugging Face]] hosts Llama 2 and the gpt-oss models, and David Evan Harris notes it also hosts "Llama 2 Uncensored." Its CEO, Clem Delangue, makes the defensive-security case for open weights.
- **Frontier lab on the risk side** — [[Anthropic]] says it has never sought a ban, but its CEO argues open weights potentially carry higher misuse risk than closed models.
- **Judges of the label** — the [[OpenSourceInitiative|OSI]] and its former executive [[StefanoMaffulli|Stefano Maffulli]] reject Llama's "open source" billing, and the OSI endorses a [[FreeSoftwareFoundation|Free Software Foundation]] evaluation of the Llama 3.1 license. The Radboud researchers Andreas Liesenfeld and Mark Dingemanse grade releases on 14 dimensions.
- **Government voices** — the U.S. NTIA ([[ntia-open-model-weights-report|National Telecommunications and Information Administration]]) advises monitoring rather than restricting weights. Senators Richard Blumenthal and Josh Hawley questioned the 2023 LLaMA leak.
- **Anchor concepts** — [[OpenWeights|Open weights]] is the release posture and [[FineTuning|fine-tuning]] the capability it unlocks. [[Distillation]] is the technique the 2026 policy fight turns on, [[ModelLicensing|model licensing]] the layer of terms, and [[AISafety|AI safety]] the axis of the risk dispute.

## Subtopics

The **weights-without-data bargain** is the cluster's core. The [[open-source-ai-models-how-open|Hunton primer]] classes [[DeepSeek]] R1 as open weights because its weights are public but its [[TrainingData|training data]] is not. It says the category seems to strike a balance that works for some providers and users this early in LLM development. [[osi-open-weights-good-open-source-better|The OSI's 2026 post]] calls open weights a real improvement over closed models, but holds that only full [[OpenSourceAI|open-source AI]] grants all four freedoms. [[red-hat-open-source-ai-point-of-view|Red Hat CTO Chris Wright]] sets the bar lower, at openly licensed weights plus open software, arguing training data alone does not fit the "preferred form" for modification. The OSI post points to [[hello-olmo-truly-open-llm|Ai2's OLMo]], shipped with its pretraining data and training code. The data question itself is argued at [[open-training-data-requirement|the open training-data dispute]].

The **custom-license problem** is where the release label and the license part ways. The [[llama-3-1-community-license|Llama 3.1 license]] grants a royalty-free right to modify and redistribute. It also requires a "Built with Llama" notice and compliance with an Acceptable Use Policy, and it withholds the grant from licensees above 700 million monthly active users. [[osi-meta-llama-2-license-not-open-source|The OSI's 2023 post]] ruled the Llama 2 license not open source under points 5 and 6 of the [[OpenSourceDefinition|Open Source Definition]].

[[osi-meta-llama-license-still-not-open-source|The OSI's 2025 follow-up]] says Llama 3.x still fails, and that newer terms exclude people in the European Union. Among the Llama sources, the two OSI posts and the FAccT survey each carry a `contradicts:` citation against [[Meta]], while Meta's own announcements quote no outside judge. The label clash is traced at [[llama-open-source-label|the Llama open-source label dispute]], and [[open-source-ai-every-camp-standard|a cross-camp synthesis]] tests which releases pass the stricter bar.

The **irreversibility dispute** turns on one fact both sides accept: published weights cannot be withdrawn. [[open-source-ai-uniquely-dangerous|David Evan Harris]] cites "Llama 2 Uncensored" as proof that safeguards can be stripped, and proposes pausing new unsecured releases. The [[joint-statement-ai-safety-openness|Joint Statement on AI Safety and Openness]], hosted by [[Mozilla]], calls openness "an antidote, not a poison." [[societal-impact-open-foundation-models|Sayash Kapoor and 24 co-authors]] find current research insufficient to characterize open models' marginal misuse risk. The full exchange sits at [[open-weights-safety-tradeoff|the open-weights safety dispute]].

The **policy response** moved from a leak to talk of a ban. In 2023 [[senators-question-meta-llama-leak|the senators]] questioned Meta's "unrestrained and permissive" LLaMA distribution, and every expert VentureBeat quoted defended open release. [[ntia-open-model-weights-report|NTIA]] later recommended against immediately restricting open weights while building capacity to monitor them. In 2026 [[anthropic-position-open-weights-models|Amodei's post]] answered reports that US officials were weighing a ban on US companies using Chinese open-weights models. He argues such bans miss his main concerns, and backs chip controls, a distillation crackdown and mandatory testing instead.

- **Distillation as a policy lever** — [[deepseek-r1-release|DeepSeek]] released six models distilled from R1 and licensed R1's outputs for [[Distillation|distillation]]. The [[open-weights-american-ai-leadership|open weights letter]] opposes sweeping restrictions on the technique, and Amodei urges a crackdown on industrial-scale distillation operations.
- **Fine-tuning cuts both ways** — [[welcome-gpt-oss-openai|Hugging Face's gpt-oss post]] documents [[FineTuning|fine-tuning]] support, and Wright says most community improvements come that way. [[open-weight-models-frontier-safety-gap|TechCrunch]] reports that the same capability lets self-hosters strip safeguards the API enforced.
- **License families** — the Hunton primer traces [[ModelLicensing|model licensing]] to software's permissive MIT, BSD (Berkeley Software Distribution) and Apache 2.0 licenses and its copyleft GPL (General Public License) family, Affero GPL included, all of which cover only the software. The Linux Foundation's [[openmdw-1-1-nvidia-adoption|OpenMDW-1.1]] instead puts weights, code, documentation and data under one permissive grant — the opposite pole from [[MistralAI|Mistral AI]]'s non-commercial MNPL.
- **Cost as a driver** — the Hunton primer says open models spare users licensing fees and training from scratch, and relays claims that R1 cost roughly $6 million to train. [[open-source-ai-path-forward|Zuckerberg's Llama 3.1 letter]] claims inference at roughly 50% of the cost of closed models such as GPT-4o.

## Key Trends & Figures

**Major weight releases arrive under an "open source" label**
- 2023-07: [[llama-2-meta-microsoft|Llama 2]] released free for research and commercial use, with [[OpenWeights|weights]] and starting code; [[Meta]] reports over 100,000 access requests for Llama 1.
- 2024-07-23: Llama 3.1 405B, which [[open-source-ai-path-forward|Zuckerberg]] calls "the first frontier-level open source AI model."
- 2025-01: [[DeepSeek]] R1 under MIT, which [[open-source-ai-models-how-open|Hunton]] classes as open weights; reported to have cost roughly $6 million to train.
- Hunton also counts Mistral AI's Pixtral Large, xAI's Grok-1 and Alibaba's Qwen 3 as open weights; none has a source page here.
- 2025-08-05: [[OpenAI]]'s gpt-oss-120b (117B parameters) and gpt-oss-20b (21B) under Apache 2.0, welcomed by [[HuggingFace|Hugging Face]].

**License terms run from permissive to restricted**
- The [[llama-3-1-community-license|Llama 3.1 license]], a custom [[ModelLicensing|model license]], requires a separate grant for licensees above 700 million monthly active users.
- 2024-05-29: [[mistral-ai-non-production-license|Mistral AI]] launches the MNPL, with Codestral its first model; [[MistralAI|the firm]]'s other releases stay on Apache 2.0.
- 2026-05-28: the Linux Foundation releases [[openmdw-1-1-nvidia-adoption|OpenMDW-1.1]] for AI model distributions, and NVIDIA plans to adopt it for four open model families.

**Openness audits rank weights-only releases low**
- The [[rethinking-open-source-generative-ai|FAccT survey]] scores 40 text and 6 text-to-image generators on 14 dimensions.
- It finds roughly the bottom third of text generators share only weights, and rates only BloomZ as substantially [[OpenSourceAI|open source]].
- It places Meta, Google, Cohere, Microsoft and Mistral in the lower ranks, and argues Meta and Mistral drag down average openness because smaller players build on their weights.
- 2024-10-28: the OSI's [[osi-open-source-ai-definition|Open Source AI Definition (OSAID) 1.0]] launches with [[hello-olmo-truly-open-llm|OLMo]] among the models that passed its validation phase and Llama 2 among those that did not; the [[OpenSourceInitiative|OSI]] says these results are not certifications and that it will not review individual AI systems.

**Two openness coalitions and the first measured risk result**
- The [[joint-statement-ai-safety-openness|Joint Statement]], hosted by [[Mozilla]], links 1821 signatures, including staff listed with Meta, Mistral AI and Hugging Face.
- The [[open-weights-american-ai-leadership|open weights letter]] counts more than 270 signing organizations by 2026-08-03, OpenAI and NVIDIA among them.
- 2026-08-04: SaferAI places Z.ai's [[open-weight-models-frontier-safety-gap|GLM-5.2]] only a few months behind OpenAI and [[Anthropic]] frontier models on cyber and biology tasks.

## Adjacent Domains & Scope

- [[open-source-ai-definition|Open-Source AI Definition]] — sets the OSI standard, hosts the training-data dispute that weights-only releases fall short of, and carries the open-washing concept and the EU AI Act's treatment of openly licensed models. This cluster covers the vendor releases those standards, charges and exemptions apply to, with their licenses and their risk, not the definition's drafting.

<!-- AUTO:MEMBERS BEGIN -->
## Key Members (auto-extracted, top 15 by intra-cluster connectivity)

**Entities** (6)
- [[Meta]]
- [[OpenAI]]
- [[DeepSeek]]
- [[HuggingFace]]
- [[MistralAI]]
- [[Anthropic]]

**Concepts** (5)
- [[OpenWeights]]
- [[ModelLicensing]]
- [[FineTuning]]
- [[Distillation]]
- [[AISafety]]
<!-- AUTO:MEMBERS END -->

<!-- AUTO:SOURCES BEGIN -->
## Sources

27 total — see [Open Weights catalog](../sources/_catalog-open-weights.md).

Top 15 by weight:
- [[anthropic-position-open-weights-models]] _(w=1.00)_
- [[llama-3-1-community-license]] _(w=1.00)_
- [[societal-impact-open-foundation-models]] _(w=1.00)_
- [[deepseek-r1-release]] _(w=0.86)_
- [[llama-2-meta-microsoft]] _(w=0.83)_
- [[open-source-ai-path-forward]] _(w=0.83)_
- [[senators-question-meta-llama-leak]] _(w=0.83)_
- [[open-weight-models-frontier-safety-gap]] _(w=0.71)_
- [[open-weights-american-ai-leadership]] _(w=0.71)_
- [[ntia-open-model-weights-report]] _(w=0.67)_
- [[mistral-ai-non-production-license]] _(w=0.67)_
- [[welcome-gpt-oss-openai]] _(w=0.62)_
- [[joint-statement-ai-safety-openness]] _(w=0.57)_
- [[open-source-ai-models-how-open]] _(w=0.57)_
- [[red-hat-open-source-ai-point-of-view]] _(w=0.57)_
<!-- AUTO:SOURCES END -->
