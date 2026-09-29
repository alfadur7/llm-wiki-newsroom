---
title: "'Open-Washing' Is Everywhere in AI. Four Criteria Cut Through It"
type: source
tags: [open-washing, open-source-ai, open-weights, training-data, China, model-licensing]
published: 2026-07-25
scraped: 2026-09-27
source_file: "raw/NewsScrap/‘Open-Washing’ Is Everywhere in AI. Four Criteria Cut Through It.md"
source_url: "https://www.techpolicy.press/open-washing-is-everywhere-in-ai-four-criteria-cut-through-it/"
last_updated: 2026-09-27
---

## Summary

In a Tech Policy Press perspective dated 2026-07-25, JJ Jasser, a professor and director of data analytics at Rollins College, argues that [[MoonshotAI|Moonshot]]'s Kimi K3 is not [[OpenSourceAI|open-source AI]] and that calling it so is [[OpenWashing|open-washing]]. He grants that K3's benchmark results are real, then reports that the Kimi app refused his question about the 1989 Tiananmen Square protests and left China out of an app it built on the history of protest. He measures K3 against the [[OpenSourceInitiative]]'s definitions and against a four-part test from his own co-authored paper: public architecture, training code, weights and [[TrainingData|training data]], all under unrestricted licenses. By that test he judges K3 at best an [[OpenWeights|open-weight]] model, and on the day he wrote not even that. He argues that only training-data transparency can show why a model omits history, and that China's use of "open" in its AI diplomacy raises the stakes of the label. The piece is a single-author opinion essay; Moonshot is not quoted responding, and external assessment of the author's tests is outside the raw's scope.

## Key Claims

