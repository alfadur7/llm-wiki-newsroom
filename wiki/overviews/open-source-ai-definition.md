---
title: "Open-Source AI Definition"
type: overview
tags: []
cluster: open-source-ai-definition
sources: []
last_updated: 2026-07-17
---

# Open-Source AI Definition

## Overview

On 2024-10-28 the [[OpenSourceInitiative]] released the [[OpenSourceAI|Open Source AI Definition]] (OSAID) 1.0, the first attempt to settle what "open source" means once a system is a trained model rather than software alone. The definition is deliberately binary: a system either grants the four freedoms — to use, study, modify, and share for any purpose without permission — or it does not. To qualify, a release must provide three components: data information, complete source code, and model parameters. OSI validated a short list of compliant models (Pythia, OLMo, Amber, CrystalCoder, T5) and judged [[Meta]]'s Llama non-compliant.

The definition matters because traditional software licenses never anticipated [[TrainingData]], weights, and the cost of reproducing a model from scratch. OSI frames a clear binary standard as the precondition for two things its leadership cares about: informing regulators who increasingly write "open source" into law, and curbing [[OpenWashing]], the practice of claiming the open-source brand while withholding components. The 4 source pages in this cluster are dominated by `[fact]`- and `[analysis]`-grade claims, with [[OpenSourceInitiative]] as the recurring claimant on the definitional side.

The OSAID was produced through a multi-year co-design process and was endorsed by at least 20 organizations, [[Mozilla]] prominent among them. Yet the same document that compliant-model validation rests on was approved by OSI's 10-person board rather than a full membership vote — a procedural fact critics return to. The most contested design choice is that OSAID requires "data information" (enough detail to recreate a substantially equivalent system) rather than the raw dataset itself, on the argument that some data, such as medical records, cannot be legally shared.

The cluster therefore organizes around one tension axis: **a workable binary standard vs. a maximalist open-data requirement**. Endorsers ([[Mozilla]], OSI) argue a shared, imperfect-but-clear definition is more useful to developers and regulators today than waiting for a stricter one; critics led by the [[FreeSoftwareFoundation]] hold that without the raw training data the label is hollow, since the data is effectively the source code. How that axis resolves will shape whether "open source AI" converges on one standard or fractures into competing definitions.

## Recent Changes

- 2024-12-05 — Coverage rounds up the growing criticism of the OSAID over its omission of open training data, with [[FreeSoftwareFoundation]] figures leading the dissent.
- 2024-10-28 — [[OpenSourceInitiative]] publishes OSAID 1.0 and the validated-model list; [[Mozilla]] endorses it the same day.
- Stable period since: no new material has entered this cluster in the months following the launch debate.

## Key Entities & Concepts

The cluster splits into three roles. The **standard-setter** is [[OpenSourceInitiative]], author and steward of the OSAID. The **endorser** wing is led by [[Mozilla]], which frames openness as an AI-safety precondition and defends the data-information requirement as already stricter than most releases. The **dissenter** is the [[FreeSoftwareFoundation]], building a stricter open-data alternative. The two anchor concepts are [[OpenSourceAI]] (the definition itself) and [[TrainingData]] (the component the camps fight over); [[OpenWashing]] is the practice the definition is meant to constrain.

## Subtopics

The **data-information compromise** is the heart of the cluster. OSAID requires enough detail to recreate a substantially equivalent system rather than the raw [[TrainingData]], a deliberate concession to fields like medical AI where datasets cannot be legally shared. Endorsers read this as pragmatic; the [[FreeSoftwareFoundation]] reads it as fatal, holding that data and processing scripts must respect the four freedoms or the model is not free. This axis is analysed in depth in [[open-training-data-requirement|the open-training-data dispute]].

Yet the endorser position is not static acceptance. [[Mozilla]] backs the standard as "an important step forward" while conceding its data treatment "will need refinement" ([[mozilla-celebrates-osaid|its endorsement post]]). Having convened experts with EleutherAI on open-dataset norms, its [forecast]-grade intent is to raise the data bar over time.

Critics reject the refinement-over-time framing: they hold the data omission is disqualifying now, not a defect to be fixed later. A companion analysis, [[open-source-ai-every-camp-standard|what clears every camp's bar]], finds the only plausible candidates are the fully-open-data models OSI itself validated.

The **binary-vs-spectrum question** is the second axis. [[OpenSourceAI]] is intentionally all-or-nothing so that regulators and civil society can tell genuinely open systems from marketing, and so [[OpenWashing]] has a clear line to fall on the wrong side of. Critics counter that a binary that admits data-less models simply moves the open-washing line rather than removing it.

- **Procedural legitimacy** — the OSAID was approved by OSI's 10-person board rather than a full membership vote, which critics including OSI co-founder Bruce Perens cite when arguing the standard lacks community mandate.
- **Validation as enforcement** — by publishing a compliant list (Pythia, OLMo, Amber, CrystalCoder, T5) and a non-compliant verdict on [[Meta]]'s Llama, OSI turned the definition into a working test rather than an abstract principle.
- **Proof-of-viability models** — fully open-data releases such as OLMo (AI2) and Pythia (EleutherAI) are offered as evidence the open-data path is achievable, undercutting the "niche-only" defense.

## Key Trends & Figures

**Definition milestones**
- 2024-10-28: OSAID 1.0 released by [[OpenSourceInitiative]] after a multi-year co-design process.
- Endorsed by at least 20 organizations on launch, including [[Mozilla]].

**Compliance verdicts**
- Validated as compliant: Pythia, OLMo, Amber, CrystalCoder, T5.
- Judged non-compliant: [[Meta]]'s Llama, for missing components and conflicting license terms.

**Governance signals**
- Approved by a 10-person board rather than full membership.
- 2024-12: a campaign announced to run for the OSI board on a platform to repeal the OSAID.

## Adjacent Domains & Scope

- [[licensing-open-washing|Licensing & Open-Washing]] — covers the license-term mechanics and the Llama open-washing case; this cluster covers the definition that judges those terms, not the terms themselves.
- [[open-weights|Open Weights]] — covers the weights-only middle ground that the OSAID explicitly does not accept as fully open; the boundary is the definitional line between "open weights" and "open source."

<!-- AUTO:MEMBERS BEGIN -->
## Key Members (auto-extracted, top 15 by intra-cluster connectivity)

**Entities** (3)
- [[OpenSourceInitiative]]
- [[FreeSoftwareFoundation]]
- [[Mozilla]]

**Concepts** (2)
- [[TrainingData]]
- [[OpenSourceAI]]
<!-- AUTO:MEMBERS END -->

<!-- AUTO:SOURCES BEGIN -->
## Sources

4 total — see [Open-Source AI Definition catalog](../sources/_catalog-open-source-ai-definition.md).

Top 4 by weight:
- [[case-against-osaid]] _(w=0.67)_
- [[mozilla-celebrates-osaid]] _(w=0.67)_
- [[open-source-ai-models-how-open]] _(w=0.43)_
- [[osi-open-source-ai-definition]] _(w=0.43)_
<!-- AUTO:SOURCES END -->
