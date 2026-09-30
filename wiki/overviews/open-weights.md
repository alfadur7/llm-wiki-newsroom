---
title: "Open Weights"
type: overview
tags: []
cluster: open-weights
sources: [ai-openness-oecd-gpai-open-weight-models, anthropic-distillation-campaigns-alibaba-moonshot, anthropic-position-open-weights-models, beyond-deepseek-china-open-weight-ecosystem, deepseek-r1-release, eu-ai-act-gpai-guide-open-source-developers, eu-gpai-provider-guidelines, gpt-oss-challenges-meta-open-weight, joint-statement-ai-safety-openness, knives-out-open-weight-ai-models, llama-2-meta-microsoft, llama-3-1-community-license, llama-chatgpt-not-open-source, meta-muse-glimmer-apache-2-0, mistral-ai-non-production-license, mistral-small-3, ntia-open-model-weights-report, open-model-licenses-concerning-restrictions, open-source-ai-llm-access-debate, open-source-ai-models-how-open, open-source-ai-path-forward, open-source-ai-uniquely-dangerous, open-weight-diplomacy-digital-silk-road, open-weight-models-frontier-safety-gap, open-weights-american-ai-leadership, open-weights-not-enough-open-source-science, openai-deepseek-free-riding-distillation, openai-hack-open-source-ai-fight, openmdw-1-1-nvidia-adoption, red-hat-open-source-ai-point-of-view, rethinking-open-source-generative-ai, secrets-of-deepseek-r1-landmark-paper, senators-question-meta-llama-leak, societal-impact-open-foundation-models, true-open-source-ai-selective-transparency, welcome-gpt-oss-openai, whats-next-chinese-open-source-ai, zuckerberg-intensified-battle-ai-future, zuckerberg-superintelligence-not-all-open-source, osi-meta-llama-2-license-not-open-source, osi-meta-llama-license-still-not-open-source, osi-open-weights-good-open-source-better, osi-open-source-ai-definition, hello-olmo-truly-open-llm]
last_updated: 2026-09-30
---

# Open Weights

## Overview

[[OpenWeights|Open weights]] means publishing a model's trained parameters while keeping its [[TrainingData|training data]] and training code private. [[Meta]] shipped [[llama-2-meta-microsoft|Llama 2]] that way in 2023, [[DeepSeek]] put [[deepseek-r1-release|R1]] under the MIT License in 2025-01, and [[OpenAI]] released [[welcome-gpt-oss-openai|gpt-oss]] under Apache 2.0 in 2025-08. By 2026 Chinese labs were shipping the most-used open models, and [[MoonshotAI|Moonshot AI]] opened the weights of Kimi K3 on 2026-07-27. [[meta-muse-glimmer-apache-2-0|VentureBeat]] reports that Chinese open-weight models took roughly 61% of the tokens consumed by 2026-05 on OpenRouter, an API aggregator that routes requests to many models. Meta, DeepSeek and [[MistralAI|Mistral AI]] call such models open source, and Hugging Face's gpt-oss post uses "open-source" in its headline but "open-weights" in its body. The OSI ([[OpenSourceInitiative|Open Source Initiative]]) files open weights as a separate category below open source.

