"""Completion-threshold counts derived from the manifest criterion roster.

Computes the completion counts (total·required) from each content-type's
`roster` in `.claude/layers/_manifest.json` (the full enumeration of
required·optional criteria). After the craft extraction reduced the Rubric
tables out of the layers, this replaces the old `_rubric.py` table parsing with
the manifest roster as the single SoT — eliminating the mirror (the Part1/Part2
table·header echo).

The `threshold_label` format is byte-identical to `_rubric.py` (zero regression
in the completion-condition string).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import NamedTuple

_MANIFEST_PATH = Path(__file__).resolve().parents[2] / ".claude" / "layers" / "_manifest.json"


class Counts(NamedTuple):
    """Per-content-type roster tally (threshold_label reads only total·required)."""
    total: int
    required: int


def _load_manifest() -> dict:
    return json.loads(_MANIFEST_PATH.read_text(encoding="utf-8"))


def counts(content_type: str) -> Counts:
    """Compute (total, required) from manifest[content_type].roster.

    total = len(required) + len(optional), required = len(required).
    A content-type with no roster defined yields Counts(0,0)."""
    roster = _load_manifest().get(content_type, {}).get("roster")
    if not roster:
        return Counts(0, 0)
    req = roster.get("required", [])
    opt = roster.get("optional", [])
    return Counts(total=len(req) + len(opt), required=len(req))


def threshold_label(c: Counts, *, exclude_total: int = 0, exclude_required: int = 0) -> str:
    """`required {R} + overall {X}+/{Y} PASS` format.

    Variants with exemption criteria (e.g. contradiction other-fragmentary
    exempts N2·D5·D6·S3) subtract the exempted counts from total·required
    separately — required exemptions (N2, 1 item) and optional exemptions
    (D5·D6·S3, 3 items) differ, so the two arguments are kept separate."""
    total = max(0, c.total - exclude_total)
    req = max(0, c.required - exclude_required)
    pass_min = max(0, total - 2)  # PASS bar = total - 2 advisory tolerance
    return f"required {req} + overall {pass_min}+/{total} PASS"
