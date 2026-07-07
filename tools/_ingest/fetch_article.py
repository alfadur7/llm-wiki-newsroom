"""Fetch article from URL with browser-like headers, save as markdown.

Usage:
    python tools/_ingest/fetch_article.py <url> [output_filename]

Output:
  HTML URL : raw/NewsScrap/<slug>.md   (Obsidian Web Clipper compatible)
  PDF URL  : raw/PDF/<slug>.pdf        (binary only — no stub markdown)
             PDFs are centrally managed under raw/PDF/. Next /wiki-ingest
             pass scans raw/PDF/ for new *.pdf files; Claude reads the
             binary directly and creates wiki/sources/<slug>.md with
             `source_file:` pointing at the PDF and (when known)
             `source_url:` set to the download URL. The wiki source
             page is the authoritative home for URL metadata.

Rationale:
  WebSearch results often return URLs that reject generic bot User-Agents.
  This script mimics a browser to bypass simple bot detection. PDF support
  lets the same pipeline absorb regulator reports, broker research notes,
  and conference decks without a separate ingestion path.
"""
import sys
import re
from pathlib import Path
from datetime import date
from typing import Callable
from urllib.parse import urlparse, parse_qs, unquote, urljoin

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent.parent))  # _ingest/ → tools/ root (shared modules)
from _net import (  # noqa: E402
    safe_get,
    safe_get_stream,
    curl_get,
    wayback_snapshot,
    BLOCKED_STATUSES,
    CurlUnavailable,
    UnsafeURLError,
)
from _lib import (  # noqa: E402
    korean_mode,
    REPO_ROOT as _REPO_ROOT,
    atomic_write_bytes,
    atomic_write_text,
)

# Browser-like headers to bypass simple bot detection
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    # English-native by default; under WIKI_LANG=ko send the Korean-first
    # header so ko-locale sites serve their Korean rendering.
    "Accept-Language": (
        "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
        if korean_mode()
        else "en-US,en;q=0.9"
    ),
    # `br` excluded — without the `brotli`/`brotlicffi` package, requests
    # can't auto-decompress a Brotli response, and `r.text` decodes the
    # compressed raw bytes as-is, garbling the entire body (reproduced on
    # some domains such as modern Discourse and wikidocs). gzip/deflate
    # alone gets a valid response from every site, so we prioritize
    # dependency-free compatibility here.
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Cache-Control": "max-age=0",
}

# URL variant fallbacks — applied only when the default fetch returns short content.
# Each entry: (domain suffix, transform fn). Transform should return None or the
# original URL if no variant applies. Sites here typically render the desktop
# page client-side via JS, but expose a server-rendered AMP/print variant that
# fetch_article can extract directly. Add entries as failures accumulate (see
# raw/_archive.md FAILED:short-content patterns).
def _chosun_amp(url: str) -> str:
    """chosun.com family — append ?outputType=amp (leave as-is if already present)."""
    parsed = urlparse(url)
    if "outputType=amp" in (parsed.query or ""):
        return url
    sep = "&" if parsed.query else "?"
    return url + sep + "outputType=amp"


def _naver_link_bridge_expand(url: str) -> str | None:
    """link.naver.com/bridge?url=<encoded>&dst=... → extract the real article URL.

    A naver.me shortlink, after safe_get_stream follows the redirect, lands
    final_url at link.naver.com/bridge. The bridge page itself is short HTML
    meant to invoke the mobile app (no article selector match → short-content
    fail), so fetching it is pointless. Unquote the `url` query parameter and
    return the real article URL.
    """
    parsed = urlparse(url)
    if not parsed.path.startswith("/bridge"):
        return None
    qs = parse_qs(parsed.query)
    target = qs.get("url", [None])[0]
    return unquote(target) if target else None


def unwrap_share_wrapper(url: str) -> str:
    """Unwrap a known share/redirect interstitial that embeds the real URL in
    a query param, returning the embedded URL (else the input unchanged).

    LinkedIn's mobile share-sheet wraps outbound links in
    `linkedin.com/safety/go/?url=<encoded>&...`. That interstitial itself
    404s on fetch (it is a JS warning page, not a redirect), so unwrap it
    BEFORE fetching — the embedded `url` is the real destination (often an
    `lnkd.in` shortlink that then redirects to the article). Applied once at
    the fetch entry point so both the PDF-sniff and HTML paths see the real
    URL, and the saved `source_url` anchors to the destination, not the
    wrapper.
    """
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    host = host[4:] if host.startswith("www.") else host
    if host == "linkedin.com" and parsed.path.startswith("/safety/go"):
        target = parse_qs(parsed.query).get("url", [None])[0]
        if target:
            return unquote(target)
    return url


