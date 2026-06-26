"""scholarly-citation craft skill — deterministic checks.

Verifiable-attribution craft — claim atomization, evidence grading, claimant
attribution, citation typing, anchoring. It owns the measurement of the source
page's cit.* criteria (legacy G1–G5·C1–C3·A1–A3). A craft synthesizing external
sources (Toulmin·scite/Elicit·WP:ASF·scite Smart Citations·Xanadu·Hyper-G·APA)
into an atomic-claim schema.

content-type-agnostic: wiki-global state (page_index·section-title lookup) is
injected by the orchestrator (tools/_lint/source.py) — this module uses only pure
text measurement + injected context. The measurement logic was ported verbatim
from source.py `_evaluate` (diff-0).

NOTE: the schema matchers below key on the live English wiki schema (## Key Claims·
## Connections·[fact]/[analysis]/[forecast]·## Key Quotes·## Representative Evidence)
and fire normally. Only the Korean-prose matchers are dormant on an English corpus —
G3 (와/및 conjunctions), G5 (Korean verb endings) — and fire under WIKI_LANG=ko.
"""

from __future__ import annotations

import re


# ── cit measurement regexes (ported verbatim from source.py) ──
# Grade markers [fact]/[analysis]/[forecast] — the live English source.md schema.
GRADE_MARKER_RE = re.compile(r"^-\s*\[(fact|analysis|forecast)\]", re.MULTILINE)
CLAIM_LINE_RE = re.compile(r"^-\s+(.+?)\s*$", re.MULTILINE)
GRADE_PLUS_CLAIMANT_RE = re.compile(r"^-\s*\[(fact|analysis|forecast)\]\s+\[\[", re.MULTILINE)
CITATION_PREFIX_RE = re.compile(r"^-\s*(cites|references|contradicts|defines)\s*:", re.MULTILINE)
CONNECT_LINE_RE = re.compile(r"^-\s+.+?$", re.MULTILINE)
QUOTE_LINE_RE = re.compile(r"^>\s+[\"“”].+", re.MULTILINE)
QUOTE_WITH_SPEAKER_RE = re.compile(r"^>\s+[\"“”].*?—.*?\[\[", re.MULTILINE)
H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
# (dormant: G3 keys on the Korean "and" conjunctions 와/및 joining two hubs; never
#  fires on English prose. An English equivalent would detect "and" between two
#  [[hub]] links. See FLAG.)
G3_COMPOSITE_RE = re.compile(r"\[\[[^\]]+\]\][^\n]*\s(와|및)\s[^\n]*\[\[[^\]]+\]\]")
# (dormant: G5 keys on Korean verb endings 했고…했다/한다/이다/된다; never fires on
#  English prose. An English equivalent would detect verb-phrase juxtaposition like
#  "…did, and …did". See FLAG.)
G5_VERB_SPLIT_RE = re.compile(r"했고\s*,\s*[^\n]*?(했다|한다|이다|된다)")
ANCHOR_LINK_RE = re.compile(r"\[\[([^\]|#]+)#([^\]|]+)(?:\|[^\]]+)?\]\]")
# Keys on the live English grade markers [fact]/[analysis]/[forecast].
CLAIMANT_AFTER_GRADE_RE = re.compile(
    r"^-\s*\[(?:fact|analysis|forecast)\]\s+\[\[([^\]|#]+)(?:\|[^\]]+)?\]\]", re.MULTILINE
)
CONNECT_PREFIX_TARGET_RE = re.compile(
    r"^-\s*(cites|references|contradicts|defines)\s*:\s*\[\[([^\]|#]+)(?:\|[^\]]+)?\]\]",
    re.MULTILINE,
)


# ── overview·contradiction schema meta-use (legacy G1·G2) ──
# Ported from the _contradiction_meta_patterns module shared by overview.py·
# contradiction.py. advisory count of whether the EDITOR body of a cluster overview·
# theme/aggregate contradiction makes meta-use of the source schema's evidence grade
# (fact/analysis/forecast)·citation type (cites/references/contradicts/defines).
# Measures whether a synthesis page reflects the Phase 2 schema (attached to 1283
# sources) — scite Smart Citations·evidence grading craft.

