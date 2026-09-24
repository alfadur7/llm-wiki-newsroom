# Overview

This wiki is a knowledge base comprising **34 source documents** (2023~2026), **10 entities**, **11 concepts**, **2 field overviews**, **1 analysis reports**, **0 associative trails**, and **0 timelines**.

Sources are automatically classified into 2 topic clusters via Leiden topology clustering: **Open Weights(27)**, **Open-Source AI Definition(25)**. A single source may span multiple clusters (listed in every catalog where its weight is ≥0.3); for the full cluster list and members, see [[index]] or `graph/_clusters.json`.

This wiki maps the argument over what "open source" should mean for AI models. At its center is the OSI ([[OpenSourceInitiative|Open Source Initiative]]), whose 2024 [[OpenSourceAI|Open Source AI Definition]] drew an endorsement from [[Mozilla]] and stricter rival tests from the [[FreeSoftwareFoundation|Free Software Foundation]]. Around it sit [[OpenWeights|open-weights]] releases such as [[Meta]]'s Llama, [[DeepSeek]]'s R1 and [[OpenAI]]'s gpt-oss, with the [[ModelLicensing|licenses]] they ship under and the [[OpenWashing|open-washing]] charges they draw. The [[EUAIAct|EU AI Act]] adds an exemption that gives the label a legal payoff.

A 2026 fight over whether such releases serve or threaten [[AISafety|safety]] brings in [[Anthropic]], and [[TrainingData|training data]] is the component every camp returns to. Nearly two years after the definition, these disputes are argued more than measured, and the record holds no revision of it.

## Recent Changes

- 2026-09-16 — An OSI blog post by Katie Steen-James sorts AI systems into closed, open-weight and Open Source, placing open weights one rung below the definition. [[OpenSourceInitiative]]
- 2026-08-04 — TechCrunch reports a SaferAI finding that Z.ai's open-weight model refused none of the offensive cyber or biology tasks it was given. [[AISafety]]
- 2026-08-02 — The European Commission's enforcement powers over general-purpose AI providers begin to apply; the record shows no enforcement action since. [[EUAIAct]]
- 2026-07-27 — Anthropic CEO Dario Amodei writes that Anthropic has never advocated a ban on open-weights models, while calling for mandatory pre-release safety testing. [[Anthropic]]
- 2026-07-24 — An open letter on a Microsoft page asks policymakers not to prohibit open weights or restrict distillation; Meta, OpenAI and Mistral are among its signatories. [[Distillation]]

## 1. [[open-source-ai-definition|Open-Source AI Definition]]

On 2024-10-28 the OSI published version 1.0 of the OSAID ([[OpenSourceAI|Open Source AI Definition]]), 16 months after a kickoff at [[Mozilla]]'s San Francisco office. The [[osi-open-source-ai-definition|reference text]] makes it a pass/fail test: a system must grant the freedoms to use, study, modify and share it without asking permission. Those freedoms rest on detailed data information, complete code and the model parameters, not on the [[TrainingData|training data]] itself. Mozilla [[mozilla-celebrates-osaid|endorsed the text]] the same day.

The [[OpenSourceInitiative|OSI]] is the steward, with [[StefanoMaffulli|Stefano Maffulli]] as its public voice through the release. Mozilla and [[open-future-osaid-step-forward|Open Future]] back its floor, though Open Future would have given it another name. The data-required critics gather around the FSF ([[FreeSoftwareFoundation|Free Software Foundation]]), joined by OSI co-founder Bruce Perens and a [[debian-ai-models-dfsg|Debian proposal]] to declare models without their data non-free. The form critics, led by [[osaid-take-it-or-leave-it|Yaniv Benhamou and Michel Reymond]] of the University of Geneva, prefer graded openness such as the [[ModelOpennessFramework|Model Openness Framework]].

The text drew disputes over substance and over form. The OSI's FAQ, as [[case-against-osaid|The New Stack]] quotes it, wants open-source AI to exist "in fields where data cannot be legally shared, for example medical AI," which a data requirement would rule out. The FSF's [[fsf-free-ml-application-criteria|draft criteria]] answer that an application is not free unless its data and processing scripts respect the four freedoms. On form, Benhamou and Reymond prefer tiers to a single pass/fail line.

