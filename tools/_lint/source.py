"""Source page schema lint — `wiki/sources/<slug>.md` (L2-1, Phase 2 schema).

Phase 2(2026-05-02) introduced a 3-layer epistemics primitive on source
pages — claim atomization (`## Key Claims` atomic units with grade marker
`[fact]`/`[analysis]`/`[forecast]` + claimant wikilink), citation type prefix
(`## Connections` lines start with `cites:`/`references:`/`contradicts:`/`defines:`),
and evidence grade (the marker itself). This module implements the 10
automated criteria defined in `.claude/layers/source.md`.

Schema deviations hard-fail (exit 1), like the graph/hub/meta groups — the
1,283-source migration completed 2026-05-04 (CLAUDE.md "Source Page Format").
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import WIKI, WIKILINK_ANY_RE, parse_frontmatter, read_text_cached, real_source_files, strip_code, strip_frontmatter  # noqa: E402
sys.path.insert(0, str(Path(__file__).parent))
from _advisory_common import mark  # noqa: E402

import importlib.util as _ilu  # noqa: E402
import json as _json  # noqa: E402

# cit.* (G1–G5·C1–C3·A1–A3) measurement is owned by the scholarly-citation
# skill. The call configuration is the manifest SoT (`source.bundles`).
# Wiki-global state (page_index·section title) is injected by the orchestrator
# code; the threshold (c2) comes from manifest params.
_REPO_ROOT = Path(__file__).resolve().parents[2]
_MANIFEST = _json.loads((_REPO_ROOT / ".claude" / "layers" / "_manifest.json").read_text(encoding="utf-8"))
_cit_skill_name = "scholarly-citation"
_cit_bundle_cfg = _MANIFEST["source"]["bundles"][_cit_skill_name]
_cit_spec = _ilu.spec_from_file_location(
    "cit_checks", _REPO_ROOT / ".claude" / "skills" / _cit_skill_name / "checks.py"
)
cit_skill = _ilu.module_from_spec(_cit_spec)
_cit_spec.loader.exec_module(cit_skill)
_CIT_FN = _cit_bundle_cfg["fn"]
_CIT_PARAMS = _cit_bundle_cfg.get("params", {})

SOURCES_DIR = WIKI / "sources"

# Source slug filename convention — lowercase kebab-case (.claude/policies/
# naming.md "Source slugs: kebab-case"). Enforced as a HARD fail independent of
# the Phase 2 schema check: a non-kebab slug (e.g. camelCase `openBSD`)
# silently breaks wikilinks/orphans when referencing pages use a different case,
# and is immediately fixable by rename — no natural-accumulation margin applies.
# `_`-prefixed files (catalogs) are meta artifacts, excluded.
SLUG_KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# Wiki page index — built once per run, used for G4 (claimant validity),
# A3 (anchor validity), and C3 (type-hub matching). Maps every plausible
# wikilink form (stem · stem.md · subdir/stem.md) to the canonical
# (rel_path, page_type) tuple. Mirrors `_lib._build_id_map`.
_PAGE_INDEX_CACHE: dict[str, tuple[str, str]] | None = None

# Section-title cache for A3 anchor validity. Lazy-populated on first
# need per target file (post-Phase-2 anchor coverage scales — caching
# avoids re-reading the same target file across multiple sources).
_SECTION_TITLES_CACHE: dict[str, set[str]] = {}


def _target_section_titles(rel: str) -> set[str]:
    """Return the set of H2 section titles for a wiki/<rel> file. Cached."""
    cached = _SECTION_TITLES_CACHE.get(rel)
    if cached is not None:
        return cached
    try:
        content = read_text_cached(WIKI / rel)
    except OSError:
        # Do not cache — if a transient I/O error permanently froze an empty
        # set, subsequent A3 anchor checks would misjudge every anchor in that file.
        return set()
    titles = {m.group(1).strip() for m in H2_RE.finditer(content)}
    _SECTION_TITLES_CACHE[rel] = titles
    return titles


def _build_page_index() -> dict[str, tuple[str, str]]:
    """Walk wiki/ once and map wikilink forms → (rel, type)."""
    global _PAGE_INDEX_CACHE
    if _PAGE_INDEX_CACHE is not None:
        return _PAGE_INDEX_CACHE
    idx: dict[str, tuple[str, str]] = {}
    for root, _dirs, files in os.walk(WIKI):
        for f in files:
            if not f.endswith(".md") or f.startswith("_"):
                continue
            fp = Path(root) / f
            rel = str(fp.relative_to(WIKI)).replace("\\", "/")
            try:
                content = read_text_cached(fp)
            except Exception:
                continue
            fm = parse_frontmatter(content)
            page_type = fm.get("type", "unknown")
            stem = f.removesuffix(".md")
            idx.setdefault(rel, (rel, page_type))
            idx.setdefault(stem, (rel, page_type))
            idx.setdefault(stem + ".md", (rel, page_type))
    _PAGE_INDEX_CACHE = idx
    return idx

# Phase 2 migration toggle. While advisory, the lint reports counts but
# always returns exit code 0 so existing 1,283 non-compliant sources do
# not block other lint groups. Migration completion flips this to False.
# Acceptable residual fails — corpus-level migration tolerance.
# Some claimants are intrinsically unfixable (general nouns, multi-entity
# enumerations, single-cite people below stub threshold) and create
# permanent G2/G4 fails that no further migration round can resolve.
# Two-tier policy:
#   1. INTRINSICALLY_UNFIXABLE_SOURCES — explicit whitelist of permanent
#      residual fails (policy-aligned with `feedback_no_single_source_stub`:
#      single-cite claimants below stub threshold, general nouns, etc.).
#      These do NOT count toward ACCEPTABLE_FAILS.
#   2. ACCEPTABLE_FAILS — natural-accumulation margin for unwhitelisted
#      fails between ingest cycles. New regressions exceeding this
#      threshold trigger hard fail.
# Whitelist members are surfaced as advisory but excluded from threshold
# enforcement so the margin remains a regression detector, not a hiding
# mechanism.
ACCEPTABLE_FAILS = 10

# Permanent residual whitelist — single-cite claimants below stub threshold,
# general nouns, or self-cluster repetition without multi-cluster spread.
# Policy SoT: `.claude/policies/naming.md` "entity-addition threshold" + memory
# `feedback_no_single_source_stub` (cross-policy: same threshold governs both
# entity stub creation and source-schema claimant fixability).
# Adding a slug here MUST cite the policy clause that justifies permanent
# residual status (single-cite claim source · generic-noun form · no multi-cluster appearance).
INTRINSICALLY_UNFIXABLE_SOURCES: set[str] = {
    # Sprint 5 residual single-cite claimants (accumulated 2026-05-07~05-10):
    "subquadratic-subq-1m-preview-12m-token-context",       # G4: [[Subquadratic]] self-cites 5 times · multi-cluster 0
    "toss-large-conglomerate-designation-2026",             # G2: DowKiwoom·DB·Daishin·Minister Choi single-cite
    "namyangju-wangsuk-3rd-newtown-site-2026-06",           # G2: construction industry·government generic nouns
    "moreh-tenstorrent-llm-inference-dgx-class",            # G2: Tenstorrent single-cite
    "goldman-quantum-computing-pullback-2026",              # G2: Rigetti·Deloitte·Korea Center for International Finance·Subodh Kulgarni single-cite
    "bigtech-ai-security-redesign-2026",                    # G2: Trend Micro single-cite
    # Track A baseline-31 full sweep (2026-05-19~05-20 cleanup) residual single-cite entities:
    "mythos-korea-structural-vulnerability-kim-seungjoo",   # G4: Kim Seung-joo (Korea University Graduate School of Information Security) single-cite · multi-cluster 0
    "lee-jaebum-claude-code-personal-agent-sol-tina",       # G4: Lee Jae-beom (Kakao co-founder · Three Body Partners) single-cite · multi-cluster 0
    "openai-recurring-crisis-narrative-history",            # A2: Gary Marcus·MarketWatch single-cite speakers (A2 advisory level)
    # Namesake split (2026-05-24): the [[Lee Sang-geun]] entity is the DGB Daegu Bank ICT Group deputy president (3 sources).
    # The Lee Sang-geun in this source (director of the Korea University AI Security Research Center) is a namesake with only 2 distinct sources →
    # below stub threshold (≥3), kept as a plain-text claimant per feedback_no_single_source_stub policy →
    # intrinsically not G2-wikilinkable (cannot mislink a namesake to the [[Lee Sang-geun]] deputy-president entity).
    "mythos-shock-7-month-golden-time",                     # G2: Lee Sang-geun, director of Korea University AI Security Research Center, namesake plain text (4 claim lines)
    # Demotion sweep (2026-05-26, confirmed at desk 2nd gate): hub demotion·absorption left the entity
    # intentionally hub-less → claimant ends as plain text (not G2-wikilinkable unless re-promoted).
    # feedback_no_single_source_stub: subjects desk-confirmed and demoted as stub-ineligible because single-cite·isolated.
    "ai-dev-42-percent-speed-boost",                        # G2: Kim Tae-yang (SK Planet CTO) deleted and demoted → plain text
    "hyundaicard-ai-data-science-global",                   # G2: Bae Kyung-hwa (Hyundai Card digital division head) deleted and demoted → plain text
    "kb-securities-ai-wm-1q-130percent",                    # G2: Seoul Economic Daily (news outlet) deleted and demoted → plain text
    "kiwoong-info-efta-non-face-identity-verification",     # G2: Kiwoong Information & Communication (single-cite DSP) deleted and demoted → plain text
    "skt-ceo-yu-apac-ai-computing-2030",                    # G2: Yoo Young-sang (former SKT CEO) absorbed into SK Telecom and demoted → plain text
    # Demotion sweep (2026-06-24, confirmed at desk 2nd gate): single-cite·isolated entity hub demotion·deletion
    # left the claimant as plain text. Below feedback_no_single_source_stub threshold (≥3 cites·multi-cluster).
    "oasis-route-mini-ai-checkout",                         # G2: Oasis Market (grocery distribution, out-of-domain single-cite) deleted and demoted → plain text
    "lablup-amax-ai-infra-global",                          # G2: Shin Jeong-kyu (Lablup CEO) demoted → plain text
    "lablup-nvidia-ai-summit-japan",                        # G2: Shin Jeong-kyu (Lablup CEO) demoted → plain text
    "datadog-gpu-monitoring-launch",                        # G2: Datadog (single-cite identity) demoted → plain text
    "darkweb-phishing-kit-financial-cybercrime-kaspersky-2026",  # G2: Kaspersky (single-cite) demoted → plain text
    # G2 advisory triage (2026-06-24, operator judgment): suspected multi-source claimants, but
    # actual source tallies (excluding catalog/source_map) all came in below threshold (≥3 sources·multi-cluster).
    "germany-bfv-palantir-replace-chapsvision",            # G2: BfV (German Federal Office for the Protection of the Constitution) foreign agency, 1 source
    "kor-govt-openai-tac-mythos-shield",                   # G2: Choi Woo-hyuk (Ministry of Science and ICT) single-cite + reporter generic noun
    "openai-daybreak-cyber-defense-vision",                # G2: The Verge (outlet) — an outlet cannot be a claimant entity
    "ms-mdash-mythos-rival-kim-taesoo",                    # G2: Kim Tae-soo (MS security VP) 2 sources·single cluster, below threshold (external standing is clear but operator-whitelisted)
    "tci-fund-microsoft-divest-ai-disruption",             # G2: TCI/Christopher Hohn (activist fund) 2 sources, peripheral mention
    # ingest 2026-05-26: single-cite (1 source) · person Human Reviewer Gate claimants — below stub threshold
    # (≥3 distinct sources), so handled as plain text. On reaching ≥3, missing-entity detection
    # re-surfaces → at that point create the entity and remove from the whitelist (feedback_no_single_source_stub).
    "cerebras-kimi-k26-gpu-speed",                          # G2: Cerebras (single-cite AI chip vendor) plain text
    "akb-dnotitia-agent-knowledgebase",                     # G2: Dnotitia (single-cite developer) plain text
    "geohot-eternal-sloptember",                            # G2: George Hotz (single-cite · person gate) plain text
    # ingest 2026-06-07: single-cite (1 source) claimants — below stub threshold (≥3 distinct sources),
    # ending as plain text. On reaching ≥3, missing-entity re-surfaces → create the entity and remove.
    "samsung-electro-mechanics-silicon-capacitor-1-5t",     # G2: Samsung Electro-Mechanics (single-cite component maker) plain text
    "nh-agilesoda-acquisition",                             # G2: AgileSoda (single-cite acquired AI firm) plain text
    "china-datacenter-pe-exit",                             # G2: PDG·Warburg Pincus·Bain·Carlyle·Blackstone (single-cite foreign PE) plain text
    "quiet-ace-leaves-company",                             # G2: Unicorn Jungle (single-cite outlet) · low-relevance org-theory column plain text
    # ingest 2026-06-10 (inbox/NewsScrap): single-cite (1 source) claimants — below stub threshold (≥3 distinct
    # sources + ≥2 clusters), ending as plain text. Confirmed at desk VERIFY₂. On reaching ≥3,
    # missing-entity re-surfaces → create the entity and remove (feedback_no_single_source_stub).
    "a2sys-lee-dongsoo-seed-160bn",                         # G2: A2SYS (new startup) · Lee Dong-soo (founder) single-cite · multi-cluster 0 plain text
    # ingest 2026-06-12 (inbox 14 + NewsScrap 4): single-cite (1 source) claimants — below stub threshold
    # (≥3 distinct sources + ≥2 clusters), ending as plain text. On reaching ≥3,
    # missing-entity re-surfaces → create the entity and remove (feedback_no_single_source_stub).
    "xiaomi-mimo-ultraspeed-1000-tokens",                   # G2: Xiaomi·Artificial Analysis·Decrypt (foreign press) single-cite plain text (Xiaomi is borderline — gate on hold)
    "nds-aws-digital-service-iaas-registration",            # G2: NDS (single-cite AWS partner MSP) · Kim Jung-won (CEO) single-cite · multi-cluster 0 plain text
    "insignary-ai-code-opensource-license-risk",            # G2: Mike Pittenger (Insignary CSO) single-cite · multi-cluster 0 plain text
    # ingest 2026-06-14 (NewsScrap): single-cite (1 source) claimants — below stub threshold (≥3 distinct
    # sources + ≥2 clusters), ending as plain text. On reaching ≥3, missing-entity re-surfaces →
    # create the entity and remove (feedback_no_single_source_stub).
    "github-credential-leak-db-access-tving-dayone",         # G2: News1 (press)·TVING·Day1 Company (self-reporting breach party)·Kim Myung-joo (Seoul Women's University professor) single-cite · multi-cluster 0 plain text claimant
    "bytec-system-qilin-ransomware-breach",                  # G2: Bytec System (victim company)·Qilin (ransomware actor) single-cite · multi-cluster 0 plain text claimant
    "xiaomi-mimo-code-claude-code",                          # G2: Xiaomi claimant has 3 cumulative sources but all in a single LLM cluster (multi-cluster 0) — same gate-on-hold as xiaomi-mimo-ultraspeed; the org stub is operator judgment
    # ingest 2026-06-16 (NewsScrap, crawl supplement): single-cite (1 source) analyst claimants —
    # below stub threshold (≥3 distinct sources + ≥2 clusters), ending as plain text. Per desk ADAPT₂
    # instruction (attribution accuracy > G2 wikilink ratio), the [[Amazon]] misattribution was corrected to the actual speaker as plain text.
    # On reaching ≥3, missing-entity re-surfaces → create the entity and remove (feedback_no_single_source_stub).
    "aws-datacenter-water-efficiency",                       # G2: Matt Kimball (Moor Insights & Strategy) · Sanchit Vir Gogia (Greyhound Research) single-cite · multi-cluster 0 plain text claimant
    # ingest 2026-06-17 (inbox 19 + NewsScrap cumulative, 50-source batch): single-cite (1 source)
    # claimants — below stub threshold (≥3 distinct sources + ≥2 clusters), ending as plain text.
    # Strong candidates (McKinsey·Korea Investment & Securities·SpaceX·Coinone) were resolved with new entities in this batch.
    # Below are the residual single-cites. On reaching ≥3, missing-entity re-surfaces → create the entity and remove
    # (feedback_no_single_source_stub).
    "newcore-ai-agent-identity-seed-funding",                # G4: Newcore (new agent-identity-management firm, 2 sources) · Zohar Alon (CEO) single-cite · multi-cluster 0 plain text claimant
    "bigtech-asia-aidc-2year-buildout-korea-excluded",       # G4: Lee Hae-min (Rebuilding Korea Party lawmaker) · Korea Data Center Council single-cite · multi-cluster 0 plain text claimant
    "heat-pump-ai-datacenter-waste-heat-kimm",               # G4: Korea Institute of Machinery and Materials (the report's own author) · Park Jong-bae et al. single-cite · multi-cluster 0 plain text claimant
    "kisa-security-advisory-surge-ai-vulnerability",         # G4: CVE (generic noun) · Lee Yong-jun (Far East University professor) single-cite · multi-cluster 0 plain text claimant
    "metro-transmission-grid-7year-delay-4gw-blocked",       # G4: Park Jong-bae (Konkuk University professor) · Hanam City single-cite · multi-cluster 0 plain text claimant
    "work-ai-index-uk-2026-botsitting-productivity",         # G4: Glean · Jeong Heung-jun (Seoul National University of Science and Technology professor) single-cite · multi-cluster 0 plain text claimant
    "stt-gdc-seoul1-first-korea-datacenter-open",            # G4: STT GDC Korea (STT GDC · Hyosung Heavy Industries 60-40 joint venture) — same STT Seoul 1 facility event, 2 sources (paired with hyosung-stt-seoul1-datacenter-2026) · multi-cluster 0 plain text claimant
}

# Required Rubric criteria — any FAIL on these
# keys causes a non-zero exit (subject to ACCEPTABLE_FAILS at corpus level).
# Mirrors the `required_keys` list used by _print_corpus_summary for
# top-fail reporting; kept as a module constant so the corpus-scan and
# per-file paths share the same definition.
REQUIRED_KEYS = ("g1", "g2", "g4", "c1", "c3", "s1", "l1")

REQUIRED_SECTIONS = ("## Summary", "## Key Claims", "## Connections")
W1_MIN_LINKS = 5
L1_MIN_SLUG_LEN = 10

# The cit.* measurement regexes (grade·claimant·citation prefix·quote·composite·anchor)
# were moved verbatim to scholarly-citation/checks.py. This file measures only S1·W1·L1·desk.

# L1 — raw kebab-case slug exposure (no pipe alias).
L1_RAW_SLUG_RE = re.compile(r"\[\[([a-z][a-z0-9\-]{" + str(L1_MIN_SLUG_LEN - 1) + r",})\]\]")

# Section header detector.
H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)

# Wikilink (any) — captures inner target (without optional pipe alias).

# Desk-review sub-trigger — `[fact] ≥ 7 AND quoted citations ≥ 3`.
# 2026-05-19 threshold raised (5→7·2→3) — overall source distribution dropped 8.4% → 2.2%.
# Rationale for raising: desk PoC found a 45% critical+high defect rate · 4x reduction in
# operational burden · concentration on multi-speaker in-depth-reporting sources. SoT: the
# applicability scope in .claude/agents/desk.md.
DESK_TRIGGER_JARYO_MIN = 7
DESK_TRIGGER_QUOTE_MIN = 3
DESK_QUOTE_RE = re.compile(r"^>\s+", re.MULTILINE)
DESK_JARYO_RE = re.compile(r"^-\s*\[fact\]", re.MULTILINE)


def _has_section(content: str, header: str) -> bool:
    return bool(re.search(rf"^{re.escape(header)}\s*$", content, re.MULTILINE))


F1_DATE_RE = re.compile(r"^last_updated:\s*(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)
SCRAPED_RE = re.compile(r"^scraped:\s*(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)


def _evaluate(rel: str, content: str) -> dict:
    """Run all 10 Rubric criteria on a single source file.

    Returns dict with per-criterion result + samples for advisory output.
    """
    body = strip_code(content)

    # F1 (advisory) — frontmatter `last_updated: YYYY-MM-DD` present.
    # Advisory only (not in REQUIRED_KEYS) so the 18 existing sources missing
    # this field don't retroactively break ACCEPTABLE_FAILS. New ingest
    # path stamps last_updated automatically; this check surfaces gaps for
    # batch fix without blocking lint.
    _fm_end = content.find("\n---", 4)
    _fm_head = content[: _fm_end + 4] if _fm_end != -1 else content[:600]
    f1_pass = bool(F1_DATE_RE.search(_fm_head))

    # S1 — required sections.
    sections_present = [h for h in REQUIRED_SECTIONS if _has_section(body, h)]
    s1_count = len(sections_present)
    s1_pass = s1_count == len(REQUIRED_SECTIONS)

    # cit.* (G1–G5·C1–C3·A1–A3) — measured by the scholarly-citation skill.
    # Wiki-global state (page_index·section-title lookup) is injected by the
    # orchestrator. The returned dict is byte-identical to the existing
    # _evaluate key tuples (moved verbatim).
    page_index = _build_page_index()
    _cit = getattr(cit_skill, _CIT_FN)(
        body, page_index=page_index, section_titles_fn=_target_section_titles, **_CIT_PARAMS
    )

    # W1 — wikilink count.
    body_no_fm = strip_frontmatter(body)
    w1_links = len(WIKILINK_ANY_RE.findall(body_no_fm))
    w1_pass = w1_links >= W1_MIN_LINKS

    # L1 — raw slug exposure.
    l1_raw_slugs = L1_RAW_SLUG_RE.findall(body_no_fm)
    l1_pass = len(l1_raw_slugs) == 0

    # Desk-review sub-trigger (advisory).
    desk_jaryo = len(DESK_JARYO_RE.findall(body))
    desk_quote = len(DESK_QUOTE_RE.findall(body))
    desk_trigger = desk_jaryo >= DESK_TRIGGER_JARYO_MIN and desk_quote >= DESK_TRIGGER_QUOTE_MIN

    # T1 (HARD gate, unconditional — like the filename kebab check) —
    # frontmatter `tags` present AND non-empty. The source.md authoring standard
    # (line 81) mandates filling tags, but historically there was no check, so
    # empty `tags: []` accumulated indefinitely
    # (feedback_close_enforcement_gap_not_instance). The deployed graph browser
    # consumes frontmatter tags as a node meta badge, so an empty value means
    # unfinished authoring. Being a blocking gate, it FAILs until the reporter's
    # self-VERIFY (`lint source <slug> until PASS`) loop fills it. tags is a
    # meaning-judgment field with no auto-fix — suggest_tags.py proposes candidates.
    _tags = parse_frontmatter(content).get("tags")
    t1_pass = isinstance(_tags, list) and any(str(t).strip() for t in _tags)

    # Sc1 (HARD gate, unconditional — like T1) — frontmatter
    # `scraped: YYYY-MM-DD` present + valid. It is the weekly-briefing
    # collection-week aggregation key (a committed signal); if missing, the
    # source drops out of that week's roster. Ingest fills it from raw `created`
    # (source.md schema). Being a format field, it is a blocking gate — a missing
    # value means unfinished authoring.
    sc1_pass = bool(SCRAPED_RE.search(_fm_head))

    return {
        "rel": rel,
        "s1": (s1_pass, s1_count, len(REQUIRED_SECTIONS)),
        **_cit,
        "w1": (w1_pass, w1_links),
        "l1": (l1_pass, l1_raw_slugs[:5]),
        "f1": (f1_pass,),
        "t1": (t1_pass,),
        "sc1": (sc1_pass,),
        "desk": (desk_trigger, desk_jaryo, desk_quote),
    }


def _print_per_file(result: dict) -> None:
    """Emit three-line Rubric output for a single source file."""

    rel = result["rel"]
    s1_pass, s1_n, s1_total = result["s1"]
    g1_pass, g1_n, g1_total, g1_samples = result["g1"]
    g2_pass, g2_n, g2_total, g2_samples = result["g2"]
    g3_pass, g3_violations = result["g3"]
    g4_pass, g4_n, g4_total, g4_samples = result["g4"]
    g5_pass, g5_violations = result["g5"]
    c1_pass, c1_n, c1_total = result["c1"]
    c2_pass, c2_pct, c2_total = result["c2"]
    c3_pass, c3_n, c3_total, c3_samples = result["c3"]
    a1_pass, a1_n, a1_total = result["a1"]
    a2_pass, a2_n, a2_total = result["a2"]
    a3_pass, a3_n, a3_total, a3_samples = result["a3"]
    w1_pass, w1_n = result["w1"]
    l1_pass, l1_samples = result["l1"]
    (f1_pass,) = result["f1"]
    (t1_pass,) = result["t1"]
    (sc1_pass,) = result["sc1"]

    c2_str = "—" if c2_pct < 0 else f"{c2_pct}%"
    a1_str = "—" if a1_total == 0 else f"{a1_n}/{a1_total}"
    a2_str = "—" if a2_total == 0 else f"{a2_n}/{a2_total}"
    a3_str = "—" if a3_total == 0 else f"{a3_n}/{a3_total}"
    g4_str = "—" if g4_total == 0 else f"{g4_n}/{g4_total}"
    c3_str = "—" if c3_total == 0 else f"{c3_n}/{c3_total}"

    print(f"{rel}:")
    print(
        f"  [Rubric] G1 grade={g1_n}/{g1_total} {mark(g1_pass)}  "
        f"G2 claimant={g2_n}/{g2_total} {mark(g2_pass)}  "
        f"G3 atomic={g3_violations} {mark(g3_pass)}  "
        f"G4 valid_claimant={g4_str} {mark(g4_pass)}  "
        f"G5 composite={g5_violations} {mark(g5_pass)}"
    )
    print(
        f"  [Rubric] C1 prefix={c1_n}/{c1_total} {mark(c1_pass)}  "
        f"C2 ref_ratio={c2_str} {mark(c2_pass)}  "
        f"C3 type_hub={c3_str} {mark(c3_pass)}"
    )
    print(
        f"  [Rubric] A1 anchored={a1_str} {mark(a1_pass)}  "
        f"A2 quote_attr={a2_str} {mark(a2_pass)}  "
        f"A3 valid_anchor={a3_str} {mark(a3_pass)}  "
        f"S1 sections={s1_n}/{s1_total} {mark(s1_pass)}  "
        f"W1 links={w1_n} {mark(w1_pass)}  "
        f"L1 raw_slugs={len(l1_samples)} {mark(l1_pass)}  "
        f"F1 last_updated={mark(f1_pass)}  "
        f"T1 tags={mark(t1_pass)}  "
        f"Sc1 scraped={mark(sc1_pass)}"
    )

    # Advisory samples for FAILed criteria.
    if not g1_pass and g1_samples:
        print(f"  [Rubric] G1 missing grade lines: {g1_samples}")
    if not g2_pass and g2_samples:
        print(f"  [Rubric] G2 missing claimant lines: {g2_samples}")
    if not g4_pass and g4_samples:
        print(f"  [Rubric] G4 invalid claimant: {g4_samples}")
    if not c3_pass and c3_samples:
        print(f"  [Rubric] C3 type-hub mismatches: {c3_samples}")
    if not a3_pass and a3_samples:
        print(f"  [Rubric] A3 invalid anchors: {a3_samples}")
    if not l1_pass and l1_samples:
        print(f"  [Rubric] L1 raw slug samples: {l1_samples}")

    desk_trigger, desk_jaryo, desk_quote = result["desk"]
    if desk_trigger:
        print(
            f"  [Advisory] Desk qualitative review recommended — [fact]={desk_jaryo} AND "
            f"quoted citations={desk_quote} (sub-trigger met)"
        )


def _print_corpus_summary(results: list[dict]) -> None:
    """Emit one-line aggregate counts across all source files."""
    total = len(results)
    if total == 0:
        print("No source files found.")
        return

    g1_pass_n = sum(1 for r in results if r["g1"][0])
    g2_pass_n = sum(1 for r in results if r["g2"][0])
    g4_pass_n = sum(1 for r in results if r["g4"][0])
    c1_pass_n = sum(1 for r in results if r["c1"][0])
    c3_pass_n = sum(1 for r in results if r["c3"][0])
    s1_pass_n = sum(1 for r in results if r["s1"][0])
    l1_pass_n = sum(1 for r in results if r["l1"][0])
    f1_pass_n = sum(1 for r in results if r["f1"][0])
    t1_pass_n = sum(1 for r in results if r["t1"][0])
    sc1_pass_n = sum(1 for r in results if r["sc1"][0])

    print(f"Source schema diagnosis — {total} files (Phase 2)")
    print(
        f"  G1 grade marker     PASS={g1_pass_n}/{total} ({100 * g1_pass_n // total}%)"
    )
    print(
        f"  G2 claimant link    PASS={g2_pass_n}/{total} ({100 * g2_pass_n // total}%)"
    )
    print(
        f"  G4 valid claimant   PASS={g4_pass_n}/{total} ({100 * g4_pass_n // total}%)"
    )
    print(
        f"  C1 citation prefix  PASS={c1_pass_n}/{total} ({100 * c1_pass_n // total}%)"
    )
    print(
        f"  C3 type-hub match   PASS={c3_pass_n}/{total} ({100 * c3_pass_n // total}%)"
    )
    print(
        f"  S1 required sects   PASS={s1_pass_n}/{total} ({100 * s1_pass_n // total}%)"
    )
    print(
        f"  L1 raw slug clean   PASS={l1_pass_n}/{total} ({100 * l1_pass_n // total}%)"
    )
    print(
        f"  F1 last_updated     PASS={f1_pass_n}/{total} ({100 * f1_pass_n // total}%) [advisory]"
    )
    print(
        f"  T1 tags non-empty   PASS={t1_pass_n}/{total} ({100 * t1_pass_n // total}%) [hard gate]"
    )
    print(
        f"  Sc1 scraped present PASS={sc1_pass_n}/{total} ({100 * sc1_pass_n // total}%) [hard gate]"
    )

    desk_n = sum(1 for r in results if r["desk"][0])
    print(
        f"  Desk-review trigger {desk_n}/{total} ({100 * desk_n // total}%) "
        f"[advisory] — [fact] ≥ {DESK_TRIGGER_JARYO_MIN} AND quoted citations ≥ "
        f"{DESK_TRIGGER_QUOTE_MIN}"
    )

    # Top non-compliant slugs (by number of FAILed required criteria).
    fail_counts = []
    for r in results:
        n_fail = sum(1 for k in REQUIRED_KEYS if not r[k][0])
        if n_fail > 0:
            fail_counts.append((n_fail, r["rel"]))
    fail_counts.sort(reverse=True)

    if fail_counts:
        print(f"\n  Non-compliant top 20 (most-failed first):")
        for n_fail, rel in fail_counts[:20]:
            slug = rel.removeprefix("sources/").removesuffix(".md")
            print(f"    [{n_fail}/{len(REQUIRED_KEYS)} fail] {slug}")
        if len(fail_counts) > 20:
            print(f"    ... and {len(fail_counts) - 20} more")


def run(target: str | None = None, fix: bool = False, **_kwargs) -> int:
    """Lint source pages against Phase 2 schema (claim atomization +
    citation type + evidence grade).

    target=None     → corpus-level summary across all sources/.
    target=<slug>   → per-file Rubric output for that single source.
    fix             → no-op (semantic migration is not script-fixable).
    """
    if not SOURCES_DIR.is_dir():
        print(f"ERROR: {SOURCES_DIR} not found.", file=sys.stderr)
        return 2

    if target:
        slug = target.removesuffix(".md")
        path = SOURCES_DIR / f"{slug}.md"
        if not path.is_file():
            print(f"ERROR: source file not found: {path}", file=sys.stderr)
            return 2
        content = path.read_text(encoding="utf-8", errors="replace")
        rel = f"sources/{slug}.md"
        result = _evaluate(rel, content)
        _print_per_file(result)
        # T1 tags hard gate — unconditional (like filename kebab).
        if not result["t1"][0]:
            print(
                f"\n  [Hard fail] empty frontmatter tags (T1) — source.md authoring standard "
                f"'fill tags'. For candidates see `python tools/_ingest/suggest_tags.py "
                f"--file {path}`."
            )
            return 1
        # Sc1 scraped hard gate — unconditional (weekly-briefing collection-week aggregation key).
        if not result["sc1"][0]:
            print(
                f"\n  [Hard fail] missing/invalid frontmatter `scraped` (Sc1) — source.md "
                f"schema 'scraped: YYYY-MM-DD' (raw `created` collection date). It is the weekly-briefing "
                f"aggregation key, so if missing the source drops out of that week's roster."
            )
            return 1
        if any(not result[k][0] for k in REQUIRED_KEYS):
            if slug in INTRINSICALLY_UNFIXABLE_SOURCES:
                print(
                    "\n  [Whitelist] permanent residual (INTRINSICALLY_UNFIXABLE_SOURCES) "
                    "— REQUIRED_KEYS fail surfaced as advisory only."
                )
                return 0
            return 1
        return 0

    # Corpus-level scan.
    results = []
    bad_filenames = []
    for path in real_source_files():
        if not SLUG_KEBAB_RE.match(path.name[:-3]):
            bad_filenames.append(path.name)
        content = path.read_text(encoding="utf-8", errors="replace")
        rel = f"sources/{path.name}"
        results.append(_evaluate(rel, content))

    _print_corpus_summary(results)

    # Filename convention (HARD fail, unconditional — see SLUG_KEBAB_RE).
    if bad_filenames:
        print(
            f"\n  [Hard fail] {len(bad_filenames)} source filename(s) not "
            f"lowercase kebab-case (.claude/policies/naming.md 'Source slugs'). "
            f"Rename to `[a-z0-9-]` — non-kebab slugs silently break "
            f"wikilinks/orphans across referencing hubs:"
        )
        for name in bad_filenames[:20]:
            print(f"    {name}")
        return 1
    print(
        f"  OK - source filenames lowercase kebab-case "
        f"({len(results)} files)"
    )

    # T1 tags hard gate (HARD fail, unconditional) — empty/missing
    # frontmatter tags. Closes the enforcement gap that let 110 `tags: []` sources
    # accumulate. tags is semantic (no auto-fix) → suggest_tags.py surfaces candidates.
    empty_tags = [r for r in results if not r["t1"][0]]
    if empty_tags:
        print(
            f"\n  [Hard fail] {len(empty_tags)} source(s) with empty/missing "
            f"frontmatter tags (T1) — source.md authoring standard 'fill tags'. The deployed graph "
            f"browser consumes them as node badges, so an empty value means unfinished authoring. For candidates: "
            f"`python tools/_ingest/suggest_tags.py --file wiki/sources/<slug>.md`:"
        )
        for r in empty_tags[:20]:
            print(f"    {r['rel'].removeprefix('sources/').removesuffix('.md')}")
        if len(empty_tags) > 20:
            print(f"    ... and {len(empty_tags) - 20} more")
        return 1
    print(f"  OK - source tags non-empty ({len(results)} files) [T1]")

    # Sc1 scraped hard gate (HARD fail, unconditional) — missing/invalid
    # frontmatter `scraped`. It is the weekly-briefing collection-week aggregation key (committed), so a missing value drops that week.
    missing_scraped = [r for r in results if not r["sc1"][0]]
    if missing_scraped:
        print(
            f"\n  [Hard fail] {len(missing_scraped)} source(s) missing/invalid "
            f"frontmatter `scraped` (Sc1) — source.md schema 'scraped: YYYY-MM-DD'"
            f"(raw `created` collection date). The weekly-briefing aggregation key:"
        )
        for r in missing_scraped[:20]:
            print(f"    {r['rel'].removeprefix('sources/').removesuffix('.md')}")
        if len(missing_scraped) > 20:
            print(f"    ... and {len(missing_scraped) - 20} more")
        return 1
    print(f"  OK - source scraped present ({len(results)} files) [Sc1]")

    failing = [
        r for r in results
        if any(not r[k][0] for k in REQUIRED_KEYS)
    ]
    def _slug_of(r: dict) -> str:
        return r["rel"].removeprefix("sources/").removesuffix(".md")
    whitelisted = [r for r in failing if _slug_of(r) in INTRINSICALLY_UNFIXABLE_SOURCES]
    whitelisted_slugs = {_slug_of(r) for r in whitelisted}
    unwhitelisted = [r for r in failing if _slug_of(r) not in whitelisted_slugs]
    if whitelisted:
        print(
            f"\n  [Whitelist] {len(whitelisted)} permanent residual "
            f"(INTRINSICALLY_UNFIXABLE_SOURCES, policy: "
            f".claude/policies/naming.md 'entity-addition threshold'). Excluded from "
            f"ACCEPTABLE_FAILS threshold — surfaced as advisory only."
        )
    if len(unwhitelisted) > ACCEPTABLE_FAILS:
        print(
            f"\n  [Hard fail] {len(unwhitelisted)} new non-compliant sources "
            f"exceeds ACCEPTABLE_FAILS={ACCEPTABLE_FAILS} (whitelist excluded). "
            f"Resolve regressions before merging — see Source Page Format in CLAUDE.md."
        )
        return 1
    if unwhitelisted:
        print(
            f"\n  [Advisory] {len(unwhitelisted)}/{ACCEPTABLE_FAILS} natural-"
            f"accumulation margin used — review for stub-threshold promotion "
            f"or whitelist registration."
        )
    return 0