# G1 — evidence grade reflection.
# (partly dormant: several patterns key on Korean meta-phrases — 1차/2차/3차 fact
#  (primary/secondary/tertiary source), 발화 주체/발화자 (claimant), 직접 인용
#  (direct quote), fact급/analysis급/forecast급, [fact]/[analysis]/[forecast], 증거 등급. The English
#  patterns (attribution·grade [ABC]·evidence grade) DO fire. An English equivalent
#  would add "primary/secondary source", "claimant", "direct quote", "[fact]/
#  [analysis]/[forecast]". See FLAG.)
GRADE_META_PATTERNS = [
    re.compile(r"1차\s*fact"),
    re.compile(r"2차\s*fact"),
    re.compile(r"3차\s*fact"),
    re.compile(r"발화\s*주체"),
    re.compile(r"발화자"),
    re.compile(r"직접\s*인용"),
    re.compile(r"attribution", re.IGNORECASE),
    re.compile(r"\bgrade\s*[ABC]\b", re.IGNORECASE),
    re.compile(r"fact급"),
    re.compile(r"analysis급"),
    re.compile(r"forecast급"),
    re.compile(r"\[fact\]"),
    re.compile(r"\[analysis\]"),
    re.compile(r"\[forecast\]"),
    re.compile(r"evidence\s*grade", re.IGNORECASE),
    re.compile(r"증거\s*grade", re.IGNORECASE),
    re.compile(r"증거\s*등급"),
]

# G2 — citation-type meta-distinction.
# (partly dormant: several patterns key on Korean meta-phrases — 정의/반박/인용
#  attribution, 맥락 참조 (context reference), cite/인용 강도 (cite strength), 강한
#  결합/약한 참조 (strong coupling/weak reference). The English literals (cites:·
#  references:·contradicts:·defines:) DO fire. An English equivalent would add
#  "context reference", "cite strength", "strong coupling/weak reference". See FLAG.)
CITATION_TYPE_META_PATTERNS = [
    re.compile(r"정의\s*attribution", re.IGNORECASE),
    re.compile(r"반박\s*attribution", re.IGNORECASE),
    re.compile(r"인용\s*attribution", re.IGNORECASE),
    re.compile(r"맥락\s*참조"),
    re.compile(r"cite\s*강도", re.IGNORECASE),
    re.compile(r"인용\s*강도"),
    re.compile(r"강한\s*결합"),
    re.compile(r"약한\s*참조"),
    re.compile(r"\bcites\s*:"),
    re.compile(r"\breferences\s*:"),
    re.compile(r"\bcontradicts\s*:"),
    re.compile(r"\bdefines\s*:"),
]


def count_grade_meta(content: str) -> int:
    """cit.grade-meta algorithm — count of evidence-grade meta expressions (legacy G1).

    content is the EDITOR region (AUTO blocks excluded) extracted and injected by the
    orchestrator — this function does not know the content type. The threshold VALUE
    (≥2) is manifest-injected."""
    return sum(len(p.findall(content)) for p in GRADE_META_PATTERNS)


def count_cite_type_meta(content: str) -> int:
    """cit.cite-type-meta algorithm — count of citation-type meta-distinction expressions (legacy G2)."""
    return sum(len(p.findall(content)) for p in CITATION_TYPE_META_PATTERNS)


def _section_body(content: str, header: str) -> str:
    """Return the body of the H2 section (`## <header>`), or '' if absent. Ported
    verbatim from source.py."""
    pattern = re.compile(rf"^{re.escape(header)}\s*$", re.MULTILINE)
    m = pattern.search(content)
    if not m:
        return ""
    body_start = m.end()
    next_h2 = H2_RE.search(content, body_start)
    body_end = next_h2.start() if next_h2 else len(content)
    return content[body_start:body_end]


