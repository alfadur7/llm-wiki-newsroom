"""Published-content → build/governance-internal reference hygiene.

Wiki content shipped to RAG (root meta + entities·concepts·overviews·
contradictions·syntheses·timelines·trails) must not link into the repo's
build/governance tree — `.claude/`, `tools/`, `CLAUDE.md`, `raw/`, `log.md`.
Those targets are plumbing a Q&A reader can neither open nor needs; they leak
as self-meta into the exported corpus (the export dead-strips the link to plain
text, but the governance phrase still pollutes the prose).

This is the mirror of two existing guards:
  - `.claude/` guides must not carry decisions/external refs (claude-guideline-voice)
  - L2-2 hubs must not carry editor self-meta (`hub voice`)

Detection is link-based, which is false-positive-free: a *markdown link* whose
target resolves into the governance tree is always a self-reference. Plain-text
mentions of these names as a topic (e.g. Claude Code's `CLAUDE.md` memory file,
`SKILL.md`) are not links and are left alone.

No --fix: removing/rephrasing a governance reference is an authoring decision
(like `hub voice`). The check reports file·line·target for manual cleanup.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import WIKI, read_text_cached  # noqa: E402

# Content destined for the RAG export (sources are excluded — their bodies are
# not exported, only the one-line index). Root meta files are checked by name.
ROOT_META = ["overview.md", "contradiction.md", "index.md"]
CONTENT_SUBDIRS = [
    "entities", "concepts", "overviews", "contradictions",
    "syntheses", "timelines", "trails",
]

_MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_LEADING_DOTSLASH_RE = re.compile(r"^(?:\.\./)+|^\./")


def _is_governance_target(target: str) -> bool:
    """True when a markdown link target points into the build/governance tree."""
    t = target.split("#", 1)[0].strip()
    if not t or t.startswith(("http://", "https://", "mailto:")):
        return False
    t = _LEADING_DOTSLASH_RE.sub("", t)
    low = t.lower()
    return (
        low == "claude.md"
        or low.endswith("/claude.md")
        or low == "log.md"
        or low.startswith(".claude/")
        or low.startswith("tools/")
        or low.startswith("raw/")
    )


def _scan(path: Path) -> list[tuple[int, str]]:
    hits: list[tuple[int, str]] = []
    for i, line in enumerate(read_text_cached(path).split("\n"), 1):
        for target in _MD_LINK_RE.findall(line):
            if _is_governance_target(target):
                hits.append((i, target))
    return hits


def _content_files() -> list[Path]:
    files: list[Path] = []
    for name in ROOT_META:
        p = WIKI / name
        if p.exists():
            files.append(p)
    for sub in CONTENT_SUBDIRS:
        d = WIKI / sub
        if d.is_dir():
            files.extend(
                p for p in sorted(d.glob("*.md")) if not p.name.startswith("_")
            )
    return files


def run(**_kwargs) -> int:
    flagged: list[tuple[str, int, str]] = []
    for f in _content_files():
        for line_no, target in _scan(f):
            flagged.append((f.relative_to(WIKI).as_posix(), line_no, target))

    if not flagged:
        print("OK - no published content links into the build/governance tree")
        return 0

    print(f"FAIL - {len(flagged)} governance-internal link(s) in published content")
    print("(remove or rephrase — RAG readers cannot open these, and they leak as self-meta)")
    for rel, line_no, target in flagged:
        print(f"  {rel}:{line_no}  → ({target})")
    return 1


if __name__ == "__main__":
    sys.exit(run())
