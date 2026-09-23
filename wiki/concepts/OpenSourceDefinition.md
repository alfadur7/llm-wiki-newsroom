---
title: "Open Source Definition"
type: concept
tags: [OSD, open-source, licensing, OSI, DFSG]
sources: [osi-meta-llama-2-license-not-open-source, osi-meta-llama-license-still-not-open-source, sfc-osaid-erodes-open-source, debian-ai-models-dfsg, what-does-open-source-ai-mean, osi-readies-controversial-osaid, open-future-osaid-step-forward, case-against-osaid]
last_updated: 2026-09-23
---

## Overview

The Open Source Definition (OSD) is the software-license standard stewarded by the [[OpenSourceInitiative]] (OSI). TechCrunch's Paul Sawers reported in June 2024 that the OSI had stewarded it for more than a quarter of a century. Software Freedom Conservancy's Bradley M. Kühn states the OSD was based in large part on the Debian Free Software Guidelines (DFSG), and LWN's Joe Brockmeier likewise describes it as derived from the DFSG; the OSI uses it to judge whether a license qualifies as open source.

In the AI-openness debate the OSD serves as the yardstick in two ways. The OSI applies it directly to model licenses: it cites OSD points 5 and 6, under which an Open Source license may not discriminate against persons, groups, or fields of endeavor, to rule that [[Meta]]'s Llama licenses are not open source. It is also the benchmark against which critics and defenders measure the OSI's separate [[OpenSourceAI]] definition (OSAID), which admits AI systems without their [[TrainingData|training data]].

## Key Points

- **Origin** — the sources date the OSD differently: Kühn states it was first published in February 1999, while OSI executive director Stefano Maffulli (June 2024) and OSI co-founder Bruce Perens (December 2024) each call it 26 years old.
- **Applied to Llama** — in 2023 the OSI argued that paragraph 2 of the Llama 2 license, which restricts commercial use for some users, and the Acceptable Use Policy's purpose restrictions break the OSD; it explained the field-of-use bar by noting that future uses cannot be known beforehand. In 2025 it said the Llama 3.1 Community License still fails points 5 and 6, agreed with the [[FreeSoftwareFoundation]]'s evaluation that it fails freedom 0, the freedom to use the model for any purpose, and held that the OSAID is not needed to judge the Llama licenses.
- **Whether it transfers to AI** — Perens holds that "the plain old Open Source Definition" can be applied to AI. Maffulli says a "simple translation" of the OSD to AI would not work and expects the OSAID not to last 26 years like the OSD. RedMonk's Stephen O'Grady contrasts the OSD's easy yes-or-no license test with an OSAID that needs nuance, and argues the term was defined for a narrow asset.
- **Authority carried over to the OSAID** — Open Future's Alek Tarkowski and Paul Keller argue the OSAID carries extra weight because of the OSI's standing as OSD steward. Kühn argues the OSI should have issued the OSAID as "recommendations" rather than a definition with authority equivalent to the OSD. Brockmeier notes that many critics feel the OSAID devalues the OSD.

## Connections
- [[OpenSourceInitiative]] — steward of the OSD and author of the OSAID
- [[OpenSourceAI]] — the OSI's AI definition, measured against the OSD by its critics and defenders
- [[Meta]] — whose Llama licenses the OSI rules fail OSD points 5 and 6
- [[FreeSoftwareFoundation]] — whose Llama 3.1 evaluation the OSI endorses alongside its OSD ruling
- [[ModelLicensing]] — the OSD is applied here as a test of model-license terms
- [[TrainingData]] — the component the OSAID leaves optional, the point on which critics say it departs from the OSD
