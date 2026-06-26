"""Process URL queue from raw/_inbox.md, fetch each via fetch_article.py, archive results.

Usage:
    python tools/_ingest/fetch_inbox.py

Reads raw/_inbox.md (one URL per line, optionally followed by `  # key=value ...`
metadata), checks each against `_source_map.json::by_url` for dedup, fetches the
rest via fetch_article.py logic (HTML → raw/NewsScrap/<slug>.md or PDF →
raw/PDF/<slug>.pdf), and rewrites the inbox keeping only URLs that failed
transiently so the next run retries them. Successful and deduplicated URLs are
dropped from the inbox; every outcome (OK / SKIPPED / FAILED) is appended to
raw/_archive.md.

Inbox line format (single-queue model — see .claude/operations/gap-detection-rollout.md):

    https://example.com/article-A
    https://example.com/article-B  # source=auto-gap gap=single-source hub=AICC ts=2026-05-15T02:00Z

Two spaces + `#` separates the URL from inline metadata so URL fragments (`#anchor`,
no preceding space) remain part of the URL. Lines without metadata default to
`source=mobile`. The metadata is forwarded into the saved raw file's frontmatter
via `fetch_article.save_markdown(..., ingest_meta=...)`.

Never commits or pushes — the operator inspects the working tree and commits manually.
This honors the "commit/push requires the wiki operator's approval" project rule.

Channels of entry that populate this queue:
  - Mobile share-sheet (HTTP Shortcuts → GitHub Contents API, no metadata)
  - Interactive /wiki-news (source=interactive)
  - /wiki-news --gap --batch (source=auto-gap, gap=sparse-cluster|single-source|stale-hub)
  - Background cron / /schedule (source=cron-news or hook-adapt)

See .claude/operations/mobile-inbox-setup.md for the one-time mobile setup.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

# On a Windows cp949 console, printing Korean / en-dash etc. raises
# UnicodeEncodeError, so reconfigure stdout/stderr to UTF-8. This is a Python
# 3.7+ feature, safe on the standard interpreter.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass

import requests

sys.path.insert(0, str(Path(__file__).parent.parent))  # _ingest/ → tools/ root (shared modules)
from _lib import atomic_write_text, canonicalize_url  # noqa: E402
from _net import safe_get_stream, BLOCKED_STATUSES, UnsafeURLError  # noqa: E402
from _ingest.fetch_article import (  # noqa: E402
    HEADERS,
    fetch_html,
    fetch_pdf,
    is_pdf_url,
    save_markdown,
    save_pdf,
    unwrap_share_wrapper,
    _pdf_title_from_response,
    _stream_pdf_body,
)


REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # tools/_ingest/ → repo root
INBOX = REPO_ROOT / "raw" / "_inbox.md"
ARCHIVE = REPO_ROOT / "raw" / "_archive.md"
SOURCE_MAP = REPO_ROOT / "wiki" / "sources" / "_source_map.json"

INBOX_HEADER = """# Inbox

Multi-channel URL queue. One line = one URL, optionally with `  # key=value ...` metadata attached.
Entry channels: mobile share-sheet · `/wiki-news` interactive · `/wiki-news --gap --batch` · background cron.

Emptied by running `python tools/_ingest/fetch_inbox.py` or `/wiki-ingest inbox`
(failed URLs are retained so the next run retries them).

Line format:
  https://example.com/article-A
  https://example.com/article-B  # source=auto-gap gap=single-source hub=AICC ts=2026-05-15T02:00Z

The separator between the URL and the metadata is **two spaces + `#`**. A URL fragment (`#anchor`) attaches with no space, so it stays safe.
A URL without metadata defaults to `source=mobile`.

Guides: [.claude/operations/mobile-inbox-setup.md](../.claude/operations/mobile-inbox-setup.md)
       [.claude/operations/gap-detection-rollout.md](../.claude/operations/gap-detection-rollout.md)

<!-- URLs below this line. Blank lines and lines starting with # are ignored. -->
"""

ARCHIVE_HEADER = """# Archive

