"""encyclopedia-writing craft skill — deterministic checks.

The "full modularization" pattern that combines the probabilistic part
(SKILL.md craft prose) and the deterministic part (this module) in a single skill
folder. It reads criteria.json as the single SoT and provides craft-agnostic
measurement algorithms. The threshold VALUE is injected from the manifest by the
caller (the content-type orchestrator = tools/lint.py) — the skill does not know
the content type.

Owns the enc.* criteria bundles across four content types, each injected per
_manifest.json bundles: wikilink craft (enc.link-density · enc.first-mention ·
enc.slug-alias · enc.abbr-gloss), NPOV (enc.verdict-restraint), the
contradiction-theme NPOV bundle (W1·N4·N5·N6·N7·L1·X2), the
contradiction-aggregate (N5·N7·D2·D3·F1) and overview-aggregate (D2·F1)
bundles, and the L2-2 hub body/connection grouping.
"""

from __future__ import annotations

import re


# craft structural regexes — owned by the skill (content-type-agnostic).
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]")
AUTO_BLOCK_RE = re.compile(
    r"<!--\s*AUTO:\w+\s*BEGIN\s*-->.*?<!--\s*AUTO:\w+\s*END\s*-->",
    re.DOTALL,
)


# ── encyclopedic-notation craft (verdict restraint·slug alias·abbr gloss) — ported verbatim from overview.py ──
# External craft sources: NPOV (verdict restraint)·MoS (slug alias·abbreviation
# first-mention gloss). All act directly on the EDITOR region text
# (content-type-agnostic·advisory).

# B1 — verdict sentences. NPOV: an editor does not assert their own conclusion.
# (dormant: matches Korean verb endings such as '합리적이다'/'부합한다'/'입증됐다';
#  it will NOT fire on English prose. An English equivalent would need to detect
#  verdict phrases like "is reasonable", "is consistent with", "has the most
#  explanatory power". See FLAG in summary.)
_VERDICT_RE = re.compile(
    r"(?:이|가)\s*(?:합리적이다|가장\s*설명력이\s*높다|부합한다|"
    r"확정됐다|실증됐다|확인됐다|정당화된다|입증됐다)"
    r"|에\s*부합한다"
)


def find_verdict_hits(content: str) -> list:
    """enc.verdict-restraint — list of verdict-phrase excerpts (each ≤60 chars). NPOV restraint."""
    hits = []
    for m in _VERDICT_RE.finditer(content):
        start = max(0, m.start() - 30)
        end = min(len(content), m.end() + 10)
        hits.append(re.sub(r"\s+", " ", content[start:end]).strip())
    return hits


def find_unaliased_slugs(content: str, *, min_len: int = 10) -> list:
    """enc.slug-alias — list of stems where a kebab-case slug of ≥min_len chars is
    exposed as a bare `[[slug]]` (no alias). MoS: avoid raw slug exposure, prefer a
    human-readable alias. Threshold manifest-injected."""
    violations: list = []
    for m in re.finditer(r"\[\[([^\]]+)\]\]", content):
        raw = m.group(1).strip()
        if "|" in raw:
            continue
        stem = raw.split("/")[-1]
        if len(stem) >= min_len and "-" in stem and re.fullmatch(r"[a-z0-9\-]+", stem):
            violations.append(stem)
    return violations


# L3 — first-mention parenthetical gloss for English abbreviations. MoS: gloss an
# acronym on its first appearance. (Language-agnostic: uppercase acronyms occur in
# English prose too.)
_ABBR_RE = re.compile(r"(?<![A-Za-z])([A-Z][A-Z0-9]{1,4})(?![A-Za-z])")
_ABBR_ALLOWLIST = {
    "AI", "API", "GPU", "CPU", "RAM", "SSD", "HDD", "LLM", "ML", "DC",
    "IT", "AX", "DX", "CX", "ROI", "KPI", "RTO", "RPO", "DR", "BCP",
    "VPN", "SSL", "TLS", "URL", "HTTP", "HTTPS", "JSON", "YAML", "XML",
    "CSV", "PDF", "HTML", "CSS",
    "ESG", "IPO", "CEO", "CTO", "CIO", "CFO", "COO",
    "RAG", "NPU", "DPU",
    "OS", "OT", "EU", "UK", "US", "KR", "JP", "CN", "UAE",
    "HBM", "DDR", "TSMC",
    "USD", "EUR", "JPY", "KRW", "CBDC", "USDC", "USDT",
    "SDK", "IDE", "CLI", "GUI", "UI", "UX", "IAM",
    "MVP", "POC", "QA",
    "APT", "MFA", "ZTNA", "SASE", "SIEM", "SOC", "SOAR",
    "EDR", "NDR", "XDR", "EPP", "CNAPP", "CSPM", "CWPP", "CIEM",
    "PPA", "SMR",
}


