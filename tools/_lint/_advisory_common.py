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

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import read_text_cached  # noqa: E402
sys.path.insert(0, str(Path(__file__).parent))
from _manifest_counts import counts as _roster_counts, threshold_label  # noqa: E402


def mark(ok) -> str:
    """Rubric advisory PASS/FAIL glyph."""
    return "✅" if ok else "⚠️"


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
