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
# What G2 measures is whether the claimant is **named** (WP:ASF). The wikilink is
# one means to that end, so when a speaker falls below the page-creation threshold
# the plain-text real name is the terminal form — accepting only wikilinks leaves
# every page citing such a speaker permanently FAILing, and the author reaches for
# some nearby entity to get through (the misattribution path). Plain text is
# admitted, and the three cases below are screened out instead. Whether a short
# plain head is the speaker or the topic is not machine-decidable and stays with
# the Desk.
GRADE_HEAD_RE = re.compile(r"^\[(?:fact|analysis|forecast)\]\s+(.*)$")
# (1) Anonymous / collective subjects are barred in plain text too — the
# unattributed phrasing WP:ASF forbids. In English the discriminator is case: a
# named source carries a capitalized final word (`Free Software Foundation`),
# a weasel does not (`the foundation`). Keying on the word alone without that
# boundary would drop the very names the guideline offers as correct examples.
WEASEL_LAST_WORD = frozenset({
    "government", "industry", "market", "media", "authorities", "officials",
    "sources", "experts", "observers", "insiders", "critics", "supporters",
    "analysts", "community", "foundation", "public", "regulators", "researchers",
    "commentators", "advocates", "developers", "companies", "vendors",
})
_LEADING_ARTICLE_RE = re.compile(r"^(?:the|a|an)\s+", re.I)


def _is_weasel_head(head: str) -> bool:
    words = _LEADING_ARTICLE_RE.sub("", head).split()
    if not words:
        return True
    last = words[-1]
    return last.lower().strip(".,;:") in WEASEL_LAST_WORD and not last[:1].isupper()


# (2) Blocks pushing content into the head slot. Longest measured in-corpus: 28.
CLAIMANT_HEAD_MAX = 40
CITATION_PREFIX_RE = re.compile(r"^-\s*(cites|references|contradicts|defines)\s*:", re.MULTILINE)
CONNECT_LINE_RE = re.compile(r"^-\s+.+?$", re.MULTILINE)
QUOTE_LINE_RE = re.compile(r"^>\s+[\"“”].+", re.MULTILINE)
# A2 speaker attribution — quote marks pair up, so the outermost quotation closes at an
# **even-indexed** mark. The separator is the first *spaced* dash between such a mark and
# the next mark, and the attribution is everything after it. Every clause there was bought
# by a class that a cheaper rule got wrong: keyed on any dash, a dash inside the quotation
# passes as an attribution and exempts a quote that names nobody; keyed on the text after
# the last mark, a quoted title in the attribution (`— [[X]], author of "Y"`) swallows it
# and reports a linked speaker as unattributed; ignoring parity, a nested term
# (`"they call it "open source" — …`) outranks the real separator and credits a link from
# inside the quotation as the speaker; requiring the dash to sit *immediately* after the
# mark, anything between the two (`"…" (emphasis added) — X`, `"…," she said — X`, or a
# Korean particle) reads as naming nobody; and allowing an unspaced dash, a hyphenated
# date (`"…" 2024-10-28`) poses as a separator. The dash *character class* matches the
# sibling parser in `tools/_lint/cited_speakers.py`, which permits an unspaced dash where
# this does not.
#
# The premise is narrower than "marks pair up": it is that no even-indexed mark before the
# outer closer carries a spaced dash inside its own window. Two things break it — an
# unbalanced mark shifts every later parity, and in a balanced nested quotation the inner
# *opening* mark sits at an even index, so a spaced dash within the nested phrase wins.
# Scarcity is not the backstop: 20 of the 3,198 quote lines in the sibling corpus that
# shares this schema carry a wikilink inside the quotation body, so the window bound is.
#
# Known cost, measured on that corpus: the in-window search is a loosening. 15 lines read
# differently than under an adjacent-dash rule and every one moves toward PASS or exempt —
# 4 correctly, while 7 newly credit a concept hub or an employer org as the speaker (the
# blind spot step 5 forbids editorially and no check can see) and 2 lose a correct FAIL.
QUOTE_MARK_RE = re.compile(r"[\"“”]")
SPEAKER_DASH_RE = re.compile(r"\s+[—–-]+\s+")
SPEAKER_LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
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
#  references:·contradicts:·defines:) also fire, but the lint callers judge G2 only
#  under WIKI_LANG=ko and show it as not applicable (—) in English. See FLAG.)
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

    claimant_slot_filled = 0
    g2_plain = 0
    g2_missing_samples = []
    for line in claim_lines:
        m = GRADE_HEAD_RE.match(line)
        if not m:
            continue  # a missing grade marker is G1's business
        rest = m.group(1)
        if rest.startswith("[["):
            claimant_slot_filled += 1
            continue
        head = rest.split("—", 1)[0].strip() if "—" in rest else ""
        # (3) A plain head that names a real page is evasion — it could have been linked.
        if (
            head
            and len(head) <= CLAIMANT_HEAD_MAX
            and not _is_weasel_head(head)
            and head not in page_index
        ):
            claimant_slot_filled += 1
            g2_plain += 1
        elif len(g2_missing_samples) < 3:
            g2_missing_samples.append(line[:60])
    g2_pass = (claim_total == 0) or (claimant_slot_filled == claim_total)

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
    # Two things only are decided mechanically: is a speaker named at all, and if one
    # is linked, does the target exist. Whether a plain-text speaker should have been
    # linked is not machine-decidable — the org in a role line is not the speaker
    # (`Matt Garman, AWS CEO`), so name-matching would manufacture misattribution.
    # Plain-text speakers therefore leave the denominator, and link *validity* is
    # counted in place of link presence.
    quotes_body = _section_body(body, "## Key Quotes")
    quote_lines = QUOTE_LINE_RE.findall(quotes_body)
    a2_total = 0
    a2_with = 0
    for line in quote_lines:
        marks = list(QUOTE_MARK_RE.finditer(line))
        attribution = ""
        for i, mark in enumerate(marks, 1):
            if i % 2:
                continue  # an opening mark — a dash after it sits inside the quotation
            stop = marks[i].start() if i < len(marks) else len(line)
            dash = SPEAKER_DASH_RE.search(line, mark.end(), stop)
            if dash:
                attribution = line[dash.end():].strip()
                break
        if not attribution:
            a2_total += 1  # nobody named — there is no attribution to exempt
            continue
        link = SPEAKER_LINK_RE.search(attribution)
        if link:
            a2_total += 1
            if link.group(1).strip() in page_index:
                a2_with += 1
        elif attribution.split(",", 1)[0].strip() in page_index:
            a2_total += 1  # a plain name that has a page is link evasion, as in G2 (3)
        # else: plain-text speaker with no page — not judged
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
        "g2": (g2_pass, claimant_slot_filled, claim_total, g2_missing_samples, g2_plain),
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
        text = source_md_path.read_text(encoding="utf-8", errors="replace")
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
        for m in ANCHOR_LINK_RE.finditer(bullet):
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
