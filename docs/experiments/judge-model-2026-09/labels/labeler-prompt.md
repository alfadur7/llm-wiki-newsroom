L2-1 source VERIFY₂ — Desk review of source pages (working dir: <repo root>). Read-only: no edits.

Follow `.claude/agents/desk.md` in full for the **L2-1 source** cell: read each page in full and its raw original (`source_file:`) side by side, under desk.md's I/O contract (including its rule for raws over 40KB), apply the six lenses and both personas, and run the attribution spot check against the original. Review each page independently of the others.

Report **every** defect you find — there is no cap on the number per page. Rate severity strictly on desk.md's scale.

Ground only on: the pages listed below, their raw originals, hub pages they link where you need them, and the SoTs desk.md names. Do not read `log.md`, git history, or anything under `tools/`.

Reply with JSON lines only — no other text, no code fence:
- one object per defect: {"page": "<slug>", "severity": "critical|high|medium|low", "lens": "<lens>", "location": "<short quote from the page>", "issue": "<what is wrong>", "evidence": "<what the original says, or why>"}
- then one object per page, including pages with no defects: {"page": "<slug>", "reviewed": true, "defects": <count>}

Pages (slugs under wiki/sources/):