def find_abbr_violations(content: str) -> list:
    """enc.abbr-gloss — list of English abbreviations whose first appearance lacks a
    parenthetical gloss (allowlist excluded)."""
    # Strip YAML frontmatter first — English tokens in the tags:/sources: arrays
    # (NLP·OCR·RPA, etc.) are metadata, not body abbreviations (in the body they
    # appear as [[wikilink]]s). Exclude the frontmatter from glossing (same pattern
    # as _s6_long_sentences, content-type-agnostic).
    if content.startswith("---"):
        fm_end = content.find("\n---", 4)
        if fm_end > 0:
            content = content[fm_end + 4:]
    clean = re.sub(r"\[\[[^\]]+\]\]", " ", content)
    clean = re.sub(r"```.*?```", "", clean, flags=re.DOTALL)
    clean = re.sub(r"`[^`]*`", "", clean)
    seen: dict = {}
    for m in _ABBR_RE.finditer(clean):
        abbr = m.group(1)
        if abbr in _ABBR_ALLOWLIST:
            continue
        if abbr not in seen:
            after = clean[m.end():m.end() + 2]
            if after.lstrip().startswith("("):
                seen[abbr] = 0
            else:
                seen[abbr] = 1
    return [a for a, v in seen.items() if v > 0]


def count_wikilinks_in_editor_region(content: str, *, strip_auto: bool = True) -> int:
    """enc.link-density algorithm — count of [[wikilink]] in the EDITOR region.

    Craft logic that unifies a measurement which previously lived in two places
    (the layers Rubric prose and an overview.py constant). strip_auto is a
    content-type param (L2-3=True excludes AUTO, L2-4=False raw) — manifest-injected.
    """
    editor = AUTO_BLOCK_RE.sub("", content) if strip_auto else content
    return len(WIKILINK_RE.findall(editor))


def _split_h2_sections(editor: str) -> dict[str, str]:
    """Split the EDITOR into sections by `## ` heading (text before the first
    heading is `_preamble`).

    1:1 identical to the section-split logic in overview.py `_link_metrics` — the
    basis for the equivalence guarantee.
    """
    sections: dict[str, str] = {}
    current = "_preamble"
    buffer: list[str] = []
    for line in editor.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m and not line.startswith("###"):
            if buffer:
                sections[current] = "\n".join(buffer)
            current = f"## {m.group(1).strip()}"
            buffer = []
        else:
            buffer.append(line)
    if buffer:
        sections[current] = "\n".join(buffer)
    return sections


def count_duplicate_links(
    content: str,
    *,
    exempt_sections=(),
    strip_auto: bool = True,
    unit: str = "h2",
    include_preamble: bool = True,
    exclude_patterns=(),
):
    """enc.first-mention algorithm — same-stem wikilink duplicates within a unit
    (n>1 → n-1 accumulated).

    Wikipedia MoS "first-mention principle / overlinking avoidance" craft.
    Content-type variants are absorbed via manifest params — exempt_sections·
    strip_auto·unit (h2|h3 duplication unit)·include_preamble (whether to include
    the lead before the first heading)·exclude_patterns (regex strings that strip
    structural repetition such as drill-down links). Returns:
    (dup_total, duplicates[(heading::stem, n)]). The duplicates list is filled only
    for unit=h2 (used for the report's top-dup line).
    """
    editor = AUTO_BLOCK_RE.sub("", content) if strip_auto else content
    exempt = set(exempt_sections)
    compiled = [re.compile(p, re.MULTILINE) if isinstance(p, str) else p for p in exclude_patterns]
    duplicates: list[tuple[str, int]] = []
    dup_total = 0
    for heading, body in _split_h2_sections(editor).items():
        if heading in exempt:
            continue
        if not include_preamble and heading == "_preamble":
            continue
        cleaned = body
        for pat in compiled:
            cleaned = pat.sub("", cleaned)
        parts = re.split(r"^###\s", cleaned, flags=re.MULTILINE) if unit == "h3" else [cleaned]
        for part in parts:
            counts: dict[str, int] = {}
            for target in WIKILINK_RE.findall(part):
                stem = target.strip().split("/")[-1]
                counts[stem] = counts.get(stem, 0) + 1
            for stem, n in counts.items():
                if n > 1:
                    if unit == "h2":
                        duplicates.append((f"{heading}::{stem}", n))
                    dup_total += n - 1
    return dup_total, duplicates


