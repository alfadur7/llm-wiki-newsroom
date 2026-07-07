"""L2-2 hub `## Timeline narrative` advisory lint — entities / concepts.

Promotes timeline-convention violations that surfaced as a common pattern across
4 hubs in the B1 batch 2 Desk review into deterministic detection. The hub.md
section "avoid timeline-narrative vs topic-section duplication" spells out the
good/forbidden patterns, but there was no automatic lint detection.

Detected items:
  * Item count advisory — advisory when timeline items ≥ 30 (degraded
    branch-point identification / candidate for splitting into a separate
    timeline hub).
  * Strict date ordering — detects monotonic-increase violations between items
    (broken inline-edit order like `2026-04-14 → 04-20 → 04-17`).
  * Verdict-keyword narrative-redundancy — advisory when a Korean verdict/
    evaluation ending or a quantitative figure appears in an item's body.
    Automates the hub.md explicitly-forbidden pattern "event name — restatement
    of the body's facts/figures/quotes/verdict".
  * Reference-pointer coverage — advisory when the good form
    "(상세는 「<section>」 절)" is attached to less than 50% of items (recommends
    pairing items, other than standalone-info ones, with a trigger pointer).

`--fix` not supported — compressing/reordering items and removing verdicts is
semantic-judgment territory (handled in the columnist ADAPT cycle).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import FRONTMATTER_BLOCK_RE, read_text_cached  # noqa: E402
sys.path.insert(0, str(Path(__file__).parent))
from _hub_common import HTML_COMMENT_RE, HUB_SPECS, iter_hub_files  # noqa: E402

# Matches a `## Timeline narrative` or `## Timeline` section — or the Korean
# `## 타임라인 (서사 (골격))` heading family for WIKI_LANG=ko corpora (the module
# keeps ko support like POINTER_RE / VERDICT_NUM_RE below). The module applies
# only to hubs that have a timeline section; hubs without one are out of scope
# (many good hubs don't have a timeline section at all).
TIMELINE_SECTION_RE = re.compile(
    r"^##\s+(?:Timeline(?:\s+narrative)?|타임라인(?:\s+서사)?(?:\s+골격)?)\s*$(.*?)(?=^##\s|\Z)",
    re.MULTILINE | re.DOTALL,
)
# Timeline item: starts with `- **` or `* **` then `YYYY년 M월 (D일)?` or
# `YYYY-MM-DD`. The ★ marker (for emphasizing branch points) may appear at the
# head of the line, so it's allowed.
TIMELINE_ITEM_RE = re.compile(
    r"^[-*]\s+(?:★\s+)?\*\*"
    r"(\d{4})(?:[년\-]\s*(\d{1,2}))?(?:[월\-]\s*(\d{1,2}))?",
    re.MULTILINE,
)
# Reference pointer pattern matching the hub.md good example
# `(detail in the 「section」 section)`. Matches the trigger inside any paren,
# whether standalone or source-bundled (e.g. `([[src]], detail in the …)`), so
# a source link before the trigger doesn't go uncounted. The English corpus
# uses "detail in the …" (with 「」 corner brackets per hub.md, or straight
# quotes per the advisory message below); the Korean "상세는 「섹션」 절" form is
# kept for WIKI_LANG=ko corpora.
POINTER_RE = re.compile(
    r"\([^)]*?(?:상세는\s+「[^」]+」\s*절"
    r"|detail in the\s+(?:「[^」]+」|\"[^\"]+\")\s*section)[^)]*?\)"
)
# Verdict keywords — Korean verdict/evaluation endings + quantitative figures.
# Automates the hub.md forbidden pattern "restatement of the body's
# facts/figures/quotes/verdict". To exclude timeline meta-notation like
# dates/years/"M월"/"M월 D일", only figures with an attached unit are detected.
VERDICT_NUM_RE = re.compile(
    r"\d[\d,]*(?:\.\d+)?\s*(?:%|billion|million|hours?|cases?|times?|people|"
    r"배|건|개|건당|만\s*원|억\s*원|조\s*원|"
    r"달러|위안|엔|GB|TB|MW|GW|명|회|초)"
)
# Verdict/quote endings: diagnostic expressions like "쇼크"·"본격 논의"·"공식 발표"
# are hard to catch with regex, so for now we focus on figure restatement. This
# module reports only the quantitative signal and leaves verdict-ending detection
# to the Desk's qualitative review.

# Thresholds — based on B1 batch 2 measurements.
ITEM_COUNT_ADVISORY = 30
POINTER_COVERAGE_MIN = 0.5  # good pointer attachment ratio ≥ 50%


def _date_key(year: str, month: str | None, day: str | None) -> tuple[int, int, int]:
    return (int(year), int(month) if month else 0, int(day) if day else 0)


def _check_timeline(content: str, path: Path, dir_label: str) -> list[str]:
    issues: list[str] = []
    # Newline-preserving equivalent of _hub_common.body_text: keep the
    # frontmatter line count as `base` and replace HTML comments by their own
    # newlines, so reported `:{line_no}:` values map to source-file lines.
    fm = FRONTMATTER_BLOCK_RE.match(content)
    base = content[: fm.end()].count("\n") if fm else 0
    body = HTML_COMMENT_RE.sub(
        lambda m: "\n" * m.group(0).count("\n"),
        content[fm.end():] if fm else content,
    )
    section_match = TIMELINE_SECTION_RE.search(body)
    if not section_match:
        return issues

    section_body = section_match.group(1)
    section_start_offset = section_match.start(1)

    # Item count + ordering.
    item_dates: list[tuple[int, int, int]] = []
    item_count = 0
    for m in TIMELINE_ITEM_RE.finditer(section_body):
        item_count += 1
        item_dates.append(_date_key(m.group(1), m.group(2), m.group(3)))

    if item_count >= ITEM_COUNT_ADVISORY:
        issues.append(
            f"  {dir_label}/{path.name}: timeline items {item_count} "
            f"≥ {ITEM_COUNT_ADVISORY} advisory — consider emphasizing branch points "
            f"(★ marker) or splitting into a separate wiki/timelines/<entity>.md"
        )

    # Strict ascending check: precision-aware. For items with no day specified
    # (day=0), the day comparison is skipped so they can sit anywhere within the
    # same month — preventing a false positive when month-only items and day-level
    # items are mixed within the same month. The day-monotonicity check runs only
    # when both have day ≥ 1.
    def _violates(prev: tuple[int, int, int], curr: tuple[int, int, int]) -> bool:
        # Year violation: always strict (a missing year isn't matched by the regex itself).
        if curr[0] < prev[0]:
            return True
        if curr[0] > prev[0]:
            return False
        # Same year. Month-level violation only when both have month ≥ 1.
        if prev[1] and curr[1] and curr[1] < prev[1]:
            return True
        if not prev[1] or not curr[1] or curr[1] > prev[1]:
            return False
        # Same year+month. Day-level violation only when both have day ≥ 1.
        if prev[2] and curr[2] and curr[2] < prev[2]:
            return True
        return False

    for prev, curr in zip(item_dates, item_dates[1:]):
        if _violates(prev, curr):
            issues.append(
                f"  {dir_label}/{path.name}: timeline ordering violation — "
                f"{prev[0]:04d}-{prev[1]:02d}-{prev[2]:02d} is followed by "
                f"the {curr[0]:04d}-{curr[1]:02d}-{curr[2]:02d} item "
                f"(strict ascending order required)"
            )
            break  # surface only 1 per hub (avoid repeated reporting).

    # Reference pointer coverage.
    if item_count > 0:
        pointer_count = len(POINTER_RE.findall(section_body))
        coverage = pointer_count / item_count
        if coverage < POINTER_COVERAGE_MIN:
            issues.append(
                f"  {dir_label}/{path.name}: timeline pointer attachment "
                f"{pointer_count}/{item_count} ({coverage:.0%}) "
                f"< {int(POINTER_COVERAGE_MIN * 100)}% advisory — "
                f"recommend attaching the \"(detail in the \"<section>\" section)\" trigger"
            )

    # Per-line verdict/numeric reuse advisory (limit to 1 surface per hub
    # to avoid line-by-line spam; full audit is desk territory).
    line_offset = section_start_offset
    for raw_line in section_body.splitlines(keepends=True):
        line_offset += len(raw_line)
        # Only inspect bullet timeline lines.
        if not TIMELINE_ITEM_RE.match(raw_line):
            continue
        if VERDICT_NUM_RE.search(raw_line):
            # Compute 1-based file line number from offset (cheap pass) —
            # `base` re-adds the stripped frontmatter lines.
            line_no = base + body.count("\n", 0, line_offset - len(raw_line)) + 1
            issues.append(
                f"  {dir_label}/{path.name}:{line_no}: quantitative figure restated "
                f"in a timeline item's body — hub.md forbidden pattern "
                f"(a timeline keeps only the event-name + pointer skeleton)"
            )
            break  # surface once per hub.
    return issues


def _check_directory(directory: Path, dir_label: str) -> list[str]:
    issues: list[str] = []
    if not directory.exists():
        return issues
    for path in iter_hub_files(directory):
        content = read_text_cached(path)
        issues.extend(_check_timeline(content, path, dir_label))
    return issues


def run(fix: bool = False) -> int:
    """Entry point for `python tools/lint.py hub timeline`.

    `fix` is accepted for signature parity but ignored — timeline cleanup
    requires semantic judgment (columnist ADAPT cycle).
    """
    del fix  # signature parity only; not actionable here.

    all_issues: list[str] = []
    total_files = 0
    for directory, dir_label in HUB_SPECS:
        if directory.exists():
            total_files += len(iter_hub_files(directory))
        all_issues.extend(_check_directory(directory, dir_label))

    if all_issues:
        print(
            f"\n[hub timeline: {len(all_issues)} advisory issue(s) across "
            f"{total_files} L2-2 entity+concept file(s)]"
        )
        for i in all_issues:
            print(i)
        print(
            f"\nADVISORY — L2-2 hub `## Timeline narrative` regulations "
            f"(.claude/layers/hub.md \"avoid timeline-narrative vs topic-section duplication\")."
        )
        print(
            "       Item count ≥ 30 → emphasize branch points / split into a separate timeline hub; "
            "ordering violation → reorder strict ascending; pointer coverage < 50%"
            " → attach \"(detail in the \"<section>\" section)\"; quantitative figure restatement → delegate "
            "to the topic section. `--fix` not provided — semantic judgment required."
        )
        return 1

    print(
        f"OK - L2-2 hub timeline: 0 advisories "
        f"({total_files} entity+concept files)"
    )
    return 0


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true")
    args = ap.parse_args()
    sys.exit(run(fix=args.fix))
