---
title: "Considering the OpenMDW license"
type: source
tags: [licensing, open-source-ai, open-weights]
published: 2026-08-21
scraped: 2026-09-27
source_file: raw/NewsScrap/Considering the OpenMDW license.md
source_url: "https://lwn.net/Articles/1089251/"
last_updated: 2026-09-27
---

## Summary

LWN's Jonathan Corbet reports, in an article dated 2026-08-21, on the discussion after the [[LinuxFoundation|Linux Foundation]]'s Mike Dolan submitted the [[OpenMDW]] ("Open Model, Data, and Weights") license to the [[OpenSourceInitiative|Open Source Initiative]] (OSI) for approval. OpenMDW is a permissive, MIT-like license meant to cover a whole model distribution under one license. Reviewers on the OSI list objected to a disclaimer that makes users responsible for clearing third-party rights and to a termination clause that ends all rights if the licensee sues over patent or copyright infringement by the model materials, which Dolan defended as symmetry. Corbet writes that the discussion wound down without a clear outcome and that the OSI does not appear ready to approve the license in its current form.

## Key Claims

- [fact] Jonathan Corbet — reports that the Linux Foundation's Mike Dolan brought the OpenMDW ("Open Model, Data, and Weights") license to the [[OpenSourceInitiative]] for approval
- [analysis] Jonathan Corbet — describes the OSI's process for developing its [[OpenSourceAI|Open Source AI Definition]] as "controversial at best", along with its output
- [analysis] Mike Dolan — explained that model distributions bundle software, model weights, documentation and other artifacts, while existing licenses focus on software and tend not to address model output
- [analysis] Jonathan Corbet — characterizes OpenMDW at its core as a permissive license similar to the MIT license, aimed at letting distributors place a whole open model under a single license within [[ModelLicensing|model licensing]]
- [fact] Jonathan Corbet — reports that OpenMDW states explicitly that it imposes no restrictions on any output created by the model
- [fact] Jonathan Corbet — reports that OpenMDW grants "all copyright, patent, database, and trade secret rights" represented by the model distribution
- [fact] Jonathan Corbet — reports that the license's all-caps disclaimer makes the user solely responsible for clearing other persons' rights in the model materials, obtaining any needed consents, and performing any due diligence
- [analysis] Pamela Chestek — called clearing those rights "an impossibility generally", particularly when there is no disclosure of the [[TrainingData|training materials]]
- [analysis] Pamela Chestek — said the disclaimer could be read as a licensor requirement, so a user sued for copyright infringement could also be accused of violating the license
- [fact] Jonathan Corbet — reports that OpenMDW terminates all rights of a licensee who files, maintains, or voluntarily joins a lawsuit asserting that the model materials infringe any patent or copyright, unless the suit answers one first brought against them
- [analysis] Richard Fontana — argued the termination clause is too broad because it covers copyright as well as patent claims and extends to seemingly unrelated materials such as Python code distributed along with the model
- [analysis] Richard Fontana — suggested that terminating rights to unrelated materials could violate section 9 of the [[OpenSourceDefinition|Open Source Definition]], which prohibits restrictions on unrelated software
- [analysis] Richard Fontana — said the license's "Model Materials" term is not well defined
- [analysis] Richard Fontana — suggested restricting termination to the model weights at issue
- [analysis] Rob Landley — asked whether a code owner who sues a third-party fork that incorporated their proprietary code would lose access to the original OpenMDW-licensed project
- [analysis] Kevin Fleming — pointed out that a copyright holder can usually show infringement only by exercising the model, yet suing ends their access to the model they need for evidence
- [analysis] Simon Phipps — said that "a license revoking Freedom 0 upon a copyright claim cannot assure software freedom"
- [analysis] Mike Dolan — responded that the termination clause gives the license symmetry, so a party cannot argue a distribution infringes while still enjoying its usage rights
- [analysis] Mike Dolan — argued that model publishers' main legal exposure is copyright claims over the works models are built from, so a patent-only clause would copy Apache-2.0's form without its function
- [analysis] Eric Schultz — called the termination clause "an amnesty for, depending on how courts rule, large scale copyright infringement by model creators"
- [analysis] Pamela Chestek — said the license is not symmetric, since the model producer may know whether it copied copyrighted material while the recipient must give up copyright claims without knowing
- [analysis] Jonathan Corbet — writes that the conversation wound down without a clear outcome and that the OSI does not appear ready to approve the license in its current form
- [analysis] Jonathan Corbet — writes that the changes that would make OpenMDW acceptable have been neither specified nor accepted by its proponents
- [analysis] Jonathan Corbet — argues that OpenMDW aims to reduce distributors' risk of copyright or patent suits over a model's training or output, while signaling that using LLMs may itself prove risky

## Key Quotes

> "an impossibility generally, and particularly if there is not even any disclosure of what the training materials are" — Pamela Chestek, OSI license-review participant

> "Not only does the license extend termination to copyright litigation, it also broadens the scope of termination by covering seemingly unrelated materials. For example, suppose I believe that an OpenMDW-1.1-licensed model infringes my copyrights. I sue the model licensor, but now my copyright and patent rights to some Python code distributed (in some sense) along with the model are terminated." — Richard Fontana, OSI license-review participant

> "a license revoking Freedom 0 upon a copyright claim cannot assure software freedom" — Simon Phipps, OSI license-review participant

> "Models are built from large bodies of existing works, and that is where the model publisher's legal exposure arises. For those model publishers, the realistic assertion they face is that the licensed materials themselves infringe, and that infringement claim likely runs under copyright, not patent law. A patent-only provision in this context would replicate Apache-2.0's form while abandoning its function - there would not be symmetry." — Mike Dolan, [[LinuxFoundation|Linux Foundation]]

> "an amnesty for, depending on how courts rule, large scale copyright infringement by model creators" — Eric Schultz, OSI license-review participant

## Connections

- references: [[OpenSourceInitiative]] — OpenMDW was submitted to the OSI for approval, and the review took place on its license-review list
- references: [[OpenMDW]] — the license under review: its permissive grant, rights-clearing disclaimer and termination clause, and the objections to them
- cites: [[LinuxFoundation]] — quotes the Linux Foundation's Mike Dolan submitting OpenMDW and defending its termination clause as symmetry
- references: [[ModelLicensing]] — OpenMDW is a single permissive license for a whole model distribution
- references: [[OpenSourceDefinition]] — Fontana argues the termination clause may conflict with OSD section 9
- references: [[OpenSourceAI]] — Corbet frames the license against the OSI's contested Open Source AI Definition
- references: [[TrainingData]] — Chestek ties the impossibility of clearing rights to undisclosed training materials
- contradicts: [[openmdw-1-1-nvidia-adoption|Linux Foundation OpenMDW-1.1 release]] — the Linux Foundation presents OpenMDW as a clear, permissive framework, while OSI reviewers call its grant fuzzy, its termination clause overbroad, and its rights-clearing duty impossible
