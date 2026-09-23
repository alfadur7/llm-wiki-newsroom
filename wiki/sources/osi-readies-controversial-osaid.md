---
title: "OSI Readies Controversial Open AI Definition"
type: source
tags: [OSAID, open-source-ai, training-data, criticism]
published: 2024-10-25
scraped: 2026-09-23
source_file: raw/NewsScrap/OSI readies controversial Open AI definition.md
source_url: "https://lwn.net/Articles/995159/"
last_updated: 2026-09-23
---

## Summary

Writing for LWN.net two days before the board vote, Joe Brockmeier surveys the Open Source Initiative's draft Open Source AI Definition and the objections it drew. The draft requires code, model parameters, and detailed data information, but not the training data itself. Critics say that choice sets the bar too low. They include julia ferraioli, Tom Callaway, Giacomo Tesio, the Free Software Foundation, and the Software Freedom Conservancy. OSI executive director Stefano Maffulli rejects the charge that OSI compromised, and RedMonk's Stephen O'Grady argues the term "open source" should not be stretched to AI at all.

## Key Claims

- [fact] [[OpenSourceInitiative]] — scheduled its board vote on the Open Source AI Definition for 2024-10-27, with version 1.0 slated for publication on 2024-10-28
- [fact] [[StefanoMaffulli]] — announced in June 2023, as OSI executive director, the organization's intent to define open-source AI, objecting to models "claiming to be 'open' or 'Open Source'" while adding restrictions that break the Open Source Definition
- [fact] [[OpenSourceInitiative]] — held the definition's kickoff meeting on 2023-06-21 at [[Mozilla]]'s San Francisco headquarters, then ran in-person and online sessions plus an online forum
- [analysis] Joe Brockmeier — explains that an AI system's data cannot be wholly separated from the system the way a game's assets can, citing the GPLv2 release of Quake III Arena without its pak content files
- [fact] [[OpenSourceInitiative]] — takes the draft's definition of an AI system from the OECD Recommendation of the Council on Artificial Intelligence
- [fact] [[OpenSourceInitiative]] — requires in the draft the source code for training and running the system, the model parameters, and "sufficiently detailed information" about the training data
- [fact] [[OpenSourceInitiative]] — requires data information and model parameters to be available under "OSI-approved terms" rather than OSI-approved licenses
- [analysis] Joe Brockmeier — points out that the OSI has not yet supplied a definition of "OSI-approved terms"
- [fact] [[OpenSourceInitiative]] — does not require release of the [[TrainingData]] itself, only detailed information about it
- [fact] [[OpenSourceInitiative]] — published draft version 0.0.9 on 2024-08-22, acknowledging training data as "one of the most hotly debated parts of the definition"
- [analysis] [[OpenSourceInitiative]] — concluded that training data is a benefit rather than a requirement because it is not part of the preferred form for modifying an existing AI system
- [analysis] julia ferraioli — argues that without data the OSAID guarantees only the ability to use and distribute an AI system, plus building on it through transfer learning and [[FineTuning]]
- [analysis] Tom Callaway — acknowledges valid reasons to withhold training data: its monetary value, licenses that bar redistribution, confidentiality such as medical data, and copyright-lawsuit risk
- [analysis] Tom Callaway — argues that a data-optional definition devalues the meaning of "open source" in all other contexts
- [analysis] Giacomo Tesio — lists issues he considers unaddressed in the OSAID's RC2 draft, including inherent insecurity from undetectable backdoors planted in machine-learning models
- [fact] [[FreeSoftwareFoundation]] — announced it is working on a statement of criteria for free machine-learning applications
- [analysis] [[FreeSoftwareFoundation]] — holds that an ML application is not free unless all its training data and processing scripts respect the four freedoms
- [analysis] [[FreeSoftwareFoundation]] — distinguishes nonfree from unethical, saying use of a nonfree ML application with valid reasons to withhold data, such as medical data, could be ethically excusable
- [fact] Software Freedom Conservancy — announced an aspirational statement, "Machine-Learning-Assisted Programming that Respects User Freedom," developed in response to GitHub Copilot and limited to computer-assisted programming
- [analysis] Software Freedom Conservancy — says it avoided any process that auto-endorses the practices of companies with widely deployed proprietary products, without naming the OSI
- [analysis] [[StefanoMaffulli]] — rejects the claim that the OSAID lowers the bar, saying neither the more-components camp nor the weights-and-architecture camp offers an optimal approach
- [analysis] [[StefanoMaffulli]] — attributes the OSAID's preferred form for modification to its list of endorsers and to Carnegie Mellon University's comment, not to himself or the OSI board
- [analysis] [[StefanoMaffulli]] — says a "simple translation" of the Open Source Definition to AI would not work
- [analysis] Stephen O'Grady — argues the term open source should not be extended into AI, because it was defined for a narrow asset two decades ago
- [analysis] Stephen O'Grady — argues the OSAID needs nuance and explanation, unlike the Open Source Definition's easy yes-or-no license test
- [analysis] Stephen O'Grady — says the OSI should have crafted a definition from a clean slate rather than reshaping a decades-old one
- [forecast] Joe Brockmeier — expects the OSI board to adopt the current draft or something close to it, with its impact much less certain

## Key Quotes

> "After long deliberation and co-design sessions we have concluded that defining training data as a benefit, not a requirement, is the best way to go. [...] But training data is not part of the preferred form for making modifications to an existing AI system. The insights and correlations in that data have already been learned." — [[OpenSourceInitiative]], OSAID 0.0.9 announcement

> "They would be able to build on top of it, through methods such as transfer learning and fine-tuning, but that's it." — julia ferraioli

> "If we let the Open Source AI definition contain a loophole that makes data optional, we devalue the meaning of "open source" in all other contexts. While there are lots of companies who would like to see open source mean less, I think it's critical that we not compromise here, even if it means there are less Open Source AI systems at first." — Tom Callaway

> "we believe that we cannot say a ML application 'is free' unless all its training data and the related scripts for processing it respect all users, following the four freedoms" — [[FreeSoftwareFoundation]]

> "The OSAID grants users the rights (with licenses) and the tools (with the list of required components) to meaningfully collaborate and innovate on (and fork, if required) AI systems. We have not compromised on our principles: we learned many new things from actual AI experts along the way." — [[StefanoMaffulli]], OSI executive director

> "At its heart, the current deliberation around an open source definition for AI is an attempt to drag a term defined over two decades ago to describe a narrowly defined asset into the present to instead cover a brand new, far more complicated future set of artifacts." — Stephen O'Grady, RedMonk founder

## Connections

- cites: [[OpenSourceInitiative]] — quotes the 0.0.9 announcement and Maffulli's defense of the draft
- contradicts: [[OpenSourceInitiative]] — reports critics who oppose making training data optional and say the definition sets the bar too low
- defines: [[OpenSourceAI]] — sets out the draft's required components and its OECD-derived definition of an AI system
- references: [[TrainingData]] — the component whose optional status is the core of the dispute
- cites: [[FreeSoftwareFoundation]] — quotes its criteria that free ML requires free training data
- references: [[Mozilla]] — hosted the definition's 2023 kickoff meeting
- references: [[FineTuning]] — named by ferraioli as among the few things a data-less definition still permits
- references: [[osi-open-source-ai-definition|OSI Open Source AI Definition 1.0]] — the OSI's reference page for the definition under vote
- references: [[OpenSourceDefinition]] — Maffulli says a simple translation of the OSD to AI would not work, and O'Grady contrasts its yes-or-no license test with the OSAID
- cites: [[StefanoMaffulli]] — his emailed defense of the draft is the article's main answer to its critics
