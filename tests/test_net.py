"""Unit tests for the `tools/_net.py` SSRF helpers — network-independent paths only
(blocked-IP classification, scheme rejection, curl header parsing)."""
import pytest

from _net import (
    BLOCKED_STATUSES,
    UnsafeURLError,
    _is_blocked_ip,
    _parse_curl_headers,
    _validate_url,
)


@pytest.mark.parametrize("addr", [
    "127.0.0.1",          # loopback
    "10.1.2.3",           # RFC1918
    "192.168.0.5",        # RFC1918
    "169.254.169.254",    # link-local — cloud metadata
    "0.0.0.0",            # unspecified
    "::1",                # v6 loopback
    "::ffff:127.0.0.1",   # v6-mapped v4 — explicit unwrap path
    "not-an-ip",          # unparseable → fail-closed
])
def test_blocked_ips(addr):
    assert _is_blocked_ip(addr) is True


@pytest.mark.parametrize("addr", ["8.8.8.8", "1.1.1.1", "2606:4700::1111"])
def test_public_ips_allowed(addr):
    assert _is_blocked_ip(addr) is False


@pytest.mark.parametrize("url", [
    "file:///etc/passwd",
    "gopher://x/",
    "ftp://x/",
    "https://",   # no host
])
def test_validate_url_rejects_without_dns(url):
    # Scheme/host validation must fail before DNS resolution (network-independent).
    with pytest.raises(UnsafeURLError):
        _validate_url(url)


def test_parse_curl_headers_lowercase_last_wins():
    headers = _parse_curl_headers(
        "HTTP/1.1 301 Moved\r\nLocation: /a\r\nLocation: /b\r\nContent-Type: text/html\r\n"
    )
    assert headers["location"] == "/b"
    assert headers["content-type"] == "text/html"


def test_blocked_statuses_are_waf_codes():
    assert {401, 403, 429} <= BLOCKED_STATUSES
