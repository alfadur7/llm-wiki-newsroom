---
title: "Open Weights"
type: overview
tags: []
cluster: open-weights
sources: []
last_updated: 2026-06-26
---

# Open Weights

## Overview

[[OpenWeights|Open weights]] is the release model that sits between fully proprietary systems and the strict [[OpenSourceAI]] standard: a provider publishes the trained weights and parameters needed to run a model but withholds the training data, detailed data information, and training algorithms. The leading example is [[DeepSeek]]'s R1, released in 2025-01 under the permissive MIT license, whose weights are public while its training corpus is not. This cluster is documented by a single legal-primer source, so its claims are best read as an `[analysis]`-grade framing of an emerging category rather than a settled standard.

The category matters because it captures most of what the market actually ships under the "open" banner. Publishing weights lets a user run and [[FineTuning|fine-tune]] a model on its own data without paying licensing fees or training from scratch, which is attractive to organizations that need a customized model but lack the resources to build one. The trade-off, the primer stresses, is that an open-weights release does not let a user fully understand, reproduce, or audit the underlying model — including its inherent biases — because the data and algorithms are unavailable.

The cluster's anchor concepts are [[OpenWeights]] (the release posture) and [[FineTuning]] (the capability it unlocks), with [[DeepSeek]] as the worked example. R1 drew attention partly on cost claims — roughly $6 million to train, a fraction of comparable models — which sharpened the appeal of a weights-only release that others can adapt cheaply.

The tension axis here is **practical adaptability vs. genuine transparency**. Proponents see open weights as a pragmatic balance that works for many providers and users at this early stage of LLM development; the stricter camp behind the [[OpenSourceAI]] definition sees it as precisely the partial release the OSAID was written to exclude. Whether "open weights" hardens into a respected middle category or becomes a synonym for [[OpenWashing]] depends on how that line holds.

## Recent Changes

- 2025-05-19 — A legal primer frames the open-weights middle ground against the OSAID, using [[DeepSeek]] R1 as the leading example.
- 2025-01 — [[DeepSeek]] releases R1 with MIT-licensed weights but a withheld training corpus, the cluster's defining case.
- Stable period since: the category is new and still lightly documented in this wiki.

## Key Entities & Concepts

The single **provider** documented here is [[DeepSeek]], whose R1 is the canonical open-weights release. The two anchor **concepts** are [[OpenWeights]], the release posture that publishes parameters while keeping training data secret, and [[FineTuning]], the adaptation capability that makes a weights-only release useful. The cluster is defined by what it contrasts against — the fuller [[OpenSourceAI]] standard — rather than by a dense roster of actors.

## Subtopics

The **weights-without-data bargain** is the core of the cluster. Because the weights are published, a user can adapt the model rapidly via [[FineTuning]] without ever seeing the original [[TrainingData]]; that same omission is why an open-weights model cannot be fully audited or reproduced. The bargain is what separates this category from full [[OpenSourceAI]].

The **licensing-vs-completeness distinction** matters because a permissive license does not by itself make a release open. [[DeepSeek]] ships R1's weights under MIT, yet R1 is still classified as open weights rather than open source because the data component is missing — a reminder that license text and component completeness are independent axes, examined further under [[licensing-open-washing|the licensing field]].

- **Cost as a driver** — R1's roughly $6 million training-cost claim made a cheap-to-adapt, weights-only release commercially compelling.
- **Reproducibility gap** — without training data or algorithms, inherent biases and failure modes cannot be independently verified.

## Key Trends & Figures

**Defining releases**
- 2025-01: [[DeepSeek]] R1, MIT-licensed weights, withheld training data.
- Roughly $6 million reported training cost, a fraction of comparable models.

**Category framing**
- 2025-05-19: open weights positioned as an early-stage balance between proprietary and fully open.
- Distinguished from [[OpenSourceAI]] by the absence of data information and training code.

**Capability profile**
- Enables [[FineTuning]] on user data without retraining from scratch.
- Blocks full audit, reproduction, and bias inspection.

## Adjacent Domains & Scope

- [[open-source-ai-definition|Open-Source AI Definition]] — sets the strict standard that open-weights releases deliberately fall short of; this cluster covers the middle ground, not the definitional bar itself.
- [[licensing-open-washing|Licensing & Open-Washing]] — covers how license terms and partial releases can blur into open-washing; this cluster covers the weights-release model that such labeling is often applied to.

<!-- AUTO:MEMBERS BEGIN -->
## Key Members (auto-extracted, top 15 by intra-cluster connectivity)

**Entities** (1)
- [[DeepSeek]]

**Concepts** (2)
- [[OpenWeights]]
- [[FineTuning]]
<!-- AUTO:MEMBERS END -->

<!-- AUTO:SOURCES BEGIN -->
## Sources

1 total — see [Open Weights catalog](../sources/_catalog-open-weights.md).

Top 1 by weight:
- [[open-source-ai-models-how-open]] _(w=0.43)_
<!-- AUTO:SOURCES END -->
