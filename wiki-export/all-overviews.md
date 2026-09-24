# All OVERVIEWS (2)

---

---
title: "Open-Source AI Definition"
type: overview
tags: []
cluster: open-source-ai-definition
sources: [osi-open-source-ai-definition, osi-readies-controversial-osaid, techcrunch-osaid-official-definition, what-does-open-source-ai-mean, mozilla-celebrates-osaid, open-future-osaid-step-forward, case-against-osaid, sfc-osaid-erodes-open-source, fsf-free-ml-application-criteria, debian-ai-models-dfsg, osaid-take-it-or-leave-it, osi-meta-llama-2-license-not-open-source, osi-meta-llama-license-still-not-open-source, osi-open-weights-good-open-source-better, eu-gpai-provider-guidelines, hello-olmo-truly-open-llm, rethinking-open-source-generative-ai, red-hat-open-source-ai-point-of-view, joint-statement-ai-safety-openness]
last_updated: 2026-09-24
---

# Open-Source AI Definition

## Overview

On 2024-10-28 the OSI (the [[OpenSourceInitiative|Open Source Initiative]]) [[techcrunch-osaid-official-definition|published version 1.0]] of the OSAID ([[OpenSourceAI|Open Source AI Definition]]), its answer to what "open source" means for a trained model. The [[osi-open-source-ai-definition|reference page]] makes it a pass/fail test: a system must grant the freedoms to use, study, modify, and share it without asking permission. Those freedoms depend on three components — detailed data information, complete code, and the model parameters — but not on the [[TrainingData|training data]] itself. [[Mozilla]] [[mozilla-celebrates-osaid|endorsed the text]] the same day. The FSF ([[FreeSoftwareFoundation|Free Software Foundation]]) and [[debian-ai-models-dfsg|Debian developers]] set out [[fsf-free-ml-application-criteria|stricter tests]] of their own.

[[StefanoMaffulli|Stefano Maffulli]] announced the effort in 2023-06, and LWN.net [[osi-readies-controversial-osaid|reports a kickoff meeting]] at Mozilla's San Francisco office on 2023-06-21. Drafts [[what-does-open-source-ai-mean|0.0.8]] and 0.0.9 followed in 2024, and the board vote was set for 2024-10-27, the day before release.

The need, in the OSI's framing, comes from a gap in the old tools. Software licenses cover code, but a model's weights and data sit outside them, so the OSD ([[OpenSourceDefinition|Open Source Definition]]) cannot be applied unchanged. The OSI names two goals: a common understanding "to educate policy makers," and a line against [[OpenWashing|open-washing]], the use of the label for restricted releases. The [[EUAIAct|EU AI Act]] gives that line regulatory weight, since [[eu-gpai-provider-guidelines|openly licensed models]] can qualify for exemptions from some duties. Yet the OSI has no enforcement mechanism. The 16 source pages grouped here run from the OSI's 2023-07 ruling on [[Meta]]'s Llama 2 license to [[osi-open-weights-good-open-source-better|a 2026-09-16 OSI blog post]]. They hold 285 claims, half of them `[analysis]`-grade argument by named claimants, and ten of the pages record a direct disagreement with the definition or with Meta.

Three tension axes follow. The first is **a data-information floor vs an open-data requirement**. The OSI wants a standard that systems trained on unshareable data can meet; the FSF and Debian's Mo Zhou treat withheld data as disqualifying. The second is **one binary line vs graded or lesser standing**. Mozilla values the precision of a single test, while [[osaid-take-it-or-leave-it|legal scholars]] prefer [[ModelOpennessFramework|tiers]]. The Software Freedom Conservancy's [[sfc-osaid-erodes-open-source|Bradley M. Kühn]] wants the text demoted to "recommendations." The third is **the steward's label vs the vendor's label**. Meta rejected the definition at its release, and no source here records it withdrawing [[llama-open-source-label|the "open source" label for Llama]]. By Maffulli's account, talks with the OSI moved Google and Microsoft off the label but not Meta. The Act's exemptions could turn that branding dispute into a compliance one. Whether persuasion alone can hold the line is the question the newest sources leave open.

## Recent Changes

