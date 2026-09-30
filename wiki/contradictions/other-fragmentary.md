---
title: "Residual Fragmentary Issues"
type: contradiction
tags: [residual, open-source-ai, licensing, open-weights, regulation]
sources: [debian-ai-gr-withdrawn, debian-ai-models-dfsg, lwn-openmdw-license-review, openmdw-1-1-nvidia-adoption, open-weights-not-open-source-label-dispute, eu-ai-act-gpai-guide-open-source-developers, osi-eu-code-of-practice-open-source, open-weight-diplomacy-digital-silk-road, open-weights-american-ai-leadership, knives-out-open-weight-ai-models, beyond-deepseek-china-open-weight-ecosystem]
last_updated: 2026-09-30
---

# Residual Fragmentary Issues

## Opposing Positions

This page holds the source-to-source disagreements that fit no named theme. They share no single axis. Five disagreements sit here, and they fall into three groups by character: a forecast overtaken by events, one license review read in opposite ways, and two single-pair disputes that no other source joins.

**Forecast overtaken by events**: In April 2025 LWN reported that a Debian proposal to deny free-software status to AI models shipped without their [[TrainingData|training data]] looked likely to pass. Its later report records the proposal's withdrawal before any vote. The two reports do not oppose each other; the second supersedes the first's forecast.

**One review, opposite readings**: The [[LinuxFoundation|Linux Foundation]] presents its [[OpenMDW]] model license as clear and permissive. Reviewers on the [[OpenSourceInitiative|Open Source Initiative]] (OSI) license-review mailing list objected to specific clauses in its text. Former OSI executive director [[StefanoMaffulli|Stefano Maffulli]] attributes those objections to ideological bias. The two disagreements here are about the same review.

**Single-pair disputes**: A guide to the [[EUAIAct|EU AI Act]] reads the European Commission's guidelines as letting a free and open-source license carry proportionate safety restrictions. The OSI had argued, against earlier drafts of the EU Code of Practice, that use restrictions conflict with the [[OpenSourceDefinition|Open Source Definition]] ([[osi-eu-code-of-practice-open-source|OSI on the EU Code of Practice]]). Separately, the industry open letter *Open Weights and American AI Leadership*, hosted by Microsoft, says [[OpenWeights|open weights]] help organizations avoid lock-in ([[open-weights-american-ai-leadership|the letter]]). Chinmayi Sharma, an associate professor at Fordham Law School writing in Lawfare, argues they are not inherently sovereignty-enhancing.

## Representative Evidence

*Forecast overtaken by events*

