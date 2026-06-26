"""`tools/mine_feedback.py` recurrence-rate self-improvement signal regression tests (Brain benchmark T2).

Verifies that `--checkpoint` computes the recurrence rate of already-treated
patterns against the previous cycle's CORRECTION fingerprint — a measured
self-improvement signal (lower recurrence = feedback settled). The review window
is lower-bounded only (after the watermark), so cycles are simulated in
chronological order.

The fixtures use Korean operator utterances, and the Korean correction/prohibition
patterns are gated on korean_mode(), so these tests run under WIKI_LANG=ko via an
autouse fixture.
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import mine_feedback as mf  # noqa: E402


@pytest.fixture(autouse=True)
def _korean_mode(monkeypatch):
    monkeypatch.setenv("WIKI_LANG", "ko")


def _turn(ts, text):
    return json.dumps({"type": "user", "timestamp": ts + "T00:00:00Z",
                       "message": {"content": text}})


def _write(path, turns):
    path.write_text("\n".join(turns), encoding="utf-8")


def test_correction_counts_excludes_zero_and_noncorrection():
    from collections import Counter
    hits = Counter({"correction": 2, "추가 요구": 9, "승인·확정": 3})
    # Exclude OPERATION/SUCCESS patterns and zero-count entries; keep CORRECTION only.
    assert mf.correction_counts(hits) == {"correction": 2}


def test_first_checkpoint_has_no_recurrence(tmp_path, monkeypatch):
    monkeypatch.setattr(mf, "WATERMARK_PATH", tmp_path / "wm.json")
    cc = {"correction": 1, "prohibition": 1}
    entry = mf.write_checkpoint("2026-03-31", None, "cycle1", cc)
    assert entry.get("recurrence") is None
    assert entry["correction_total"] == 2


def test_recurrence_rate_across_cycles(tmp_path, monkeypatch):
    """Add transcripts in chronological order and verify the recurrence rate."""
    monkeypatch.setattr(mf, "WATERMARK_PATH", tmp_path / "wm.json")
    td = tmp_path / "transcripts"
    td.mkdir()

    # cycle1: only s1 exists
    _write(td / "s1.jsonl", [_turn("2026-03-01", "작업 시작"),       # kickoff (excluded)
                             _turn("2026-03-02", "그게 아니야 틀렸어"),  # correction
                             _turn("2026-03-03", "하지 마")])           # prohibition
    cc1 = mf.correction_counts(mf._scan(td, 0, mf.read_watermark())["hits"])
    mf.write_checkpoint("2026-03-31", mf.read_watermark(), "cycle1", cc1)
    assert cc1 == {"correction": 1, "prohibition": 1}
    assert mf.read_watermark() == "2026-03-31"

    # cycle2: add s2 — correction recurs / prohibition settled / band-aid is new
    _write(td / "s2.jsonl", [_turn("2026-04-01", "다음 작업"),        # kickoff (excluded)
                             _turn("2026-04-02", "아닌데 잘못됐어"),     # correction (recurs)
                             _turn("2026-04-03", "미봉책이야 땜질")])    # band-aid (new)
    cc2 = mf.correction_counts(mf._scan(td, 0, mf.read_watermark())["hits"])
    entry2 = mf.write_checkpoint("2026-04-30", mf.read_watermark(), "cycle2", cc2)
    assert cc2 == {"correction": 1, "band-aid": 1}

    rec = entry2["recurrence"]
    assert rec["prev_patterns"] == 2          # cycle1: correction·prohibition
    assert rec["recurring"] == ["correction"]   # only correction recurs
    assert rec["rate"] == 0.5                  # 1/2

    # persisted JSON: watermark advanced + 2 history entries accumulated
    data = json.loads((tmp_path / "wm.json").read_text(encoding="utf-8"))
    assert data["last_review"] == "2026-04-30"
    assert len(data["history"]) == 2


def test_scan_returns_none_without_transcripts(tmp_path):
    assert mf._scan(tmp_path, 0, None) is None
