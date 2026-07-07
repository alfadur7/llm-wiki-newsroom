"""L2-2 hub frontmatter + body schema lint — entities / concepts / timelines.

Added during the lint group refactor (2026-04-19) to cover the previously
unchecked L2-2 hub files. .claude/layers/hub.md requires every
subdirectory page to carry: title · type · tags · sources · last_updated.
Extended 2026-04-21 with `### Entity/Concept Body Structure` enforcement —
entity/concept pages must include `## Overview` (lead section) + `## Connections`
(bottom section) + body ≥ 200 chars, per the strict convention codified after
corpus measurement (de facto standard, 90~99% compliance). This module enforces
both contracts on the three hub directories.

Scope boundary: timeline body structure is not enforced here (timeline
narrative format differs — content is chronology-oriented, not entity
summary).

--fix mode auto-completes two deterministic fields only:
  * `type`: inferred from the directory (entities/→entity, concepts/→concept,
    timelines/→timeline). Either inserted when missing, or corrected when
    mismatched with the directory.
  * `last_updated`: inferred from `git log -1 --format=%cs -- <path>`.
    Falls back to today's date when git is unavailable.

`title`, `tags`, `sources` are NEVER auto-filled — each requires semantic
judgment (title from filename is unreliable in a Korean/English mixed
repo, tags are domain-dependent, and `sources` needs a wiki-wide scan to
avoid overwriting authored values). Body-section violations are also
reported only — `## Overview` / `## Connections` content requires domain judgment
unsuited to mechanical lint.
"""
from __future__ import annotations

import re
import sys
from datetime import date as _date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import FRONTMATTER_BLOCK_RE as FRONTMATTER_RE, WIKI, atomic_write_text, korean_mode, parse_frontmatter, read_text_cached  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from _schema_common import check_frontmatter  # noqa: E402
from _hub_common import iter_hub_files  # noqa: E402
from _editor_date import last_commit_date  # noqa: E402

ENTITIES_DIR = WIKI / "entities"
CONCEPTS_DIR = WIKI / "concepts"
TIMELINES_DIR = WIKI / "timelines"

# Required frontmatter fields per L2-2 hub type. Entities/concepts need
# `sources` because they index the source reflections citing them.
# Timelines are narrative aggregations of the entity's story across
# sources rather than source-indexed stubs, so a global `sources:` list
# would duplicate what the body already cites inline via [[wikilinks]].
# Keeping the field absent also avoids noisy lint failures for timeline
# stubs that cannot easily enumerate every contributing source.
# An entity is classified as person/org/product via `kind` (person|org|product)
# — because the hub-promotion policy treats people differently from orgs/products
# (naming.md entity classification, hub.md ②′). concept·timeline are a single kind
# and so don't carry a kind.
VALID_ENTITY_KINDS = {"person", "org", "product"}
HUB_REQUIRED_BY_TYPE: dict[str, set[str]] = {
    "entity":   {"title", "type", "kind", "tags", "sources", "last_updated"},
    "concept":  {"title", "type", "tags", "sources", "last_updated"},
    "timeline": {"title", "type", "tags", "last_updated"},
}

HUB_SPECS = [
    (ENTITIES_DIR, "entities", "entity"),
    (CONCEPTS_DIR, "concepts", "concept"),
    (TIMELINES_DIR, "timelines", "timeline"),
]


# Hybrid-frontmatter corruption guard. Pattern:
#     sources: [a, b, c]
#     - orphan_1
#     - orphan_2
# Any bullet lines that follow an inline-array `sources:[...]` value are
# silently dropped by `tools/_lib.py:parse_frontmatter` (the parser resets
# current_list_key=None after a flow value, never resuming block-list
# continuation). Prior to 2026-04-21 this silently removed 820 slugs across
# 42 hub files from graph/backlinks/cluster assignment; a one-off recovery
# restored them and this guard prevents regression: any reintroduction of
# the hybrid pattern is a schema FAIL. `\s*` before the bullet: indented
# orphan bullets (the block-list shape Obsidian emits) are dropped by the
# parser exactly like column-0 ones, so both must trip the guard. A following
# `key:` line breaks the match, so a legitimate next field never false-positives.
HYBRID_FRONTMATTER_RE = re.compile(
    r"^sources:\s*\[[^\]]*\]\s*\n\s*-\s+",
    re.MULTILINE,
)