URL_VARIANT_FALLBACKS: list[tuple[str, Callable[[str], str | None]]] = [
    ("chosun.com", _chosun_amp),  # matches both biz.chosun.com and www.chosun.com
    ("link.naver.com", _naver_link_bridge_expand),  # final_url of a naver.me shortlink
]


def _matches_domain(url: str, domain: str) -> bool:
    host = urlparse(url).netloc.lower()
    return host == domain or host.endswith("." + domain)


def get_fallback_urls(url: str) -> list[str]:
    """Return domain-specific alternate URLs to try on short-content failure.

    Empty list if the URL has no registered variant. Returned variants are
    deduplicated and exclude the original URL.
    """
    out: list[str] = []
    for domain, transform in URL_VARIANT_FALLBACKS:
        if _matches_domain(url, domain):
            alt = transform(url)
            if alt and alt != url and alt not in out:
                out.append(alt)
    return out


# Common content selectors for Korean news sites
CONTENT_SELECTORS = [
    "article",
    "div.article_body",
    "div#articleBodyContents",
    "div.article-body",
    "div.news_content",
    "div#contents",
    "div.view_text",
    "div#newsEndContents",
    "div.article_view",
    "main",
]


def clean_filename(title: str, max_len: int = 80) -> str:
    """Make filename-safe string from title.

    Strips:
      - Windows-illegal chars (`<>:"/\\|?*`)
      - ASCII control chars (0x00-0x1F + DEL 0x7F) — NUL truncation on
        POSIX, `OSError: [Errno 22]` on Windows
      - Leading dots (`.`/`..` would walk up the directory tree once
        joined with output_dir)
      - Trailing dots and whitespace (Windows strips these silently and
        the resulting name collides with siblings)
    """
    s = re.sub(r'[\x00-\x1f\x7f<>:"/\\|?*]', '', title)
    s = re.sub(r'\s+', ' ', s).strip()
    s = s.lstrip('.')
    s = s.rstrip(' .')
    if len(s) > max_len:
        s = s[:max_len].rstrip(' .')
    return s


def _safe_join(output_dir: Path, filename: str) -> Path:
    """Join `filename` under `output_dir`, asserting the resolved path
    stays inside `output_dir`. Raises ValueError on traversal attempt.

    Defense in depth — `clean_filename` already strips path separators
    and leading dots, but a server-supplied Content-Disposition value
    may bypass that helper if a future call site forgets to sanitize.
    """
    output_dir = output_dir.resolve()
    candidate = (output_dir / filename).resolve()
    try:
        candidate.relative_to(output_dir)
    except ValueError as e:
        raise ValueError(
            f"path traversal blocked: `{filename}` escapes `{output_dir}`"
        ) from e
    return candidate


def _resolve_unique_path(title: str, url: str, output_dir: Path,
                         ext: str, default: str) -> Path:
    """Return a non-colliding `<slug>.<ext>` path under `output_dir`.

    Slug derivation order: cleaned title → URL last path segment →
    `default`. When `<slug>.<ext>` already exists, append `_2`/`_3`/…
    until a free name is found.

    Why both fallback layers + collision suffix:
    a single hard-coded `default` (e.g. "article") meant two URLs whose
    title extraction failed in the same run silently overwrote each
    other. The path segment fallback restores per-URL distinctness, and
    the numeric suffix protects against any residual collision (incl.
    two distinct URLs whose extracted titles legitimately collapse to
    the same slug after `clean_filename`).
    """
    slug = clean_filename(title)
    if not slug:
        seg = urlparse(url).path.rstrip("/").rsplit("/", 1)[-1]
        slug = clean_filename(seg)
    if not slug:
        slug = default
    candidate = _safe_join(output_dir, f"{slug}.{ext}")
    n = 2
    while candidate.exists():
        candidate = _safe_join(output_dir, f"{slug}_{n}.{ext}")
        n += 1
    return candidate


