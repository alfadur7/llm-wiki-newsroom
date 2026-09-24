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

<!-- AUTO:MEMBERS BEGIN -->
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
<!-- AUTO:MEMBERS END -->

<!-- AUTO:SOURCES BEGIN -->
## Sources

25 total — see [Open-Source AI Definition catalog](../sources/_catalog-open-source-ai-definition.md).

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
<!-- AUTO:SOURCES END -->