# Entity/Concept body structure requirements (CLAUDE.md → Entity/Concept
# Body Structure, codified 2026-04-21). Strict mode — enforced at FAIL level
# now that all 423 files were migrated to compliance in prior commits.
SECTION_GAEYO_RE = re.compile(r"^##\s+Overview\s*$", re.MULTILINE)
SECTION_YEONGYEOL_RE = re.compile(r"^##\s+Connections\s*$", re.MULTILINE)
# Legacy section name from the pre-normalization Korean corpus. CLAUDE.md
# mandates `## Connections` as the canonical form; `## 위키 연결` (and prefix
# variants like `## 위키 연결 문서`/`## 위키 연결 페이지`) are deprecated synonyms.
# `--fix` rewrites the bare form in place; prefix variants (where the legacy
# heading sits alongside a canonical `## Connections`, indicating a duplicate residual
# section) are flagged for manual review since safe auto-removal would require
# body diff judgment. Gated behind korean_mode() like the Hangul-title check —
# the legacy heading only occurs in WIKI_LANG=ko corpora.
SECTION_LEGACY_YEONGYEOL_RE = re.compile(r"^##\s+위키 연결\s*$", re.MULTILINE)
SECTION_LEGACY_YEONGYEOL_PREFIX_RE = re.compile(
    r"^##\s+위키 연결(?:\s+\S.*)?$", re.MULTILINE
)
# Body length floor: ≥ 200 chars of non-frontmatter content. Conservative
# vs the observed p10 (entities 297 · concepts 483) so early stubs aren't
# blocked prematurely.
MIN_BODY_CHARS = 200

# Body structure is checked for entity and concept only. Timeline pages
# follow a chronology format (year-anchored events) that uses different
# section names — enforcing `## Overview` / `## Connections` on timelines would force
# an unnatural fit.
BODY_CHECKED_TYPES = {"entity", "concept"}


def _has_hangul(s: str) -> bool:
    """True iff `s` contains at least one Hangul syllable (U+AC00–U+D7A3).

    Used to detect Korean-named entities — file stem in Hangul signals
    "Korean entity that goes by a Korean name in the wiki" per CLAUDE.md
    Naming Conventions. The frontmatter `title` must then also include
    Hangul (canonical Korean name first, optional `(English Name)` after)
    so the graph node label and Obsidian page title stay in Korean.
    Bilingual titles like "신한금융그룹 (Shinhan Financial Group)" pass.
    English-only titles like "KBFinancialGroup" fail.
    """
    return any(0xAC00 <= ord(c) <= 0xD7A3 for c in s)


def _inject_or_set_field(content: str, key: str, value: str) -> str:
    """Insert or replace `key: value` inside the YAML frontmatter block.

    Handles three cases:
      1. No frontmatter at all      → prepend a minimal `---\n<key>: <value>\n---\n`
      2. Frontmatter exists, key missing → append `<key>: <value>` before the closing `---`
      3. Frontmatter has key        → replace its value line

    Only used for deterministic fields (type, last_updated). String values
    are inserted verbatim; the caller is responsible for YAML-safety.
    """
    m = FRONTMATTER_RE.match(content)
    if not m:
        return f"---\n{key}: {value}\n---\n\n" + content

    block = m.group(1)
    # Line-level replace or insert
    key_re = re.compile(rf"^{re.escape(key)}\s*:\s*.*$", re.MULTILINE)
    if key_re.search(block):
        new_block = key_re.sub(f"{key}: {value}", block, count=1)
    else:
        new_block = block.rstrip() + f"\n{key}: {value}"
    return f"---\n{new_block}\n---\n" + content[m.end():]


