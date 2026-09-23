---
title: "AI Safety"
type: concept
tags: [ai-safety, open-weights, misuse-risk, safeguards, policy]
sources: [anthropic-position-open-weights-models, joint-statement-ai-safety-openness, llama-2-meta-microsoft, ntia-open-model-weights-report, open-source-ai-path-forward, open-source-ai-uniquely-dangerous, open-weight-models-frontier-safety-gap, open-weights-american-ai-leadership, rethinking-open-source-generative-ai, senators-question-meta-llama-leak, societal-impact-open-foundation-models]
last_updated: 2026-09-23
---

## Overview

In this wiki, AI safety appears as the axis of a dispute over whether releasing model weights openly makes AI safer or more dangerous. Even the 2026 open weights letter, an industry open letter hosted by Microsoft that more than 270 organizations signed, concedes that once released, [[OpenWeights|weights]] are beyond the original developer's control, and modified versions are difficult to trace or reverse. TechCrunch reports that safeguards applied at a hosted API cannot be enforced once someone runs the weights on their own hardware, where they can be removed or the model [[FineTuning|fine-tuned]]. The sources split on what follows from that fact.

Proponents of open release, among them [[Meta]], the signatories of a [[Mozilla]]-hosted joint statement, and the open weights letter's signatories, argue that open models can be stress-tested and scrutinized by a broad community and that proprietary or closed models carry risks of their own. Former Meta employee David Evan Harris argues that stripped safeguards and irreversible release make unsecured models riskier for misuse such as disinformation, scams, and chemical or biological weapons. Anthropic CEO Dario Amodei says Anthropic has never advocated a ban on open-weights models and calls those without dangerous capabilities a public good; he argues that open-weights models potentially carry higher misuse risk than closed ones, but that whether they do should emerge from testing rather than be decided in advance. Other sources treat the question as unsettled: a 2024 paper by Sayash Kapoor and 24 co-authors finds current research insufficient to characterize the marginal misuse risk of open models, and the U.S. National Telecommunications and Information Administration (NTIA) recommends monitoring risks rather than restricting weights immediately.

## Key Points

- **Scrutiny as safety** — [[Meta]] argued at the Llama 2 release that opening access lets developers and researchers stress test models and fix problems as a community. Mark Zuckerberg wrote in 2024 that he expects [[OpenSourceAI|open source AI]] to be safer than the alternatives, especially against unintentional harm, because open systems can be widely scrutinized.
- **Defenders vs attackers** — the open weights letter's signatories argue that cybersecurity defenders need models comparable to those attackers use, and Hugging Face CEO Clem Delangue makes a similar defensive case in TechCrunch's reporting. Henry Papadatos, executive director of the evaluation group SaferAI, calls that defensive benefit often overstated. Amodei rejects the letter's claim that broad access necessarily helps defenders more than attackers, and expects biology to have a strong attacker-defender asymmetry.
- **Stripped safeguards** — Harris cites "Llama 2 Uncensored," a Llama 2 derivative with its safety features removed, and argues that a maker is largely powerless once such a version is released, while jailbreaks of secured systems can be fixed as they are found.
- **Absent safeguards at release** — SaferAI, testing Z.ai's open-weight GLM-5.2 through Z.ai's own public API, found that it refused none of the offensive cyber or biology tasks it was given, and reports that Z.ai published no safety framework, pre-deployment testing commitments, or risk assessment for the model.
- **Misuse claims contested** — in 2023, Senators Richard Blumenthal and Josh Hawley questioned the LLaMA leak over misuse in spam, fraud, and malware; experts quoted by VentureBeat disputed this, with Christopher Manning judging the release not an unacceptable risk and Vipul Ved Prakash calling the spam concern a straw man.
- **Proposed remedies** — Harris proposes pausing new unsecured releases until safety features cannot easily be removed. Amodei urges mandatory pre-release safety testing of all sufficiently capable models, open and closed. Papadatos names pre-training filtering of [[TrainingData|training data]] as a technique that could help.
- **Safety as a reason for secrecy** — Andreas Liesenfeld and Mark Dingemanse argue that corporate appeals to "AI Safety" as a reason for secrecy mostly obscure present harms and limit legal exposure from disclosing training data.

## Connections
- [[OpenWeights]] — the release model whose safety effects are disputed
- [[OpenSourceAI]] — the label under which Meta and Zuckerberg argue open models are safer
- [[Meta]] — its Llama releases are the central case for both proponents and critics
- [[Mozilla]] — hosts the joint statement calling openness an antidote for AI safety
- [[FineTuning]] — a route by which released safeguards can be stripped
- [[TrainingData]] — pre-training filtering is a proposed mitigation; disclosure is contested on safety grounds
