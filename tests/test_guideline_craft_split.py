"""Boundary contract for the craft/project voice split.

Craft deliberation-narrative detectors (project-agnostic English surface
forms) live in .claude/skills/guideline-writing/checks.py; only patterns
tied to this wiki's vocabulary stay in tools/_lint/meta_schema.py
(PROJECT_VOICE_PATTERNS). This test pins the split so a future move is a
deliberate edit here, not silent drift, and asserts detection behavior on
representative English samples.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools" / "_lint"))

import meta_schema  # noqa: E402

gdl = meta_schema._load_gdl_checks()

CRAFT_LABELS = {
    "decision option name",
    "reinforcement counter",
    "introduction timestamp",
    "changelog section header",
    "recurrence prevention narrative",
}
PROJECT_LABELS = {
    "external case reference",
    "benchmark absorption narrative",
    "trail curriculum misframe",
}

# (text, expected craft label) — each craft detector must fire.
POSITIVES = [
    ("Adopt Option E+ for the gate ordering", "decision option name"),
    ("Reinforcement 2 tightened the threshold", "reinforcement counter"),
    ("(adopted 2026-05-10) after the pilot", "introduction timestamp"),
    ("2026-05-10 introduced with the desk gate", "introduction timestamp"),
    ("## Changelog", "changelog section header"),
    ("### Revision History", "changelog section header"),
    ("this rule prevents a recurrence of the earlier case",
     "recurrence prevention narrative"),
]

# Benign guideline prose that must NOT fire (FP guards).
NEGATIVES = [
    "explicitly choose one of (a)/(b)/(c) below, then retry",
    "several options exist; pick the cheapest rung",
    "structural prevention: a byproduct flow skips the stub gate",
    "the report is due 2026-05-10 at the latest",
    "log entries are appended at the bottom",
    "Change the wording, not the tier",
]


def _findings(text):
    lines = list(enumerate(text.splitlines(), 1))
    return gdl.find_deliberation_narrative(lines)


def test_skill_checks_load():
    assert gdl is not None, "guideline-writing/checks.py must ship with the repo"


def test_craft_label_set_pinned():
    assert {label for label, _ in gdl.DELIBERATION_PATTERNS} == CRAFT_LABELS


def test_project_label_set_pinned():
    assert {label for label, _ in meta_schema.PROJECT_VOICE_PATTERNS} == PROJECT_LABELS


def test_craft_positives_fire():
    for text, expected in POSITIVES:
        found = _findings(text)
        assert found and found[0][1] == expected, (text, found)


def test_craft_negatives_do_not_fire():
    for text in NEGATIVES:
        assert _findings(text) == [], text


def test_no_craft_pattern_left_in_project_set():
    # A craft-positive sample must not be caught by any project pattern —
    # the split is exclusive, not overlapping.
    for text, _ in POSITIVES:
        for label, pat in meta_schema.PROJECT_VOICE_PATTERNS:
            assert not pat.search(text), (label, text)


def test_evaluate_counts_violations():
    lines = list(enumerate(["ok line", "## Changelog", "Reinforcement 3"], 1))
    assert gdl.evaluate_deliberation_narrative(lines) == 2


# --- criteria.json ↔ checks.py schema contract ---

def test_criteria_schema_contract():
    crit = json.loads(
        (REPO / ".claude" / "skills" / "guideline-writing" / "criteria.json")
        .read_text(encoding="utf-8"))["criteria"]
    assert all(cid.startswith("gdl.") for cid in crit)
    for cid, cdef in crit.items():
        if cdef["judge"] == "A":
            assert "comparator" in cdef and "default_threshold" in cdef, cid
            assert hasattr(gdl, cdef["algorithm"]), cid
        else:
            assert cdef["judge"] == "M" and "pass_condition" in cdef, cid
