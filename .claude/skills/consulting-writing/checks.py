"""consulting-writing craft skill — deterministic checks.

Craft drawn from the management-consulting deliverable tradition (McKinsey SCR·
Minto Pyramid/MECE·BCG bold-bullet·"So what upfront"·Forrester Landscape). It owns
the MECE (Collectively Exhaustive) measurements of an aggregate roll-up —
overview L2-4 cluster completeness and contradiction-aggregate tension-axis
grouping. Many criteria (C1 SCR·C2 bold-bullet·C3 So-what·S2 numeric precision,
etc.) are judge=M (qualitative), so only the SKILL.md /
criteria.json definitions live here and desk reviews them.

content-type-agnostic: shared parsing (analysis_section·content·cluster_slugs) is
orchestrator-injected. The measurement logic was ported verbatim from lint
(_check_*_md).
"""

from __future__ import annotations

import re


# MECE measurement regexes (verbatim from lint) — language-agnostic structure
# (### headings, ## N. [[slug]] section markers).
AXIS_SUBSECTION_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
CLUSTER_SECTION_RE = re.compile(
    r"^##\s+\d+\.\s+\[\[([a-z][a-z0-9\-]+)(?:\|[^\]]*)?\]\]", re.MULTILINE
)
AXES_MIN = 2
AXES_MAX = 4


# ── con.numeric-density (BCG number isolation) — ported verbatim from overview.py ──
# When one paragraph is overpacked with number tokens, the key numbers get buried
# (BCG: isolate them in bold-bullets). Date fragments and wikilink targets are
# editorially meaningless numbers, so they are masked first. Threshold is
# manifest-injected.
_DENSITY_DATE_YMD_RE = re.compile(r"\b\d{4}(?:[-./]\d{1,2}(?:[-./]\d{1,2})?)?\b")
# (dormant: matched Korean date suffixes 년/월/일; an English wiki uses numeric or
#  ISO dates, already covered by _DENSITY_DATE_YMD_RE above. See FLAG in summary.)
_DENSITY_DATE_KO_RE = re.compile(r"\d{4}\s*년(?:\s*\d{1,2}\s*월(?:\s*\d{1,2}\s*일)?)?")
# Number+unit token for paragraph figure density. English-native units/magnitudes
# first; the Korean counters fire under WIKI_LANG=ko.
_DENSITY_NUM_UNIT_RE = re.compile(
    r"\d+(?:[,.]\d+)*\s*(?:%|percent|billion|million|trillion|"
    r"GB|TB|PB|GW|MW|km|kg|ppm|hours?|cases?|people|users|points?|"
    r"조|억|천만|백만|만|건|대|명|장|배|개월|개|호|층|년|번째|주|시간|분)"
)


def count_density_violations(content: str, *, max_per_para: int = 5) -> list:
    """con.numeric-density — list of (paragraph index, count) for paragraphs whose
    number-token count > max_per_para.

    content is the EDITOR region extracted by the orchestrator. After masking dates
    and wikilinks, split into paragraphs on blank lines. The threshold VALUE is
    manifest-injected (content-type-agnostic)."""
    clean = _DENSITY_DATE_YMD_RE.sub(" ", content)
    clean = _DENSITY_DATE_KO_RE.sub(" ", clean)
    clean = re.sub(r"\[\[[^\]]+\]\]", " ", clean)
    paras = re.split(r"\n\s*\n", clean)
    violations = []
    for i, p in enumerate(paras):
        if not p.strip():
            continue
        count = len(_DENSITY_NUM_UNIT_RE.findall(p))
        if count > max_per_para:
            violations.append((i, count))
    return violations


def eval_contradiction_aggregate_mece(analysis_section: str) -> dict:
    """contradiction aggregate D1 — count of `### <axis>` subsections under
    `## Per-Theme Deep Analysis` (`### 기타`/other is excluded as the MECE
    residual). axes in the 2–4 range. axes_named is also returned because N7 (enc)
    reuses it. Ported verbatim from contradiction.py.

    (The residual axis is excluded from the count: English `Other` or, under
    WIKI_LANG=ko, `기타`.)"""
    axis_matches = AXIS_SUBSECTION_RE.findall(analysis_section)
    axes_named = [a for a in axis_matches if a.strip().lower() not in ("other", "기타")]
    d1_axes = len(axes_named)
    return {
        "d1_axes": d1_axes,
        "axes_named": axes_named,
        "d1_ok": AXES_MIN <= d1_axes <= AXES_MAX,
        "axes_min": AXES_MIN,
        "axes_max": AXES_MAX,
    }


def eval_overview_aggregate_mece(content: str, *, cluster_slugs: set) -> dict:
    """overview L2-4 D1 — every cluster appears as a `## N. [[slug|alias]]` section
    (MECE Collectively Exhaustive). The section matches are returned with their
    (slug, end-pos) info because D2 (enc drill-down) reuses them. Ported verbatim
    from overview.py."""
    section_spans = [
        (m.group(1), m.end()) for m in CLUSTER_SECTION_RE.finditer(content)
    ]
    sections_found = {slug for slug, _ in section_spans}
    d1_count = len(sections_found & cluster_slugs)
    d1_total = len(cluster_slugs)
    return {
        "d1_count": d1_count,
        "d1_total": d1_total,
        "d1_ok": d1_count == d1_total,
        "d1_missing": sorted(cluster_slugs - sections_found),
        "section_spans": section_spans,
        "section_count": len(section_spans),
    }