def _apply_auto_fix(path: Path, fm: dict, expected_type: str) -> tuple[bool, list[str]]:
    """Apply deterministic frontmatter fixes. Returns (changed, actions)."""
    actions: list[str] = []
    content = read_text_cached(path)
    new_content = content

    # type: insert if missing, correct if mismatched.
    ft = fm.get("type")
    if not ft:
        new_content = _inject_or_set_field(new_content, "type", expected_type)
        actions.append(f"type=<missing> → {expected_type}")
    elif ft != expected_type:
        new_content = _inject_or_set_field(new_content, "type", expected_type)
        actions.append(f"type={ft} → {expected_type}")

    # last_updated: insert if missing.
    if not fm.get("last_updated"):
        commit_date = last_commit_date(path) or _date.today().isoformat()
        new_content = _inject_or_set_field(new_content, "last_updated", commit_date)
        actions.append(f"last_updated=<missing> → {commit_date}")

    # Legacy section heading (ko-mode): rewrite the legacy `## 위키 연결` heading
    # to the canonical Connections form (CLAUDE.md canonical form). Deterministic
    # body fix — only affects the heading line; body content is preserved verbatim.
    if korean_mode() and SECTION_LEGACY_YEONGYEOL_RE.search(new_content):
        new_content = SECTION_LEGACY_YEONGYEOL_RE.sub("## Connections", new_content)
        actions.append("## 위키 연결 → ## Connections (legacy heading normalized)")

    if new_content != content:
        atomic_write_text(path, new_content)
        return True, actions
    return False, actions


def _check_body(content: str, path: Path, expected_type: str, dir_label: str) -> list[str]:
    """Check Entity/Concept Body Structure compliance.

    Enforced only for types in BODY_CHECKED_TYPES. Returns issue lines for:
      - `## Overview` section missing
      - `## Connections` section missing
      - body content below MIN_BODY_CHARS (frontmatter-stripped, whitespace
        counted as-is — a hub with only section headers and no prose still
        has some char count, but falls well under 200)
    """
    if expected_type not in BODY_CHECKED_TYPES:
        return []
    issues: list[str] = []
    fm_match = FRONTMATTER_RE.match(content)
    body = content[fm_match.end():] if fm_match else content

    if not SECTION_GAEYO_RE.search(body):
        issues.append(
            f"  {dir_label}/{path.name}: missing required `## Overview` section "
            f"(.claude/layers/hub.md)"
        )
    has_canonical = bool(SECTION_YEONGYEOL_RE.search(body))
    has_legacy_bare = korean_mode() and bool(SECTION_LEGACY_YEONGYEOL_RE.search(body))
    has_legacy_prefix = korean_mode() and bool(SECTION_LEGACY_YEONGYEOL_PREFIX_RE.search(body))
    has_legacy_variant = has_legacy_prefix and not has_legacy_bare
    if not has_canonical and not has_legacy_bare:
        issues.append(
            f"  {dir_label}/{path.name}: missing required `## Connections` section "
            f"(.claude/layers/hub.md)"
        )
    elif has_legacy_bare and not has_canonical:
        issues.append(
            f"  {dir_label}/{path.name}: legacy `## 위키 연결` heading — "
            f"normalize to `## Connections` (run with --fix to auto-rewrite)"
        )
    if has_legacy_variant:
        issues.append(
            f"  {dir_label}/{path.name}: legacy `## 위키 연결 …` prefix variant "
            f"alongside canonical `## Connections` — duplicate residual section requires "
            f"manual merge or removal (auto-fix declined to avoid body data loss)"
        )
    body_len = len(body.strip())
    if body_len < MIN_BODY_CHARS:
        issues.append(
            f"  {dir_label}/{path.name}: body length {body_len} chars < {MIN_BODY_CHARS} chars floor "
            f"(stub minimum; expand prose or connections)"
        )
    return issues