# ── contradiction theme enc.* (N4·N5·N6·N7 NPOV·W1 links·L1 alias·X2 back-ref) ──
# Ported verbatim from contradiction.py `_rubric_metrics`. Shared sections (conflict·
# verdict·derived)·source_slugs·cluster_slugs are orchestrator-injected. WIKILINK_RE reused.

# (dormant: every pattern below keys on Korean verdict verb endings; none will fire
#  on English prose. An English equivalent would need verdict phrases like
#  "is reasonable", "has the most explanatory power", "is consistent with", "leans
#  toward", "is appropriate", "clearly", "the only interpretation/answer". See FLAG.)
VERDICT_FAIL_PATTERNS = [
    re.compile(r"(이|가)\s*합리적이다"),
    re.compile(r"가장\s*설명력이\s*높다"),
    re.compile(r"에\s*부합한다"),
    re.compile(r"에\s*기운\s*상태"),
    re.compile(r"(이|가)\s*적절하다"),
    re.compile(r"명백히\s"),
    re.compile(r"(이|가)\s*[^.?!\n]{0,30}유일한\s*(해석|답|해결책)"),
]
# English-native first: %|percent + magnitude words (billion|million|trillion) +
# common counters (hours|people|users|cases|points|x|×) fire on the English corpus;
# the Korean units (조|억|만|퍼센트|달러|시간|배|명…) fire under WIKI_LANG=ko. Single
# SoT — `_lint/contradiction.py` consumes this exact regex (was a drifted second copy).
NUMBER_TOKEN_RE = re.compile(
    r"\d+(?:,\d{3})*(?:\.\d+)?\s*"
    r"(?:%|percent|"
    r"billion|million|trillion|"
    r"hours?|hrs?|people|users|cases?|points?|x|×|"
    r"조|억|만|천억|백만|퍼센트|"
    r"달러|위안|유로|파운드|엔|"
    r"시간|배|명|건|개|대|기|점|"
    r"GW|MW|TB|PB|GB|"
    r"ppm|kg|km)"
    r"(?:\s*원)?"
)
N6_MIN_TOKEN_LEN = 3
N6_NUMBER_REUSE_MAX = 2
# The English keyword "Timeline" is live on English derived-tensions prose; the six
# Korean transition keywords (before/after/generation/reversal/turning point/angle)
# fire under WIKI_LANG=ko.
N6_DERIVED_TRANSITION_KEYWORDS = ["이전", "이후", "세대", "반전", "전환점", "각도", "Timeline"]
# A/B/C position label (N7). The letter is captured in `p` when it follows
# `Position ` (English `**Position A**`, per contradiction.md) or in `b` when it
# leads (`**C — Mediation**`, Korean `**A 입장**`). The strict alternation mirrors
# contradiction.py's DIALECTIC_LABEL_RE so ordinary bold phrases starting with a
# bare A/B/C (`**A key caveat**`) are not matched.
DIALECTIC_LABEL_RE = re.compile(
    r"\*\*(?:Position\s+(?P<p>[ABC])\b|(?P<b>[ABC])\s*(?:[—-]|입장|중재|제3관점))[^*]*\*\*"
)
# Value-laden words used in a faction subtitle (N7 skew). English-native set first;
# the Korean set fires under WIKI_LANG=ko. Matched case-insensitively in _value_hits.
LABEL_VALUE_WORDS = {
    "myth", "empirical", "skepticism", "science", "heresy", "mainstream",
    "orthodoxy", "orthodox", "innovation", "optimism", "pessimism", "extreme",
    "fanaticism", "blind faith", "illusion", "bubble", "camp",
    "신화", "실증", "회의론", "과학", "이단", "주류", "정설",
    "혁신", "낙관", "비관", "극단", "광신", "맹신", "환상", "거품",
    "진영", "정통",
}
RAW_KEBAB_SLUG_RE = re.compile(r"\[\[([a-z][a-z0-9]*(?:-[a-z0-9]+){2,})(?:#[^|\]]+)?\]\]")
L1_MIN_SLUG_LEN = 10


