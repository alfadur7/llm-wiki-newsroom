"""Trail page schema lint — `wiki/trails/<slug>.md` (L2-3 Path axis).

A trail is an ordered associative path through 5–12 hubs (Memex trail-blazing)
with a short through-line essay. This module checks the structural contract
codified in `.claude/layers/trail.md` and reuses the manifest roster for the
completion-criteria string (mirrors `synthesis.py` / `overview.py`).

Auto-measured structural (layers-owned, craft-free) criteria:
  * struct.schema-sections — `## Path` + `## Commentary` present
  * struct.path-links      — every `## Path` numbered item starts with `N. [[Hub]]`
  * struct.path-length     — 4 ≤ hop count ≤ 12
  * enc.slug-alias (L1)    — no raw ≥10-char kebab slug exposed without pipe alias

NOTE — trail frontmatter divergence: existing trails use `created:` (no
`last_updated`, no `sources:`). This lint accepts `created` as-is per the
recommended owner-gate default (match reality, not force the common schema).
Broken-link is delegated to `python tools/lint.py graph structure`.

Advisory rollout: `ADVISORY_MODE = True` until the seed calibration batch
(plan step 2). Mirrors `source.py` / `synthesis.py`.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import WIKI, atomic_write_text, parse_frontmatter, read_text_cached, section_body, strip_code, strip_frontmatter  # noqa: E402
sys.path.insert(0, str(Path(__file__).parent))  # tools/_lint/ — sibling import
from _advisory_common import L1_MIN_SLUG_LEN, L1_RAW_SLUG_RE, iter_md, mark as _mark, print_rewrite_block  # noqa: E402

TRAILS_DIR = WIKI / "trails"

ADVISORY_MODE = True

REQUIRED_FRONTMATTER = {"title", "type", "created"}
REQUIRED_SECTIONS = ("## Path", "## Commentary")
PATH_MIN, PATH_MAX = 4, 12

# struct.path-length is optional per _manifest.json trail.roster / trail.md —
# reported in the [Rubric]/PathLen output but never gates the exit code.
REQUIRED_KEYS = ("schema", "path_links", "slug_alias")

# A `## Path` numbered list item: `1. ...`, `12. ...`
PATH_ITEM_RE = re.compile(r"^\s*\d+\.\s+(.*)$", re.MULTILINE)
# Item must begin with a wikilink (allowing bold/pipe alias): `N. [[Hub]] — ...`
PATH_ITEM_LINKED_RE = re.compile(r"^\s*\d+\.\s+\*{0,2}\[\[")


def _evaluate(rel: str, slug: str, content: str) -> dict:
    fm = parse_frontmatter(content)
    body = strip_code(strip_frontmatter(content))

    sections_present = [h for h in REQUIRED_SECTIONS if re.search(rf"^{re.escape(h)}\s*$", body, re.MULTILINE)]
    schema_pass = len(sections_present) == len(REQUIRED_SECTIONS)
    fm_missing = sorted(f for f in REQUIRED_FRONTMATTER if not fm.get(f))

    # Path items in the `## Path` section.
    gyeongno = section_body(body, "Path")
    items = PATH_ITEM_RE.findall(gyeongno)
    linked = [ln for ln in gyeongno.splitlines() if PATH_ITEM_LINKED_RE.match(ln)]
    n_items = len(items)
    n_linked = len(linked)
    path_links_pass = n_items > 0 and n_linked == n_items
    path_length_pass = PATH_MIN <= n_items <= PATH_MAX

    l1_raw = L1_RAW_SLUG_RE.findall(body)
    slug_alias_pass = len(l1_raw) == 0

    return {
        "rel": rel,
        "slug": slug,
        "schema": (schema_pass, len(sections_present), len(REQUIRED_SECTIONS)),
        "fm_missing": fm_missing,
        "path_links": (path_links_pass, n_linked, n_items),
        "path_length": (path_length_pass, n_items),
        "slug_alias": (slug_alias_pass, l1_raw[:5]),
    }


def _print_per_file(r: dict) -> None:
    schema_pass, s_n, s_total = r["schema"]
    pl_pass, pl_n, pl_total = r["path_links"]
    plen_pass, plen_n = r["path_length"]
    sa_pass, sa_samples = r["slug_alias"]
    print(f"{r['rel']}:")
    print(
        f"  [Rubric] S1 sections={s_n}/{s_total} {_mark(schema_pass)}  "
        f"PathLinks={pl_n}/{pl_total} {_mark(pl_pass)}  "
        f"PathLen={plen_n} (4–12) {_mark(plen_pass)}  "
        f"L1 raw_slugs={len(sa_samples)} {_mark(sa_pass)}"
    )
    if r["fm_missing"]:
        print(f"  [Rubric] frontmatter missing: {r['fm_missing']}")
    if not sa_pass and sa_samples:
        print(f"  [Rubric] L1 raw slug samples: {sa_samples}")


def _print_corpus_summary(results: list[dict]) -> None:
    total = len(results)
    if total == 0:
        print("No trail files found.")
        return

    def pct(n: int) -> str:
        return f"{n}/{total} ({100 * n // total}%)"

    print(f"Trail schema diagnosis — {total} files")
    print(f"  S1 schema-sections  PASS={pct(sum(1 for r in results if r['schema'][0]))}")
    print(f"  PathLinks all-linked PASS={pct(sum(1 for r in results if r['path_links'][0]))}")
    print(f"  PathLen 4–12        PASS={pct(sum(1 for r in results if r['path_length'][0]))}")
    print(f"  L1 slug-alias clean PASS={pct(sum(1 for r in results if r['slug_alias'][0]))}")
    fails = [r for r in results if any(not r[k][0] for k in REQUIRED_KEYS)]
    if fails:
        print(f"\n  Non-compliant trails ({len(fails)}):")
        for r in fails:
            print(f"    {r['slug']} — {[k for k in REQUIRED_KEYS if not r[k][0]]}")
    if ADVISORY_MODE:
        print(
            "\n  [Advisory mode] seed calibration not yet complete — exit 0 even if "
            "files fail. See .claude/layers/trail.md → Migration."
        )


def _skeleton(slug: str) -> str:
    return (
        f'---\ntitle: "{slug}"\ntype: trail\ntags: []\ncreated: YYYY-MM-DD\n---\n\n'
        f"## Path\n\n1. [[Hub1]] — _TODO: one line on the starting point's role and transition._\n"
        f"2. [[Hub2]] — _TODO._\n3. [[Hub3]] — _TODO._\n4. [[Hub4]] — _TODO._\n\n"
        f"## Commentary\n\n_TODO: 1-2 paragraph through-line narrative — name the path's through-line and tension._\n"
    )


def _print_rewrite_block(slug: str, path: Path, exists: bool) -> None:
    print_rewrite_block(
        "trail", slug, path, exists, "L2-3 associative trail",
        [
            "Read .claude/layers/trail.md (Authoring + Rubric)",
            f"Read {path.as_posix()} (current state)",
            "Select 5-12 hubs in hop order → `## Path` numbered `N. [[Hub]] — role/transition commentary`",
            "`## Commentary` 1-2 paragraph through-line narrative (jrn.kicker)",
            "self-VERIFY₀: `python tools/lint.py trail " + slug + "`",
        ],
        "trail", "iterate until the bar is met (qualitative review is the desk's VERIFY₂)")


def run(target: str | None = None, fix: bool = False, **_kwargs) -> int:
    if not TRAILS_DIR.is_dir():
        print(f"ERROR: {TRAILS_DIR} not found.", file=sys.stderr)
        return 2

    if target:
        slug = target.removesuffix(".md")
        path = TRAILS_DIR / f"{slug}.md"
        if fix and not path.is_file():
            atomic_write_text(path, _skeleton(slug))
            print(f"Created skeleton: {path.as_posix()}")
            _print_rewrite_block(slug, path, exists=False)
            return 0
        if not path.is_file():
            print(f"ERROR: trail file not found: {path}", file=sys.stderr)
            return 2
        content = read_text_cached(path)
        result = _evaluate(f"trails/{slug}.md", slug, content)
        _print_per_file(result)
        if fix:
            _print_rewrite_block(slug, path, exists=True)
        if ADVISORY_MODE:
            return 0
        return 1 if any(not result[k][0] for k in REQUIRED_KEYS) else 0

    results = []
    for path, content in iter_md(TRAILS_DIR):
        results.append(_evaluate(f"trails/{path.name}", path.name[:-3], content))
    _print_corpus_summary(results)
    if ADVISORY_MODE:
        return 0
    return 1 if any(any(not r[k][0] for k in REQUIRED_KEYS) for r in results) else 0
