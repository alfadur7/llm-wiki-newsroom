---
title: "Licensing & Open-Washing"
type: overview
tags: []
cluster: licensing-open-washing
sources: []
last_updated: 2026-06-26
---

# Licensing & Open-Washing

## Overview

This cluster covers the legal and rhetorical machinery of "open" AI: [[ModelLicensing]], the terms that govern how a model may be used, modified, and redistributed, and [[OpenWashing]], the practice of claiming the open-source brand while withholding components or attaching restrictions. The recurring case is [[Meta]]'s Llama, released in early 2023 under a custom community license that markets the model as open while imposing usage restrictions — which the [[OpenSourceInitiative]] cites as non-compliant with the [[OpenSourceAI]] definition. The 3 sources here carry a mix of `[fact]` license descriptions and `[analysis]` claims about why the labeling matters.

Licensing is where open-source AI diverges from open-source software. Conventional licenses split into permissive families (MIT, BSD, Apache 2.0) that impose few obligations and copyleft families (GPL, Affero GPL) that require sharing derivatives under the same terms. But a model adds components beyond software — data, data information, weights, parameters — so a software license alone cannot make a model open. That gap is the opening that open-washing exploits.

[[OpenWashing]] matters because the "open source" label carries reputational and, increasingly, regulatory weight. The [[OpenSourceInitiative]] frames it as a primary motivation for the OSAID, naming [[Meta]]'s Llama as a confusing example; researchers argue the consequences for innovation, research, and public understanding are considerable. [[Mozilla]] echoes the concern, citing "open-ish models like Meta's Llama 3" as exactly what a clear definition should sort out.

The tension axis is **a permissive license as sufficient signal vs. component completeness as the real test**. One reading treats a familiar license like MIT as the marker of openness; the other holds that license text is independent of whether the data and code that make a model reproducible are actually released. [[DeepSeek]]'s R1 sharpens the point — MIT-licensed weights, withheld data — showing a permissive license and a fully open model are not the same thing.

## Recent Changes

- 2024-12-05 — Renewed criticism frames the open-source label as a licensing-and-completeness dispute, with [[OpenWashing]] fears at the center.
- 2024-10-28 — [[OpenSourceInitiative]] names [[Meta]]'s Llama as non-compliant, making it the reference open-washing case.
- Stable period since: the licensing debate tracks the broader definition fight rather than moving independently.

## Key Entities & Concepts

The **issuer at the center** is [[Meta]], whose Llama community license is the most-cited contested case. The **standard-setter** judging those terms is the [[OpenSourceInitiative]]; [[Mozilla]] is the **advocate** that frames clear licensing as a remedy. The two anchor **concepts** are [[ModelLicensing]] (the terms themselves) and [[OpenWashing]] (the misuse of the label), with [[DeepSeek]]'s MIT-licensed R1 recurring as the contrast case.

## Subtopics

The **permissive-vs-copyleft inheritance** is the starting point. Open-source AI borrows its license vocabulary from software — MIT and Apache on the permissive side, GPL on the copyleft side — but [[ModelLicensing]] must stretch to cover data and weights that software licenses never addressed, which is why a familiar license name no longer guarantees an open model.

The **custom-license problem** is where [[OpenWashing]] enters. [[Meta]]'s Llama uses a bespoke community license with usage restrictions that the [[OpenSourceInitiative]] judges incompatible with the [[OpenSourceAI]] freedoms; the marketing says "open," the terms say otherwise. This gap between brand and license is the open-washing mechanism, and it links directly to [[open-training-data-requirement|the dispute over what "open" must include]].

- **Regulatory stakes** — as "open source" enters law, a soft definition lets restricted models claim benefits intended for genuinely open ones.
- **License vs. completeness** — [[DeepSeek]] R1's MIT weights show a permissive license can still accompany an incomplete (data-less) release.

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

<!-- AUTO:MEMBERS BEGIN -->
## Key Members (auto-extracted, top 15 by intra-cluster connectivity)

**Entities** (1)
- [[Meta]]

**Concepts** (2)
- [[ModelLicensing]]
- [[OpenWashing]]
<!-- AUTO:MEMBERS END -->

<!-- AUTO:SOURCES BEGIN -->
## Sources

3 total — see [Licensing & Open-Washing catalog](../sources/_catalog-licensing-open-washing.md).

Top 3 by weight:
- [[osi-open-source-ai-definition]] _(w=0.43)_
- [[case-against-osaid]] _(w=0.33)_
- [[mozilla-celebrates-osaid]] _(w=0.33)_
<!-- AUTO:SOURCES END -->
