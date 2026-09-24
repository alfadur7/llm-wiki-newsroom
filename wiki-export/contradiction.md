# Contradictions by Theme

This page surveys the **23 source-to-source contradictions** recorded across the wiki's sources, grouped into 4 topic categories plus a residual bucket that is currently empty. Each category has its own page, linked below, where the opposing camps and their evidence are set out in full. For the subject-by-subject map of the wiki, start at [[index]].

**Summary of recent update** (2026-09-24): a batch of new sources raised the recorded disagreements from one to 23, and the single theme on training data became four. None of the 23 is a clash of measured facts. Each is an argued disagreement between named voices, and several are paired by this wiki from separate sources rather than being direct exchanges between the parties.

## Synopsis

The four themes sort onto three tension axes.

**First, components: what an open system must include.** The oldest and most technical question is whether a model can be called open source without its [[TrainingData|training data]]. The [[OpenSourceInitiative|Open Source Initiative]] (OSI) holds that detailed information about the data is enough. The [[FreeSoftwareFoundation|Free Software Foundation]] (FSF), OSI co-founder Bruce Perens and a Debian proposal hold that the data itself must be released. The argument has spread from the OSI's own drafting process to Debian and the FSF, each setting its own bar.

**Second, authority: who sets and applies the label.** Two themes turn on authority rather than on components. [[Meta]] calls Llama "open source" and disputes the OSI's standing to say otherwise. Critics of the Open Source AI Definition (OSAID) dispute whether any single steward's pass/fail line should carry the name at all. The OSI holds no trademark on the term and no enforcement lever, and its lists of which systems pass are, in its own words, "not certifications of any kind."

**Third, release: what open weights call for.** The safety theme sets advocates who treat openness as a safety mechanism against critics who hold [[OpenWeights|open weights]] uniquely hard to govern. Both sides accept that released weights leave the developer's control. They differ on whether wide access helps defenders or attackers more.

---

## Per-Theme Deep Analysis

### Components: what open source AI must include

