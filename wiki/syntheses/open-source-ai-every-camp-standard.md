---
title: "What Counts as Open Source AI Under Every Camp's Standard"
type: synthesis
tags: [open-source-ai, OSAID, training-data, open-weights]
sources: [osi-open-source-ai-definition, case-against-osaid, mozilla-celebrates-osaid, open-source-ai-models-how-open]
last_updated: 2026-07-01
---

# What Counts as Open Source AI Under Every Camp's Standard

## Summary

To count as [[OpenSourceAI]] under *every* camp in this debate, a model has to clear the **stricter** of two bars — the open-data camp's, which strictly contains the [[OpenSourceInitiative]]'s. Today the only plausible candidates are the fully-open-data models the OSI itself validated — **OLMo and Pythia** — and even they qualify only for the data-openness they demonstrably have, not on any verdict the critics have actually issued. The dividing line, in both camps, is [[TrainingData]]: everything downstream of that one question follows from it.

## 1. Two standards, one nested inside the other

The two definitions differ on a single component. The [[osi-open-source-ai-definition|Open Source AI Definition]] grants the four freedoms (use, study, modify, share) on access to **data *information*, source code, and parameters** — enough to recreate a substantially equivalent system, but not the raw [[TrainingData]] itself. The open-data camp — the [[FreeSoftwareFoundation]] and critics including Bruce Perens and Bradley Kuhn — holds instead that training data is effectively the source code, so a model is not free unless the **data and its processing scripts** respect the four freedoms [[case-against-osaid]].

That makes the open-data bar a superset of the OSI's: it demands data information, code, and parameters *and* the data and scripts on top. "Open source under every camp" therefore is not an average of the two positions but the higher of them — the OSI's requirements plus open training data and open processing scripts. The [[Mozilla]] endorsement does not add a third bar: [[Mozilla]] backs the same binary OSI standard as "an important step forward" [[mozilla-celebrates-osaid]], conceding only that its data treatment "will need refinement."

## 2. What the composite bar rules out

The stricter bar sets a floor that most "open" releases sit below. [[OpenWeights]] releases — [[DeepSeek]]'s R1 being the leading example, with public MIT-licensed weights but withheld data — clear neither bar, because "an open weights AI release does not enable the user to fully understand, reproduce or adapt the underlying AI model" without the training data or algorithms [[open-source-ai-models-how-open]]. And the OSI's own bar already excludes the best-known "open-ish" models: it judged [[Meta]]'s Llama 2 **non-compliant** [[osi-open-source-ai-definition]]. So a model that only ships weights fails long before the open-data question is even reached — the composite standard is decided among models that already pass the OSI, not among open-weights releases.

## 3. The candidates that clear it — and the gap

Among OSI-passing models, the ones that also meet the open-data camp's core demand are those releasing actual data, not just data information. The OSI validated **Pythia, OLMo, Amber, CrystalCoder, and T5** as OSAID-compliant [[osi-open-source-ai-definition]]. Of these, the issue analysis in [[open-training-data-requirement]] identifies OLMo and Pythia as fully open-*data* models — the property the open-data camp demands — noting their existence undercuts the "open data is unworkable" defense. Such a model is meeting the open-data camp's central requirement while already holding the OSI's certification.

The honest gap is why this is not a clean "yes." The corpus establishes that OLMo and Pythia are OSAID-validated and open-data, but it does **not** record the [[FreeSoftwareFoundation]] or any critic formally certifying them against the full four-freedoms-on-data-and-scripts test. Their data is open; whether their processing scripts and data licenses satisfy the open-data camp's complete standard is not settled here. The defensible answer is that the OSAID-validated open-data models are the only candidates, and they qualify for the data-openness they demonstrably have — not as a judgment the critics have handed down.

## Connections

- **Concepts** — [[OpenSourceAI]] · [[TrainingData]] · [[OpenWeights]] · [[OpenWashing]]
- **Entities** — [[OpenSourceInitiative]] · [[FreeSoftwareFoundation]] · [[Mozilla]] · [[Meta]] · [[DeepSeek]]
- **Issue** — [[open-training-data-requirement]] (the contradiction this synthesis resolves into an answer)
- **Sources** — [[osi-open-source-ai-definition]] · [[case-against-osaid]] · [[mozilla-celebrates-osaid]] · [[open-source-ai-models-how-open]]