def evaluate_citation(
    body: str,
    *,
    page_index: dict,
    section_titles_fn,
    c2_ref_ratio_max: float = 0.95,
    c2_min_lines: int = 5,
) -> dict:
    """Measure the source page's cit.* criteria (G1–G5·C1–C3·A1–A3).

    body is the strip_code'd body. page_index ({slug: (rel, hub_type)})·
    section_titles_fn (rel → section-title set) are wiki-global state injected by the
    orchestrator. The c2 threshold is manifest-injected (content-type-agnostic). The
    returned dict is byte-identical to source.py `_evaluate`'s key tuples.
    """
    # G1, G2, G3 — atomic units in `## Key Claims`.
    # `## Key Claims` is the live English source.md section header.
    claims_body = _section_body(body, "## Key Claims")
    claim_lines = [m.group(1) for m in CLAIM_LINE_RE.finditer(claims_body)]
    claim_total = len(claim_lines)

    grade_count = len(GRADE_MARKER_RE.findall(claims_body))
    g1_pass = (claim_total == 0) or (grade_count == claim_total)
    g1_missing_samples = []
    if not g1_pass:
        for line in claim_lines:
            if not re.match(r"\[(fact|analysis|forecast)\]", line):
                g1_missing_samples.append(line[:60])
                if len(g1_missing_samples) >= 3:
                    break

    grade_with_claimant = len(GRADE_PLUS_CLAIMANT_RE.findall(claims_body))
    g2_pass = (claim_total == 0) or (grade_with_claimant == claim_total)
    g2_missing_samples = []
    if not g2_pass:
        for line in claim_lines:
            if re.match(r"\[(fact|analysis|forecast)\]", line) and not re.match(
                r"\[(fact|analysis|forecast)\]\s+\[\[", line
            ):
                g2_missing_samples.append(line[:60])
                if len(g2_missing_samples) >= 3:
                    break

    g3_violations = len(G3_COMPOSITE_RE.findall(claims_body))
    g3_pass = g3_violations == 0

    # G4 — claimant wikilink target validity.
    claimant_targets = CLAIMANT_AFTER_GRADE_RE.findall(claims_body)
    claimant_total = len(claimant_targets)
    claimant_valid = sum(1 for t in claimant_targets if t.strip() in page_index)
    g4_pass = claimant_total == 0 or claimant_valid == claimant_total
    g4_invalid_samples = [t for t in claimant_targets if t.strip() not in page_index][:3]

    # G5 — composite verb-clause split.
    g5_violations = 0
    for line in claim_lines:
        if G5_VERB_SPLIT_RE.search(line):
            g5_violations += 1
    g5_pass = g5_violations == 0

    # C1, C2 — citation-type prefix in `## Connections` (live English header).
    connect_body = _section_body(body, "## Connections")
    connect_lines = [m.group(0) for m in CONNECT_LINE_RE.finditer(connect_body)]
    connect_total = len(connect_lines)
    prefix_count = len(CITATION_PREFIX_RE.findall(connect_body))
    c1_pass = (connect_total == 0) or (prefix_count == connect_total)

    ref_count = len(
        [m for m in CITATION_PREFIX_RE.finditer(connect_body) if m.group(1) == "references"]
    )
    if connect_total < c2_min_lines:
        c2_pass = True
        c2_ratio_pct = -1  # exempt sentinel
    else:
        c2_ratio = ref_count / connect_total if connect_total else 0
        c2_ratio_pct = round(c2_ratio * 100)
        c2_pass = c2_ratio <= c2_ref_ratio_max

    # C3 — type-hub matching. `defines:` requires concept hub.
    c3_violations: list[str] = []
    c3_total = 0
    for m in CONNECT_PREFIX_TARGET_RE.finditer(connect_body):
        c3_total += 1
        prefix, target = m.group(1), m.group(2).strip()
        entry = page_index.get(target)
        if entry is None:
            continue  # broken link is G4/structure's job
        _, hub_type = entry
        if prefix == "defines" and hub_type != "concept":
            c3_violations.append(f"{prefix}: [[{target}]] (hub_type={hub_type})")
    c3_pass = len(c3_violations) == 0

    # A1 — anchor presence in `[fact]`·`[analysis]` claim lines (advisory only).
    # Keys on the live English grade markers [fact]/[analysis].
    anchor_eligible_lines = [ln for ln in claim_lines if re.match(r"\[(fact|analysis)\]", ln)]
    anchored_lines = [
        ln for ln in anchor_eligible_lines if re.search(r"\[\[[^\]]*#[^\]]+\]\]", ln)
    ]
    a1_eligible = len(anchor_eligible_lines)
    a1_anchored = len(anchored_lines)
    a1_pass = True  # advisory — always PASS

    # A2 — blockquote speaker attribution in `## Key Quotes` (live English header).
    quotes_body = _section_body(body, "## Key Quotes")
    quote_lines = QUOTE_LINE_RE.findall(quotes_body)
    quote_with_speaker = QUOTE_WITH_SPEAKER_RE.findall(quotes_body)
    if not quote_lines:
        a2_pass = True
        a2_total = 0
        a2_with = 0
    else:
        a2_total = len(quote_lines)
        a2_with = len(quote_with_speaker)
        a2_pass = a2_with == a2_total

    # A3 — anchor wikilink validity (`[[<slug>#<section>]]`).
    a3_total = 0
    a3_valid = 0
    a3_invalid_samples: list[str] = []
    for m in ANCHOR_LINK_RE.finditer(claims_body):
        a3_total += 1
        target_slug, section = m.group(1).strip(), m.group(2).strip()
        entry = page_index.get(target_slug)
        if entry is None:
            a3_invalid_samples.append(f"{target_slug}#{section} (slug not found)")
            continue
        target_rel, _ = entry
        if section in section_titles_fn(target_rel):
            a3_valid += 1
        else:
            a3_invalid_samples.append(f"{target_slug}#{section} (section not found)")
    a3_pass = a3_total == 0 or a3_valid == a3_total

    return {
        "g1": (g1_pass, grade_count, claim_total, g1_missing_samples),
        "g2": (g2_pass, grade_with_claimant, claim_total, g2_missing_samples),
        "g3": (g3_pass, g3_violations),
        "g4": (g4_pass, claimant_valid, claimant_total, g4_invalid_samples),
        "g5": (g5_pass, g5_violations),
        "c1": (c1_pass, prefix_count, connect_total),
        "c2": (c2_pass, c2_ratio_pct, connect_total),
        "c3": (c3_pass, c3_total - len(c3_violations), c3_total, c3_violations[:3]),
        "a1": (a1_pass, a1_anchored, a1_eligible),
        "a2": (a2_pass, a2_with, a2_total),
        "a3": (a3_pass, a3_valid, a3_total, a3_invalid_samples[:3]),
    }


