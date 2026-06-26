"""Link-following crawl enrichment — an OKF-style web pass for gap augmentation.

Complements `/wiki-news --gap` (WebSearch). Instead of querying a search engine,
this follows the *outbound links* of known-good seed pages and surfaces the ones
that

  (a) live on an allowlisted news domain (`tools/_news/domains.py`),
  (b) are not already a wiki source (`_source_map.json::by_url`, canonical), and
  (c) mention an existing wiki concept (a hub label or tag).

Test (c) is OKF's "relevance to existing concepts", made deterministic against
the hub/tag vocabulary the wiki already holds — hub labels score 2, tags 1, so a
single concrete entity mention clears the default threshold while a lone generic
tag does not.

Why a second channel beside `--gap`: a search engine surfaces pages that match a
*query*; a link crawl surfaces pages that known sources *cite* — adjacency a
query never reaches (the OKF web-pass value proposition). Both feed the same
`raw/_inbox.md` queue, so fetch + ingest + the desk publish gate stay downstream
unchanged. This tool NEVER writes wiki pages: editorial judgment is deferred to
the reporter (source authoring) and the desk (publish gate). It is read-only by
default; `--append-inbox` is the one opt-in side effect.

Deterministic + testable: no LLM, no search API. The crawl/classify core takes
an injectable `fetcher` so tests run without network.

Usage:
    python tools/_news/crawl.py --url https://example.com/article [--url ...]
    python tools/_news/crawl.py --seed-file seeds.txt --json
    python tools/_news/crawl.py --url <seed> --append-inbox

Safety caps (OKF web-pass limits):
    --max-pages       total pages fetched, seeds + followed (default 5)
    --max-depth       link-hops to FOLLOW beyond seeds (default 0 = seeds only)
    --per-domain-cap  max candidates surfaced from one domain (default 3)
    --min-score       relevance threshold (default 2; label=2, tag=1)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
from urllib.parse import unquote, urlparse

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent.parent))  # _news/ → tools/ root
from _lib import REPO_ROOT, WIKI, canonicalize_url, korean_mode  # noqa: E402
from _net import safe_get_stream, UnsafeURLError  # noqa: E402
from _news.domains import GLOBAL_IT_FINANCE_NEWS, KOREAN_IT_FINANCE_NEWS  # noqa: E402
from _news.gap_queries import _load_hub_fm, load_gaps_json  # noqa: E402
from _news.normalize import hub_korean_label, normalize_tags  # noqa: E402
from _ingest.fetch_article import HEADERS, extract_links  # noqa: E402

INBOX = REPO_ROOT / "raw" / "_inbox.md"
SOURCE_MAP = WIKI / "sources" / "_source_map.json"
BACKLINKS = WIKI / "_backlinks.json"

# Track-A gap types that map to a specific hub (so their existing sources give a
# crawl seed). sparse-cluster is cluster-scoped — no single seed URL — so it
# stays on the WebSearch path (`/wiki-news --gap`), not the crawl path.
HUB_GAP_TYPES = ("single-source", "stale-hub")

# Concept-relevance weights. A hub label is a specific entity/concept name
# (e.g. 신한은행, 에이전틱 AI) so one hit is a strong signal; a tag is broader, so
# it takes two to clear the default threshold on its own.
LABEL_WEIGHT = 2
TAG_WEIGHT = 1

# Minimum length for an ASCII/Latin vocabulary term — single/double-char
# acronyms (AI, IT, ML) match almost any tech page and would make every link a
# candidate. Hangul is exempt at length 2: terms like 은행·보험·증권·카드
# (bank·insurance·securities·card) are specific.
MIN_TERM_LEN = 3
_HANGUL = re.compile(r"[가-힣]")


def _term_ok(term: str) -> bool:
    """Keep a vocabulary term iff it carries enough signal.

    `len >= MIN_TERM_LEN` for any script, OR (under WIKI_LANG=ko) a 2-char term
    containing Hangul (meaningful Korean domain words the blunt length cut would
    otherwise drop). The Hangul exemption never fires on English vocabulary, so
    gating it is intent-making rather than a behavior change for an English corpus.
    """
    if len(term) >= MIN_TERM_LEN:
        return True
    return korean_mode() and len(term) >= 2 and bool(_HANGUL.search(term))

# Inbox queue alarm — mirrors the `/wiki-news --gap` cap so the operator sees a
# consistent backpressure signal regardless of which channel filled the queue.
INBOX_ALARM = 30


# URL shapes that are index/search/listing pages rather than single articles —
# the crawl wants editorial article targets, not navigation. Matched (lowercased)
# against host + path + query so it generalizes across outlets (dedicated search
# hosts, tag/category indexes, keyword-search and paginated-list query params).
LISTING_MARKERS = (
    "articlelist", "tag_list", "/tag/", "/tags/", "/category/", "/categories/",
    "/search", "kwd=", "sc_word=", "/sitemap", "/rss", "/feed",
)


def _is_listing(url: str) -> bool:
    """True iff the URL is a search/index/listing page, not an article.

    A dedicated `search.*` host is always a listing; otherwise match the
    path+query against `LISTING_MARKERS`. Conservative by design — section
    indexes without a marker word (e.g. `/kr/enterprise-applications/`) slip
    through and are caught downstream by the operator/desk gate."""
    p = urlparse(url)
    if (p.hostname or "").lower().startswith("search."):
        return True
    hay = (p.path + "?" + (p.query or "")).lower()
    return any(m in hay for m in LISTING_MARKERS)


def allowed_hosts() -> set[str]:
    """Union of the Korean + global news allowlists (registrable suffixes)."""
    return set(KOREAN_IT_FINANCE_NEWS) | set(GLOBAL_IT_FINANCE_NEWS)


def _registrable_host(host: str) -> str:
    """Lowercase host with a leading `www.` stripped so apex and www variants
    collapse to one key for capping, dedup, and provenance."""
    host = (host or "").lower()
    return host[4:] if host.startswith("www.") else host


def _host_allowed(host: str, allowed: set[str]) -> bool:
    """True iff `host` equals or is a subdomain of any allowlisted domain."""
    host = _registrable_host(host)
    return any(host == d or host.endswith("." + d) for d in allowed)


def build_vocabulary(hub_fm: dict[str, dict] | None = None) -> dict[str, int]:
    """Build the relevance vocabulary `{term: weight}` from the wiki's hubs.

    Hub labels (the Korean searchable form of each entity/concept title) get
    `LABEL_WEIGHT`; normalized tags get `TAG_WEIGHT`. A label also wins over a
    tag of the same string. Terms shorter than `MIN_TERM_LEN` are dropped.
    `hub_fm` is injectable for tests; defaults to a live load of every hub.
    """
    if hub_fm is None:
        hub_fm = _load_hub_fm()
    vocab: dict[str, int] = {}
    for hub_id, fm in hub_fm.items():
        t = fm.get("title")
        raw = t if isinstance(t, str) and t else hub_id.split("/")[-1].removesuffix(".md")
        label = hub_korean_label(raw).strip().lower()
        if _term_ok(label):
            vocab[label] = LABEL_WEIGHT
        for tag in normalize_tags(fm.get("tags") or []):
            t = tag.strip().lower()
            if _term_ok(t) and vocab.get(t, 0) < TAG_WEIGHT:
                vocab[t] = TAG_WEIGHT
    return vocab


def score_relevance(text: str, vocab: dict[str, int]) -> tuple[int, list[str]]:
    """Sum the weights of distinct vocabulary terms occurring in `text`.

    Returns `(score, matched_terms)`. Matching is case-insensitive substring
    — Korean labels rarely produce spurious substrings, and dropping <3-char
    terms removes the worst English false positives."""
    haystack = text.lower()
    score = 0
    hits: list[str] = []
    for term, weight in vocab.items():
        if term in haystack:
            score += weight
            hits.append(term)
    return score, hits


def _load_known_urls() -> set[str]:
    """Canonical set of every URL already recorded in the source map."""
    if not SOURCE_MAP.exists():
        return set()
    sm = json.loads(SOURCE_MAP.read_text(encoding="utf-8"))
    return {canonicalize_url(u) for u in (sm.get("by_url") or {})}


def _slug_to_url() -> dict[str, str]:
    """Reverse the source map into `{source_slug: url}` (first url wins).

    `_source_map.json::by_url` is `{url: slug}`; near-1:1 in practice, so the
    reverse is unambiguous enough to resolve a citing source back to its URL."""
    if not SOURCE_MAP.exists():
        return {}
    sm = json.loads(SOURCE_MAP.read_text(encoding="utf-8"))
    rev: dict[str, str] = {}
    for url, slug in (sm.get("by_url") or {}).items():
        rev.setdefault(slug, url)
    return rev


def seeds_from_gaps(gap_types: tuple[str, ...] = HUB_GAP_TYPES, *, limit: int = 5,
                    gaps_json: dict | None = None, backlinks: dict | None = None,
                    slug_url: dict[str, str] | None = None) -> dict[str, list[str]]:
    """Derive crawl seeds for hub-scoped Track-A gaps → `{hub_id: [seed_urls]}`.

    For each under-served hub, follow its citing sources (`_backlinks.json`,
    keyed by hub stem) to their canonical URLs (`_slug_to_url`). Those existing
    sources are the pages that already cover the hub, so crawling them harvests
    the *adjacent* pages they cite — the gap-fill signal. Hubs whose sources
    have no recoverable URL (PDF/AiChat-derived) yield no seed and are skipped.
    All data inputs are injectable for testing.
    """
    if gaps_json is None:
        gaps_json = load_gaps_json(limit=limit)
    if backlinks is None:
        backlinks = json.loads(BACKLINKS.read_text(encoding="utf-8")) if BACKLINKS.exists() else {}
    if slug_url is None:
        slug_url = _slug_to_url()
    track_a = gaps_json.get("track_a", {})
    out: dict[str, list[str]] = {}
    for gt in gap_types:
        for row in (track_a.get(gt) or [])[:limit]:
            hub_id = row.get("id")
            if not hub_id:
                continue
            stem = hub_id.split("/")[-1].removesuffix(".md")
            urls: list[str] = []
            for bl in backlinks.get(stem, []):
                frm = bl.get("from", "")
                if not frm.startswith("sources/"):
                    continue
                sslug = frm.split("/", 1)[1].removesuffix(".md")
                u = slug_url.get(sslug)
                if u and u not in urls:
                    urls.append(u)
            if urls:
                out[hub_id] = urls
    return out


def classify_link(url: str, anchor: str, *, vocab: dict[str, int],
                  known: set[str], allowed: set[str], no_filter: bool) -> dict:
    """Classify one harvested link into skip/candidate, with the reason.

    Decision order (first match wins), mirroring OKF's skip/enrich triage:
      off-domain    — host not on the allowlist (unless `no_filter`)
      listing       — search/index/listing page, not an article
      known-source  — canonical URL already in the source map
      off-topic     — no concept-relevance signal (score below threshold is
                      decided by the caller; here score 0 is off-topic)
      candidate     — allowlisted, novel, concept-relevant
    The relevance text is the anchor plus the URL's decoded path so a bare
    "[article](/2026/shinhan-ai)" link still matches on the slug.
    """
    host = _registrable_host(urlparse(url).hostname or "")
    relevance_text = f"{anchor} {unquote(urlparse(url).path)}"
    score, hits = score_relevance(relevance_text, vocab)
    base = {"url": url, "anchor": anchor, "host": host, "score": score, "hits": hits}
    if not no_filter and not _host_allowed(host, allowed):
        return {**base, "status": "off-domain"}
    if _is_listing(url):
        return {**base, "status": "listing"}
    if canonicalize_url(url) in known:
        return {**base, "status": "known-source"}
    if score <= 0:
        return {**base, "status": "off-topic"}
    return {**base, "status": "candidate"}


def _fetch_page(url: str, timeout: int = 15) -> tuple[str, str] | None:
    """SSRF-safe GET → `(final_url, html)`, or None on block/error.

    Seeds are operator-chosen known-good pages, so this uses the plain
    `safe_get_stream` path rather than fetch_article's full WAF/Wayback
    ladder — a blocked seed is logged and skipped, not recovered. (Escalating
    a seed to the heavy fallback is a deliberate non-goal for the PoC.)
    """
    try:
        with safe_get_stream(url, headers=HEADERS, timeout=timeout) as r:
            if r.status_code >= 400:
                return None
            if "html" not in r.headers.get("Content-Type", "").lower():
                return None
            if r.encoding and r.encoding.lower() in ("iso-8859-1", "latin-1"):
                r.encoding = r.apparent_encoding or "utf-8"
            return r.url, r.text
    except (requests.exceptions.RequestException, UnsafeURLError):
        return None


def crawl(seeds: list[str], *, vocab: dict[str, int], known: set[str],
          allowed: set[str], max_pages: int = 5, max_depth: int = 0,
          per_domain_cap: int = 3, min_score: int = 2, no_filter: bool = False,
          fetcher: Callable[[str], "tuple[str, str] | None"] = _fetch_page) -> dict:
    """Breadth-first link crawl from `seeds`, surfacing relevant novel links.

    Fetches each seed (depth 0), harvests + classifies its outbound links, and
    collects the candidates. When `max_depth > 0`, allowlisted novel candidate
    pages are themselves fetched (depth+1) up to `max_pages` total fetches —
    the OKF recursive web pass, bounded. Candidates are deduped by canonical
    URL (best score wins), ranked by score, then trimmed by `per_domain_cap`.

    `fetcher` is injectable so tests drive the crawl from in-memory HTML with
    no network. Returns a result dict (visited / candidates / skipped / stats).
    """
    queue: deque[tuple[str, int]] = deque((s, 0) for s in seeds)
    fetched_canon: set[str] = set()
    visited: list[dict] = []
    cand_by_url: dict[str, dict] = {}
    skipped = Counter()

    while queue and len(visited) < max_pages:
        url, depth = queue.popleft()
        canon = canonicalize_url(url)
        if canon in fetched_canon:
            continue
        fetched_canon.add(canon)

        page = fetcher(url)
        if page is None:
            visited.append({"url": url, "depth": depth, "ok": False, "links": 0})
            continue
        final_url, html = page
        links = extract_links(BeautifulSoup(html, "html.parser"), final_url)
        visited.append({"url": final_url, "depth": depth, "ok": True, "links": len(links)})

        seed_host = _registrable_host(urlparse(final_url).hostname or "")
        for link_url, anchor in links:
            c = classify_link(link_url, anchor, vocab=vocab, known=known,
                              allowed=allowed, no_filter=no_filter)
            if c["status"] != "candidate" or c["score"] < min_score:
                skipped[c["status"] if c["status"] != "candidate" else "below-threshold"] += 1
                continue
            lc = canonicalize_url(link_url)
            if lc in fetched_canon:
                continue
            prev = cand_by_url.get(lc)
            if prev is None or c["score"] > prev["score"]:
                c = {**c, "found_on": seed_host}
                cand_by_url[lc] = c
            # Recurse into novel candidate pages when depth budget allows.
            if depth < max_depth and lc not in fetched_canon:
                queue.append((link_url, depth + 1))

    candidates = _rank_and_cap(list(cand_by_url.values()), per_domain_cap)
    return {
        "seeds": seeds,
        "visited": visited,
        "candidates": candidates,
        "stats": {
            "pages_fetched": sum(1 for v in visited if v["ok"]),
            "pages_failed": sum(1 for v in visited if not v["ok"]),
            "candidates": len(candidates),
            "candidates_pre_cap": len(cand_by_url),
            **{f"skipped_{k}": v for k, v in skipped.items()},
        },
    }


def _rank_and_cap(candidates: list[dict], per_domain_cap: int) -> list[dict]:
    """Sort candidates by score (desc) then enforce the per-domain cap.

    Sorting before capping means each domain keeps its highest-scoring links.
    A secondary key on URL keeps the order deterministic across runs."""
    candidates.sort(key=lambda c: (-c["score"], c["url"]))
    per_domain: Counter = Counter()
    out: list[dict] = []
    for c in candidates:
        if per_domain[c["host"]] >= per_domain_cap:
            continue
        per_domain[c["host"]] += 1
        out.append(c)
    return out


def append_to_inbox(candidates: list[dict]) -> int:
    """Append candidates to `raw/_inbox.md` with crawl provenance.

    Line format matches the single-queue model consumed by
    `tools/_ingest/fetch_inbox.py`:
        <url>  # source=auto-crawl found_on=<host> score=<n> ts=<iso>
    Returns the number of lines appended. Creates the file (header only) if
    absent. The operator drains the queue via `/wiki-ingest inbox`.
    """
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    lines = [
        f"{c['url']}  # source=auto-crawl found_on={c['found_on']} "
        f"score={c['score']} ts={ts}"
        for c in candidates
    ]
    if not lines:
        return 0
    existing = INBOX.read_text(encoding="utf-8") if INBOX.exists() else "# Inbox\n"
    if not existing.endswith("\n"):
        existing += "\n"
    INBOX.write_text(existing + "\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)


def _inbox_queue_len() -> int:
    """Count active URL lines in the inbox (non-empty, non-comment)."""
    if not INBOX.exists():
        return 0
    return sum(
        1 for ln in INBOX.read_text(encoding="utf-8").splitlines()
        if ln.strip().startswith(("http://", "https://"))
    )


def render_report(result: dict) -> str:
    s = result["stats"]
    lines = [
        "=== crawl enrichment ===",
        f"Seeds:          {len(result['seeds'])}",
        f"Pages fetched:  {s['pages_fetched']}  (failed: {s['pages_failed']})",
        f"Candidates:     {s['candidates']}  (pre-cap: {s['candidates_pre_cap']})",
        "",
    ]
    skips = {k[len("skipped_"):]: v for k, v in s.items() if k.startswith("skipped_")}
    if skips:
        lines.append("Skipped links: " + ", ".join(f"{k}={v}" for k, v in sorted(skips.items())))
        lines.append("")
    if result["candidates"]:
        lines.append(f"--- Candidates ({len(result['candidates'])}) ---")
        for c in result["candidates"]:
            lines.append(f"- [{c['score']}] {c['url']}")
            label = c["anchor"] or "(no anchor)"
            lines.append(f"      {label}  ← {', '.join(c['hits'][:5])}")
        lines.append("")
    else:
        lines.append("No relevant novel candidates surfaced.")
        lines.append("")
    return "\n".join(lines)


def _read_seeds(args: argparse.Namespace) -> list[str]:
    seeds = list(args.url or [])
    if args.seed_file:
        for ln in Path(args.seed_file).read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if ln.startswith(("http://", "https://")):
                seeds.append(ln)
    # Dedup preserving order.
    seen: set[str] = set()
    out: list[str] = []
    for s in seeds:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Link-following crawl enrichment (OKF-style web pass).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--url", action="append", help="seed URL (repeatable)")
    ap.add_argument("--seed-file", help="file with one seed URL per line")
    ap.add_argument("--gap-seed", action="store_true",
                    help="derive seeds from hub-scoped Track-A gaps "
                         "(single-source·stale-hub) — the gap-fill entry point")
    ap.add_argument("--gap-type", choices=list(HUB_GAP_TYPES), default=None,
                    help="with --gap-seed: restrict to one hub-gap type")
    ap.add_argument("--max-pages", type=int, default=5, help="total pages fetched (default 5)")
    ap.add_argument("--max-depth", type=int, default=0,
                    help="link-hops to follow beyond seeds (default 0 = seeds only)")
    ap.add_argument("--per-domain-cap", type=int, default=3,
                    help="max candidates surfaced per domain (default 3)")
    ap.add_argument("--min-score", type=int, default=2,
                    help="relevance threshold; label=2 tag=1 (default 2)")
    ap.add_argument("--no-filter", action="store_true", help="disable the domain allowlist")
    ap.add_argument("--append-inbox", action="store_true",
                    help="append candidates to raw/_inbox.md (default: report only)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    args = ap.parse_args()

    gap_seed_map: dict[str, list[str]] = {}
    if args.gap_seed:
        gap_types = (args.gap_type,) if args.gap_type else HUB_GAP_TYPES
        try:
            gap_seed_map = seeds_from_gaps(gap_types, limit=args.max_pages)
        except RuntimeError as e:
            print(f"ERROR: gap diagnosis unavailable — {e}", file=sys.stderr)
            return 2
        seeds = [u for urls in gap_seed_map.values() for u in urls]
        if not seeds:
            print("No hub-scoped Track-A gaps with recoverable seed URLs "
                  "(single-source·stale-hub). Nothing to crawl.")
            return 0
    else:
        seeds = _read_seeds(args)
        if not seeds:
            print("ERROR: provide seeds via --url/--seed-file, or use --gap-seed",
                  file=sys.stderr)
            return 2

    result = crawl(
        seeds,
        vocab=build_vocabulary(),
        known=_load_known_urls(),
        allowed=allowed_hosts(),
        max_pages=args.max_pages,
        max_depth=args.max_depth,
        per_domain_cap=args.per_domain_cap,
        min_score=args.min_score,
        no_filter=args.no_filter,
    )

    if gap_seed_map:
        result["gap_seeds"] = gap_seed_map

    appended = 0
    if args.append_inbox:
        appended = append_to_inbox(result["candidates"])
        result["stats"]["appended_to_inbox"] = appended

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if gap_seed_map:
            print(f"Gap-seed: {len(gap_seed_map)} hub(s) → {len(seeds)} seed URL(s)")
            for hub_id, urls in gap_seed_map.items():
                print(f"  {hub_id}  ({len(urls)} source seed)")
            print()
        print(render_report(result))
        if args.append_inbox:
            qlen = _inbox_queue_len()
            print(f"Appended {appended} candidate(s) to raw/_inbox.md  (queue: {qlen})")
            if qlen >= INBOX_ALARM:
                print(f"  ⚠ queue length {qlen} ≥ {INBOX_ALARM} — drain via /wiki-ingest inbox")
    return 0


if __name__ == "__main__":
    sys.exit(main())
