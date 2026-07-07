"""journalism-writing craft skill — deterministic checks.

Craft drawn from the journalism / argumentation tradition (reporting·explainer·
inverted pyramid·Toulmin·Hegelian dialectic·fairness). It owns the contradiction
theme jrn.* measurements (legacy T4·D1·D5·D6 — Toulmin qualifier·Hegelian dialectic
structure). Many criteria (J1 Lede·J2 Nut graph, etc.) are judge=M (qualitative), so
only the SKILL.md / criteria.json definitions live here and desk reviews them.

content-type-agnostic: the shared section (conflict_section) is extracted and
injected by the orchestrator. The measurement logic was ported verbatim from
contradiction.py `_rubric_metrics` (diff-0).
"""

from __future__ import annotations

import re


# ── dialectic/Toulmin measurement regexes (verbatim from contradiction.py) ──
# Toulmin qualifier phrasings (T4). English-native forms first; the Korean forms
# fire under WIKI_LANG=ko.
QUALIFIER_PATTERNS = [
    re.compile(r"in the short[- ]term", re.IGNORECASE),
    re.compile(r"on this metric", re.IGNORECASE),
    re.compile(r"within \d+ years?", re.IGNORECASE),
    re.compile(r"\bthis (?:study|sample|design|experiment)\b", re.IGNORECASE),
    re.compile(r"as of \d{4}", re.IGNORECASE),
    re.compile(r"\bcurrently\b", re.IGNORECASE),
    re.compile(r"over the (?:medium|long)[- ]term", re.IGNORECASE),
    re.compile(r"단기적(으로|인)"),
    re.compile(r"이\s*지표(에서|로)"),
    re.compile(r"\d+년\s*(내|이내)"),
    re.compile(r"(이|그|해당)\s*(연구|설계|표본|실험)"),
    re.compile(r"(보고된|한정된|특정)\s*표본"),
    re.compile(r"\d{4}년\s*현재"),
    re.compile(r"현재\s*기준"),
    re.compile(r"중장기"),
]
# Hegelian dialectic A/B/C position label (D1/D5). The letter is captured in `p`
# when it follows `Position ` (English `**Position A**`, per contradiction.md) or
# in `b` when it leads (`**C — Mediation**`, Korean `**A 입장**`). The strict
# alternation mirrors contradiction.py's DIALECTIC_LABEL_RE so ordinary bold
# phrases starting with a bare A/B/C (`**A key caveat**`) are not matched.
DIALECTIC_LABEL_RE = re.compile(
    r"\*\*(?:Position\s+(?P<p>[ABC])\b|(?P<b>[ABC])\s*(?:[—-]|입장|중재|제3관점))[^*]*\*\*"
)
C_LABEL_BROAD_RE = re.compile(r"\*\*C\s+[^*]+\*\*")  # language-agnostic (any **C …** label)
# C-position meta-critique keywords (D6). English-native literals first; the Korean
# forms fire under WIKI_LANG=ko.
C_META_KEYWORDS = [
    "internal contradiction", "meta-critique", "meta-criticism", "self-serving",
    "interest bias", "both sides at once", "both camps", "fully neutral observer",
    "내부 모순", "메타 비판", "메타 비평", "셀프 서빙",
    "이해관계 편향", "양측 동시", "양쪽 모두", "완전 중립 관찰자",
    "모두 self", "둘 다 self",
]


def _count_words(text: str) -> int:
    """Whitespace-delimited word count (D5). Verbatim from contradiction.py."""
    return len([t for t in text.split() if t.strip()])


def _dialectic_paragraph_words(conflict_section: str) -> dict:
    """Per-paragraph A/B/C word counts in `## Opposing Positions`. Verbatim from
    contradiction.py."""
    out = {"A": 0, "B": 0, "C": 0}
    label_iter = list(DIALECTIC_LABEL_RE.finditer(conflict_section))
    for i, match in enumerate(label_iter):
        label = match.group("p") or match.group("b")
        start = match.end()
        end = label_iter[i + 1].start() if i + 1 < len(label_iter) else len(conflict_section)
        body = conflict_section[start:end]
        if out[label] == 0:
            out[label] = _count_words(body)
    return out


def evaluate_contradiction_dialectic(body: str, *, conflict_section: str) -> dict:
    """Measure contradiction theme jrn.* (T4 Toulmin qualifier·D1·D5·D6 Hegelian
    dialectic). conflict_section is orchestrator-injected. The returned dict is
    byte-identical to the corresponding _rubric_metrics keys (verbatim port)."""
    # T4 — qualifier tokens across the body
    qualifiers = sum(len(p.findall(body)) for p in QUALIFIER_PATTERNS)

    # D1 — number of distinct dialectic label kinds
    labels = len({
        m.group("p") or m.group("b") for m in DIALECTIC_LABEL_RE.finditer(conflict_section)
    })

    # D5 — A/B/C paragraph word counts
    paragraph_words = _dialectic_paragraph_words(conflict_section)
    a_w, b_w, c_w = paragraph_words["A"], paragraph_words["B"], paragraph_words["C"]

    # D6 — C-stance meta-critique keywords
    c_meta_hits: list = []
    c_matches = list(C_LABEL_BROAD_RE.finditer(conflict_section))
    if c_matches:
        c_start = c_matches[0].start()
        remainder = conflict_section[c_matches[0].end():]
        next_bullet = re.search(r"\n\s*-\s+", remainder)
        c_end = (
            c_matches[0].end() + next_bullet.start()
            if next_bullet else len(conflict_section)
        )
        c_region = conflict_section[c_start:c_end]
        for kw in C_META_KEYWORDS:
            if kw in c_region:
                c_meta_hits.append(kw)
    c_meta_count = len(c_meta_hits)

    return {
        "T4_qualifiers": qualifiers,
        "D1_labels": labels,
        "D5_words": {"A": a_w, "B": b_w, "C": c_w},
        "D6_c_meta_count": c_meta_count,
        "D6_c_meta_hits": c_meta_hits,
    }


def evaluate_contradiction_aggregate(*, insights_section: str) -> dict:
    """Measure contradiction aggregate jrn.* (T4 — `## Implications` qualifier).
    insights_section is orchestrator-injected. Ported verbatim from contradiction.py."""
    t4_qualifiers = sum(len(p.findall(insights_section)) for p in QUALIFIER_PATTERNS)
    return {"t4_qualifiers": t4_qualifiers}


def evaluate_overview_aggregate(*, all_links: list, cluster_slugs: set) -> dict:
    """Measure overview L2-4 D3 (cross-cluster reference balance — due impartiality).
    all_links·cluster_slugs are orchestrator-injected. Ported verbatim from
    overview.py. (Counts slug references — language-agnostic.)"""
    cluster_ref_counts: dict = {}
    for target in all_links:
        stem = target.strip().split("/")[-1]
        if stem in cluster_slugs:
            cluster_ref_counts[stem] = cluster_ref_counts.get(stem, 0) + 1
    if len(cluster_ref_counts) >= 2:
        max_refs = max(cluster_ref_counts.values())
        min_refs = min(cluster_ref_counts.values())
        d3_ratio = max_refs / min_refs if min_refs > 0 else float("inf")
    else:
        max_refs = sum(cluster_ref_counts.values())
        min_refs = max_refs if cluster_ref_counts else 0
        d3_ratio = 1.0 if cluster_ref_counts else 0.0
    return {"max_refs": max_refs, "min_refs": min_refs, "d3_ratio": d3_ratio}
