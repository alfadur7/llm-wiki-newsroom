---
title: "What does 'open source AI' mean, anyway?"
type: source
tags: [open-source-ai, OSAID, open-washing, training-data, open-weights]
published: 2024-06-22
scraped: 2026-09-23
source_file: raw/NewsScrap/What does 'open source AI' mean, anyway TechCrunch.md
source_url: "https://techcrunch.com/2024/06/22/what-does-open-source-ai-mean-anyway/"
last_updated: 2026-09-23
---

## Summary

In a 2024-06-22 TechCrunch feature, senior reporter Paul Sawers describes how the [[OpenSourceInitiative]], led by executive director Stefano Maffulli, was drafting an Open Source AI Definition that then stood at version 0.0.8. The draft grants freedoms to use, study, modify, and share an AI system, but it makes the full [[TrainingData|training dataset]] an optional component; Maffulli argues that knowing the data's provenance and processing matters more. The piece also covers OSS Capital founder Joseph Jacks's view that open source cannot apply to model weights, and Maffulli's claim that everyone in the discussion agrees [[Meta]]'s Llama is not open source. It reports that the OSI took a Sloan Foundation grant of about $250,000 to offset its reliance on corporate donors, Meta among them.

## Key Claims

- [analysis] Paul Sawers — reports that no one agrees on what "open source" means in the context of AI, which has carried the open-versus-proprietary software tension into the AI space
- [analysis] Paul Sawers — writes that, by most estimations, [[Meta]]'s Llama-branded large language models are not really open source
- [fact] Paul Sawers — reports that the [[OpenSourceInitiative]] began working toward a definition of open source AI some three years before the article, through conferences, workshops, panels, webinars, and reports
- [fact] Paul Sawers — reports that the [[OpenSourceInitiative]] has stewarded the Open Source Definition for software for more than a quarter of a century
- [analysis] Joseph Jacks — says there is "no such thing as open-source AI," because open source was invented explicitly for software source code
- [analysis] Joseph Jacks — argues that neural network weights are not software source code, since they are unreadable by humans and not debuggable
- [analysis] Joseph Jacks — argues that the fundamental rights of open source do not translate to neural network weights in any congruent manner
- [fact] Paul Sawers — reports that Joseph Jacks and his OSS Capital colleague Heather Meeker came up with their own definition built around the concept of [[OpenWeights|open weights]]
- [fact] [[StefanoMaffulli]] — told TechCrunch that Jacks's point is correct, and that the OSI first debated whether to call it open source AI at all but found everyone already using the term
- [fact] Paul Sawers — reports that the [[OpenSourceInitiative]] relies on sponsorships from donors including Amazon, Google, Microsoft, Cisco, Intel, Salesforce, and [[Meta]]
- [fact] Paul Sawers — reports that app developers with more than 700 million monthly users must request a special license from [[Meta]] to use Llama, which Meta grants at its own discretion
- [fact] Paul Sawers — reports that [[Meta]] called Llama 2 open source but used phrases such as "openly available" and "openly accessible" for Llama 3 in April 2024, while still calling the model "open source" in some places
- [fact] [[StefanoMaffulli]] — said that everyone else in the conversation agrees Llama cannot be considered open source, and that people he spoke with at [[Meta]] know it is "a little bit of a stretch"
- [analysis] Paul Sawers — raises a possible conflict of interest in a company that piggybacks on open source branding while also funding the stewards of the definition
- [fact] Paul Sawers — reports that the [[OpenSourceInitiative]] secured a grant of around $250,000 from the Sloan Foundation to help fund its push toward the Open Source AI Definition
- [fact] [[StefanoMaffulli]] — said that the OSI could give up [[Meta]]'s money at any time and that the organization's structure does not allow its corporate donors to interfere
- [fact] Paul Sawers — reports that the Open Source AI Definition draft stood at version 0.0.8, made up of a preamble, the definition itself, and a checklist of required components
- [fact] Paul Sawers — reports that the draft grants the freedoms to use an AI system for any purpose without permission, to study how it works and inspect its components, and to modify and share it for any purpose
- [fact] Paul Sawers — reports that the draft makes access to the full training dataset an "optional" component
- [analysis] [[StefanoMaffulli]] — argues that knowing where the [[TrainingData|training data]] came from and how it was labeled, de-duplicated, and filtered matters more than having the plain dataset
- [analysis] [[StefanoMaffulli]] — says releasing the full dataset is often not possible or practical, for example when it contains confidential or copyrighted information the developer cannot redistribute
- [analysis] Paul Sawers — notes that techniques such as federated learning, differential privacy, and homomorphic encryption train models without sharing the data itself with the system
- [analysis] [[StefanoMaffulli]] — says the statistical and random logic of training means a model cannot be replicated from its dataset the way software is rebuilt from source
- [fact] Paul Sawers — reports that the definition's checklist is based on the academic paper that proposes the Model Openness Framework, which rates models on their completeness and openness
- [fact] Paul Sawers — reports that the OSI calls the planned launch the "stable version" rather than the "final release," because parts of it are likely to evolve
- [forecast] [[StefanoMaffulli]] — expects the definition not to last 26 years like the Open Source Definition, since its component checklist depends on technology
- [forecast] Paul Sawers — reports that the stable definition was expected to be approved by the OSI board at the All Things Open conference at the end of October 2024, after a roadshow across five continents
- [analysis] [[StefanoMaffulli]] — describes the definition as "feature complete," with the checklist now being tested for systems that should be included or excluded

