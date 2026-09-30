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

<!-- AUTO:MEMBERS BEGIN -->
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
<!-- AUTO:MEMBERS END -->

<!-- AUTO:SOURCES BEGIN -->
## Sources

39 total — see [Open-Source AI Definition catalog](../sources/_catalog-open-source-ai-definition.md).

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
<!-- AUTO:SOURCES END -->
