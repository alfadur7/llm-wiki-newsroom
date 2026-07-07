"""Page-gap suggestions - informational lint pass.

Aggregates two signals for "pages worth creating":
  link_candidates - hub backlink clusters pointing at broken targets
  text_candidates - plain-text noun candidates without matching pages

Unlike other lint checks, this pass never fails the suite (rc always 0).
Results are ranked candidates for human review, not actionable issues.

The two signals stay in separate modules on purpose:
  - Independent algorithms with no shared logic (backlink-graph analysis
    vs. text heuristics), so merging them would bundle ~360 lines of
    unrelated code into one file.
  - `text_candidates.py` carries large, continuously-curated noise tables
    (BLOCKLIST, KOREAN_ALIAS, Korean tail-noise) that are edited
    frequently as new false positives surface; keeping them in a
    dedicated file makes the edit surface obvious.
  - Matches the one-check-per-file convention used elsewhere under
    `_lint/` (structure.py, source_orphans.py, cited_speakers.py, ...).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lint import link_candidates, text_candidates  # noqa: E402


def run(*, json_out: bool = False,
        min_seeds: int = 2,
        min_mentions: int = 10,
        min_pages: int = 5,
        top: int | None = None) -> int:
    if json_out:
        cc_results = link_candidates._find(min_seeds=min_seeds)
        if top is not None:
            # --top caps results per signal (lint.py help) — text_candidates
            # below already honors it; without this slice the JSON doc emitted
            # the full uncapped link_candidates list.
            cc_results = cc_results[:top]
        cc_payload = {"min_seeds": min_seeds, "results": cc_results}
        tc_payload, _ = text_candidates._candidates(
            min_mentions=min_mentions,
            min_pages=min_pages,
            top=top if top is not None else text_candidates.DEFAULT_TOP,
        )
        # Emit ONE combined JSON document so a consumer can json.loads the
        # stream; previously link_candidates and text_candidates each printed
        # their own object, yielding two concatenated docs ("Extra data" error).
        print(json.dumps(
            {"link_candidates": cc_payload, "text_candidates": tc_payload},
            ensure_ascii=False,
            indent=2,
        ))
        return 0

    print("Page-gap suggestions — informational, not failures.")
    print("These are ranked candidates for new pages; human review required.\n")

    cc_kwargs = {"min_seeds": min_seeds}
    if top is not None:
        cc_kwargs["top"] = top
    link_candidates.run(**cc_kwargs)
    print()

    tc_kwargs = {"min_mentions": min_mentions, "min_pages": min_pages}
    if top is not None:
        tc_kwargs["top"] = top
    text_candidates.run(**tc_kwargs)
    return 0
