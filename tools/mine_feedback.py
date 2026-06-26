"""Transcript pattern mining — surface this wiki's operator utterances split into three minibatches.

A companion tool to the SoT self-evolution workflow. Recommended once per quarter. Being a
prefilter, the final meaning judgment happens when the output is read — surfaced as three
minibatches:
- CORRECTION (corrections, prohibitions, band-aids, method changes, etc.): candidate latent feedback not yet encoded.
- OPERATION (extra requests, retries, omissions, etc.): normal cycle operation already absorbed by ADAPT/debugging — for monitoring.
- SUCCESS (approvals, confirmations): candidates for codifying a repeatedly-approved procedure into the SoT/skills.

The review cycle is bounded by a watermark — a run surfaces only utterances after the
watermark (the last review-complete date), and once you finish a review pass you stamp the
watermark to today with `--checkpoint`. The next run automatically targets only what came
after. A run alone does not advance the watermark (to prevent permanently dropping unreviewed
utterances) — the boundary is the step that explicitly marks review complete. The watermark
lives in `tools/_feedback-review.json` (committed to the repo — being a date, it is
machine-independent, so cloud and multiple machines share the same boundary). `--checkpoint`
accumulates the date + `--note` + this cycle's CORRECTION fingerprint into the history, and
computes the recurrence rate of already-treated patterns against the previous fingerprint
(lower recurrence = feedback settled — a human-gate signal for measured self-improvement). The
cycle is recorded in git.

Usage:
    python tools/mine_feedback.py               # only after the watermark (or all if none)
    python tools/mine_feedback.py --all         # ignore the watermark, re-review everything
    python tools/mine_feedback.py --since 2026-03-01   # one-off manual window
    python tools/mine_feedback.py --checkpoint  # review complete → confirm watermark=today
    python tools/mine_feedback.py --dir <d> --samples 3

Output: to stdout, the review window + per-pattern hit count + sample utterances. The operator
reads the result and decides whether to encode new feedback (Editor-in-Chief § SoT
self-evolution workflow trigger).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _review  # noqa: E402  # shares the review-cycle watermark skeleton (isomorphic to mine_failures)
from _lib import REPO_ROOT, korean_mode  # noqa: E402

# Default transcript dir is derived from the repo path (Claude Code encodes the
# project path as a `c--…` slug under ~/.claude/projects). Derive it so the path
# resolves on any machine; `--dir` overrides. The slug is the absolute repo path
# with drive-colon and separators replaced by `-` and lowercased drive letter.
def _default_transcript_dir() -> Path:
    slug = str(REPO_ROOT).replace(":", "-").replace("\\", "-").replace("/", "-")
    if slug and slug[0].isalpha():
        slug = slug[0].lower() + slug[1:]
    return Path.home() / ".claude" / "projects" / slug


DEFAULT_TRANSCRIPT_DIR = _default_transcript_dir()
# Review-cycle boundary — a repo-committed file (fixed relative to __file__, independent of transcript --dir).
# The watermark is a date, so it is machine-independent → keep it in git so cloud and multiple machines share the same boundary.
WATERMARK_PATH = Path(__file__).resolve().parent / "_feedback-review.json"


def read_watermark():
    """Return the last review-complete date (YYYY-MM-DD), or None if absent."""
    return _review.read_watermark(WATERMARK_PATH)


def write_checkpoint(when: str, since, note: str, cc: dict | None = None) -> dict:
    """Advance the review-complete boundary to today + append to the history (to be committed to the repo).

    When cc (this cycle's CORRECTION fingerprint) is provided, compute the recurrence rate of
    already-treated patterns against the previous fingerprint and record it in the history — the
    human-gate counterpart of Brain-style 'measured self-improvement' (lower recurrence = feedback
    settled). The recurrence rate is merely a surfaced result and is unrelated to advancing the watermark.
    """
    history = _review.load_history(WATERMARK_PATH)
    entry = {"checkpoint": when, "reviewed_since": since, "note": note}
    if cc is not None:
        entry["correction_counts"] = cc
        entry["correction_total"] = sum(cc.values())
        prev = next((h for h in reversed(history) if h.get("correction_counts")), None)
        if prev:
            prev_pats = set(prev["correction_counts"])
            recurring = sorted(prev_pats & set(cc))
            entry["recurrence"] = {
                "prev_patterns": len(prev_pats),
                "recurring_patterns": len(recurring),
                "rate": round(len(recurring) / len(prev_pats), 2) if prev_pats else None,
                "recurring": recurring,
            }
    history.append(entry)
    _review.write_review(WATERMARK_PATH, when, history)
    return entry

META_PREFIXES = (
    "<ide_opened_file>", "<ide_closed_file>", "<ide_selection>",
    "<local-command-stdout>", "<system-reminder>", "<command-name>",
    "<command-message>", "<command-args>", "Caveat:",
    "<teammate-message",  # agent-team relay — not an operator utterance
    "Stop hook feedback:",  # hook-injected system message — not an operator utterance
)
META_EXACT = {"Tool loaded.", "[Request interrupted by user]", ""}

# Three minibatches — (1) CORRECTION: behavior-correction signals → candidate new feedback to encode (2) OPERATION:
# normal cycle-operation utterances (extra requests, retries, etc.) → already absorbed by ADAPT/debugging, for monitoring (3) SUCCESS:
# approval signals → candidates for codifying a repeatedly-approved procedure. Broad tokens (그리고/또/다시/아니라/임시 etc.) have
# high false positives on neutral prose, so they are tightened with refinement and negative lookahead — this tool is a prefilter, so the final meaning judgment is at the reading stage.
# NOTE: the dict keys below and the regex bodies are matching-data against Korean transcripts (the keys are also
# cross-run join keys persisted in _feedback-review.json) — left untranslated on purpose.
CORRECTION_PATTERNS = {
    "prohibition": re.compile(r"(하지\s*마|그만\s*해|안\s*돼|금지|쓰지\s*마|넣지\s*마)"),
    "correction": re.compile(r"(그게\s*아니|아니야|아닌데|틀려|틀렸|잘못|오류|실수)"),
    "방식 변경": re.compile(r"(그렇게\s*말고|이렇게\s*말고|말고\s*[^없])"),
    "band-aid": re.compile(r"(미봉|땜질|편법|임시방편|임시(?!\s*(폴더|디렉터리|디렉토리|파일|경로|디스크|저장)))"),
    "예시 천착 신호": re.compile(r"(예시.{0,10}(말고|말것|아니|천착)|에\s*매몰|예시.{0,5}그대로)"),
    "외부 벤치 거부": re.compile(r"(채택\s*안|도입\s*안|이미\s*더\s*잘|더\s*잘\s*구현|벤치마크.{0,12}(거부|불필요|채택\s*안))"),
    "반말 (호칭 누락 가능)": re.compile(r"^(해|해라|줘|만들어|넣어|빼|지워)\s*$"),
    "[en] no/actually": re.compile(r"\b(no,? actually|wait,? no|instead)\b", re.I),
    "[en] don't/stop": re.compile(r"\b(don'?t|stop|never)\s+\w", re.I),
}
OPERATION_PATTERNS = {
    "추가 요구": re.compile(r"(덧붙여|덧붙이|추가로|보강하|보완해)"),
    "재시도": re.compile(r"(재작성|재실행|재시도|다시\s*(해|작성|실행|지시|검토|확인))"),
    "누락 지적": re.compile(r"(빠졌|누락|왜.{0,15}안\s*[했넣]|안\s*나옴|안\s*보임|없어졌|없잖)"),
    "확인 요구": re.compile(r"(확인했\?|체크했\?|봤어\?|검토했\?|읽었\?)"),
    "왜 질문": re.compile(r"(왜\s+(그|그렇|이렇|안)|왜.{0,10}\?)"),
    "[en] can you also": re.compile(r"can you (also|then|please)", re.I),
}
SUCCESS_PATTERNS = {
    "승인·확정": re.compile(r"(좋아|좋습니다|좋네|맞아|맞습니다|맞네|그대로|완벽|정확해|훌륭|바로\s*그|이대로)"),
    "진행·발행 지시": re.compile(r"(진행해|그렇게\s*해|커밋해|커밋하|발행해|배포해|채택해|채택하)"),
    "[en] looks good": re.compile(r"\b(lgtm|looks good|perfect|exactly|great)\b", re.I),
}
PATTERNS = {**CORRECTION_PATTERNS, **OPERATION_PATTERNS, **SUCCESS_PATTERNS}


def _active_patterns() -> dict:
    """Patterns to match against transcripts. The `[en]` patterns are always on;
    the Korean-keyed patterns fire only under WIKI_LANG=ko (they never match an
    English transcript, so gating just skips dead work for an English corpus).
    Read live so tests/per-run config can toggle it."""
    if korean_mode():
        return PATTERNS
    return {k: v for k, v in PATTERNS.items() if k.startswith("[en]")}

META_TAG_RE = re.compile(r"<(system-reminder|ide_[a-z_]+|command-(?:name|message|args)|local-command-stdout)>.*?</\1>", re.S)


def extract_user_text(d):
    """Extract only genuine user utterances. Exclude tool results, ide, system-reminder, and command bodies."""
    if d.get("type") != "user":
        return None
    if "toolUseResult" in d:
        return None
    msg = d.get("message", {})
    content = msg.get("content")
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        parts = [p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"]
        text = "\n".join(parts)
    else:
        return None
    text = text.strip()
    if text in META_EXACT:
        return None
    if any(text.startswith(pref) for pref in META_PREFIXES):
        return None
    text = META_TAG_RE.sub("", text).strip()
    if not text or len(text) < 2:
        return None
    first_line = text.split("\n", 1)[0]
    if first_line.startswith(("---", "#", "|", "```")):
        return None
    if "<task-notification>" in text or "<task-id>" in text:
        return None
    if len(text) > 800:
        return None
    return text


def _scan(transcript_dir: Path, samples_per_pattern: int, since: str | None):
    """Scan utterances in the review window (after `since`) and tally pattern hits/samples. None if no files.

    Shared by mine() (output) and checkpoint (recurrence-rate fingerprint) — the single SoT for window decisions.
    """
    files = sorted(transcript_dir.glob("*.jsonl"))
    if not files:
        return None
    total_user_turns = 0
    hit_counter: Counter = Counter()
    samples = defaultdict(list)
    session_dates = []
    for fp in files:
        kickoff_seen = False
        try:
            with fp.open(encoding="utf-8") as f:
                for line in f:
                    try:
                        d = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    text = extract_user_text(d)
                    if text is None:
                        continue
                    ts = (d.get("timestamp") or "")[:10]
                    is_kickoff = not kickoff_seen  # the session's actual first utterance (decided before the window filter)
                    kickoff_seen = True
                    if since and ts and ts <= since:
                        continue  # before the watermark — an already-reviewed period
                    total_user_turns += 1
                    if ts:
                        session_dates.append(ts)
                    if is_kickoff:
                        continue  # a task-kickoff instruction (not a reaction), excluded from feedback
                    for name, pat in _active_patterns().items():
                        if pat.search(text):
                            hit_counter[name] += 1
                            if len(samples[name]) < samples_per_pattern:
                                samples[name].append((ts, text[:200].replace("\n", " / ")))
        except OSError as e:
            print(f"err {fp.name}: {e}", file=sys.stderr)
    return {"files": len(files), "turns": total_user_turns,
            "hits": hit_counter, "samples": samples, "dates": session_dates}


def correction_counts(hits: Counter) -> dict:
    """This window's per-CORRECTION-pattern hits (excluding 0) — the cycle fingerprint."""
    return {n: hits[n] for n in CORRECTION_PATTERNS if hits[n]}


def mine(transcript_dir: Path, samples_per_pattern: int = 5, since: str | None = None) -> int:
    scan = _scan(transcript_dir, samples_per_pattern, since)
    if scan is None:
        print(f"no transcripts in {transcript_dir}", file=sys.stderr)
        print("(the default path is the operator's local machine only — on other machines "
              "specify --dir <transcript-dir>)", file=sys.stderr)
        return 1
    total_user_turns = scan["turns"]
    hit_counter = scan["hits"]
    samples = scan["samples"]
    session_dates = scan["dates"]
    print(f"transcript files: {scan['files']}")
    print(f"review window: {('after ' + since) if since else 'ALL (no watermark)'}")
    print(f"total user turns (cleaned): {total_user_turns}")
    if session_dates:
        print(f"date range: {min(session_dates)} ~ {max(session_dates)}")
    print()
    for label, group in (
        ("CORRECTION (candidate new feedback to encode)", CORRECTION_PATTERNS),
        ("OPERATION (normal cycle operation — absorbed by ADAPT/debugging, monitor)", OPERATION_PATTERNS),
        ("SUCCESS (candidate reusable procedure to codify)", SUCCESS_PATTERNS),
    ):
        ranked = sorted(((hit_counter[n], n) for n in group), reverse=True)
        subtotal = sum(c for c, _ in ranked)
        print(f"=== {label} — hits {subtotal} ===")
        for cnt, name in ranked:
            print(f"  {cnt:5d}  {name}")
        print()
    print(f"=== Samples (up to {samples_per_pattern} per pattern) ===")
    for name, _ in hit_counter.most_common():
        print(f"\n--- {name} ({hit_counter[name]}) ---")
        for ts, t in samples[name]:
            print(f"  [{ts}] {t}")
    print(f"\n[watermark] after CORRECTION review is complete: "
          f"python tools/mine_feedback.py --checkpoint  (only later utterances target the next cycle)")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--dir", type=Path, default=DEFAULT_TRANSCRIPT_DIR,
                   help="Claude Code transcript .jsonl directory")
    p.add_argument("--samples", type=int, default=5, help="number of samples to print per pattern")
    p.add_argument("--since", default=None,
                   help="only utterances after this date (YYYY-MM-DD) — one-off manual window (ignores the watermark)")
    p.add_argument("--all", action="store_true", help="ignore the watermark and re-review everything")
    p.add_argument("--checkpoint", nargs="?", const="", default=None,
                   help="confirm review complete — advance the watermark to today (or a given YYYY-MM-DD), no mining")
    p.add_argument("--note", default="", help="one-line review note to record in the history on --checkpoint")
    args = p.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if args.checkpoint is not None:
        when = args.checkpoint or date.today().isoformat()
        prev_watermark = read_watermark()
        # the CORRECTION fingerprint of the previous review window (after prev watermark) — for computing the recurrence rate
        scan = _scan(args.dir, 0, prev_watermark)
        cc = correction_counts(scan["hits"]) if scan else None
        entry = write_checkpoint(when, prev_watermark, args.note, cc)
        print(f"[watermark] review complete confirmed: {when} → {WATERMARK_PATH.name} (to be committed to the repo) — "
              f"the next run surfaces only after this date. needs git add then commit.")
        if cc is not None:
            print(f"[self-improvement] this cycle's CORRECTION total {sum(cc.values())} / "
                  f"{len(cc)} pattern(s)")
        rec = entry.get("recurrence")
        if rec:
            print(f"[self-improvement] recurrence rate of already-treated CORRECTION patterns: "
                  f"{rec['recurring_patterns']}/{rec['prev_patterns']} = {rec['rate']} "
                  f"(lower = more settled) — recurring: {', '.join(rec['recurring']) or 'none'}")
        raise SystemExit(0)
    if args.all:
        since = None
    elif args.since:
        since = args.since
    else:
        since = read_watermark()
    raise SystemExit(mine(args.dir, args.samples, since))


if __name__ == "__main__":
    main()
