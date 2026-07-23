"""`tools/_lib.py` unit tests — encodes the bug classes found in the
2026-06-12 audit as regression guards (frontmatter `---`-in-value early
termination, quote-escape corruption (=the 558-title _backlinks incident),
wikilink regex family semantics, cache invalidation, AUTO block group-ref
injection, slug path injection)."""
import time

import pytest

import _lib
from _lib import (
    FRONTMATTER_BLOCK_RE,
    WIKILINK_ANY_RE,
    WIKILINK_RE,
    WIKILINK_STEM_RE,
    WIKILINK_TARGET_RE,
    atomic_write_if_changed,
    atomic_write_text,
    canonicalize_url,
    parse_frontmatter,
    parse_page_meta,
    read_text_cached,
    safe_link_text,
    safe_slug_path,
    strip_frontmatter,
    title_sort_key,
    update_auto_block,
)


# ---------------------------------------------------------------- frontmatter

def test_parse_frontmatter_scalar_and_lists():
    fm = parse_frontmatter(
        "---\n"
        'title: "제목"\n'
        "type: source\n"
        "tags: [a, b]\n"
        "sources:\n"
        "- one\n"
        "- two\n"
        "---\n본문"
    )
    assert fm["title"] == "제목"
    assert fm["tags"] == ["a", "b"]
    assert fm["sources"] == ["one", "two"]


def test_parse_frontmatter_escaped_quote_title():
    # The prototype of the 558-title _backlinks.json corruption incident — the
    # `.strip('"')` approach dropped the closing quote and left `\"` residue.
    fm = parse_frontmatter('---\ntitle: "안도걸 \\"입법 속도\\""\n---\n')
    assert fm["title"] == '안도걸 "입법 속도"'
    fm2 = parse_frontmatter("---\ntitle: '스테이블코인'\n---\n")
    assert fm2["title"] == "스테이블코인"


def test_frontmatter_dash_in_value_not_truncated():
    # The `---`-in-value trap — input that broke the split("---", 2)·find("---", 3) family.
    text = '---\ntitle: "A --- B"\ntype: source\n---\n본문 시작'
    assert parse_frontmatter(text)["title"] == "A --- B"
    assert strip_frontmatter(text) == "\n본문 시작"


def test_strip_frontmatter_edge_cases():
    assert strip_frontmatter("no frontmatter") == "no frontmatter"
    assert strip_frontmatter("---\nunterminated") == "---\nunterminated"


def test_frontmatter_block_re_group():
    m = FRONTMATTER_BLOCK_RE.match("---\nkey: v\n---\nbody")
    assert m and m.group(1) == "key: v"
    assert FRONTMATTER_BLOCK_RE.match("body first\n---\n") is None


def test_parse_page_meta_title_and_description():
    title, ptype, desc, _sf, date, _su = parse_page_meta(
        "---\n"
        'title: "T"\n'
        "type: entity\n"
        "published: 2026-01-02\n"
        "---\n"
        "<!-- 약어 주석 -->\n"
        "# 헤더\n"
        "이것이 첫 본문 문단이다. 뒤는 잘린다.\n",
        "stub.md",
    )
    assert (title, ptype, date) == ("T", "entity", "2026-01-02")
    assert desc == "이것이 첫 본문 문단이다."


# ---------------------------------------------------------------- wikilink family

def test_wikilink_family_anchor_semantics():
    text = "[[일반]] [[anchored#섹션]] [[aliased|표시]] [[anchor알리아스#s|표시]]"
    # WIKILINK_RE — does not match anchored links at all (basis for audit A3 ruling).
    assert WIKILINK_RE.findall(text) == ["일반", "aliased"]
    # TARGET — captures the full anchor-inclusive target (normalization is the comparison site's job).
    assert WIKILINK_TARGET_RE.findall(text) == ["일반", "anchored#섹션", "aliased", "anchor알리아스#s"]
    # STEM — consumes alias·anchor, leaving only the bare stem.
    assert WIKILINK_STEM_RE.findall(text) == ["일반", "anchored", "aliased", "anchor알리아스"]
    # ANY — existence count.
    assert len(WIKILINK_ANY_RE.findall(text)) == 4


# ---------------------------------------------------------------- url·slug·misc

def test_canonicalize_url_tracking_and_order():
    a = canonicalize_url("HTTPS://News.Example.com/a?utm_source=x&b=2&a=1&fbclid=z#frag")
    b = canonicalize_url("https://news.example.com/a?a=1&b=2")
    assert a == b
    # path is identity-bearing — case is preserved.
    assert canonicalize_url("https://e.com/Path") != canonicalize_url("https://e.com/path")


def test_safe_slug_path_rejects_injection(tmp_path):
    assert safe_slug_path(tmp_path, "ok-slug-1").name == "ok-slug-1.md"
    for bad in ("../escape", "a/b", "한글", "", "UPPER"):
        with pytest.raises(ValueError):
            safe_slug_path(tmp_path, bad)


def test_update_auto_block_literal_backslash():
    src = "head\n<!-- AUTO:X BEGIN -->\nold\n<!-- AUTO:X END -->\ntail"
    body = r"C:\Users\foo \1 \g<0>"  # input that crashed/corrupted if interpreted as a group-ref
    out, found = update_auto_block(src, "X", body)
    assert found and body in out and "old" not in out
    _out2, found2 = update_auto_block("no markers", "X", "y")
    assert not found2


