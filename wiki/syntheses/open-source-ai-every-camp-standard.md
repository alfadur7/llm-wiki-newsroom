---
title: "What Counts as Open Source AI Under Every Camp's Standard"
type: synthesis
tags: [open-source-ai, OSAID, training-data, open-weights]
sources: [osi-open-source-ai-definition, fsf-free-ml-application-criteria, osi-meta-llama-license-still-not-open-source, hello-olmo-truly-open-llm, case-against-osaid, osi-open-weights-good-open-source-better, rethinking-open-source-generative-ai, open-future-osaid-step-forward, red-hat-open-source-ai-point-of-view, debian-ai-models-dfsg, mozilla-celebrates-osaid, open-source-ai-models-how-open, techcrunch-osaid-official-definition]
last_updated: 2026-09-24
---

# What Counts as Open Source AI Under Every Camp's Standard

## Summary

No release in this corpus is documented as clearing every camp's bar for [[OpenSourceAI|open source AI]]; Ai2's OLMo comes closest. Its 2024-02-01 release of OLMo 7B shipped the pretraining data, the code that builds that data, the training code and the weights — every component the OSI and FSF tests name — and a model called OLMo passed the [[OpenSourceInitiative|Open Source Initiative]] (OSI)'s validation phase. Three gaps stop that short of a yes: the OSI's list names no version, the release announcement states no license terms, and no open-data critic has applied its test to OLMo. The dividing question in every camp is still [[TrainingData|training data]]: must the data itself be released on free terms, or is a description of it enough?

## 1. Every camp's bar is the union of two lists

Two stated tests set the bar. The [[osi-open-source-ai-definition|Open Source AI Definition]] (OSAID) grants the four freedoms (use, study, modify, share) through access to "the preferred form to make modifications to the system." [[open-future-osaid-step-forward|Open Future's reading of the text]] breaks that form into three conditions: detailed information about the training data, code for training and running the system under OSI-approved licenses, and model parameters, including weights, made available. The [[FreeSoftwareFoundation|Free Software Foundation]] (FSF) asks for more on data. Its [[fsf-free-ml-application-criteria|2024-10-22 statement]] requires that all the software, for both training and inference, grant the four freedoms, and that "all its training data and the related scripts for processing it" do so too. On parameters, though, the FSF says only that the four freedoms "may translate into a demand" that the release include them.

So neither list simply contains the other. The FSF is stricter on data and scripts, and the OSI is firmer on parameters. A release that satisfies every camp therefore has to meet the union of the two: free training data and processing scripts, free software, and weights that are actually released.

The two camps also demand the data on different grounds. OSI co-founder Bruce Perens holds that the training data is the source code, as [[case-against-osaid|The New Stack's round-up of critics]] reports. The FSF says the opposite: training data is not the "source code" of model parameters "in the usual sense." It demands the data anyway, because in practice people study and adapt a model by analyzing its data and retraining it. A release that cleared the union would not settle which of those reasons is right.

Other positions in the corpus sit inside the union or have not been adopted:

- **Below it** — Red Hat CTO Chris Wright sets a [[red-hat-open-source-ai-point-of-view|minimum threshold]] of open source-licensed weights plus open source software, and calls it "a starting point of open source AI, not the final destination."
- **The same bar, a different name** — Alek Tarkowski and Paul Keller of Open Future accept the OSAID's floor but would have kept the name "open source" for systems that include open data. That is a claim about labels. The data demand it implies is already in the FSF half of the union.
- **Proposed, not adopted** — Debian developer Mo Zhou's [[debian-ai-models-dfsg|General Resolution]] would treat models released without their original training data or program as non-free. Thorsten Glaser's counter-proposal goes further. It asks for data "legally obtained and used," data licensed for distribution, and models that can be rebuilt reproducibly, and the report records one developer seconding it. The corpus holds no vote result for either text. This page therefore measures releases against the OSI and FSF tests. It treats Glaser's text as an outer bound that no release here has been tested against.
- **An endorsement, not a bar** — [[Mozilla]] backs the OSI standard as "an important step forward" [[mozilla-celebrates-osaid|in its endorsement]], while granting that some disagree with its treatment of training data.

## 2. What the union rules out

Most releases called "open" fall on the data side of the union. The [[open-source-ai-models-how-open|Hunton legal primer]] places [[DeepSeek]] R1 in the [[OpenWeights|open-weights]] middle ground: its weights are public under an MIT license, but its training data is not. With no data released, R1 fails the FSF half of the union on its face. [[Meta]]'s Llama 2 is among the systems that did not pass the OSI's validation phase, which the reference page says lack required components or carry legal terms at odds with open source. The OSI's rulings on Llama itself rest on the older license test, traced in [[llama-open-source-label|the Llama label dispute]].

Documenting every component is not enough on its own, because the camps also split on [[ModelLicensing|license terms]]. The [[rethinking-open-source-generative-ai|openness survey]] that Andreas Liesenfeld and Mark Dingemanse presented at FAccT '24, the ACM Conference on Fairness, Accountability, and Transparency, scores a system as fully licensed when an OSI license or a Responsible AI License (RAIL) covers it. Its walkthrough of BloomZ against Llama concludes that "Only BloomZ can substantially claim open source status." BloomZ, from the BigScience Workshop team, releases its code under Apache 2.0 and its weights under RAIL. Open Future, by contrast, reads the OSAID as excluding systems under responsible AI licenses, because those licenses restrict certain uses. The OSI's own reference page lists BLOOM, from the same BigScience team, among the models that "would probably pass if they changed their licenses/legal terms." So the survey's leading example of open source status comes from a team whose model the OSI says would probably pass but for its license terms. That is why the license is one of the gaps for OLMo below.

## 3. OLMo: every component documented, not every link

The [[hello-olmo-truly-open-llm|Ai2 announcement]] of 2024-02-01 lists what shipped with OLMo 7B:

- **Data and scripts** — the Dolma corpus of three trillion tokens, "including code that produces the training data."
- **Weights and training software** — full weights for four variants at the 7B scale, each trained to at least 2 trillion tokens, with inference code, training metrics and training logs.
- **Evaluation** — the development evaluation suite, with more than 500 checkpoints per model.

That list covers data, processing scripts, training software and weights, which is every item in the union. The source is Ai2's own announcement, though, and it assesses Ai2's "truly open" claim against no outside test. The release also came about nine months before either test existed: the FSF statement is dated 2024-10-22, and the OSAID 1.0 was [[techcrunch-osaid-official-definition|released on 2024-10-28]].

Three gaps stand between those components and a finding that OLMo clears every camp's bar.

**Which OLMo.** The OSI's reference page lists "OLMo (AI2)" among the models that passed without naming a version. The [[osi-open-weights-good-open-source-better|OSI's 2026 blog post]] says a memorization study was "only possible because Olmo is released as Open Source AI," again without a version. The FAccT survey ranks "OLMo Instruct" near full openness, a name the Ai2 announcement does not use. The model the round-up calls "AMD's OLMo" is AMD's own 1-billion-parameter release, not Ai2's. No source in the corpus ties the model that passed validation to the 2024-02-01 release that documents open data.

**Which license.** The FSF test turns on whether data and scripts "respect all users, following the four freedoms," and the OSI requires code under OSI-approved licenses. Both are questions about license terms. The Ai2 announcement says what it released and where to get it (on [[HuggingFace|Hugging Face]] and GitHub), but not under what terms. Section 2 shows that license terms alone can split the camps.

**Who applies the test.** As of its 2024-10-22 statement the FSF's working group was still drafting the exact text of its criteria, and the corpus holds no final text. The one FSF finding on a model that the corpus records is second-hand: the OSI's [[osi-meta-llama-license-still-not-open-source|2025-02-18 post on Llama]] agrees with an FSF evaluation that the Llama 3.1 Community License fails freedom 0, the freedom to use the model for any purpose. That is a ruling on a license under the software freedoms, not an application of the machine-learning criteria. The OSI, for its part, says its validation results "should be seen as part of the definitional process" and are "not certifications of any kind," and that it "will not validate or review individual AI systems." It does intend, [[techcrunch-osaid-official-definition|TechCrunch reports]], to flag models described as open source that fall short, and it has set up a committee to monitor how the OSAID is applied. Neither camp, then, names a body that confirms a pass. What OLMo lacks is a positive ruling against either bar, not a party able to object. The same gap in the OSAID's design is followed in [[osaid-form-and-legitimacy|the dispute over the definition's form and legitimacy]].

