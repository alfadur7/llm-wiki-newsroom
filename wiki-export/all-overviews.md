# All OVERVIEWS (3)

---

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

## Sources

5 total — see Open-Model Governance catalog.

Top 5 by weight:
- [[eleutherai-common-pile-dataset]] _(w=0.40)_
- [[tech-industry-open-source-ai-definition-problem]] _(w=0.36)_
- [[apertus-fully-open-multilingual-llm]] _(w=0.33)_
- [[eu-ai-act-gpai-guide-open-source-developers]] _(w=0.33)_
- [[open-weights-not-open-source-label-dispute]] _(w=0.31)_



---

---
title: "Open-Source AI Definition"
type: overview
tags: []
cluster: open-source-ai-definition
sources: [osi-open-source-ai-definition, osi-readies-controversial-osaid, techcrunch-osaid-official-definition, infoworld-osi-unveils-osaid-1-0, euronews-meta-open-source-ai-not-all-it-seems, tech-industry-open-source-ai-definition-problem, what-does-open-source-ai-mean, mozilla-celebrates-osaid, mozilla-eleutherai-hf-sb-1047-letter, open-future-osaid-step-forward, case-against-osaid, sfc-osaid-erodes-open-source, fsf-free-ml-application-criteria, debian-ai-models-dfsg, debian-ai-gr-withdrawn, osaid-take-it-or-leave-it, osi-meta-llama-2-license-not-open-source, osi-meta-llama-license-still-not-open-source, osi-eu-code-of-practice-open-source, open-secret-of-open-washing, open-washing-four-criteria, osi-open-weights-good-open-source-better, open-weights-not-open-source-label-dispute, lwn-openmdw-license-review, hello-olmo-truly-open-llm, apertus-fully-open-multilingual-llm, eu-gpai-provider-guidelines, rethinking-open-source-generative-ai, open-weight-diplomacy-digital-silk-road]
last_updated: 2026-09-30
---

# Open-Source AI Definition

## Overview

On 2024-10-28 the OSI (the [[OpenSourceInitiative|Open Source Initiative]]) [[techcrunch-osaid-official-definition|published version 1.0]] of the OSAID ([[OpenSourceAI|Open Source AI Definition]]), its pass/fail test for when an AI system counts as open source. The [[osi-open-source-ai-definition|reference page]] requires the freedoms to use, study, modify, and share a system without asking permission. Those freedoms rest on detailed data information, complete code, and the model parameters, but not on the [[TrainingData|training data]] itself. [[Mozilla]] [[mozilla-celebrates-osaid|endorsed the text]] the same day, while the FSF ([[FreeSoftwareFoundation|Free Software Foundation]]) was [[fsf-free-ml-application-criteria|drafting a stricter test]] of its own.

[[StefanoMaffulli|Stefano Maffulli]], then the OSI's executive director, announced the effort in 2023-06. LWN (Linux Weekly News) [[osi-readies-controversial-osaid|reports a kickoff meeting]] at Mozilla's San Francisco office on 2023-06-21. By 2024-03 the OSI had gathered [[tech-industry-open-source-ai-definition-problem|a group of about 70]] researchers, lawyers, and activists, with staff from [[Meta]], Google, and Amazon among them. Drafts [[what-does-open-source-ai-mean|0.0.8]] and 0.0.9 followed that year, and [[infoworld-osi-unveils-osaid-1-0|InfoWorld]] reports that more than 25 organizations took part in the co-design. The 26 source pages grouped here run from the OSI's 2023-07 ruling on Meta's Llama 2 license to [[osi-open-weights-good-open-source-better|a 2026-09-16 OSI blog post]].

The need, in the OSI's framing, comes from a gap in the old tools. Software licenses cover code, but a model's weights and data sit outside them, so the OSD ([[OpenSourceDefinition|Open Source Definition]]) cannot be applied unchanged. The OSI names two goals: a common understanding for policymakers, and a line against [[OpenWashing|open-washing]], the use of the label for restricted releases. Law gives that line a payoff, since the [[EUAIAct|EU AI Act]] exempts some openly licensed models from certain duties. Yet the OSI has no enforcement mechanism, and Chainguard's Dan Lorenc [[open-secret-of-open-washing|points out]] that no one can be forced to use its definitions. By evidence grade, 278 of the pages' 528 claims are argument by named claimants and 211 are reported fact, and 18 of the 26 pages record a direct disagreement.

