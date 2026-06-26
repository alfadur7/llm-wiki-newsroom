"""Detect cited speakers without entity pages (lint check, batch mode).

Scans `> "..." — name (title)` blockquote attributions. Speakers cited
at or above the threshold who lack an `entities/<name>.md` page are
surfaced as actionable findings.

WIKI_LANG=ko only: the name/title matchers key on the Korean byline
convention (Hangul names + Korean role nouns), so the engine's English-native
default skips this check (see `run`). On an English corpus, blockquote speaker
attribution is covered by the scholarly-citation `cit.A2` check, and the
person-stub threshold by `python tools/count_mentions.py <name>`
(`.claude/policies/naming.md`).
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import WIKI, korean_mode, read_text_cached, strip_code  # noqa: E402

QUOTE_ATTR_RE = re.compile(
    r"^>\s.*?[\"\u201c\u201d\u2018\u2019].+?[\"\u201c\u201d\u2018\u2019]"
    r"\s*[\u2014\u2013\-]+\s*"
    r"(?P<attrib>[^\n]+?)\s*$",
    re.MULTILINE,
)

NAME_PARSE_RE = re.compile(
    r"^(?P<name>"
    # Two-word Korean name or a Hangul transliteration of a Western name
    # (includes "다리오 아모데이"·"사티아 나델라"·"양희동 이화여대" — the latter is
    # corrected by _clean_name via INSTITUTION_SUFFIXES)
    r"[가-힣]{2,5}\s+[가-힣]{2,5}"
    # Korean name with a one-syllable surname + 2-syllable given name (split form like "박 은솔")
    r"|[가-힣]{2,5}\s+[김이박최정황조강윤장한오서신권송안전홍고문양손배백허유남심노]"
    # English multi-word name (for Western names)
    r"|[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,2}"
    # Korean name alone
    r"|[가-힣]{2,5}"
    # Single English name
    r"|[A-Z][a-zA-Z]+"
    r")"
    r"(?P<rest>.*)$"
)

LATIN_ALIAS_RE = re.compile(
    r"\(([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,2})\)"
)

TITLE_KEYWORDS = (
    "대표", "행장", "은행장", "회장", "사장", "부사장", "전무", "상무", "이사",
    "위원장", "위원", "장관", "차관", "총리", "부총리", "대통령", "지사장",
    "본부장", "센터장", "팀장", "교수", "연구원", "박사", "부행장",
    "CEO", "CTO", "CIO", "CFO", "COO", "CISO", "CDO",
    "Director", "President", "Chairman", "Founder", "VP", "Vice President",
)

BLOCKLIST = {
    "CIO", "CIO Korea", "CTO", "ZDNet", "TechCrunch", "WSJ", "FT",
    "금융위원", "행안부", "과기정통부", "금융감독원",
}

COMPANY_PREFIXES = (
    "삼성", "KT", "LG", "SK", "NH", "NHN", "BNK", "KB", "신한", "우리",
    "하나", "네이버", "카카오", "토스", "쿠팡", "포스코", "현대", "한화",
    "대구", "대구은행", "DGB",
    "업스테이지", "이노그리드", "리벨리온", "쿠콘", "웹케시", "메가존",
    "베스핀", "티맥스", "코어위브", "엘리스", "마음AI", "래블업", "Lablup",
    "BC카드", "Bespin", "MuseSpark",
    "Microsoft", "MS", "Anthropic", "Nvidia", "AWS", "Google", "OpenAI",
    "엔비디아", "오픈AI", "마이크로소프트", "앤트로픽", "딥시크",
    "오라클", "Oracle", "스노우플레이크", "Snowflake",
    "코헤시티", "Cohesity", "베리타스", "Veritas",
    "사주핑",
)

# If the second word ends with one of these suffixes, treat it as an affiliation
# (university, research institute, etc.) → only the first word is the name.
# e.g. "양희동 이화여대" → "양희동", "김상배 서울대" → "김상배", "최병호 고려대" → "최병호"
INSTITUTION_SUFFIXES = (
    "대학교", "대학", "대",
    "연구원", "연구소",
    "센터",
    "재단", "협회",
    "병원",
)

GOVT_PREFIXES = (
    "과기정통부", "과학기술정보통신부",
    "금융감독원", "금융보안원", "금융위원회", "금융위원장",
    "행안부", "행정안전부",
    "개인정보보호위원회", "개인정보",
    "디지털플랫폼정부", "디지털플랫폼",
    "국가정보원",
)

KOREAN_TO_ENGLISH = {
    "다리오 아모데이": "DarioAmodei",
    "사티아 나델라": "SatyaNadella",
    "젠슨 황": "JensenHuang",
    "마크 베니오프": "MarkBenioff",
    "마크 저커버그": "MarkZuckerberg",
    "찰스 라만나": "CharlesLamanna",
    "산제이 푸넨": "SanjayPoonen",
    "제이미 다이먼": "JamieDimon",
    "크리스티안 클레이너만": "ChristianKleinerman",
    "래리 엘리슨": "LarryEllison",
    "매트 가먼": "MattGarman",
    "스콧 덴스모어": "ScottDensmore",
    "스콧 우": "ScottWu",
    "안드레이 카르파티": "AndrejKarpathy",
    "다니엘라 아모데이": "DanielaAmodei",
    "젠슨황": "JensenHuang",
}

# Stub-worthiness threshold — applies only to core figures with "many citations
# AND appearance across multiple sources". Memory feedback
# `feedback_no_single_source_stub` policy: a one-off mention in 1~2 sources is
# not a stub candidate, and title authority (CEO/legislator/professor) is not the
# pull — frequency of appearance within the wiki corpus is the real measure. Both
# conditions must hold for an actionable stub:
#   * total citation count ≥ DEFAULT_MIN_QUOTES (many citations)
#   * number of source files appeared in ≥ DEFAULT_MIN_SOURCES (multiple sources)
# Even if the same speaker is cited multiple times within one file, it counts as
# 1 source — "one article directly quoting one person multiple times = a single
# strong citation".
DEFAULT_MIN_QUOTES = 3
DEFAULT_MIN_SOURCES = 3


def _clean_name(name: str) -> str:
    parts = name.split()
    if len(parts) >= 2:
        second = parts[1]
        if any(second.startswith(p) for p in COMPANY_PREFIXES):
            return parts[0]
        if any(second.startswith(p) for p in TITLE_KEYWORDS):
            return parts[0]
        if any(second.startswith(p) for p in GOVT_PREFIXES):
            return parts[0]
        # If it ends with a university/research-institute suffix, treat as an affiliation
        if any(second.endswith(s) for s in INSTITUTION_SUFFIXES):
            return parts[0]
    return name


def _candidate_stems(name: str, latin_alias: str | None = None) -> set[str]:
    out: set[str] = set()
    raw = name.strip()
    out.add(raw)
    out.add(raw.replace(" ", ""))
    if latin_alias:
        latin = latin_alias.strip()
        out.add(latin)
        out.add(latin.replace(" ", ""))
    if raw in KOREAN_TO_ENGLISH:
        out.add(KOREAN_TO_ENGLISH[raw])
    return out


def run(
    *,
    json_out: bool = False,
    min_quotes: int = DEFAULT_MIN_QUOTES,
    min_sources: int = DEFAULT_MIN_SOURCES,
) -> int:
    if not korean_mode():
        # Korean byline detector — fires only under WIKI_LANG=ko (see module
        # docstring). English-native default: no-op, English attribution is
        # covered by cit.A2 + count_mentions.py.
        if json_out:
            print(json.dumps(
                {"skipped": "WIKI_LANG=ko only", "uncovered_speakers": []},
                ensure_ascii=False,
            ))
        else:
            print("Cited speakers: skipped (WIKI_LANG=ko only — English uses cit.A2 + count_mentions.py)")
        return 0

    entity_stems: set[str] = {
        p.stem
        for p in (WIKI / "entities").glob("*.md")
        if not p.name.startswith("_")
    }

    speaker_quotes: dict[str, list[dict]] = defaultdict(list)
    for sub in ("sources", "entities", "concepts"):
        d = WIKI / sub
        if not d.exists():
            continue
        for p in d.glob("*.md"):
            if p.name.startswith("_"):
                continue
            text = strip_code(read_text_cached(p))
            for m in QUOTE_ATTR_RE.finditer(text):
                attrib = m.group("attrib").strip()
                nm = NAME_PARSE_RE.match(attrib)
                if not nm:
                    continue
                name = _clean_name(nm.group("name").strip())
                if not any(k in attrib for k in TITLE_KEYWORDS):
                    continue
                if len(name) < 2:
                    continue
                if name in BLOCKLIST:
                    continue
                alias_m = LATIN_ALIAS_RE.search(attrib)
                latin_alias = alias_m.group(1) if alias_m else None
                stems = _candidate_stems(name, latin_alias)
                if stems & entity_stems:
                    continue
                speaker_quotes[name].append(
                    {
                        "page": f"{p.relative_to(WIKI).as_posix()}",
                        "attrib": attrib,
                        "latin_alias": latin_alias,
                    }
                )

    uncovered = []
    for name, quotes in sorted(
        speaker_quotes.items(), key=lambda x: -len({q["page"] for q in x[1]})
    ):
        # Dual threshold — surface only core figures with "many citations AND
        # appearance across multiple sources". See DEFAULT_MIN_* docstring above
        # for the rationale. The source count counts only distinct pages in the
        # sources/ folder — a citation in an entity/concept hub is a re-citation
        # of a source, not a distinct source (consistent with the
        # `.claude/policies/naming.md` person-stub threshold "≥3 distinct source
        # citations"). quote_count keeps the full total including hub re-citations
        # (the many-citations signal).
        unique_pages = {q["page"] for q in quotes}
        unique_sources = {q["page"] for q in quotes if q["page"].startswith("sources/")}
        if len(unique_sources) < min_sources or len(quotes) < min_quotes:
            continue
        uncovered.append(
            {
                "name": name,
                "quote_count": len(quotes),
                "unique_pages": len(unique_pages),
                "unique_sources": len(unique_sources),
                "samples": quotes[:3],
            }
        )

    if json_out:
        print(json.dumps(
            {
                "min_quotes": min_quotes,
                "min_sources": min_sources,
                "uncovered_speakers": uncovered,
                "total_speakers_seen": len(speaker_quotes),
            },
            ensure_ascii=False,
            indent=2,
        ))
    else:
        print(
            f"Cited speakers seen: {len(speaker_quotes)}; "
            f"uncovered (≥{min_quotes} quotes AND ≥{min_sources} sources): "
            f"{len(uncovered)}"
        )
        for c in uncovered[:30]:
            print(f"  {c['name']}  sources={c['unique_sources']} pages={c['unique_pages']} quotes={c['quote_count']}")
            for q in c["samples"][:2]:
                print(f"      {q['page']}: {q['attrib'][:90]}")
        if len(uncovered) > 30:
            print(f"  ... and {len(uncovered)-30} more")

    return 0 if not uncovered else 1
