---
title: "EU AI Act"
type: concept
tags: [ai-act, regulation, general-purpose-ai, open-source-ai, licensing]
sources: [eu-gpai-provider-guidelines, open-future-osaid-step-forward, open-source-ai-uniquely-dangerous, osaid-take-it-or-leave-it, rethinking-open-source-generative-ai]
last_updated: 2026-09-23
---

## Overview

The EU AI Act is the European Union regulation whose obligations for providers of general-purpose AI (GPAI) models enter into application on 2 August 2025, according to the European Commission, with the Commission's enforcement powers following from 2 August 2026 and a 2 August 2027 deadline for models already on the market before August 2025. In the Commission's July 2025 guidelines, a GPAI model is one trained with more than 10^23 floating point operations of compute that can generate language, text-to-image, or text-to-video output. The Commission lists the baseline duties as giving information to AI-system providers that integrate the model and putting in place a policy to comply with European copyright law; providers of models with systemic risk must also assess and mitigate those risks and notify the AI Office. The Commission describes the guidelines as not legally binding but as its interpretation of the Act that will guide enforcement.

In this wiki the Act appears mainly through its free and open-source exemption, the point where [[OpenSourceAI]] status carries regulatory weight. The Commission's guidelines set conditions under which models released under a free and open-source license ([[ModelLicensing]]) that meet certain transparency conditions may be exempt from certain obligations, and they address when an actor modifying a model becomes its provider, a question relevant to [[FineTuning]].

## Key Points

- **Exemption scope** — Andreas Liesenfeld and Mark Dingemanse quote the 24 February 2024 draft of the Act, which exempts providers of models "under a free and open licence" from the duty to keep detailed technical documentation. David Evan Harris, a former [[Meta]] employee, says companies and allied advocacy groups made limited progress in winning exemptions for some unsecured models.
- **Open-washing incentive** — Liesenfeld and Dingemanse argue the exemption makes open source status highly attractive as a way to escape documentation duties, rewarding [[OpenWashing]]. They warn that the Act "is at risk of tying itself to a moving target: a licence-based definition of 'open source AI' that itself is evolving."
- **Training-content summary** — Article 53(1)(d) requires GPAI providers to publish "a sufficiently detailed summary about the content used for training"; the EU AI Office presented a template for it on 17 January 2025, which Yaniv Benhamou and Michel Reymond report drew mixed reactions from the Open Source Initiative (OSI) community over its lack of granularity. Liesenfeld and Dingemanse had predicted in 2024 that the template would become the focus of intense lobbying.
- **Relation to the OSI definition** — Benhamou and Reymond argue that the [[OpenSourceInitiative]]'s Open Source AI Definition (OSAID) tracks the Act's Article 53(2) open source definition closely, is stricter on [[TrainingData]] disclosure, and should not in principle conflict with it, since the Act governs EU market access. Alek Tarkowski and Paul Keller of Open Future say the OSAID's name aligns it with the Act's definition, which also does not require training data to be shared, and propose the OSAID data requirements as a reference point for the Act's transparency requirement.

## Connections

- [[OpenSourceAI]] — the status that triggers the Act's free and open-source exemption
- [[ModelLicensing]] — the license a model is released under determines exemption eligibility
- [[OpenWashing]] — the practice critics say the licence-based exemption rewards
- [[TrainingData]] — the subject of the Article 53(1)(d) training-content summary
- [[FineTuning]] — the guidelines address when a modifying actor becomes a provider
- [[OpenSourceInitiative]] — its OSAID is compared against the Act's open source definition
- [[Meta]] — Harris, a former employee, discusses the exemption fight over unsecured models
