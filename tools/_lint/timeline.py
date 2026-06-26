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

Advisory rollout: `ADVISORY_MODE = True` until the seed calibration batch
(the 6 remaining region timelines are converted). Mirrors `trail.py`.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import WIKI, atomic_write_text, parse_frontmatter, read_text_cached, strip_code, strip_frontmatter  # noqa: E402
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
# Timeline dated entry: "- **2026-05** ..." / "- ★ **2026년 5월 13일** — ...".
TL_ENTRY_RE = re.compile(r"^\s*-\s*(?:★\s*)?\*\*\s*([^*]+?)\s*\*\*\s*(.*)$", re.MULTILINE)
# A bold token that is a pure date (digits + date separators only), rejecting
# `## Flow Summary` range-label bullets (e.g. "2019~2021 기반 다지기" / "laying the groundwork").
DATE_ONLY_RE = re.compile(r"^\d{4}[\d\s\-.년월일]*$")
# First wikilink in an entry body, stripping pipe alias / `#` anchor.
ANY_LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")


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

    return {
        "rel": rel,
        "slug": slug,
        "schema": (schema_pass, flow_present, year_present),
        "fm_missing": fm_missing,
        "source_indexed": (source_indexed_pass, src_n, hub_n, len(entries)),
    }


def _print_per_file(r: dict) -> None:
    schema_pass, flow, year = r["schema"]
    si_pass, src_n, hub_n, total = r["source_indexed"]
    flavor = "path" if si_pass else "region"
    print(f"{r['rel']}:")
    print(
        f"  [Rubric] S1 schema={'FlowSummary' if flow else '—'}+{'YYYY' if year else '—'} {_mark(schema_pass)}  "
        f"SourceIndexed src={src_n}/hub={hub_n}/total={total} → {flavor} {_mark(si_pass)}"
    )
    if r["fm_missing"]:
        print(f"  [Rubric] frontmatter missing: {r['fm_missing']}")
    if not si_pass and total:
        print(f"  [Rubric] region regression — make each dated entry's first link a [[source-id]] (entity-led {hub_n})")


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
    if ADVISORY_MODE:
        print(
            "\n  [Advisory mode] seed calibration not yet complete — exit 0 even if "
            "files fail. See .claude/layers/timeline.md → Migration."
        )


def _skeleton(slug: str) -> str:
    return (
        f'---\ntitle: "Timeline: {slug}"\ntype: timeline\ntags: []\n'
        f"last_updated: YYYY-MM-DD\n---\n\n"
        f"## Timelines: [[{slug}]] (N)\n\n## Flow Summary\n\n"
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
        if ADVISORY_MODE:
            return 0
        return 1 if any(not result[k][0] for k in REQUIRED_KEYS) else 0

    results = []
    for path, content in iter_md(TIMELINES_DIR):
        results.append(_evaluate(f"timelines/{path.name}", path.name[:-3], content))
    _print_corpus_summary(results)
    if ADVISORY_MODE:
        return 0
    return 1 if any(any(not r[k][0] for k in REQUIRED_KEYS) for r in results) else 0
