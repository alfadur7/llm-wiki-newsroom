"""`tools/_ingest/fetch_inbox.py` redirect-dedup unit tests — no network or disk.

Inbox-time dedup only looks at the original URL. fetch_one re-checks the *final*
URL resolved after redirects (r.url for PDF-via-redirect, _final_url for HTML)
against dedup_index, so a different short URL pointing at the same target is not
saved twice. Network functions are monkeypatched."""
import sys
from pathlib import Path

# conftest puts tools/ on sys.path, but fetch_inbox lives under _ingest/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from _ingest import fetch_inbox as F  # noqa: E402


class _FakeStream:
    """safe_get_stream(...) context manager + response stub."""

    def __init__(self, url, ctype=""):
        self.url = url
        self.headers = {"Content-Type": ctype}

    def raise_for_status(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_html_final_url_dedup_skips(monkeypatch):
    monkeypatch.setattr(F, "unwrap_share_wrapper", lambda u: u)
    monkeypatch.setattr(F, "is_pdf_url", lambda *a, **k: False)
    monkeypatch.setattr(F, "safe_get_stream", lambda *a, **k: _FakeStream("https://x.com/a"))
    monkeypatch.setattr(
        F, "fetch_html",
        lambda url, timeout=15: ("https://final.com/article?utm_source=x", "T", "D", "x" * 200),
    )
    monkeypatch.setattr(F, "save_markdown", lambda *a, **k: _fail_on_save())
    idx = {F.canonicalize_url("https://final.com/article"): "existing-slug"}
    status, path = F.fetch_one("https://short.link/xyz", dedup_index=idx)
    assert status == "SKIPPED:duplicate-of-existing-slug"
    assert path is None


def test_pdf_redirect_dedup_skips(monkeypatch):
    monkeypatch.setattr(F, "unwrap_share_wrapper", lambda u: u)
    # direct-url is_pdf_url(url) → False; redirect is_pdf_url(r.url, ctype) → True.
    monkeypatch.setattr(F, "is_pdf_url", lambda u, ctype="": ctype == "application/pdf")
    monkeypatch.setattr(
        F, "safe_get_stream",
        lambda *a, **k: _FakeStream("https://cdn.com/file.pdf", "application/pdf"),
    )
    monkeypatch.setattr(F, "save_pdf", lambda *a, **k: _fail_on_save())
    idx = {F.canonicalize_url("https://cdn.com/file.pdf"): "existing-pdf"}
    status, path = F.fetch_one("https://short.link/pdf", dedup_index=idx)
    assert status == "SKIPPED:duplicate-of-existing-pdf"
    assert path is None


def test_html_no_false_skip_when_final_url_novel(monkeypatch):
    saved = Path("raw/NewsScrap/new.md")
    monkeypatch.setattr(F, "unwrap_share_wrapper", lambda u: u)
    monkeypatch.setattr(F, "is_pdf_url", lambda *a, **k: False)
    monkeypatch.setattr(F, "safe_get_stream", lambda *a, **k: _FakeStream("https://x.com/a"))
    monkeypatch.setattr(
        F, "fetch_html",
        lambda url, timeout=15: ("https://final.com/novel", "T", "D", "x" * 200),
    )
    monkeypatch.setattr(F, "save_markdown", lambda *a, **k: saved)
    idx = {F.canonicalize_url("https://final.com/other"): "existing-slug"}
    status, path = F.fetch_one("https://short.link/xyz", dedup_index=idx)
    assert status == "OK"
    assert path == saved


def _fail_on_save():
    raise AssertionError("save_* must not be called when the final URL is a duplicate")
