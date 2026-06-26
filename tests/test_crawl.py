"""`tools/_news/crawl.py` unit tests — network-independent paths only.

The crawl core takes an injected fetcher, so in-memory HTML drives the whole
pipeline (BFS, classify, ranking, caps, pre-inbox-append) without any network.

These tests exercise the Korean-corpus behavior of crawl (2-char Hangul
vocabulary terms etc.), so they run under WIKI_LANG=ko via an autouse fixture."""
import sys
from pathlib import Path

import pytest

# conftest already puts tools/ on sys.path, but crawl lives under _news/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from _ingest.fetch_article import extract_links  # noqa: E402
from _news import crawl as C  # noqa: E402
from bs4 import BeautifulSoup  # noqa: E402


@pytest.fixture(autouse=True)
def _korean_mode(monkeypatch):
    # crawl's 2-char Hangul term exemption is gated on korean_mode(); the fixtures
    # below use Korean vocabulary, so pin the corpus language for every test here.
    monkeypatch.setenv("WIKI_LANG", "ko")


# ── extract_links ──────────────────────────────────────────────────────────
def test_extract_links_strips_chrome_and_resolves_relative():
    html = """
    <html><body>
      <nav><a href="/menu">메뉴</a></nav>
      <article>
        <a href="/2026/shinhan-ai">신한은행 기사</a>
        <a href="https://other.com/x">외부</a>
        <a href="#top">앵커</a>
        <a href="mailto:a@b.com">메일</a>
      </article>
      <footer><a href="/about">회사소개</a></footer>
    </body></html>
    """
    links = extract_links(BeautifulSoup(html, "html.parser"), "https://news.co.kr/p")
    urls = [u for u, _ in links]
    assert "https://news.co.kr/2026/shinhan-ai" in urls   # relative resolved
    assert "https://other.com/x" in urls
    assert "https://news.co.kr/menu" not in urls           # nav stripped
    assert "https://news.co.kr/about" not in urls          # footer stripped
    assert not any(u.startswith(("mailto", "https://news.co.kr/p#")) for u in urls)


def test_extract_links_dedups_by_resolved_url():
    html = '<a href="/x">a</a><a href="/x">b</a>'
    links = extract_links(BeautifulSoup(html, "html.parser"), "https://e.com/")
    assert len(links) == 1
    assert links[0][1] == "a"  # first anchor wins


# ── vocabulary + scoring ───────────────────────────────────────────────────
@pytest.fixture
def vocab():
    hub_fm = {
        "entities/신한은행.md": {"title": "신한은행", "tags": ["은행", "디지털뱅킹"]},
        "concepts/에이전틱 AI.md": {"title": "에이전틱 AI", "tags": ["ai", "llm"]},
    }
    return C.build_vocabulary(hub_fm)


def test_build_vocabulary_weights_and_min_len(vocab):
    assert vocab["신한은행"] == C.LABEL_WEIGHT
    assert vocab["은행"] == C.TAG_WEIGHT
    assert "ai" not in vocab          # <3 chars dropped
    assert vocab["llm"] == C.TAG_WEIGHT


def test_score_relevance_label_beats_tag(vocab):
    score, hits = C.score_relevance("신한은행이 AI를 도입", vocab)
    assert score >= C.LABEL_WEIGHT
    assert "신한은행" in hits
    assert C.score_relevance("관련 없는 텍스트", vocab)[0] == 0


# ── host allowlist ─────────────────────────────────────────────────────────
@pytest.mark.parametrize("host,ok", [
    ("etnews.com", True),
    ("www.etnews.com", True),
    ("sub.etnews.com", True),
    ("evil.com", False),
])
def test_host_allowed(host, ok):
    assert C._host_allowed(host, {"etnews.com"}) is ok


# ── classify_link ──────────────────────────────────────────────────────────
def test_classify_link_statuses(vocab):
    allowed = {"etnews.com"}
    known = {C.canonicalize_url("https://etnews.com/known")}

    off_domain = C.classify_link("https://evil.com/신한은행", "신한은행", vocab=vocab,
                                 known=known, allowed=allowed, no_filter=False)
    assert off_domain["status"] == "off-domain"

    dup = C.classify_link("https://etnews.com/known", "신한은행", vocab=vocab,
                          known=known, allowed=allowed, no_filter=False)
    assert dup["status"] == "known-source"

    off_topic = C.classify_link("https://etnews.com/sports", "축구 경기", vocab=vocab,
                                known=known, allowed=allowed, no_filter=False)
    assert off_topic["status"] == "off-topic"

    cand = C.classify_link("https://etnews.com/new", "신한은행 AI 발표", vocab=vocab,
                           known=known, allowed=allowed, no_filter=False)
    assert cand["status"] == "candidate"
    assert cand["score"] >= C.LABEL_WEIGHT


