---
title: "Distillation"
type: concept
tags: [distillation, open-weights, ai-policy, model-training]
sources: [open-weights-american-ai-leadership, deepseek-r1-release, open-source-ai-path-forward, anthropic-position-open-weights-models]
last_updated: 2026-09-23
---

## Overview

Distillation is described by the signatories of the 2026 open weights letter as training one model on another model's outputs, a technique they call widely used for model improvement, evaluation, and validation. It differs from [[FineTuning]], which continues training a model on additional data: in distillation the training signal is a second model's outputs, and the usual product is a smaller model. In its DeepSeek-R1 announcement, [[DeepSeek]] released six small models distilled from R1, which it calls fully open-sourced, moved R1's code and models to the MIT License, and stated that R1's API (application programming interface) outputs may now be used for fine-tuning and distillation; it claims its distilled 32B and 70B models perform on par with OpenAI-o1-mini. In the 2024 Llama 3.1 letter, Mark Zuckerberg of [[Meta]] presents distilling a model to an organization's optimal size as a developer benefit of what he calls open source AI (the wiki's [[OpenWeights|open weights]] release model), expects the 405B model to be the best choice for distilling smaller models, and states that Amazon, Databricks, and NVIDIA were launching services to distill Llama models.

## Policy Positions

None of the sources calls for a blanket restriction on distillation; they differ in how much weight they put on curbing its use against closed models. The open weights letter signatories ask policymakers not to impose sweeping restrictions on distillation, saying unlawful extraction of value from closed models should be handled through targeted legal and commercial frameworks. Anthropic CEO Dario Amodei says he agrees with that point and presents his own call to crack down on "industrial-scale" distillation operations as the same kind of measure. He argues these operations let China partially evade chip bans and can bring the Chinese frontier to within a few months of the US frontier, though not to equal capability, and adds that the state backing of such operations matters more than the fact that many release open-weights models. He says Anthropic identifies and bans accounts that use its models for industrial-scale distillation, but that such accounts are often found only after substantial distillation has occurred, and no single company can solve the problem. For its own model, DeepSeek sits at the permissive end: its announcement tells users to "distill & commercialize freely" and opens R1's API outputs to distillation.

## Connections
- [[FineTuning]] — the adjacent adaptation technique; DeepSeek and Meta license or promote the two together
- [[OpenWeights]] — the release model under which Meta, calling it open source AI, lists distillation as a developer benefit
- [[DeepSeek]] — released six distilled R1 models and licensed R1 outputs for distillation
- [[Meta]] — promotes Llama 3.1 405B as a source model for distilling smaller models
- [[ModelLicensing]] — R1's MIT License explicitly permits distillation