Accumulated results of `python tools/_ingest/fetch_inbox.py` runs. Grouped by date, with the most recent date at the end of the file.

Each line format: `- HH:MM [<source>] <URL> → <result>`
- `[<source>]` — entry channel (`mobile`/`interactive`/`auto-gap`/`cron-news`/`hook-adapt`). An entry without metadata is `[mobile]`.
- `<path> OK` — fetch succeeded
- `SKIPPED (duplicate of <slug>)` — URL already ingested
- `FAILED:<reason>` — failed (URL retained in the inbox, retried on the next run)
"""


def load_source_map() -> dict:
    if not SOURCE_MAP.exists():
        return {"by_url": {}, "by_path": {}}
    return json.loads(SOURCE_MAP.read_text(encoding="utf-8"))


# Inline metadata format: URL, then two spaces + `#`, then `key=value` pairs.
# The two-space prefix prevents URL fragments (`https://x/y#anchor`) from being
# mis-parsed as metadata. Quoted values (`query="..."`) preserve embedded spaces.
_INLINE_META_RE = re.compile(r"^(\S+)  #\s*(.*)$")
_META_KV_RE = re.compile(r'(\w+)=(?:"([^"]*)"|(\S+))')


def parse_meta(meta_str: str) -> dict:
    """Parse `key=value key="value with spaces"` into a dict.

    Unknown keys are kept verbatim — the downstream consumer (fetch_article
    save_markdown) decides which keys to emit. Returns {} on empty / unparseable
    input so the caller can treat metadata as additive."""
    out: dict = {}
    for m in _META_KV_RE.finditer(meta_str):
        key = m.group(1)
        val = m.group(2) if m.group(2) is not None else m.group(3)
        out[key] = val
    return out


# Header sentinel — parse_inbox only scans lines AFTER this marker so that
# the header itself may quote example URLs (e.g. `https://example.com/...`)
# without those examples being parsed as queue entries.
_INBOX_SENTINEL = "<!-- URLs below this line."


def parse_inbox(text: str) -> list[tuple[str, dict]]:
    """Return `[(url, meta_dict), ...]` in inbox order.

    Only lines AFTER the `<!-- URLs below this line. ... -->` sentinel are
    considered. Within that region, skips blank lines and `#` / `<!--`
    comments. Lines starting with http(s):// are URL entries; inline
    `  # ...` after the URL parses into the meta dict. URLs without inline
    meta get `{}` (the caller can default `source=mobile` downstream).

    If the sentinel is missing (legacy inbox file), the entire text is
    scanned — keeps the helper usable from unit tests and older repos."""
    body = text
    idx = text.find(_INBOX_SENTINEL)
    if idx != -1:
        # Skip past the sentinel line itself.
        eol = text.find("\n", idx)
        body = text[eol + 1 :] if eol != -1 else ""

    entries: list[tuple[str, dict]] = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#") or line.startswith("<!--"):
            continue
        if not line.startswith(("http://", "https://")):
            continue
        m = _INLINE_META_RE.match(line)
        if m:
            url, meta_str = m.group(1), m.group(2)
            entries.append((url, parse_meta(meta_str)))
        else:
            entries.append((line, {}))
    return entries


def format_entry(url: str, meta: dict) -> str:
    """Render `(url, meta)` back to a single inbox line (inverse of parse_inbox)."""
    if not meta:
        return url
    parts = []
    for k, v in meta.items():
        sv = str(v)
        if " " in sv or "\t" in sv:
            parts.append(f'{k}="{sv}"')
        else:
            parts.append(f"{k}={sv}")
    return f"{url}  # " + " ".join(parts)


def write_inbox(retain: list[tuple[str, dict]]) -> None:
    body = INBOX_HEADER
    if retain:
        body += "\n" + "\n".join(format_entry(u, m) for u, m in retain) + "\n"
    atomic_write_text(INBOX, body)


# Date-prefixed H2 section header (e.g. `## 2026-05-07`). Line-anchored
# so we never mistake a body-quoted occurrence (URL, article title) for
# a real section delimiter.
_DATE_SECTION_RE = re.compile(r"^## \d{4}-\d{2}-\d{2}\s*$", re.MULTILINE)


def append_archive(entries: list[tuple[str, str, str, str]]) -> None:
    """entries: `[(ts, source, url, result), ...]`.

    `source` is the inbox-metadata channel (e.g. `mobile`, `auto-gap`,
    `interactive`); when no metadata accompanied the URL we synthesize
    `mobile` so the archive always carries a channel tag."""
    if not entries:
        return
    today = date.today().isoformat()
    section_marker = f"## {today}"
    new_lines = "\n".join(
        f"- {ts} [{source}] {url} → {result}" for ts, source, url, result in entries
    )

    existing = ARCHIVE.read_text(encoding="utf-8") if ARCHIVE.exists() else ARCHIVE_HEADER

    today_pat = re.compile(rf"^{re.escape(section_marker)}\s*$", re.MULTILINE)
    today_match = today_pat.search(existing)
    if today_match:
        rest_start = today_match.end()
        next_section = _DATE_SECTION_RE.search(existing, rest_start)
        if next_section:
            insert_pos = next_section.start()
            head = existing[:insert_pos].rstrip()
            tail = existing[insert_pos:].lstrip("\n")
            existing = head + "\n" + new_lines + "\n\n" + tail
        else:
            existing = existing.rstrip() + "\n" + new_lines + "\n"
    else:
        existing = existing.rstrip() + "\n\n" + section_marker + "\n" + new_lines + "\n"

    atomic_write_text(ARCHIVE, existing)


def fetch_one(
    url: str, meta: dict | None = None, dedup_index: dict | None = None
) -> tuple[str, Path | None]:
    """Fetch URL and save under raw/. Returns (status, output_path).

    `dedup_index` maps canonical-URL → existing source slug. The inbox-time
    dedup in main() only sees the original URL; this re-checks the *redirect-
    resolved* final URL (PDF-via-redirect's `r.url`, HTML's `_final_url`) before
    saving, so two different shortlinks to one target don't both persist. On a
    hit returns ("SKIPPED:duplicate-of-<slug>", None) — main() drops it like an
    inbox-time skip. PDFs especially need this: they carry no frontmatter URL,
    so the next /wiki-ingest pass can't dedup them by URL.

    status ∈ {"OK", "FAILED:<reason>"}.

    `meta` (from `parse_inbox`) is forwarded into the saved markdown's
    frontmatter via `save_markdown(ingest_meta=...)`. PDF saves don't carry
    inline metadata — the PDF binary has no frontmatter, and the wiki source
    page (created by /wiki-ingest) is the canonical home for URL metadata."""
    # Unwrap share-sheet interstitials (e.g. LinkedIn /safety/go) up front so
    # both the PDF-sniff and HTML paths fetch — and persist — the real URL.
    url = unwrap_share_wrapper(url)
    dedup_index = dedup_index or {}
    try:
        if is_pdf_url(url):
            body, title = fetch_pdf(url)
            path = save_pdf(url, body, title)
            return "OK", path

        # Streaming GET first to sniff for PDF-via-redirect (Content-Type).
        # `with` releases the connection (and its session, chained onto
        # close in _net) on every exit path — the PDF return, an exception,
        # or the HTML fall-through — instead of leaking it on all but the
        # HTML path. The block also closes before fetch_html re-fetches.
        try:
            with safe_get_stream(url, headers=HEADERS, timeout=15) as r:
                r.raise_for_status()
                ctype = r.headers.get("Content-Type", "")
                if is_pdf_url(r.url, ctype):
                    dup = dedup_index.get(canonicalize_url(r.url))
                    if dup:
                        return f"SKIPPED:duplicate-of-{dup}", None
                    body = _stream_pdf_body(r)
                    title = _pdf_title_from_response(r)
                    path = save_pdf(r.url, body, title)
                    return "OK", path
        except requests.exceptions.HTTPError as e:
            # A WAF block on the PDF-sniff GET means we cannot sniff — fall
            # through to fetch_html, which retries via curl / Wayback before
            # giving up. Non-block HTTP errors stay fatal (handled below).
            status = e.response.status_code if e.response is not None else None
            if status not in BLOCKED_STATUSES:
                raise

        _final_url, title, description, content = fetch_html(url, timeout=15)
        dup = dedup_index.get(canonicalize_url(_final_url))
        if dup:
            return f"SKIPPED:duplicate-of-{dup}", None
        if (not content) or len(content) < 100:
            return f"FAILED:short-content({len(content)}chars)", None
        path = save_markdown(url, title, description, content, ingest_meta=meta)
        return "OK", path
    except UnsafeURLError as e:
        return f"FAILED:BLOCKED({e})", None
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code if e.response is not None else "?"
        return f"FAILED:HTTP-{code}", None
    except requests.exceptions.RequestException as e:
        return f"FAILED:{type(e).__name__}", None
    except OSError as e:
        # Disk-side failure (full / permission / quota). Distinguish from
        # network errors so retry behavior at the caller can differ — and
        # surface the underlying message so the operator can diagnose
        # without re-running with stack traces.
        import traceback
        traceback.print_exc(file=sys.stderr)
        return f"FAILED:save-OSError({e.errno}:{e.strerror or e})", None
    except Exception as e:  # noqa: BLE001 — surface unexpected errors as FAILED
        import traceback
        traceback.print_exc(file=sys.stderr)
        return f"FAILED:{type(e).__name__}({e})", None


def main() -> int:
    if not INBOX.exists():
        print(f"No inbox at {INBOX} — creating empty file.")
        write_inbox([])
        return 0

    entries = parse_inbox(INBOX.read_text(encoding="utf-8"))
    if not entries:
        print("Inbox empty.")
        return 0

    smap = load_source_map()
    by_url: dict = smap.get("by_url", {})
    # Catch re-scrape variants that differ only by tracking params (mobile
    # share-sheet appends utm_*/fbclid). Exact match wins; canonical is fallback.
    by_url_canon: dict = {canonicalize_url(k): v for k, v in by_url.items()}

    archive_entries: list[tuple[str, str, str, str]] = []
    retain: list[tuple[str, dict]] = []
    ok_count = 0

    for url, meta in entries:
        ts = datetime.now().strftime("%H:%M")
        source = meta.get("source", "mobile")

        slug = by_url.get(url) or by_url_canon.get(canonicalize_url(url))
        if slug:
            archive_entries.append((ts, source, url, f"SKIPPED (duplicate of {slug})"))
            print(f"[SKIP] [{source}] {url} -> {slug}")
            continue

        print(f"[FETCH] [{source}] {url}")
        status, path = fetch_one(url, meta=meta, dedup_index=by_url_canon)
        if status == "OK" and path is not None:
            # save_markdown / save_pdf return _REPO_ROOT-anchored absolute paths;
            # render relative to REPO_ROOT for a clean archive/log entry.
            rel = path.relative_to(REPO_ROOT).as_posix()
            archive_entries.append((ts, source, url, f"{rel} OK"))
            print(f"  -> {rel}")
            ok_count += 1
        elif status.startswith("SKIPPED:"):
            # Redirect-resolved final URL matched an existing source — drop it
            # (don't retain), like the inbox-time dedup at the top of the loop.
            dup = status.split("duplicate-of-", 1)[-1]
            archive_entries.append((ts, source, url, f"SKIPPED (redirect duplicate of {dup})"))
            print(f"  -> SKIPPED (redirect duplicate of {dup})")
        else:
            archive_entries.append((ts, source, url, status))
            retain.append((url, meta))
            print(f"  -> {status} (kept in inbox for retry)")

    write_inbox(retain)
    append_archive(archive_entries)

    print()
    print(f"Processed {len(entries)} URLs · OK={ok_count} · retained={len(retain)}")
    print(f"Archive: {ARCHIVE.relative_to(REPO_ROOT).as_posix()}")
    if ok_count:
        print()
        print("Next: /wiki-ingest raw/NewsScrap (or raw/PDF if PDFs were fetched).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