def _slug_only(target: str) -> str:
    """Strip path and #anchor from a target. Verbatim from contradiction.py."""
    bare = target.strip().split("/")[-1]
    return bare.split("#", 1)[0]


def _split_sentences(text: str) -> list:
    """Coarse sentence split of body text (N5). Verbatim from contradiction.py.
    (Splits on .!?。 + newlines — language-agnostic, but feeds the dormant Korean
    VERDICT_FAIL_PATTERNS.)"""
    parts = re.split(r"(?<=[.!?。])\s+|\n+", text)
    return [p.strip() for p in parts if p.strip()]


def evaluate_contradiction_npov(
    body: str,
    *,
    conflict_section: str,
    verdict_section: str,
    derived_section: str,
    source_slugs: set,
    cluster_slugs: set,
) -> dict:
    """Measure contradiction theme enc.* (W1·N4·N5·N6·N7·L1·X2). Shared sections are
    orchestrator-injected. The returned dict is byte-identical to the corresponding
    _rubric_metrics keys."""
    # W1
    total_links = len(WIKILINK_RE.findall(body))

    # N4 — max re-appearance of a source-slug wikilink
    slug_counts: dict = {}
    for target in WIKILINK_RE.findall(body):
        stem = _slug_only(target)
        if source_slugs and stem not in source_slugs:
            continue
        slug_counts[stem] = slug_counts.get(stem, 0) + 1
    top_reused = sorted(slug_counts.items(), key=lambda x: -x[1])[:3]
    reuse_max = top_reused[0][1] if top_reused else 0

    # N5 — verdict sentences in `## Interpretive Direction` (Korean verdict matcher; ko-mode)
    verdict_fails = 0
    for sentence in _split_sentences(verdict_section):
        if any(p.search(sentence) for p in VERDICT_FAIL_PATTERNS):
            verdict_fails += 1

    # X2 — landscape back-reference
    landscape_refs = 0
    for target in WIKILINK_RE.findall(body):
        stem = _slug_only(target)
        if stem in cluster_slugs:
            landscape_refs += 1

    # L1 — raw kebab-case source slug (≥10 chars, no alias)
    raw_slug_matches = [m for m in RAW_KEBAB_SLUG_RE.findall(body) if len(m) >= L1_MIN_SLUG_LEN]
    raw_slugs = len(raw_slug_matches)

    # N6 — number-token re-appearance
    body_no_links = WIKILINK_RE.sub("", body)
    num_counts: dict = {}
    for tok in NUMBER_TOKEN_RE.findall(body_no_links):
        norm = tok.strip()
        if len(norm) < N6_MIN_TOKEN_LEN:
            continue
        norm = re.sub(r"\s+", " ", norm).strip()
        num_counts[norm] = num_counts.get(norm, 0) + 1
    top_num_reused = sorted(num_counts.items(), key=lambda x: -x[1])[:3]
    num_reuse_max = top_num_reused[0][1] if top_num_reused else 0

    derived_no_links = WIKILINK_RE.sub("", derived_section)
    derived_has_transition = any(kw in derived_no_links for kw in N6_DERIVED_TRANSITION_KEYWORDS)
    derived_reused_tokens: list = []
    for tok, n in top_num_reused:
        if n > N6_NUMBER_REUSE_MAX and tok in derived_no_links:
            derived_reused_tokens.append(tok)

    # N7 — value-word skew across the A·B labels (English-first LABEL_VALUE_WORDS; Korean set ko-mode)
    label_value_words: dict = {"A": [], "B": [], "C": []}
    for match in DIALECTIC_LABEL_RE.finditer(conflict_section):
        label = match.group("p") or match.group("b")
        full = match.group(0)
        paren = re.search(r"\(([^)]+)\)", full)
        subtitle = paren.group(1) if paren else ""
        hits = [w for w in LABEL_VALUE_WORDS if w in subtitle.lower()]
        if hits and not label_value_words[label]:
            label_value_words[label] = hits
    a_has = bool(label_value_words["A"])
    b_has = bool(label_value_words["B"])
    label_skew = 1 if (a_has != b_has) else 0

    return {
        "W1_total": total_links,
        "N4_reuse_max": reuse_max,
        "N4_top": top_reused,
        "N5_verdict_fails": verdict_fails,
        "N6_num_reuse_max": num_reuse_max,
        "N6_top": top_num_reused,
        "N6_derived_has_transition": derived_has_transition,
        "N6_derived_reused_tokens": derived_reused_tokens,
        "N7_label_skew": label_skew,
        "N7_label_words": label_value_words,
        "L1_raw_slugs": raw_slugs,
        "L1_samples": raw_slug_matches[:3],
        "X2_landscape_refs": landscape_refs,
    }


