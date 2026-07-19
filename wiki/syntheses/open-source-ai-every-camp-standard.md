---
title: "What Counts as Open Source AI Under Every Camp's Standard"
type: synthesis
tags: [open-source-ai, OSAID, training-data, open-weights]
sources: [osi-open-source-ai-definition, case-against-osaid, mozilla-celebrates-osaid, open-source-ai-models-how-open]
last_updated: 2026-07-19
---

# What Counts as Open Source AI Under Every Camp's Standard

## Summary

To count as [[OpenSourceAI]] under *every* camp in this debate, a model has to clear the **stricter** of two bars — the open-data camp's, which on the [[FreeSoftwareFoundation]]'s stated criteria contains the [[OpenSourceInitiative]]'s. On the corpus as it stands, **no model is documented as clearing both bars**. OLMo is the nearest candidate: OSI validated Ai2's OLMo, and Ai2 is reported to be releasing LLMs with open training data — but the report never names OLMo among them, and nothing here addresses the processing scripts and data licenses the open-data camp also demands. The dividing line, in both camps, is [[TrainingData]]: everything downstream of that one question follows from it.

## 1. Two standards, one nested inside the other

The two definitions differ on a single component. The [[osi-open-source-ai-definition|Open Source AI Definition]] grants the four freedoms (use, study, modify, share) on access to **data *information*, source code, and parameters** — enough to recreate a substantially equivalent system, but not the raw [[TrainingData]] itself. The open-data camp — the [[FreeSoftwareFoundation]] and critics including Bruce Perens and Bradley Kuhn — holds instead that training data is effectively the source code, so a model is not free unless the **data and its processing scripts** respect the four freedoms [[case-against-osaid]].

On the FSF's criteria that makes the open-data bar a superset of the OSI's: it demands data information, code, and parameters *and* the data and scripts on top. Not every critic frames it as an extension — Perens argues the 26-year-old Open Source Definition should simply be applied to AI, treating the OSAID as an unnecessary fork rather than a floor to build on; this synthesis takes the stacking reading because it is the one the FSF states in criteria form. "Open source under every camp" therefore is not an average of the two positions but the higher of them — the OSI's requirements plus open training data and open processing scripts. The [[Mozilla]] endorsement does not add a third bar: [[Mozilla]] backs the same binary OSI standard as "an important step forward" [[mozilla-celebrates-osaid]], acknowledging that some disagree with aspects such as the training-data treatment and that "the definition will need refinement over time."

## 2. What the composite bar rules out

The stricter bar sets a floor that most "open" releases sit below. [[OpenWeights]] releases — [[DeepSeek]]'s R1 being the leading example, with public MIT-licensed weights but withheld data — clear neither bar, because "an open weights AI release does not enable the user to fully understand, reproduce or adapt the underlying AI model" without the training data or algorithms [[open-source-ai-models-how-open]]. And the OSI's own bar already excludes the best-known open-ish models: it judged [[Meta]]'s Llama 2 **non-compliant** [[osi-open-source-ai-definition]]. So a model that only ships weights fails long before the open-data question is even reached — the composite standard is decided among models that already pass the OSI, not among open-weights releases.

## 3. The candidates that clear it — and the gap

Among OSI-passing models, the ones that also meet the open-data camp's core demand are those releasing actual data, not just data information. The OSI validated **Pythia, OLMo, Amber, CrystalCoder, and T5** as OSAID-compliant [[osi-open-source-ai-definition]] — results OSI stresses are "not certifications of any kind." [[case-against-osaid]] gathers the open-data counter-evidence against the "niche-only" defense: Pleias's fully open multilingual dataset of over 2 trillion tokens, Ai2's LLMs with open training data, and AMD's "fully open 1 billion parameter language models," which an observer rebutting the "no good example of an open data LLM" argument cites as settling the point. Two gaps stop that evidence short of the question here. The report never says which Ai2 releases carry open training data, so it does not reach the validated OLMo specifically; and the observer's decisive example is AMD's release, not the Ai2 artifact on OSI's list. For Pythia, Amber, CrystalCoder, and T5 there is no open-data finding at all — OSAID validation turns on data *information*, so it cannot stand in for one.

The honest gap is why this is not a clean "yes." The open-data camp's bar is not data alone — the [[FreeSoftwareFoundation]]'s criteria "will require the software, as well as the raw training data and associated scripts, to grant users the four freedoms." This corpus records open training data for Ai2 as a publisher but never for the validated OLMo itself, says nothing about processing scripts or data licenses for any validated model, and records no critic certifying one. The defensible answer is therefore negative: no model here is documented as clearing every camp's bar. OLMo is the nearest candidate, on a property attributed to its publisher rather than established for the artifact.

## Connections

- **Concepts** — [[OpenSourceAI]] · [[TrainingData]] · [[OpenWeights]] · [[OpenWashing]]
- **Entities** — [[OpenSourceInitiative]] · [[FreeSoftwareFoundation]] · [[Mozilla]] · [[Meta]] · [[DeepSeek]]
- **Issue** — [[open-training-data-requirement]] (the contradiction this synthesis resolves into an answer)
- **Sources** — [[osi-open-source-ai-definition]] · [[case-against-osaid]] · [[mozilla-celebrates-osaid]] · [[open-source-ai-models-how-open]]