## Key Quotes

> "Neural net weights are not software source code; they are unreadable by humans, [and they are not] debuggable. Furthermore, the fundamental rights of open source also don't translate over to NNWs in any congruent manner." — Joseph Jacks, founder of OSS Capital

> "The point is correct. One of the initial debates we had was whether to call it open source AI at all, but everyone was already using the term." — [[StefanoMaffulli]], OSI executive director

> "Everyone else that is involved in the conversation is perfectly agreeing that Llama itself cannot be considered open source. People I've spoken with who work at Meta, they know that it's a little bit of a stretch." — [[StefanoMaffulli]], OSI executive director

> "That's one of the things that the Sloan grant makes even more clear: We could say goodbye to Meta's money anytime." — [[StefanoMaffulli]], OSI executive director

> "It's much better to know that information than to have the plain dataset without the rest of it." — [[StefanoMaffulli]], OSI executive director

> "There is a variety of statistical and random logic that happens during the training that means it cannot make it replicable in the same way as software." — [[StefanoMaffulli]], OSI executive director

> "We can't really expect this definition to last for 26 years like the Open Source Definition." — [[StefanoMaffulli]], OSI executive director

> "This is the final stretch. We have reached a feature complete version of the definition; we have all the elements that we need." — [[StefanoMaffulli]], OSI executive director

## Connections

- cites: [[OpenSourceInitiative]] — quotes executive director Stefano Maffulli on the draft definition, its data rule, and the OSI's funding
- defines: [[OpenSourceAI]] — sets out the draft 0.0.8 freedoms to use, study, modify, and share an AI system
- contradicts: [[OpenSourceAI]] — Joseph Jacks argues there is no such thing as open-source AI, since open source was written for source code
- contradicts: [[Meta]] — Maffulli says Llama cannot be considered open source, against Meta's own "open source" labeling
- references: [[TrainingData]] — the draft makes the full dataset optional and prioritizes data provenance and processing details
- references: [[OpenWeights]] — Jacks and Heather Meeker propose an open-weights definition in place of open source
- references: [[ModelLicensing]] — Llama's 700-million-monthly-user license condition and the OSI's license spectrum
- references: [[OpenWashing]] — Meta's shifting "open source" and "openly available" language for Llama
- references: [[osi-open-source-ai-definition|The Open Source AI Definition 1.0]] — the stable release the June 2024 draft was heading toward
- references: [[ModelOpennessFramework]] — the draft OSAID's component checklist is based on the paper that proposes the framework
- references: [[OpenSourceDefinition]] — reports the OSI has stewarded the OSD for over 25 years, and Maffulli expects the OSAID not to last as long
- cites: [[StefanoMaffulli]] — the main speaker, explaining the drafting process and why Llama cannot be considered open source
