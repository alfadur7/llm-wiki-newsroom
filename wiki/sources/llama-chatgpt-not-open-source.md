---
title: "Llama and ChatGPT Are Not Open-Source"
type: source
tags: [Meta, OpenAI, Llama, ChatGPT, open-washing, reproducibility]
published: 2023-07-27
scraped: 2026-09-27
source_file: raw/NewsScrap/LLAMA and ChatGPT Are Not Open-Source.md
source_url: "https://spectrum.ieee.org/open-source-llm-not-open"
last_updated: 2026-09-27
---

## Summary

A 27 July 2023 IEEE Spectrum news story by Michael Nolan reports on research by Radboud University's Andreas Liesenfeld, Mark Dingemanse and colleagues, presented at the ACM Conference on Conversational User Interfaces. The researchers scored nominally open-source LLMs on availability, documentation and access, and they rank [[OpenAI]]'s ChatGPT worst and [[Meta]]'s Llama 2 second worst. Nolan notes that Meta released Llama 2's weights, evaluation code and documentation but not its [[TrainingData|training data]] or training code. The researchers found every assessed model closed in two ways: little detail on reinforcement learning with human feedback (RLHF), and no peer review. Dingemanse calls Meta's use of "open source" for Llama 2 "positively misleading"; the story carries no response from Meta or OpenAI.

## Key Claims

- [fact] Michael Nolan — reports that [[Meta]] released Llama 2 as open source with access to the model's weights, evaluation code and documentation
- [fact] [[Meta]] — states that the open-source release was meant to make Llama 2 "accessible to individuals, creators, researchers, and businesses so they can experiment, innovate, and scale their ideas responsibly"
- [fact] Michael Nolan — reports that Meta is not sharing Llama 2's training data or the code used to train it
- [analysis] Michael Nolan — assesses that Llama 2 is considerably closed off compared with other open-source LLMs and open-source software packages generally
- [analysis] Michael Nolan — observes that third parties have built applications on the base model while developers and researchers have limited ability to pick the model apart
- [fact] Andreas Liesenfeld and Mark Dingemanse — present a multidimensional assessment of model openness in research shown at the ACM Conference on Conversational User Interfaces
- [fact] Andreas Liesenfeld and Mark Dingemanse — scored 15 nominally open-source LLMs on availability, documentation and methods of access
- [fact] Michael Nolan — reports that the Radboud team's online table has since expanded to 21 models, with 20 entries at press time
- [fact] Andreas Liesenfeld — says the team started the project while looking for AI models to use in its own teaching and research
- [analysis] Andreas Liesenfeld — argues that research results should stay reproducible for as long as possible, and that ChatGPT did not offer this
- [fact] Michael Nolan — reports that [[OpenAI]] closed access to much of its research code after launching GPT-4 and receiving a substantial investment from Microsoft
- [fact] Andreas Liesenfeld and Mark Dingemanse — rate ChatGPT worst of all models in the openness table
- [fact] Andreas Liesenfeld and Mark Dingemanse — mark ChatGPT "closed" on every dimension except model card and preprint, where it gets "partial"
- [fact] Andreas Liesenfeld and Mark Dingemanse — rank Llama 2 second worst overall, only marginally more open than ChatGPT
- [fact] Michael Nolan — reports that a Stanford University and UC Berkeley preprint found GPT-4 and GPT-3.5 reasoning performance changed between March and June 2023, mostly for the worse
- [fact] Michael Nolan — reports that OpenAI made no announcement accompanying those performance changes
- [analysis] Michael Nolan — argues that unannounced model changes may prevent reproduction of research results obtained with those models
- [analysis] Andreas Liesenfeld and Mark Dingemanse — find that several smaller, research-focused models were considerably more open than Llama 2 or ChatGPT
- [analysis] Andreas Liesenfeld and Mark Dingemanse — find that very few assessed models gave sufficient detail of their RLHF refinement process
- [analysis] Michael Nolan — describes RLHF as a labor-intensive, human-in-the-loop step that appears to be the "secret sauce" behind contemporary LLM performance
- [analysis] Andreas Liesenfeld and Mark Dingemanse — point out that commercial LLM releases have avoided peer review
- [fact] Michael Nolan — reports that ChatGPT and Llama 2 were both released with only a company-hosted preprint document
- [analysis] Michael Nolan — suggests the preprint-only release was most likely meant to protect trade secrets about model structure and training
- [analysis] Andreas Liesenfeld and Mark Dingemanse — remain wary of commercial model use in academic research
- [analysis] Mark Dingemanse — states that Meta's "open source" label for Llama 2 is positively misleading because no source is visible and the training data is entirely undocumented
- [analysis] Mark Dingemanse — calls Llama 2's technical documentation "really rather poor" beyond its charts

## Key Quotes

> "Meta using the term 'open source' for this is positively misleading: There is no source to be seen, the training data is entirely undocumented, and beyond the glossy charts the technical documentation is really rather poor. We do not know why Meta is so intent on getting everyone into this model, but the history of this company's choices does not inspire confidence. Users beware." — Mark Dingemanse, Radboud University

> "If you write a research paper, you want the results to be reproducible for as long as possible." — Andreas Liesenfeld, assistant professor at Radboud University

> "That's something you would specifically value if you do research using these technologies, right? That's something we did not see, for instance, from ChatGPT" — Andreas Liesenfeld, assistant professor at Radboud University

## Connections

- contradicts: [[Meta]] — Dingemanse calls Meta's "open source" label for Llama 2 "positively misleading," and the team ranks Llama 2 second worst for openness
- cites: [[OpenAI]] — ChatGPT is marked closed on nearly every dimension, and OpenAI closed much of its research code after GPT-4
- references: [[OpenWashing]] — the story reports that few ostensibly open-source LLMs live up to the openness claim
- references: [[OpenWeights]] — Llama 2 ships its weights but not its training data or training code
- references: [[TrainingData]] — Meta withholds Llama 2's training data, which Dingemanse calls "entirely undocumented"
- references: [[OpenSourceAI]] — the Radboud team scores models on a multidimensional openness rubric instead of accepting the label
- references: [[llama-2-meta-microsoft|Meta's Llama 2 announcement]] — the release whose "open source" billing the story disputes
- references: [[rethinking-open-source-generative-ai|Liesenfeld and Dingemanse's FAccT '24 paper]] — the same Radboud team's later survey of the openness table