def _yaml_safe_string(s: str) -> str:
    """Sanitize an externally-sourced string for safe embedding in a
    double-quoted YAML scalar.

    Server-supplied og:title / og:description / Content-Disposition values
    can contain characters that break out of the `"..."` quoting and inject
    arbitrary frontmatter keys (e.g. a literal newline followed by
    `tags: [pwn]`). This function:

      1. Strips ASCII control chars (0x00-0x1F + 0x7F) and Unicode line/
         paragraph separators (U+2028, U+2029) that YAML 1.2 treats as
         line breaks inside scalars.
      2. Backslash-escapes `\\` and `"` per YAML 1.2 §7.3.1 double-quoted
         scalar escape rules.

    The result is safe to interpolate inside `"..."` in handwritten YAML.
    """
    s = re.sub(r'[\x00-\x1f\x7f\u2028\u2029]', '', s)
    return s.replace('\\', '\\\\').replace('"', '\\"')


def extract_content(soup: BeautifulSoup) -> str:
    """Extract main article text from common container selectors."""
    # Remove scripts, styles, nav, footer
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
        tag.decompose()

    # Try known content selectors
    for sel in CONTENT_SELECTORS:
        el = soup.select_one(sel)
        if el and len(el.get_text(strip=True)) > 200:
            return el.get_text("\n", strip=True)

    # Fallback: body text
    body = soup.find("body")
    if body:
        return body.get_text("\n", strip=True)
    return soup.get_text("\n", strip=True)


def extract_title(soup: BeautifulSoup) -> str:
    """Extract article title from og:title, h1, or <title>."""
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        return og["content"].strip()
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)
    t = soup.find("title")
    if t:
        return t.get_text(strip=True)
    return ""


# Site-chrome containers whose links are navigation/social boilerplate, not
# editorial outbound references. `extract_links` strips these so the harvested
# links carry the "this source cites that" signal the crawl enrichment follows.
CHROME_TAGS = ["script", "style", "nav", "footer", "header", "aside", "iframe"]


def extract_links(soup: BeautifulSoup, base_url: str) -> list[tuple[str, str]]:
    """Harvest editorial outbound `(url, anchor_text)` pairs from a page.

    Used by the link-following crawl enrichment (`tools/_news/crawl.py`).
    Removes site-chrome containers first (so menu/footer/social links don't
    drown the editorial ones), resolves relative hrefs against `base_url`,
    keeps only http(s), drops same-page anchors and `mailto:`/`javascript:`/
    `tel:` schemes, and deduplicates by resolved URL (first anchor wins).

    MUTATES `soup` (decomposes chrome) — pass a soup you do not need intact.
    Canonical dedup against the source map is the caller's job (`_lib.
    canonicalize_url`); this stays dependency-light so it can run standalone.
    """
    for tag in soup(CHROME_TAGS):
        tag.decompose()
    seen: set[str] = set()
    out: list[tuple[str, str]] = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "mailto:", "javascript:", "tel:")):
            continue
        resolved = urljoin(base_url, href)
        if urlparse(resolved).scheme not in ("http", "https"):
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        out.append((resolved, a.get_text(strip=True)))
    return out


def extract_description(soup: BeautifulSoup) -> str:
    """Extract article description from og:description or meta description."""
    og = soup.find("meta", property="og:description")
    if og and og.get("content"):
        return og["content"].strip()
    md = soup.find("meta", {"name": "description"})
    if md and md.get("content"):
        return md["content"].strip()
    return ""


def _fix_encoding_inplace(r: requests.Response) -> None:
    """Heuristic encoding fixup. Many Korean sites declare ISO-8859-1
    or Latin-1 in the HTTP header while the body is actually UTF-8 or
    cp949. `r.apparent_encoding` (chardet) is more reliable in those
    cases — falls back to utf-8 if chardet returns None.
    """
    if r.encoding and r.encoding.lower() in ("iso-8859-1", "latin-1"):
        r.encoding = r.apparent_encoding or "utf-8"


def _extract_html_response(r) -> tuple[str, str, str, str]:
    """Run the encoding fixup + BeautifulSoup extraction on a response
    (real or curl-synthesized). Returns (final_url, title, desc, content)."""
    _fix_encoding_inplace(r)
    soup = BeautifulSoup(r.text, "html.parser")
    return (
        r.url,
        extract_title(soup),
        extract_description(soup),
        extract_content(soup),
    )


