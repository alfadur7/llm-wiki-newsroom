---
title: "Fine-Tuning"
type: concept
tags: [fine-tuning, open-weights, model-weights, adaptation]
sources: [open-source-ai-models-how-open]
last_updated: 2026-06-26
---

## Overview

Fine-tuning adapts a pre-trained model to a specific domain or task by continuing training on additional data, modifying or adding to the model's internal weights and parameters. It is the primary capability an [[OpenWeights]] release enables: because the weights are published, a user can tailor the model with its own data and deploy a customized system rapidly, avoiding the significant cost of training from scratch. This makes open-weights models attractive to organizations that need a customized model but lack the resources or expertise to build one. Fine-tuning does not require access to the original [[TrainingData]], which is why it remains possible even when a provider withholds its training corpus.

## Connections
- [[OpenWeights]] — the release model that makes fine-tuning practical
- [[ModelLicensing]] — license terms govern whether fine-tuned derivatives may be shared
- [[TrainingData]] — fine-tuning adds data without access to the original corpus
- [[OpenSourceAI]] — fine-tuning is one of the four freedoms (modify)