1. **[[open-training-data-requirement|OSAID Definition vs Open Training-Data Requirement]]** (6 disagreements) — The OSI's October 2024 definition accepts "data information" in place of the data itself. It argues that training data is not part of the "preferred form for making modifications," and its FAQ says a data requirement would shut out fields such as medical AI. Red Hat's Chris Wright adds that most improvement happens by modifying weights or through [[FineTuning|fine-tuning]]. The FSF, Perens and AWS's Tom Callaway hold the data to be the source of a model, and Mo Zhou's Debian resolution would declare models without it non-free ([[debian-ai-models-dfsg|LWN on the resolution]]). Open Future's Alek Tarkowski and Paul Keller accept the data-information floor but would have named it after open weights ([[open-future-osaid-step-forward|their assessment]]).

   Both camps concede ground. All three voices that raise medical data accept it as a case where withholding is defensible, and Red Hat calls its weights-first threshold "a starting point." The open-data releases listed in [[case-against-osaid|The New Stack's round-up]] answer the charge that there is "no good example" of an open-data model. They do not answer the objection that open data is too thin to train large foundation models. The theme page sets one set of monitoring points per camp: the Debian vote and the FSF's pending criteria on one side, the EU AI Act's training-data template on the other.

### Authority: who sets and applies the label

2. **[[llama-open-source-label|Meta's 'open source' label for Llama vs the OSI and critics' rejection]]** (8 disagreements) — [[Meta]] has called each Llama generation "open source," from the [[llama-2-meta-microsoft|Llama 2 release]] to [[open-source-ai-path-forward|Mark Zuckerberg's 2024 letter]]. Its spokesperson rejects the OSI's definition, defends the license and its acceptable use policy as guardrails against harmful deployments, and points to rival codifications from the Linux Foundation, the FSF and others. Meta also puts off training-data disclosure while regulation evolves. The OSI's [[osi-meta-llama-2-license-not-open-source|2023 post]] rules the license out under two non-discrimination clauses of the [[OpenSourceDefinition|Open Source Definition]]. Andreas Liesenfeld and Mark Dingemanse reach the same verdict on other grounds, finding Llama "at best open weights" because it withholds training code and data ([[rethinking-open-source-generative-ai|their 2024 survey]] for the ACM Conference on Fairness, Accountability, and Transparency, FAccT).

   The two objections lead to different exits. A license objection could in principle be met by relicensing; the withheld-components objection could not, without the disclosure Meta has deferred. Nor do the rival codifications clear Llama: the FSF, one of those Meta cited, found the Llama 3.1 license fails freedom 0, the freedom to run the program for any purpose. Meta's side rests on first-person announcements and one spokesperson statement that never answers the clause-by-clause reading, so the two sides do not argue from a shared test.

3. **[[osaid-form-and-legitimacy|A single binary definition vs graded openness or repeal]]** (6 disagreements) — The OSI and [[Mozilla]] defend one pass/fail test as clear for developers and regulators alike. Three objections stand against it. University of Geneva researchers lean toward graded openness and the FAccT authors argue for it, as in the [[ModelOpennessFramework|Model Openness Framework]]. Bradley M. Kühn of the Software Freedom Conservancy wants the text demoted to recommendations ([[sfc-osaid-erodes-open-source|his Conservancy post]]). Joseph Jacks holds that the term cannot carry over to model weights at all ([[what-does-open-source-ai-mean|TechCrunch's drafting-stage feature]]).

   The camps sit closer on mechanics than their labels suggest. The graded critics accept a cutoff for regulatory purposes, and the OSI itself ranks open-weight systems below its line ([[osi-open-weights-good-open-source-better|OSI blog, 2026]]). What stays contested is who holds the authority to draw that line and give it the standing of the Open Source Definition. The OSI says it will not validate or review individual systems, so who applies the line to a given model is left unresolved.

### Release: what open weights call for

4. **[[open-weights-safety-tradeoff|Openness as a safety mechanism vs open weights as uniquely hard to govern]]** (4 disagreements) — A 2026 letter has more than 270 signatories, Meta and Mozilla among them. It calls openness possibly "one of the most important paths to AI safety and security" ([[open-weights-american-ai-leadership|the open weights letter]]). It argues that defenders need models comparable to the ones attackers use. David Evan Harris had argued two years earlier, in IEEE Spectrum, that safeguards can be stripped from a downloaded model, citing the "Llama 2 Uncensored" derivative, and that a release cannot be recalled ([[open-source-ai-uniquely-dangerous|his essay]]). [[Anthropic]]'s Dario Amodei opposes a ban on the category but doubts that openness helps defenders more ([[anthropic-position-open-weights-models|his position post]]).

   Both sides accept that released weights leave the developer's control; the letter concedes it in its own text. The split over whether access helps defenders or attackers more is argued more than measured. SaferAI's test of one open model is the only measured result, and it probed the safeguards the developer shipped, not stripped ones ([[open-weight-models-frontier-safety-gap|TechCrunch on the evaluation]]). Only Amodei answers the letter directly; most other pairings are set side by side across sources. The policy voices lean toward measuring first: the U.S. National Telecommunications and Information Administration ([[ntia-open-model-weights-report|NTIA]]) recommends monitoring before restricting, and Amodei proposes pre-release testing of open and closed models alike.

### Other

5. **[[other-fragmentary|Residual Fragmentary Issues]]** (0 disagreements) — The holding place for one-off disagreements that fit no axis. It is currently empty, since every one of the 23 falls under a named theme. It stays in place so that a future single dispute has a home without being spun into a thin theme of its own.

## Implications

**① Authority, more than components, runs through three of the four themes.** In the [[llama-open-source-label|Llama dispute]], Meta questions the OSI's standing rather than its reading of the license. In the [[osaid-form-and-legitimacy|binary-definition dispute]], the critics contest who may draw the line at all. Even the [[open-training-data-requirement|training-data dispute]] has moved from the OSI's process to Debian and the FSF. Since the [[OpenSourceInitiative|OSI]] has no means to make its reading stick, several stewards with different bars look likelier in the short term than one settled definition.

**② Llama is the test case that recurs across themes.** [[Meta]]'s models appear on every axis. They are the product whose label is disputed, an example of withheld training data, and Kühn's example in the binary-definition dispute. In the safety theme Meta is an advocate as well as an exhibit. It has argued since the Llama 2 release that community stress testing makes open models safer, and it signed the open weights letter. Critics answer with the 2023 [[senators-question-meta-llama-leak|LLaMA leak letter]] and the "Llama 2 Uncensored" derivative. Separately, Meta is among the OSI's corporate funders, a tie TechCrunch raised as a possible conflict of interest in the label dispute.

**③ The evidence on every axis is argument, rarely measurement.** Each of the 23 disagreements rests on attribution to a named claimant, mostly analysis- or forecast-grade argument. The measured material is thin: the FAccT survey scoring 46 systems on 14 openness dimensions, and SaferAI's single evaluation in the [[open-weights-safety-tradeoff|safety theme]]. On this evidence grade, no theme yet has the data to settle its central premise. Readers may do best to weigh each claim by who makes it and on what grounds.

**④ The concessions each theme records narrow every dispute toward the label and who applies it.** Once the ground each camp gives up is set aside, what stays open is less which components or risks matter than who may call a given system open source. The [[open-source-ai-every-camp-standard|synthesis on what clears every camp's bar]] still finds no model documented as clearing both the OSI's bar and the stricter open-data one.

**⑤ Regulation may decide what the camps cannot.** The [[EUAIAct|EU AI Act]] lifts some documentation duties for models under a free and open licence, which the FAccT authors warn makes the label worth claiming. Meta defers training-data disclosure to regulation, Open Future offers the OSAID floor as a reference for the Act's training-data template, and NTIA recommends monitoring open-weight risks. As of 2026-09 these sources record no regulator adopting a tiered scale or mandatory pre-release testing. Whether a branding dispute becomes a compliance one is the point to watch.

## Notes on the Evidence

- **Counting**: each disagreement is counted once in the total of 23. One of them — Perens's charge that the OSAID is "less than Open Source" — belongs to both the training-data and the binary-definition themes, so the per-theme figures (6, 8, 6 and 4) add up to 24.
- **Balance**: the safety theme is the smallest, with 4 disagreements, and draws on the most recent sources, reaching into 2026. The newest arguments in the Llama, training-data and binary-definition themes date from February, April and March 2025. The 2026 OSI post cited above restates the OSI's ladder rather than adding to the dispute, so those three pages may lag later events.
- **Pairings**: several oppositions are assembled by this wiki from separate sources rather than being direct replies. The training-data theme has one head-on rebuttal, Red Hat's answer to the claim that data is a model's source code.
- **Status**: no disagreement here is recorded as resolved. Each theme page closes with monitoring points instead of a verdict, and theme assignments may change as sources are added.

## Source References

- Per-theme pages: [[open-training-data-requirement|training data]], [[llama-open-source-label|the Llama label]], [[osaid-form-and-legitimacy|binary definition and legitimacy]], [[open-weights-safety-tradeoff|open weights and safety]], and the [[other-fragmentary|residual bucket]]
- Related synthesis: [[open-source-ai-every-camp-standard|What Counts as Open Source AI Under Every Camp's Standard]]
- Concept pages behind the disputes: [[OpenSourceAI|open source AI]], [[OpenWashing|open-washing]], [[ModelLicensing|model licensing]], [[AISafety|AI safety]]
- Canonical definition text: [[osi-open-source-ai-definition|The Open Source AI Definition 1.0]]
- Entry point for the whole wiki: [[index]]