- 2026-09-16 — An OSI post by Katie Steen-James sorts AI systems into closed, open-weight, and Open Source, placing open weights one rung below the OSAID. [[osi-open-weights-good-open-source-better|OSI blog]]
- 2026-08-02 — The date the European Commission set for its enforcement powers over general-purpose AI providers to apply; the corpus records no enforcement action since. [[EUAIAct]]
- Stable period since: no source after [[debian-ai-models-dfsg|LWN's 2025-04-25 Debian report]] revises or contests the definition's text. The corpus records no OSAID revision, no amendment-committee output, and no result for Kühn's board run.

## Key Entities & Concepts

- **The steward** — the [[OpenSourceInitiative|OSI]] authors the OSAID and applies the older OSD to model licenses. [[StefanoMaffulli|Maffulli]] was its public voice through the 2024 release. Jordan Maris wrote [[osi-meta-llama-license-still-not-open-source|its 2025 Llama post]] and Katie Steen-James [[osi-open-weights-good-open-source-better|its 2026 open-weights post]].
- **Endorsers and mediators** — [[Mozilla]] hosted the kickoff and [[mozilla-celebrates-osaid|endorsed version 1.0]]. The New Stack counts at least 20 endorsing organizations, and the OSI names Suse, EleutherAI, Ai2, the Eclipse Foundation, and the OpenInfra Foundation among them. [[open-future-osaid-step-forward|Open Future's]] Alek Tarkowski and Paul Keller back the floor but would have given it another name. Mozilla also hosts the [[joint-statement-ai-safety-openness|Joint Statement on AI Safety and Openness]], whose safety case belongs to [[open-weights-safety-tradeoff|the openness-and-safety theme]].
- **Data-required critics** — the [[FreeSoftwareFoundation|FSF]] is [[fsf-free-ml-application-criteria|drafting criteria]] that demand free training data. [[sfc-osaid-erodes-open-source|Kühn]], Tom Callaway, julia ferraioli, and OSI co-founder [[case-against-osaid|Bruce Perens]] argue the definition sets the bar too low. Debian developers [[debian-ai-models-dfsg|Mo Zhou]] and Sam Johnston take the fight into distribution policy.
- **Form and naming critics** — [[osaid-take-it-or-leave-it|Yaniv Benhamou and Michel Reymond]] of the University of Geneva, and Radboud's [[rethinking-open-source-generative-ai|Andreas Liesenfeld and Mark Dingemanse]], prefer graded openness. OSS Capital's [[what-does-open-source-ai-mean|Joseph Jacks]] and RedMonk's [[osi-readies-controversial-osaid|Stephen O'Grady]] doubt the term transfers to AI at all.
- **The labeled and the regulator** — [[Meta]] took part in drafting yet [[techcrunch-osaid-official-definition|disagrees with the result]]. The European Commission [[eu-gpai-provider-guidelines|applies]] the [[EUAIAct|AI Act]], whose open-source exemption gives the label a legal payoff.
- **Anchor concepts** — [[OpenSourceAI]] is the definition itself, and the [[OpenSourceDefinition|OSD]] is its inherited yardstick. [[TrainingData]] is the contested component, and the [[ModelOpennessFramework|Model Openness Framework]] is the tiered rival. [[OpenWashing]] names the practice all camps say they oppose.

## Subtopics

The **data-information compromise** is the cluster's core dispute, followed in depth at [[open-training-data-requirement|the open training-data theme]]. The [[OpenSourceInitiative|OSI]]'s 0.0.9 draft called [[TrainingData|training data]] "a benefit, not a requirement." Its reason was that the data's insights "have already been learned." Its FAQ, as [[case-against-osaid|The New Stack]] quotes it, wants open source AI to exist "in fields where data cannot be legally shared, for example medical AI." The [[FreeSoftwareFoundation|FSF]]'s [[fsf-free-ml-application-criteria|draft criteria]] answer that an application is not free unless its data and processing scripts respect the four freedoms.

The two camps concede more than their headlines suggest. The FSF allows that using a nonfree system could be "ethically excusable" when data such as personal medical data cannot be released. [[Mozilla]]'s [[mozilla-celebrates-osaid|endorsement]] grants that some disagree with the data treatment. It adds that the definition "will need refinement over time," and states a `[forecast]`-grade aim to make open datasets more commonplace. [[open-future-osaid-step-forward|Open Future]] frames the choice as "a stronger but narrower standard" against "a weaker but broader" one, and says the OSI took the second. The [[debian-ai-models-dfsg|Debian resolution]] would pull free-software distribution toward the first. A companion analysis, [[open-source-ai-every-camp-standard|what clears every camp's bar]], compares the camps' tests.

The **binary form and its standing** make a second dispute, set out at [[osaid-form-and-legitimacy|the binary-definition theme]]. Mozilla calls the binary "akin to the existing definition" and praises its precision for regulators. Benhamou and Reymond call it [[osaid-take-it-or-leave-it|a "take it or leave it" approach]] and prefer tiers like the [[ModelOpennessFramework|Model Openness Framework]]. [[sfc-osaid-erodes-open-source|Kühn]] objects to its rank rather than its binary form, and announced a run for the OSI board to have it repealed.