Standing is the third fault line. The New Stack reports Debian developer Sam Johnston's point that the OSI's 10-person board, not its membership, approved the text. The Software Freedom Conservancy's [[sfc-osaid-erodes-open-source|Bradley M. Kühn]] objects to the text's rank rather than its form: he wants it demoted to "recommendations," and ran for the OSI board to have it repealed.

The OSI's volunteers ran a validation phase that passed five systems and failed Llama 2, Grok, Phi-2 and Mixtral. The reference page calls those results "not certifications of any kind" and says the OSI "will not validate or review individual AI systems," so no body applies the line to releases. The OSI's rulings on [[Meta]]'s Llama rest instead on the older OSD ([[OpenSourceDefinition|Open Source Definition]]): a [[osi-meta-llama-2-license-not-open-source|2023 post]] found the Llama 2 license fails its non-discrimination points 5 and 6. A [[osi-meta-llama-license-still-not-open-source|2025 follow-up]] says Llama 3.x still fails, and that the newer definition is not needed to reach that verdict.

Details: [[open-source-ai-definition|the Open-Source AI Definition field]].

## 2. [[open-weights|Open Weights]]

[[OpenWeights|Open weights]] means publishing a model's trained parameters while keeping its training data and code private. [[Meta]] shipped [[llama-2-meta-microsoft|Llama 2]] that way in 2023-07, and [[DeepSeek]] put [[deepseek-r1-release|its R1 model]] under the MIT License in 2025-01. [[OpenAI]]'s [[welcome-gpt-oss-openai|gpt-oss models]] followed on 2025-08-05 under Apache 2.0. A [[open-source-ai-models-how-open|2025-05-19 legal primer]] from Hunton notes that users can [[FineTuning|fine-tune]] such a model but cannot fully understand or reproduce it, biases included, without its data and algorithms.

The grouping pairs releasers such as Meta, DeepSeek, OpenAI and [[MistralAI|Mistral AI]] with [[HuggingFace|Hugging Face]], the hosting venue that recurs across its sources. [[Anthropic]] enters as the frontier lab arguing the risk side. Of the 18 sources that belong chiefly to this grouping, half are statements by model developers or their partners, and only two are academic papers. Their evidence grade is therefore mostly analysis, with facts resting on license texts, release specifications and a few measured evaluations.

Licensing is the layer where the release label and the terms part ways, and the Hunton primer notes that permissive grants such as MIT and Apache 2.0 were written for software only. The [[llama-3-1-community-license|Llama 3.1 Community License]] grants a royalty-free right to modify and redistribute, but withholds the grant above 700 million monthly active users. It also binds use to an Acceptable Use Policy, which Meta defends as a guardrail against harmful deployments. Mistral AI's non-commercial [[mistral-ai-non-production-license|Non-Production License]] and the Linux Foundation's [[openmdw-1-1-nvidia-adoption|OpenMDW-1.1]], one permissive grant over weights, code, documentation and data, mark the poles of [[ModelLicensing|model licensing]].

Two tensions run through the grouping. The first sets openness as a safeguard against release as an irreversible risk, and both sides accept that published weights cannot be recalled. A [[open-weights-american-ai-leadership|2026-07-24 open letter]], with more than 270 signing organizations as of 2026-08-03, concedes the point and answers with broad outside scrutiny. [[anthropic-position-open-weights-models|Anthropic CEO Dario Amodei]] instead asks that every capable model, open or closed, be [[AISafety|safety]]-tested before release. SaferAI's test of [[open-weight-models-frontier-safety-gap|Z.ai's GLM-5.2]] is the one measured risk result, and it probed the safeguards Z.ai shipped, not stripped ones.