# ── contradiction AGGREGATE enc.* (N5·N7 NPOV·D2 Summary drill·D3 DUE balance·F1 Coatrack) ──
# Ported verbatim from contradiction.py `_check_contradictions_md`. Shared parsing
# (insights_section·analysis_section·all_links·axes_named[from con D1]) is orchestrator-injected.

L24_THEME_REF_RE = re.compile(r"\[\[([a-z][a-z0-9\-]+?)(?:\|([^\]]+))?\]\]")


def evaluate_contradiction_aggregate(
    *,
    insights_section: str,
    analysis_section: str,
    all_links: list,
    axes_named: list,
    theme_slugs: set,
    cluster_slugs: set,
) -> dict:
    """Measure contradiction aggregate enc.* (N5·N7·D2·D3·F1). Shared parsing is
    orchestrator-injected (axes_named comes from con D1). The returned dict is
    byte-identical to the corresponding _check_contradictions_md values (verbatim
    port)."""
    # N5 — verdict sentences in `## Implications` (reuses Part 1 lexicon; dormant Korean)
    insights_verdict_fails = 0
    for sentence in _split_sentences(insights_section):
        if any(p.search(sentence) for p in VERDICT_FAIL_PATTERNS):
            insights_verdict_fails += 1

    # N7 — value-word skew in axis titles (axes_named comes from con D1; English-first lexicon, Korean set ko-mode)
    axis_skew_hits: list = []
    for axis_name in axes_named:
        # axis-title separators: 'vs'·'/'·'·' fire on English; '대' is the Korean
        # "vs" separator and is dormant on English titles.
        parts = re.split(r"\s+(?:vs|대|·|/)\s+", axis_name.strip(), maxsplit=1)
        if len(parts) != 2:
            continue
        left_hits = [w for w in LABEL_VALUE_WORDS if w in parts[0].lower()]
        right_hits = [w for w in LABEL_VALUE_WORDS if w in parts[1].lower()]
        if bool(left_hits) != bool(right_hits):
            axis_skew_hits.append(f"{axis_name.strip()} (L={left_hits}, R={right_hits})")
    n7_skew = len(axis_skew_hits)

    # D2 — theme-reference pipe aliases in the analysis section
    analysis_theme_refs: list = []
    for match in L24_THEME_REF_RE.finditer(analysis_section):
        slug = match.group(1).strip()
        alias = match.group(2)
        if slug in theme_slugs:
            analysis_theme_refs.append((slug, alias))
    d2_total = len(analysis_theme_refs)
    d2_aliased = sum(1 for _slug, alias in analysis_theme_refs if alias)
    d2_raw = [slug for slug, alias in analysis_theme_refs if not alias]

    # D3 — per-axis theme balance
    axis_theme_counts: dict = {}
    axis_parts = re.split(r"^###\s+", analysis_section, flags=re.MULTILINE)
    for part in axis_parts[1:]:
        lines = part.splitlines()
        if not lines:
            continue
        axis_name = lines[0].strip()
        # Skip the MECE residual axis: English `Other` or, under WIKI_LANG=ko, `기타`.
        if axis_name.lower() in ("other", "기타"):
            continue
        body = "\n".join(lines[1:])
        count = sum(
            1 for m in L24_THEME_REF_RE.finditer(body)
            if m.group(1).strip() in theme_slugs
        )
        if count > 0:
            axis_theme_counts[axis_name] = count
    if len(axis_theme_counts) >= 2:
        values = list(axis_theme_counts.values())
        d3_max = max(values)
        d3_min = min(values)
        d3_ratio = d3_max / d3_min if d3_min > 0 else float("inf")
    else:
        d3_max = sum(axis_theme_counts.values())
        d3_min = d3_max if axis_theme_counts else 0
        d3_ratio = 1.0 if axis_theme_counts else 0.0

    # F1 — block landscape-cluster references (Coatrack)
    f1_refs: list = []
    for target in all_links:
        stem = target.strip().split("/")[-1].split("#", 1)[0]
        if stem in cluster_slugs:
            f1_refs.append(stem)
    f1_count = len(f1_refs)

    return {
        "insights_verdict_fails": insights_verdict_fails,
        "axis_skew_hits": axis_skew_hits,
        "n7_skew": n7_skew,
        "analysis_theme_refs": analysis_theme_refs,
        "d2_total": d2_total,
        "d2_aliased": d2_aliased,
        "d2_raw": d2_raw,
        "d3_max": d3_max,
        "d3_min": d3_min,
        "d3_ratio": d3_ratio,
        "f1_refs": f1_refs,
        "f1_count": f1_count,
    }


