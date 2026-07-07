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
from _lib import FRONTMATTER_BLOCK_RE, REPO_ROOT, WIKI, WIKILINK_ANY_RE, parse_frontmatter, read_text_cached, real_source_files, strip_code, strip_frontmatter  # noqa: E402
sys.path.insert(0, str(Path(__file__).parent))
from _advisory_common import L1_MIN_SLUG_LEN, L1_RAW_SLUG_RE, mark  # noqa: E402

import importlib.util as _ilu  # noqa: E402
import json as _json  # noqa: E402

# cit.* (G1–G5·C1–C3·A1–A3) measurement is owned by the scholarly-citation
# skill. The call configuration is the manifest SoT (`source.bundles`).
# Wiki-global state (page_index·section title) is injected by the orchestrator
# code; the threshold (c2) comes from manifest params.
_MANIFEST = _json.loads((REPO_ROOT / ".claude" / "layers" / "_manifest.json").read_text(encoding="utf-8"))
_cit_skill_name = "scholarly-citation"
_cit_bundle_cfg = _MANIFEST["source"]["bundles"][_cit_skill_name]
_cit_spec = _ilu.spec_from_file_location(
    "cit_checks", REPO_ROOT / ".claude" / "skills" / _cit_skill_name / "checks.py"
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
# Empty in this distribution — entries accumulate as the operated corpus does.
INTRINSICALLY_UNFIXABLE_SOURCES: set[str] = set()

# Required Rubric criteria — any FAIL on these
# keys causes a non-zero exit (subject to ACCEPTABLE_FAILS at corpus level).
# Mirrors the `required_keys` list used by _print_corpus_summary for
# top-fail reporting; kept as a module constant so the corpus-scan and
# per-file paths share the same definition.
REQUIRED_KEYS = ("g1", "g2", "g4", "c1", "c3", "s1", "l1")

REQUIRED_SECTIONS = ("## Summary", "## Key Claims", "## Connections")
W1_MIN_LINKS = 5

# The cit.* measurement regexes (grade·claimant·citation prefix·quote·composite·anchor)
# were moved verbatim to scholarly-citation/checks.py. This file measures only S1·W1·L1·desk.
# L1 (raw kebab-case slug exposure) constants live in _advisory_common (shared with synthesis·trail).

# Section header detector.
H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)

# Wikilink (any) — captures inner target (without optional pipe alias).

# Desk-review sub-trigger — `[fact] ≥ 7 AND quoted citations ≥ 3`.
# 2026-05-19 threshold raised (5→7·2→3) — overall source distribution dropped 8.4% → 2.2%.
# Rationale for raising: desk PoC found a 45% critical+high defect rate · 4x reduction in
# operational burden · concentration on multi-speaker in-depth-reporting sources. SoT: the
# applicability scope in .claude/agents/desk.md.
DESK_TRIGGER_FACT_MIN = 7
DESK_TRIGGER_QUOTE_MIN = 3
DESK_QUOTE_RE = re.compile(r"^>\s+", re.MULTILINE)
DESK_FACT_RE = re.compile(r"^-\s*\[fact\]", re.MULTILINE)


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
    _fm_m = FRONTMATTER_BLOCK_RE.match(content)
    _fm_head = _fm_m.group(1) if _fm_m else ""
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
    desk_fact = len(DESK_FACT_RE.findall(body))
    desk_quote = len(DESK_QUOTE_RE.findall(body))
    desk_trigger = desk_fact >= DESK_TRIGGER_FACT_MIN and desk_quote >= DESK_TRIGGER_QUOTE_MIN

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
        "desk": (desk_trigger, desk_fact, desk_quote),
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

    desk_trigger, desk_fact, desk_quote = result["desk"]
    if desk_trigger:
        print(
            f"  [Advisory] Desk qualitative review recommended — [fact]={desk_fact} AND "
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
        f"[advisory] — [fact] ≥ {DESK_TRIGGER_FACT_MIN} AND quoted citations ≥ "
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
        content = read_text_cached(path)
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
        content = read_text_cached(path)
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
