"""Shared review-cycle watermark — mine_feedback (human channel) and mine_failures (automated channel).

Both self-evolution input tools use the same watermark skeleton: `{last_review, history[]}`.
Only file I/O and advancing last_review are factored out here; the per-channel fields of
each history entry (correction_counts vs. cluster_counts, recurrence computation) are built
by each tool — the identifying part is shared, the divergent part stays with the caller.
"""
from __future__ import annotations

import json
from pathlib import Path

from _lib import atomic_write_text


def _load(path: Path) -> dict:
    """Watermark JSON as a dict. Read failure, corruption, and a non-dict root
    all give an empty dict — callers call `.get()` straight away, so returning a
    list/str root as-is takes down `mine_feedback`/`mine_failures` with an
    AttributeError."""
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def read_watermark(path: Path) -> str | None:
    """Date the last review completed (YYYY-MM-DD), or None if absent."""
    return _load(path).get("last_review") or None


def in_window(when: str | None, since: str | None) -> bool:
    """Is `when` inside the review window — **boundary day included**. An item
    with no date is included too (never hide it).

    Both the watermark and the records are day-granular, so an exclusive
    comparison drops anything logged on the checkpoint day itself, permanently
    and silently: the next run's window starts after it. The cost of showing a
    boundary-day item once more is settled at the next checkpoint; the cost of
    losing one is that nobody ever learns it existed.

    Shared by both channels because they had duplicated the comparison AND
    diverged on the undated case (the automated channel excluded, the human
    channel included). Fixing one alone would leave that divergence in place.
    """
    if not since:
        return True
    return not when or str(when) >= since


def load_history(path: Path) -> list:
    """Existing review-history list (the caller computes recurrence from this history).

    Its only callers are write paths (append, then write_review), so it does not
    use _load's fail-open: a file that exists but cannot be read would proceed as
    an empty list and overwrite the whole committed history. Only absence means
    a first checkpoint."""
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise SystemExit(f"{path} unreadable — aborting to avoid overwriting the history ({e})")
    h = data.get("history") if isinstance(data, dict) else None
    if h is None:
        return []
    if not isinstance(h, list):
        raise SystemExit(f"{path} history is not a list — aborting to avoid overwriting the history")
    return h


def write_review(path: Path, when: str, history: list) -> None:
    """Advance last_review to `when` and record history (committed to the repo)."""
    atomic_write_text(
        path,
        json.dumps({"last_review": when, "history": history}, ensure_ascii=False, indent=2) + "\n",
    )
