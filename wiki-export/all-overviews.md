# All OVERVIEWS (3)

---

---
title: "Licensing & Open-Washing"
type: overview
tags: []
cluster: licensing-open-washing
sources: []
last_updated: 2026-07-17
---

# Licensing & Open-Washing

## Overview

This cluster covers the legal and rhetorical machinery of "open" AI: [[ModelLicensing]], the terms that govern how a model may be used, modified, and redistributed, and [[OpenWashing]], the practice of claiming the open-source brand while withholding components or attaching restrictions. The recurring case is [[Meta]]'s Llama, released in early 2023 under a custom community license that markets the model as open while imposing usage restrictions — which the [[OpenSourceInitiative]] cites as non-compliant with the [[OpenSourceAI]] definition. The 3 sources here carry a mix of `[fact]` license descriptions and `[analysis]` claims about why the labeling matters.

Licensing is where open-source AI diverges from open-source software. Conventional licenses split into permissive families (MIT, BSD, Apache 2.0) that impose few obligations and copyleft families (GPL, Affero GPL) that require sharing derivatives under the same terms. But a model adds components beyond software — data, data information, weights, parameters — so a software license alone cannot make a model open. That gap is the opening that open-washing exploits.

[[OpenWashing]] matters because the "open source" label carries reputational and, increasingly, regulatory weight. The [[OpenSourceInitiative]] frames it as a primary motivation for the OSAID, naming [[Meta]]'s Llama as a confusing example; researchers argue the consequences for innovation, research, and public understanding are considerable. [[Mozilla]] echoes the concern, citing "open-ish models like Meta's Llama 3" as exactly what a clear definition should sort out. But critics read it the other way: a camp anchored by the [[FreeSoftwareFoundation]] argues the OSAID's silence on [[TrainingData|training data]] risks legitimizing the open-washing it set out to name.

The tension axis is **a permissive license as sufficient signal vs. component completeness as the real test**. One reading treats a familiar license like MIT as the marker of openness; the other holds that license text is independent of whether the data and code that make a model reproducible are actually released. [[DeepSeek]]'s R1 sharpens the point — MIT-licensed weights, withheld data — showing a permissive license and a fully open model are not the same thing.

## Recent Changes

- 2024-12-05 — [[case-against-osaid|A roundup of OSAID criticism]] frames the open-source label as a licensing-and-completeness dispute, with [[OpenWashing]] fears at the center.
- 2024-10-28 — [[OpenSourceInitiative]] names [[Meta]]'s Llama as non-compliant, making it the reference open-washing case.
- Stable period since: the licensing debate tracks the broader definition fight rather than moving independently.

## Key Entities & Concepts

The **issuer at the center** is [[Meta]], whose Llama community license is the most-cited contested case. The **standard-setter** judging those terms is the [[OpenSourceInitiative]]; [[Mozilla]] is the **advocate** that frames clear licensing as a remedy. The **critics** are the countervailing camp — the [[FreeSoftwareFoundation]], alongside Open Source Initiative co-founder Bruce Perens and the Software Freedom Conservancy's Bradley Kuhn. Their [[case-against-osaid|case against the OSAID]] `contradicts:` the [[OpenSourceAI]] standard as "less than Open Source," fearing its data carve-out lets restricted models keep the open label. The two anchor **concepts** are [[ModelLicensing]] (the terms themselves) and [[OpenWashing]] (the misuse of the label), with [[DeepSeek]]'s MIT-licensed R1 recurring as the contrast case.

## Subtopics

The **permissive-vs-copyleft inheritance** is the starting point. Open-source AI borrows its license vocabulary from software — MIT and Apache on the permissive side, GPL on the copyleft side — but [[ModelLicensing]] must stretch to cover data and weights that software licenses never addressed, which is why a familiar license name no longer guarantees an open model.

The **custom-license problem** is where [[OpenWashing]] enters. [[Meta]]'s Llama uses a bespoke community license with usage restrictions that the [[OpenSourceInitiative]] judges incompatible with the [[OpenSourceAI]] freedoms; the marketing says "open," the terms say otherwise. This gap between brand and license is the open-washing mechanism, and it links directly to [[open-training-data-requirement|the dispute over what "open" must include]].

- **Regulatory stakes** — as "open source" enters law, a soft definition lets restricted models claim benefits intended for genuinely open ones.
- **License vs. completeness** — [[DeepSeek]] R1's MIT weights show a permissive license can still accompany an incomplete (data-less) release. [[open-source-ai-every-camp-standard|What clears every camp's bar]] traces which releases survive the stricter, data-inclusive test.