The other models that passed validation stand further back. Pythia, CrystalCoder and T5 have no open-data release recorded in the corpus, and passing the OSAID turns on data *information*, so it cannot stand in for one. LLM360's Amber comes a step closer. It passed validation by name, and the FAccT survey says the organisations behind AmberChat, OLMo Instruct and BloomZ "have gone to great lengths to make training data, code, training pipelines, and documentation available." The corpus holds no release record for Amber itself.

## 4. What the answer settles, and what would close the gap

The answer is narrow. No release here is documented as meeting the union of the OSI and FSF tests. OLMo is where the gap is smallest, and there the gap is in the record, not in the components: a version, a license statement, and a body that applies the test. A license statement for Dolma and the OLMo code, together with a final FSF text applied to a named release, would close most of it. The OSI has said it will not rule on individual systems, so the version gap on its side may stay open.

The answer does not reach the scale question. The open-data releases in the round-up answer the objection that there is "no good example of an open data LLM." Open Future's point that open resources lack the volume and diversity to train large foundation models is argued in [[open-training-data-requirement|the open training-data dispute]], and this page does not settle it.

## Connections

- **Cluster overviews** — [[open-source-ai-definition|Open-Source AI Definition overview]] · [[open-weights|Open-weights overview]]
- **Concepts** — [[OpenSourceAI]] · [[TrainingData]] · [[OpenWeights]] · [[ModelLicensing]] · [[OpenWashing]]
- **Entities** — [[OpenSourceInitiative]] · [[FreeSoftwareFoundation]] · [[Mozilla]] · [[Meta]] · [[DeepSeek]] · [[HuggingFace]]
- **Themes** — [[open-training-data-requirement|OSAID vs open training-data requirement]] (the dispute this synthesis turns into an answer) · [[osaid-form-and-legitimacy|OSAID form and legitimacy]] · [[llama-open-source-label|Llama open-source label]]
- **Sources** — [[osi-open-source-ai-definition|OSI reference page]] · [[fsf-free-ml-application-criteria|FSF criteria statement]] · [[hello-olmo-truly-open-llm|Hello OLMo]] · [[case-against-osaid|The Case Against the OSAID]] · [[osi-open-weights-good-open-source-better|OSI on open weights, 2026]] · [[rethinking-open-source-generative-ai|FAccT '24 openness survey]] · [[open-future-osaid-step-forward|Open Future assessment]] · [[red-hat-open-source-ai-point-of-view|Red Hat point of view]] · [[debian-ai-models-dfsg|Debian DFSG debate]] · [[osi-meta-llama-license-still-not-open-source|OSI on the Llama 3.x license]] · [[mozilla-celebrates-osaid|Mozilla endorsement]] · [[open-source-ai-models-how-open|Hunton primer]] · [[techcrunch-osaid-official-definition|TechCrunch on the 1.0 release]]
