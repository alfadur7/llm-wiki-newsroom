---
title: "Open-Weight AI Models Are Catching Up to the Frontier. The Safety Gap Remains."
type: source
tags: [open-weights, ai-safety, cybersecurity, ai-policy, China, open-source-ai]
published: 2026-08-04
scraped: 2026-09-23
source_file: "raw/NewsScrap/Open-weight AI models are catching up to the frontier. The safety gap remains. T.md"
source_url: "https://techcrunch.com/2026/08/04/open-weight-ai-models-are-catching-up-to-the-frontier-the-safety-gap-remains/"
last_updated: 2026-09-23
---

## Summary

A TechCrunch article by Rebecca Bellan reports a SaferAI evaluation finding that Z.ai's [[OpenWeights|open-weight]] model GLM-5.2 is only a few months behind OpenAI's GPT-5.5 and Anthropic's Claude Opus 4.7 on cyber and biology capabilities, yet refused none of the offensive tasks it was given. SaferAI's executive director Henry Papadatos argues that capability must be assessed together with mitigations, and that safeguards applied at the API level cannot be enforced once someone runs the weights on their own hardware. Stanford's Graham Webster explains that Chinese AI rules have historically targeted political content and social stability rather than catastrophic risk. Hugging Face CEO Clem Delangue makes the defensive case for open weights, which Papadatos calls overstated. Z.ai did not respond to TechCrunch's questions about its pre-release safety testing.

## Key Claims

- [fact] SaferAI — reports that Z.ai's open-weight GLM-5.2 is only a few months behind OpenAI's GPT-5.5 and Anthropic's Claude Opus 4.7 on cyber and biology capabilities
- [fact] SaferAI — ran its evaluation of GLM-5.2 through Z.ai's public API
- [fact] SaferAI — found that GLM-5.2 refused none of the offensive cyber or biology tasks it was given
- [fact] SaferAI — reports that Claude Opus 4.7 refused so consistently that SaferAI could not complete the CyberGym benchmark on it
- [fact] SaferAI — says Z.ai did not publish a safety framework, pre-deployment testing commitments, or a risk assessment for GLM-5.2
- [analysis] Henry Papadatos — argues that the frontier of capability is not the frontier of risk, so the state of mitigations must be weighed to assess risk properly
- [analysis] TechCrunch — reports that safety measures Z.ai applies to its hosted API become unenforceable once someone runs the [[OpenWeights|open weights]] on their own hardware, where safeguards can be removed or modified, the model [[FineTuning|fine-tuned]], or the system prompt changed
- [analysis] TechCrunch — reports that frontier developers such as OpenAI and Anthropic rely on classifiers, refusal training, and API-level controls to limit dangerous cyber and biological assistance
- [fact] Far.ai — found hundreds of universal jailbreaks, defined as reusable keys that succeed on most harmful requests, in frontier models including xAI's Grok 4.5 and Google DeepMind's Gemini 3.1 Pro
- [analysis] Far.ai — reports that jailbreaks succeed when attackers combine manipulation techniques such as roleplaying, authority impersonation, fake conversation history, and follow-up prompts
- [analysis] Henry Papadatos — argues that safe capabilities should be accessible to anyone while dangerous ones are removed, even in an open-source release
- [analysis] Henry Papadatos — names pre-training data filtering, which removes offensive cybersecurity information from the [[TrainingData|training data]] before training, as a technique that could help
- [analysis] TechCrunch — reports that some research suggests data filtering can reduce hazardous biological knowledge without harming overall performance, but that filtering is much less practical for cybersecurity
- [analysis] TechCrunch — explains that it is difficult to train a general model that excels at coding without also making it a good hacker, and that coding's commercial value pressures developers to keep improving it
- [fact] [[Anthropic]] — states in the Opus 5 system card that the model can search for vulnerabilities in uncompiled source code but not in compiled software
- [fact] TechCrunch — asked Z.ai whether it ran internal or third-party frontier safety evaluations before releasing GLM-5.2 and received no response
- [fact] Xi Jinping — emphasized the importance of open-weight models at the World AI Conference while stressing that AI must remain under strict human control
- [analysis] Graham Webster — says Chinese AI regulation has historically focused on politically sensitive content, misinformation, and social stability rather than catastrophic risks such as offensive cyber capabilities and biological misuse
- [analysis] Graham Webster — says many Chinese policy researchers believe American companies will likely encounter a truly novel frontier risk first
- [analysis] Graham Webster — suggests the mechanism Chinese model providers use to refuse certain political topics could potentially be adapted to refuse offensive cyber attacks or harmful biological engineering
- [analysis] Graham Webster — says Chinese companies' behind-the-scenes coordination with regulators makes their internal pre-release testing hard to see
- [fact] TechCrunch — reports that Hugging Face relied on GLM-5.2 to defend itself against OpenAI's breach
- [analysis] Clem Delangue — argues that the systems that helped stop an AI-powered cyberattack can help defend against millions of cyberattacks every day
- [analysis] Henry Papadatos — says the defensive benefit of open-weight models is often overstated and does not justify open-sourcing dangerous capabilities

## Key Quotes

> "The frontier of capability is not the frontier of risk, and so we do have to take into account the state of the mitigations as well to assess the risk properly." — Henry Papadatos, executive director of SaferAI

> "The objective should clearly be that the good capabilities — the safe ones — are accessible to anyone, and then we try to remove the bad ones, even in an open source fashion." — Henry Papadatos, executive director of SaferAI

> "The main point in my mind is that we shouldn't just accept that dangerous capabilities are easily accessible by anyone anywhere." — Henry Papadatos, executive director of SaferAI

> "U.S. AI thinkers are, in general, more concerned with this existential catastrophic [idea] than the Chinese community." — Graham Webster, Stanford Cyber Policy Center

> "The Chinese system has confidence that they control the use of these technologies inside China." — Graham Webster, Stanford Cyber Policy Center

> "The same systems that helped stop an AI-powered cyberattack can now help defend against millions of cyberattacks every day, while helping us identify and fix vulnerabilities before attackers exploit them." — Clem Delangue, CEO of Hugging Face

## Connections

- references: [[OpenWeights]] — GLM-5.2 is the open-weight model whose released weights place safeguards beyond the developer's enforcement
- references: [[FineTuning]] — fine-tuning downloaded weights is one way the article says safeguards can be stripped
- references: [[TrainingData]] — pre-training data filtering is the mitigation Papadatos proposes for open releases
- references: [[OpenSourceAI]] — Papadatos frames removing dangerous capabilities as compatible with an open-source release
- contradicts: [[open-weights-american-ai-leadership|Open Weights and American AI Leadership]] — the letter argues defenders need open models comparable to attackers', while Papadatos calls that defensive benefit overstated
- cites: [[Anthropic]] — Claude Opus 4.7 is the closed comparison model that refused the offensive tasks, and the Opus 5 system card is cited on vulnerability search
- references: [[OpenAI]] — GPT-5.5 is the closed frontier model GLM-5.2 trails by a few months, and OpenAI is named among developers relying on API-level controls
- references: [[AISafety]] — SaferAI finds GLM-5.2 refused no offensive cyber or biology tasks, and API safeguards are unenforceable on self-hosted weights