## Key Trends & Figures

**Contested licenses**
- [[Meta]]'s Llama: custom community license with usage restrictions, judged non-compliant.
- [[DeepSeek]] R1: permissive MIT weights, but withheld training data.

**License families**
- Permissive: MIT, BSD, Apache 2.0 — few obligations.
- Copyleft: GPL 2.0/3.0, Affero GPL — share-alike requirements.

**Open-washing signals**
- 2024-10-28: [[OpenSourceInitiative]] names Llama as the reference confusing case.
- Researchers flag considerable consequences for innovation and public understanding.

## Adjacent Domains & Scope

- [[open-source-ai-definition|Open-Source AI Definition]] — sets the standard that license terms are judged against; this cluster covers the terms and the labeling practice, not the definition that adjudicates them.
- [[open-weights|Open Weights]] — covers the weights-only release model that permissive licenses are often applied to; this cluster covers the licensing and labeling layer around such releases.

## Key Members (auto-extracted, top 15 by intra-cluster connectivity)

**Entities** (1)
- [[Meta]]

**Concepts** (2)
- [[ModelLicensing]]
- [[OpenWashing]]

## Sources

3 total — see Licensing & Open-Washing catalog.

Top 3 by weight:
- [[osi-open-source-ai-definition]] _(w=0.43)_
- [[case-against-osaid]] _(w=0.33)_
- [[mozilla-celebrates-osaid]] _(w=0.33)_



---

---
title: "Open-Source AI Definition"
type: overview
tags: []
cluster: open-source-ai-definition
sources: []
last_updated: 2026-07-19
---

# Open-Source AI Definition

## Overview

On 2024-10-28 the [[OpenSourceInitiative]] released the [[OpenSourceAI|Open Source AI Definition]] (OSAID) 1.0, the first attempt to settle what "open source" means once a system is a trained model rather than software alone. The definition is deliberately binary: a system either grants the four freedoms — to use, study, modify, and share for any purpose without permission — or it does not. To qualify, a release must provide three components: data information, complete source code, and model parameters. OSI validated a short list of compliant models (Pythia, OLMo, Amber, CrystalCoder, T5) and judged [[Meta]]'s Llama 2 non-compliant.

The definition matters because traditional software licenses never anticipated [[TrainingData]], weights, and the cost of reproducing a model from scratch. OSI frames a clear binary standard as the precondition for two things its leadership cares about: informing regulators who increasingly write "open source" into law, and curbing [[OpenWashing]], the practice of claiming the open-source brand while withholding components. The 4 source pages in this cluster are dominated by `[fact]`- and `[analysis]`-grade claims, with [[OpenSourceInitiative]] as the recurring claimant on the definitional side.

The OSAID was produced through a multi-year co-design process and was endorsed by at least 20 organizations, [[Mozilla]] prominent among them. Yet the same document that compliant-model validation rests on was approved by OSI's 10-person board rather than a full membership vote — a procedural fact critics return to. The most contested design choice is that OSAID requires "data information" (enough detail to recreate a substantially equivalent system) rather than the raw dataset itself, on the argument that some data, such as medical records, cannot be legally shared.

The cluster therefore organizes around one tension axis: **a workable binary standard vs. a maximalist open-data requirement**. Endorsers ([[Mozilla]], OSI) argue a shared, imperfect-but-clear definition is more useful to developers and regulators today than waiting for a stricter one; critics led by the [[FreeSoftwareFoundation]] hold that without the raw training data the label is hollow, since the data is effectively the source code. How that axis resolves will shape whether "open source AI" converges on one standard or fractures into competing definitions.

## Recent Changes

- 2024-12-05 — Coverage rounds up the growing criticism of the OSAID over its omission of open training data, with critics from Debian, the Software Freedom Conservancy, and OSI's own co-founder leading the dissent.
- 2024-10-28 — [[OpenSourceInitiative]] publishes OSAID 1.0 and the validated-model list; [[Mozilla]] endorses it the same day.
- Stable period since: no new material has entered this cluster since 2024-12-05 — roughly 19 months as of 2026-07-19, during which this corpus records no outcome for the board-repeal campaign.

## Key Entities & Concepts

The cluster splits into three roles. The **standard-setter** is [[OpenSourceInitiative]], author and steward of the OSAID. The **endorser** wing is led by [[Mozilla]], which frames openness as an AI-safety precondition and defends the data-information requirement as already stricter than most releases. The **dissenter** wing is anchored by the [[FreeSoftwareFoundation]], building a stricter open-data alternative, with critics from Debian and the Software Freedom Conservancy alongside it. The two anchor concepts are [[OpenSourceAI]] (the definition itself) and [[TrainingData]] (the component the camps fight over); [[OpenWashing]] is the practice the definition is meant to constrain.

