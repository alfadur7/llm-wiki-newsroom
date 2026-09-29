---
title: "Open weights are not open source: Why AI's favorite label is under dispute"
type: source
tags: [open-weights, open-source-ai, OSAID, licensing, open-washing]
published: 2026-09-15
scraped: 2026-09-27
source_file: "raw/NewsScrap/Open weights are not open source Why AI's favorite label is under dispute.md"
source_url: "https://www.theregister.com/columnists/2026/09/15/open-weights-are-not-open-source-why-ais-favorite-label-is-under-dispute/5295436"
last_updated: 2026-09-27
---

## Summary

In a 2026-09-15 column for The Register, Steven J. Vaughan-Nichols argues that most models the AI industry calls "open source" are only [[OpenWeights|open-weight]]: users can download and run them but cannot inspect, reproduce or rebuild them. He sets the [[OpenSourceInitiative]]'s own distinction and Stanford HAI director James Landay's critique beside the continuing attacks on the OSI's [[OpenSourceAI|Open Source AI Definition]] from Bruce Perens, Bradley Kuhn, Richard Fontana and Luca Antiga. He then turns to the [[LinuxFoundation|Linux Foundation]]'s [[OpenMDW]] license, submitted to the OSI, and to former OSI executive director [[StefanoMaffulli|Stefano Maffulli]]'s charge that its review is ideologically biased. The column ends without a verdict on whether the OSI will adopt OpenMDW.

## Key Claims

- [analysis] Steven J. Vaughan-Nichols — argues that the AI industry abuses the word "open", describing models published to [[HuggingFace|Hugging Face]] as "open source" when they may only be open-weight
- [analysis] Steven J. Vaughan-Nichols — argues that the difference decides whether users can merely deploy a finished network or can inspect, reproduce, alter and redistribute the system that produced it
- [analysis] Steven J. Vaughan-Nichols — says an open-weight model can be self-hosted and [[FineTuning|fine-tuned]] on internal documents without routing prompts through a proprietary API
- [analysis] Steven J. Vaughan-Nichols — says running open weights locally can give users more control over data, privacy, costs, supplier API changes and vendor lock-in
- [fact] [[OpenSourceInitiative]] — defines open weights as "the final weights and biases of a trained neural network"
- [fact] [[OpenSourceInitiative]] — states that weights alone expose only "a fraction of the information required for full accountability"
- [fact] James Landay — calls open weights "progress" but says they amount to "open distribution", not an open model
- [analysis] James Landay — contends that without disclosed [[TrainingData|training data]] or a "thoroughly documented, auditable account of it", outsiders cannot test, reproduce or challenge a model's work in the fullest sense
- [analysis] Steven J. Vaughan-Nichols — lists what outsiders cannot determine without training data, including copyrighted or private material, underrepresented languages, benchmark leakage and post-training alignment methods
- [fact] Steven J. Vaughan-Nichols — reports that OSAID 1.0 requires model parameters, including weights, to be available under OSI-approved terms but prescribes no specific legal mechanism
- [analysis] Luca Antiga — argues that OSAID's treatment of weights leaves "a gaping hole" that makes licenses less effective for judging whether OSI-licensed AI systems can be adopted
- [fact] Bruce Perens — declared that OSAID is "not Open Source" and that the OSI itself is now involved in "Openwashing"
- [analysis] Bradley Kuhn — with Red Hat counsel Richard Fontana, calls for OSAID to be repealed, arguing that the OSI acted too quickly and that the definition split the FOSS community
- [fact] Steven J. Vaughan-Nichols — reports that the OSI acknowledged at the October 2024 release of OSAID 1.0 that the definition would continue to evolve
- [analysis] Steven J. Vaughan-Nichols — reports that critics contend OSAID's central shortcomings remain unresolved
- [fact] Steven J. Vaughan-Nichols — reports that the Linux Foundation's Mike Dolan submitted the Open Model, Data, and Weights (OpenMDW) license to the OSI
- [fact] Steven J. Vaughan-Nichols — reports that OpenMDW has existed since 2025 and lists contributors from Amazon, [[Meta]], IBM, Microsoft and Nvidia
- [analysis] Steven J. Vaughan-Nichols — explains that OpenMDW defines separate terms for a model's architecture, training data and weights, bringing them under one agreement as a form of [[ModelLicensing|model licensing]]
- [analysis] Steven J. Vaughan-Nichols — calls the OpenMDW approach reasonable and notes that the submission met objections on the OSI license-review mailing list
- [analysis] [[StefanoMaffulli]] — says the OpenMDW review appears "tainted by an ideological bias" against big tech and therefore against AI
- [forecast] Steven J. Vaughan-Nichols — warns that unless someone sets licensing terms covering code, data and weights together, "open AI" risks becoming an empty marketing term

