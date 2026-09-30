# Overview

<!-- AUTO:STATS BEGIN -->
This wiki is a knowledge base comprising **66 source documents** (2023~2026), **15 entities**, **12 concepts**, **3 field overviews**, **1 analysis reports**, **0 associative trails**, and **0 timelines**.

Sources are automatically classified into 3 topic clusters via Leiden topology clustering: **Open Weights(51)**, **Open-Model Governance(5)**, **Open-Source AI Definition(39)**. A single source may span multiple clusters (listed in every catalog where its weight is ≥0.3); for the full cluster list and members, see [[index]] or `graph/_clusters.json`.
<!-- AUTO:STATS END -->

This wiki maps the argument over what "open source" should mean for AI models. At its center is the OSI ([[OpenSourceInitiative|Open Source Initiative]]), whose 2024 [[OpenSourceAI|Open Source AI Definition]] drew an endorsement from [[Mozilla]] and a stricter rival test from the [[FreeSoftwareFoundation|Free Software Foundation]]. Around it sit [[OpenWeights|open-weights]] releases from [[Meta]], [[DeepSeek]], [[OpenAI]] and [[MoonshotAI|Moonshot AI]], with the [[ModelLicensing|licenses]] they ship under and the [[OpenWashing|open-washing]] charges they draw. Between the two sit the rules and builders that give the label force: the [[EUAIAct|EU AI Act]], the [[LinuxFoundation|Linux Foundation]]'s [[OpenMDW]] license, and fully open releases from [[Ai2]] and [[EleutherAI]].

By 2026 two older fights had reached the same pitch as the definition dispute. One asks whether published weights serve or threaten [[AISafety|safety]], and brings in [[Anthropic]]. The other asks when [[Distillation|distillation]] of a rival's model becomes theft, a charge US labs and officials level at Chinese labs. [[TrainingData|Training data]] is the component every camp returns to, and nearly two years after the definition the record holds no revision of it.

## Recent Changes

- 2026-09-16 — An OSI blog post by Katie Steen-James sorts AI systems into closed, open-weight and Open Source, placing open weights one rung below the definition. [[OpenSourceInitiative]]
- 2026-09-15 — A Register column quotes former OSI executive director Stefano Maffulli calling the OSI's review of the OpenMDW license "tainted by an ideological bias". [[StefanoMaffulli]]
- 2026-09-10 — Anthropic reports nearly 200 million exchanges across five distillation campaigns against its Claude models, the largest of which it attributes to Alibaba. [[Distillation]]
- 2026-08-21 — LWN (Linux Weekly News) reports that the OSI's list discussion of OpenMDW wound down with no approval in sight. [[OpenMDW]]
- 2026-08-10 — Meta releases the 30-billion-parameter Muse Glimmer under Apache 2.0, without its training data or training code. [[Meta]]
- 2026-08-04 — TechCrunch reports a SaferAI finding that Z.ai's open-weight model refused none of the offensive cyber or biology tasks it was given. [[AISafety]]
- 2026-07-27 — Moonshot AI opens the Kimi K3 weights, and Anthropic CEO Dario Amodei writes that Anthropic has never advocated a ban on open-weights models. [[MoonshotAI]]

## 1. [[open-source-ai-definition|Open-Source AI Definition]]

On 2024-10-28 the OSI published version 1.0 of the OSAID ([[OpenSourceAI|Open Source AI Definition]]), 16 months after a kickoff at [[Mozilla]]'s San Francisco office. The [[osi-open-source-ai-definition|reference text]] makes it a pass/fail test: a system must grant the freedoms to use, study, modify and share it without asking permission. Those freedoms rest on detailed data information, complete code and the model parameters, not on the [[TrainingData|training data]] itself. Mozilla [[mozilla-celebrates-osaid|endorsed the text]] the same day.

The [[OpenSourceInitiative|OSI]] is the steward, and [[StefanoMaffulli|Stefano Maffulli]], then its executive director, was its public voice through the release. [[open-future-osaid-step-forward|Open Future]] accepts the floor but would have reserved "open source" for systems with open data. The data-required critics gather around the FSF ([[FreeSoftwareFoundation|Free Software Foundation]]), joined by OSI co-founder Bruce Perens and a [[debian-ai-models-dfsg|Debian proposal]] by Mo Zhou, [[debian-ai-gr-withdrawn|withdrawn before a vote]] on 2025-05-08. The form critics, such as [[osaid-take-it-or-leave-it|Yaniv Benhamou and Michel Reymond]] of the University of Geneva, prefer graded openness such as the [[ModelOpennessFramework|Model Openness Framework]].

