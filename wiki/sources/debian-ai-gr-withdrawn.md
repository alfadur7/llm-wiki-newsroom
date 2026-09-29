---
title: "Debian AI General Resolution Withdrawn"
type: source
tags: [debian, dfsg, training-data, open-source-ai, OSAID]
published: 2025-05-20
scraped: 2026-09-27
source_file: raw/NewsScrap/Debian AI General Resolution withdrawn.md
source_url: "https://lwn.net/Articles/1020968/"
last_updated: 2026-09-27
---

## Summary

Joe Brockmeier reports for LWN that Debian developer Mo Zhou withdrew, on May 8, 2025, his proposed General Resolution (GR) that would have required the original [[TrainingData|training data]] for AI models to be released before they could count as compliant with the Debian Free Software Guidelines (DFSG). According to the report, early support gave way to objections that the rule would also make trained components of long-standing packages such as Bayesian spam filters, OCR tools, and text-to-speech software non-free, and none of the counter-proposals had gathered enough sponsors for the ballot. Brockmeier contrasts the proposal with the [[OpenSourceInitiative]]'s Open Source AI Definition (OSAID), which does not require training data, and notes that Zhou expects to need a few months before returning to the GR.

## Key Claims

- [fact] Mo Zhou — posted an early draft of the GR to the debian-project mailing list in February and sent a revised proposal to the debian-vote mailing list on April 19
- [fact] Mo Zhou — proposed that "AI models released under open source license without original training data or program" are not seen as DFSG-compliant
- [analysis] Joe Brockmeier — explains that an artifact that is not DFSG-compliant cannot enter Debian's main repository, though Debian can still distribute it through the contrib, non-free, and non-free-firmware repositories, which are not part of the distribution
- [analysis] Joe Brockmeier — states that Zhou's proposal contrasts with the [[OpenSourceInitiative]]'s OSAID, announced in October 2024, which does not require the release of [[TrainingData|training data]]
- [analysis] Joe Brockmeier — reports that the OSI judged it sufficient to provide model parameters plus detailed training-data information that would let "a skilled person" build "a substantially equivalent system"
- [fact] Thorsten Glaser — proposed a counter-proposal that would require model training to happen during the package build or the model to be rebuilt reproducibly, in addition to requiring training data
- [analysis] Joe Brockmeier — notes that Glaser's counter-proposal would demand training hardware from Debian's infrastructure
- [fact] Sam Hartman — proposed that each application could define its own preferred form of modification, which might or might not include training data
- [fact] Bill Allombert — argued that without training data Debian has no way to know what is inside a model, which "could generate backdoors and non-free copyrighted material"
- [analysis] Sam Hartman — countered that Debian had accepted x86 machine code as a preferred form of modification and that inspectability has never been at the core of the DFSG
- [forecast] Sam Hartman — predicted that "black box inspection tools" would eventually improve the ability to inspect models
- [fact] Aigars Mahinovs — submitted a proposal stating that training data is not source code for DFSG purposes, requiring the OSAID's "training data information" and treating actual training data as "an intermediate build artifact"
- [fact] Wouter Verhelst — objected to Mahinovs' proposal, saying Debian would have to drop its reproducibility goals if such AI models were accepted in main
- [analysis] Stefano Zacchiroli — suggested that the Mahinovs and Hartman proposals could be merged because they went in the same direction
- [fact] Joe Brockmeier — reports that none of the counter-proposals had received enough sponsors to be added to the ballot
- [analysis] Joe Brockmeier — notes that games, spam filters, OCR tools, and text-to-speech software also depend on trained models missing their training data and could be seen as non-free under the proposal
- [fact] Ansgar Burchardt — pointed out that spam or phishing emails could not be packaged as training data for Bayesian classifiers because they are unlikely to be under a free license
- [analysis] Russ Allbery — said a classifier trained on such data would not be DFSG-free and should not be included in Debian main
- [analysis] Sam Hartman — argued that excluding Bayesian classifiers from main would mean Debian had "lost sight of our users"
- [forecast] Stefano Zacchiroli — predicted that, if the proposal won, packagers would have to patch software to download model data on first use or give up maintaining those packages
- [fact] Mo Zhou — withdrew the proposal on May 8, saying the community was unprepared to vote on it
- [fact] Mo Zhou — asked for tools to scan the Debian archive for packages the GR might affect
- [fact] Mo Zhou — said he would build a demonstration of a backdoor planted in a neural network, and that he would need a few months before returning to the GR
- [analysis] Russ Allbery — said delaying the GR was the right decision because developers had not thought the question through as thoroughly as they believed
- [fact] Joe Brockmeier — reports that Hartman and Mahinovs formally withdrew their proposals, while Glaser had not withdrawn his
- [forecast] Joe Brockmeier — expects that defining AI models without overlapping less controversial data will be difficult for Debian

## Key Quotes

> "AI models released under open source license without original training data or program" are not seen as DFSG-compliant. — Mo Zhou, Debian developer (Proposal A text)

> "The model could generate backdoors and non-free copyrighted material or even more harmful content." — Bill Allombert, Debian developer

> "That doesn't mean I think it's bad or immoral or anything like that. I have a database like that myself. :) It's simply not free software, and is outside the scope of what Debian is for." — Russ Allbery, Debian developer

> "Saying that even if someone is as dedicated to freedom as they can be, they can never live up to our standards and include that reasonable functionality in Debian main makes me think we have lost sight of our users." — Sam Hartman, Debian developer

> "I don't think anyone is saying that we shouldn't have this conversation and a vote, only that we (myself very much included) are realizing that we hadn't actually thought this through as thoroughly as we had thought." — Russ Allbery, Debian developer

## Connections

- contradicts: [[OpenSourceAI]] — Zhou's proposal would deny DFSG status to models without training data, which the OSAID admits as open-source AI
- cites: [[OpenSourceInitiative]] — quotes the OSAID's parameters-plus-data-information standard that Zhou's proposal contrasts with
- references: [[TrainingData]] — whether training data must be released is the question the GR raised and left unresolved
- references: [[OpenWeights]] — models released under open licenses without training data are the case the GR would classify as non-free
- contradicts: [[debian-ai-models-dfsg|Debian Debates AI Models and the DFSG]] — the earlier LWN report forecast the GR would likely pass; this report records its withdrawal before a vote