- [[debian-ai-models-dfsg#Key Claims|LWN, "Debian debates AI models and the DFSG"]] — Joe Brockmeier reported on 2025-04-25 that Mo Zhou's General Resolution already had enough sponsors, and that "if the discussion reflects the overall mood of Debian developers, the GR would be likely to pass."
- [[debian-ai-gr-withdrawn#Key Claims|LWN, "Debian AI General Resolution withdrawn"]] — Brockmeier then reports that Zhou withdrew the proposal on May 8, 2025, saying the community was unprepared to vote. Objections had grown that trained components of spam filters, OCR tools and text-to-speech packages would become non-free.

*One review, opposite readings*

- [[openmdw-1-1-nvidia-adoption#Key Quotes|Linux Foundation, OpenMDW-1.1 release]] — the Linux Foundation's own press release, from 2026-05-28, quotes CEO Jim Zemlin: NVIDIA's adoption helps establish "a clear and permissive framework for sharing AI models at global scale." No outside assessment of the license appears in it.
- [[lwn-openmdw-license-review#Key Quotes|LWN, "Considering the OpenMDW license"]] — Pamela Chestek calls the duty to clear third-party rights "an impossibility generally," and Richard Fontana calls the termination clause too broad. Simon Phipps writes that "a license revoking Freedom 0 upon a copyright claim cannot assure software freedom."
- [[open-weights-not-open-source-label-dispute#Key Quotes|The Register, "Open weights are not open source"]] — Steven J. Vaughan-Nichols quotes Maffulli: "I continue getting the impression that the OpenMDW review is tainted by an ideological bias." The column itself calls the OpenMDW approach reasonable and ends without a verdict.

*Single-pair disputes*

- [[eu-ai-act-gpai-guide-open-source-developers#Key Claims|Osborne et al., EU AI Act guide for open-source developers]] — the authors read paragraphs 78 and 83 of the Commission's guidelines as excluding research-only and acceptable-use licenses. They read paragraph 84 as allowing "specific, proportionate, and safety-oriented usage restrictions" where the licensor sees a significant risk.
- [[open-weight-diplomacy-digital-silk-road#Key Claims|Sharma, "Open-Weight Diplomacy"]] — Sharma grants that a weight file can be copied and "kept forever," unlike a Huawei switch. She argues that countries adopting Chinese models grow dependent "because of the next release they don't have."

## Derived Tensions & Generational Readings

Each group stays out of the named themes for its own reason. The Debian pair touches the question of the [[open-training-data-requirement|OSAID Definition vs Open Training-Data Requirement]] theme, but the two reports agree on the substance. What changed between them is the event, so the pair is a time-shifted update rather than an opposition. The withdrawal did not settle the question: Zhou said he would need a few months before returning to it ([[debian-ai-gr-withdrawn|LWN]]). As of 2026-09, no later report is in these sources.

The OpenMDW pair is the only group with a shared axis. Both disagreements concern whether a license written for whole model distributions meets the OSI's standard. The Linux Foundation's side is voiced mainly through its own release and Mike Dolan's replies on the list, where he defends the termination clause as symmetry. A model publisher's exposure runs under copyright, he argues, so a patent-only provision "would replicate Apache-2.0's form while abandoning its function." Chestek answered that the license is not symmetric: the model's producer may know whether it copied protected material, while the recipient gives up its copyright claims without knowing whether they were infringed ([[lwn-openmdw-license-review|LWN]]).

Maffulli's charge moves the question from the license text to the reviewers. The dispute is over how to read the objections: LWN reports them as clause-level defects, while Maffulli reads them as motive. His charge carries weight as the view of the executive who led the OSI's own definition, yet it comes from a single quote ([[open-weights-not-open-source-label-dispute|The Register]]).

The EU pair is narrower than its wording suggests. The OSI's post, from March 2025, objected to Code of Practice drafts that *mandated* acceptable use policies: under those drafts, it wrote, "developers would have to choose between complying with the Code of Practice or being Open Source." It reports that the third draft made them optional ([[osi-eu-code-of-practice-open-source|OSI]]). The guide, from August 2025, reads a different instrument, the Commission's guidelines, as *permitting* some restrictions ([[eu-ai-act-gpai-guide-open-source-developers|the guide]]). The two meet only at the level of principle: whether any use restriction can sit inside an open-source license. The same principle drives the [[llama-open-source-label|vendor-label theme]], but there the subject is a vendor's claim, not a regulator's definition. The OSI's answer to paragraph 84 itself is not in these sources.

Sharma's argument sits beside the [[open-weights-safety-tradeoff|safety theme]] without joining it. That theme asks whether open release helps defenders or attackers; Sharma sets misuse risk aside as real but not the largest stake. Her subject is dependency through compute, cloud and the next release ([[open-weight-diplomacy-digital-silk-road|Sharma]]). The pairing with the open weights letter rests on a match of signatories. Sharma describes an industry letter, without giving its title, signed by Nvidia, Microsoft, Meta and over 230 other companies and organizations. The Microsoft-hosted letter lists the same three companies and reports more than 270 signatories as of 2026-08-03. Its case is that organizations "want to know that they will not become locked into a single provider or lose the knowledge and capabilities they build over time." The letter's signatories give no reply to her in these sources ([[open-weights-american-ai-leadership|the letter]]).

The pairs differ in how far their disagreement has gone. Only the EU pair gives opposite answers to one question, and even there the two sides read different instruments. The OpenMDW objections are specific and quoted, but their motive is contested. The Sharma pair is a claim that has drawn no reply, and the Debian pair records an update.

## Interpretive Direction

On current evidence, the OpenMDW pair looks like the nearest candidate for promotion out of this bucket. LWN reports that the OSI does not appear ready to approve the license in its current form, and that the changes needed have not been specified. An OSI decision, a revised license, or a Linux Foundation answer to the reviewers would each add claims on the same axis. The EU guide's authors, who include Linux Foundation researchers writing in a personal capacity, also judge that OpenMDW likely qualifies as a free and open-source license under the Act. That opinion predates the dispute: the guide appeared on 2025-08-04, before OpenMDW-1.1 (2026-05-28) and LWN's report on the OSI review (2026-08), and it tests the license against the Act's own definition of a free and open-source license, not the Open Source Definition. Restated against the OSI's standard, it could form a third side. If such claims accumulate to theme size, a theme on model-specific licenses against the Open Source Definition could absorb both the OpenMDW pair and the EU pair, since both turn on what an open license may restrict.

The other items currently point elsewhere. If Debian revives the resolution, the new reports belong in the training-data theme, and the withdrawal becomes that theme's history. Sharma's dependency argument would need answers from other sources before it could stand as an axis. Adjacent Lawfare and Stanford HAI pieces cover the same Chinese releases ([[knives-out-open-weight-ai-models|Lawfare, "Knives Are Out"]]; [[beyond-deepseek-china-open-weight-ecosystem|Stanford HAI, "Beyond DeepSeek"]]), and they are the likely starting points. The landscape these fragments sit in is surveyed in the [[open-source-ai-definition|Open-Source AI Definition]], [[open-weights|Open Weights]] and [[open-model-governance|Open-Model Governance]] cluster overviews. The [[distillation-free-riding-dispute|distillation theme]] and the [[osaid-form-and-legitimacy|definition-legitimacy theme]] complete the set of named themes.