# ── overview L2-4 AGGREGATE enc.* (D2 Summary drill-down·F1 Coatrack) ──
# Ported verbatim from overview.py `_check_overview_md`. section_spans (from con D1)·
# all_links·theme_stems (wiki-global) are orchestrator-injected.

def evaluate_overview_aggregate(content: str, *, section_spans: list, all_links: list, theme_stems: set) -> dict:
    """Measure overview L2-4 D2 (drill-down)·F1 (Coatrack). section_spans is the con
    D1 output [(slug, match_end)]. theme_stems is wiki-global (orchestrator-injected).
    Verbatim from overview.py."""
    # D2 — self-slug drill-down link inside the cluster section
    d2_missing: list = []
    for slug, start in section_spans:
        next_h2 = re.search(r"^##\s", content[start:], re.MULTILINE)
        end = start + next_h2.start() if next_h2 else len(content)
        sec_text = content[start:end]
        if not re.search(rf"\[\[{re.escape(slug)}(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]", sec_text):
            d2_missing.append(slug)
    d2_found = len(section_spans)
    d2_count = d2_found - len(d2_missing)

    # F1 — block theme references (Coatrack)
    f1_count = 0
    for target in all_links:
        stem = target.strip().split("/")[-1].split("#", 1)[0]
        if stem in theme_stems:
            f1_count += 1

    return {
        "d2_count": d2_count,
        "d2_found": d2_found,
        "d2_missing": d2_missing,
        "f1_count": f1_count,
    }


# ── L2-2 hub enc.* (body density·`## Connections` grouping — encyclopedic nav-anchor form) ──
# Ported verbatim from hub_body.py `_check_body`. central_anchor (wiki-global inbound·
# whether it's an entity)·thresholds are orchestrator/manifest-injected. Detects
# bloat beyond the nav-anchor's responsibility.

_HUB_FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
_HUB_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
# Matches the `## Connections` hub section (the live English header, per hub.md);
# the hub body / link-grouping checks scope to this section.
_HUB_YEONGYEOL_RE = re.compile(r"^##\s+Connections\s*$(.*?)(?=^##\s|\Z)", re.MULTILINE | re.DOTALL)


def evaluate_hub_body(
    content: str,
    *,
    central_anchor: bool,
    body_len_advisory: int = 12000,
    yeongyeol_link_advisory: int = 50,
) -> dict:
    """Measure L2-2 hub body density (prose ≥ advisory · separates nav-anchor
    responsibility) and flat grouping of `## Connections` links. prose excludes the
    `## Connections` section (the nav link list is not prose). central_anchor (an
    entity or inbound≥threshold) is exempt from the body advisory — orchestrator-
    injected. Verbatim from hub_body.py. The orchestrator formats issues from the
    return value."""
    fm_match = _HUB_FM_RE.match(content)
    body = content[fm_match.end():] if fm_match else content
    body = _HUB_HTML_COMMENT_RE.sub("", body)

    prose = _HUB_YEONGYEOL_RE.sub("", body)
    body_len = len(prose.strip())
    body_fires = body_len >= body_len_advisory and not central_anchor

    section_match = _HUB_YEONGYEOL_RE.search(body)
    link_count = 0
    grouped = False
    link_fires = False
    if section_match:
        section_body = section_match.group(1)
        link_count = len(WIKILINK_RE.findall(section_body))
        grouped = bool(re.search(r"^###\s+", section_body, re.MULTILINE))
        link_fires = link_count >= yeongyeol_link_advisory and not grouped

    return {
        "body_len": body_len,
        "body_fires": body_fires,
        "yeongyeol_link_count": link_count,
        "grouped": grouped,
        "link_fires": link_fires,
    }