def _fetch_blocked_fallback(url: str, timeout: int) -> tuple[str, str, str, str] | None:
    """Recover an HTML page whose WAF blocked `requests` (HTTP 403 etc.).

    Tier 1 — curl the original URL (curl's TLS fingerprint passes WAFs that
    reject urllib3's). Tier 2 — if curl is also blocked (full JS challenge),
    extract the Internet Archive's snapshot. Returns the extraction tuple, or
    None if neither tier yields ≥100 chars of body. On a Wayback hit the
    ORIGINAL url is reported as final_url so callers that derive `source_url`
    from the return value stay anchored to the real source.
    """
    candidates: list[tuple[str, bool]] = [(url, False)]  # (candidate, is_wayback)
    snap = wayback_snapshot(url, timeout=timeout)
    if snap:
        candidates.append((snap, True))
    for candidate, is_wayback in candidates:
        try:
            r = curl_get(candidate, timeout=timeout, headers=HEADERS)
        except (CurlUnavailable, UnsafeURLError, OSError, ValueError):
            continue
        if r.status_code >= 400:
            continue
        final_url, title, description, content = _extract_html_response(r)
        if content and len(content) >= 100:
            return (url if is_wayback else final_url), title, description, content
    return None


def fetch_html(url: str, timeout: int = 15) -> tuple[str, str, str, str]:
    """Fetch HTML URL and return (final_url, title, description, content).

    Single source of truth for the HTML pipeline shared by `fetch_article.main`
    and `fetch_inbox.fetch_one`. Performs:

      1. SSRF-safe streaming GET
      2. Encoding fixup (mojibake-prone Korean sites)
      3. Title / description / content extraction via BeautifulSoup
      4. Short-content fallback — re-fetches via domain-specific URL
         variants (e.g. chosun.com `?outputType=amp`) when the first
         response yields <100 chars of body. The fallback URL is
         re-validated for SSRF on each hop.
      5. WAF-block fallback — on a blocked HTTP status (403 etc.) retries
         via curl (different TLS fingerprint), then the Wayback snapshot.

    Raises `requests.exceptions.HTTPError` on HTTP error (unless a block
    fallback succeeds), `UnsafeURLError` on SSRF block. Caller decides what
    to do when content is still empty (the function returns best-effort).
    """
    try:
        with safe_get_stream(url, headers=HEADERS, timeout=timeout) as r:
            r.raise_for_status()
            final_url, title, description, content = _extract_html_response(r)
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else None
        if status in BLOCKED_STATUSES:
            fb = _fetch_blocked_fallback(url, timeout)
            if fb is not None:
                return fb
        raise

    if (not content) or len(content) < 100:
        for alt_url in get_fallback_urls(final_url):
            try:
                with safe_get(alt_url, headers=HEADERS, timeout=timeout) as r2:
                    r2.raise_for_status()
                    _fix_encoding_inplace(r2)
                    soup2 = BeautifulSoup(r2.text, "html.parser")
                    content2 = extract_content(soup2)
                    if content2 and len(content2) >= 100:
                        title = extract_title(soup2) or title
                        description = extract_description(soup2) or description
                        content = content2
                        final_url = alt_url
                        break
            except (requests.exceptions.RequestException, UnsafeURLError):
                continue
    if (not content) or len(content) < 100:
        # A JS-rendered page comes back as 200 + thin body, so it never takes
        # the BLOCKED_STATUSES path — try the curl/Wayback tier once as a last resort.
        fb = _fetch_blocked_fallback(final_url, timeout)
        if fb is not None:
            return fb
    return final_url, title, description, content


def is_pdf_url(url: str, content_type: str = "") -> bool:
    """Classify URL as PDF by path extension or response Content-Type."""
    if "application/pdf" in content_type.lower():
        return True
    path = urlparse(url).path.lower()
    return path.endswith(".pdf")


PDF_MAX_BYTES = 100 * 1024 * 1024  # 100 MB hard cap on a single PDF download.


