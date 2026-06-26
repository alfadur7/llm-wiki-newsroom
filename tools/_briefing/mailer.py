"""Gmail SMTP delivery (STARTTLS). Zero external dependencies — only stdlib smtplib / email.

Credentials and recipients come from environment variables:
  GMAIL_USER           sending Gmail address (e.g. sender@example.com)
  GMAIL_APP_PASSWORD   16-char Gmail app password (not the regular password)
  BRIEFING_RECIPIENTS  recipients, comma-separated

To keep addresses and passwords out of the repo, inject them only via GH Secrets (or local env).
"""
from __future__ import annotations

import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

# Invisible characters that str.strip() cannot remove — if they leak in from a
# secret/address saved as UTF-8-BOM, they cause an ascii encoding error at the
# SMTP RCPT stage (the 2026-06 delivery failure). They are never valid in an
# email address or credential, so strip all of them.
_INVISIBLE = "\ufeff\u200b\u200c\u200d\u2060"  # BOM·ZWSP·ZWNJ·ZWJ·word-joiner
_INVISIBLE_TABLE = {ord(c): None for c in _INVISIBLE}


def clean_addr(value: str) -> str:
    """Strip invisible characters (BOM / zero-width) from an address/credential, then trim whitespace."""
    return value.translate(_INVISIBLE_TABLE).strip()


def recipients_from_env() -> list[str]:
    """BRIEFING_RECIPIENTS (comma-separated) → list of addresses. Drops empty items and invisible characters."""
    raw = os.environ.get("BRIEFING_RECIPIENTS", "")
    return [c for a in raw.split(",") if (c := clean_addr(a))]


def send(subject: str, html: str, text: str, recipients: list[str]) -> None:
    """Send a multipart/alternative (text+html) email via Gmail SMTP.

    GMAIL_USER / GMAIL_APP_PASSWORD env vars are required. Raises ValueError if recipients is empty."""
    user = clean_addr(os.environ.get("GMAIL_USER", ""))
    password = clean_addr(os.environ.get("GMAIL_APP_PASSWORD", ""))
    if not user or not password:
        raise ValueError("The GMAIL_USER and GMAIL_APP_PASSWORD environment variables are required.")
    if not recipients:
        raise ValueError("No recipients (set BRIEFING_RECIPIENTS or --to).")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = formataddr(("Weekly Briefing", user))
    # Recipients are delivered via BCC only — listing them in the To header would
    # expose every recipient's address to the others. Actual delivery is decided
    # by the sendmail() envelope, so everyone still receives it even when left out
    # of the headers. The Bcc header itself is not added to the message (adding it
    # would defeat the exposure prevention). To is filled with the sender's own
    # address — an empty To hurts spam-filter scoring.
    msg["To"] = formataddr(("Weekly Briefing", user))
    # Attach text first — clients display the last part (html) preferentially, with text as fallback.
    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls(context=ssl.create_default_context())
        smtp.login(user, password)
        smtp.sendmail(user, recipients, msg.as_string())
