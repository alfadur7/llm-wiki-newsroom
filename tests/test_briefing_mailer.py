"""Regression tests for sanitizing invisible characters in briefing mail recipients/credentials.

2026-06 send failure: the BRIEFING_RECIPIENTS secret carried a UTF-8 BOM (\\ufeff),
causing UnicodeEncodeError('ascii' ... '\\ufeff') at the SMTP RCPT step. str.strip()
does not remove the BOM, so explicit sanitization is required.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from _briefing import mailer  # noqa: E402


def test_clean_addr_strips_bom_and_whitespace():
    assert mailer.clean_addr("﻿me@x.com  ") == "me@x.com"


def test_clean_addr_strips_zero_width_chars():
    # Remove ZWSP, ZWNJ, ZWJ, and word-joiner
    dirty = "a​b‌c‍d⁠@x.com"
    assert mailer.clean_addr(dirty) == "abcd@x.com"


def test_clean_addr_keeps_ascii_intact():
    assert mailer.clean_addr("plain@example.com") == "plain@example.com"


def test_recipients_from_env_drops_bom(monkeypatch):
    # Even with a BOM-laden secret and empty items mixed in, only clean ascii addresses remain.
    monkeypatch.setenv("BRIEFING_RECIPIENTS", "﻿one@x.com, ,two@x.com​")
    recips = mailer.recipients_from_env()
    assert recips == ["one@x.com", "two@x.com"]
    # The sanitized result must be ascii-encodable for SMTP RCPT to pass.
    for r in recips:
        r.encode("ascii")


def test_send_bcc_hides_recipients(monkeypatch):
    # Recipients are delivered only via the envelope and never exposed in To/Cc/Bcc headers.
    monkeypatch.setenv("GMAIL_USER", "sender@x.com")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "app-password")
    captured = {}

    class FakeSMTP:
        def __init__(self, host, port):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def starttls(self, context=None):
            pass

        def login(self, user, password):
            pass

        def sendmail(self, from_addr, to_addrs, body):
            captured["envelope"] = list(to_addrs)
            captured["body"] = body

    monkeypatch.setattr(mailer.smtplib, "SMTP", FakeSMTP)
    recips = ["one@x.com", "two@x.com"]
    mailer.send("제목", "<p>html</p>", "text", recips)

    # Everyone delivered via the envelope
    assert captured["envelope"] == recips
    # Recipient addresses appear in no header (not exposed to each other)
    for r in recips:
        assert r not in captured["body"]
    # The Bcc header is not included in the message
    assert "Bcc:" not in captured["body"]