The legitimacy charge centers on who approved it. The New Stack reports Johnston's point that the OSI's 10-person board, not its membership, approved the text. The OSI's own page says governance of the definition rests with that board. Kühn notes that OSI by-laws let the sitting board reject election results, which limits his route to repeal.

**Open-washing and the Llama test case** show where the definition meets vendor practice; the label dispute is followed at [[llama-open-source-label|the Llama label theme]]. The OSI's [[osi-meta-llama-2-license-not-open-source|2023 ruling]] found the Llama 2 license fails [[OpenSourceDefinition|OSD]] points 5 and 6 on user and field-of-use limits. Its [[osi-meta-llama-license-still-not-open-source|2025 follow-up]] says Llama 3.x still fails, and that there is "no need to bring up" the OSAID to judge it. [[Meta]]'s spokesperson told [[techcrunch-osaid-official-definition|TechCrunch]] that "there is no single open source AI definition." The company defends the Llama license and its acceptable-use policy as guardrails against harmful deployments. It calls its handling of model details, training data included, a "cautious approach" while rules such as California's training-transparency law evolve, and it points to the Linux Foundation's and the FSF's own attempts to codify the term. In the same report Maffulli says that Google and Microsoft, after talks with the OSI, agreed to stop calling models that are not fully open "open source," and that Meta has not.

