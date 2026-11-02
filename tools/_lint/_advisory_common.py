"""Shared primitives for the advisory content-lint modules (source ·
synthesis · trail · overview · contradiction).

The three content lints (source/synthesis/trail) and the two axis lints
(overview/contradiction) have type-specific metric sets, so they don't share
the renderers themselves — what they share are idioms: the ✅/⚠️ mark, the
`_`-excluding corpus walk (cached read), and the banner / execution-order /
roster-threshold frame of the `--fix` rewrite instruction block. Only those
idioms are unified here.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import read_text_cached  # noqa: E402
sys.path.insert(0, str(Path(__file__).parent))
from _manifest_counts import counts as _roster_counts, threshold_label  # noqa: E402

# L1 (bare/un-aliased wikilink slug) detection — single definition shared by the
# source·synthesis·trail content lints (was triple-defined). A `[[slug]]` whose
# stem is >= L1_MIN_SLUG_LEN chars is machine-looking and should carry a display alias.
L1_MIN_SLUG_LEN = 10
L1_RAW_SLUG_RE = re.compile(r"\[\[([a-z][a-z0-9\-]{" + str(L1_MIN_SLUG_LEN - 1) + r",})\]\]")


def mark(ok) -> str:
    """Rubric advisory PASS/FAIL glyph; None = not applicable (—)."""
    if ok is None:
        return "—"
    return "✅" if ok else "⚠️"


# The wiki's internal schema leaking into a synthesis page's body (theme ·
# aggregate · overview). internal = source `## Connections` typing, section names
# and classifier fields; grade_tag = evidence-grade tags. Readers can decode
# neither — a grade is written as attribution ("X's analysis"). The Korean
# alternatives are the WIKI_LANG=ko schema markers; they never match English text.
SCHEMA_INTERNAL_RE = re.compile(
    r"\b(?:cites|references|contradicts|defines)\s*:"
    r"|`##\s*(?:Connections|Key Claims|Key Quotes|연결|주요 주장|주요 인용)`"
    r"|\btype\s*=\s*(?:real|soft|superseded|related)\b"
    r"|\b(?:evidence_strength|type_score)\s*[=\d]"
)
SCHEMA_GRADE_TAG_RE = re.compile(r"\[(?:fact|analysis|forecast|자료|분석|전망)\]")


def schema_leak_line(text: str, indent: str = "    ") -> str | None:
    """One body-schema-leak advisory line, or None when there is nothing to report."""
    internal = len(SCHEMA_INTERNAL_RE.findall(text))
    grade = len(SCHEMA_GRADE_TAG_RE.findall(text))
    if not (internal or grade):
        return None
    return f"{indent}[Advisory] schema leak: internal={internal} grade_tag={grade} ⚠️"


def iter_md(directory: Path):
    """Walk the `_`-excluding .md corpus — yields (path, cached text)."""
    for path in sorted(directory.glob("*.md")):
        if path.name.startswith("_"):
            continue
        yield path, read_text_cached(path)


def print_rewrite_block(
    group: str,
    slug: str,
    path: Path,
    exists: bool,
    target_desc: str,
    steps: list[str],
    roster_type: str,
    final_note: str,
) -> None:
    """Common frame for the `--fix` Claude rewrite instruction block.

    Banner + Target + (when new) skeleton guidance + numbered execution order +
    roster-threshold closing line. Type-specific differences are injected via
    the steps/final_note strings.
    """
    print("=" * 72)
    print(f"[/wiki-lint {group} {slug} --fix] Claude rewrite instruction block")
    print("=" * 72)
    print(f"Target: {path.as_posix()} ({target_desc})")
    if not exists:
        print("Status: new — skeleton created. Author the EDITOR block in the order below.")
    print()
    print("Execution order (Claude):")
    for i, step in enumerate(steps, 1):
        print(f"  {i}. {step}")
    p = _roster_counts(roster_type)
    print(f"  {len(steps) + 1}. {threshold_label(p)} {final_note}")
    print()
