---
title: "Open Weights"
type: concept
tags: [open-weights, model-weights, fine-tuning, licensing]
sources: [open-source-ai-models-how-open, osi-open-source-ai-definition]
last_updated: 2026-06-26
---

## Overview

Open weights is a release model in which an AI provider publishes the trained weights and parameters needed to run a model, but typically withholds the training data, detailed data information, and training algorithms. It occupies a middle ground between fully proprietary models and the stricter [[OpenSourceAI]] standard: users can run the model and [[FineTuning|fine-tune]] it on their own data without paying licensing fees or training from scratch, while the provider keeps its training corpus and know-how as trade secrets. The trade-off is that an open-weights release does not let a user fully understand, reproduce, or audit the underlying model — including its inherent biases — because the training data and algorithms are unavailable. DeepSeek R1 (MIT-licensed weights, January 2025) is a widely cited example.

## Connections
- [[OpenSourceAI]] — the stricter standard open weights does not meet
- [[ModelLicensing]] — open weights is a licensing posture distinct from open source
- [[FineTuning]] — the primary capability an open-weights release enables
- [[TrainingData]] — the component an open-weights release withholds
- [[DeepSeek]] — a prominent open-weights model release