Critics turn the [[OpenWashing|open-washing]] charge back on the definition. The [[rethinking-open-source-generative-ai|FAccT '24 survey]] (ACM Conference on Fairness, Accountability, and Transparency) calls any single measure, such as an open license, one of the most effective methods for open-washing. Open Future reports that open-data advocates see the missing data requirement as open-washing too. The same authors credit the OSAID with making corporate open-washing easy to spot, the use Mozilla's endorsement foresees for "open-ish models like Meta's Llama 3."

- **Validation, not certification** — the OSI's volunteers ran models through a "Validation phase" to test the text itself. Five passed, and Llama 2, Grok, Phi-2, and Mixtral did not. The reference page calls the results "not certifications of any kind." It says the OSI "will not validate or review individual AI systems," so no body applies the line to releases.
- **The [[EUAIAct|AI Act]] connection** — the [[eu-gpai-provider-guidelines|Commission's 2025-07-31 guidelines]] set conditions under which models "released under a free and open-source license" may be exempt from certain duties. Benhamou and Reymond find the OSAID tracks the Act's Article 53(2) definition and is stricter on data disclosure, with no conflict in principle. Liesenfeld and Dingemanse argue the exemption makes open-source status attractive as a way to escape documentation duties.
- **Open-data proof points** — [[hello-olmo-truly-open-llm|Ai2's 2024-02-01 OLMo 7B release]] shipped its three-trillion-token Dolma corpus with the code that builds it. The OSI's validation list names OLMo without a version, so the corpus does not tie the passing release to the open-data one. The OSI's 2026 post cites an OLMo memorization study that the full data made possible. The New Stack adds Pleias's open dataset and AMD's 1-billion-parameter models, which answer the "no good example" objection. They do not answer Open Future's point that open data lacks the volume and diversity to train large foundation models.
- **Does the term transfer at all** — Jacks says there is "no such thing as [[OpenSourceAI|open-source AI]]," and [[StefanoMaffulli|Maffulli]] [[what-does-open-source-ai-mean|called that point "correct"]] before keeping the term. Perens holds that the plain OSD "can be applied to AI," and O'Grady says the OSI should have started from a clean slate.
- **Funding and independence** — both TechCrunch pieces report that Meta, Google, and Microsoft are among the OSI's corporate funders. The OSI took a Sloan Foundation grant of about $250,000. Maffulli said the OSI "could say goodbye to Meta's money anytime." Kühn argues the process amplified stakeholders who would profit from a retroactive "open source" label.
- **A vendor's lower floor** — [[red-hat-open-source-ai-point-of-view|Red Hat CTO Chris Wright]] sets a minimum of openly licensed weights plus open software. He calls the link between any one item of training data and the weights "tenuous and indirect," and says his threshold is not a formal definition.

## Key Trends & Figures

**The definition took 16 months from kickoff to release**
- 2023-06-21: kickoff meeting at [[Mozilla]]'s San Francisco office, per [[osi-readies-controversial-osaid|LWN's pre-vote survey]].
- 2023-07-20: the [[OpenSourceInitiative|OSI]] [[osi-meta-llama-2-license-not-open-source|rules the Llama 2 license]] not open source under the [[OpenSourceDefinition|OSD]].
- 2024-06-22: [[what-does-open-source-ai-mean|draft 0.0.8]] makes the full [[TrainingData|training dataset]] an "optional" component.
- 2024-08-22: draft 0.0.9 calls training data "one of the most hotly debated parts of the definition."
- 2024-10-27 / 2024-10-28: scheduled board vote, then [[techcrunch-osaid-official-definition|publication of version 1.0]] and [[mozilla-celebrates-osaid|Mozilla's endorsement]].

**The requirements set a disclosure floor, not a data release**
- Code used to train and run the system must be under OSI-approved licenses, per [[open-future-osaid-step-forward|Open Future's summary]] of the text.
- Parameters and data information must be under "OSI-approved terms," which LWN's Joe Brockmeier notes the OSI had not yet defined.
- Data information must describe all training data and list public and third-party sources, so that "a skilled person" can build "a substantially equivalent system" ([[osaid-take-it-or-leave-it|Kluwer Copyright Blog]]).

**The validation phase split tested models three ways**
- Passed, per the [[osi-open-source-ai-definition|OSI's reference page]]: Pythia (EleutherAI), OLMo (Ai2), Amber and CrystalCoder (LLM360), and T5 (Google).
- Would "probably pass" with changed legal terms: BLOOM (BigScience), Starcoder2 (BigCode), and Falcon (TII).
- Failed for missing components or incompatible terms: Llama 2 ([[Meta]]), Grok (X/Twitter), Phi-2 (Microsoft), and Mixtral (Mistral).
- The [[rethinking-open-source-generative-ai|FAccT '24 leaderboard]], scored separately, also puts OLMo Instruct and LLM360's AmberChat near full openness.

**Dissent moved from the OSI's forum into other institutions**
- 2024-10-22: the [[FreeSoftwareFoundation|FSF]] [[fsf-free-ml-application-criteria|announces its free machine-learning criteria]], after work that began in 2024-05.
- 2024-10-31: Kühn [[sfc-osaid-erodes-open-source|announces a single-issue run]] for the OSI board.
- 2024-12-05: [[case-against-osaid|The New Stack rounds up critics]], including Perens, Kühn, and Johnston.
- 2025-04: [[debian-ai-models-dfsg|Mo Zhou's Debian resolution]] gathers enough sponsors to proceed; the corpus records no vote result.

**The regulatory clock runs to 2027**
- 2025-01-17: the EU AI Office presents its template for the Article 53(1)(d) training-content summary.
- 2025-08-02: general-purpose AI obligations under the [[EUAIAct|AI Act]] apply, per the [[eu-gpai-provider-guidelines|Commission's guidelines]], with enforcement powers a year later.
- 2027-08-02: deadline for models on the market before the obligations applied.

## Adjacent Domains & Scope

- [[open-weights|Open Weights]] — covers the weights-only releases, their safety debate, [[ModelLicensing|model licensing]], and the Llama license text. This cluster covers the definition that places those releases below the open-source line, and keeps the OSI's rulings on those license terms and the open-washing charge built on them.

## Key Members (auto-extracted, top 15 by intra-cluster connectivity)

**Entities** (4)
- [[OpenSourceInitiative]]
- [[FreeSoftwareFoundation]]
- [[Mozilla]]
- [[StefanoMaffulli]]

**Concepts** (6)
- [[OpenSourceAI]]
- [[TrainingData]]
- [[OpenWashing]]
- [[EUAIAct]]
- [[OpenSourceDefinition]]
- [[ModelOpennessFramework]]

## Sources

25 total — see Open-Source AI Definition catalog.

Top 15 by weight:
- [[osi-readies-controversial-osaid]] _(w=0.88)_
- [[case-against-osaid]] _(w=0.83)_
- [[mozilla-celebrates-osaid]] _(w=0.83)_
- [[fsf-free-ml-application-criteria]] _(w=0.75)_
- [[osi-meta-llama-license-still-not-open-source]] _(w=0.71)_
- [[sfc-osaid-erodes-open-source]] _(w=0.71)_
- [[osi-meta-llama-2-license-not-open-source]] _(w=0.71)_
- [[what-does-open-source-ai-mean]] _(w=0.70)_
- [[debian-ai-models-dfsg]] _(w=0.67)_
- [[open-future-osaid-step-forward]] _(w=0.67)_
- [[techcrunch-osaid-official-definition]] _(w=0.67)_
- [[osi-open-weights-good-open-source-better]] _(w=0.60)_
- [[osaid-take-it-or-leave-it]] _(w=0.60)_
- [[osi-open-source-ai-definition]] _(w=0.57)_
- [[openmdw-1-1-nvidia-adoption]] _(w=0.50)_



---

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

## Sources

27 total — see Open Weights catalog.

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