The second tension sets the vendor's label against a license-and-completeness test. Meta and DeepSeek call their releases open source, while the [[osi-open-weights-good-open-source-better|OSI's 2026-09-16 post]] calls open weights better than closed models but short of open-source AI. Radboud's Andreas Liesenfeld and Mark Dingemanse, in their [[rethinking-open-source-generative-ai|FAccT '24 survey]] (Conference on Fairness, Accountability, and Transparency), score 40 text and 6 text-to-image generators on 14 dimensions. They find roughly the bottom third of text generators share only weights.

Details: [[open-weights|the Open Weights field]].

## Cross-Domain Threads

### One word, several judges

Across both groupings, the label "open source" has no single owner. [[Meta]] applies it to Llama, and its spokesperson told [[techcrunch-osaid-official-definition|TechCrunch]] that "there is no single open source AI definition," since earlier definitions "do not encompass the complexities" of today's models. The same statement defends the Llama license and its use policy as guardrails against harmful deployments.

Against Meta stand the [[OpenSourceInitiative|OSI]]'s license rulings and the [[FreeSoftwareFoundation|FSF]]'s finding that the Llama 3.1 license fails freedom 0, the freedom to use the model for any purpose. The FAccT survey adds its grading of withheld components, and by [[StefanoMaffulli|Maffulli]]'s account, talks with the OSI moved Google and Microsoft off the label but not Meta. The record on this is uneven: Meta's side rests on first-person announcements and one spokesperson statement that never answers the clause-by-clause reading of its license. The two sides do not argue from a shared test.

No party can make its reading stick. Kühn notes that the OSI never secured a trademark on the term, and TechCrunch reports that the OSI has no enforcement mechanism of its own. The OSI itself sorts systems into closed, open-weight and Open Source, a three-rung ladder with its definition as the only top rung.

### Training data as the fault line

[[TrainingData|Training data]] is the component both groupings keep returning to. The definition grouping argues over whether it must be released, the weights grouping is defined by withholding it, and a permissive license says nothing about it. [[Meta]] calls its handling of model details, training data included, a "cautious approach" while rules such as California's training-transparency law evolve.

Open releases of data exist but stay small in the record. [[hello-olmo-truly-open-llm|Ai2's OLMo 7B]] shipped in 2024-02 with its three-trillion-token Dolma corpus and the code that builds it. Open Future holds that open data still lacks the volume and diversity to train large foundation models. [[Mozilla]]'s endorsement grants that the definition "will need refinement over time" and states an aim to make open datasets more commonplace. A [[open-source-ai-every-camp-standard|companion analysis]] asks which releases clear both the OSI's bar and the stricter open-data one.

### Regulation raises the stakes before the evidence arrives

Law is starting to attach consequences to the label. The OSI says its definition aims at a common understanding "to educate policy makers" and a line against [[OpenWashing|open-washing]]. Under the [[EUAIAct|EU AI Act]], the Commission's [[eu-gpai-provider-guidelines|2025-07-31 guidelines]] set conditions under which models "released under a free and open-source license" may be exempt from certain duties. The FAccT survey's authors warned in 2024 that the Act's exemption makes open-source status attractive as a way around documentation duties.

In the United States the argument is about release itself. The National Telecommunications and Information Administration ([[ntia-open-model-weights-report|NTIA]]) advises monitoring open weights rather than immediately restricting them. [[societal-impact-open-foundation-models|Sayash Kapoor and 24 co-authors]] find research insufficient to characterize their marginal misuse risk. In 2026 [[Anthropic]]'s Amodei answered reports of a possible ban on US companies using Chinese open-weights models by backing chip controls, a distillation crackdown and mandatory testing instead.

## What the Record Can Settle

Neither grouping yet has the evidence to settle its central premise. Nearly every claim rests on attribution to a named claimant, and the evidence grade is mostly analysis and forecast rather than measured fact. The measured material is thin: the FAccT survey's scores and SaferAI's single evaluation.

The record is also uneven in time. The release and safety sources run into 2026-09, while the newest arguments on Llama's label, the definition's data clause and its form date from 2025-02, 2025-04 and 2025-03. As of 2026-09-24 the record holds no revision of the definition, no Debian vote result and no outcome of Kühn's board run.