The text drew disputes over substance, form and standing. The OSI's FAQ (frequently asked questions), as [[case-against-osaid|The New Stack]] quotes it, wants open-source AI to exist "in fields where data cannot be legally shared, for example medical AI". The FSF's [[fsf-free-ml-application-criteria|draft criteria]] answer that an application is not free unless its data and processing scripts respect the four freedoms. On standing, Debian developer Sam Johnston notes that the OSI's 10-person board, not its membership, approved the text, and the Software Freedom Conservancy's [[sfc-osaid-erodes-open-source|Bradley M. Kühn]] ran for that board to have it repealed.

The OSI calls its validation results, which failed Llama 2 among others, "not certifications of any kind," and says it "will not validate or review individual AI systems". Its rulings on [[Meta]]'s Llama rest instead on the older OSD ([[OpenSourceDefinition|Open Source Definition]]): a [[osi-meta-llama-2-license-not-open-source|2023 post]] found the Llama 2 license fails its non-discrimination points 5 and 6. A [[osi-meta-llama-license-still-not-open-source|2025 follow-up]] says Llama 3.x still fails, without needing the newer definition. The opposition has outlasted the release: in 2026-09 [[open-weights-not-open-source-label-dispute|The Register]] carried Kühn and Red Hat's Richard Fontana calling for repeal, in a statement it does not date.

Details: [[open-source-ai-definition|the Open-Source AI Definition field]].

## 2. [[open-model-governance|Open-Model Governance]]

On 2025-07-31 the European Commission issued its guidelines for general-purpose AI providers, and on 2026-08-02 its enforcement powers began. That rule, a license seeking the OSI's approval and a set of fully open builders form a bridge between the other two groupings rather than a debate of its own. What they share is the power to make an "open" label count in those neighbors' arguments. Of the wiki's 66 sources, one, [[eleutherai-common-pile-dataset|TechCrunch's report on EleutherAI's Common Pile]], belongs chiefly here and 31 others bear on it; five, that one included, bear closely enough to be catalogued under it.

The rules center on the [[EUAIAct|EU AI Act]]: under the Commission's [[eu-gpai-provider-guidelines|guidelines]], models "released under a free and open-source license" can be spared some GPAI (general-purpose AI) duties. The sources record no enforcement action since the Commission's powers began. A [[eu-ai-act-gpai-guide-open-source-developers|guide by Cailean Osborne and co-authors]], hosted by [[HuggingFace|Hugging Face]], lists three conditions: an open license, public weights and architecture, and no monetization. It states that it is not legal advice, much as the Commission calls its guidelines not legally binding.

The [[LinuxFoundation|Linux Foundation]] asked the OSI to approve [[OpenMDW]], one permissive grant over weights, code, documentation and data that [[openmdw-1-1-nvidia-adoption|NVIDIA plans to adopt]]. On the OSI's list, as [[lwn-openmdw-license-review|LWN reports]], Pamela Chestek called its rights-clearing duty "an impossibility generally," and LWN's Jonathan Corbet concluded that the OSI did not appear ready to approve it. The builders are [[Ai2]], [[EleutherAI]] and the Swiss team behind [[apertus-fully-open-multilingual-llm|Apertus]], who publish data and code to show what a full release looks like. EleutherAI's benchmark results for the Common Pile and Apertus's "fully open" claim are their makers' own, with no outside test in the sources.

Three tensions, each imported from a neighbor, run through the bridge. On legal payoff vs label discipline, the guide's authors welcome the exemption as easing compliance, while [[open-secret-of-open-washing|Steven J. Vaughan-Nichols]] calls the reward an incentive to [[OpenWashing|open-wash]]. On one grant vs who bears risk, the Linux Foundation's Mike Dolan defends OpenMDW's termination clause as symmetry, while OSI reviewers say it puts rights-clearing and litigation risk on recipients. On whether open data suffices, EleutherAI's Stella Biderman rejects "the common idea that unlicensed text drives performance". Open Future's Alek Tarkowski and Paul Keller had argued in 2024 that open resources are too thin for large models.

