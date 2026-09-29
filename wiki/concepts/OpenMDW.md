---
title: "OpenMDW"
type: concept
tags: [licensing, open-source-ai, open-weights, model-licensing]
sources: [openmdw-1-1-nvidia-adoption, lwn-openmdw-license-review, open-weights-not-open-source-label-dispute, eu-ai-act-gpai-guide-open-source-developers]
last_updated: 2026-09-27
---

## Overview

OpenMDW (Open Model, Data and Weights) is a permissive license for AI model distributions published by the [[LinuxFoundation|Linux Foundation]], which says it launched the license in 2025 together with the PyTorch Foundation and released version 1.1 on 2026-05-28 ([[openmdw-1-1-nvidia-adoption]]). According to the Linux Foundation, the license covers models (architecture, weights and parameters), code, documentation and data, giving a model and its related artifacts one legal framework; the same announcement says Nvidia plans to adopt OpenMDW-1.1 for future releases of its Cosmos, Isaac GR00T, Ising and Nemotron model families. The Linux Foundation presents it as filling a gap left by software licenses not designed for AI artifacts and by custom AI licenses with restrictive usage terms. It is one named license within the broader question of [[ModelLicensing|model licensing]].

LWN's Jonathan Corbet characterizes OpenMDW as a permissive license similar to the MIT license that places no restrictions on model output and grants "all copyright, patent, database, and trade secret rights" in the distribution ([[lwn-openmdw-license-review]]). Steven J. Vaughan-Nichols of The Register reports that the license lists contributors from Amazon, [[Meta]], IBM, Microsoft and Nvidia, and describes it as setting separate terms for architecture, training data and weights under one agreement ([[open-weights-not-open-source-label-dispute]]).

## Key Points

- **OSI review** — the Linux Foundation's Mike Dolan submitted OpenMDW to the [[OpenSourceInitiative|Open Source Initiative]] (OSI) for approval. Reviewers on the OSI list objected to a disclaimer that makes users responsible for clearing third-party rights and to a termination clause that ends a licensee's rights if it sues over patent or copyright infringement by the model materials. Pamela Chestek called clearing those rights "an impossibility generally," and Richard Fontana argued the termination clause is too broad because it covers copyright as well as patent claims and extends to seemingly unrelated materials; Dolan defended the clause as symmetry. As of LWN's 2026-08-21 report, Corbet writes that the discussion wound down without a clear outcome and that the OSI did not appear ready to approve the license in its current form ([[lwn-openmdw-license-review]]).
- **Bias charge** — former OSI executive director [[StefanoMaffulli|Stefano Maffulli]] says the review appears "tainted by an ideological bias" against big tech; Vaughan-Nichols calls the approach reasonable but reaches no verdict on whether the OSI will adopt it ([[open-weights-not-open-source-label-dispute]]).
- **EU AI Act** — researchers from [[HuggingFace|Hugging Face]], [[Mozilla]] and the Linux Foundation judge that the [[EUAIAct|EU AI Act]]'s free and open-source license definition likely covers OpenMDW alongside Apache 2.0 and MIT, in a guide that states it is not legal advice ([[eu-ai-act-gpai-guide-open-source-developers]]).

## Connections

- [[ModelLicensing]] — the broader concept; OpenMDW is one named model license
- [[LinuxFoundation]] — publisher of OpenMDW and its 1.1 release
- [[OpenSourceInitiative]] — the body whose license review OpenMDW entered
- [[StefanoMaffulli]] — charges that the OSI review is ideologically biased
- [[Meta]] — listed among OpenMDW's contributors
- [[EUAIAct]] — whose open-source license definition likely covers OpenMDW, per the Hugging Face guide
- [[HuggingFace]] — host and co-author of the EU AI Act guide
- [[Mozilla]] — co-author of the EU AI Act guide
- [[openmdw-1-1-nvidia-adoption]] — Linux Foundation release of OpenMDW-1.1 and Nvidia's adoption
- [[lwn-openmdw-license-review]] — LWN on the OSI license-review discussion
- [[open-weights-not-open-source-label-dispute]] — The Register on the submission and the bias charge
- [[eu-ai-act-gpai-guide-open-source-developers]] — EU AI Act guide expecting OpenMDW to qualify