def _stream_pdf_body(r: requests.Response) -> bytes:
    """Drain a streaming response body up to `PDF_MAX_BYTES`.

    Iterates `iter_content` chunks instead of `r.content` so memory stays
    bounded and the download aborts as soon as the cap is exceeded — the
    prior `r.content` access defeated `stream=True` and could OOM on a
    multi-hundred-MB PDF or a malicious infinite-stream URL.
    """
    chunks: list[bytes] = []
    received = 0
    for chunk in r.iter_content(chunk_size=64 * 1024):
        if not chunk:
            continue
        received += len(chunk)
        if received > PDF_MAX_BYTES:
            r.close()
            raise ValueError(
                f"PDF exceeds {PDF_MAX_BYTES // (1024 * 1024)} MB cap "
                f"(received {received:,} bytes from {r.url})"
            )
        chunks.append(chunk)
    return b"".join(chunks)


def _pdf_title_from_response(r: requests.Response) -> str:
    """Pick a filename for a PDF response: Content-Disposition first,
    then the last URL path segment, else `document`."""
    cd = r.headers.get("Content-Disposition", "")
    m = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)"?', cd, re.IGNORECASE)
    if m:
        return unquote(m.group(1)).rsplit(".pdf", 1)[0]
    last = urlparse(r.url).path.rsplit("/", 1)[-1]
    return last.rsplit(".pdf", 1)[0] or "document"


def fetch_pdf(url: str, timeout: int = 30) -> tuple[bytes, str]:
    """Download a PDF as bytes. Returns (body, suggested_title)."""
    with safe_get_stream(url, headers=HEADERS, timeout=timeout) as r:
        r.raise_for_status()
        body = _stream_pdf_body(r)
        title = _pdf_title_from_response(r)
    return body, title


def sniff_and_save_pdf(
    url: str,
    timeout: int = 15,
    dedup_check: Callable[[str], str | None] | None = None,
) -> tuple | None:
    """PDF-via-redirect detection — streaming GET to sniff the final Content-Type.

    Some sites issue HTTP redirects from an apparently-HTML URL to a PDF binary;
    those are routed into the PDF saver here. Single definition shared by
    `main()` and `fetch_inbox.fetch_one` (the sniff + WAF fall-through used to
    be copy-pasted between them). `with` releases the connection (and chained
    session) on every exit path — PDF return, exception, or HTML fall-through —
    and closes before the caller's fetch_html re-fetches.

    `dedup_check` (optional) receives the redirect-resolved final URL *before*
    the body downloads and returns an existing source slug or None.

    Returns:
      None                       — not a PDF, or a WAF block prevented sniffing
                                   (caller proceeds to fetch_html, which retries
                                   blocked statuses via curl / Wayback)
      ("duplicate", slug)        — dedup_check matched; nothing downloaded
      ("saved", pdf_path, title, n_bytes, final_url)

    Non-blocked HTTPError propagates.
    """
    try:
        with safe_get_stream(url, headers=HEADERS, timeout=timeout) as r:
            r.raise_for_status()
            ctype = r.headers.get("Content-Type", "")
            if is_pdf_url(r.url, ctype):
                if dedup_check is not None:
                    dup = dedup_check(r.url)
                    if dup:
                        return ("duplicate", dup)
                body = _stream_pdf_body(r)
                title = _pdf_title_from_response(r)
                pdf_path = save_pdf(r.url, body, title)
                return ("saved", pdf_path, title, len(body), r.url)
    except requests.exceptions.HTTPError as e:
        # A WAF block on the PDF-sniff GET means we cannot sniff — fall
        # through to fetch_html, which retries via curl / Wayback.
        status = e.response.status_code if e.response is not None else None
        if status not in BLOCKED_STATUSES:
            raise
    return None


