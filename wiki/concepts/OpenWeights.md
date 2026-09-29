---
title: "Open Weights"
type: concept
tags: [open-weights, model-weights, fine-tuning, licensing]
sources: [open-source-ai-models-how-open, osi-open-source-ai-definition, anthropic-position-open-weights-models, debian-ai-models-dfsg, deepseek-r1-release, fsf-free-ml-application-criteria, hello-olmo-truly-open-llm, joint-statement-ai-safety-openness, llama-2-meta-microsoft, llama-3-1-community-license, ntia-open-model-weights-report, open-future-osaid-step-forward, open-source-ai-path-forward, open-source-ai-uniquely-dangerous, open-weight-models-frontier-safety-gap, open-weights-american-ai-leadership, openmdw-1-1-nvidia-adoption, osi-open-weights-good-open-source-better, red-hat-open-source-ai-point-of-view, rethinking-open-source-generative-ai, senators-question-meta-llama-leak, societal-impact-open-foundation-models, welcome-gpt-oss-openai, what-does-open-source-ai-mean, ai-openness-oecd-gpai-open-weight-models, apertus-fully-open-multilingual-llm, beyond-deepseek-china-open-weight-ecosystem, debian-ai-gr-withdrawn, eu-ai-act-gpai-guide-open-source-developers, gpt-oss-challenges-meta-open-weight, knives-out-open-weight-ai-models, llama-chatgpt-not-open-source, meta-muse-glimmer-apache-2-0, mistral-small-3, mozilla-eleutherai-hf-sb-1047-letter, open-model-licenses-concerning-restrictions, open-source-ai-llm-access-debate, open-washing-four-criteria, open-weight-diplomacy-digital-silk-road, open-weights-not-enough-open-source-science, open-weights-not-open-source-label-dispute, openai-deepseek-free-riding-distillation, openai-hack-open-source-ai-fight, secrets-of-deepseek-r1-landmark-paper, true-open-source-ai-selective-transparency, whats-next-chinese-open-source-ai, zuckerberg-intensified-battle-ai-future, zuckerberg-superintelligence-not-all-open-source]
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
