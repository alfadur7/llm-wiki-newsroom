"""Conflict axis lint — `wiki/contradictions/<theme>.md` (L2-3).

Extracted from the former `content_schema.py` monolith during the lint
group refactor (2026-04-19). Owns every check and mutation against
theme MD files:

  * MD schema       — frontmatter + required H2 sections; placeholder
                      insertion for missing H2s. Theme MDs have no AUTO
                      blocks by design (see CLAUDE.md "Theme Contradiction
                      Format" — internal management info stays in the
                      program-layer JSONs, not in reader pages).
  * Legacy AUTO     — detect + strip leftover `<!-- AUTO:CLAIMS/SOURCES
                      BEGIN/END -->` blocks from files authored before
                      the AUTO-removal refactor (2026-04-20). `--fix`
                      performs the strip non-destructively.
  * JSON ↔ MD map   — every theme slug declared in
                      `_contradictions_themes.json` has a matching MD;
                      every MD is declared in the JSON. The JSON is SoT
                      for "which themes exist", so divergence indicates
                      MD staleness — `--fix` auto-creates skeletons for
                      JSON-only slugs.
  * Drift (info)    — MD frontmatter `sources:` vs the source-set
                      implied by the theme's `claim_ids` (informational
                      only — signals editorial `sources:` staleness).

JSON-internal validity (schema, claim id existence, coverage, Phase 2
bounds, Freshness vs `_contradictions.json`) lives in the sibling
`contradiction_theme.py` module and is not duplicated here.

Axis pairing: the landscape axis equivalent lives in `overview.py`.

L2-4 aggregate (`wiki/contradiction.md`) Rubric + drill-down verification
lives in `_check_contradictions_md` (the `aggregate` target scope of `run()`).
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date as _date, datetime as _datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import AUTO_BLOCK_RE, CLUSTERS_JSON, REPO_ROOT, WIKI, WIKILINK_TARGET_RE, atomic_write_text, confirm_changes, parse_frontmatter, print_delete_cleanup_advisory, read_source_date, real_source_files, safe_slug_path, section_body, slug_only, strip_frontmatter  # noqa: E402
from _advisory_common import mark  # noqa: E402
from _manifest_counts import _load_manifest, counts as _roster_counts, threshold_label  # noqa: E402

import importlib.util as _ilu  # noqa: E402


def _load_skill_checks(name: str, alias: str):
    """Load `.claude/skills/<name>/checks.py` as a standalone module.

    Spec-loaded (not registered in sys.modules) — `alias` only namespaces
    the spec so the four skill loads below cannot collide.
    """
    spec = _ilu.spec_from_file_location(
        alias, REPO_ROOT / ".claude" / "skills" / name / "checks.py"
    )
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_MANIFEST = _load_manifest()

# theme cit.* (L2·L3·L4) measurement is owned by the scholarly-citation skill.
# Call configuration comes from the manifest SoT (`contradiction-theme.bundles`).
# Wiki-wide (sources_dir) and shared parsing (claim_sources·evidence_slugs)
# are injected by the orchestrator.
cit_skill = _load_skill_checks("scholarly-citation", "cit_checks_contra")
_CIT_CONTRA_FN = _MANIFEST["contradiction-theme"]["bundles"]["scholarly-citation"]["fn"]

# theme enc.* (N4·N5·N6·N7·W1·L1·X2) measurement is owned by the encyclopedia-writing skill.
enc_skill = _load_skill_checks("encyclopedia-writing", "enc_checks_contra")
_ENC_CONTRA_FN = _MANIFEST["contradiction-theme"]["bundles"]["encyclopedia-writing"]["fn"]

# theme jrn.* (T4·D1·D5·D6 — Toulmin qualifier·Hegelian dialectic) measurement is owned by the journalism-writing skill.
jrn_skill = _load_skill_checks("journalism-writing", "jrn_checks_contra")
_JRN_CONTRA_FN = _MANIFEST["contradiction-theme"]["bundles"]["journalism-writing"]["fn"]

# aggregate MECE(D1) measurement is owned by the consulting-writing skill.
con_skill = _load_skill_checks("consulting-writing", "con_checks_contra")
# aggregate bundle fn names (contradiction-aggregate content-type)
_AGG = _MANIFEST["contradiction-aggregate"]["bundles"]
_AGG_CON_FN = _AGG["consulting-writing"]["fn"]
_AGG_ENC_FN = _AGG["encyclopedia-writing"]["fn"]
_AGG_JRN_FN = _AGG["journalism-writing"]["fn"]

sys.path.insert(0, str(Path(__file__).parent))
from _editor_date import git_head_text  # noqa: E402
from _schema_common import (  # noqa: E402
    check_frontmatter,
    section_present as _section_present,
)
from contradiction_theme import (  # noqa: E402
    _print_rewrite_block as _print_theme_rewrite_block,
    is_themes_json_stale,
)

CONTRADICTIONS_DIR = WIKI / "contradictions"
CONTRADICTIONS_MD_PATH = WIKI / "contradiction.md"
THEMES_JSON = CONTRADICTIONS_DIR / "_contradictions_themes.json"
CLAIMS_JSON = CONTRADICTIONS_DIR / "_contradictions.json"
# CLUSTERS_JSON (X2/F1 input) is imported from _lib — repo-root anchored, so
# X2/F1 no longer silently degrade when lint runs from a non-root cwd.

# Module-level chain-pending flag. Set when `run(fix=True)` detects that
# `_contradictions_themes.json` is stale relative to `_contradictions.json`
# and emits the rewrite block. `tools/lint.py` reads this via
# `chain_pending_reason()` after `all --fix --yes` completes so the final
# SUMMARY can elevate the signal beyond a plain `[FAIL]` (Claude must
# execute the rewrite block before any other lint/build action).
#
# 2026-04-30: introduced after a Claude session demoted the rewrite block
# to a "remaining work" item in lint-report.md instead of executing the
# emitted Phase 1·2 chain — `--yes` flag was supposed to be the explicit
# opt-in for chain execution. The signal here makes that contract
# enforceable at the SUMMARY layer.
_CHAIN_PENDING_REASON: str | None = None


def chain_pending_reason() -> str | None:
    """Return chain-pending reason string, or None if no chain action is required.

    Read by `tools/lint.py _run_all` after the contradiction group finishes
    to emit a CHAIN-REQUIRED summary line + non-zero exit code distinct
    from a generic FAIL.
    """
    return _CHAIN_PENDING_REASON


def _set_chain_pending(reason: str) -> None:
    """Internal: mark module as chain-pending. Idempotent — first reason wins."""
    global _CHAIN_PENDING_REASON
    if _CHAIN_PENDING_REASON is None:
        _CHAIN_PENDING_REASON = reason

CONTRADICTION_REQUIRED_FRONTMATTER = {"title", "type", "last_updated"}
CONTRADICTION_REQUIRED_SECTIONS = ("## Opposing Positions", "## Representative Evidence", "## Derived Tensions & Generational Readings", "## Interpretive Direction")

# L2-4 aggregate — `wiki/contradiction.md` required sections (Part 2 Rubric S1).
AGGREGATE_REQUIRED_SECTIONS = ("## Synopsis", "## Per-Theme Deep Analysis", "## Implications", "## Source References")

# Rubric thresholds — see .claude/layers/contradiction.md Part 1
W1_MIN_LINKS = 30
S2_EVIDENCE_MIN = 3
S2_EVIDENCE_MAX = 7
X1_SOURCE_COVERAGE_MIN_RATIO = 0.7
N4_REUSE_MAX = 2
N5_VERDICT_FAIL_MAX = 2
N6_NUMBER_REUSE_MAX = 2
S3_LEAD_NUMBERS_MAX = 4
S3_LEAD_WIKILINKS_MAX = 5
# L1 (raw-slug length) threshold lives with the L1 measurement in the
# encyclopedia-writing skill's checks.py (L1_MIN_SLUG_LEN).

# Rubric Part 2 (Aggregate) thresholds — `.claude/layers/contradiction.md` Part 2
L24_W1_MIN = 50
L24_S2_INSIGHTS_MIN = 3
# D1 (axis-count range) threshold lives with the D1 measurement in the
# consulting-writing skill's checks.py (AXES_MIN/AXES_MAX) — consumed via
# the bundle's d1_ok/axes_min/axes_max return values.
L24_D3_BALANCE_MAX = 4.0

# S2 — `## Implications` bullet count. Bold labels emphasized with numbered markers (①②③…⑩).
L24_INSIGHT_BULLET_RE = re.compile(r"\*\*[①②③④⑤⑥⑦⑧⑨⑩]")

# F2 — head-matter statistics matching regex. Extracts the actual figures
# from the head-matter sentence patterns "**N source-to-source contradictions**"
# + "M topic clusters" and compares them against the JSON aggregate.
L24_CLAIMS_STAT_RE = re.compile(r"\*\*(\d+(?:,\d{3})*)\s*source-to-source contradictions?\*\*")
L24_THEMES_STAT_RE = re.compile(r"(\d+)\s*topic (?:clusters?|categories|themes?)")

# The D1 (axis detection) and D2 (theme link format) measurement regexes moved
# to the aggregate craft modules — consulting-writing (AXIS_SUBSECTION_RE) and
# encyclopedia-writing (L24_THEME_REF_RE).

# The N5 (assertive prescription vocabulary), T4 (scope qualifier), and N7
# (faction-label value words) lexicons moved to craft measurement —
# encyclopedia-writing (N5·N7) and journalism-writing (T4) checks.py own them.

# Bold-label matching for the `## Opposing Positions` position labels, used only
# to locate where the lead paragraph ends (the consumer uses `.start()`, not the
# captured groups — the extra named groups in the skill's regex are harmless here).
# Single SoT: the enc skill owns the A/B/C label grammar (was a drifted local
# copy here); consume it directly so the copies cannot diverge.
DIALECTIC_LABEL_RE = enc_skill.DIALECTIC_LABEL_RE


# N6 — numeric token regex. Counts **only measurements that carry a unit** so
# that timestamp/context tokens like year, month, day, and ordinal numbers are
# not misdetected as N6. Independent of source-slug reuse (N4), this counts the
# document-wide recurrence of surface numeric figures (reader-review lens 3 —
# "the same five facts keep coming back").
#
# MATCH examples: `19%`, `1,300억`, `13시간`, `2,800억 달러`, `3,000억 원`,
#           `94%`, `2조`, `300만 명`, `15배`, `135조 원`
# EXCLUDE examples: `2024년`, `3월`, `17일`, `2030` (bare year), `10대` (no unit)
#
# Time units (`년`·`월`·`일`·`시`·`분`·`초`) are deliberately excluded — these are
# timestamps, not "core measurements". `시간` (duration) is included instead (`13시간 장애`).
# Single SoT: the enc skill owns the N6 number-token lexicon (was a drifted second
# copy here); consume it directly so the two cannot diverge.
NUMBER_TOKEN_RE = enc_skill.NUMBER_TOKEN_RE
N6_MIN_TOKEN_LEN = 3  # A unit-bearing token of 2 chars or fewer is not meaningful. Safety guard.


# G1·G2 — Phase 2 source schema meta-use (dimension 6).
# Measurement (count_grade_meta·count_cite_type_meta) is owned by the
# scholarly-citation skill (migrated from legacy _contradiction_meta_patterns).
# theme, aggregate, and cluster overview share the same craft functions for
# metric consistency. The threshold VALUE is injected from manifest checks.
_G1_THRESHOLD = _MANIFEST["contradiction-theme"]["checks"]["cit.grade-meta"]["threshold"]            # =2
_G2_THRESHOLD = _MANIFEST["contradiction-theme"]["checks"]["cit.cite-type-meta"]["threshold"]        # =1
_L24_G1_THRESHOLD = _MANIFEST["contradiction-aggregate"]["checks"]["cit.grade-meta"]["threshold"]    # =2
_L24_G2_THRESHOLD = _MANIFEST["contradiction-aggregate"]["checks"]["cit.cite-type-meta"]["threshold"]  # =1



WIKILINK_RE = WIKILINK_TARGET_RE  # captures the target (including #anchor) — _slug_only normalizes it


_slug_only = slug_only  # shared _lib helper (was a local copy — see WIKILINK_RE note above)

# Match a full `<!-- AUTO:<NAME> BEGIN -->...<!-- AUTO:<NAME> END -->` block
# for any NAME. Used to strip legacy blocks left over from the pre-2026-04-20
# build pipeline that mirrored claim data into theme MDs.
LEGACY_AUTO_BLOCK_RE = re.compile(
    r"<!--\s*AUTO:(\w+)\s*BEGIN\s*-->.*?<!--\s*AUTO:\1\s*END\s*-->",
    re.DOTALL,
)

# Strip the legacy `## Sources` H2 heading whenever it appears with no
# bullet content underneath. Earlier versions only matched the EOF case
# (post-AUTO-block strip), but the same heading also surfaces orphaned
# mid-file when LEGACY_AUTO_BLOCK_RE removed an AUTO:SOURCES block whose
# next sibling was another H2. The regex now matches `## Sources` followed
# only by whitespace through to the next H2 boundary or EOF.
# No re.MULTILINE: with it, `$` in the lookahead matched before ANY newline,
# so a populated `## Sources` heading followed by a blank line was silently
# deleted during --fix. `\Z` keeps the match anchored to true EOF.
LEGACY_SOURCES_HEADING_RE = re.compile(
    r"\n##\s+Sources\s*\n+(?=##\s|\s*\Z)"
)

# Per-section TODO placeholder inserted by --fix when a required H2 is
# missing. Mirrors the overview.py skeleton pattern — body content
# restoration remains a Claude/editor responsibility. The placeholder
# keeps schema lint passing while clearly flagging the content gap for
# later authoring.
SECTION_PLACEHOLDER = {
    "## Opposing Positions": "_TODO: 2-3 paragraphs. Describe which factions claim what and where they clash. Position A / Position B (+ optional mediating Position C)._",
    # Use backtick-wrapped `[[source-slug]]` so the structure lint treats it
    # as inline code (not a wikilink). Placeholder text must never trigger
    # downstream "broken link" detection.
    "## Representative Evidence": "_TODO: List evidence sources — vendor data, independent research, field cases, etc. — in_ `[[source-slug]]` _format._",
    "## Derived Tensions & Generational Readings": "_TODO: Secondary debates flowing from the conflict, shifts in interpretation over time, and differences in viewpoint across generations and factions._",
    "## Interpretive Direction": "_TODO: Editorial assessment, domain implications, and follow-up monitoring points._",
}


def _skeleton_theme(slug: str, name: str) -> str:
    """Skeleton template for a new wiki/contradictions/<slug>.md file.

    Triggered by --fix when the JSON declares a theme slug whose MD does
    not exist. Body content (the four H2 sections) stays as TODO
    placeholders; Claude/editor authors them in a separate pass.

    No AUTO blocks — theme MDs are pure editorial content by design.
    """
    today = _date.today().isoformat()
    return (
        f"---\n"
        f"title: \"{name}\"\n"
        f"type: contradiction\n"
        f"tags: []\n"
        f"sources: []\n"
        f"last_updated: {today}\n"
        f"---\n\n"
        f"# {name}\n\n"
        f"## Opposing Positions\n\n"
        f"{SECTION_PLACEHOLDER['## Opposing Positions']}\n\n"
        f"## Representative Evidence\n\n"
        f"{SECTION_PLACEHOLDER['## Representative Evidence']}\n\n"
        f"## Derived Tensions & Generational Readings\n\n"
        f"{SECTION_PLACEHOLDER['## Derived Tensions & Generational Readings']}\n\n"
        f"## Interpretive Direction\n\n"
        f"{SECTION_PLACEHOLDER['## Interpretive Direction']}\n"
    )


def _strip_legacy_auto_blocks(content: str) -> tuple[str, list[str]]:
    """Remove any `<!-- AUTO:<NAME> BEGIN -->...END -->` block from the
    file content, plus a trailing `## Sources` heading orphaned by the
    AUTO:SOURCES strip.

    Returns (new_content, stripped_names).
    stripped_names is ordered by position for stable reporting.
    """
    stripped: list[str] = []

    def _record_and_erase(match: re.Match[str]) -> str:
        stripped.append(match.group(1))
        return ""

    new_content = LEGACY_AUTO_BLOCK_RE.sub(_record_and_erase, content)
    new_content = LEGACY_SOURCES_HEADING_RE.sub("\n", new_content)
    # Collapse triple+ blank lines introduced by strip
    new_content = re.sub(r"\n{3,}", "\n\n", new_content).rstrip() + "\n"
    return new_content, stripped


def _load_themes_json() -> tuple[dict | None, str | None]:
    if not THEMES_JSON.exists():
        return None, f"{THEMES_JSON} not found — run `/wiki-lint contradiction theme --fix`"
    try:
        data = json.loads(THEMES_JSON.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return None, f"{THEMES_JSON}: top-level must be object"
        return data, None
    except json.JSONDecodeError as e:
        return None, f"{THEMES_JSON}: invalid JSON — {e}"


def _load_claims_json() -> list[dict]:
    if not CLAIMS_JSON.exists():
        return []
    try:
        data = json.loads(CLAIMS_JSON.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def _md_theme_slugs() -> set[str]:
    if not CONTRADICTIONS_DIR.exists():
        return set()
    return {
        p.stem for p in CONTRADICTIONS_DIR.glob("*.md")
        if not p.name.startswith("_")
    }


def _insert_missing_sections(content: str, missing: list[str]) -> tuple[str, list[str]]:
    """Insert `## <section>` + TODO placeholder for each missing required section.

    Sections are appended in CONTRADICTION_REQUIRED_SECTIONS order,
    placed at the end of the document. If a legacy AUTO marker block is
    still present (pre-migration files), insert BEFORE it so the AUTO
    block stays flagged by the legacy-migration check until stripped.
    """
    inserted: list[str] = []
    new_content = content
    auto_match = re.search(r"<!--\s*AUTO:\w+\s*BEGIN\s*-->", new_content)
    anchor = auto_match.start() if auto_match else len(new_content.rstrip())

    blocks: list[str] = []
    for sec in CONTRADICTION_REQUIRED_SECTIONS:
        if sec in missing:
            placeholder = SECTION_PLACEHOLDER.get(sec, "_TODO: ..._")
            blocks.append(f"{sec}\n\n{placeholder}")
            inserted.append(sec)

    if not blocks:
        return content, []

    insertion = "\n\n" + "\n\n".join(blocks) + "\n\n"
    new_content = new_content[:anchor].rstrip() + insertion + new_content[anchor:].lstrip()
    return new_content, inserted


def _load_cluster_slugs() -> set[str]:
    """Cluster slug SoT (`graph/_clusters.json`) for X2 landscape back-ref.

    Absent file → empty set (X2 silently degrades rather than aborting the
    Rubric pass; build the graph first to enable X2).
    """
    if not CLUSTERS_JSON.exists():
        return set()
    try:
        data = json.loads(CLUSTERS_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    return {c["slug"] for c in data.get("clusters", []) if isinstance(c, dict) and "slug" in c}


def _load_source_slugs() -> set[str]:
    """Source slug SoT — filenames under `wiki/sources/`.

    Used to filter N4 (reuse_max) and S2 (evidence slugs) so they only
    count citations of source pages. Entity/concept wikilinks recur
    naturally via attribution and are not what Rubric N4 targets.
    Enumeration delegates to `_lib.real_source_files()` (the single SoT
    for the `_`-prefix exclusion).
    """
    return {p.stem for p in real_source_files()}



def _extract_section(content: str, heading: str) -> str:
    """Return body text between `## <heading>` and the next H2 (or EOF).

    Prefix match: the section line may carry a parenthetical subtitle
    (e.g. `## Per-Theme Deep Analysis (12 + 기타)`) — heading match requires
    only that the H2 line *starts* with `## <heading>` after whitespace.
    Delegates to the shared `_lib.section_body` extractor.
    """
    return section_body(content, heading, prefix=True)


def _claims_by_id(claims: list[dict]) -> dict[str, dict]:
    """Claim-record index keyed by `id` — single definition for the sites
    that resolve claim_ids against `_contradictions.json` records."""
    return {c["id"]: c for c in claims if isinstance(c, dict) and "id" in c}


def _sources_for_claim_ids(claim_ids: list, by_id: dict[str, dict]) -> set[str]:
    """Resolve claim ids to the unique source stems their records cite."""
    stems: set[str] = set()
    for cid in claim_ids:
        rec = by_id.get(cid)
        if not rec:
            continue
        stem = rec.get("source", "").removeprefix("sources/").removesuffix(".md")
        if stem:
            stems.add(stem)
    return stems


def _source_coverage(
    body: str,
    theme_slug: str,
    themes_doc: dict,
    claims: list[dict],
) -> tuple[int, int, set[str]]:
    """X1 — (source_refs, total_sources, claim_source_set) for this theme.

    Denominator = unique source set derived from theme claim_ids (SoT
    deterministic). Numerator = count of those sources whose slug
    appears as a substring in body. Substring matching is deliberate
    — it matches both raw `[[slug]]` and aliased `[[slug|한글]]`
    forms without reparsing.

    Per Rubric X1 (option A — Cite depth, simple ratio threshold 0.7):
    measures the fraction of theme's claim source pool that is
    actually cited in body. Threshold is a simple ratio (no
    max(3, ...) absolute floor — small themes use the same ratio).
    Returns the claim-source set so L2 Cite consistency check can
    reuse it.
    """
    themes = themes_doc.get("themes", {})
    theme_obj = themes.get(theme_slug)
    if not isinstance(theme_obj, dict):
        return 0, 0, set()
    claim_ids = theme_obj.get("claim_ids") or []

    claim_sources = _sources_for_claim_ids(claim_ids, _claims_by_id(claims))

    total = len(claim_sources)
    if total == 0:
        return 0, 0, claim_sources

    refs = sum(1 for s in claim_sources if s in body)
    return refs, total, claim_sources


def _rubric_metrics(
    path: Path,
    theme_slug: str,
    themes_doc: dict,
    claims: list[dict],
    cluster_slugs: set[str],
    source_slugs: set[str],
) -> dict:
    """Compute Rubric Part 1 metrics for a single theme MD.

    Returns a dict keyed by the Rubric criterion code so the formatter
    can render the advisory line and downstream callers (e.g. future
    CI thresholds) can consume individual values.
    """
    content = path.read_text(encoding="utf-8")
    body = strip_frontmatter(content)

    # S1 — 4 H2 + TODO 0. Line-start prefix match (same logic as the
    # aggregate path): rejects in-body prose mentions but allows suffix
    # variants on the heading line.
    sections_present = sum(
        1 for s in CONTRADICTION_REQUIRED_SECTIONS
        if re.search(rf"^{re.escape(s)}", body, re.MULTILINE)
    )
    todo_count = len(re.findall(r"_TODO:", body))

    # Opposing-positions section — shared by jrn dialectic (D1/D5/D6), enc N7, and S3. Extracted by the orchestrator.
    conflict_section = _extract_section(body, "Opposing Positions")

    # S2 — evidence bullets inside `## Representative Evidence`
    evidence_section = _extract_section(body, "Representative Evidence")
    evidence_bullets = [
        line for line in evidence_section.splitlines()
        if re.match(r"^\s*-\s+", line)
    ]
    # Count one `[[...]]` per bullet as "a piece of evidence" — a bullet citing
    # multiple sources still counts as one evidence item; the slug-unique
    # check below catches low-diversity padding.
    # Evidence bullet = bullet with ≥1 source-slug wikilink. Entity-only
    # bullets (no source citation) aren't "evidence" in the Rubric sense.
    evidence_slugs: set[str] = set()
    evidence_count = 0
    for b in evidence_bullets:
        bullet_sources: set[str] = set()
        for target in WIKILINK_RE.findall(b):
            stem = _slug_only(target)
            if not source_slugs or stem in source_slugs:
                bullet_sources.add(stem)
        if bullet_sources:
            evidence_count += 1
            evidence_slugs |= bullet_sources
    evidence_slug_count = len(evidence_slugs)

    # X1 — source coverage (Cite ratio, simple ≥0.7 threshold)
    source_refs, source_total, claim_sources = _source_coverage(
        body, theme_slug, themes_doc, claims,
    )
    # L2·L3·L4 — cit.* (cite consistency·evidence grounding·anchor) measurement
    # moved (verbatim) to the scholarly-citation skill. Shared parsing
    # (claim_sources·evidence_slugs) and wiki-wide (sources_dir) are injected by the orchestrator.
    fm = parse_frontmatter(content)
    fm_sources = fm.get("sources") or []
    _cit_contra = getattr(cit_skill, _CIT_CONTRA_FN)(
        body,
        fm_sources=fm_sources,
        claim_sources=claim_sources,
        evidence_slugs=evidence_slugs,
        source_slugs=source_slugs,
        sources_dir=WIKI / "sources",
    )

    # T4·D1·D5·D6 — jrn.* (Toulmin qualifier·Hegelian dialectic) measurement moved to the journalism-writing skill.
    _dialectic = getattr(jrn_skill, _JRN_CONTRA_FN)(body, conflict_section=conflict_section)

    # S3 — dialectic section lead paragraph density.
    # Lead = text from section start up to the first bold-label bullet or
    # the first blank line followed by a bullet, whichever comes first.
    lead_end_match = re.search(r"\n\s*\n\s*-\s+", conflict_section)
    label_start = DIALECTIC_LABEL_RE.search(conflict_section)
    candidates = []
    if lead_end_match:
        candidates.append(lead_end_match.start())
    if label_start:
        # Backtrack to start of the line containing the label
        line_start = conflict_section.rfind("\n", 0, label_start.start()) + 1
        candidates.append(line_start)
    lead_end = min(candidates) if candidates else len(conflict_section)
    lead_text = conflict_section[:lead_end]
    # Strip wikilinks for number counting to avoid slug-digit false positives,
    # but keep the original for wikilink counting.
    lead_text_no_links = WIKILINK_RE.sub("", lead_text)
    lead_nums = sum(
        1 for tok in NUMBER_TOKEN_RE.findall(lead_text_no_links)
        if len(tok.strip()) >= N6_MIN_TOKEN_LEN
    )
    lead_wikilinks = len(WIKILINK_RE.findall(lead_text))

    # G1·G2 — Phase 2 source schema meta-use (advisory, dimension 6).
    # Whole body (frontmatter excluded) — theme MDs have no AUTO blocks, so
    # body is used as-is. In the aggregate path this is called via a separate
    # EDITOR-only extraction function.
    g1_grade_meta = cit_skill.count_grade_meta(body)
    g2_cite_type_meta = cit_skill.count_cite_type_meta(body)

    # enc.* (W1·N4·N5·N6·N7·L1·X2) measurement moved to the encyclopedia-writing skill.
    # Shared sections (conflict was extracted at D1/D5), source_slugs, and cluster_slugs are injected.
    verdict_section = _extract_section(body, "Interpretive Direction")
    derived_section = _extract_section(body, "Derived Tensions & Generational Readings")
    _npov = getattr(enc_skill, _ENC_CONTRA_FN)(
        body,
        conflict_section=conflict_section,
        verdict_section=verdict_section,
        derived_section=derived_section,
        source_slugs=source_slugs,
        cluster_slugs=cluster_slugs,
    )

    return {
        "S1_sections": sections_present,
        "S1_todo": todo_count,
        **_npov,
        **_dialectic,
        "S2_evidence": evidence_count,
        "S2_slugs": evidence_slug_count,
        "S3_lead_nums": lead_nums,
        "S3_lead_wikilinks": lead_wikilinks,
        "X1_source_refs": source_refs,
        "X1_source_total": source_total,
        **_cit_contra,
        "G1_grade_meta": g1_grade_meta,
        "G2_cite_type_meta": g2_cite_type_meta,
    }


# ----- Claims drift detector + staleness advisory -----
# Parallels overview AUTO drift detector (tools/_lint/overview.py) but
# adapts to contradiction theme structure: theme MDs have no AUTO blocks,
# so drift is computed from JSON SoT — _contradictions_themes.json
# claim_ids + _contradictions.json claim records resolved to source dates.
#
# Thresholds tuned 2026-04-21 in parallel with overview drift:
#   - Jaccard/delta: same scale as overview (0.85 / 0.70, 15% / 30%)
#   - top5_new: tighter (1/4) since themes have fewer sources than clusters
#   - top5 ranking: recency PRIMARY (per user direction) — "most recent
#     editorially-relevant source" semantics. Count secondary, slug
#     tertiary for determinism (mirrors AUTO:SOURCES tie-breaker).
# Staleness is orthogonal to drift: detects themes that haven't received
# fresh claims in 180+ days regardless of whether the existing claims
# changed recently.

CLAIMS_DRIFT_JACCARD_STABLE = 0.85
CLAIMS_DRIFT_JACCARD_REWRITE = 0.70
CLAIMS_DRIFT_SOURCE_STABLE = 0.15
CLAIMS_DRIFT_SOURCE_REWRITE = 0.30
CLAIMS_DRIFT_TOP5_STABLE = 1
CLAIMS_DRIFT_TOP5_REWRITE = 4
CLAIMS_STALENESS_DAYS = 180  # 6 months — newest claim older than this → advisory

def _git_head_json(path: Path) -> object | None:
    """Return the JSON parsed from `git show HEAD:<path>`, or None if the
    file is new, removed, or unparseable. bytes capture + utf-8 replace
    decode for Windows cp949 compatibility."""
    text = git_head_text(path)
    if text is None:
        return None
    try:
        return json.loads(text)
    except ValueError:
        return None


def _theme_source_ranking(
    claim_ids: list[str], claims_by_id: dict[str, dict]
) -> list[tuple[str, int, str]]:
    """Resolve claim_ids to (source, claim_count, date) tuples, sorted
    by recency-primary three-stage stable cascade:
      1. tertiary: source slug asc (determinism)
      2. secondary: claim count desc (editorial weight among same-date)
      3. primary:   source date desc (newer first — "recency primary"
         per A path; captures surge of recent claims before they accumulate
         enough frequency to dominate)
    """
    from collections import Counter
    counts: Counter[str] = Counter()
    for cid in claim_ids:
        c = claims_by_id.get(cid)
        if c:
            counts[c.get("source", "")] += 1
    stats = [(src, n, read_source_date(src)) for src, n in counts.items() if src]
    stats.sort(key=lambda x: x[0])                 # tertiary: slug asc
    stats.sort(key=lambda x: x[1], reverse=True)   # secondary: count desc
    stats.sort(key=lambda x: x[2], reverse=True)   # primary: date desc
    return stats


def _claims_drift_line(
    theme_slug: str,
    current_themes_doc: dict,
    current_claims: list[dict],
    head_themes_doc: object,
    head_claims: object,
) -> str | None:
    """Compute per-theme drift vs git HEAD. Silent when theme is new,
    baseline missing, or all metrics sit in the 'stable' tier.
    """
    new_ids = set(current_themes_doc.get("themes", {}).get(theme_slug, {}).get("claim_ids", []))
    if not isinstance(head_themes_doc, dict):
        return None
    old_ids = set(head_themes_doc.get("themes", {}).get(theme_slug, {}).get("claim_ids", []))
    if not old_ids:
        return None  # new theme — no baseline

    if not isinstance(head_claims, list):
        return None

    # Jaccard on claim_id sets
    union = new_ids | old_ids
    jaccard = len(new_ids & old_ids) / len(union) if union else 1.0

    # Source sets resolved from claims
    new_by_id = _claims_by_id(current_claims)
    old_by_id = _claims_by_id(head_claims)

    new_sources = {new_by_id[i]["source"] for i in new_ids if i in new_by_id and new_by_id[i].get("source")}
    old_sources = {old_by_id[i]["source"] for i in old_ids if i in old_by_id and old_by_id[i].get("source")}

    old_n, new_n = len(old_sources), len(new_sources)
    delta = abs(new_n - old_n) / max(old_n, 1)

    # Recency-primary top-5
    new_top5 = [s for s, _, _ in _theme_source_ranking(list(new_ids), new_by_id)[:5]]
    old_top5 = set(s for s, _, _ in _theme_source_ranking(list(old_ids), old_by_id)[:5])
    top5_new = sum(1 for s in new_top5 if s not in old_top5)

    if (jaccard < CLAIMS_DRIFT_JACCARD_REWRITE
        or delta > CLAIMS_DRIFT_SOURCE_REWRITE
        or top5_new >= CLAIMS_DRIFT_TOP5_REWRITE):
        icon, note = "🔴", f"rewrite — recommend `/wiki-lint contradiction {theme_slug} --fix`"
    elif (jaccard < CLAIMS_DRIFT_JACCARD_STABLE
          or delta > CLAIMS_DRIFT_SOURCE_STABLE
          or top5_new > CLAIMS_DRIFT_TOP5_STABLE):
        icon, note = "🟡", "drift — recommend re-reviewing the representative evidence"
    else:
        return None

    sign = "+" if new_n >= old_n else "-"
    delta_str = f"{sign}{delta * 100:.0f}%"
    return (
        f"    [Claims drift] claim_jaccard={jaccard:.2f}  "
        f"source_delta={delta_str} (srcs {old_n}→{new_n})  "
        f"top5_new={top5_new}  {icon} {note}"
    )


def _claims_staleness_line(
    theme_slug: str,
    themes_doc: dict,
    claims_list: list[dict],
) -> str | None:
    """Check if the newest claim source date is older than CLAIMS_STALENESS_DAYS.
    Orthogonal to drift — fires regardless of whether claim_ids changed
    recently. Silent when theme has no claims or dates can't be resolved.
    """
    claim_ids = themes_doc.get("themes", {}).get(theme_slug, {}).get("claim_ids", [])
    if not claim_ids:
        return None
    claims_by_id = _claims_by_id(claims_list)
    newest = ""
    for cid in claim_ids:
        c = claims_by_id.get(cid)
        if not c:
            continue
        d = read_source_date(c.get("source", ""))
        if d > newest:
            newest = d
    if not newest:
        return None
    try:
        newest_date = _datetime.strptime(newest, "%Y-%m-%d").date()
    except ValueError:
        return None
    age = (_date.today() - newest_date).days
    if age <= CLAIMS_STALENESS_DAYS:
        return None
    return (
        f"    [Claims staleness] newest_claim={newest} ({age} days ago) ⚠️  "
        f"— no new material in {CLAIMS_STALENESS_DAYS // 30}+ months"
    )


def _format_metrics_line(m: dict, exempt: set[str] | None = None) -> list[str]:
    """Render Rubric metrics as advisory lines.

    `exempt` lists criteria codes whose PASS/FAIL mark should be replaced
    with a neutral `—` (e.g. D5 for `other-fragmentary`, which has no
    single dialectic axis).
    """
    exempt = exempt or set()

    def _mark(code: str, ok) -> str:
        if code in exempt:
            return "—"
        if ok is None:  # auto-exempt (e.g. L3 when no source has quote section)
            return "—"
        return mark(ok)

    s1_ok = m["S1_sections"] == len(CONTRADICTION_REQUIRED_SECTIONS) and m["S1_todo"] == 0
    w1_ok = m["W1_total"] >= W1_MIN_LINKS
    n4_ok = m["N4_reuse_max"] <= N4_REUSE_MAX
    n5_ok = m["N5_verdict_fails"] <= N5_VERDICT_FAIL_MAX
    n6_ok = m["N6_num_reuse_max"] <= N6_NUMBER_REUSE_MAX
    n7_ok = m["N7_label_skew"] == 0
    t4_ok = m["T4_qualifiers"] >= 1
    d1_ok = m["D1_labels"] >= 2
    c_w = m["D5_words"]["C"]
    ab_max = max(m["D5_words"]["A"], m["D5_words"]["B"])
    d5_ok = (c_w == 0) or (c_w <= ab_max and ab_max > 0)
    d6_ok = m["D6_c_meta_count"] == 0
    s2_ok = (
        S2_EVIDENCE_MIN <= m["S2_evidence"] <= S2_EVIDENCE_MAX
        and S2_EVIDENCE_MIN <= m["S2_slugs"] <= S2_EVIDENCE_MAX
    )
    s3_ok = (
        m["S3_lead_nums"] <= S3_LEAD_NUMBERS_MAX
        and m["S3_lead_wikilinks"] <= S3_LEAD_WIKILINKS_MAX
    )
    if m["X1_source_total"] > 0:
        x1_ratio = m["X1_source_refs"] / m["X1_source_total"]
        x1_ok = x1_ratio >= X1_SOURCE_COVERAGE_MIN_RATIO
    else:
        x1_ok = True  # theme with no claim sources — trivially PASS
    x2_ok = m["X2_landscape_refs"] >= 1
    l1_ok = m["L1_raw_slugs"] == 0
    l2_ok = m["L2_missing_count"] == 0
    # L3: PASS when at least 1 evidence source with quotes has ≥1 quote
    # grounded in body. Exempt (displayed as —) when no evidence source has
    # a `## Key Quotes` section (total_with_quotes == 0).
    if m["L3_total_with_quotes"] == 0:
        l3_ok = None  # exempt
    else:
        l3_ok = m["L3_grounded"] >= 1

    # G1·G2 — Phase 2 schema meta-use (advisory, dimension 6).
    # Thresholds: G1 ≥ 2 (grade meta), G2 ≥ 1 (citation-type meta).
    g1_ok = m["G1_grade_meta"] >= _G1_THRESHOLD
    g2_ok = m["G2_cite_type_meta"] >= _G2_THRESHOLD

    ab_str = f"A={m['D5_words']['A']}/B={m['D5_words']['B']}"
    d5_str = f"C={c_w}/{ab_str}"
    x1_pct = (m["X1_source_refs"] / m["X1_source_total"] * 100) if m["X1_source_total"] else 0
    x1_str = f"{m['X1_source_refs']}/{m['X1_source_total']} ({x1_pct:.0f}%)"
    s3_str = f"nums={m['S3_lead_nums']}/wiki={m['S3_lead_wikilinks']}"
    l3_str = f"{m['L3_grounded']}/{m['L3_total_with_quotes']}"

    lines = [
        f"    [Rubric] S1={m['S1_sections']}/4 todo={m['S1_todo']} {_mark('S1', s1_ok)}  "
        f"S2 evidence={m['S2_evidence']} slugs={m['S2_slugs']} {_mark('S2', s2_ok)}  "
        f"S3 lead {s3_str} {_mark('S3', s3_ok)}  "
        f"W1 links={m['W1_total']} {_mark('W1', w1_ok)}  "
        f"D1 labels={m['D1_labels']} {_mark('D1', d1_ok)}  "
        f"D5 {d5_str} {_mark('D5', d5_ok)}  "
        f"D6 C_meta={m['D6_c_meta_count']} {_mark('D6', d6_ok)}",
        f"    [Rubric] N4 reuse_max={m['N4_reuse_max']} {_mark('N4', n4_ok)}  "
        f"N5 verdict_fails={m['N5_verdict_fails']} {_mark('N5', n5_ok)}  "
        f"N6 num_reuse_max={m['N6_num_reuse_max']} {_mark('N6', n6_ok)}  "
        f"N7 label_skew={m['N7_label_skew']} {_mark('N7', n7_ok)}  "
        f"T4 qualifiers={m['T4_qualifiers']} {_mark('T4', t4_ok)}",
        f"    [Rubric] X1 source_refs={x1_str} {_mark('X1', x1_ok)}  "
        f"X2 landscape={m['X2_landscape_refs']} {_mark('X2', x2_ok)}  "
        f"L1 raw_slugs={m['L1_raw_slugs']} {_mark('L1', l1_ok)}  "
        f"L2 cite_miss={m['L2_missing_count']} {_mark('L2', l2_ok)}  "
        f"L3 grounded={l3_str} {_mark('L3', l3_ok)}",
        f"    [Rubric] G1 grade_meta={m['G1_grade_meta']} {_mark('G1', g1_ok)}  "
        f"G2 cite_type_meta={m['G2_cite_type_meta']} {_mark('G2', g2_ok)}",
    ]
    if m["N4_top"] and m["N4_reuse_max"] > N4_REUSE_MAX:
        top_str = ", ".join(f"{stem}×{n}" for stem, n in m["N4_top"] if n > N4_REUSE_MAX)
        if top_str:
            lines.append(f"    [Rubric] N4 over-reused slugs: {top_str}")
    if m["N6_top"] and m["N6_num_reuse_max"] > N6_NUMBER_REUSE_MAX:
        top_str = ", ".join(
            f'"{tok}"×{n}' for tok, n in m["N6_top"] if n > N6_NUMBER_REUSE_MAX
        )
        if top_str:
            lines.append(f"    [Rubric] N6 over-reused figures: {top_str}")
        # advisory hint — recurrence in the `## Derived Tensions & Generational Readings`
        # section plus the absence of a time-axis keyword suggests possible "re-invoking
        # the same fact from the same angle". No effect on hard FAIL (advisory message
        # only). Pairs with the guide's Rubric N6 cue.
        if m["N6_derived_reused_tokens"] and not m["N6_derived_has_transition"]:
            tok_str = ", ".join(f'"{t}"' for t in m["N6_derived_reused_tokens"][:3])
            lines.append(
                f"    [Advisory] N6 derived-section reuse without transition: "
                f"{tok_str} (no time-axis or context-transition keyword — qualitative review recommended)"
            )
    if "N7" not in exempt and m["N7_label_skew"] == 1:
        a_words = m["N7_label_words"]["A"]
        b_words = m["N7_label_words"]["B"]
        lines.append(
            f"    [Rubric] N7 label value-words: A={a_words}, B={b_words}"
        )
    if "D6" not in exempt and m["D6_c_meta_count"] > 0:
        lines.append(
            f"    [Rubric] D6 C meta-critique keywords: {m['D6_c_meta_hits']}"
        )
    if "S3" not in exempt and not (
        m["S3_lead_nums"] <= S3_LEAD_NUMBERS_MAX
        and m["S3_lead_wikilinks"] <= S3_LEAD_WIKILINKS_MAX
    ):
        lines.append(
            f"    [Rubric] S3 lead over-limits: nums={m['S3_lead_nums']}"
            f"/max={S3_LEAD_NUMBERS_MAX}, wikilinks={m['S3_lead_wikilinks']}"
            f"/max={S3_LEAD_WIKILINKS_MAX}"
        )
    if m["L1_samples"]:
        lines.append(f"    [Rubric] L1 raw slug samples: {m['L1_samples']}")
    if m["L2_missing_count"] > 0:
        lines.append(
            f"    [Rubric] L2 missing from frontmatter: {m['L2_missing_slugs']}"
        )
    if m["L3_missing_grounding"]:
        lines.append(
            f"    [Rubric] L3 missing evidence grounding: {m['L3_missing_grounding']}"
        )
    # L4 advisory — Xanadu citation anchoring. Reported as informational
    # ratio "anchored/quoted" without ✅/❌ since migration is in progress.
    if m["L4_quoted_total"] > 0:
        lines.append(
            f"    [Advisory] L4 anchored quotes: {m['L4_anchored']}/{m['L4_quoted_total']}"
            + ("" if m["L4_anchored"] == m["L4_quoted_total"]
               else "  (Xanadu citation anchoring — see .claude/layers/contradiction.md)")
        )
        if m["L4_unanchored_samples"]:
            lines.append(
                f"    [Advisory] L4 unanchored bullets ({len(m['L4_unanchored_samples'])}): "
                f"{m['L4_unanchored_samples'][:2]}"
            )
    return lines


def _check_contradictions_md(
    theme_slugs: set[str],
    cluster_slugs: set[str],
    claim_count: int,
    non_fragmentary_theme_count: int,
) -> tuple[list[str], list[str]]:
    """Evaluate `wiki/contradiction.md` against the L2-4 Aggregate Rubric.

    Computes automatic indicators from Part 2 Rubric (17 criteria, 2026-04-20
    N5·N7 promotion):
      - Common (Part 1 inherited): N5 · N7 · T4 · S1 · S2 · W1 · W4 · X1
      - L2-4 only: D1 (number of tension axes) · D2 (drill-down alias) · D3
        (per-axis theme balance) · F1 (landscape-ref block) · F2 (head-matter
        statistics match)

    N5·N7 aggregate variants reuse the Part 1 lexicons owned by the
    encyclopedia-writing skill (checks.py) but target different sections:
      - N5 aggregate: `## Implications` section (Part 1 targets `## Interpretive Direction`)
      - N7 aggregate: `### <axis>` subsection titles under `## Per-Theme Deep
        Analysis` (Part 1 targets `**Position A (...)**` bold labels)

    Returns (issues, metrics_lines). Mirrors `overview._check_overview_md`
    pattern so `run(target="aggregate")` can consume the same shape.
    """
    issues: list[str] = []
    metrics_lines: list[str] = []

    if not CONTRADICTIONS_MD_PATH.exists():
        issues.append("  wiki/contradiction.md missing")
        return issues, metrics_lines

    content = CONTRADICTIONS_MD_PATH.read_text(encoding="utf-8")

    # S1 — required sections present (AGGREGATE_REQUIRED_SECTIONS).
    # Line-start prefix match: rejects in-body prose mentions (substring `in`
    # would falsely pass a quoted reference) but allows suffix variants like
    # `## Per-Theme Deep Analysis (10 + 기타)` per the same prefix rule applied by
    # `_extract_section`. Heading + everything-after-it on the same line is
    # treated as a single header for completeness purposes.
    sections_present = sum(
        1 for s in AGGREGATE_REQUIRED_SECTIONS
        if re.search(rf"^{re.escape(s)}", content, re.MULTILINE)
    )
    s1_ok = sections_present == len(AGGREGATE_REQUIRED_SECTIONS)

    # S2 — `## Implications` numbered bullets (①②③…)
    insights_section = _extract_section(content, "Implications")
    s2_insights = len(L24_INSIGHT_BULLET_RE.findall(insights_section))
    s2_ok = s2_insights >= L24_S2_INSIGHTS_MIN

    # W1 — total wikilinks (document-wide)
    all_links = WIKILINK_RE.findall(content)
    w1_count = len(all_links)
    w1_ok = w1_count >= L24_W1_MIN

    # X1 — every theme slug appears somewhere in body (pipe-aliased or raw)
    covered_themes: set[str] = set()
    for target in all_links:
        stem = _slug_only(target)
        if stem in theme_slugs:
            covered_themes.add(stem)
    x1_missing = sorted(theme_slugs - covered_themes)
    x1_ok = len(x1_missing) == 0

    # D1 — MECE axis grouping measurement moved to the consulting-writing skill.
    analysis_section = _extract_section(content, "Per-Theme Deep Analysis")
    _agg_con = getattr(con_skill, _AGG_CON_FN)(analysis_section)
    d1_axes = _agg_con["d1_axes"]
    axes_named = _agg_con["axes_named"]

    # F2 — head-matter statistics match JSON SoT.
    # Claim count stat: "**N source-to-source contradictions**" vs len(claims).
    # Theme count stat: "M topic clusters" vs the non-fragmentary theme count.
    claim_stat_match = L24_CLAIMS_STAT_RE.search(content)
    theme_stat_match = L24_THEMES_STAT_RE.search(content)
    f2_drift: list[str] = []
    if claim_stat_match:
        declared_claims = int(claim_stat_match.group(1).replace(",", ""))
        if declared_claims != claim_count:
            f2_drift.append(f"claims declared={declared_claims} actual={claim_count}")
    else:
        f2_drift.append("claims stat regex not matched")
    if theme_stat_match:
        declared_themes = int(theme_stat_match.group(1))
        if declared_themes != non_fragmentary_theme_count:
            f2_drift.append(
                f"themes declared={declared_themes} "
                f"actual={non_fragmentary_theme_count} (non-fragmentary)"
            )
    else:
        f2_drift.append("themes stat regex not matched")
    f2_ok = len(f2_drift) == 0

    # T4(jrn)·N5·N7·D2·D3·F1(enc) craft measurement moved to the skill bundles.
    # Shared parsing and axes_named (con D1 output) are injected by the orchestrator;
    # the _ok threshold decisions stay in the orchestrator.
    t4_qualifiers = getattr(jrn_skill, _AGG_JRN_FN)(insights_section=insights_section)["t4_qualifiers"]
    t4_ok = t4_qualifiers >= 1
    _agg_enc = getattr(enc_skill, _AGG_ENC_FN)(
        insights_section=insights_section,
        analysis_section=analysis_section,
        all_links=all_links,
        axes_named=axes_named,
        theme_slugs=theme_slugs,
        cluster_slugs=cluster_slugs,
    )
    insights_verdict_fails = _agg_enc["insights_verdict_fails"]
    n5_ok = insights_verdict_fails <= N5_VERDICT_FAIL_MAX
    axis_skew_hits = _agg_enc["axis_skew_hits"]
    n7_skew = _agg_enc["n7_skew"]
    n7_ok = n7_skew == 0
    d1_ok = _agg_con["d1_ok"]
    d2_total = _agg_enc["d2_total"]
    d2_aliased = _agg_enc["d2_aliased"]
    d2_raw = _agg_enc["d2_raw"]
    d2_ok = d2_total > 0 and len(d2_raw) == 0
    d3_max = _agg_enc["d3_max"]
    d3_min = _agg_enc["d3_min"]
    d3_ratio = _agg_enc["d3_ratio"]
    d3_ok = d3_ratio <= L24_D3_BALANCE_MAX
    f1_refs = _agg_enc["f1_refs"]
    f1_count = _agg_enc["f1_count"]
    f1_ok = f1_count == 0

    # Collect HARD issues (required failures); advisory goes to metrics line.
    if not s1_ok:
        missing_sections = [
            s for s in AGGREGATE_REQUIRED_SECTIONS
            if not re.search(rf"^{re.escape(s)}", content, re.MULTILINE)
        ]
        issues.append(
            f"  wiki/contradiction.md: S1 FAIL — missing required section(s): "
            f"{missing_sections}"
        )
    if not x1_ok:
        issues.append(
            f"  wiki/contradiction.md: X1 FAIL — {len(x1_missing)} theme(s) "
            f"missing from body: {x1_missing}"
        )
    if not d1_ok:
        issues.append(
            f"  wiki/contradiction.md: D1 FAIL — {d1_axes} named axes "
            f"(expected {_agg_con['axes_min']}~{_agg_con['axes_max']}): {axes_named}"
        )
    if not d2_ok:
        if d2_total == 0:
            issues.append(
                "  wiki/contradiction.md: D2 FAIL — no theme references "
                "detected in `## Per-Theme Deep Analysis` section"
            )
        else:
            issues.append(
                f"  wiki/contradiction.md: D2 FAIL — {len(d2_raw)} theme "
                f"reference(s) missing pipe alias: {sorted(set(d2_raw))}"
            )
    if not f1_ok:
        issues.append(
            f"  wiki/contradiction.md: F1 FAIL — {f1_count} cluster-slug "
            f"reference(s) found (L2-4 forbids landscape refs): "
            f"{sorted(set(f1_refs))}"
        )
    if not f2_ok:
        issues.append(
            f"  wiki/contradiction.md: F2 FAIL — head-matter statistics "
            f"drift: {f2_drift}"
        )

    ok = mark
    metrics_lines.append("wiki/contradiction.md:")
    metrics_lines.append(
        f"  [Rubric L2-4] T4 qualifiers={t4_qualifiers} {ok(t4_ok)}  "
        f"S1 sections={sections_present}/{len(AGGREGATE_REQUIRED_SECTIONS)} {ok(s1_ok)}  "
        f"S2 insights={s2_insights} {ok(s2_ok)}  "
        f"W1 links={w1_count} {ok(w1_ok)}"
    )
    metrics_lines.append(
        f"  [Rubric L2-4] N5 verdict_fails={insights_verdict_fails} {ok(n5_ok)}  "
        f"N7 axis_skew={n7_skew} {ok(n7_ok)}"
    )
    x1_frag = f"{len(covered_themes)}/{len(theme_slugs)}"
    metrics_lines.append(
        f"  [Rubric L2-4] X1 theme_coverage={x1_frag} {ok(x1_ok)}  "
        f"D1 axes={d1_axes} {ok(d1_ok)}  "
        f"D2 alias={d2_aliased}/{d2_total} {ok(d2_ok)}  "
        f"D3 balance={d3_max}/{d3_min}={d3_ratio:.2f} {ok(d3_ok)}  "
        f"F1 cluster_refs={f1_count} {ok(f1_ok)}  "
        f"F2 stats={'drift' if f2_drift else 'ok'} {ok(f2_ok)}"
    )
    # G1·G2 — Phase 2 source schema meta-use (advisory, dimension 6 aggregate).
    # Applies to the entire EDITOR region of the aggregate body, outside any AUTO
    # block (AUTO_BLOCK_RE is the single SoT — see _lib; the aggregate currently
    # carries none, so this is a defensive strip).
    aggregate_editor = AUTO_BLOCK_RE.sub("", content)
    g1_grade_meta = cit_skill.count_grade_meta(aggregate_editor)
    g2_cite_type_meta = cit_skill.count_cite_type_meta(aggregate_editor)
    g1_ok = g1_grade_meta >= _L24_G1_THRESHOLD
    g2_ok = g2_cite_type_meta >= _L24_G2_THRESHOLD
    metrics_lines.append(
        f"  [Rubric L2-4] G1 grade_meta={g1_grade_meta} {ok(g1_ok)}  "
        f"G2 cite_type_meta={g2_cite_type_meta} {ok(g2_ok)}"
    )
    if axis_skew_hits:
        metrics_lines.append(
            f"    [Rubric L2-4] N7 skewed axes: {axis_skew_hits}"
        )
    if x1_missing:
        metrics_lines.append(f"    [Rubric L2-4] X1 missing themes: {x1_missing}")
    if d2_raw:
        metrics_lines.append(
            f"    [Rubric L2-4] D2 un-aliased theme refs: {sorted(set(d2_raw))}"
        )
    if f1_refs:
        metrics_lines.append(
            f"    [Rubric L2-4] F1 cluster refs (forbidden): {sorted(set(f1_refs))}"
        )
    if f2_drift:
        metrics_lines.append(f"    [Rubric L2-4] F2 drift: {f2_drift}")

    return issues, metrics_lines


def _emit_rewrite_block_aggregate(claim_count: int, theme_count: int) -> None:
    """Print the Claude rewrite instruction block for `wiki/contradiction.md`.

    Parallels `_emit_rewrite_block` (theme-level) but targets the L2-4
    aggregate — Claude reads Part 2 of the authoring guide/rubric,
    consumes all theme MDs + JSON stats, and rewrites the aggregate
    document. Mechanical fixes are not applicable here (the aggregate
    file has no AUTO blocks or skeleton target state).
    """
    print()
    print("=" * 72)
    print("[/wiki-lint contradiction aggregate --fix] Claude rewrite instruction block")
    print("=" * 72)
    print("Target: wiki/contradiction.md (L2-4 aggregate contradictions)")
    print(f"Current JSON SoT: claims={claim_count} · themes={theme_count} (non-fragmentary + other-fragmentary)")
    print()
    print("Execution order (Claude):")
    print("  1. Read .claude/layers/contradiction.md → Part 2 (Aggregate Rubric)")
    print("  2. Read wiki/contradictions/_contradictions_themes.json → all theme slug·name·claim_ids")
    print("  3. Read wiki/contradictions/_contradictions.json → total claim count·type distribution")
    print("  4. Read wiki/contradiction.md (current state — to capture reusable implications and tension-axis naming)")
    print(f"  5. Read all {theme_count} theme MDs (`wiki/contradictions/<theme>.md`) — gather bottom-up consolidation material centered on each `## Opposing Positions`·`## Interpretive Direction`")
    print("  6. Decide whether to keep the tension axes — keep the current axes named in `## Per-Theme Deep Analysis` by default. Only check whether the themes can be placed, and redesign the axes only when 2+ themes don't fit the existing axes")
    print("  7. Authoring Guide Part 2 → perform execution step 6 (rewrite the whole file with the Write tool · no frontmatter, starting from `# Contradictions by Topic`)")
    print("  8. Match head-matter statistics to SoT: `**N source-to-source contradictions**`·`M topic clusters` (F2 criterion · use the current JSON claims/themes values as-is)")
    print("  9. Re-run `python tools/lint.py contradiction aggregate` → check Rubric L2-4 metrics")
    p2 = _roster_counts("contradiction-aggregate")
    print(f" 10. Iterate until {threshold_label(p2)} is achieved")
    print(" 11. When done, append one line `## [YYYY-MM-DD] lint | contradictions aggregate rewrite` to `log.md`")


def _emit_rewrite_block(theme_slug: str, themes_doc: dict) -> None:
    """Print the Claude rewrite instruction block for a single theme MD.

    Mirrors the overview.py pattern — mechanical fixes (skeleton, legacy
    AUTO strip, section placeholder insertion) happen in --fix mode, then
    this block hands off EDITOR authoring to Claude via the contradiction
    Authoring Guide + Rubric. The script never edits EDITOR content itself
    (dual-automation boundary).

    When `other-fragmentary` is targeted, the block notes the
    N2·D5·D6·S3 exemption so Claude doesn't try to force a dialectic axis
    on what is a residual bucket by design.
    """
    themes = themes_doc.get("themes", {})
    theme_obj = themes.get(theme_slug) if isinstance(themes, dict) else None
    theme_name = theme_obj.get("name") if isinstance(theme_obj, dict) else None
    claim_count = (
        len(theme_obj.get("claim_ids") or []) if isinstance(theme_obj, dict) else 0
    )

    is_fragmentary = theme_slug == "other-fragmentary"

    print()
    print("=" * 72)
    print("[/wiki-lint contradiction --fix] Claude rewrite instruction block")
    print("=" * 72)
    print(f"Target: wiki/contradictions/{theme_slug}.md (L2-3 theme contradiction)")
    if theme_name:
        print(f"Theme name: {theme_name}")
    if claim_count:
        print(f"Linked claims: {claim_count} (see _contradictions_themes.json → {theme_slug}.claim_ids)")
    if is_fragmentary:
        print("Special case: `other-fragmentary` has no single opposing axis — exempt from N2·D5·D6·S3 criteria")
    print()
    print("Execution order (Claude):")
    print("  1. Read .claude/layers/contradiction.md → Part 1 (Theme)")
    print(f"  2. Read wiki/contradictions/_contradictions_themes.json → themes.{theme_slug}")
    print("  3. Read wiki/contradictions/_contradictions.json → resolve claim_ids (id → source/claim/type)")
    print(f"  4. Read wiki/contradictions/{theme_slug}.md (current state)")
    print("  5. Read through 3-6 representative source MDs for the core opposing axis, prioritizing type=real among claim_ids")
    print("     (extra) When selecting representative evidence, prefer the newest source `date:` frontmatter at equal relevance —")
    print("     but preserve at least 1 item from the middle/older part of the overall date distribution to keep evidence of the historical origin")
    print("  6. Authoring Guide Part 1 → perform execution steps 6-7 (write the 4 H2 sections + update frontmatter sources/last_updated)")
    print(f"  7. Re-run `python tools/lint.py contradiction {theme_slug}` → check Rubric metrics")
    p1 = _roster_counts("contradiction-theme")
    if is_fragmentary:
        # other-fragmentary is exempt from N2·D5·D6·S3 (consistent with the three lint `—` marks) —
        # total -4; for required, only N2 of those is required, so -1. Residual-bucket preservation exception.
        print(f"  8. Iterate until {threshold_label(p1, exclude_total=4, exclude_required=1)} is achieved  (N2·D5·D6·S3 exempt)")
    else:
        print(f"  8. Iterate until {threshold_label(p1)} is achieved")
    print("  9. Check the external-reader perspective via the `.claude/agents/desk.md` procedure")


def _check_one_md(path: Path, fix: bool) -> tuple[list[str], int]:
    """Schema + legacy-AUTO-block check for a single existing theme MD file."""
    issues: list[str] = []
    actions = 0

    content = path.read_text(encoding="utf-8")
    fm = parse_frontmatter(content)
    issues.extend(check_frontmatter(fm, CONTRADICTION_REQUIRED_FRONTMATTER, path))
    if fm.get("type") and fm["type"] != "contradiction":
        issues.append(f"  {path.name}: frontmatter `type` is `{fm['type']}` — expected `contradiction`")

    # Legacy AUTO block migration — strip first so subsequent section
    # checks operate on the post-migration content. Non-destructive: only
    # removes explicit `<!-- AUTO:* BEGIN/END -->` wrappers (and an
    # orphaned `## Sources` heading left behind).
    legacy_blocks = LEGACY_AUTO_BLOCK_RE.findall(content)
    if legacy_blocks:
        if fix:
            new_content, stripped = _strip_legacy_auto_blocks(content)
            if stripped:
                atomic_write_text(path, new_content)
                content = new_content
                actions += 1
                print(
                    f"  ~ contradictions/{path.name}: stripped legacy AUTO "
                    f"block(s): {', '.join(stripped)}"
                )
        else:
            issues.append(
                f"  {path.name}: legacy AUTO block(s) present "
                f"({', '.join(sorted(set(legacy_blocks)))}) — theme MDs no "
                f"longer use AUTO blocks; run `/wiki-lint contradiction --fix` to strip"
            )

    # Section presence is line-anchored (header at line start) via the shared
    # `_schema_common.section_present`, matching the advisory S1 metric.
    missing_sections = [s for s in CONTRADICTION_REQUIRED_SECTIONS if not _section_present(content, s)]

    if fix and missing_sections:
        new_content, inserted = _insert_missing_sections(content, missing_sections)
        if inserted:
            atomic_write_text(path, new_content)
            content = new_content
            actions += 1
            print(f"  ~ contradictions/{path.name}: inserted {len(inserted)} section placeholder(s)")
            missing_sections = [s for s in CONTRADICTION_REQUIRED_SECTIONS if not _section_present(content, s)]

    for sec in missing_sections:
        issues.append(f"  {path.name}: section missing `{sec}`")

    return issues, actions


def _plan_mapping_changes(
    themes_doc: dict,
    only_theme: str | None,
) -> tuple[list[tuple[str, str]], list[str], list[str]]:
    """Compute the JSON ↔ MD reconciliation plan (E) without mutating.

    Returns:
      creates: list of (slug, name) tuples for JSON-only slugs ready to
               materialize as skeleton MDs. Slugs with empty/invalid name
               are skipped and surfaced as `invalid_name` instead.
      deletes: list of slugs whose MD exists but is not in the JSON SoT.
      invalid_name: list of JSON slugs whose `name` field is unusable.

    Pure planner — never reads or writes filesystem beyond the existing
    MD slug enumeration in _md_theme_slugs(). Execution (and the
    confirmation prompt) is the caller's responsibility.
    """
    themes = themes_doc.get("themes", {})
    if not isinstance(themes, dict):
        return [], [], []

    json_slugs: set[str] = set(themes.keys())
    md_slugs = _md_theme_slugs()

    if only_theme is not None:
        json_slugs &= {only_theme}
        md_slugs &= {only_theme}

    creates: list[tuple[str, str]] = []
    invalid_name: list[str] = []
    for slug in sorted(json_slugs - md_slugs):
        theme_obj = themes.get(slug, {})
        name = theme_obj.get("name") if isinstance(theme_obj, dict) else None
        if not isinstance(name, str) or not name.strip():
            invalid_name.append(slug)
            continue
        creates.append((slug, name))

    deletes = sorted(md_slugs - json_slugs)
    return creates, deletes, invalid_name


def _execute_mapping_plan(
    creates: list[tuple[str, str]],
    deletes: list[str],
) -> int:
    """Apply a confirmed plan: create skeleton MDs + delete orphan MDs."""
    actions = 0
    if creates:
        CONTRADICTIONS_DIR.mkdir(parents=True, exist_ok=True)
    for slug, name in creates:
        target = safe_slug_path(CONTRADICTIONS_DIR, slug)
        atomic_write_text(target, _skeleton_theme(slug, name))
        actions += 1
        print(f"  + created contradictions/{slug}.md (skeleton from _contradictions_themes.json)")
    actually_deleted: list[str] = []
    for slug in deletes:
        target = safe_slug_path(CONTRADICTIONS_DIR, slug)
        if target.exists():
            target.unlink()
            actions += 1
            actually_deleted.append(slug)
            print(f"  - deleted contradictions/{slug}.md (orphan MD — slug not in _contradictions_themes.json)")
    if actually_deleted:
        print_delete_cleanup_advisory(
            actually_deleted,
            kind="contradiction theme",
            check_cluster_labels=False,
        )
    return actions


def _check_frontmatter_drift(themes_doc: dict, claims: list[dict], only_theme: str | None = None) -> list[str]:
    """G. Informational — theme MD frontmatter `sources:` vs JSON-implied sources.

    Reports each theme where the MD `sources:` set diverges from the unique
    source slugs implied by the JSON `claim_ids`. Pure informational signal
    for AUTO:CLAIMS filtering accuracy — does not affect pass/fail.
    """
    notes: list[str] = []
    themes = themes_doc.get("themes", {})
    if not isinstance(themes, dict):
        return notes

    by_id = _claims_by_id(claims)

    for slug, theme in themes.items():
        if only_theme is not None and slug != only_theme:
            continue
        if not isinstance(theme, dict):
            continue
        md_path = CONTRADICTIONS_DIR / f"{slug}.md"
        if not md_path.exists():
            continue
        fm = parse_frontmatter(md_path.read_text(encoding="utf-8"))
        md_sources = {
            str(s).removeprefix("sources/").removesuffix(".md")
            for s in (fm.get("sources") or [])
            if isinstance(s, str)
        }

        json_sources = _sources_for_claim_ids(theme.get("claim_ids", []) or [], by_id)

        only_md = md_sources - json_sources
        only_json = json_sources - md_sources
        if only_md or only_json:
            parts = []
            if only_json:
                parts.append(f"JSON-implied not in MD: {sorted(only_json)[:3]}")
            if only_md:
                parts.append(f"MD-only: {sorted(only_md)[:3]}")
            notes.append(f"  {slug}.md: " + " | ".join(parts))

    return notes


def run(target: str | None = None, fix: bool = False, auto_yes: bool = False) -> int:
    """Entry point for `python tools/lint.py contradiction [<target>] [--fix [--yes]]`.

    target:
      - None          → every theme MD + JSON↔MD mapping + aggregate check
      - "<theme>"     → single theme (MD + its mapping row only)
      - "aggregate"   → only `wiki/contradiction.md` (L2-4) evaluation

    fix:
      - False → diagnostics only (no prompt, no mutations)
      - True  → planned repairs after confirmation:
          create: JSON-only slug → skeleton MD from _contradictions_themes.json name
          delete: MD-only slug   → remove orphan MD (slug not in JSON SoT)
        Plus non-destructive content fixes on existing files (proceed
        without extra prompt — they touch only file content, not file
        existence):
          * Legacy AUTO blocks → strip (theme MDs use no AUTO blocks)
          * Missing required H2 sections → insert TODO placeholder
        With target="<theme>" → Claude rewrite block (Part 1) appended.
        With target="aggregate" → Claude rewrite block (Part 2) appended
        (mechanical fixes N/A — aggregate file has no skeleton/AUTO targets).

    auto_yes:
      - False → create/delete plan triggers `confirm_changes()` prompt;
        non-TTY callers (Claude Code Bash, CI) abort the create/delete
        portion with a hint to re-invoke with --yes.
      - True  → skip the prompt and apply the plan unconditionally.
        Use only after reviewing the planned changes upstream.

    SoT freshness gate: when fix=True, this entry checks whether
    `_contradictions_themes.json` is stale relative to `_contradictions.json`
    (the upstream raw claims DB) before any mutations. If stale,
    fix is downgraded to False (this call skips MD mutations so stale
    theme boundaries are not propagated) and the Phase 1·2 theme rewrite
    block is emitted so Claude can auto-chain the regeneration and
    re-invocation. Diagnostic output still runs so the user sees the
    current mapping picture. The `--yes` flag on the enclosing call acts
    as the explicit opt-in for chaining probabilistic-reasoning work
    (theme regeneration) into a single `--fix` session.
    """
    themes_doc, themes_err = _load_themes_json()
    if themes_err:
        print(f"ERROR: {themes_err}", file=sys.stderr)
        return 2
    assert themes_doc is not None

    # target dispatch — "aggregate" is a reserved value like "theme",
    # handled by a dedicated branch that skips theme-level processing.
    scope = "all"
    if target == "aggregate":
        scope = "aggregate"
    elif target is not None:
        scope = "theme"

    if fix:
        stale, reason = is_themes_json_stale()
        if stale:
            _set_chain_pending(f"themes_json_stale: {reason}")
            print()
            print(
                f"STALE --fix chain: _contradictions_themes.json is stale ({reason})."
            )
            print(
                "This call skips MD mutations to avoid propagating outdated theme "
                "boundaries. The theme rewrite block below instructs Claude to "
                "regenerate the SoT JSON (Phase 1·2), then re-run this command."
            )
            print("(Diagnostic continues; MD mutations are skipped this pass.)")
            _print_theme_rewrite_block()
            print()
            print(
                "After the rewrite block completes, re-run "
                "`/wiki-lint contradiction --fix --yes` to reconcile MDs against "
                "the refreshed theme map."
            )
            print()
            print("⚡ ACTION REQUIRED — Claude must execute the rewrite block above")
            print("   immediately, regardless of estimated work size (e.g. 250 claims).")
            print("   The `--yes` flag is the explicit opt-in for chain execution.")
            print("   Demoting this to a 'remaining work' item violates the opt-in")
            print("   contract. Do NOT proceed to lint-report.md authoring or any")
            print("   other lint/build command until Phase 1·2 is complete.")
            print()
            fix = False

    md_slugs = _md_theme_slugs()
    json_slugs = set(themes_doc.get("themes", {}).keys())

    only_theme: str | None = None
    if scope == "theme":
        if target not in md_slugs and target not in json_slugs:
            print(
                f"ERROR: target '{target}' is not an existing theme slug "
                f"(MD or JSON) or the reserved 'aggregate' keyword.",
                file=sys.stderr,
            )
            print(
                f"Valid MD slugs: {sorted(md_slugs)}\n"
                f"Valid JSON slugs: {sorted(json_slugs)}\n"
                f"Reserved keyword: 'aggregate' (for wiki/contradiction.md)",
                file=sys.stderr,
            )
            return 2
        only_theme = target

    # theme-level processing is skipped when scope=="aggregate".
    # aggregate-only run focuses on wiki/contradiction.md evaluation.
    creates: list[tuple[str, str]] = []
    deletes: list[str] = []
    invalid_name: list[str] = []
    if scope != "aggregate":
        creates, deletes, invalid_name = _plan_mapping_changes(themes_doc, only_theme)

    map_actions = 0
    map_hard: list[str] = []

    for slug in invalid_name:
        map_hard.append(
            f"  JSON-declared theme `{slug}` has empty/invalid name — "
            f"cannot generate skeleton MD. Fix _contradictions_themes.json first."
        )

    if fix:
        plan = {"create": [f"contradictions/{s}.md" for s, _ in creates],
                "delete": [f"contradictions/{s}.md" for s in deletes]}
        approved = confirm_changes(
            plan,
            context="contradiction MD ↔ _contradictions_themes.json sync",
            auto_yes=auto_yes,
        )
        if approved:
            map_actions = _execute_mapping_plan(creates, deletes)
        else:
            # Plan rejected (or non-TTY without --yes) — surface mismatches
            # as hard issues so the lint exit code reflects unresolved drift.
            for slug, _name in creates:
                map_hard.append(
                    f"  contradictions/{slug}.md missing (theme `{slug}` declared in "
                    f"_contradictions_themes.json) — re-run --fix and confirm, or "
                    f"add --yes after reviewing"
                )
            for slug in deletes:
                map_hard.append(
                    f"  contradictions/{slug}.md exists but theme `{slug}` is not in "
                    f"_contradictions_themes.json — re-run --fix and confirm to delete, "
                    f"or regenerate JSON via `/wiki-lint contradiction theme --fix`"
                )
    else:
        for slug, _name in creates:
            map_hard.append(
                f"  contradictions/{slug}.md missing (theme `{slug}` declared in "
                f"_contradictions_themes.json) — `/wiki-lint contradiction --fix` "
                f"creates skeleton (with confirmation)"
            )
        for slug in deletes:
            map_hard.append(
                f"  contradictions/{slug}.md exists but theme `{slug}` is not in "
                f"_contradictions_themes.json — `/wiki-lint contradiction --fix` "
                f"deletes orphan (with confirmation), or regenerate JSON via "
                f"`/wiki-lint contradiction theme --fix`"
            )

    schema_issues: list[str] = []
    schema_actions = 0
    md_paths: list[Path] = []
    if scope != "aggregate" and CONTRADICTIONS_DIR.exists():
        for path in sorted(CONTRADICTIONS_DIR.glob("*.md")):
            if path.name.startswith("_"):
                continue
            if only_theme is not None and path.stem != only_theme:
                continue
            md_paths.append(path)
            issues, actions = _check_one_md(path, fix)
            schema_issues.extend(issues)
            schema_actions += actions

    claims = _load_claims_json()
    cluster_slugs = _load_cluster_slugs()
    source_slugs = _load_source_slugs()

    # Rubric Part 1 advisory — computed after any --fix mutations so the
    # numbers reflect the post-fix state the user will re-lint against.
    metrics_reports: list[str] = []
    # Load HEAD baselines once for the whole loop — avoids N git calls.
    head_themes_doc = _git_head_json(THEMES_JSON)
    head_claims = _git_head_json(CLAIMS_JSON)
    if scope != "aggregate":
        for path in md_paths:
            theme_slug = path.stem
            exempt = (
                {"N2", "D5", "D6", "S3"} if theme_slug == "other-fragmentary" else set()
            )
            m = _rubric_metrics(
                path, theme_slug, themes_doc, claims, cluster_slugs, source_slugs,
            )
            # Skip the advisory for skeleton-only files — S1 TODO placeholders
            # flood the output with FAILs that just repeat the schema warning.
            # A fresh skeleton (or one restored by _insert_missing_sections) has
            # all required H2s present, so gating on S1_sections never fired;
            # detect "still all placeholders" via the TODO count instead.
            if m["S1_todo"] >= len(CONTRADICTION_REQUIRED_SECTIONS):
                continue
            file_lines = _format_metrics_line(m, exempt=exempt)
            drift = _claims_drift_line(
                theme_slug, themes_doc, claims, head_themes_doc, head_claims,
            )
            if drift:
                file_lines.append(drift)
            stale = _claims_staleness_line(theme_slug, themes_doc, claims)
            if stale:
                file_lines.append(stale)
            if file_lines:
                metrics_reports.append(f"  contradictions/{path.name}:")
                metrics_reports.extend(file_lines)

    if metrics_reports:
        print(
            "\n[Theme Contradiction Rubric metrics — advisory, see "
            ".claude/layers/contradiction.md Part 1]"
        )
        for line in metrics_reports:
            print(line)

    # L2-4 aggregate evaluation — Rubric Part 2 (15 criteria).
    aggregate_issues: list[str] = []
    aggregate_metrics: list[str] = []
    if scope in ("all", "aggregate"):
        theme_slugs_all = set(themes_doc.get("themes", {}).keys())
        non_fragmentary_count = sum(
            1 for s in theme_slugs_all if s != "other-fragmentary"
        )
        aggregate_issues, aggregate_metrics = _check_contradictions_md(
            theme_slugs_all,
            cluster_slugs,
            claim_count=len(claims),
            non_fragmentary_theme_count=non_fragmentary_count,
        )
        if aggregate_metrics:
            print(
                "\n[Aggregate Contradictions Rubric metrics — advisory, see "
                ".claude/layers/contradiction.md Part 2]"
            )
            for line in aggregate_metrics:
                print(line)

    drift_notes: list[str] = []
    if scope != "aggregate":
        drift_notes = _check_frontmatter_drift(themes_doc, claims, only_theme=only_theme)

    hard_issues = map_hard + schema_issues + aggregate_issues

    if fix and (map_actions or schema_actions):
        print(f"  contradictions: {map_actions} mapping action(s), {schema_actions} schema fix(es) applied")

    if hard_issues:
        print(f"\n[contradiction scope: {len(hard_issues)} schema/mapping issue(s)]")
        for line in hard_issues:
            print(line)

    if drift_notes:
        print(
            f"\n[contradiction scope: {len(drift_notes)} frontmatter↔JSON sources drift "
            f"note(s) — informational]"
        )
        for line in drift_notes:
            print(line)

    # Rewrite block dispatch: aggregate block for aggregate target, theme
    # block for single-theme target. scope="all" deliberately omits both
    # — that matches the "probabilistic-reasoning triggers require an explicit
    # invocation" principle from CLAUDE.md (`/wiki-lint --fix` / `all --fix`
    # never triggers a Claude rewrite; only `/wiki-lint contradiction <target> --fix` does).
    if fix and scope == "aggregate":
        _emit_rewrite_block_aggregate(
            claim_count=len(claims),
            theme_count=len(themes_doc.get("themes", {})),
        )
    elif fix and only_theme is not None:
        _emit_rewrite_block(only_theme, themes_doc)

    if hard_issues:
        print(
            "\nFAIL — contradiction scope has schema/mapping/aggregate deviations. "
            "See .claude/layers/contradiction.md + Contradictions Sync Rule."
        )
        return 1

    print("\nOK — contradiction scope: theme MD schema + JSON↔MD mapping + aggregate L2-4")
    return 0


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?", default=None)
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--yes", "-y", action="store_true")
    args = ap.parse_args()
    sys.exit(run(target=args.target, fix=args.fix, auto_yes=args.yes))