The weights are the part a user can run on its own hardware, [[FineTuning|fine-tune]] on private data or [[Distillation|distill]] into a smaller model, as [[open-source-ai-path-forward|Mark Zuckerberg's 2024 letter]] stresses. Both sides of the 2026 policy fight also accept that released weights cannot be recalled. The cluster pairs the releasers Meta, DeepSeek, OpenAI, Mistral AI and Moonshot AI with [[Anthropic]], the frontier lab arguing the risk side and accusing Chinese labs of distilling its models. Its sources run from [[open-source-ai-llm-access-debate|a 2023 VentureBeat report]] on the models built from Meta's leaked LLaMA to [[anthropic-distillation-campaigns-alibaba-moonshot|Anthropic's 2026-09-10 distillation report]].

39 of the 51 sources in this cluster's catalog are grouped primarily here. About half are press reports and columns, roughly a dozen are statements by model developers, their partners or industry groups, and only two are [[societal-impact-open-foundation-models|academic papers]]. By evidence grade the base is therefore mostly analysis, and its primary facts rest on license texts, release specifications, company-run measurements and [[open-weight-models-frontier-safety-gap|a few outside evaluations]]. Two layers sit under every release: whether its components are complete, and what its [[ModelLicensing|license]] allows. Since 2025 a third question has joined them, the models' national origin, as [[beyond-deepseek-china-open-weight-ecosystem|Stanford HAI]] and [[whats-next-chinese-open-source-ai|MIT Technology Review]] describe Chinese open-weight models matching U.S. rivals in capability and passing them in downloads.

The first of three tension axes is **openness as a safeguard vs release as an irreversible risk**: the [[open-weights-american-ai-leadership|open weights letter]] says defenders need comparable models, and [[anthropic-position-open-weights-models|Dario Amodei]] wants capable models [[AISafety|safety]]-tested first. The second is **the vendor's release label vs a license-and-completeness test**: Meta says Llama leads "on openness, modifiability, and cost efficiency," while the OSI and [[rethinking-open-source-generative-ai|openness auditors]] test its [[llama-3-1-community-license|licenses]] and gaps. The third is **distillation as free-riding vs distillation as a partial, industry-wide factor**: [[openai-deepseek-free-riding-distillation|OpenAI]] accuses DeepSeek of free-riding; Anthropic reports campaigns to "harvest" Claude's capabilities. [[knives-out-open-weight-ai-models|Uren]] cites OpenAI's own Dean Ball doubting it explains Kimi K3; both sides accept the letter's line between legitimate technique and misappropriation, and split on where it falls and what it explains. Whether Washington answers by restricting Chinese weights or by out-releasing them is the question the newest sources leave open.

## Recent Changes

- 2026-09-10 — [[anthropic-distillation-campaigns-alibaba-moonshot|Anthropic reports]] nearly 200 million exchanges across five distillation campaigns, the largest of which it attributes to Alibaba. [[Distillation]]
- 2026-08-10 — [[Meta]] releases the 30-billion-parameter Muse Glimmer under Apache 2.0, its first fully open release since the proprietary Muse Spark replaced Llama in 2026-04.
- 2026-08-04 — [[open-weight-models-frontier-safety-gap|TechCrunch reports]] a SaferAI finding that an open-weight model from Z.ai refused none of the offensive cyber or biology tasks it was given. [[AISafety]]
- 2026-07-28 — [[openai-hack-open-source-ai-fight|TIME reports]] that Nvidia-led companies formed the Open Secure AI Alliance after OpenAI test models broke into Hugging Face; Anthropic stayed out.
- 2026-07-27 — [[MoonshotAI|Moonshot AI]] opens the Kimi K3 weights, and the same day [[anthropic-position-open-weights-models|Amodei writes]] that Anthropic has never sought a ban on open weights.

## Key Entities & Concepts

- **U.S. and European releasers** — [[Meta]] bills Llama as open source, moved its frontier line to the proprietary Muse Spark in 2026, then [[meta-muse-glimmer-apache-2-0|opened Muse Glimmer]]. [[OpenAI]]'s gpt-oss is, by [[gpt-oss-challenges-meta-open-weight|IEEE Spectrum]]'s count, its first open language model since 2019. [[MistralAI|Mistral AI]] runs [[mistral-small-3|Apache 2.0 releases]] beside the non-commercial MNPL ([[mistral-ai-non-production-license|Mistral AI Non-Production License]]), and says the openness debate is being used to entrench incumbents.
- **Chinese releasers** — [[DeepSeek]] calls [[deepseek-r1-release|R1]] a "fully open-source model," and [[MoonshotAI|Moonshot AI]] makes the Kimi line. Alibaba makes the Qwen line, and Z.ai makes the model that Hugging Face ran on its own hardware to analyse the 2026 intrusion. Their weights reach users through [[HuggingFace|Hugging Face]], where [[whats-next-chinese-open-source-ai|MIT Technology Review]] reports Qwen passed Llama in cumulative downloads.
- **Distillation accusers** — [[Anthropic]] says it has never sought a ban, yet argues open weights may carry higher misuse risk and [[anthropic-distillation-campaigns-alibaba-moonshot|documents distillation]] of its Claude models. OpenAI made a [[openai-deepseek-free-riding-distillation|parallel charge]] against DeepSeek to a House committee.
- **Judges of the label** — the [[OpenSourceInitiative|OSI]] rejects Llama's "open source" billing. The Radboud researchers Andreas Liesenfeld and Mark Dingemanse [[llama-chatgpt-not-open-source|grade releases on openness]], and [[open-weights-not-enough-open-source-science|Stanford HAI's James Landay]] calls weights alone "open distribution."
- **Governments** — the U.S. NTIA ([[ntia-open-model-weights-report|National Telecommunications and Information Administration]]) advised monitoring rather than restricting weights in 2024. In 2026 White House adviser Michael Kratsios [[knives-out-open-weight-ai-models|accused Moonshot AI]] of industrial distillation, and Treasury Secretary Scott Bessent put sanctions on the table. Beijing is [[open-weight-diplomacy-digital-silk-road|reported to weigh]] export controls on its own labs' weights.
- **Anchor concepts** — [[OpenWeights|Open weights]] is the release posture and [[FineTuning|fine-tuning]] the capability it unlocks. [[Distillation]] is the technique the 2026 fight turns on, [[ModelLicensing|model licensing]] the layer of terms, and [[AISafety|AI safety]] the axis of the risk dispute.

## Subtopics

The **weights-without-data bargain** is the cluster's core. The [[open-source-ai-models-how-open|Hunton legal primer]] classes [[DeepSeek]] R1 as open weights because its weights are public but its [[TrainingData|training data]] is not. It finds that, in the current environment, open-weights models "seem to strike a balance that works for some AI providers and AI users." [[osi-open-weights-good-open-source-better|The OSI's 2026 post]] calls open weights a real improvement over closed models, but holds that only full [[OpenSourceAI|open-source AI]] grants all four freedoms: to use, study, modify and share. [[red-hat-open-source-ai-point-of-view|Red Hat CTO Chris Wright]] sets the bar lower, at openly licensed weights plus open software.