Details: [[open-model-governance|the Open-Model Governance field]].

## 3. [[open-weights|Open Weights]]

[[OpenWeights|Open weights]] means publishing a model's trained parameters while keeping its training data and training code private. [[Meta]] shipped [[llama-2-meta-microsoft|Llama 2]] that way in 2023-07, [[DeepSeek]] put [[deepseek-r1-release|R1]] under the MIT License in 2025-01, and [[OpenAI]]'s [[welcome-gpt-oss-openai|gpt-oss]] followed in 2025-08 under Apache 2.0. A [[open-source-ai-models-how-open|legal primer]] from the law firm Hunton notes that users can [[FineTuning|fine-tune]] such a model but cannot fully understand or reproduce it, biases included, without its data and algorithms.

The grouping pairs the releasers Meta, DeepSeek, OpenAI, [[MistralAI|Mistral AI]] and [[MoonshotAI|Moonshot AI]] with [[Anthropic]], the frontier lab arguing the risk side and accusing Chinese labs of distilling its models. By 2026 Chinese open-weight models led in use: [[meta-muse-glimmer-apache-2-0|VentureBeat]] reports that they took roughly 61% of the tokens consumed on OpenRouter, a service routing requests to many models, by 2026-05. Of the 51 sources on this grouping, 39 belong chiefly to it; about half are press reports and columns, and only two are academic papers. Its evidence grade is therefore mostly analysis, with facts resting on license texts, release specifications, company-run counts and a few outside evaluations.

Licensing is the layer where the release label and the terms part ways. The [[llama-3-1-community-license|Llama 3.1 Community License]] withholds its grant above 700 million monthly active users and binds use to an Acceptable Use Policy, which Meta defends as a guardrail. Since 2025 the big releases have moved toward standard grants, Meta's own Muse Glimmer among them, though [[open-weight-diplomacy-digital-silk-road|Chinmayi Sharma]] reports that the Kimi K3 license makes large hosts sign a separate agreement. In their [[rethinking-open-source-generative-ai|FAccT '24 survey]] (Conference on Fairness, Accountability, and Transparency), Radboud's Liesenfeld and Dingemanse find roughly the bottom third of text generators share only weights.

On risk, both sides of the safety fight accept that published weights cannot be recalled. The [[open-weights-american-ai-leadership|2026-07-24 open letter]], hosted by Microsoft and signed by more than 270 companies and organizations including Meta, OpenAI and Mozilla, answers with outside scrutiny. [[anthropic-position-open-weights-models|Amodei]] instead asks that every capable model, open or closed, be [[AISafety|safety]]-tested first.

Critics such as [[open-source-ai-uniquely-dangerous|David Evan Harris]] warn that safeguards can be stripped from released weights. SaferAI's test of [[open-weight-models-frontier-safety-gap|Z.ai's GLM-5.2]] is the one measured risk result, and it probed the safeguards Z.ai shipped, not stripped ones. On [[Distillation|distillation]], OpenAI and Anthropic accuse Chinese labs of harvesting their outputs, while [[knives-out-open-weight-ai-models|Tom Uren]] cites OpenAI's head of strategic futures, Dean Ball, doubting it explains Kimi K3's performance.

Details: [[open-weights|the Open Weights field]].

## Cross-Domain Threads

### One word, several judges

Across all three groupings, the label "open source" has no single owner. [[Meta]] applies it to Llama, and its spokesperson told [[techcrunch-osaid-official-definition|TechCrunch]] that "there is no single open source AI definition". [[MarkZuckerberg|Mark Zuckerberg]] kept the claim in 2026, writing at Muse Glimmer's release that "Meta is a strong supporter of open source". Against Meta stand the [[OpenSourceInitiative|OSI]]'s license rulings and the [[FreeSoftwareFoundation|FSF]]'s finding that the Llama 3.1 license fails freedom 0, the freedom to use the model for any purpose.

The record on this is uneven: Meta's side rests on first-person announcements and one spokesperson statement that never answers the clause-by-clause reading of its license. By [[StefanoMaffulli|Maffulli]]'s account, talks with the OSI moved Google and Microsoft off the label but not Meta. The charge now reaches Chinese releases too. In a 2026-07-25 essay written before the release, JJ Jasser [[open-washing-four-criteria|calls Kimi K3]] at best an open-weight model, and calling it open source "a category error."