The first of three tension axes is **a data-information floor vs an open-data requirement**, which divides the OSI from the FSF and from Debian's data-requirement camp. The second is **one binary line vs graded or lesser standing**: Mozilla prizes a single test, while [[osaid-take-it-or-leave-it|legal scholars]] prefer [[ModelOpennessFramework|tiers]] and [[sfc-osaid-erodes-open-source|Bradley M. Kühn]] seeks repeal. The third is **the steward's test vs the vendor's label**: Meta rejected the definition, and a 2026 essay [[open-washing-four-criteria|calls Moonshot's Kimi K3 open-washing]]. Meanwhile the OSI's former executive director [[open-weights-not-open-source-label-dispute|calls its review of a new model license biased]]. The newest sources do not settle whether a steward with no power beyond persuasion can hold that line.

## Recent Changes

- 2026-09-16 — An OSI post by Katie Steen-James sorts AI systems into closed, open-weight, and Open Source, placing open weights one rung below the OSAID. [[osi-open-weights-good-open-source-better|OSI blog]]
- 2026-09-15 — Steven J. Vaughan-Nichols reports in The Register that Kühn and Red Hat's Richard Fontana want the OSAID repealed, and that Maffulli calls the OpenMDW review biased. [[open-weights-not-open-source-label-dispute|The Register]]
- 2026-08-21 — LWN's Jonathan Corbet writes that the OSI does not appear ready to approve the Linux Foundation's OpenMDW license in its current form. [[lwn-openmdw-license-review|LWN]]
- 2026-07-25 — JJ Jasser argues in Tech Policy Press that Kimi K3 (a Moonshot AI model) is at best an open-weight model and that calling it open source is "a category error." [[open-washing-four-criteria|Tech Policy Press]]

## Key Entities & Concepts

