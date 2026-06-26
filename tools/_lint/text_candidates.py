"""Text-based page candidates — frequent noun phrases without matching pages.

Paired with link_candidates.py in the `suggestions` pipeline. Both surface
potential wiki pages that don't yet exist; this module scans TEXT
(plain-text noun phrases in page bodies), the other scans LINKS
(broken wikilinks converging across hubs).

Heuristics:
  - Latin TitleCase phrases: 1-3 capitalised tokens
  - Korean noun-like tokens: 4+ Hangul characters in a single run

Strict filters:
  - body text only (frontmatter, code blocks, inline code stripped)
  - existing entity/concept/source stems excluded (after normalisation)
  - minimum mentions and minimum page count thresholds
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import (  # noqa: E402
    read_text_cached,
    WIKI,
    WIKILINK_RE,
    strip_frontmatter,
    strip_code,
)

LATIN_RE = re.compile(r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,2})\b")
KOREAN_RE = re.compile(r"([가-힣]{4,})")

DEFAULT_MIN_MENTIONS = 10
DEFAULT_MIN_PAGES = 5
DEFAULT_TOP = 50

BLOCKLIST = {
    "AI", "ai", "AX", "ax", "IT", "it",
    "클라우드", "데이터센터", "GPU", "보안", "금융", "통신",
    "프로젝트", "소프트웨어", "네트워크", "비즈니스", "거버넌스",
    "아키텍처", "파트너십", "프레임워크", "모니터링", "라이선스",
    "엔터프라이즈", "스타트업", "에이전트", "기업", "시장",
    "솔루션", "플랫폼", "인프라", "정책", "전략", "혁신", "성장",
    "기술", "데이터", "서비스", "고객", "산업", "시스템",
    "규제", "분야", "지원", "관리", "제공", "도입", "구축",
    "CEO", "CTO", "CIO", "CFO", "VP",
    "LG", "SK", "SW", "DB",
    "프로세스", "애플리케이션", "워크로드", "컨텍스트", "엔지니어링",
    "금융그룹", "하드웨어", "스토리지", "공공기관", "라이브러리",
    "서비스를", "데이터를", "기반으로", "에이전트가",
    "제공한다", "발표했다", "제공하는", "지원한다",
    "전망이다", "확대된다", "추진한다", "강조했다",
    "위한", "관련", "통해",
    # C-group noise: generic words/categories that aren't page candidates
    "패러다임", "업데이트", "프로그램", "가능하게", "대한민국",
    "영업이익", "기업가치", "전문기업", "중소기업", "엔지니어",
    "어시스턴트", "프로토콜", "인제스트", "컨소시엄",
    "싱가포르", "인도네시아",
    "트러스트", "의사결정",
}

KOREAN_ALIAS = {
    "마이크로소프트": "Microsoft",
    "엔비디아": "Nvidia",
    "오픈AI": "OpenAI",
    "오픈에이아이": "OpenAI",
    "앤트로픽": "Anthropic",
    "앤스로픽": "Anthropic",
    "구글": "Google",
    "아마존": "Amazon",
    "테슬라": "Tesla",
    "메타": "Meta",
    "애플": "Apple",
    "오라클": "Oracle",
    "딥시크": "DeepSeek",
    "코헤시티": "Cohesity",
    "베리타스": "Veritas",
    "스노우플레이크": "Snowflake",
    "데이터브릭스": "Databricks",
    "팔란티어": "Palantir",
    "에퀴닉스": "Equinix",
    "코어위브": "CoreWeave",
    "람다랩스": "LambdaLabs",
    "엘리슨": None,
    "프라이빗": "OnPremiseAI",
    "온프레미스": "OnPremiseAI",
    "하이브리드": "HybridCloud",
    "멀티클라우드": "MultiCloud",
    "오픈소스": "OpenSource",
    "쿠버네티스": "Kubernetes",
    "에이전틱": "AgenticAI",
    "프롬프트": "PromptEngineering",
    "에이전트": None,
    "컨테이너": "Container",
    "메인프레임": "Mainframe",
    "코파일럿": "Copilot",
    "마이데이터": "MyData",
    "스테이블코인": "Stablecoin",
    "DR": "DisasterRecovery",
    "MS": "Microsoft",
    "네이티브": None,
    "국민은행": None,
    "농협은행": None,
    # C-group: already covered by existing pages (plain-text mining noise)
    "코어뱅킹": "CoreBankingModernization",
    "블록체인": "Blockchain",
    "인터넷은행": "InternetBank",
    "재해복구": "DisasterRecovery",
    "마이그레이션": "CloudMigration",
    "시중은행": None,
    "금융지주": None,
    "오케스트레이션": "MultiAgentOrchestration",
    "하이퍼클로바": "하이퍼클로바",
    "데이터베이스": None,
    "컨택센터": "AICC",
    "신한금융": None,
    "유지보수": None,
    "파운데이션": "FoundationModel",
    "개인정보": "PersonalDataProtection",
    "내부통제": "Compliance",
    "ROI": "AIProjectROI",
    "AIDC": "AIDataCenter",
    "DC": None,
    "SI": "SystemIntegration",
    "SKT": None,
    "Amazon": None,
    "MOU": None,
    "KB": None,
    "PaaS": "KPaaS",
    "ICT": "AICT",
    "SCP": None,
    "ERP": "ERP",
    "컴플라이언스": "Compliance",
    "사이버보안": "CyberSecurity",
    "오픈시프트": "OpenShift",
}

KOREAN_TAIL_NOISE = (
    "은", "는", "이", "가", "을", "를", "의", "에", "도",
    "와", "과", "로", "으로", "에서", "에게", "한테",
    "다", "한다", "했다", "된다", "되었다", "한", "된", "할",
    "이다", "이며", "였다",
)


def _strip_wikilinks(text: str) -> str:
    return WIKILINK_RE.sub("", text)


def _normalise(s: str) -> str:
    return s.lower().replace(" ", "").replace("-", "").replace("_", "")


def _is_conjugated_korean(token: str) -> bool:
    return any(token.endswith(s) for s in KOREAN_TAIL_NOISE)


def _index_existing_pages() -> tuple[set[str], dict[str, str]]:
    stems: set[str] = set()
    norm_map: dict[str, str] = {}
    for sub in ("entities", "concepts", "syntheses", "trails", "timelines", "sources"):
        d = WIKI / sub
        if not d.exists():
            continue
        for p in d.glob("*.md"):
            if p.name.startswith("_"):
                continue
            stems.add(p.stem)
            norm_map[_normalise(p.stem)] = p.stem
    for p in WIKI.glob("*.md"):
        if not p.name.startswith("_"):
            stems.add(p.stem)
            norm_map[_normalise(p.stem)] = p.stem
    return stems, norm_map


def _candidates(*,
                min_mentions: int = DEFAULT_MIN_MENTIONS,
                min_pages: int = DEFAULT_MIN_PAGES,
                top: int = DEFAULT_TOP) -> tuple[dict, int]:
    """Mine plain-text mention candidates into a structured payload.

    Returns (payload, indexed_page_count) where payload is the JSON-serialisable
    dict {"min_mentions", "min_pages", "candidates"}. Split out of run() so the
    suggestions.py JSON path can fold this into a single combined document
    instead of emitting a second concatenated JSON object on stdout.
    """
    stems, norm_map = _index_existing_pages()

    mentions: Counter = Counter()
    page_set: dict[str, set[str]] = defaultdict(set)

    for sub in ("sources", "entities", "concepts", "syntheses", "trails", "timelines"):
        d = WIKI / sub
        if not d.exists():
            continue
        for p in d.glob("*.md"):
            if p.name.startswith("_"):
                continue
            raw = read_text_cached(p)
            text = _strip_wikilinks(strip_code(strip_frontmatter(raw)))
            page_id = f"{sub}/{p.stem}"

            for m in LATIN_RE.findall(text):
                token = m.strip()
                if token in BLOCKLIST:
                    continue
                aliased = KOREAN_ALIAS.get(token)
                if aliased is None and token in KOREAN_ALIAS:
                    continue
                check_token = aliased or token
                if _normalise(check_token) in norm_map:
                    continue
                mentions[token] += 1
                page_set[token].add(page_id)
            for m in KOREAN_RE.findall(text):
                token = m.strip()
                if token in BLOCKLIST:
                    continue
                if _is_conjugated_korean(token):
                    continue
                aliased = KOREAN_ALIAS.get(token)
                if aliased is None and token in KOREAN_ALIAS:
                    continue
                check_token = aliased or token
                if _normalise(check_token) in norm_map:
                    continue
                mentions[token] += 1
                page_set[token].add(page_id)

    candidates = []
    for token, n in mentions.most_common():
        pages = page_set[token]
        if n < min_mentions or len(pages) < min_pages:
            continue
        candidates.append({
            "token": token,
            "mentions": n,
            "page_count": len(pages),
            "sample_pages": sorted(pages)[:3],
        })
        if len(candidates) >= top:
            break

    payload = {
        "min_mentions": min_mentions,
        "min_pages": min_pages,
        "candidates": candidates,
    }
    return payload, len(stems)


def run(*, json_out: bool = False,
        min_mentions: int = DEFAULT_MIN_MENTIONS,
        min_pages: int = DEFAULT_MIN_PAGES,
        top: int = DEFAULT_TOP) -> int:
    payload, indexed = _candidates(min_mentions=min_mentions, min_pages=min_pages, top=top)
    candidates = payload["candidates"]

    if json_out:
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        print(
            f"Plain-text mention candidates "
            f"(>= {min_mentions} mentions, >= {min_pages} pages, top {top}):"
        )
        print(f"Total existing pages indexed (excluded): {indexed}")
        for c in candidates:
            sample = ", ".join(c["sample_pages"])
            print(f"  [{c['mentions']:4d}/{c['page_count']:3d}p]  {c['token']}")
            print(f"      e.g. {sample}")
    return 0