- [fact] JJ Jasser — reports that Kimi K3 ranks among the top five models on the Artificial Analysis Intelligence Index and took first place in the Frontend Code Arena leaderboard
- [fact] JJ Jasser — reports that when he asked K3 about the 1989 Tiananmen Square protest, it replied: "Sorry, I cannot provide this information. Please feel free to ask another question."
- [analysis] JJ Jasser — cautions that he tested the Kimi app rather than the model weights, and that app-layer filters can differ from the underlying model
- [analysis] JJ Jasser — notes that independent testing has found Chinese models vary, some engaging honestly in English while aligning with official positions in Chinese-language settings
- [fact] JJ Jasser — reports that an app K3 built on major protests in history covered the Peasants' Revolt, the Salt March, the Arab Spring and Black Lives Matter, and nothing from China's history
- [analysis] JJ Jasser — argues that the model "taught confidently and incompletely," leaving users no way to see what was missing, while conceding this was a single test of a non-deterministic model
- [analysis] JJ Jasser — calls the omission part of a general problem with large language models that extends beyond Chinese models
- [analysis] JJ Jasser — rejects the defense that K3's progress shows open-source AI catching up to proprietary models, because K3 is not open source
- [analysis] JJ Jasser — states that "open-source" is a standard with specific criteria, not a marketing register [[open-washing-four-criteria#Key Quotes|Key Quotes]]
- [fact] JJ Jasser — states that for over two decades the [[OpenSourceInitiative]] has maintained the software definition granting the freedom to use, study, modify and share, for anyone and for any purpose
- [fact] JJ Jasser — states that in 2024 the [[OpenSourceInitiative]] extended this into the Open Source AI Definition, which requires the complete training code and sufficiently detailed information about the training data for others to understand and recreate the system
- [analysis] JJ Jasser — defines, with co-authors in an AI and Ethics article, a model as open source only when its architecture, training code, model weights and training data are all public under licenses permitting unrestricted use, modification and redistribution
- [analysis] JJ Jasser — names the Allen Institute's OLMo, EleutherAI's GPT-NeoX and LLM360's K2 among the handful of models that meet all four criteria
- [fact] JJ Jasser — reports that Moonshot promised to release K3's weights on July 27 and that, as of his writing, the weights were unavailable and K3 was API-only
- [forecast] JJ Jasser — expects K3's weights to arrive under a "Modified MIT" license with added conditions, which he says is not an OSI-approved open-source license
- [forecast] JJ Jasser — expects K3's training data and training pipeline to remain closed after the weight release
- [analysis] JJ Jasser — classifies K3 as at best an open-weight model that can be downloaded and run but never fully studied or reconstructed, and calls the open-source label "a category error" [[open-washing-four-criteria#Key Quotes|Key Quotes]]
- [analysis] JJ Jasser — describes open-washing, a term he attributes to researchers, as borrowing openness's credibility while withholding the transparency that justifies it
- [analysis] JJ Jasser — argues that open-source development expands epistemic capability, the freedom to understand how an AI system produces its outputs, and that this matters most in education
- [analysis] JJ Jasser — argues that only training-data transparency can show whether missing events were absent from the data, removed in curation or suppressed afterward
- [analysis] JJ Jasser — argues that weight inspection cannot reveal the systematically shaped worldview of a model trained on curated data
- [analysis] JJ Jasser — argues that fine-tuning away refusals cannot restore history that was never in the training data
- [analysis] JJ Jasser — recommends that no benchmark score earn a censoring model a place in education until its data is transparent
- [fact] JJ Jasser — reports that at the World Artificial Intelligence Conference in Shanghai, China called open source and openness "vital pathways" to inclusive AI development
- [fact] JJ Jasser — reports that China announced at the conference the World Artificial Intelligence Cooperation Organization, an intergovernmental body headquartered in Shanghai and pitched to the Global South
- [analysis] JJ Jasser — cites Carnegie Endowment researchers as documenting a pivot in Beijing's AI diplomacy from exporting infrastructure toward recrafting global AI governance norms and institutions
- [analysis] JJ Jasser — argues that when "open" becomes a geopolitical brand, the open-source versus open-weight distinction determines who can inspect the systems entire regions build on [[open-washing-four-criteria#Key Quotes|Key Quotes]]
- [analysis] JJ Jasser — grants that China is not losing the AI race in raw capability, and locates the gap instead in the ceiling that opacity sets on trust

## Key Quotes

> "\"Open-source\" is not a marketing register. It is a standard with specific criteria." — JJ Jasser, professor and director of data analytics, Rollins College

> "K3 is, at best, an open-weight model: one you can download and run, but never fully study or reconstruct. Today it is not even that." — JJ Jasser, professor and director of data analytics, Rollins College

> "Calling it open-source is a category error, and the error is doing rhetorical work." — JJ Jasser, professor and director of data analytics, Rollins College

> "When \"open\" becomes a geopolitical brand, the difference between open-source and open-weight stops being pedantic; it determines who can inspect the systems entire regions will build on." — JJ Jasser, professor and director of data analytics, Rollins College

## Connections

- references: [[OpenWashing]] — applies the open-washing charge to Kimi K3 and restates the term as borrowing openness's credibility without its transparency
- defines: [[OpenSourceAI]] — presents a four-criterion test (architecture, training code, weights, training data, all under unrestricted licenses) as the bar for open-source AI
- cites: [[OpenSourceInitiative]] — relies on the OSI's software definition and the requirements of its 2024 Open Source AI Definition as the governing standard
- references: [[MoonshotAI]] — maker of Kimi K3, whose promised July 27 weight release and expected "Modified MIT" license Jasser examines
- references: [[OpenWeights]] — places K3 at best in the open-weight category, downloadable but not reconstructable
- references: [[TrainingData]] — argues data transparency is the only way to explain a model's omissions
- references: [[ModelLicensing]] — notes K3's expected "Modified MIT" license is not OSI-approved
- references: [[FineTuning]] — argues fine-tuning away refusals cannot restore history absent from the training data
- references: [[open-weight-diplomacy-digital-silk-road|Open-Weight Diplomacy]] — another essay on Kimi K3 and China's AI diplomacy, which reports that the weights did ship on July 27
