---
title: "Debian Debates AI Models and the DFSG"
type: source
tags: [debian, dfsg, training-data, open-source-ai, OSAID]
published: 2025-04-25
scraped: 2026-09-23
source_file: raw/NewsScrap/Debian debates AI models and the DFSG.md
source_url: "https://lwn.net/Articles/1018497/"
last_updated: 2026-09-23
---

## Summary

Joe Brockmeier reports for LWN on a Debian General Resolution (GR) proposed by developer Mo Zhou. The GR would declare that AI models released under an open-source license without their original [[TrainingData|training data]] or training program do not meet the Debian Free Software Guidelines (DFSG). According to the report, the proposal drew broad support and enough sponsors to proceed, while Thorsten Glaser offered a far stricter counter-proposal and other developers raised questions about existing packages that ship trained weights. Brockmeier notes that passage would put Debian at odds with the [[OpenSourceInitiative]]'s Open Source AI Definition, which does not require training data.

## Key Claims

- [fact] Mo Zhou — sent a revised GR proposal to the debian-vote mailing list on April 19, with appendices on AI technology, earlier discussions, and possible implications
- [fact] Mo Zhou — proposed that "AI models released under open source license without original training data or program" are not seen as DFSG-compliant
- [fact] Mo Zhou — excluded the software that runs AI models, such as Python scripts or C++ programs, from the proposal's scope, since traditional software is already a well-defined case
- [fact] Mo Zhou — defined a pre-trained AI model as a binary "model checkpoint" or "state dictionary" of matrices and vectors that an inference program loads to produce outputs
- [analysis] Joe Brockmeier — reports an apparent consensus in the discussion that AI models lacking [[TrainingData|training data]] are not DFSG-compliant, with open questions about exact wording and the impact on existing packages
- [fact] Joe Brockmeier — reports that Francois Mazen, Timo Röhling, Matthias Urlichs, Christian Kastner, Boyuan Yang, and others replied to support and sponsor the proposal, which requires five additional sponsors to proceed
- [fact] Thorsten Glaser — posted a counter-proposal on April 23 that would require models to be trained "only from legally obtained and used works" and the training data itself to carry a license suitable for distribution
- [fact] Thorsten Glaser — proposed that a model may enter Debian's main archive only if training happens during the package build or the trained model can be rebuilt reproducibly from the same source
- [fact] Thorsten Glaser — described his counter-proposal as "a hard anti-AI stance (with select exceptions)"
- [fact] Joe Brockmeier — reports that Thomas Goirand said he would second Glaser's proposal and was the only one to endorse it so far
- [analysis] Gunnar Wolf — argued that Debian cannot extend DFSG-freeness to a binary it cannot recreate, while users could still download models elsewhere or Debian could host them in its non-free repository
- [analysis] Mo Zhou — lists in the proposal's Appendix D that almost no useful AI models could enter Debian's main archive under this interpretation
- [analysis] Mo Zhou — lists as an upside that Debian avoids handling 10+GB models in .deb packages and mirrors avoid carrying such large binaries
- [fact] Simon McVittie — asked how many packages the GR would make release-critical-buggy and whether it would take effect during the Debian 13 ("trixie") freeze or at the start of the next release cycle
- [fact] Russ Allbery — observed that GNU Backgammon ships neural-network weights that have no source code
- [fact] Ansgar Burchardt — said the GR could affect Tesseract, OpenCV, Festival, and other software with weights and data of uncertain origin
- [analysis] Matthias Urlichs — suggested the affected packages could move to Debian's contrib archive with their models placed in non-free, rather than be removed
- [forecast] Joe Brockmeier — expects the GR would be likely to pass if the discussion reflects the overall mood of Debian developers
- [analysis] Joe Brockmeier — states that passage would contrast with the [[OpenSourceInitiative]]'s Open Source AI Definition, which requires weights under "OSI-approved terms" but not the supply of [[TrainingData|training data]]
- [analysis] Joe Brockmeier — notes that many critics feel the OSAID devalues the Open Source Definition, which was itself derived from the DFSG

## Key Quotes

> "AI models released under open source license without original training data or program" are not seen as DFSG-compliant. — Mo Zhou, Debian developer (Proposal A text)

> "cannot magically extend DFSG-freeness to a binary we have no way to recreate" — Gunnar Wolf, Debian developer

> "a hard anti-AI stance (with select exceptions)" — Thorsten Glaser, Debian developer

> "I'm not even sure if the data on which it's trained (backgammon games, I think mostly against bots) is copyrightable." — Russ Allbery, Debian developer

## Connections

- contradicts: [[OpenSourceAI]] — the GR would deny free-software status to models without training data, which the OSAID admits as open-source AI
- references: [[OpenSourceInitiative]] — the OSAID steward whose definition the GR would contrast with
- references: [[TrainingData]] — the component whose absence the proposal treats as disqualifying
- references: [[OpenWeights]] — models released under open licenses without their training data are the case the GR classifies as non-free
- references: [[ModelLicensing]] — the proposal holds that a DFSG-compliant license alone does not make a model free
- references: [[OpenSourceDefinition]] — notes critics feel the OSAID devalues the OSD, which was itself derived from the DFSG