def _check_directory(directory: Path, dir_label: str, expected_type: str, fix: bool) -> tuple[list[str], int]:
    issues: list[str] = []
    fixed = 0
    if not directory.exists():
        return issues, 0

    for path in iter_hub_files(directory):
        content = read_text_cached(path)
        fm = parse_frontmatter(content)

        if fix:
            changed, actions = _apply_auto_fix(path, fm, expected_type)
            if changed:
                fixed += 1
                print(f"  ~ {dir_label}/{path.name}: {', '.join(actions)}")
                # Re-parse frontmatter after the write so subsequent reporting
                # reflects the corrected state.
                fm = parse_frontmatter(read_text_cached(path))
                content = read_text_cached(path)

        required = HUB_REQUIRED_BY_TYPE.get(expected_type, set())
        for issue in check_frontmatter(fm, required, path):
            issues.append(issue.replace(f"  {path.name}", f"  {dir_label}/{path.name}"))

        # tags non-blank content. check_frontmatter catches missing/`[]` (falsy)
        # but passes `tags: [""]` — a non-empty list of blank strings. Mirror the
        # source-page T1 gate's `any(str(t).strip())` so hub tags verification is
        # equally strict (graph node labels carry these tags as meta badges).
        if "tags" in required:
            tv = fm.get("tags")
            if isinstance(tv, list) and tv and not any(str(t).strip() for t in tv):
                issues.append(
                    f"  {dir_label}/{path.name}: frontmatter `tags` has no non-blank "
                    f"entries (whitespace-only) — fill semantic tags"
                )

        ft = fm.get("type")
        if ft and ft != expected_type:
            issues.append(
                f"  {dir_label}/{path.name}: frontmatter `type: {ft}` mismatches directory "
                f"(expected `{expected_type}`)"
            )

        # Validate the entity `kind` value (a missing one is caught by `required` above). Block invalid values outside person/org/product.
        if expected_type == "entity":
            kind_val = fm.get("kind")
            if kind_val and kind_val not in VALID_ENTITY_KINDS:
                issues.append(
                    f"  {dir_label}/{path.name}: frontmatter `kind: {kind_val}` invalid "
                    f"(expected one of {sorted(VALID_ENTITY_KINDS)})"
                )

        # Korean-named hub → Korean title alignment. WIKI_LANG=ko only: a Hangul
        # filename signals the Korean entity convention, so the title must then
        # carry Hangul too (canonical Korean name first, optional `(English)`
        # after) so the graph node label and Obsidian page title don't drift to
        # English. Without this guard, frontmatter like `title: "KBFinancialGroup"`
        # on a `KB금융그룹.md` file silently produces an English graph label even
        # though the filename is Korean (regression caught 2026-05-04 across 8
        # entity files). Gated behind korean_mode() like hub_voice.py — on the
        # English-native default a stray Hangul filename is not forced to a
        # Hangul title (it would be a hard FAIL otherwise).
        title_val = fm.get("title", "") or ""
        if korean_mode() and _has_hangul(path.stem) and not _has_hangul(title_val):
            issues.append(
                f"  {dir_label}/{path.name}: Hangul filename → frontmatter "
                f"`title: \"{title_val}\"` is English-only (CLAUDE.md → "
                f"Language Rules: the `title` value must be written in Hangul). "
                f"Use Korean primary, optional `(English Name)` parenthetical "
                f"e.g. `\"{path.stem} (English Name)\"`."
            )

        # Hybrid-frontmatter corruption guard (scan raw text — parser silently
        # drops orphan bullets, so fm dict alone cannot detect this).
        fm_match = FRONTMATTER_RE.match(content)
        if fm_match and HYBRID_FRONTMATTER_RE.search(fm_match.group(1)):
            issues.append(
                f"  {dir_label}/{path.name}: hybrid frontmatter — "
                f"`sources:[...]` inline array followed by `- orphan` bullets "
                f"(parser silently drops bullets; convert the whole `sources:` "
                f"field to a pure block list — remove the inline array and "
                f"list every slug as `  - <slug>` under it)"
            )

        # Entity/Concept body structure (## Overview + ## Connections + ≥200 chars).
        issues.extend(_check_body(content, path, expected_type, dir_label))

    return issues, fixed


def run(fix: bool = False) -> int:
    """Entry point for `python tools/lint.py hub schema [--fix]`.

    --fix auto-completes deterministic fields (type, last_updated) only.
    title/tags/sources remain as reported issues — they require semantic
    judgment unsuitable for mechanical lint.
    """
    all_issues: list[str] = []
    total_files = 0
    total_fixed = 0
    for directory, dir_label, expected_type in HUB_SPECS:
        if directory.exists():
            total_files += len(iter_hub_files(directory))
        issues, fixed = _check_directory(directory, dir_label, expected_type, fix)
        all_issues.extend(issues)
        total_fixed += fixed

    if fix and total_fixed:
        print(f"\n[hub schema --fix] {total_fixed} file(s) patched (type / last_updated)")

    if all_issues:
        print(f"\n[hub schema: {len(all_issues)} issue(s) across {total_files} L2-2 file(s)]")
        for i in all_issues:
            print(i)
        print("\nFAIL — L2-2 hub frontmatter deviations (.claude/layers/hub.md).")
        if not fix:
            print("       `--fix` auto-completes type + last_updated only; tags/sources/title stay manual.")
        return 1

    print(f"OK - L2-2 hub schema: frontmatter + body ({total_files} files: entities + concepts + timelines)")
    return 0


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true")
    args = ap.parse_args()
    sys.exit(run(fix=args.fix))
