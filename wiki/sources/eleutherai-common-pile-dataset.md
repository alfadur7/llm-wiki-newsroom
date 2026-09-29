---
title: "EleutherAI Releases Massive AI Training Dataset of Licensed and Open Domain Text"
type: source
tags: [training-data, open-source-ai, open-weights]
published: 2025-06-06
scraped: 2026-09-27
source_file: raw/NewsScrap/EleutherAI releases massive AI training dataset of licensed and open domain text.md
source_url: "https://techcrunch.com/2025/06/06/eleutherai-releases-massive-ai-training-dataset-of-licensed-and-open-domain-text/"
last_updated: 2026-09-27
---

## Summary

TechCrunch's Kyle Wiggers reports that [[EleutherAI]] released the Common Pile v0.1 on 2025-06-06, an 8-terabyte collection of openly licensed and public-domain text that the organization claims is one of the largest of its kind for [[TrainingData|training AI models]]. EleutherAI says it trained two 7-billion-parameter models on part of it, Comma v0.1-1T and Comma v0.1-2T, and claims they rival [[Meta]]'s first Llama model on coding, image understanding and math benchmarks. Executive director Stella Biderman argues that copyright lawsuits have cut AI companies' transparency without changing how they source data, and that the idea that unlicensed text drives performance is "unjustified." The performance figures are EleutherAI's own claims, and no external assessment of them is within the raw's scope.

## Key Claims

- [fact] [[EleutherAI]] — released the Common Pile v0.1, an 8-terabyte dataset of openly licensed and public-domain text, after around two years of work with Poolside, [[HuggingFace]], other startups and several academic institutions
- [analysis] [[EleutherAI]] — claims the Common Pile v0.1 is one of the largest collections of licensed and open-domain text for training AI models
- [fact] [[EleutherAI]] — made the Common Pile v0.1 downloadable from [[HuggingFace]] and GitHub
- [fact] [[EleutherAI]] — built the dataset in consultation with legal experts and drew on sources including 300,000 public-domain books digitized by the Library of Congress and the Internet Archive
- [fact] [[EleutherAI]] — used Whisper, the open-source speech-to-text model from [[OpenAI]], to transcribe audio content for the dataset
- [fact] [[EleutherAI]] — trained two 7-billion-parameter models, Comma v0.1-1T and Comma v0.1-2T, on only a fraction of the Common Pile v0.1
- [analysis] [[EleutherAI]] — claims the Comma models perform on par with models developed on unlicensed, copyrighted data
- [analysis] [[EleutherAI]] — claims the Comma models rival [[Meta]]'s first Llama model on benchmarks for coding, image understanding and math
- [analysis] Stella Biderman — argues that copyright lawsuits have not meaningfully changed data-sourcing practices in model training but have drastically decreased the transparency AI companies engage in [[eleutherai-common-pile-dataset#Key Quotes|Key Quotes]]
- [fact] Stella Biderman — said researchers at some companies cited lawsuits as the reason they could not release research in data-centric areas [[eleutherai-common-pile-dataset#Key Quotes|Key Quotes]]
- [analysis] Stella Biderman — argues that the common idea that unlicensed text drives performance is unjustified [[eleutherai-common-pile-dataset#Key Quotes|Key Quotes]]
- [forecast] Stella Biderman — expects the quality of models trained on openly licensed content to improve as the amount of accessible openly licensed and public-domain data grows
- [analysis] Kyle Wiggers — reports that AI companies including [[OpenAI]] face lawsuits over training practices that scrape copyrighted books and research journals from the web
- [analysis] Kyle Wiggers — reports that most AI companies maintain that the U.S. fair-use doctrine shields them when they train on copyrighted work without permission
- [analysis] Kyle Wiggers — reads the Common Pile v0.1 as partly an effort to right EleutherAI's release years earlier of The Pile, an open training collection that included copyrighted material
- [forecast] [[EleutherAI]] — commits to releasing open datasets more frequently with its research and infrastructure partners
- [fact] Stella Biderman — clarified on X that EleutherAI contributed to the release, while development involved many partners including the University of Toronto, which helped lead the research

## Key Quotes

> "[Copyright] lawsuits have not meaningfully changed data sourcing practices in [model] training, but they have drastically decreased the transparency companies engage in." — Stella Biderman, executive director, [[EleutherAI]]

> "Researchers at some companies we have spoken to have also specifically cited lawsuits as the reason why they've been unable to release the research they're doing in highly data-centric areas." — Stella Biderman, executive director, [[EleutherAI]]

> "In general, we think that the common idea that unlicensed text drives performance is unjustified. As the amount of accessible openly licensed and public domain data grows, we can expect the quality of models trained on openly licensed content to improve." — Stella Biderman, executive director, [[EleutherAI]]

## Connections

- references: [[TrainingData]] — the Common Pile v0.1 is an openly licensed and public-domain training corpus released in full
- cites: [[EleutherAI]] — the releasing organization; the dataset description, the Comma benchmark claims and executive director Stella Biderman's remarks are its own
- references: [[HuggingFace]] — a collaborator on the dataset and one of its download venues
- references: [[OpenAI]] — its Whisper model transcribed audio for the dataset, and it is named among AI companies facing training-data lawsuits
- references: [[Meta]] — its first Llama model is the benchmark EleutherAI says the Comma models rival
- contradicts: [[open-future-osaid-step-forward|Open Future on the OSAID]] — Open Future argues open resources lack the volume and diversity to train large foundation models, while EleutherAI claims models trained on openly licensed text perform on par with those trained on copyrighted data
