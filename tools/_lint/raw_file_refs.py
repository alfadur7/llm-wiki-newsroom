"""Source page → raw file reference integrity.

Every `wiki/sources/<slug>.md` frontmatter declares a `source_file:` value
pointing at the raw scrape under `raw/`. Two corruption patterns silently
break that link without producing a parse error:

  Smart-quote folding — an editor or copy step replaces typographic quotes
    ('U+2018, 'U+2019, "U+201C, "U+201D) with ASCII (', ") in the source_file
    value while the raw filename keeps the originals. `build.py index`
    normalizes quotes when emitting `_source_map.json::by_path`, but the
    raw-side lookup uses the un-normalized raw path, so the dedup map fails
    to match an obviously-identical filename.

  Quote stripping — the source_file value drops the quote characters
    entirely (e.g. `LG CNS, 금융 맞춤형 LLM 평가 도구 출시.md` instead of
    `LG CNS, 금융 맞춤형 'LLM 평가 도구' 출시.md`). Normalize-then-compare
    cannot recover this case; ingest sees the raw file as new even though a
    source page already exists for the same article.

Both patterns are bulk historical drift, not one-off authoring mistakes —
fixing them requires sweeping the whole sources/ tree against the raw/
tree, not editing pages one at a time.

--fix repairs every source_file value where the raw tree contains exactly
one file matching either the quote-normalized basename or (as a secondary
fallback) the basename with all quote characters stripped. Ambiguous
matches and basenames with no candidate are reported and left untouched
for human review.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import (  # noqa: E402
    FRONTMATTER_BLOCK_RE,
    REPO_ROOT,
    WIKI,
    atomic_write_text,
    normalize_quotes,
    parse_frontmatter,
    read_text_cached,
    real_source_files,
)

RAW = REPO_ROOT / "raw"
SOURCES = WIKI / "sources"

_TYPOGRAPHIC_QUOTES = "‘’“”"
# Backslash also stripped: a third corruption variant escapes ASCII quotes
# inside the YAML value (e.g. `\"...\"`), leaving stray backslashes that
# don't appear in the raw filename.
_STRIP_CHARS = _TYPOGRAPHIC_QUOTES + "'\"\\"

# Fuzzy match thresholds. A fourth corruption variant truncates or
# paraphrases the raw filename in source_file (omitting trailing publisher
# suffixes like "- 뉴스와이어", inserting/removing parenthetical
# annotations, swapping spacing). Token-set Jaccard catches these.
# Above HIGH: auto-fix candidate (still needs --fix opt-in).
# Between LOW and HIGH: SUGGESTION list (human review only).
_FUZZY_HIGH = 0.7
_FUZZY_LOW = 0.4

_TOKEN_SPLIT_RE = re.compile(r'["\'()<>·…,\-—–]+')


def _quote_stripped(s: str) -> str:
    return s.translate({ord(c): None for c in _STRIP_CHARS})


def _tokens(s: str) -> set[str]:
    """Token-set for Jaccard comparison. Strips punctuation, drops the
    trailing `md`/`pdf` extension token so ".md" itself is not a token."""
    folded = normalize_quotes(s)
    folded = _TOKEN_SPLIT_RE.sub(" ", folded)
    return {t for t in folded.split() if t and t.lower() not in {"md", "pdf"}}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _index_raw_tree() -> tuple[dict[str, list[str]], dict[str, list[str]], list[tuple[str, set[str]]]]:
    # Both indexes keep candidate LISTS: two raw files sharing a basename in
    # different subdirs must route to the AMBIGUOUS bucket, not last-wins.
    by_norm: dict[str, list[str]] = {}
    by_stripped: dict[str, list[str]] = {}
    by_tokens: list[tuple[str, set[str]]] = []
    if not RAW.exists():
        return by_norm, by_stripped, by_tokens
    for root, _dirs, files in os.walk(RAW):
        for f in files:
            if not (f.endswith(".md") or f.endswith(".pdf")):
                continue
            rel = Path(root, f).relative_to(REPO_ROOT).as_posix()
            by_norm.setdefault(normalize_quotes(f), []).append(rel)
            by_stripped.setdefault(_quote_stripped(f), []).append(rel)
            by_tokens.append((rel, _tokens(f)))
    return by_norm, by_stripped, by_tokens


def _best_fuzzy(sf_tokens: set[str], by_tokens: list[tuple[str, set[str]]]) -> tuple[str | None, float]:
    best: str | None = None
    best_score = 0.0
    for rel, raw_tokens in by_tokens:
        score = _jaccard(sf_tokens, raw_tokens)
        if score > best_score:
            best_score = score
            best = rel
    return best, best_score


_SOURCE_FILE_RE = re.compile(r"^source_file:\s*(.+?)\s*$", re.MULTILINE)


def _read_source_file(path: Path) -> str | None:
    # Canonical frontmatter parser — handles YAML quoting/unescaping and only
    # looks inside the frontmatter block (a body line starting `source_file:`
    # is not a field).
    val = parse_frontmatter(read_text_cached(path)).get("source_file")
    return val if isinstance(val, str) and val else None


def _replace_source_file(path: Path, new_value: str) -> None:
    text = read_text_cached(path)
    fm = FRONTMATTER_BLOCK_RE.match(text)
    if not fm:
        raise RuntimeError(f"no frontmatter block in {path}")
    # Substitute within the frontmatter only, so a body line that happens to
    # start with `source_file:` is never rewritten.
    new_fm, n = _SOURCE_FILE_RE.subn(f"source_file: {new_value}", fm.group(0), count=1)
    if n != 1:
        raise RuntimeError(f"could not replace source_file in {path}")
    atomic_write_text(path, new_fm + text[fm.end():])


def run(fix: bool = False, **_kwargs) -> int:
    if not SOURCES.exists():
        print("OK - no sources/ directory")
        return 0

    by_norm, by_stripped, by_tokens = _index_raw_tree()

    fixable: list[tuple[str, str, str]] = []
    ambiguous: list[tuple[str, str, list[str]]] = []
    suggestions: list[tuple[str, str, str, float]] = []
    no_match: list[tuple[str, str]] = []

    for p in real_source_files():
        sf = _read_source_file(p)
        if not sf:
            continue
        if (REPO_ROOT / sf).is_file():
            continue
        bn = os.path.basename(sf)
        bn_norm = normalize_quotes(bn)
        bn_stripped = _quote_stripped(bn)
        if bn_norm in by_norm:
            cands = by_norm[bn_norm]
            if len(cands) == 1:
                fixable.append((p.name, sf, cands[0]))
                continue
            ambiguous.append((p.name, sf, cands))
            continue
        if bn_stripped in by_stripped:
            cands = by_stripped[bn_stripped]
            if len(cands) == 1:
                fixable.append((p.name, sf, cands[0]))
                continue
            ambiguous.append((p.name, sf, cands))
            continue
        # Fuzzy fallback. Token-set Jaccard against the raw tree catches
        # cases where source_file paraphrases or truncates the original
        # filename (e.g. drops "- 뉴스와이어", inserts "에서 본", swaps
        # parenthetical annotations).
        best, score = _best_fuzzy(_tokens(bn), by_tokens)
        if best is not None and score >= _FUZZY_HIGH:
            fixable.append((p.name, sf, best))
            continue
        if best is not None and score >= _FUZZY_LOW:
            suggestions.append((p.name, sf, best, score))
            continue
        no_match.append((p.name, sf))

    if fix and fixable:
        for _slug, _old, target in fixable:
            page = SOURCES / _slug
            _replace_source_file(page, target)

    if fixable:
        label = "FIXED" if fix else "AUTO-FIXABLE"
        print(f"\n[{label}: {len(fixable)}]")
        preview = fixable[:10]
        for slug, old, new in preview:
            print(f"  {slug}")
            print(f"    - {old}")
            print(f"    + {new}")
        if len(fixable) > len(preview):
            print(f"  ... +{len(fixable) - len(preview)} more")

    if ambiguous:
        print(f"\n[AMBIGUOUS: {len(ambiguous)}] (multiple raw candidates - human review)")
        for slug, sf, cands in ambiguous:
            print(f"  {slug}")
            print(f"    sf: {sf}")
            for c in cands:
                print(f"    candidate: {c}")

    if suggestions:
        print(
            f"\n[SUGGESTION: {len(suggestions)}] "
            f"(weak fuzzy match {_FUZZY_LOW:.1f} ≤ Jaccard < {_FUZZY_HIGH:.1f} - human review)"
        )
        for slug, sf, best, score in suggestions:
            print(f"  {slug} [score={score:.2f}]")
            print(f"    sf : {sf}")
            print(f"    raw: {best}")

    if no_match:
        print(f"\n[NO MATCH: {len(no_match)}] (no raw candidate - human review)")
        preview = no_match[:30]
        for slug, sf in preview:
            print(f"  {slug}: {sf}")
        if len(no_match) > len(preview):
            print(f"  ... +{len(no_match) - len(preview)} more")

    if not fixable and not ambiguous and not suggestions and not no_match:
        print("OK - all source_file references resolve to existing raw files")
        return 0

    if fix:
        remaining = len(ambiguous) + len(suggestions) + len(no_match)
        print()
        if remaining == 0:
            print(f"OK - {len(fixable)} reference(s) repaired, all source_file references valid")
            return 0
        print(
            f"FIXED {len(fixable)} · {remaining} remaining "
            f"({len(ambiguous)} ambiguous · {len(suggestions)} suggestion · {len(no_match)} no-match — manual review)"
        )
        return 1

    total = len(fixable) + len(ambiguous) + len(suggestions) + len(no_match)
    print(
        f"\nFAIL - {total} broken source_file reference(s) "
        f"({len(fixable)} auto-fixable · {len(ambiguous)} ambiguous · "
        f"{len(suggestions)} suggestion · {len(no_match)} no-match)"
    )
    print("Run `python tools/lint.py graph raw-files --fix` to repair the auto-fixable subset.")
    return 1


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true")
    args = ap.parse_args()
    sys.exit(run(fix=args.fix))