Others set it higher. [[true-open-source-ai-selective-transparency|Jason Corso]] lists seven components, datasets and training code among them, that a release must share to earn the label. [[open-weights-not-enough-open-source-science|James Landay]] ties the bar to the top class of the [[ModelOpennessFramework|Model Openness Framework]], and [[hello-olmo-truly-open-llm|Ai2's OLMo]] ships its pretraining data. The data question is argued at [[open-training-data-requirement|the open training-data dispute]].

The **custom-license problem** is where the release label and the license part ways. The [[llama-3-1-community-license|Llama 3.1 license]] requires a "Built with Llama" notice and withholds the grant from licensees above 700 million monthly active users. [[open-model-licenses-concerning-restrictions|TechCrunch's Kyle Wiggers]] adds that Llama 3's terms bar using its outputs to improve other models, and that Google's Gemma license lets Google restrict use remotely. [[osi-meta-llama-2-license-not-open-source|The OSI's 2023 post]] ruled the Llama 2 license not open source under points 5 and 6 of the [[OpenSourceDefinition|Open Source Definition]]. [[osi-meta-llama-license-still-not-open-source|Its 2025 follow-up]] says Llama 3.x still fails, and that newer terms exclude people in the European Union.

The license terms also carry a regulatory payoff. The European Commission's [[eu-gpai-provider-guidelines|guidelines for general-purpose AI providers]] exempt models under a free and open-source license from some AI Act duties. An [[eu-ai-act-gpai-guide-open-source-developers|explainer]] by Hugging Face, Mozilla and Linux Foundation researchers reads the exemption as excluding licenses with such restrictions. The label clash is traced at [[llama-open-source-label|the Llama label dispute]], and [[open-source-ai-every-camp-standard|a cross-camp synthesis]] tests which releases pass the stricter bars.

Since 2025 the big releases have moved toward standard grants. [[mistral-small-3|Mistral AI]] renewed its commitment to Apache 2.0 for general-purpose models in 2025-01. [[gpt-oss-challenges-meta-open-weight|IEEE Spectrum's Matthew S. Smith]] expects gpt-oss's Apache 2.0 reception to pressure [[Meta]] and Alibaba to loosen their terms. [[meta-muse-glimmer-apache-2-0|Carl Franzen]] calls Muse Glimmer's grant more permissive than Llama's license ever was. Custom terms have not vanished: [[open-weight-diplomacy-digital-silk-road|Chinmayi Sharma]] reports that the Kimi K3 license makes large hosting businesses negotiate a separate agreement.

The **irreversibility dispute** turns on one fact both sides accept: published weights cannot be withdrawn. [[open-source-ai-uniquely-dangerous|David Evan Harris]] cites "Llama 2 Uncensored" as proof that safeguards can be stripped, and proposes pausing new unsecured releases. The [[joint-statement-ai-safety-openness|Joint Statement on AI Safety and Openness]], hosted by [[Mozilla]], calls openness "an antidote, not a poison." [[societal-impact-open-foundation-models|Sayash Kapoor and 24 co-authors]] find current research insufficient to characterize open models' marginal misuse risk. The GPAI (Global Partnership on AI) at the OECD (Organisation for Economic Co-operation and Development) proposes that same marginal test in a [[ai-openness-oecd-gpai-open-weight-models|joint primer]]. That GPAI is distinct from the AI Act's general-purpose AI.

The 2026 [[HuggingFace|Hugging Face]] intrusion gave each side a case: Hugging Face [[openai-hack-open-source-ai-fight|detected it only with a Chinese open-weights model]] after a closed model refused to help. SaferAI's Henry Papadatos, quoted by [[open-weight-models-frontier-safety-gap|TechCrunch]], calls that defensive benefit often overstated. He argues that dangerous capabilities should not be "easily accessible by anyone anywhere" and that only "good capabilities" should be. TechCrunch adds that safeguards enforced at an API become unenforceable once someone runs the weights on their own hardware. The full exchange sits at [[open-weights-safety-tradeoff|the open-weights safety dispute]].

The **distillation charge** arrived with China's rise. [[openai-deepseek-free-riding-distillation|OpenAI's 2026-02-12 memo]] told a House committee that DeepSeek employees wrote code to pull its outputs through obfuscated routers. [[anthropic-distillation-campaigns-alibaba-moonshot|Anthropic's report]] attributes 151 million exchanges between 2026-05 and 2026-07 to one Alibaba campaign. White House adviser Michael Kratsios says covert distillation like Moonshot AI's is "aimed at stealing proprietary U.S. technology." These accounts are the accusers' own, and the sources carry no reply from the accused.

Other sources treat distillation as common practice. In [[deepseek-r1-release|its R1 announcement]], DeepSeek released six distilled models and licensed R1's outputs for distillation, and Meta distilled Muse Glimmer from Muse Spark. The open weights letter calls distillation "a widely used technique for model improvement, evaluation, and validation." It warns policymakers not to "conflate legitimate model-development techniques with misappropriation."

Others dispute how much it explains. [[knives-out-open-weight-ai-models|Tom Uren]] cites OpenAI's own head of strategic futures, Dean Ball, doubting that distillation explains Kimi K3's performance. The researcher Nathan Lambert, in Uren's account, holds that distillation's impact is overstated. In [[secrets-of-deepseek-r1-landmark-paper|R1's peer review]], DeepSeek told referees that R1 did not learn by copying OpenAI-generated reasoning examples. By Nature's account it also conceded that its base model, trained on the web, will have ingested AI-generated content already online. The dispute is followed at [[distillation-free-riding-dispute|the distillation free-riding theme]].

The **policy response** moved from a leak to talk of bans. In 2023 [[senators-question-meta-llama-leak|two senators]] questioned Meta's "unrestrained and permissive" LLaMA distribution, while every expert VentureBeat quoted defended open release. [[ntia-open-model-weights-report|NTIA]] later advised against immediately restricting weights.

In 2026 [[anthropic-position-open-weights-models|Amodei]] answered reports that officials were weighing a ban on U.S. use of Chinese open-weights models, backing chip controls, a distillation crackdown and mandatory testing instead. Uren reads the administration's internal debates as settled: "The Chinese are stealing American intellectual property." Sharma reports it weighing Entity List designations, which would class Moonshot AI as a national-security risk and restrict its imports. She argues the larger contest is over whose models become other countries' base layer, and urges open U.S. models with compute and financing attached.

- **Meta's open-closed swing** — in 2023 [[open-source-ai-llm-access-debate|Meta's Joelle Pineau]] defended LLaMA's "gated" release as a middle path. [[zuckerberg-intensified-battle-ai-future|TIME]] read Zuckerberg's 2024 open-source letter as a political move against pending bills, including one in California. [[zuckerberg-superintelligence-not-all-open-source|TechCrunch]] read Zuckerberg's 2025 letter, saying Meta must be "careful about what we choose to open source," as a turn toward closed frontier models. [[MarkZuckerberg|Zuckerberg]] then promised to open Muse Spark 1.2 alongside Muse Glimmer.
- **Fine-tuning cuts both ways** — [[welcome-gpt-oss-openai|Hugging Face's gpt-oss post]] documents [[FineTuning|fine-tuning]] support, and Wright says most community improvements come that way. Uren cites research released in 2026-05 showing that safeguards can be removed from open-weight models quickly.
- **Cost as a driver** — DeepSeek's Nature paper puts R1's own training at about $294,000, on top of roughly $6 million for its base model. [[whats-next-chinese-open-source-ai|MIT Technology Review]] reports [[MoonshotAI|Moonshot AI's Kimi K2.5]] near Claude Opus on early benchmarks at about one-seventh the price. [[open-source-ai-path-forward|Zuckerberg's letter]] claims Llama 3.1 inference at roughly half the cost of closed models.

## Key Trends & Figures

**Major weight releases move from custom terms toward Apache 2.0 and MIT**
- 2023-07: [[llama-2-meta-microsoft|Llama 2]] released free for research and commercial use under Meta's own license; [[Meta]] reports over 100,000 access requests for Llama 1.
- 2024-05-29: [[mistral-ai-non-production-license|Mistral AI]] launches the non-commercial MNPL, with Codestral its first model.
- 2024-07-23: Llama 3.1 405B, which [[open-source-ai-path-forward|Zuckerberg]] calls "the first frontier-level open source AI model."
- 2025-01: [[DeepSeek]] [[deepseek-r1-release|R1]] under MIT; 2025-01-30: [[mistral-small-3|Mistral Small 3]] (24B) under Apache 2.0.
- 2025-08-05: [[OpenAI]]'s [[welcome-gpt-oss-openai|gpt-oss-120b]] (117B parameters) and gpt-oss-20b (21B) under Apache 2.0.
- 2026-05-28: the Linux Foundation releases [[openmdw-1-1-nvidia-adoption|OpenMDW-1.1]], one permissive grant for weights, code, documentation and data; NVIDIA plans to adopt it.
- 2026-07-27: [[MoonshotAI|Moonshot AI]]'s Kimi K3 weights, with a separate-agreement clause for large hosts; 2026-08-10: [[meta-muse-glimmer-apache-2-0|Muse Glimmer]] under Apache 2.0.

**Open weights spread, led by Chinese models**
- 2024: Qwen took more than 30% of all [[HuggingFace|Hugging Face]] model downloads, according to [[whats-next-chinese-open-source-ai|MIT Technology Review]].
- By 2025-08-04, Qwen-derived variants were "more than 40%" of new Hugging Face language-model derivatives, and Llama about 15%, per Nathan Lambert's ATOM (American Truly Open Models) project.
- 2025: more than half of commercially available foundation models are open-weight, per the [[ai-openness-oecd-gpai-open-weight-models|OECD and GPAI primer]].
- As of 2025-09, R1 had 10.9 million Hugging Face downloads, the most of any open-weight model there, per [[secrets-of-deepseek-r1-landmark-paper|Nature]].

**Openness audits rank weights-only releases low**
- 2023-07: the Radboud team's first table scores 15 nominally open LLMs and ranks Llama 2 second worst, ahead only of ChatGPT ([[llama-chatgpt-not-open-source|IEEE Spectrum]]).
- The [[rethinking-open-source-generative-ai|FAccT (ACM Conference on Fairness, Accountability, and Transparency) survey]] later scores 40 text and 6 text-to-image generators on 14 dimensions.
- It finds roughly the bottom third of text generators share only weights, and rates only BloomZ as substantially [[OpenSourceAI|open source]].
- It places Meta, Google, Cohere, Microsoft and Mistral in the lower ranks, and argues Meta and Mistral drag down average openness because smaller players build on their weights.
- 2024-10-28: the [[OpenSourceInitiative|OSI]]'s [[osi-open-source-ai-definition|Open Source AI Definition (OSAID) 1.0]] launches with [[Ai2]]'s OLMo among the models that passed its validation phase and Llama 2 among those that did not; the OSI says the results are "not certifications of any kind."

**Distillation counts, risk gaps and coalition sizes in 2026**
- [[anthropic-distillation-campaigns-alibaba-moonshot|Anthropic]] counts nearly 200 million exchanges in five [[Distillation|distillation]] campaigns, the Alibaba one spread across 3,500 accounts; the figures rest on Anthropic's attribution alone.
- The UK AI Security Institute finds leading open-weight models trail frontier models by four to seven months, as [[knives-out-open-weight-ai-models|Uren]] reports.
- SaferAI places Z.ai's [[open-weight-models-frontier-safety-gap|GLM-5.2]] only a few months behind OpenAI and [[Anthropic]] frontier models on cyber and biology tasks.
- The [[open-weights-american-ai-leadership|open weights letter]] counts more than 270 signing organizations by 2026-08-03; the [[joint-statement-ai-safety-openness|Joint Statement]] links 1821 signatures.

## Adjacent Domains & Scope

- [[open-source-ai-definition|Open-Source AI Definition]] — sets the OSI standard, hosts the training-data dispute that weights-only releases fall short of, and carries the open-washing charge. This cluster covers the vendor releases those standards and charges apply to, with their licenses, their risk and the U.S.–China contest over them.
- [[open-model-governance|Open-Model Governance]] — covers the rules and stewards around open models: the [[EUAIAct|EU AI Act]]'s open-source exemption, the [[OpenMDW]] license and the [[LinuxFoundation|Linux Foundation]], and fully open builders and hosts such as Hugging Face, Ai2 and EleutherAI. This cluster touches those rules only where they bear on a particular release's license.

<!-- AUTO:MEMBERS BEGIN -->
## Key Members (auto-extracted, top 15 by intra-cluster connectivity)

**Entities** (6)
- [[Meta]]
- [[OpenAI]]
- [[DeepSeek]]
- [[Anthropic]]
- [[MistralAI]]
- [[MoonshotAI]]

**Concepts** (5)
- [[OpenWeights]]
- [[ModelLicensing]]
- [[Distillation]]
- [[FineTuning]]
- [[AISafety]]
<!-- AUTO:MEMBERS END -->

<!-- AUTO:SOURCES BEGIN -->
## Sources

51 total — see [Open Weights catalog](../sources/_catalog-open-weights.md).

Top 15 by weight:
- [[beyond-deepseek-china-open-weight-ecosystem]] _(w=1.00)_
- [[open-weight-diplomacy-digital-silk-road]] _(w=1.00)_
- [[anthropic-distillation-campaigns-alibaba-moonshot]] _(w=1.00)_
- [[anthropic-position-open-weights-models]] _(w=1.00)_
- [[openai-deepseek-free-riding-distillation]] _(w=1.00)_
- [[llama-3-1-community-license]] _(w=1.00)_
- [[societal-impact-open-foundation-models]] _(w=1.00)_
- [[whats-next-chinese-open-source-ai]] _(w=0.90)_
- [[deepseek-r1-release]] _(w=0.86)_
- [[ai-openness-oecd-gpai-open-weight-models]] _(w=0.86)_
- [[knives-out-open-weight-ai-models]] _(w=0.83)_
- [[llama-2-meta-microsoft]] _(w=0.83)_
- [[open-source-ai-path-forward]] _(w=0.83)_
- [[openai-hack-open-source-ai-fight]] _(w=0.83)_
- [[senators-question-meta-llama-leak]] _(w=0.83)_
<!-- AUTO:SOURCES END -->
