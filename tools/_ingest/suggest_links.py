"""Detect existing wiki pages that appear in body text without a wikilink.

This is the cascading-update companion to /wiki-ingest. When a new
source page is written, its body often mentions companies, concepts
or people that already have a wiki page — but as plain text rather
than as `[[wikilink]]`. Those plain-text mentions never feed the
backlink graph, so the page silently misses connections.

This tool walks one (or all) source pages, looks at the body text
(frontmatter / code / inline-code / existing wikilinks stripped),
and lists existing entity / concept stems that appear unlinked.

Usage:
  python tools/_ingest/suggest_links.py --file wiki/sources/xyz.md
  python tools/_ingest/suggest_links.py                    # scan all sources
  python tools/_ingest/suggest_links.py --scope hubs       # entities + concepts
  python tools/_ingest/suggest_links.py --scope all        # everything
  python tools/_ingest/suggest_links.py --json             # machine-readable

Exit codes:
  0 - no unlinked mentions found above threshold
  1 - candidates surfaced (count printed)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))  # _ingest/ → tools/ root (shared modules)
from _lib import (  # noqa: E402
    WIKI,
    WIKILINK_STEM_RE,
    strip_frontmatter,
    strip_code,
    strip_blockquotes,
    parse_frontmatter,
)

DEFAULT_MIN_COUNT = 1
DEFAULT_TOP = 30

MIN_STEM_LEN_LATIN = 3
MIN_STEM_LEN_KOREAN = 2

KOREAN_CHAR_RE = re.compile(r"[가-힣]+")

# Short generic Korean words to skip when building title aliases.
_ALIAS_NOISE = {
    "전략", "보안", "현대화", "인프라", "서비스", "에이전트",
    "플랫폼", "시스템", "기반", "모델", "기술", "경제",
    "시장", "산업", "정책", "도입", "구축", "관리", "전환",
    "리더십", "비용", "생산성", "프로젝트", "데이터센터",
    "반도체", "프로토콜", "아키텍처", "거버넌스", "프레임워크",
    "네이티브", "어시스턴트", "엔지니어링",
}

SCOPE_DIRS: dict[str, list[str]] = {
    "sources":   ["sources"],
    "hubs":      ["entities", "concepts"],
    "syntheses": ["syntheses", "trails", "timelines"],
    "all":       ["sources", "entities", "concepts", "syntheses", "trails", "timelines"],
}


def tiered_min_count(stem: str, base: int) -> int:
    """Short Latin stubs (e.g. API, VM, GPT) are noisy; require more hits."""
    if re.match(r"^[A-Za-z0-9]+$", stem):
        if len(stem) <= 3:
            return max(base, 3)
        if len(stem) <= 5:
            return max(base, 2)
    return base


def strip_wikilinks_keep_text(text: str) -> tuple[str, set[str]]:
    """Replace `[[Stem]]`, `[[Stem|Display]]` and anchored `[[Stem#Section]]`
    links with the Display text (so we don't false-flag the visible Korean
    string as a missing link), and return the set of bare stems that were
    already wikilinked (anchor/alias stripped)."""
    linked: set[str] = set()

    def repl(m: re.Match) -> str:
        body = m.group(0)[2:-2]
        # Bare stem = text before any #anchor or |alias. Register it as linked;
        # keep only the |alias display text (drop the stem/anchor text entirely).
        target = body.split("|", 1)[0].split("#", 1)[0]
        linked.add(target.strip())
        return body.split("|", 1)[1] if "|" in body else ""

    new_text = WIKILINK_STEM_RE.sub(repl, text)
    return new_text, linked


def _title_korean_aliases(title: str, stem: str) -> list[str]:
    """Extract Korean compound aliases from a page title.

    For ``title="코어 뱅킹 현대화"`` → ``["코어뱅킹", "코어뱅킹현대화"]``
    For ``title="앤스로픽"`` → ``["앤스로픽"]``
    """
    # Strip parenthetical and subtitle separators (— · :)
    clean = re.sub(r"\(.*?\)", "", title)
    clean = re.split(r"\s*[—\-:·]\s*", clean)[0].strip()
    tokens = KOREAN_CHAR_RE.findall(clean)
    if not tokens or len(tokens) > 5:
        return []

    aliases: set[str] = set()

    # Single Korean name (entity like 앤스로픽)
    if len(tokens) == 1:
        tok = tokens[0]
        if len(tok) >= 3 and tok != stem and tok not in _ALIAS_NOISE:
            aliases.add(tok)
        return list(aliases)

    # Contiguous n-gram compounds (n=2..len)
    for length in range(2, len(tokens) + 1):
        for start in range(len(tokens) - length + 1):
            sub_tokens = tokens[start : start + length]
            # Skip if all sub-tokens are generic noise
            if all(t in _ALIAS_NOISE for t in sub_tokens):
                continue
            compound = "".join(sub_tokens)
            if len(compound) >= 3 and compound != stem:
                aliases.add(compound)

    return list(aliases)


def _title_english_aliases(title: str, stem: str) -> list[str]:
    """Spaced display-form aliases for a multi-word Latin title.

    PascalCase stems (``OpenSourceAI``) are matched verbatim by Pass 1's
    ``\\bOpenSourceAI\\b``, which English prose — written spaced ("Open Source
    AI") — never satisfies. The spaced title is registered as an alias so the
    plain-text mention is detected. Single-word titles are already covered by
    the stem pass; Korean titles go through ``_title_korean_aliases``.

    For ``title="Open Source AI"`` → ``["Open Source AI"]``.
    """
    clean = re.sub(r"\(.*?\)", "", title)
    # Split only on a *spaced* ASCII hyphen ("Title - Subtitle"), not a bare
    # one, so hyphenated compounds ("Open-Weight Models") aren't truncated to
    # their first token and lose their spaced alias.
    clean = re.split(r"\s*[—:·]\s*|\s+-\s+", clean)[0].strip()
    if " " not in clean:                       # single token → stem pass covers it
        return []
    if not re.search(r"[A-Za-z]", clean) or KOREAN_CHAR_RE.search(clean):
        return []                              # not a pure-Latin phrase
    if len(clean) < 4 or clean.lower() == stem.lower():
        return []
    return [clean]


def index_hub_stems() -> tuple[set[str], dict[str, str]]:
    """Return (set of stems, dict alias→stem) for entity/concept pages.

    Aliases are spaced/compound display-name forms from frontmatter titles —
    English multi-word titles (`_title_english_aliases`) and, for a Korean
    corpus, Hangul compounds (`_title_korean_aliases`).
    """
    out: set[str] = set()
    alias_map: dict[str, str] = {}

    for sub in ("entities", "concepts"):
        d = WIKI / sub
        if not d.exists():
            continue
        for p in d.glob("*.md"):
            if p.name.startswith("_"):
                continue
            stem = p.stem
            if not stem:
                continue
            # Length filter to suppress single-letter / 1-char false positives.
            if re.match(r"^[A-Za-z0-9]+$", stem):
                if len(stem) < MIN_STEM_LEN_LATIN:
                    continue
            elif re.match(r"^[가-힣]+$", stem):
                if len(stem) < MIN_STEM_LEN_KOREAN:
                    continue
            out.add(stem)

            # Title-based Korean aliases
            text = p.read_text(encoding="utf-8", errors="replace")
            fm = parse_frontmatter(text)
            title = fm.get("title", "")
            if not isinstance(title, str):
                title = ""
            if title and title != stem:
                aliases = _title_english_aliases(title, stem) + _title_korean_aliases(title, stem)
                for alias in aliases:
                    if alias not in out:  # don't shadow real stems
                        alias_map[alias] = stem

    return out, alias_map


def find_unlinked(
    text: str,
    hub_stems: set[str],
    alias_map: dict[str, str] | None = None,
    self_stem: str | None = None,
    strip_quotes: bool = True,
) -> list[dict]:
    """For each hub stem (and title alias), count plain-text occurrences
    and capture a short context sample. Return sorted by count (desc)."""
    body = strip_code(strip_frontmatter(text))
    if strip_quotes:
        body = strip_blockquotes(body)
    body, already_linked = strip_wikilinks_keep_text(body)

    already_linked_norm = {x.split("/")[-1] for x in already_linked}
    if self_stem:
        already_linked_norm.add(self_stem)

    hits: dict[str, list[str]] = defaultdict(list)
    via_alias: dict[str, str] = {}  # stem → alias that matched

    # Pass 1: match by file stem (existing behaviour)
    for stem in hub_stems:
        if stem in already_linked_norm:
            continue
        if re.match(r"^[A-Za-z0-9]+$", stem):
            pattern = re.compile(r"\b" + re.escape(stem) + r"\b", re.IGNORECASE)
        else:
            pattern = re.compile(re.escape(stem))
        for m in pattern.finditer(body):
            start = max(0, m.start() - 20)
            end = min(len(body), m.end() + 20)
            ctx = body[start:end].replace("\n", " ").strip()
            hits[stem].append(ctx)

    # Pass 2: match by title-based aliases (English spaced forms + Korean compounds)
    if alias_map:
        for alias, target_stem in alias_map.items():
            if target_stem in already_linked_norm:
                continue
            if re.search(r"[A-Za-z]", alias):  # Latin phrase → word-boundary, case-insensitive
                pattern = re.compile(r"\b" + re.escape(alias) + r"\b", re.IGNORECASE)
            else:
                pattern = re.compile(re.escape(alias))
            for m in pattern.finditer(body):
                start = max(0, m.start() - 20)
                end = min(len(body), m.end() + 20)
                ctx = body[start:end].replace("\n", " ").strip()
                hits[target_stem].append(ctx)
                via_alias[target_stem] = alias

    out = []
    for stem, ctxs in sorted(hits.items(), key=lambda x: -len(x[1])):
        entry: dict = {"stem": stem, "count": len(ctxs), "samples": ctxs[:2]}
        if stem in via_alias:
            entry["alias"] = via_alias[stem]
        out.append(entry)
    return out


def scan_one(
    path: Path,
    hub_stems: set[str],
    alias_map: dict[str, str] | None = None,
    min_count: int = DEFAULT_MIN_COUNT,
    strip_quotes: bool = True,
) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    self_stem = path.stem if path.parent.name in ("entities", "concepts") else None
    candidates = [
        c
        for c in find_unlinked(text, hub_stems, alias_map=alias_map, self_stem=self_stem, strip_quotes=strip_quotes)
        if c["count"] >= tiered_min_count(c["stem"], min_count)
    ]
    try:
        rel = str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        rel = str(path)
    return {"file": rel, "unlinked": candidates}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", type=str, help="Single file (overrides --scope)")
    ap.add_argument(
        "--scope",
        choices=sorted(SCOPE_DIRS.keys()),
        default="sources",
        help="Which wiki subtree to scan (default: sources)",
    )
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--min-count", type=int, default=DEFAULT_MIN_COUNT)
    ap.add_argument("--top", type=int, default=DEFAULT_TOP, help="Cap results per file")
    ap.add_argument(
        "--include-quotes",
        action="store_true",
        help="Do not strip blockquote lines before matching",
    )
    args = ap.parse_args()

    hub_stems, alias_map = index_hub_stems()
    strip_quotes = not args.include_quotes

    targets: list[Path]
    if args.file:
        p = Path(args.file)
        if not p.exists():
            print(f"File not found: {args.file}", file=sys.stderr)
            return 2
        targets = [p]
    else:
        targets = []
        for sub in SCOPE_DIRS[args.scope]:
            d = WIKI / sub
            if not d.exists():
                continue
            targets.extend(sorted(d.glob("*.md")))
        targets = [t for t in targets if not t.name.startswith("_")]

    results = [scan_one(t, hub_stems, alias_map=alias_map, min_count=args.min_count, strip_quotes=strip_quotes) for t in targets]
    actionable = [r for r in results if r["unlinked"]]

    if args.json:
        json.dump(
            {
                "scope": args.file or args.scope,
                "min_count": args.min_count,
                "files_scanned": len(results),
                "files_with_unlinked": len(actionable),
                "results": actionable,
            },
            sys.stdout,
            ensure_ascii=False,
            indent=2,
        )
        print()
    else:
        scope_label = args.file or f"scope={args.scope}"
        print(
            f"Unlinked-mention candidates [{scope_label}] "
            f"(base min={args.min_count}, tiered by stem length) — "
            f"{len(actionable)} / {len(results)} files have findings"
        )
        for r in actionable[: 50 if not args.file else None]:
            print(f"\n{r['file']}")
            for c in r["unlinked"][: args.top]:
                sample = c["samples"][0] if c["samples"] else ""
                alias_tag = f"  (via: {c['alias']})" if c.get("alias") else ""
                print(f"  [{c['count']:2d}x]  {c['stem']}{alias_tag}")
                if sample:
                    print(f"        e.g. ...{sample}...")
    return 1 if actionable else 0


if __name__ == "__main__":
    sys.exit(main())
