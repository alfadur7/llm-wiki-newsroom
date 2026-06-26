---
title: "Open Source AI Models: How Open Are They Really? (Part 1)"
type: source
tags: [open-weights, open-source-ai, licensing, fine-tuning]
published: 2025-05-19
scraped: 2026-06-26
source_file: raw/NewsScrap/Part 1 – Open Source AI Models How Open Are They Really.md
source_url: "https://www.hunton.com/insights/publications/part-1-open-source-ai-models-how-open-are-they-really"
last_updated: 2026-06-26
---

## Summary

This Hunton legal primer explains why open-source AI diverges from open-source software: a model needs training data, code, weights, and parameters, not just software. It contrasts the OSI's strict OSAID with the emerging "open weights" middle ground, where providers release weights for fine-tuning but withhold training data — using DeepSeek R1 as a leading example and noting the trade-offs in transparency and reproducibility.

## Key Claims

- [fact] [[OpenSourceInitiative]] — released the OSAID in October 2024, requiring data information, code, and parameters as the preferred form for modification
- [analysis] [[OpenWeights]] — releases weights and parameters for [[FineTuning]] but typically withholds training data and training algorithms
- [analysis] [[DeepSeek]] — R1 (January 2025, MIT-licensed weights) is an open-weights release because the weights are public but the [[TrainingData]] is not
- [forecast] [[OpenWeights]] — open-weights releases appear to strike a balance that works for some providers and users at this early stage of LLM development

## Key Quotes

> "An open weights AI release does not enable the user to fully understand, reproduce or adapt the underlying AI model, including any inherent biases, because the user does not have access to the training data or training algorithms." — [[OpenWeights]]

## Connections

- defines: [[OpenWeights]] — the primer's central concept
- references: [[OpenSourceAI]] — the stricter standard contrasted with open weights
- references: [[DeepSeek]] — the leading open-weights example
- references: [[FineTuning]] — the capability open weights enables
- references: [[TrainingData]] — the component open weights withholds
- references: [[ModelLicensing]] — permissive vs copyleft licensing context
