# Overview

<!-- AUTO:STATS BEGIN -->
This wiki is a knowledge base comprising **4 source documents** (2024~2025), **5 entities**, **6 concepts**, **3 field overviews**, **0 analysis reports**, **0 associative trails**, and **0 timelines**.

Sources are automatically classified into 3 topic clusters via Leiden topology clustering: **Open-Source AI Definition(4)**, **Open Weights(1)**, **Licensing & Open-Washing(3)**. A single source may span multiple clusters (listed in every catalog where its weight is ≥0.3); for the full cluster list and members, see [[index]] or `graph/_clusters.json`.
<!-- AUTO:STATS END -->

This wiki maps the debate over what "open source" should mean for AI systems. The corpus gathers the [[OpenSourceInitiative]]'s 2024 attempt to fix a definition, the endorsement and criticism it drew, and the looser "open weights" releases that dominate the market in practice. Three groupings organize the field: the formal definition and its data dispute, the weights-only middle ground, and the licensing terms and open-washing that surround both. The strongest evidence base sits with the definition grouping, where the [[OpenSourceInitiative]] is the recurring claimant across multiple sources.

## Recent Changes

- 2025-05-19 — A legal primer frames the open-weights middle ground against the strict definition, using [[DeepSeek]] R1 as its leading example.
- 2025-01 — [[DeepSeek]] releases R1 with MIT-licensed weights but withheld training data, the defining open-weights case.
- 2024-12-05 — Criticism of the definition's omission of open training data is rounded up, led by the [[FreeSoftwareFoundation]] and OSI co-founder Bruce Perens.
- 2024-10-28 — The [[OpenSourceInitiative]] releases the Open Source AI Definition 1.0; [[Mozilla]] endorses it the same day, and [[Meta]]'s Llama is judged non-compliant.

## 1. [[open-source-ai-definition|Open-Source AI Definition]]

On 2024-10-28 the [[OpenSourceInitiative]] released the Open Source AI Definition 1.0, the first binary standard for open AI: a system either grants the four freedoms — use, study, modify, share — or it does not, and qualifying requires data information, source code, and parameters. OSI validated Pythia, OLMo, Amber, CrystalCoder, and T5, and judged Llama non-compliant.

The grouping's actors split three ways. The [[OpenSourceInitiative]] is the standard-setter; [[Mozilla]] is the prominent endorser, framing openness as an AI-safety precondition; the [[FreeSoftwareFoundation]] is the dissenter building a stricter alternative. The anchor concept is [[OpenSourceAI]], and the contested component is [[TrainingData]].

The central collision is whether a workable binary standard or a maximalist open-data requirement should define "open." OSI and [[Mozilla]] argue an imperfect-but-clear definition serves developers and regulators now; the [[FreeSoftwareFoundation]] holds that without raw training data the label is hollow. The procedural fact that a 10-person board, not the full membership, approved the definition feeds the dispute.

Details: [[open-source-ai-definition|the Open-Source AI Definition field]].

## 2. [[open-weights|Open Weights]]

[[DeepSeek]]'s R1, released 2025-01 under the MIT license with public weights but a withheld training corpus, is the defining case of the weights-only middle ground. It drew attention partly on a roughly $6 million training-cost claim that made a cheap-to-adapt release commercially compelling.

The grouping centers on [[DeepSeek]] as provider and on two concepts: [[OpenWeights]], the posture of publishing parameters while keeping data secret, and [[FineTuning]], the adaptation capability that makes such a release useful. It is defined by contrast with the fuller [[OpenSourceAI]] standard rather than by a dense actor roster.

The tension is practical adaptability against genuine transparency. Publishing weights lets users fine-tune without retraining, but the withheld data and algorithms mean the model cannot be fully audited, reproduced, or inspected for bias — which is precisely the partial release the strict definition was written to exclude.

Details: [[open-weights|the Open Weights field]].

## 3. [[licensing-open-washing|Licensing & Open-Washing]]

This grouping covers the terms and rhetoric of "open" AI. [[Meta]]'s Llama, released in early 2023 under a custom community license with usage restrictions, is the reference case the [[OpenSourceInitiative]] cites as non-compliant and as the canonical example of open-washing.

Licensing is where open-source AI diverges from software: permissive families (MIT, Apache) and copyleft families (GPL) were written for code, but a model adds data and weights that no software license covers. [[ModelLicensing]] and [[OpenWashing]] are the anchor concepts; [[Meta]] is the contested issuer, with [[OpenSourceInitiative]] judging and [[Mozilla]] advocating.

The collision is whether a familiar permissive license is sufficient signal of openness or whether component completeness is the real test. [[DeepSeek]] R1's MIT-licensed-but-data-less release shows the two are independent, and as "open source" enters regulation, a soft line lets restricted models claim benefits meant for open ones.

Details: [[licensing-open-washing|the Licensing & Open-Washing field]].

## Cross-Domain Threads

**One word, three standards.** The whole corpus is a fight over a single phrase. The definition grouping wants "open source" to mean the four freedoms plus reproducible components; the open-weights grouping uses "open" to mean runnable-and-adaptable; the licensing grouping shows how the word gets attached to releases that satisfy neither. The [[OpenSourceInitiative]]'s binary definition is the attempt to collapse these three readings into one, and the resistance to it — from the [[FreeSoftwareFoundation]] on one flank and from market practice on the other — is what keeps the field unsettled.

**Training data as the fault line.** [[TrainingData]] is the component that recurs across all three groupings. The definition grouping fights over whether it must be released, the open-weights grouping is defined by withholding it, and the licensing grouping shows that a permissive license says nothing about it. Whether "open" requires open data is therefore the single question that, once answered, would resolve most of the surrounding disputes at once.