def test_classify_link_matches_on_url_slug(vocab):
    # No concept in the anchor, but the slug carries it.
    c = C.classify_link("https://etnews.com/2026/신한은행-ai", "기사 보기", vocab=vocab,
                        known=set(), allowed={"etnews.com"}, no_filter=False)
    assert c["status"] == "candidate"


@pytest.mark.parametrize("url", [
    "https://search.zdnet.co.kr/?kwd=금융결제원&area=4",
    "https://www.kbanker.co.kr/news/articleList.html?sc_word=신한카드",
    "https://etnews.com/news/tag_list.html?id=1245",
    "https://zdnet.co.kr/category/ai/",
])
def test_classify_link_listing_pages_skipped(url, vocab):
    c = C.classify_link(url, "금융결제원 신한카드", vocab=vocab, known=set(),
                        allowed={"zdnet.co.kr", "kbanker.co.kr", "etnews.com"},
                        no_filter=False)
    assert c["status"] == "listing"


def test_classify_link_article_not_flagged_as_listing(vocab):
    c = C.classify_link("https://zdnet.co.kr/view/?no=20250806124704", "신한은행 에이전틱 AI",
                        vocab=vocab, known=set(), allowed={"zdnet.co.kr"}, no_filter=False)
    assert c["status"] == "candidate"


def test_classify_link_no_filter_bypasses_domain(vocab):
    c = C.classify_link("https://evil.com/x", "신한은행", vocab=vocab,
                        known=set(), allowed={"etnews.com"}, no_filter=True)
    assert c["status"] == "candidate"


# ── crawl orchestration ────────────────────────────────────────────────────
def _fake_fetcher(pages):
    """Return a fetcher mapping url → (final_url, html); None for unknown."""
    def f(url):
        return (url, pages[url]) if url in pages else None
    return f


def test_crawl_depth0_collects_seed_links(vocab):
    pages = {
        "https://etnews.com/seed": """
            <article>
              <a href="https://etnews.com/a">신한은행 AI 도입</a>
              <a href="https://etnews.com/b">축구 결과</a>
              <a href="https://evil.com/c">신한은행</a>
            </article>
        """,
    }
    res = C.crawl(["https://etnews.com/seed"], vocab=vocab, known=set(),
                  allowed={"etnews.com"}, fetcher=_fake_fetcher(pages))
    urls = [c["url"] for c in res["candidates"]]
    assert "https://etnews.com/a" in urls       # relevant + allowlisted
    assert "https://etnews.com/b" not in urls    # off-topic
    assert "https://evil.com/c" not in urls      # off-domain
    assert res["stats"]["pages_fetched"] == 1


def test_crawl_depth1_recurses_into_candidates(vocab):
    pages = {
        "https://etnews.com/seed": '<a href="https://etnews.com/a">신한은행 AI</a>',
        "https://etnews.com/a": '<a href="https://etnews.com/b">에이전틱 AI 은행</a>',
    }
    res = C.crawl(["https://etnews.com/seed"], vocab=vocab, known=set(),
                  allowed={"etnews.com"}, max_depth=1, fetcher=_fake_fetcher(pages))
    urls = [c["url"] for c in res["candidates"]]
    assert "https://etnews.com/a" in urls
    assert "https://etnews.com/b" in urls        # surfaced via depth-1 recursion
    assert res["stats"]["pages_fetched"] == 2


def test_crawl_respects_max_pages(vocab):
    pages = {
        "https://etnews.com/seed": '<a href="https://etnews.com/a">신한은행 AI</a>',
        "https://etnews.com/a": '<a href="https://etnews.com/b">신한은행 AI</a>',
        "https://etnews.com/b": '<a href="https://etnews.com/c">신한은행 AI</a>',
    }
    res = C.crawl(["https://etnews.com/seed"], vocab=vocab, known=set(),
                  allowed={"etnews.com"}, max_depth=9, max_pages=2,
                  fetcher=_fake_fetcher(pages))
    assert res["stats"]["pages_fetched"] <= 2