No party can make its reading stick. Kühn notes that the OSI never secured a trademark on the term, and TechCrunch reports that the OSI has no enforcement mechanism of its own and counts Meta among its funders. After a Sloan Foundation grant of about $250,000 meant to lessen that reliance, Maffulli [[what-does-open-source-ai-mean|told TechCrunch]] the OSI "could say goodbye to Meta's money anytime". The OSI's [[osi-open-weights-good-open-source-better|2026-09-16 post]] sorts systems into closed, open-weight and Open Source, a three-rung ladder with its definition as the only top rung.

### Training data as the fault line

[[TrainingData|Training data]] is the component all three groupings keep returning to. The definition grouping argues over whether it must be released, the weights grouping is defined by withholding it, and the fully open builders publish it. Some critics narrow the objection to the data's legal status: Lightning AI's Luca Antiga says that by neglecting training-data licensing, the OSI leaves "a gaping hole". [[Meta]] calls its handling of training-data details a "cautious approach" while rules such as California's training-transparency law evolve.

Open releases of data exist but stay below frontier scale: [[hello-olmo-truly-open-llm|Ai2's OLMo 7B]] shipped in 2024-02 with its three-trillion-token Dolma corpus and the code that builds it. The largest in the record, [[apertus-fully-open-multilingual-llm|Apertus]], reached 70B parameters in 2025-09, trained on 15 trillion tokens across more than 1,000 languages. A [[open-source-ai-every-camp-standard|companion analysis]] finds no release documented as meeting both the OSI's bar and the open-data one.

### Regulation raises the stakes before the evidence arrives

Law is starting to attach consequences to the label: under the [[EUAIAct|EU AI Act]], openly licensed models may be exempt from certain duties. The OSI says its definition aims at a common understanding "to educate policy makers" and a line against [[OpenWashing|open-washing]]. The FAccT survey's authors warned in 2024 that the exemption makes open-source status attractive as a way around documentation duties. The OSI [[osi-eu-code-of-practice-open-source|reports]] that after its objections, the third draft of the EU's Code of Practice made acceptable-use policies optional, an attribution resting on the OSI's own account.

In the United States the argument is about release itself. The NTIA ([[ntia-open-model-weights-report|National Telecommunications and Information Administration]]) advises monitoring open weights rather than immediately restricting them. [[societal-impact-open-foundation-models|Sayash Kapoor and 24 co-authors]] find research insufficient to characterize their marginal misuse risk. In 2026 [[Anthropic]]'s Amodei answered reports of a possible ban on US use of Chinese open-weights models by backing chip controls, a distillation crackdown and mandatory testing instead.

[[Distillation]] carried the dispute from technique to trade policy. [[OpenAI]] told a House committee in a [[openai-deepseek-free-riding-distillation|2026-02-12 memo]] that accounts tied to DeepSeek employees pulled its outputs through obfuscated routers. After Kimi K3's launch, White House adviser Michael Kratsios accused Moonshot AI of "covert industrial distillation," and Anthropic's [[anthropic-distillation-campaigns-alibaba-moonshot|2026-09 report]] followed.

The counts are the accusers' own. DeepSeek denied before Nature's referees that [[secrets-of-deepseek-r1-landmark-paper|R1]] copied OpenAI outputs, an answer to the 2025 suspicion; no source records a reply to the 2026 accusations. The open letter asks policymakers not to "conflate legitimate model-development techniques with misappropriation."

## What the Record Can Settle

Neither side in any grouping yet has the evidence to settle its central premise. Nearly every claim rests on attribution to a named claimant, and the evidence grade is mostly analysis and forecast rather than measured fact. The measured material is thin: the FAccT survey's scores, SaferAI's single evaluation, and company counts such as Anthropic's, which no outside party has verified in the sources.

The record is also uneven in time. The release, safety and distillation sources run into 2026-09, as do the repeal call and the OpenMDW dispute, while the newest source on the definition's data clause dates from 2025-06. As of 2026-09-30 the record holds no revision of the definition and no output from its amendment committee. Debian's proposal was withdrawn before a vote, the OpenMDW review wound down without approval, and Kühn's board run has no recorded outcome.
