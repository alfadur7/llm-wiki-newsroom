---
title: "Model Licensing"
type: concept
tags: [licensing, open-source-ai, governance, copyleft]
sources: [open-source-ai-models-how-open, case-against-osaid, osi-open-source-ai-definition]
last_updated: 2026-06-26
---

## Overview

Model licensing governs how an AI model may be used, modified, and redistributed, and it is where open-source AI diverges from traditional open-source software. Conventional OSS licenses split into permissive families (MIT, BSD, Apache 2.0) that impose few obligations and copyleft families (GPL 2.0/3.0, Affero GPL) that require sharing derived source under the same terms. AI models add components beyond software — training data, data information, weights, and parameters — so a software license alone cannot make a model open. DeepSeek R1 ships its weights under the permissive MIT license, while [[Meta]]'s Llama uses a custom community license with usage restrictions that the [[OpenSourceInitiative]] judges incompatible with the [[OpenSourceAI]] freedoms.

## Connections
- [[OpenSourceAI]] — licensing is one component the OSAID evaluates
- [[OpenWeights]] — a licensing posture that releases weights but not data
- [[OpenWashing]] — restrictive license terms enable open-washing
- [[OpenSourceInitiative]] — the body that judges license compatibility
- [[Meta]] — issuer of the contested Llama community license
