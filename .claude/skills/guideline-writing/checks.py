"""Deterministic detectors for the guideline-writing craft (gdl.*).

Caller-injection contract: functions take the target text (and any shared
parsing) as arguments and touch no disk/global state — the orchestrator
(tools/_lint/meta_schema.py voice pass) globs the guideline SoTs, reads
them, and injects each text here. Project-specific voice patterns
(external-precedent names, benchmark tallies, trail-frame vocabulary)
stay in the orchestrator; this module carries only the project-agnostic
deliberation-narrative surface forms.
"""
import re

# Craft deliberation-narrative patterns — English surface forms.
# (label, compiled regex); one label per finding, first match per line wins.
DELIBERATION_PATTERNS = [
    # "Option E+" / "option B adopted" — decision-alternative names surviving
    # into the body. Capitalized Option + single letter keeps prose like
    # "an option (a)/(b)/(c)" and "several options" out.
    ("decision option name", re.compile(r"\bOption\s+[A-Z]\+?\b")),
    # "Reinforcement 2" — iteration counters from strengthening rounds.
    ("reinforcement counter", re.compile(r"\breinforcement\s*\d+\b", re.IGNORECASE)),
    # "(adopted 2026-05-10)" / "2026-05-10 introduced" — adoption timestamps,
    # either order around an ISO date.
    ("introduction timestamp", re.compile(
        r"\b(?:adopted|introduced|effective)\s*[:\s(]*\d{4}-\d{2}-\d{2}"
        r"|\d{4}-\d{2}-\d{2}\s*(?:adopted|introduced|effective)\b",
        re.IGNORECASE,
    )),
    # An explicit history section inside a guideline (history's SoT is log.md).
    ("changelog section header", re.compile(
        r"^#{2,4}\s*(?:Changelog|Change\s*Log|Change\s*History|Revision\s*History)\s*$",
        re.IGNORECASE | re.MULTILINE,
    )),
    # "prevents a recurrence of the earlier case" — incident war stories.
    # Requires the word "recurrence" so a one-line failure-mode statement
    # ("structural prevention: X") stays legal.
    ("recurrence prevention narrative", re.compile(
        r"\brecurrence[- ]prevention\b|\bprevent(?:s|ing|ed)?\s+(?:a\s+|the\s+)?recurrence\b",
        re.IGNORECASE,
    )),
]


def find_deliberation_narrative(lines) -> list[tuple[int, str, str]]:
    """Scan (line_no, line) pairs → [(line_no, label, matched_text)].

    The caller supplies the line iterator (typically fence-stripped) so this
    module stays free of markdown parsing.
    """
    findings = []
    for i, line in lines:
        for label, pat in DELIBERATION_PATTERNS:
            m = pat.search(line)
            if m:
                findings.append((i, label, m.group(0).strip()))
                break
    return findings


def evaluate_deliberation_narrative(lines) -> int:
    """gdl.no-deliberation-narrative (judge A): violation count, pass <= 0."""
    return len(find_deliberation_narrative(lines))