def save_pdf(url: str, body: bytes, title: str,
             output_dir: Path = _REPO_ROOT / "raw" / "PDF") -> Path:
    """Save the PDF binary only, under raw/PDF/<slug>.pdf.

    No stub markdown is created. The next /wiki-ingest pass discovers new
    PDFs by scanning raw/PDF/ for *.pdf files absent from _source_map.json
    (by_path), reads the binary with Claude's Read tool, and writes
    wiki/sources/<slug>.md with `source_file: raw/PDF/<slug>.pdf` plus
    `source_url: <url>` in its frontmatter — the wiki source page holds
    all URL metadata going forward.

    The download URL is returned via stdout in main() so the operator can
    paste it into the wiki source page's frontmatter during ingest.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = _resolve_unique_path(title, url, output_dir, "pdf", "document")
    atomic_write_bytes(pdf_path, body)
    return pdf_path


def save_markdown(url: str, title: str, description: str, content: str,
                  output_dir: Path = _REPO_ROOT / "raw" / "NewsScrap",
                  ingest_meta: dict | None = None) -> Path:
    """Save fetched article as markdown with Obsidian Web Clipper compatible frontmatter.

    `ingest_meta` carries channel-of-entry metadata from `_inbox.md` (source,
    gap, hub, cluster, query, priority, ts). When present, two extra
    frontmatter keys are emitted: `ingest_source` (the channel — mobile /
    interactive / auto-gap / cron-news / hook-adapt) and `ingest_meta` (the
    remaining key=value pairs joined into a single inline mapping). This lets
    downstream wiki ingest trace why a source was acquired without parsing
    `_archive.md` retrospectively.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    fpath = _resolve_unique_path(title, url, output_dir, "md", "article")

    today = date.today().isoformat()
    extra = ""
    if ingest_meta:
        ingest_source = ingest_meta.get("source", "mobile")
        extra = f'ingest_source: "{_yaml_safe_string(ingest_source)}"\n'
        rest = {k: v for k, v in ingest_meta.items() if k != "source"}
        if rest:
            parts = [f'{k}: "{_yaml_safe_string(str(v))}"' for k, v in rest.items()]
            extra += "ingest_meta: { " + ", ".join(parts) + " }\n"
    frontmatter = f"""---
title: "{_yaml_safe_string(title)}"
source: "{_yaml_safe_string(url)}"
author:
published:
created: {today}
description: "{_yaml_safe_string(description)}"
{extra}tags:
  - clippings
---

{content}
"""
    atomic_write_text(fpath, frontmatter)
    return fpath


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/_ingest/fetch_article.py <url> [output_filename]")
        sys.exit(1)

    url = unwrap_share_wrapper(sys.argv[1])
    print(f"Fetching: {url}")

    def _report_pdf(pdf_path: Path, body_len: int, title: str, final_url: str):
        print(f"Title: {title}")
        print(f"PDF:   {pdf_path}  ({body_len:,} bytes)")
        print(f"URL:   {final_url}")
        print()
        print("Next: run /wiki-ingest raw/PDF  (folder mode auto-detects the new PDF).")
        print("      Paste the URL above into the resulting wiki/sources/<slug>.md")
        print("      frontmatter as `source_url: \"...\"` so re-download dedup works.")

    # Cheap upfront check: path ends in .pdf? Still HEAD/GET to confirm.
    if is_pdf_url(url):
        try:
            body, title = fetch_pdf(url)
        except UnsafeURLError as e:
            print(f"BLOCKED: {e}")
            sys.exit(2)
        except requests.exceptions.RequestException as e:
            print(f"PDF fetch failed: {e}")
            sys.exit(2)
        except ValueError as e:  # PDF_MAX_BYTES cap (UnsafeURLError already caught above)
            print(f"PDF fetch failed: {e}")
            sys.exit(2)
        pdf_path = save_pdf(url, body, title)
        _report_pdf(pdf_path, len(body), title, url)
        return

    try:
        sniffed = sniff_and_save_pdf(url, timeout=15)
        if sniffed is not None:
            _tag, pdf_path, title, n_bytes, final_url = sniffed
            print("(detected PDF via Content-Type after redirect)")
            _report_pdf(pdf_path, n_bytes, title, final_url)
            return

        final_url, title, description, content = fetch_html(url, timeout=15)
        if final_url != url:
            print(f"(fallback variant used: {final_url})")
    except UnsafeURLError as e:
        print(f"BLOCKED: {e}")
        sys.exit(2)
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
        sys.exit(2)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(2)
    except ValueError as e:  # PDF_MAX_BYTES cap in sniff_and_save_pdf
        print(f"PDF fetch failed: {e}")
        sys.exit(2)

    if not content or len(content) < 100:
        print(f"WARNING: Very short content ({len(content)} chars) — site may require JavaScript or have strong bot detection.")

    print(f"Title: {title}")
    print(f"Content: {len(content):,} chars")

    fpath = save_markdown(url, title, description, content)
    print(f"Saved: {fpath}")


if __name__ == "__main__":
    main()