## Subtopics

The **data-information compromise** is the heart of the cluster. OSAID requires enough detail to recreate a substantially equivalent system rather than the raw [[TrainingData]], a deliberate concession to fields like medical AI where datasets cannot be legally shared. Endorsers read this as pragmatic; the [[FreeSoftwareFoundation]] reads it as fatal, holding that data and processing scripts must respect the four freedoms or the model is not free. This axis is analysed in depth in [[open-training-data-requirement|the open-training-data dispute]].

Yet the endorser position is not static acceptance. [[Mozilla]] backs the standard as "an important step forward" while acknowledging some disagree with aspects such as its training-data treatment, and that "the definition will need refinement over time" ([[mozilla-celebrates-osaid|its endorsement post]]). Having convened experts with EleutherAI on open-dataset norms, its [forecast]-grade intent is to raise the data bar over time.

Critics reject the refinement-over-time framing: they hold the data omission is disqualifying now, not a defect to be fixed later. A companion analysis, [[open-source-ai-every-camp-standard|what clears every camp's bar]], finds no model documented as clearing both bars: open-data releases exist, but none is tied to a validated model, and the corpus never addresses processing scripts or data licenses.

The **binary-vs-spectrum question** is the second axis. [[OpenSourceAI]] is intentionally all-or-nothing so that regulators and civil society can tell genuinely open systems from marketing, and so [[OpenWashing]] has a clear line to fall on the wrong side of. Critics counter that a binary that admits data-less models simply moves the open-washing line rather than removing it.

- **Procedural legitimacy** — the OSAID was approved by OSI's 10-person board rather than a full membership vote, which Debian developer Sam Johnston cites when arguing the standard lacks community mandate.
- **Validation as enforcement** — by publishing a compliant list (Pythia, OLMo, Amber, CrystalCoder, T5) and a non-compliant verdict on [[Meta]]'s Llama 2, OSI turned the definition into a working test rather than an abstract principle.
- **Proof-of-viability models** — Pleias's fully open dataset, Ai2's open-training-data LLMs, and AMD's "fully open" 1B models are offered as evidence the open-data path is achievable, undercutting the "niche-only" defense. None is tied to the OSAID-validated OLMo specifically. OSAID validation does not itself establish open data: the definition requires data *information*, not the dataset.

## Key Trends & Figures

**Definition milestones**
- 2024-10-28: OSAID 1.0 released by [[OpenSourceInitiative]] after a multi-year co-design process.
- Endorsed by at least 20 organizations on launch, including [[Mozilla]].

**Compliance verdicts**
- Validated as compliant: Pythia, OLMo, Amber, CrystalCoder, T5.
- Judged non-compliant: [[Meta]]'s Llama 2, alongside Grok, Phi-2, and Mixtral, for missing components and conflicting license terms.

**Governance signals**
- Approved by a 10-person board rather than full membership.
- 2024-12: a campaign announced to run for the OSI board on a platform to repeal the OSAID.

## Adjacent Domains & Scope

- [[licensing-open-washing|Licensing & Open-Washing]] — covers the license-term mechanics and the Llama open-washing case; this cluster covers the definition that judges those terms, not the terms themselves.
- [[open-weights|Open Weights]] — covers the weights-only middle ground that the OSAID explicitly does not accept as fully open; the boundary is the definitional line between "open weights" and "open source."

## Key Members (auto-extracted, top 15 by intra-cluster connectivity)

**Entities** (3)
- [[OpenSourceInitiative]]
- [[FreeSoftwareFoundation]]
- [[Mozilla]]

**Concepts** (2)
- [[OpenSourceAI]]
- [[TrainingData]]

## Sources

4 total — see Open-Source AI Definition catalog.

Top 4 by weight:
- [[case-against-osaid]] _(w=0.67)_
- [[mozilla-celebrates-osaid]] _(w=0.67)_
- [[open-source-ai-models-how-open]] _(w=0.43)_
- [[osi-open-source-ai-definition]] _(w=0.43)_



---

---
title: "Open Weights"
type: overview
tags: []
cluster: open-weights
sources: []
last_updated: 2026-09-15
---

# Open Weights

## Overview

[[OpenWeights|Open weights]] is the release model that sits between fully proprietary systems and the strict [[OpenSourceAI]] standard: a provider publishes the trained weights and parameters needed to run a model but withholds the training data, detailed data information, and training algorithms. The leading example is [[DeepSeek]]'s R1, released in 2025-01 under the permissive MIT license, whose weights are public while its training corpus is not. This cluster is documented by a single legal-primer source, so its claims are best read as an `[analysis]`-grade framing of an emerging category rather than a settled standard.

The category matters because it captures most of what the market actually ships under the "open" banner. Publishing weights lets a user run and [[FineTuning|fine-tune]] a model on its own data without paying licensing fees or training from scratch, which is attractive to organizations that need a customized model but lack the resources to build one. The trade-off, the primer stresses, is that an open-weights release does not let a user fully understand, reproduce, or audit the underlying model — including its inherent biases — because the data and algorithms are unavailable.

The cluster's anchor concepts are [[OpenWeights]] (the release posture) and [[FineTuning]] (the capability it unlocks), with [[DeepSeek]] as the worked example. R1 drew attention partly on cost claims — roughly $6 million to train, a fraction of what similarly performing LLMs cost — which sharpened the appeal of a weights-only release that others can adapt cheaply.

The tension axis here is **practical adaptability vs. genuine transparency**. Proponents see open weights as a pragmatic balance that works for many providers and users at this early stage of LLM development; the stricter camp behind the [[OpenSourceAI]] definition sees it as precisely the partial release the OSAID was written to exclude. Whether "open weights" hardens into a respected middle category or becomes a synonym for [[OpenWashing]] depends on how that line holds.

## Recent Changes

- 2025-05-19 — A legal primer frames the open-weights middle ground against the OSAID, using [[DeepSeek]] R1 as the leading example.
- 2025-01 — [[DeepSeek]] releases R1 with MIT-licensed weights but a withheld training corpus, the cluster's defining case.
- Stable period since: the category is new and still lightly documented in this wiki.

## Key Entities & Concepts

The **provider** documented here is [[DeepSeek]], whose R1 is the canonical open-weights release; the source also counts Mistral AI's Pixtral Large, xAI's Grok-1 and Alibaba's Qwen 3 as open weights, none of them documented in this wiki yet. The two anchor **concepts** are [[OpenWeights]], the release posture that publishes parameters while keeping training data secret, and [[FineTuning]], the adaptation capability that makes a weights-only release useful. The cluster is defined by what it contrasts against — the fuller [[OpenSourceAI]] standard — rather than by the size of its roster.

## Subtopics

The **weights-without-data bargain** is the core of the cluster. Because the weights are published, a user can adapt the model rapidly via [[FineTuning]] without ever seeing the original [[TrainingData]]; that same omission is why an open-weights model cannot be fully audited or reproduced. The bargain is what separates this category from full [[OpenSourceAI]].

The **licensing-vs-completeness distinction** matters because a permissive license does not by itself make a release open. [[DeepSeek]] ships R1's weights under MIT, yet R1 is still classified as open weights rather than open source because the data component is missing — a reminder that license text and component completeness are independent axes, examined further under [[licensing-open-washing|the licensing field]].

- **Cost as a driver** — R1's roughly $6 million training-cost claim, set against what similarly performing LLMs cost to train, made a cheap-to-adapt, weights-only release commercially compelling.
- **Reproducibility gap** — without training data or algorithms, inherent biases and failure modes cannot be independently verified.

## Key Trends & Figures

**Defining releases**
- 2025-01: [[DeepSeek]] R1, MIT-licensed weights, withheld training data.
- Roughly $6 million reported training cost, a fraction of what similarly performing LLMs cost to train.

**Category framing**
- 2025-05-19: open weights positioned as an early-stage balance between proprietary and fully open.
- Distinguished from [[OpenSourceAI]] by the absence of data information and training code.

**Capability profile**
- Enables [[FineTuning]] on user data without retraining from scratch.
- Blocks full audit, reproduction, and bias inspection.

## Adjacent Domains & Scope

- [[open-source-ai-definition|Open-Source AI Definition]] — sets the strict standard that open-weights releases deliberately fall short of; this cluster covers the middle ground, not the definitional bar itself.
- [[licensing-open-washing|Licensing & Open-Washing]] — covers how license terms and partial releases can blur into open-washing; this cluster covers the weights-release model that such labeling is often applied to.

## Key Members (auto-extracted, top 15 by intra-cluster connectivity)

**Entities** (1)
- [[DeepSeek]]

**Concepts** (2)
- [[OpenWeights]]
- [[FineTuning]]

## Sources

1 total — see Open Weights catalog.

Top 1 by weight:
- [[open-source-ai-models-how-open]] _(w=0.43)_


