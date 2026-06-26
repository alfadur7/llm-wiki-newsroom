"""Shared helpers for L2-3/L2-4 schema lint modules.

Extracted from the former `content_schema.py` monolith when the module was
decomposed into axis-specific modules:
  - `overview.py`      — landscape axis (overviews/ + overview.md)
  - `contradiction.py` — conflict axis (contradictions/<theme>.md)

These helpers are axis-agnostic file-level schema checks:
  * frontmatter field presence
  * H2 section presence
  * AUTO marker presence + migration

Keeping the helpers in one place prevents drift between the two axis
modules when schema rules evolve (e.g. adding a required frontmatter field
that applies to both overview and contradiction files).
"""
from __future__ import annotations

import re
from pathlib import Path


def has_auto_marker(content: str, name: str) -> bool:
    return re.search(rf"<!--\s*AUTO:{re.escape(name)}\s*BEGIN\s*-->", content) is not None


def check_frontmatter(fm: dict, required: set[str], path: Path) -> list[str]:
    issues: list[str] = []
    for field in required:
        if field not in fm or not fm[field]:
            issues.append(f"  {path.name}: frontmatter missing `{field}`")
    return issues


def check_sections(content: str, required: tuple[str, ...], path: Path) -> list[str]:
    issues: list[str] = []
    for sec in required:
        if sec not in content:
            issues.append(f"  {path.name}: section missing `{sec}`")
    return issues


def check_auto_markers(content: str, markers: tuple[str, ...], path: Path) -> list[str]:
    missing: list[str] = []
    for m in markers:
        if not has_auto_marker(content, m):
            missing.append(f"  {path.name}: AUTO:{m} marker missing")
    return missing


def migrate_markers(content: str, markers: tuple[str, ...]) -> tuple[str, list[str]]:
    """Insert missing AUTO markers into a file.

    - AUTO:SOURCES: if the file already has a `## Sources` section, wrap
      it in the markers so subsequent run_pages regenerates the list.
      Otherwise append an empty marker block.
    - Non-sources markers (e.g. AUTO:MEMBERS / AUTO:CLAIMS): append empty
      marker block before the AUTO:SOURCES position (or at end of file).

    Returns (new_content, markers_added).
    """
    added: list[str] = []
    new_content = content

    if "SOURCES" in markers and not has_auto_marker(new_content, "SOURCES"):
        sources_match = re.search(r"(\n## Sources\s*\n.*?)(?=\n##\s|\Z)", new_content, re.DOTALL)
        block_begin = "<!-- AUTO:SOURCES BEGIN -->"
        block_end = "<!-- AUTO:SOURCES END -->"
        if sources_match:
            section = sources_match.group(1).rstrip()
            wrapped = f"\n{block_begin}\n{section}\n{block_end}\n"
            new_content = new_content[:sources_match.start()] + wrapped + new_content[sources_match.end():]
        else:
            new_content = new_content.rstrip() + f"\n\n{block_begin}\n## Sources\n{block_end}\n"
        added.append("SOURCES")

    sources_begin_match = re.search(r"<!--\s*AUTO:SOURCES\s*BEGIN\s*-->", new_content)
    insert_anchor = sources_begin_match.start() if sources_begin_match else len(new_content.rstrip())

    pending_blocks: list[str] = []
    for m in markers:
        if m == "SOURCES":
            continue
        if has_auto_marker(new_content, m):
            continue
        pending_blocks.append(f"<!-- AUTO:{m} BEGIN -->\n<!-- AUTO:{m} END -->")
        added.append(m)

    if pending_blocks:
        block = "\n\n".join(pending_blocks)
        pre = new_content[:insert_anchor].rstrip()
        post = new_content[insert_anchor:]
        new_content = pre + "\n\n" + block + "\n\n" + post.lstrip()

    return new_content, added
