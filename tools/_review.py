"""Shared review-cycle watermark — mine_feedback (human channel) and mine_failures (automated channel).

Both self-evolution input tools use the same watermark skeleton: `{last_review, history[]}`.
Only file I/O and advancing last_review are factored out here; the per-channel fields of
each history entry (correction_counts vs. cluster_counts, recurrence computation) are built
by each tool — the identifying part is shared, the divergent part stays with the caller.
"""
from __future__ import annotations

import json
from pathlib import Path


def _load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def read_watermark(path: Path) -> str | None:
    """Date the last review completed (YYYY-MM-DD), or None if absent."""
    return _load(path).get("last_review") or None


def load_history(path: Path) -> list:
    """Existing review-history list (the caller computes recurrence from this history)."""
    return _load(path).get("history") or []


def write_review(path: Path, when: str, history: list) -> None:
    """Advance last_review to `when` and record history (committed to the repo)."""
    path.write_text(
        json.dumps({"last_review": when, "history": history}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