- **The steward** — the [[OpenSourceInitiative|OSI]] authors the OSAID, applies the older OSD to model licenses, and reviews new licenses submitted to it. [[StefanoMaffulli|Maffulli]] led it through the 2024 release and, by 2026-09, had left the executive director post. Carlo Piana chaired [[infoworld-osi-unveils-osaid-1-0|the board that approved version 1.0]]. Jordan Maris wrote [[osi-meta-llama-license-still-not-open-source|its 2025 Llama post]] and [[osi-eu-code-of-practice-open-source|its 2025 post on the EU rules]].
- **Endorsers and mediators** — [[Mozilla]] hosted the kickoff, and its AI strategy lead Ayah Bdeir warns that an "ideologically pristine" standard no builder meets "could end up backfiring." The OSI's website, per The New Stack, lists at least 20 endorsing organizations, and InfoWorld quotes Stanford's Percy Liang and Nextcloud's Frank Karlitschek in support. [[open-future-osaid-step-forward|Open Future's]] Alek Tarkowski and Paul Keller back the floor but would have given it another name.
- **Data-required critics** — the [[FreeSoftwareFoundation|FSF]] demands free training data. [[sfc-osaid-erodes-open-source|Kühn]], Tom Callaway, julia ferraioli, and OSI co-founder [[case-against-osaid|Bruce Perens]] argue the definition sets the bar too low. Lightning AI's Luca Antiga tells [[techcrunch-osaid-official-definition|TechCrunch]] that by neglecting the licensing of training data the OSI leaves "a gaping hole." Debian developer [[debian-ai-models-dfsg|Mo Zhou]] took the fight into distribution policy, and fellow Debian developer Sam Johnston predicted that a Debian statement of disapproval could rally wider opposition.
- **Form and naming critics** — [[osaid-take-it-or-leave-it|Yaniv Benhamou and Michel Reymond]] of the University of Geneva, and Radboud's [[rethinking-open-source-generative-ai|Andreas Liesenfeld and Mark Dingemanse]], prefer graded openness. The investor [[what-does-open-source-ai-mean|Joseph Jacks]] and RedMonk's [[osi-readies-controversial-osaid|Stephen O'Grady]] doubt the term transfers to AI at all.
- **The labeled** — [[Meta]] took part in drafting yet [[techcrunch-osaid-official-definition|disagrees with the result]]. [[MoonshotAI|Moonshot AI]] makes Kimi K3. Google and Microsoft, by Maffulli's account to [[euronews-meta-open-source-ai-not-all-it-seems|Euronews]], dropped the label for models that are not fully open.
- **Anchor concepts** — [[OpenSourceAI]] is the definition itself, and the [[OpenSourceDefinition|OSD]] is its inherited yardstick. [[TrainingData]] is the contested component, and the [[ModelOpennessFramework|Model Openness Framework]] is the tiered rival. [[OpenWashing]] names the practice all camps say they oppose.

## Subtopics

The **data-information compromise** is the cluster's core dispute, followed in depth at [[open-training-data-requirement|the open training-data theme]]. The [[OpenSourceInitiative|OSI]]'s 0.0.9 draft called [[TrainingData|training data]] "a benefit, not a requirement," because its insights "have already been learned." Its FAQ, as [[case-against-osaid|The New Stack]] quotes it, wants open-source AI to exist "in fields where data cannot be legally shared, for example medical AI." [[StefanoMaffulli|Maffulli]] told [[what-does-open-source-ai-mean|TechCrunch]] that knowing how data was sourced and filtered matters more than holding the plain dataset.

The split was visible early. In [[tech-industry-open-source-ai-definition-problem|MIT Technology Review's 2024 report]], Open Future's Zuzanna Warso argues openness should extend to data, while Roman Shaposhnik proposes sharing the open corpora a model was trained on. The [[FreeSoftwareFoundation|FSF]]'s [[fsf-free-ml-application-criteria|draft criteria]] answer that an application is not free unless its data and processing scripts respect the four freedoms. Yet the FSF allows that using such a system could be "ethically excusable" when data such as medical records cannot be released. [[infoworld-osi-unveils-osaid-1-0|Info-Tech's Brian Jackson]] accepts the medical case but says it leaves copyrighted training data unaddressed.

The compromise has defenders who name its cost. [[open-future-osaid-step-forward|Open Future]] frames the choice as "a stronger but narrower standard" against "a weaker but broader" one, and says the OSI took the second. [[Mozilla]]'s [[mozilla-celebrates-osaid|endorsement]] grants that the definition "will need refinement over time" and states an aim to make open datasets more commonplace. Maffulli agreed, per [[techcrunch-osaid-official-definition|TechCrunch]], that the text will need updates, and the OSI set up a committee to monitor how it is applied and to propose amendments.

**Debian's attempt** to write a data rule into its own guidelines stalled before a vote. Mo Zhou's [[debian-ai-models-dfsg|2025-04 proposal]], which LWN's Joe Brockmeier first judged likely to pass, would have put models without their original data outside the DFSG (Debian Free Software Guidelines). Objectors then noted it could also make spam filters, OCR (optical character recognition) tools, and speech synthesizers non-free, and Zhou [[debian-ai-gr-withdrawn|withdrew it]] on 2025-05-08. A rival text from Aigars Mahinovs would have adopted the OSAID's data-information standard instead, and none of the counter-proposals reached the ballot.

The **binary form and its standing** make a second dispute, set out at [[osaid-form-and-legitimacy|the binary-definition theme]]. Mozilla calls the binary precise enough for regulators, while Benhamou and Reymond call it [[osaid-take-it-or-leave-it|a "take it or leave it" approach]] and prefer tiers like the [[ModelOpennessFramework|Model Openness Framework]]. Less than three months before its endorsement, Mozilla had co-signed [[mozilla-eleutherai-hf-sb-1047-letter|a letter]] asking California for a legal definition covering "the spectrum of openly available AI." Jacks says there is "no such thing as open-source AI," and Maffulli called that point "correct" before keeping the term.

The legitimacy charge centers on who approved it. The New Stack reports Johnston's point that the OSI's 10-person board, not its membership, approved the text, and [[sfc-osaid-erodes-open-source|Kühn]] notes that the by-laws let the board reject election results. Kühn also argues the process amplified stakeholders who would profit from a retroactive "open source" label.

[[techcrunch-osaid-official-definition|TechCrunch]] reports that Meta, Google, and Microsoft are among the OSI's funders. After a Sloan Foundation grant of about $250,000 meant to lessen its reliance on industry backers, Maffulli told [[what-does-open-source-ai-mean|TechCrunch in June]] that the OSI "could say goodbye to Meta's money anytime." In 2026 [[open-weights-not-open-source-label-dispute|The Register]] reports that Kühn and Fontana still seek repeal, and that Perens accuses the OSI itself of open-washing.

**Open-washing and the vendor's label** show where the definition meets vendor practice; the label dispute is followed at [[llama-open-source-label|the Llama label theme]]. The OSI's [[osi-meta-llama-2-license-not-open-source|2023 ruling]] found the Llama 2 license fails [[OpenSourceDefinition|OSD]] points 5 and 6 on user and field-of-use limits. Its [[osi-meta-llama-license-still-not-open-source|2025 follow-up]] says Llama 3.x still fails, and that there is "no need to bring up" the OSAID to judge it. [[Meta]]'s spokesperson told TechCrunch that "there is no single open source AI definition," pointing to the Linux Foundation's suggested definitions and the FSF's criteria as other efforts, and defended the license's acceptable-use policy as a guardrail.

Maffulli told [[euronews-meta-open-source-ai-not-all-it-seems|Euronews]] that Meta's terms of use and distribution are incompatible with open source, and that talks with Meta produced no result; Meta did not reply to Euronews. Steven J. Vaughan-Nichols [[open-secret-of-open-washing|argues]] that the AI Act's exemptions give firms a strong incentive to open-wash.

In a 2026-07-25 essay written before the release, Jasser [[open-washing-four-criteria|applies the charge]] to Kimi K3, whose weights he then expected under a "Modified MIT" license with added conditions; Moonshot is not quoted. The weights shipped on 2026-07-27 with a clause requiring large hosts to sign a separate agreement, as Chinmayi Sharma [[open-weight-diplomacy-digital-silk-road|reports in Lawfare]]; the release itself is covered at [[open-weights|Open Weights]]. Critics also turn the charge back: Open Future reports that open-data advocates see the missing data requirement as [[OpenWashing|open-washing]] too.

- **Validation, not certification** — the OSI's volunteers ran models through a "Validation phase" to test the text itself. Five passed, and Llama 2, Grok, Phi-2, and Mixtral did not. The [[osi-open-source-ai-definition|reference page]] calls the results "not certifications of any kind" and says the OSI "will not validate or review individual AI systems." The OSI judges licenses, not systems, and verdicts on individual releases come from outsiders.
- **The definition in rulebooks** — the [[osi-eu-code-of-practice-open-source|OSI reports]] that the 2025-03-11 third draft of the EU's Code of Practice made acceptable-use policies optional after its objections. Benhamou and Reymond find the OSAID tracks the [[EUAIAct|AI Act]]'s Article 53(2) and is stricter on data disclosure than the training-content summary template the EU AI Office presented on 2025-01-17. Under the [[eu-gpai-provider-guidelines|Commission's guidelines]], general-purpose AI duties applied from 2025-08-02, with enforcement powers from 2026-08-02; the sources here record no enforcement action since.
- **Open-data proof points** — [[hello-olmo-truly-open-llm|Ai2's 2024-02-01 OLMo 7B release]] shipped its three-trillion-token Dolma corpus with the code that builds it. [[apertus-fully-open-multilingual-llm|Apertus]], released by Swiss public institutions on 2025-09-02, publishes its training data and methods with 8B and 70B models. The OSI's validation list names OLMo without a version, so the sources here do not tie the passing release to the open-data one. The New Stack adds Pleias's open dataset and a fully open model series from AMD, and Jasser counts OLMo among the handful of models that meet his four criteria. Open Future answers that open data lacks the volume and diversity to train large foundation models; [[open-source-ai-every-camp-standard|a cross-camp synthesis]] tests which releases clear every bar.
- **The steward as license judge** — the Linux Foundation submitted its [[OpenMDW]] license to the OSI, and [[lwn-openmdw-license-review|reviewers]] objected to its rights-clearing disclaimer and its termination clause. Richard Fontana suggests the clause could violate section 9 of the OSD, and the Linux Foundation's Mike Dolan defends it as symmetry. Maffulli says the review appears "tainted by an ideological bias."

## Key Trends & Figures

**The definition took 16 months from kickoff to release**
- 2023-06-21: kickoff meeting at [[Mozilla]]'s San Francisco office, per [[osi-readies-controversial-osaid|LWN's pre-vote survey]].
- 2023-07-20: the [[OpenSourceInitiative|OSI]] [[osi-meta-llama-2-license-not-open-source|rules the Llama 2 license]] not open source under the [[OpenSourceDefinition|OSD]].
- 2024-03: [[tech-industry-open-source-ai-definition-problem|MIT Technology Review]], drawing on Maffulli, names [[TrainingData|training data]] the biggest sticking point for the OSI's 70-strong working group.
- 2024-06-22: [[what-does-open-source-ai-mean|draft 0.0.8]] makes the full training dataset an "optional" component.
- 2024-08-22: draft 0.0.9 calls training data "one of the most hotly debated parts of the definition."
- 2024-10-27 / 2024-10-28: scheduled board vote, then [[infoworld-osi-unveils-osaid-1-0|release at All Things Open 2024]] in Raleigh, North Carolina.

**The requirements set a disclosure floor, not a data release**
- Code used to train and run the system must be under OSI-approved licenses, per [[open-future-osaid-step-forward|Open Future's summary]] of the text.
- Parameters and data information must be under "OSI-approved terms," which LWN's Brockmeier notes the OSI had not yet defined.
- Data information must list all public and third-party training data, so that "a skilled person" can build "a substantially equivalent system" ([[osaid-take-it-or-leave-it|Kluwer Copyright Blog]]).
- Liang welcomes the rule that the complete data-processing code be open, calling it "the primary driver of model quality."

**Tested models split three ways, and stricter tests pass fewer**
- Passed, per the [[osi-open-source-ai-definition|OSI's reference page]]: Pythia (EleutherAI), OLMo (Ai2), Amber and CrystalCoder (LLM360), and T5 (Google).
- Would "probably pass" with changed legal terms: BLOOM (BigScience), Starcoder2 (BigCode), and Falcon (Technology Innovation Institute).
- Failed for missing components or incompatible terms: Llama 2 ([[Meta]]), Grok (X/Twitter), Phi-2 (Microsoft), and Mixtral (Mistral).
- The [[rethinking-open-source-generative-ai|Radboud openness survey]], presented at the 2024 Conference on Fairness, Accountability, and Transparency, finds most models billed as open are not, and ranks OLMo near the top.

**Dissent moved from the OSI's forum into other institutions**
- 2024-10-22: the [[FreeSoftwareFoundation|FSF]] [[fsf-free-ml-application-criteria|announces its free machine-learning criteria]], after work that began in 2024-05.
- 2024-10-31: Kühn [[sfc-osaid-erodes-open-source|announces a single-issue run]] for the OSI board.
- 2025-04-19 to 2025-05-08: Zhou's Debian proposal gathers sponsors, then is [[debian-ai-gr-withdrawn|withdrawn before a vote]].
- 2026-08-21: the [[lwn-openmdw-license-review|OpenMDW review]] winds down without a clear outcome.
- 2026-09-15: [[open-weights-not-open-source-label-dispute|The Register]] reports the repeal call still standing; the sources here record no OSAID revision and no output from its amendment committee.

## Adjacent Domains & Scope

- [[open-weights|Open Weights]] — covers the weights-only releases, their safety debate, [[ModelLicensing|model licensing]], and the Llama and Kimi license texts. This cluster covers the definition that places those releases below the open-source line, and keeps the OSI's rulings on their terms and the open-washing charge built on them.
- [[open-model-governance|Open-Model Governance]] — covers the rules and institutions around open models: the EU AI Act, the Linux Foundation's OpenMDW license, and open-data builders such as Ai2 and EleutherAI. This cluster keeps the OSI's own tests, including where it applies them to those laws and licenses.

## Key Members (auto-extracted, top 15 by intra-cluster connectivity)

**Entities** (3)
- [[OpenSourceInitiative]]
- [[FreeSoftwareFoundation]]
- [[Mozilla]]

**Concepts** (5)
- [[OpenSourceAI]]
- [[TrainingData]]
- [[OpenWashing]]
- [[ModelOpennessFramework]]
- [[OpenSourceDefinition]]

## Sources

39 total — see Open-Source AI Definition catalog.

Top 15 by weight:
- [[case-against-osaid]] _(w=0.83)_
- [[mozilla-celebrates-osaid]] _(w=0.83)_
- [[debian-ai-gr-withdrawn]] _(w=0.75)_
- [[osi-readies-controversial-osaid]] _(w=0.75)_
- [[fsf-free-ml-application-criteria]] _(w=0.75)_
- [[osi-meta-llama-license-still-not-open-source]] _(w=0.71)_
- [[sfc-osaid-erodes-open-source]] _(w=0.71)_
- [[infoworld-osi-unveils-osaid-1-0]] _(w=0.67)_
- [[debian-ai-models-dfsg]] _(w=0.67)_
- [[osi-open-weights-good-open-source-better]] _(w=0.60)_
- [[what-does-open-source-ai-mean]] _(w=0.60)_
- [[open-future-osaid-step-forward]] _(w=0.58)_
- [[lwn-openmdw-license-review]] _(w=0.57)_
- [[osi-eu-code-of-practice-open-source]] _(w=0.57)_
- [[osi-open-source-ai-definition]] _(w=0.57)_



---

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

## Sources

51 total — see Open Weights catalog.

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


