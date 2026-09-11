"""Standalone timeline page schema lint — `wiki/timelines/<slug>.md` (L2-2 Path).

A standalone timeline is a **source-indexed chronological index**: each dated
entry leads with `[[source-id]]` so the overlay builder classifies it as a
`path` overlay (members = ordered source nodes). This module enforces that
contract, codified in `.claude/layers/timeline.md`, and reuses the manifest
roster for the completion-criteria string (mirrors `trail.py` / `synthesis.py`).

The key guard is **source-indexed**: it mirrors the builder's path/region
decision (`tools/_build/overlays.py:_timeline_overlay`, `src_n > hub_n`) by
counting dated entries whose first wikilink resolves to a `wiki/sources/` file.
A timeline that builds to `region` (entity-led entries) is the regression this
catches — it should be converted to source-led so all timelines render alike.

Auto-measured structural (layers-owned, craft-free) criteria:
  * struct.schema-sections — `## Flow Summary` + ≥1 `### YYYY` dated section present
  * struct.source-indexed  — source-led dated entries outnumber entity-led ones
                             (→ path flavor). The region-regression guard.

NOTE — unlike trail, a timeline's dated entries INTENTIONALLY expose raw
`[[source-id]]` kebab slugs (the canonical chronological index), so the
`enc.slug-alias` rule is NOT applied to them. Broken-link is delegated to
`python tools/lint.py graph structure`.

Two checks hard-gate even under ADVISORY_MODE — MarkupLeak (tool-call XML
in the body) and Type (frontmatter `type` not matching the group). The author's
self-VERIFY0 runs this group alone, so without them a leak or a wrong `type`
clears the authoring gate; `hub schema` catches the timeline `type` later in
`lint all`, but not before the page is handed over.

Advisory rollout: `ADVISORY_MODE = True` until the seed calibration batch
(the 6 remaining region timelines are converted). Mirrors `trail.py`.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import MARKUP_LEAK_RE, TIMELINE_DATE_ONLY_RE, TIMELINE_ENTRY_RE, WIKI, WIKILINK_STEM_RE, atomic_write_text, parse_frontmatter, read_text_cached, strip_code, strip_frontmatter  # noqa: E402
sys.path.insert(0, str(Path(__file__).parent))  # tools/_lint/ — sibling import
from _advisory_common import iter_md, mark as _mark, print_rewrite_block  # noqa: E402

TIMELINES_DIR = WIKI / "timelines"
SOURCES_DIR = WIKI / "sources"

ADVISORY_MODE = True

REQUIRED_FRONTMATTER = {"title", "type", "last_updated"}
FLOW_SECTION = "## Flow Summary"

REQUIRED_KEYS = ("schema", "source_indexed")

# A dated `### YYYY` header (year section).
YEAR_HEADER_RE = re.compile(r"^###\s+\d{4}\b", re.MULTILINE)
# Timeline dated entry: "- **2026-05** ..." / "- ★ **2026-05-13** — ...".
# Shared _lib definitions — the builder (_build/overlays.py) and this lint must
# agree on which lines are dated entries, incl. the `**YYYY (planned)**` future
# anchor, or the path/region flavor verdict diverges between lint and build.
TL_ENTRY_RE = TIMELINE_ENTRY_RE
DATE_ONLY_RE = TIMELINE_DATE_ONLY_RE
# First wikilink in an entry body, stripping pipe alias / `#` anchor.
ANY_LINK_RE = WIKILINK_STEM_RE


def _is_source_link(target: str) -> bool:
    """First link is source-indexed iff `wiki/sources/<target>.md` exists.

    Mirrors the builder's `_is_source` outcome for the common case (a raw
    source-id slug). Entity/concept names (`[[Docker]]`) have no sources file,
    so they read as entity-led — exactly the region-producing case to flag.
    """
    return (SOURCES_DIR / f"{target.strip()}.md").is_file()


def _dated_entries(body: str) -> list[tuple[str, str | None]]:
    """Return [(date_str, first_link|None)] for each pure-date `### YYYY` entry."""
    out: list[tuple[str, str | None]] = []
    for m in TL_ENTRY_RE.finditer(body):
        date_str, rest = m.group(1), m.group(2)
        if not DATE_ONLY_RE.match(date_str):
            continue  # Flow Summary range label, not a dated entry
        lm = ANY_LINK_RE.search(rest)
        out.append((date_str.strip(), lm.group(1) if lm else None))
    return out


def _evaluate(rel: str, slug: str, content: str) -> dict:
    fm = parse_frontmatter(content)
    body = strip_code(strip_frontmatter(content))

    flow_present = bool(re.search(rf"^{re.escape(FLOW_SECTION)}\s*$", body, re.MULTILINE))
    year_present = bool(YEAR_HEADER_RE.search(body))
    schema_pass = flow_present and year_present
    fm_missing = sorted(f for f in REQUIRED_FRONTMATTER if not fm.get(f))

    entries = _dated_entries(body)
    src_n = sum(1 for _d, link in entries if link and _is_source_link(link))
    hub_n = len(entries) - src_n
    # Mirror the builder: a timeline is path (source-indexed) iff source-led
    # entries strictly outnumber entity-led ones. Empty → not source-indexed.
    source_indexed_pass = src_n > hub_n and src_n > 0

    # tool-call markup leak — hard-gated even under ADVISORY_MODE, as in
    # `synthesis.py`. A stray `</invoke>` fragment on a published page is an
    # accident rather than a content defect, and this is the target-scoped check
    # recommended after an edit, so a PASS here ships it.
    markup_leaks = MARKUP_LEAK_RE.findall(body)

    # frontmatter `type` value — hard-gated in the MarkupLeak tier. Outside
    # `_build/graph.py` META_NODE_TYPES the page is pulled in as a graph **node**
    # (invisible in the UI, but it skews degree and pathfinding); outside the
    # `_build/dependencies.py` upstream branch staleness goes quiet on it. A missing
    # value fails too — `_title_and_type` fills `unknown`, outside both sets.
    # `hub schema` checks this field for `wiki/timelines/` as well (and repairs it
    # on --fix), but the author's self-VERIFY0 runs this group alone, so without
    # this gate the mismatch clears the authoring gate and surfaces only later.
    actual_type = fm.get("type")

    return {
        "rel": rel,
        "slug": slug,
        "schema": (schema_pass, flow_present, year_present),
        "fm_missing": fm_missing,
        "source_indexed": (source_indexed_pass, src_n, hub_n, len(entries)),
        "markup": (len(markup_leaks) == 0, len(markup_leaks), markup_leaks[:5]),
        "page_type": (actual_type == "timeline", actual_type, "timeline"),
    }


def _print_per_file(r: dict) -> None:
    schema_pass, flow, year = r["schema"]
    si_pass, src_n, hub_n, total = r["source_indexed"]
    flavor = "path" if si_pass else "region"
    print(f"{r['rel']}:")
    print(
        f"  [Rubric] S1 schema={'FlowSummary' if flow else '—'}+{'YYYY' if year else '—'} {_mark(schema_pass)}  "
        f"SourceIndexed src={src_n}/hub={hub_n}/total={total} → {flavor} {_mark(si_pass)}  "
        f"MarkupLeak={r['markup'][1]} {_mark(r['markup'][0])}  "
        f"Type={_mark(r['page_type'][0])}"
    )
    if r["fm_missing"]:
        print(f"  [Rubric] frontmatter missing: {r['fm_missing']}")
    if not si_pass and total:
        print(f"  [Rubric] region regression — make each dated entry's first link a [[source-id]] (entity-led {hub_n})")
    if not r["markup"][0]:
        print(f"  [BLOCKER] tool-call markup leak (do not publish): {r['markup'][2]}")
    if not r["page_type"][0]:
        print(f"  [BLOCKER] frontmatter `type` is `{r['page_type'][1] or '(missing)'}` — "
              f"expected `{r['page_type'][2]}` (do not publish)")


def _print_corpus_summary(results: list[dict]) -> None:
    total = len(results)
    if total == 0:
        print("No timeline files found.")
        return

    def pct(n: int) -> str:
        return f"{n}/{total} ({100 * n // total}%)"

    print(f"Timeline schema diagnosis — {total} files")
    print(f"  S1 schema-sections  PASS={pct(sum(1 for r in results if r['schema'][0]))}")
    print(f"  SourceIndexed(path) PASS={pct(sum(1 for r in results if r['source_indexed'][0]))}")
    region = [r for r in results if not r["source_indexed"][0]]
    if region:
        print(f"\n  region-flavor timelines ({len(region)}) — to convert to source-indexed:")
        for r in region:
            _p, src_n, hub_n, tot = r["source_indexed"]
            print(f"    {r['slug']} — src={src_n}/hub={hub_n}/total={tot}")
    # markup and type sit outside REQUIRED_KEYS but still exit 1, so the reasons have
    # to be shown here — and before the advisory notice, or the line saying "exit 0" is
    # followed by the reason the run actually exits 1.
    leaks = [r["slug"] for r in results if not r["markup"][0]]
    if leaks:
        print()
        print(f"  [BLOCKER] tool-call markup leak in {len(leaks)} file(s) (do not publish): {leaks}")
    for r in [r for r in results if not r["page_type"][0]]:
        print()
        print(f"  [BLOCKER] {r['rel']}: frontmatter `type` is `{r['page_type'][1] or '(missing)'}` — "
              f"expected `{r['page_type'][2]}` (do not publish)")
    if ADVISORY_MODE:
        print(
            "\n  [Advisory mode] seed calibration not yet complete — a Rubric FAIL does "
            "not change the exit code; a MarkupLeak or Type blocker above still exits 1. "
            "See .claude/layers/timeline.md → Migration."
        )


def _skeleton(slug: str) -> str:
    return (
        f'---\ntitle: "Timeline: {slug}"\ntype: timeline\ntags: []\n'
        f"last_updated: YYYY-MM-DD\n---\n\n"
        f"## Timeline: [[{slug}]] (N entries)\n\n## Flow Summary\n\n"
        f"**Trajectory overview**: _TODO: phase → phase arrow trajectory._\n\n"
        f"- **YYYY~YYYY phase name**: _TODO: one paragraph per phase._\n\n"
        f"**Latest state**: _TODO._\n\n---\n\n"
        f"### YYYY (N)\n- **YYYY-MM-DD** [[source-id]] — _TODO: one-line event._\n"
    )


def _print_rewrite_block(slug: str, path: Path, exists: bool) -> None:
    print_rewrite_block(
        "timeline", slug, path, exists, "L2-2 standalone timeline",
        [
            "Read .claude/layers/timeline.md (Authoring + Rubric)",
            f"Read {path.as_posix()} (current state)",
            "Make each dated entry source-indexed as `- **YYYY-MM-DD** [[source-id]] — one line` (keep [[entity]] only for historical anchors with no source)",
            "`## Flow Summary` trajectory overview · phase paragraphs · latest state",
            "self-VERIFY₀: `python tools/lint.py timeline " + slug + "` → confirm flavor=path",
        ],
        "timeline", "iterate until the bar is met (qualitative review is the desk's VERIFY₂)")


def run(target: str | None = None, fix: bool = False, **_kwargs) -> int:
    if not TIMELINES_DIR.is_dir():
        print(f"ERROR: {TIMELINES_DIR} not found.", file=sys.stderr)
        return 2

    if target:
        slug = target.removesuffix(".md")
        path = TIMELINES_DIR / f"{slug}.md"
        # A timeline slug is an entity/concept stem (`AgenticAI`), so
        # `safe_slug_path`'s kebab-case check would reject every valid input.
        # What has to be blocked is `../` escape, so check directory containment
        # only.
        if path.parent.resolve() != TIMELINES_DIR.resolve():
            print(f"ERROR: unsafe target: {target!r}", file=sys.stderr)
            return 2
        if fix and not path.is_file():
            atomic_write_text(path, _skeleton(slug))
            print(f"Created skeleton: {path.as_posix()}")
            _print_rewrite_block(slug, path, exists=False)
            return 0
        if not path.is_file():
            print(f"ERROR: timeline file not found: {path}", file=sys.stderr)
            return 2
        content = read_text_cached(path)
        result = _evaluate(f"timelines/{slug}.md", slug, content)
        _print_per_file(result)
        if fix:
            _print_rewrite_block(slug, path, exists=True)
        if not result["markup"][0]:
            return 1  # markup leak hard-gates even in advisory mode
        if not result["page_type"][0]:
            return 1  # type mismatch hard-gates even in advisory mode
        if ADVISORY_MODE:
            return 0
        return 1 if any(not result[k][0] for k in REQUIRED_KEYS) else 0

    results = []
    for path, content in iter_md(TIMELINES_DIR):
        results.append(_evaluate(f"timelines/{path.name}", path.name[:-3], content))
    _print_corpus_summary(results)
    if any(not r["markup"][0] for r in results):
        return 1  # markup leak hard-gates even in advisory mode
    if any(not r["page_type"][0] for r in results):
        return 1  # type mismatch hard-gates even in advisory mode
    if ADVISORY_MODE:
        return 0
    return 1 if any(any(not r[k][0] for k in REQUIRED_KEYS) for r in results) else 0
