"""`tools/_ingest/fetch_inbox.py` redirect-dedup unit tests — no network or disk.

Inbox-time dedup only looks at the original URL. fetch_one re-checks the *final*
URL resolved after redirects (r.url for PDF-via-redirect, _final_url for HTML)
against dedup_index, so a different short URL pointing at the same target is not
saved twice. Network functions are monkeypatched — the PDF sniff lives in
fetch_article.sniff_and_save_pdf (shared with fetch_article.main), so its
network/save calls are patched in the fetch_article namespace."""
import sys
from pathlib import Path

# conftest puts tools/ on sys.path, but fetch_inbox lives under _ingest/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from _ingest import fetch_article as A  # noqa: E402
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
    monkeypatch.setattr(A, "is_pdf_url", lambda *a, **k: False)
    monkeypatch.setattr(A, "safe_get_stream", lambda *a, **k: _FakeStream("https://x.com/a"))
    monkeypatch.setattr(
        F, "fetch_html",
        lambda url, timeout=15: ("https://final.com/article?utm_source=x", "T", "D", "x" * 200),
    )
    monkeypatch.setattr(F, "save_markdown", lambda *a, **k: _fail_on_save())
    idx = {F.canonicalize_url("https://final.com/article"): "existing-slug"}
    status, path, _ = F.fetch_one("https://short.link/xyz", dedup_index=idx)
    assert status == "SKIPPED:duplicate-of-existing-slug"
    assert path is None


def test_pdf_redirect_dedup_skips(monkeypatch):
    monkeypatch.setattr(F, "unwrap_share_wrapper", lambda u: u)
    # direct-url is_pdf_url(url) → False; redirect is_pdf_url(r.url, ctype) → True.
    monkeypatch.setattr(F, "is_pdf_url", lambda u, ctype="": ctype == "application/pdf")
    monkeypatch.setattr(A, "is_pdf_url", lambda u, ctype="": ctype == "application/pdf")
    monkeypatch.setattr(
        A, "safe_get_stream",
        lambda *a, **k: _FakeStream("https://cdn.com/file.pdf", "application/pdf"),
    )
    monkeypatch.setattr(A, "save_pdf", lambda *a, **k: _fail_on_save())
    idx = {F.canonicalize_url("https://cdn.com/file.pdf"): "existing-pdf"}
    status, path, _ = F.fetch_one("https://short.link/pdf", dedup_index=idx)
    assert status == "SKIPPED:duplicate-of-existing-pdf"
    assert path is None


def test_html_no_false_skip_when_final_url_novel(monkeypatch):
    saved = Path("raw/NewsScrap/new.md")
    monkeypatch.setattr(F, "unwrap_share_wrapper", lambda u: u)
    monkeypatch.setattr(F, "is_pdf_url", lambda *a, **k: False)
    monkeypatch.setattr(A, "is_pdf_url", lambda *a, **k: False)
    monkeypatch.setattr(A, "safe_get_stream", lambda *a, **k: _FakeStream("https://x.com/a"))
    monkeypatch.setattr(
        F, "fetch_html",
        lambda url, timeout=15: ("https://final.com/novel", "T", "D", "x" * 200),
    )
    monkeypatch.setattr(F, "save_markdown", lambda *a, **k: saved)
    idx = {F.canonicalize_url("https://final.com/other"): "existing-slug"}
    status, path, _ = F.fetch_one("https://short.link/xyz", dedup_index=idx)
    assert status == "OK"
    assert path == saved


def test_html_saves_under_redirect_resolved_url(monkeypatch):
    """The save URL must be the same one dedup judged on — otherwise the stored
    key never matches and the article re-enters through its original URL."""
    seen = {}
    monkeypatch.setattr(F, "unwrap_share_wrapper", lambda u: u)
    monkeypatch.setattr(F, "is_pdf_url", lambda *a, **k: False)
    monkeypatch.setattr(A, "is_pdf_url", lambda *a, **k: False)
    monkeypatch.setattr(A, "safe_get_stream", lambda *a, **k: _FakeStream("https://x.com/a"))
    monkeypatch.setattr(
        F, "fetch_html",
        lambda url, timeout=15: ("https://final.com/article", "T", "D", "x" * 200),
    )
    monkeypatch.setattr(
        F, "save_markdown",
        lambda url, *a, **k: seen.setdefault("url", url) and None or Path("raw/x.md"),
    )
    status, _, _ = F.fetch_one("https://short.link/xyz", dedup_index={})
    assert status == "OK"
    assert seen["url"] == "https://final.com/article"


def _fail_on_save():
    raise AssertionError("save_* must not be called when the final URL is a duplicate")


def test_batch_registers_resolved_url_for_distinct_shortlinks(monkeypatch, tmp_path):
    """Two different shortlinks that resolve to one article in the same batch save once.

    Registering only the original inbox URL lets fetch_one's final-URL check miss,
    and the article is saved twice (`_2`).
    """
    inbox = tmp_path / "_inbox.md"
    inbox.write_text("https://short.link/a\nhttps://short.link/b\n", encoding="utf-8")
    monkeypatch.setattr(F, "INBOX", inbox)
    monkeypatch.setattr(F, "write_inbox", lambda *a, **k: None)
    monkeypatch.setattr(F, "append_archive", lambda *a, **k: None)
    monkeypatch.setattr(F, "load_source_map", lambda: {"by_url": {}})
    monkeypatch.setattr(F, "unwrap_share_wrapper", lambda u: u)
    monkeypatch.setattr(F, "is_pdf_url", lambda *a, **k: False)
    monkeypatch.setattr(A, "is_pdf_url", lambda *a, **k: False)
    monkeypatch.setattr(A, "safe_get_stream", lambda *a, **k: _FakeStream("https://final.com/article"))
    monkeypatch.setattr(
        F, "fetch_html",
        lambda url, timeout=15: ("https://final.com/article", "T", "D", "x" * 200),
    )
    saves = []
    monkeypatch.setattr(
        F, "save_markdown",
        lambda *a, **k: saves.append(a) or F.REPO_ROOT / "raw" / "a.md",
    )
    F.main()
    assert len(saves) == 1, saves


class _BodyStream(_FakeStream):
    def __init__(self, url, body):
        super().__init__(url, "application/pdf")
        self._body = body

    def iter_content(self, chunk_size=1):
        yield self._body

    def close(self):
        pass


def test_pdf_path_rejects_non_pdf_body(monkeypatch):
    """A `.pdf` URL that serves a 200 HTML page is not saved; it fails and stays in the inbox."""
    monkeypatch.setattr(F, "unwrap_share_wrapper", lambda u: u)
    monkeypatch.setattr(F, "is_pdf_url", lambda u, ctype="": ctype == "application/pdf")
    monkeypatch.setattr(A, "is_pdf_url", lambda u, ctype="": ctype == "application/pdf")
    monkeypatch.setattr(
        A, "safe_get_stream",
        lambda *a, **k: _BodyStream("https://cdn.com/f.pdf", b"<html>login</html>"),
    )
    monkeypatch.setattr(A, "save_pdf", lambda *a, **k: _fail_on_save())
    status, path, _ = F.fetch_one("https://short.link/pdf", dedup_index={})
    assert status.startswith("FAILED:ValueError") and path is None
    assert A._stream_pdf_body(_BodyStream("u", b"\n%PDF-1.7 ...")) == b"\n%PDF-1.7 ..."
