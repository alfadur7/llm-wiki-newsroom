"""Synthesis page schema lint — `wiki/syntheses/<slug>.md` (L2-3 Q-A axis).

A synthesis is a cross-source analytic answer to a standing question/tension —
it integrates already-ingested material (hubs·sources·themes) into one
navigable document. This module checks the structural contract codified in
`.claude/layers/synthesis.md` and reuses the manifest roster for the
completion-criteria string (mirrors `overview.py` / `source.py`).

Three structural (layers-owned, craft-free) criteria are auto-measured here:
  * struct.schema-sections — `## Summary` + `## Connections` present + ≥1 `## N.` analytic section
  * struct.source-coverage — frontmatter `sources:` largely re-appear as body [[links]]
  * struct.source-exists   — every declared `sources:` slug is a real wiki/sources/ file
  * enc.slug-alias (L1)     — no raw ≥10-char kebab slug exposed without pipe alias
Plus advisory W1 (link density) · F1 (last_updated) · [Placement] (mis-filed
news/briefing detection) · J1 (conflation surface — claim lines joining ≥2
declared sources, so the desk verifies each span-by-span rather than spot-
checking 1–2; lint surfaces WHERE, the join's validity stays desk-judged). All
advisory only, never gate the exit code.

Craft criteria (jrn.lede·con.scr·cit.* etc.) in the manifest roster are
manual (M) — judged by desk VERIFY₂, not auto-measured here (same split as
overview.py: roster drives the completion count, lint measures the A subset).

Migration mode: this lint runs in **advisory mode** until the synthesis seed
calibration batch (plan step 2) brings existing files to compliance and tunes
thresholds against the exemplar. FAIL counts display but exit code stays 0 so
the new group does not break `lint all`. Flip `ADVISORY_MODE = False` after
calibration. Mirrors the `source.py` rollout precedent.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import WIKI, WIKILINK_STEM_RE, WIKILINK_ANY_RE, MARKUP_LEAK_RE, atomic_write_text, parse_frontmatter, read_text_cached, safe_slug_path, strip_code, strip_frontmatter  # noqa: E402
sys.path.insert(0, str(Path(__file__).parent))  # tools/_lint/ — for _manifest_counts (sibling)
from _advisory_common import L1_MIN_SLUG_LEN, iter_md, mark as _mark, print_rewrite_block  # noqa: E402

# enc.slug-alias(L1) measurement is owned by the encyclopedia-writing skill;
# reuse the same implementation overview.py uses (MOVE-not-COPY) rather than a
# local regex that drifts from the skill's kebab-only·subdir-stripping semantics.
_ENC_CHECKS_PATH = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "encyclopedia-writing" / "checks.py"
_enc_spec = importlib.util.spec_from_file_location("enc_checks_syn", _ENC_CHECKS_PATH)
enc_skill = importlib.util.module_from_spec(_enc_spec)
_enc_spec.loader.exec_module(enc_skill)

SYNTHESES_DIR = WIKI / "syntheses"
SOURCES_DIR = WIKI / "sources"

# Seed-calibration toggle (plan step 2). While advisory, counts are reported
# but exit code stays 0 — keeps `lint all` green during the rollout. Flip to
# False once the seed batch lands and thresholds are tuned to the exemplar.
ADVISORY_MODE = True

REQUIRED_FRONTMATTER = {"title", "type", "sources", "last_updated"}
REQUIRED_SECTIONS = ("## Summary", "## Connections")
SOURCE_COVERAGE_MIN = 0.7  # fraction of frontmatter sources that re-appear as body [[links]]
W1_MIN_LINKS = 10

# Auto-measured required criteria — a FAIL on these gates the exit code
# (subject to ADVISORY_MODE). Manual roster criteria are desk-verified.
# enc.slug-alias (L1) is advisory-only for synthesis: unlike source/hub pages
# (which link short Korean entity names), a synthesis legitimately exposes long
# kebab slugs via inline source citations (cit.grounding idiom) and cross-layer
# links to overviews/trails/themes. Forcing pipe aliases there is noise, so L1
# is reported but does NOT gate (manifest: enc.slug-alias is optional). Tier-A
# calibration finding (exemplar ai-coding-evolution).
#
# source_exists gates: SrcCov checks reappearance only, so a fabricated source
# slug passes coverage while pointing at no file — the hallucination that the
# 2026-05-31 finance-regulation-stablecoin draft produced. Existence is the
# guard SrcCov structurally cannot be.
REQUIRED_KEYS = ("schema", "source_coverage", "source_exists")

# Numbered analytic section: `## 1. ...`, `## 12. ...`
NUMBERED_SECTION_RE = re.compile(r"^##\s+\d+\.\s+", re.MULTILINE)

# Mis-filed news/briefing heuristic — a `/wiki-news` triage report is NOT a
# synthesis (no `sources:`, body is a triage table). Placement is advisory
# only: lint surfaces it for operator triage but never moves/deletes and never
# gates the exit code. Filename signal is the primary, robust marker.
NEWS_FILENAME_RE = re.compile(r"^(news-|weekly-briefing-)")

# `## Connections` roster heading — the J1 join scan stops here. Roster lines
# legitimately co-locate many links (cluster·trail·concept·entity·theme) but are
# not claims, so they must not count as conflation surface.
CONNECT_HEADING_RE = re.compile(r"^##\s+Connections\s*$", re.MULTILINE)


def _sources_list(fm: dict) -> list[str]:
    """Frontmatter `sources:` as a clean stem list (handles list or scalar)."""
    raw = fm.get("sources")
    if raw is None:
        return []
    if isinstance(raw, str):
        raw = [s.strip() for s in raw.strip("[]").split(",") if s.strip()]
    out = []
    for s in raw:
        if not isinstance(s, str):
            continue
        stem = s.strip().strip("'\"").removesuffix(".md")
        if stem:
            out.append(stem)
    return out


def _is_news_misfile(slug: str, fm: dict) -> bool:
    """True if this file is a mis-filed news/briefing triage report."""
    if NEWS_FILENAME_RE.match(slug):
        return True
    # Secondary: no sources AND title reads as a dated news/briefing report.
    title = str(fm.get("title", ""))
    if not _sources_list(fm) and re.search(
        r"(News search|Weekly [Bb]riefing|Report \(20|뉴스 검색|주간 브리핑|리포트 \(20)", title
    ):
        return True
    return False


def _evaluate(rel: str, slug: str, content: str) -> dict:
    fm = parse_frontmatter(content)
    body = strip_code(strip_frontmatter(content))

    # struct.schema-sections — required H2 + ≥1 numbered analytic section.
    sections_present = [h for h in REQUIRED_SECTIONS if re.search(rf"^{re.escape(h)}\s*$", body, re.MULTILINE)]
    has_numbered = bool(NUMBERED_SECTION_RE.search(body))
    schema_pass = len(sections_present) == len(REQUIRED_SECTIONS) and has_numbered

    # frontmatter completeness (folded into schema reporting).
    fm_missing = sorted(f for f in REQUIRED_FRONTMATTER if not fm.get(f))

    # struct.source-coverage — frontmatter sources that re-appear as body links.
    src = _sources_list(fm)
    body_stems = {m.group(1).strip().split("/")[-1] for m in WIKILINK_STEM_RE.finditer(body)}
    if src:
        covered = sum(1 for s in src if s in body_stems)
        coverage_ratio = covered / len(src)
    else:
        covered = 0
        coverage_ratio = -1.0  # exempt (no sources declared)
    coverage_pass = coverage_ratio < 0 or coverage_ratio >= SOURCE_COVERAGE_MIN

    # struct.source-exists — declared sources must be real wiki/sources/ files
    # (hallucination guard). A fabricated slug passes SrcCov but points nowhere.
    src_missing = [s for s in src if not (SOURCES_DIR / f"{s}.md").is_file()]
    source_exists_pass = not src_missing

    # J1 (advisory) — conflation surface. A synthesis is the one page type that
    # joins ≥2 sources into one claim, so a fabricated seam (a single assertion
    # fusing two sources but present in neither span) passes every per-source
    # check: each half is anchored to a real span, only the join is invented.
    # Nothing deterministic can judge whether the join holds (semantic — desk
    # VERIFY₂), but lint CAN surface WHERE the joins are so the desk verifies each
    # span-by-span instead of spot-checking 1–2. Scan claim lines (before the
    # `## Connections` roster) for those citing ≥2 distinct declared sources. Skip
    # mis-filed news/briefing files: a triage table row lists many sources per
    # line but is not a synthesis claim, so J1 would fire in bulk on a briefing
    # and bury the genuine-synthesis signal. Those files are operator-triage.
    misfile = _is_news_misfile(slug, fm)
    join_units = []
    if not misfile:
        m_connect = CONNECT_HEADING_RE.search(body)
        claim_region = body[: m_connect.start()] if m_connect else body
        src_set = set(src)
        for line in claim_region.splitlines():
            hits = {t for m in WIKILINK_STEM_RE.finditer(line) if (t := m.group(1).strip().split("/")[-1]) in src_set}
            if len(hits) >= 2:
                join_units.append((line.strip()[:70], sorted(hits)))

    # enc.slug-alias (L1) — raw ≥10-char kebab slug exposure (owning skill impl).
    l1_raw = enc_skill.find_unaliased_slugs(body, min_len=L1_MIN_SLUG_LEN)
    slug_alias_pass = len(l1_raw) == 0

    # W1 (advisory) — wikilink density.
    w1_links = len(WIKILINK_ANY_RE.findall(body))
    w1_pass = w1_links >= W1_MIN_LINKS

    # F1 (advisory) — last_updated present. Read from parsed frontmatter, not a
    # fixed content window: a synthesis `sources:` list can be long enough to
    # push last_updated past any byte cutoff (Tier-A finding).
    f1_pass = bool(re.match(r"^\d{4}-\d{2}-\d{2}$", str(fm.get("last_updated", "")).strip()))

    # MarkupLeak — tool-call XML (`</invoke>`·`</content>`·`<parameter`·antml:)
    # that an agent Write/Edit can spill into the body. Unlike the calibration-
    # sensitive criteria above, a leak is never acceptable, so it HARD-GATES the
    # exit code even in advisory mode (closes the unmanned-routine blind spot
    # that shipped a W23 leak 2026-06-08). `body` is already code-stripped, so
    # intentional fenced XML examples are exempt.
    markup_leaks = MARKUP_LEAK_RE.findall(body)
    markup_pass = len(markup_leaks) == 0

    return {
        "rel": rel,
        "slug": slug,
        "misfile": misfile,
        "schema": (schema_pass, len(sections_present), len(REQUIRED_SECTIONS), has_numbered),
        "fm_missing": fm_missing,
        "source_coverage": (coverage_pass, covered, len(src), coverage_ratio),
        "source_exists": (source_exists_pass, src_missing),
        "slug_alias": (slug_alias_pass, len(l1_raw), l1_raw[:5]),
        "join": (len(join_units), join_units[:5]),
        "w1": (w1_pass, w1_links),
        "f1": (f1_pass,),
        "markup": (markup_pass, len(markup_leaks), markup_leaks[:5]),
    }


def _print_per_file(r: dict) -> None:
    schema_pass, s_n, s_total, has_num = r["schema"]
    cov_pass, cov_n, cov_total, cov_ratio = r["source_coverage"]
    exists_pass, src_missing = r["source_exists"]
    sa_pass, sa_count, sa_samples = r["slug_alias"]
    join_n, join_samples = r["join"]
    w1_pass, w1_n = r["w1"]
    (f1_pass,) = r["f1"]
    markup_pass, markup_count, markup_samples = r["markup"]

    cov_str = "—" if cov_ratio < 0 else f"{cov_n}/{cov_total} ({int(cov_ratio * 100)}%)"
    print(f"{r['rel']}:")
    if r["misfile"]:
        print(
            "  [Placement] ⚠️ news/briefing format — not a synthesis (no `sources:` / triage table). "
            "Not eligible for wiki/syntheses/. Operator should relocate it (no auto-move). The Rubric below is for reference only."
        )
    print(
        f"  [Rubric] S1 sections={s_n}/{s_total}+num{'✓' if has_num else '✗'} {_mark(schema_pass)}  "
        f"SrcCov={cov_str} {_mark(cov_pass)}  "
        f"SrcExist={_mark(exists_pass)}  "
        f"L1 raw_slugs={sa_count} {_mark(sa_pass)}  "
        f"J1 joins={join_n}  "
        f"W1 links={w1_n} {_mark(w1_pass)}  "
        f"F1 last_updated={_mark(f1_pass)}  "
        f"MarkupLeak={markup_count} {_mark(markup_pass)}"
    )
    if join_n:
        print(f"  [Join] {join_n} conflation surface(s) (claims joining ≥2 sources) — desk must verify span-by-span (no spot check):")
        for text, slugs in join_samples:
            print(f"    {slugs} · {text}")
    if not markup_pass:
        print(f"  [BLOCKER] tool-call markup leak (do not publish): {markup_samples}")
    if src_missing:
        print(f"  [Rubric] ⚠️ nonexistent source (suspected hallucination): {src_missing[:5]}")
    if r["fm_missing"]:
        print(f"  [Rubric] frontmatter missing: {r['fm_missing']}")
    if not sa_pass and sa_samples:
        print(f"  [Rubric] L1 raw slug samples: {sa_samples}")


def _print_corpus_summary(results: list[dict]) -> None:
    total = len(results)
    if total == 0:
        print("No synthesis files found.")
        return
    genuine = [r for r in results if not r["misfile"]]
    misfiled = [r for r in results if r["misfile"]]

    def pct(n: int, d: int) -> str:
        return f"{n}/{d} ({100 * n // d}%)" if d else "0/0"

    schema_n = sum(1 for r in genuine if r["schema"][0])
    cov_n = sum(1 for r in genuine if r["source_coverage"][0])
    exist_n = sum(1 for r in genuine if r["source_exists"][0])
    sa_n = sum(1 for r in genuine if r["slug_alias"][0])
    g = len(genuine)
    print(f"Synthesis schema diagnosis — {total} files ({g} genuine · {len(misfiled)} placement-flagged)")
    print(f"  S1 schema-sections  PASS={pct(schema_n, g)}")
    print(f"  SrcCov ≥{int(SOURCE_COVERAGE_MIN*100)}%        PASS={pct(cov_n, g)}")
    print(f"  SrcExist (real file) PASS={pct(exist_n, g)}")
    print(f"  L1 slug-alias clean PASS={pct(sa_n, g)}")
    hallucinated = [r for r in genuine if not r["source_exists"][0]]
    if hallucinated:
        print("\n  [Suspected hallucination] declares nonexistent sources (struct.source-exists FAIL):")
        for r in hallucinated:
            print(f"    {r['slug']} → {r['source_exists'][1][:5]}")
    if misfiled:
        print(f"\n  [Placement] {len(misfiled)} mis-filed news/briefing (advisory — operator triage):")
        for r in misfiled:
            print(f"    {r['slug']}")
    fails = [r for r in genuine if any(not r[k][0] for k in REQUIRED_KEYS)]
    if fails:
        print(f"\n  Non-compliant genuine syntheses ({len(fails)}):")
        for r in fails:
            failed = [k for k in REQUIRED_KEYS if not r[k][0]]
            print(f"    {r['slug']} — {failed}")
    if ADVISORY_MODE:
        print(
            "\n  [Advisory mode] seed calibration not yet complete — exit 0 even if "
            "files fail. See .claude/layers/synthesis.md → Migration."
        )


def _skeleton(slug: str) -> str:
    today = "YYYY-MM-DD"
    return (
        f'---\ntitle: "{slug}"\ntype: synthesis\ntags: []\nsources: []\n'
        f"last_updated: {today}\n---\n\n"
        f"# {slug}\n\n## Summary\n\n_TODO: 2-4 sentence lede — the answer to the standing question and the core tension._\n\n"
        f"## 1. _TODO analysis section title_\n\n_TODO: cross-source analytic prose._\n\n"
        f"## Connections\n\n_TODO: per-axis [[wikilink]] roster (cluster overview · trail · concept · entity · theme)._\n"
    )


def _print_rewrite_block(slug: str, path: Path, exists: bool) -> None:
    print_rewrite_block(
        "synthesis", slug, path, exists, "L2-3 Q-A synthesis",
        [
            "Read .claude/layers/synthesis.md (Authoring + Rubric)",
            f"Read {path.as_posix()} (current state)",
            "Identify the standing question → fill frontmatter sources[] (the source slugs being integrated)",
            "Write `## Summary` lede (jrn.lede·con.scr) → `## N.` analysis sections → `## Connections` per-axis roster",
            "self-VERIFY₀: `python tools/lint.py synthesis " + slug + "`",
        ],
        "synthesis", "iterate until the bar is met (PASS bar = roster; qualitative review is the desk's VERIFY₂)")


def run(target: str | None = None, fix: bool = False, **_kwargs) -> int:
    if not SYNTHESES_DIR.is_dir():
        print(f"ERROR: {SYNTHESES_DIR} not found.", file=sys.stderr)
        return 2

    if target:
        slug = target.removesuffix(".md")
        path = SYNTHESES_DIR / f"{slug}.md"
        if fix and not path.is_file():
            try:
                path = safe_slug_path(SYNTHESES_DIR, slug)  # gate slug→path before write
            except ValueError as exc:
                print(f"ERROR: {exc}", file=sys.stderr)
                return 2
            atomic_write_text(path, _skeleton(slug))
            print(f"Created skeleton: {path.as_posix()}")
            _print_rewrite_block(slug, path, exists=False)
            return 0
        if not path.is_file():
            print(f"ERROR: synthesis file not found: {path}", file=sys.stderr)
            return 2
        content = read_text_cached(path)
        result = _evaluate(f"syntheses/{slug}.md", slug, content)
        _print_per_file(result)
        if fix:
            _print_rewrite_block(slug, path, exists=True)
        if not result["markup"][0]:
            return 1  # markup leak hard-gates even in advisory mode
        if ADVISORY_MODE or result["misfile"]:
            return 0
        return 1 if any(not result[k][0] for k in REQUIRED_KEYS) else 0

    # Corpus scan.
    results = []
    for path, content in iter_md(SYNTHESES_DIR):
        results.append(_evaluate(f"syntheses/{path.name}", path.name[:-3], content))
    _print_corpus_summary(results)
    if any(not r["markup"][0] for r in results):
        return 1  # markup leak hard-gates even in advisory mode
    if ADVISORY_MODE:
        return 0
    genuine_fail = [r for r in results if not r["misfile"] and any(not r[k][0] for k in REQUIRED_KEYS)]
    return 1 if genuine_fail else 0