def test_crawl_per_domain_cap(vocab):
    anchors = "".join(
        f'<a href="https://etnews.com/n{i}">신한은행 AI {i}</a>' for i in range(5)
    )
    pages = {"https://etnews.com/seed": f"<article>{anchors}</article>"}
    res = C.crawl(["https://etnews.com/seed"], vocab=vocab, known=set(),
                  allowed={"etnews.com"}, per_domain_cap=2,
                  fetcher=_fake_fetcher(pages))
    assert len([c for c in res["candidates"] if c["host"] == "etnews.com"]) == 2
    assert res["stats"]["candidates_pre_cap"] == 5


def test_crawl_dedups_candidate_keeping_best_score(vocab):
    pages = {
        "https://etnews.com/seed": (
            '<a href="https://etnews.com/dup">신한은행</a>'
            '<a href="https://etnews.com/dup?utm_source=x">신한은행 에이전틱 AI</a>'
        ),
    }
    res = C.crawl(["https://etnews.com/seed"], vocab=vocab, known=set(),
                  allowed={"etnews.com"}, min_score=1, fetcher=_fake_fetcher(pages))
    # Both links canonicalize to the same URL; the higher-scoring anchor wins.
    assert res["stats"]["candidates_pre_cap"] == 1
    assert res["candidates"][0]["score"] >= C.LABEL_WEIGHT + C.TAG_WEIGHT


def test_crawl_failed_fetch_is_recorded(vocab):
    res = C.crawl(["https://etnews.com/dead"], vocab=vocab, known=set(),
                  allowed={"etnews.com"}, fetcher=_fake_fetcher({}))
    assert res["stats"]["pages_failed"] == 1
    assert res["stats"]["pages_fetched"] == 0


# ── gap-seed derivation ────────────────────────────────────────────────────
def _gaps(track_a):
    return {"track_a": track_a}


def test_seeds_from_gaps_derives_from_hub_backlinks():
    gaps = _gaps({
        "single-source": [{"id": "entities/카카오뱅크.md"}],
        "stale-hub": [{"id": "concepts/MSP.md"}],
        "sparse-cluster": [{"slug": "bank-it-digital"}],  # must be ignored
    })
    backlinks = {
        "카카오뱅크": [{"from": "sources/kakaobank-ai.md"}],
        "MSP": [{"from": "sources/msp-trend.md"}, {"from": "sources/msp-trend.md"}],
    }
    slug_url = {
        "kakaobank-ai": "https://etnews.com/kakaobank",
        "msp-trend": "https://zdnet.co.kr/msp",
    }
    out = C.seeds_from_gaps(gaps_json=gaps, backlinks=backlinks, slug_url=slug_url)
    assert out["entities/카카오뱅크.md"] == ["https://etnews.com/kakaobank"]
    assert out["concepts/MSP.md"] == ["https://zdnet.co.kr/msp"]  # deduped
    assert all("sparse" not in k for k in out)  # cluster gaps excluded


def test_seeds_from_gaps_skips_hub_without_recoverable_url():
    gaps = _gaps({"single-source": [{"id": "entities/PDFOnly.md"}]})
    backlinks = {"PDFOnly": [{"from": "sources/pdf-derived.md"}]}
    out = C.seeds_from_gaps(gaps_json=gaps, backlinks=backlinks, slug_url={})
    assert out == {}  # no url for the source → no seed → hub dropped


def test_seeds_from_gaps_ignores_non_source_backlinks():
    gaps = _gaps({"single-source": [{"id": "entities/Hub.md"}]})
    backlinks = {"Hub": [{"from": "concepts/Other.md"}]}  # hub→hub, not a source
    out = C.seeds_from_gaps(gaps_json=gaps, backlinks=backlinks,
                            slug_url={"Other": "https://x.com"})
    assert out == {}


# ── inbox append ───────────────────────────────────────────────────────────
def test_append_to_inbox_format(tmp_path, monkeypatch):
    inbox = tmp_path / "_inbox.md"
    monkeypatch.setattr(C, "INBOX", inbox)
    cands = [{"url": "https://etnews.com/a", "found_on": "etnews.com", "score": 3}]
    n = C.append_to_inbox(cands)
    assert n == 1
    text = inbox.read_text(encoding="utf-8")
    assert "https://etnews.com/a  # source=auto-crawl found_on=etnews.com score=3 ts=" in text
    assert C._inbox_queue_len() == 1