## Key Quotes

> "Open Weights refer to the final weights and biases of a trained neural network." — [[OpenSourceInitiative]]

> "Open weights are progress. You can download the model, run it on your own machine, keep it out of someone else's data pipeline. But you still can't see how the thing was built, what it was trained on, or why it behaves the way it does. That's not an open model. That's open distribution." — James Landay, director of the Stanford Institute for Human-Centered AI

> "Open weights answer 'Can I run this?' Open source answers 'Can I trust this, improve it, and build the next thing on top of it?' Right now almost everyone – American labs and Chinese labs alike – is answering the first question but nowhere close to the second." — James Landay, director of the Stanford Institute for Human-Centered AI

> "a gaping hole that will make licenses less effective in determining whether OSI-licensed AI systems can be adopted in real-world contexts." — Luca Antiga, CTO of Lightning AI

> "It's not Open Source! … It's unfortunate that the Open Source Initiative itself is now involved in Openwashing." — Bruce Perens, author of the original Open Source Definition

> "The OSI acted too quickly to impose an overly ambitious policy compromise on the community. OSAID undeniably created a rift in the FOSS community; that rift seriously damaged the OSI's reputation, authority, and influence. Meanwhile, OSAID shows no signs of having any positive policy influence on machine learning practitioners, the FOSS community, or regulators." — Bradley Kuhn (Software Freedom Conservancy) and Richard Fontana (Red Hat)

> "I continue getting the impression that the OpenMDW review is tainted by an ideological bias: Because we don't like big tech and AI now is big tech, then we don't like AI; therefore, we'll do anything to block it." — [[StefanoMaffulli]]

## Connections

- defines: [[OpenWeights]] — quotes the OSI's definition of open weights as a trained network's final weights and biases
- cites: [[OpenSourceInitiative]] — quotes the OSI's open-weights definition and its accountability caveat
- contradicts: [[OpenSourceAI]] — Perens, Kuhn, Fontana and Antiga oppose the OSI's Open Source AI Definition, with Kuhn and Fontana calling for its repeal
- references: [[OpenWashing]] — Perens accuses the OSI itself of "Openwashing"
- references: [[TrainingData]] — Landay and the author name undisclosed training data as what blocks inspection and reproduction
- references: [[OpenMDW]] — the license the Linux Foundation submitted to the OSI, whose contributors, structure and contested review the column reports
- references: [[LinuxFoundation]] — its Mike Dolan submitted OpenMDW to the OSI
- references: [[ModelLicensing]] — OpenMDW sets separate terms for architecture, data and weights under one license
- references: [[OpenSourceDefinition]] — the OSI stewards it, and Perens wrote the original
- references: [[FineTuning]] — one of the uses open weights allow
- references: [[HuggingFace]] — the venue where models labeled "open source" are published
- references: [[Meta]] — listed among OpenMDW's contributors
- cites: [[StefanoMaffulli]] — quotes his charge that the OpenMDW review is ideologically biased
- contradicts: [[lwn-openmdw-license-review|LWN on the OpenMDW license review]] — Maffulli attributes the reviewers' objections to ideological bias, while LWN reports them as specific defects in the license text
