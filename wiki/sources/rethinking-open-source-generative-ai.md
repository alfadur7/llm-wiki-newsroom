---
title: "Rethinking open source generative AI: open-washing and the EU AI Act"
type: source
tags: [open-washing, open-source-ai, ai-act, open-weights, training-data]
published: 2024-06-03
scraped: 2026-09-23
source_file: raw/PDF/facct24-120.pdf
source_url: "https://facctconference.org/static/papers24/facct24-120.pdf"
last_updated: 2026-09-23
---

## Summary

In a peer-reviewed FAccT '24 paper, Radboud University researchers Andreas Liesenfeld and Mark Dingemanse assess how open generative AI systems billed as "open" really are. They score 40 text generators and 6 text-to-image generators on 14 dimensions of openness, grouped under availability, documentation, and access and licensing, and they find that many models, including [[Meta]]'s Llama 2 and Llama 3, are "open weight" at best. The authors describe this as [[OpenWashing]], and they warn that the EU AI Act's exemptions for openly licensed models reward it. They argue that openness is composite and gradient, not binary, and that a definition resting on licensing alone is the easiest one to game. They single out disclosure of [[TrainingData]] as the area that lags furthest behind.

## Key Claims

- [fact] Andreas Liesenfeld and Mark Dingemanse — surveyed 40 text generators and 6 text-to-image generators described as open, with OpenAI's ChatGPT and DALL-E as closed reference points
- [fact] Andreas Liesenfeld and Mark Dingemanse — assessed each system on 14 dimensions of openness, each judged open, partial, or closed from the provider's own public evidence
- [fact] Andreas Liesenfeld and Mark Dingemanse — scored the judgements 1 (open), 0.5 (partial), and 0 (closed), weighting all dimensions equally, to rank systems by cumulative openness
- [fact] Andreas Liesenfeld and Mark Dingemanse — report that their framework has run since July 2023 as a public openness leaderboard that anyone can contribute evidence to, subject to expert review
- [analysis] Andreas Liesenfeld and Mark Dingemanse — argue that openness in generative AI is composite, because a system has many separately assessable elements
- [analysis] Andreas Liesenfeld and Mark Dingemanse — argue that openness is gradient, because each element can be open to different degrees, so a simple open/closed binary loses too much information
- [analysis] Andreas Liesenfeld and Mark Dingemanse — define [[OpenWashing]] as collecting credit for openness without disclosing training and tuning procedures, which lets providers escape scientific scrutiny and legal exposure
- [analysis] Andreas Liesenfeld and Mark Dingemanse — identify a "release by blogpost" strategy, in which models debut in a press release with cherry-picked benchmark tables instead of peer-reviewed documentation, as a key sign of open-washing
- [fact] [[Meta]] — introduced Llama 2 as "the next generation of our open source large language model" in a corporate blogpost [[rethinking-open-source-generative-ai#Key Quotes]]
- [fact] [[Meta]] — introduced Llama 3 as "the next generation of our state-of-the-art open source large language model" [[rethinking-open-source-generative-ai#Key Quotes]]
- [analysis] Andreas Liesenfeld and Mark Dingemanse — conclude that only BloomZ can substantially claim open source status, while [[Meta]]'s Llama 2 is "at best open weights" and closed in almost all other aspects
- [fact] Andreas Liesenfeld and Mark Dingemanse — report that Llama 2 shares only scripts for running the model, not its training or fine-tuning source code
- [fact] Andreas Liesenfeld and Mark Dingemanse — report that Llama 2's base training data is described only as "a new mix of data from publicly available sources," with no datasheet
- [fact] Andreas Liesenfeld and Mark Dingemanse — report that Llama 2's instruction-tuning data, over 1 million human binary comparisons Meta calls "Meta reward modeling data," remains undisclosed
- [fact] Andreas Liesenfeld and Mark Dingemanse — report that Llama 2 weights are available only through a consent form and access request
- [analysis] Andreas Liesenfeld and Mark Dingemanse — state that Llama 3 is no different from Llama 2 in terms of openness
- [fact] Andreas Liesenfeld and Mark Dingemanse — report that BloomZ releases its training, fine-tuning, and inference code under Apache 2.0 and its weights under the Responsible AI Licence (RAIL)
- [analysis] Andreas Liesenfeld and Mark Dingemanse — find that AllenAI's OLMo Instruct, BloomZ, and LLM360's AmberChat approach full openness and top the leaderboard
- [analysis] Andreas Liesenfeld and Mark Dingemanse — find that roughly the bottom third of text generators share only model weights and are better called [[OpenWeights]] than open source
- [analysis] Andreas Liesenfeld and Mark Dingemanse — find that the big commercial players, Meta, Google, Cohere, Microsoft, and Mistral, occupy the lower ranks of the openness table
- [analysis] Andreas Liesenfeld and Mark Dingemanse — find that most models in the bottom half give no details about datasets beyond generic descriptors designed to evade legal scrutiny
- [analysis] Andreas Liesenfeld and Mark Dingemanse — find that Stable Diffusion is the one text-to-image system that stands out for openness, while DALL-E is completely closed
- [analysis] Andreas Liesenfeld and Mark Dingemanse — observe that text-to-image generators are often released under RAIL licences, while text generators most commonly use unrestricted licences like Apache 2.0
- [analysis] Andreas Liesenfeld and Mark Dingemanse — argue that Meta and Mistral have dragged down the average level of openness through the ubiquity of their weights, as smaller players build on their models
- [fact] Andreas Liesenfeld and Mark Dingemanse — quote the February 24, 2024 draft of the EU AI Act, which exempts providers of models "under a free and open licence" from the duty to keep detailed technical documentation
- [analysis] Andreas Liesenfeld and Mark Dingemanse — argue that the AI Act exemption makes open source status highly attractive as a way to escape documentation duties and scrutiny
- [forecast] Andreas Liesenfeld and Mark Dingemanse — predict that the AI Office's still-unspecified training-data summary template will become the focus of intense lobbying
- [analysis] Andreas Liesenfeld and Mark Dingemanse — observe that current efforts to define open source AI, including the [[OpenSourceInitiative]]'s consultation, focus strongly on licensing
- [fact] Andreas Liesenfeld and Mark Dingemanse — list the "Joint Statement on AI Safety and Openness," by parties including Creative Commons, [[Mozilla]], LAION, and Open Future, as another effort to redefine open source for AI
- [analysis] Andreas Liesenfeld and Mark Dingemanse — warn that if open licensing becomes the sole deciding factor, community standards risk being co-opted and diluted, as multinationals did with fair trade coffee
- [analysis] Andreas Liesenfeld and Mark Dingemanse — call basing openness on a single measure, such as open weights or an open licence, one of the most effective methods for open-washing
- [forecast] Andreas Liesenfeld and Mark Dingemanse — predict that corporate interests will argue for the easiest-to-attain openness dimensions to weigh most heavily
- [analysis] Andreas Liesenfeld and Mark Dingemanse — argue that corporate appeals to "AI Safety" as a reason for secrecy mostly obscure present harms and limit legal exposure from disclosing [[TrainingData]]
- [analysis] Andreas Liesenfeld and Mark Dingemanse — propose "meaningful openness" as the ground between radical openness and "homeopathic openness," such as sharing weights alone
- [analysis] Andreas Liesenfeld and Mark Dingemanse — conclude that datasets lag furthest behind in openness and that full data disclosure is a key to meaningful openness
- [analysis] Andreas Liesenfeld and Mark Dingemanse — acknowledge that their training-data assessment stays superficial and that some data, such as datasets containing CSAM, requires closed-door assessment

## Key Quotes

> "Today, we're introducing the availability of Llama 2, the next generation of our open source large language model." — [[Meta]], Llama 2 release blogpost

> "Today, we're introducing Meta Llama 3, the next generation of our state-of-the-art open source large language model." — [[Meta]], Llama 3 release blogpost

> "Only BloomZ can substantially claim open source status, while Meta's Llama is at best open weights, and is closed in almost all other aspects." — Andreas Liesenfeld and Mark Dingemanse, Radboud University

> "Without technical documentation and peer review, the release-by-blogpost model is little more than pseudoscience." — Andreas Liesenfeld and Mark Dingemanse, Radboud University

> "The EU AI Act is at risk of tying itself to a moving target: a licence-based definition of 'open source AI' that itself is evolving." — Andreas Liesenfeld and Mark Dingemanse, Radboud University

> "Between radical openness and homeopathic openness lies meaningful openness." — Andreas Liesenfeld and Mark Dingemanse, Radboud University

> "fails to set meaningful dataset transparency standards" — Alek Tarkowski, sociologist and open policy advocate, on the EU AI Act

> "choose your own adventure" — Kate Downing, legal scholar, on openness in the EU AI Act

> "Audits without clear standards provide false assurance of compliance" — Ellen P. Goodman and Julia Tréhu, authors of a report on AI audit-washing

> "co-optation ... occurs primarily on the terrain of standards, in the form of weakening or dilution" — Daniel Jaffee, sociologist, on the fair trade movement

## Connections

- defines: [[OpenWashing]] — defines open-washing and its "release by blogpost" signature, backed by a 46-system survey
- contradicts: [[Meta]] — rejects Meta's "open source" billing of Llama 2 and Llama 3, judging them open weights at best
- contradicts: [[OpenSourceAI]] — argues openness is composite and gradient, and that a binary or licence-only test invites open-washing
- references: [[OpenWeights]] — classes the bottom third of surveyed text generators as open weight rather than open source
- references: [[TrainingData]] — names dataset disclosure the most lagging dimension of openness
- references: [[ModelLicensing]] — contrasts Apache 2.0, RAIL, and Meta's community licence, and warns against licence-only openness tests
- references: [[OpenSourceInitiative]] — notes the OSI definition effort's strong focus on licensing
- references: [[FineTuning]] — scores instruction-tuning data and weights as separate openness dimensions
- references: [[joint-statement-ai-safety-openness|Joint Statement on AI Safety and Openness]] — cited as a parallel effort to redefine open source for AI
- references: [[hello-olmo-truly-open-llm|OLMo release]] — OLMo Instruct tops the openness ranking
- references: [[OpenAI]] — ChatGPT and DALL-E serve as the closed reference points of the openness survey
- references: [[AISafety]] — argues corporate appeals to "AI Safety" as grounds for secrecy mostly obscure present harms and limit legal exposure
- references: [[EUAIAct]] — argues the Act's exemption for openly licensed models makes open source status a way to escape documentation duties