# ── contradiction theme cit.* (L2 cite-consistency·L3 grounding·L4 anchor) ──
# Ported verbatim from contradiction.py. wiki-global (sources_dir)·shared parsing
# (claim_sources·evidence_slugs) are orchestrator-injected.

L3_ITEM_MIN_CHARS = 20       # minimum item length to register
L3_SUBSTRING_CHARS = 20      # leading chars used for body substring match
_QUOTE_BLOCK_RE = re.compile(r'>\s*"([^"]+)"', re.MULTILINE)
# Source-evidence extractors for L3 grounding: match the live English source-page
# headers `## Key Quotes` / `## Key Claims` (source.md schema). The Korean headers
# `## 주요 인용` / `## 주요 주장` fire under WIKI_LANG=ko.
_SECTION_QUOTES_RE = re.compile(r'##\s*(?:Key Quotes|주요\s*인용)\s*\n(.*?)(?=\n##\s|\Z)', re.DOTALL)
_SECTION_CLAIMS_RE = re.compile(r'##\s*(?:Key Claims|주요\s*주장)\s*\n(.*?)(?=\n##\s|\Z)', re.DOTALL)
_BULLET_RE = re.compile(r'^\s*-\s+(.+?)$', re.MULTILINE)
# Keys on the live English grade markers [fact]/[analysis]/[forecast].
_CLAIM_PREFIX_RE = re.compile(r'^\s*\[(?:fact|analysis|forecast)\]\s*\[\[[^\]]+\]\]\s*[—–-]\s*')
_SMART_QUOTE_TRANS = str.maketrans({
    "“": '"', "”": '"',
    "‘": "'", "’": "'",
})
_QUOTE_IN_BULLET_RE = re.compile(
    r'["“”][^"“”\n]{3,}?["“”]|[「『][^」』\n]{3,}?[」』]|^>\s*["“]',
    re.MULTILINE,
)
_ANCHORED_LINK_RE = re.compile(r"\[\[([^#\]|]+)#([^|\]]+)(?:\|[^\]]+)?\]\]")
# The live English anchor-target section titles (an anchored bullet points to one
# of these source.md sections).
_ANCHOR_ALLOWED_SECTIONS = {"Key Quotes", "Key Claims", "Summary"}


def _extract_section(content: str, heading: str) -> str:
    """Body between `## <heading>` and the next H2 (or EOF). Verbatim from
    contradiction.py."""
    pattern = re.compile(
        r"^##\s+" + re.escape(heading) + r".*?$(.*?)(?=^##\s|\Z)",
        re.DOTALL | re.MULTILINE,
    )
    m = pattern.search(content)
    return m.group(1) if m else ""


