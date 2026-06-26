# Contradictions by Topic

A Layer 2-4 conflict-axis survey classifying the **1 source-to-source contradiction** accumulated in the wiki into 1 topic cluster plus a residual fragmentary bucket. The deep analysis of each topic lives in `wiki/contradictions/<topic>.md` (linked below); the raw individual-issue DB is `wiki/contradictions/_contradictions.json` (auto-generated — the classifier assigns `type`, `type_score`, and `evidence_strength`). The drill-down entry point is [[index]].

**Summary of recent update** (2026-06-26): the corpus holds a single registered contradiction, classified `soft` by the auto-classifier but kept as an independent theme because it is a clear single-axis dispute whose absorption into the residual bucket would dissolve the corpus's central question.

## Synopsis

The wiki's contradictions, at this stage, converge on one tension axis with a second bucket held open for residuals.

**First, the definitional boundary of "open."** The entire dispute is whether a model can be called open source without releasing its training data. The [[OpenSourceInitiative]]'s binary definition says data information is enough; the [[FreeSoftwareFoundation]] and allied critics say the raw data is effectively the source code, so anything less is "less than Open Source." This is a genuine A-vs-B contradiction between two camps of the same movement.

**Second, residual fragments.** No one-off oppositions have accumulated yet, but the bucket is kept open so that future fact checks, timeline corrections, or single-actor disputes have a home without being forced onto an axis they do not fit.

---

## Per-Theme Deep Analysis

### Definitional Boundary of Open Source AI

1. **[[open-training-data-requirement|OSAID Definition vs Open Training-Data Requirement]]** (~1 item) — The core dispute. The [[OpenSourceInitiative]] released the OSAID on 2024-10-28 defining openness by four freedoms plus data information, code, and parameters, deliberately not requiring raw training data so that fields like medical AI can participate; [[Mozilla]] endorsed it as "an important step forward." The [[FreeSoftwareFoundation]], with OSI co-founder Bruce Perens and SFC's Bradley Kuhn, counters that training data is the source code, so the OSAID dilutes the open-source brand — a grievance sharpened by the fact that a 10-person board, not the full membership, approved it. Representative evidence spans both camps, anchored by the canonical OSI statement and the round-up of critics.

### Residual & Emerging Issues

2. **[[other-fragmentary|Residual Fragmentary Issues]]** (~0 items) — The acceptance bucket for contradictions that do not converge on a single axis. It currently holds no claims, since the corpus's one contradiction stands as its own theme; it is kept in place per convention so future one-off oppositions can be absorbed rather than spun into thin standalone themes.

## Implications

**① A single question gates the whole field.** Whether "open" requires open training data is not one issue among many — it is the hinge on which the [[open-training-data-requirement|definition dispute]] turns, and it propagates into how licensing and weights-only releases are judged. Resolving it would settle most of the surrounding disagreements at once.

**② The fight has shifted from merits to institutions.** The [[FreeSoftwareFoundation]] camp's move to contest the [[OpenSourceInitiative]] board, rather than only argue the definition's substance, signals that the contradiction is now as much about who has authority to define "open source" as about the definition's content. This governance turn is worth monitoring at the next OSI board election.

**③ Coexisting standards, not a resolved one.** In the near term the practical outcome is two standards in parallel — the OSAID as the de facto reference and a stricter open-data criterion under development — rather than convergence. On adoption the OSAID leads; on legitimacy it remains contested, so the appearance of consensus should not be read as settlement.

## Source References

- Program-layer raw DB: `wiki/contradictions/_contradictions.json` (auto-generated; per-source and per-type detail)
- Per-topic deep dives: the [[open-training-data-requirement|OSAID definition dispute]] and the [[other-fragmentary|residual bucket]] linked above
- Theme derivation map: `wiki/contradictions/_contradictions_themes.json` (claim → theme assignment)
