"""L2-2 hub body Self-meta voice lint — entities / concepts.

The .claude/layers/hub.md "full hub authoring cautions" section specifies that
editorial editing-decision utterances (`본 hub는 ~로 둔다`·`별도 정리한다`·
`여기서는 ~만 유지한다`, etc.) must not be exposed in the body. This module
handles the same guide's automatic regex detection, surfacing the hub-authoring
cycle's sub-trigger at the lint level.

Scope: `wiki/entities/*.md` + `wiki/concepts/*.md` body (content after stripping
frontmatter). `_`-prefixed meta files are out of scope.

`--fix` not supported — deleting a justification utterance or absorbing source
attribution into a body verb is a semantic decision that requires human handling
(columnist ADAPT).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import WIKI, korean_mode, read_text_cached  # noqa: E402
sys.path.insert(0, str(Path(__file__).parent))
from _hub_common import body_text, iter_hub_files  # noqa: E402

ENTITIES_DIR = WIKI / "entities"
CONCEPTS_DIR = WIKI / "concepts"

HUB_SPECS = [
    (ENTITIES_DIR, "entities"),
    (CONCEPTS_DIR, "concepts"),
]


# Self-meta voice antipatterns. The patterns mirror the explicit expressions in
# the hub.md "Self-meta voice ban" reinforcement bullets + accumulated B1 batch 1
# cleanup detections — promoted to lint after a case of 6 critical residuals in
# the 신한은행 hub (2026-05-15). Editor decision narrative ("본 hub는 X로 둔다"·
# "별도 정리한다") muddles the wiki voice with editorial justification; the rule
# deletes the sentence or absorbs source attribution into a body verb instead.
VOICE_PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    (
        "self-hub-reference",
        re.compile(r"본\s*hub[는의]"),
        "본 hub는/본 hub의 — editor self-reference",
    ),
    (
        "self-page-reference",
        re.compile(r"본\s*페이지[는의]"),
        "본 페이지는/본 페이지의 — editor self-reference",
    ),
    (
        "separate-curation",
        re.compile(r"별도\s*정리한다"),
        "별도 정리한다 — distribution meta-statement",
    ),
    (
        "here-only-retention",
        re.compile(r"여기서는[^.\n]+만\s+유지한다"),
        "여기서는 ~만 유지한다 — distribution meta-statement",
    ),
]


def _check_body(content: str, path: Path, dir_label: str) -> list[str]:
    """Scan body for self-meta voice antipatterns. Frontmatter and HTML
    comments are stripped because policy declarations live in those zones
    (hub.md acknowledges HTML comment as declaration ≠ body prose)."""
    issues: list[str] = []
    # The antipatterns are Korean-grammar self-meta utterances; they never match
    # an English body. Gate on korean_mode() so the intent is explicit and the
    # scan is skipped entirely for an English corpus.
    if not korean_mode():
        return issues
    # Frontmatter + HTML comments stripped (policy-meta zones, not body prose —
    # abbreviation declarations there must not false-positive on "본 hub").
    body = body_text(content)

    # Skip fenced code blocks so a code example illustrating an antipattern
    # (or a quoted command) cannot raise a FAIL on non-prose content. Toggle
    # in place rather than stripping so reported `:{idx}:` line numbers stay
    # aligned with the source file.
    lines = body.splitlines()
    in_fence = False
    for idx, line in enumerate(lines, start=1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for slug, pattern, label in VOICE_PATTERNS:
            for m in pattern.finditer(line):
                issues.append(
                    f"  {dir_label}/{path.name}:{idx}: {label} "
                    f"— matched `{m.group(0)}` (.claude/layers/hub.md "
                    f"\"Self-meta voice ban\")"
                )
    return issues


def _check_directory(directory: Path, dir_label: str) -> list[str]:
    issues: list[str] = []
    if not directory.exists():
        return issues
    for path in iter_hub_files(directory):
        content = read_text_cached(path)
        issues.extend(_check_body(content, path, dir_label))
    return issues


def run(fix: bool = False) -> int:
    """Entry point for `python tools/lint.py hub voice`.

    `fix` argument is accepted for signature parity with other hub
    sub-commands but ignored — self-meta voice resolution requires semantic
    judgment (sentence deletion vs source attribution absorption) handled
    by the columnist ADAPT cycle, not mechanical replacement.
    """
    del fix  # signature parity only; not actionable here.

    all_issues: list[str] = []
    total_files = 0
    for directory, dir_label in HUB_SPECS:
        if directory.exists():
            total_files += len(iter_hub_files(directory))
        all_issues.extend(_check_directory(directory, dir_label))

    if all_issues:
        print(
            f"\n[hub voice: {len(all_issues)} issue(s) across "
            f"{total_files} L2-2 entity+concept file(s)]"
        )
        for i in all_issues:
            print(i)
        print(
            "\nFAIL — L2-2 hub self-meta voice violations "
            "(.claude/layers/hub.md \"Self-meta voice ban\")."
        )
        print(
            "       Delete the sentence or absorb source attribution into a "
            "body verb (e.g. forecasts / recommends). `--fix` not provided — semantic "
            "judgment required."
        )
        return 1

    print(
        f"OK - L2-2 hub voice: self-meta antipatterns 0 "
        f"({total_files} entity+concept files)"
    )
    return 0


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true")
    args = ap.parse_args()
    sys.exit(run(fix=args.fix))