def _normalize_for_match(s: str) -> str:
    s = s.translate(_SMART_QUOTE_TRANS)
    s = re.sub(r'[\"\'`*]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def _extract_source_evidence_items(source_md_path) -> list:
    try:
        text = source_md_path.read_text(encoding="utf-8")
    except OSError:
        return []
    items: list[str] = []
    sect_quote = _SECTION_QUOTES_RE.search(text)
    if sect_quote:
        items.extend(_QUOTE_BLOCK_RE.findall(sect_quote.group(1)))
    sect_claim = _SECTION_CLAIMS_RE.search(text)
    if sect_claim:
        claim_body = sect_claim.group(1)
        for bullet in _BULLET_RE.findall(claim_body):
            items.append(bullet)
            prose = _CLAIM_PREFIX_RE.sub("", bullet, count=1)
            if prose != bullet:
                items.append(prose)
    return [i.strip() for i in items if len(i.strip()) >= L3_ITEM_MIN_CHARS]


def _cite_consistency(body: str, frontmatter_sources: list, claim_sources: set):
    """L2 — (missing_count, missing_slugs). body ⊆ frontmatter for claim sources."""
    fm_set = set(frontmatter_sources or [])
    body_cited = [s for s in claim_sources if s in body]
    missing = sorted(s for s in body_cited if s not in fm_set)
    return len(missing), missing


def _quote_grounding(body: str, evidence_slugs: set, sources_dir):
    """L3 — (grounded, total_with_evidence, missing_slugs)."""
    grounded = 0
    total_with_evidence = 0
    missing: list[str] = []
    body_norm = _normalize_for_match(body)
    for slug in sorted(evidence_slugs):
        src = sources_dir / f"{slug}.md"
        if not src.exists():
            continue
        items = _extract_source_evidence_items(src)
        if not items:
            continue
        total_with_evidence += 1
        any_grounded = False
        for item in items:
            snippet = _normalize_for_match(item)[:L3_SUBSTRING_CHARS]
            if snippet and snippet in body_norm:
                any_grounded = True
                break
        if any_grounded:
            grounded += 1
        else:
            missing.append(slug)
    return grounded, total_with_evidence, missing


def _evidence_anchor_check(body: str, source_slugs: set):
    """L4 advisory — (anchored, quoted_total, unanchored_samples)."""
    # `Representative Evidence` is the live English contradiction.md section header.
    evidence_section = _extract_section(body, "Representative Evidence")
    if not evidence_section:
        return 0, 0, []
    parts = re.split(r"(?:^|\n)\s*-\s+", "\n" + evidence_section.strip())
    bullets = [p for p in parts if p.strip()]
    quoted_total = 0
    anchored = 0
    unanchored_samples: list[str] = []
    for bullet in bullets:
        if not _QUOTE_IN_BULLET_RE.search(bullet):
            continue
        quoted_total += 1
        bullet_anchored = False
        for m in _ANCHORED_LINK_RE.finditer(bullet):
            stem = m.group(1).strip().split("/")[-1].removesuffix(".md")
            section = m.group(2).strip()
            if section not in _ANCHOR_ALLOWED_SECTIONS:
                continue
            if source_slugs and stem not in source_slugs:
                continue
            bullet_anchored = True
            break
        if bullet_anchored:
            anchored += 1
        else:
            preview = bullet.strip().splitlines()[0][:60]
            unanchored_samples.append(preview + ("…" if len(bullet.strip()) > 60 else ""))
    return anchored, quoted_total, unanchored_samples


def evaluate_contradiction_citation(
    body: str,
    *,
    fm_sources: list,
    claim_sources: set,
    evidence_slugs: set,
    source_slugs: set,
    sources_dir,
) -> dict:
    """Measure the contradiction theme's cit.* (L2·L3·L4). claim_sources (X1)·
    evidence_slugs (S2)·sources_dir are orchestrator-injected. The returned dict is
    byte-identical to the corresponding keys of the original _rubric_metrics (verbatim
    port)."""
    l2_missing_count, l2_missing_slugs = _cite_consistency(body, fm_sources, claim_sources)
    l3_grounded, l3_total_quotes, l3_missing_grounding = _quote_grounding(
        body, evidence_slugs, sources_dir
    )
    l4_anchored, l4_quoted_total, l4_unanchored_samples = _evidence_anchor_check(
        body, source_slugs
    )
    return {
        "L2_missing_count": l2_missing_count,
        "L2_missing_slugs": l2_missing_slugs,
        "L3_grounded": l3_grounded,
        "L3_total_with_quotes": l3_total_quotes,
        "L3_missing_grounding": l3_missing_grounding,
        "L4_anchored": l4_anchored,
        "L4_quoted_total": l4_quoted_total,
        "L4_unanchored_samples": l4_unanchored_samples,
    }