def test_title_sort_key_korean_first(monkeypatch):
    # Hangul-first ordering is gated on korean_mode(); pin the corpus language so
    # the assertion still exercises ko-mode sorting.
    monkeypatch.setenv("WIKI_LANG", "ko")
    items = sorted([("Alpha",), ("나비",), ("beta",)], key=title_sort_key)
    assert [i[0] for i in items] == ["나비", "Alpha", "beta"]


def test_safe_link_text_brackets():
    assert safe_link_text("[단독] 제목") == "【단독】 제목"


# ---------------------------------------------------------------- cache·atomicity

def test_read_text_cached_invalidates_on_write(tmp_path):
    f = tmp_path / "x.md"
    atomic_write_text(f, "v1")
    assert read_text_cached(f) == "v1"
    time.sleep(0.01)  # guard against mtime_ns resolution
    atomic_write_text(f, "v2-changed")  # --fix rewrite scenario
    assert read_text_cached(f) == "v2-changed"


def test_read_text_cached_missing_raises(tmp_path):
    with pytest.raises(OSError):
        read_text_cached(tmp_path / "absent.md")


def test_atomic_write_if_changed_noop(tmp_path):
    f = tmp_path / "y.md"
    assert atomic_write_if_changed(f, "same") is True
    assert atomic_write_if_changed(f, "same") is False
    assert atomic_write_if_changed(f, "diff") is True


def test_lib_source_date_cache_dict_exists():
    # read_source_date depends on the live corpus (WIKI), so here we only guard the cache contract.
    assert isinstance(_lib._SOURCE_DATE_CACHE, dict)


# --- staleness dependency-index date key recalibration (2026-06-13) ---
# A source's upstream propagation date should be the content date
# (scraped→published), not the wiki edit date (last_updated). Using the edit
# date means a structural edit with zero factual change — like the Phase 2 schema
# migration — induces phantom staleness in every hub that cites that source
# (2026-06-13: 125→27 cases, 94 entity/concept false positives removed). It must
# be scraped-first, not published-first, to preserve the true signal (an article
# whose published date is in the past but which entered the corpus late = the
# Citibank Korea sc-gpt case).
def _dep_mod():
    import importlib
    import sys
    from pathlib import Path
    bp = str(Path(__file__).resolve().parent.parent / "tools" / "_build")
    if bp not in sys.path:
        sys.path.insert(0, bp)
    return importlib.import_module("dependencies")


def test_source_content_date_prefers_scraped_over_last_updated():
    dep = _dep_mod()
    # Phase 2 migration pattern: a 2024 article with only last_updated bumped to 2026-05.
    fm = {"type": "source", "scraped": "2024-02-22", "last_updated": "2026-05-04"}
    assert dep._source_content_date(fm) == "2024-02-22"


def test_source_content_date_scraped_beats_older_published():
    dep = _dep_mod()
    # Citibank Korea sc-gpt: published in January but entered the corpus 4-29 = true freshness.
    fm = {"type": "source", "published": "2026-01-21", "scraped": "2026-04-29"}
    assert dep._source_content_date(fm) == "2026-04-29"


def test_source_content_date_falls_back_to_page_date():
    dep = _dep_mod()
    # If both scraped·published are absent, fall back to legacy _page_date(last_updated/date/created).
    fm = {"type": "source", "last_updated": "2026-03-01"}
    assert dep._source_content_date(fm) == "2026-03-01"


def test_non_source_page_date_uses_last_updated():
    dep = _dep_mod()
    # A hub (entity, etc.) still uses the edit date (last_updated) as its own date — for downstream rulings.
    fm = {"type": "entity", "last_updated": "2026-04-10"}
    assert dep._page_date(fm) == "2026-04-10"


def test_hub_propagates_composite_date():
    """A hub contributes max(its narrative date, newest cited source content
    date) as UPSTREAM, so a newly ingested source still reaches derived pages
    now that a `sources:` append no longer bumps the hub's `last_updated`. Its
    own record keeps the narrative date."""
    dep = _dep_mod()
    meta = {
        "entities/Hub.md": {"type": "entity", "last_updated": "2026-06-26",
                            "sources": ["fresh-src"], "body": ""},
        "sources/fresh-src.md": {"type": "source", "last_updated": "2026-07-19",
                                 "sources": [], "body": ""},
    }
    # mirrors _scan_pages: both the bare stem and the rel are keys
    stem_to_rel = {"fresh-src": "sources/fresh-src.md",
                   "sources/fresh-src.md": "sources/fresh-src.md"}
    prop = dep._hub_propagated(meta, stem_to_rel)
    assert prop["entities/Hub.md"] == "2026-07-19"      # source pulls it forward
    assert "sources/fresh-src.md" not in prop           # sources are not hubs


def test_unresolved_wikilinks_matches_structure_normalization():
    """The write-time advisory and the `graph structure` batch check must agree.
    Anchors split, escaped-pipe backslash trimmed, code fences ignored, and a
    path-qualified target stays unresolved (structure.py keys on bare stems)."""
    import _lib
    stems = {"Meta", "Mozilla"}
    assert _lib.unresolved_wikilinks("[[Meta]] [[Mozilla#Stance]]", stems) == []
    assert _lib.unresolved_wikilinks("[[Ghost]]", stems) == ["Ghost"]
    assert _lib.unresolved_wikilinks("[[Meta\\|alias]]", stems) == []
    assert _lib.unresolved_wikilinks("```\n[[Ghost]]\n```", stems) == []
    assert _lib.unresolved_wikilinks("[[entities/Meta]]", stems) == ["entities/Meta"]
    # first-seen order, deduplicated
    assert _lib.unresolved_wikilinks("[[B]] [[A]] [[B]]", stems) == ["B", "A"]
