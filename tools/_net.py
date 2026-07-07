"""Network helpers with SSRF protection for the fetch_* CLI tools.

`safe_get` and `safe_get_stream` are drop-in replacements for
`requests.get` that validate the target host's resolved IPs against an
RFC 1918 / loopback / link-local / metadata-endpoint blocklist BEFORE
the request is sent — and re-validate on every redirect hop.

Why: the wiki's mobile inbox path pulls untrusted URLs from
`raw/_inbox.md` and feeds them to `requests.get(...)`. Without scheme +
host validation, an attacker could craft a URL that resolves to
`169.254.169.254` (cloud metadata), `127.0.0.1`, or any RFC 1918 host
and reach internal services from the operator's machine. Cross-origin
HTTP redirects to private ranges have the same effect.

Trade-offs intentionally NOT covered:
- DNS rebinding (validate-then-fetch race) — would require socket-level
  IP pinning. The window is small for human-driven inbox ingest, so we
  accept the residual risk.
- IPv6-mapped IPv4 (`::ffff:127.0.0.1`) — `ipaddress.ip_address` reports
  these as IPv6 and `is_private`/`is_loopback` flags don't catch them by
  default. `_is_blocked_ip` explicitly extracts the v4 mapping when
  present.
- Outbound proxy honoring — environment proxies still apply since we use
  a fresh `requests.Session()`. Operators routing through corporate
  proxies should set NO_PROXY or trust the proxy's allowlist.
"""
from __future__ import annotations

import ipaddress
import os
import re
import shutil
import socket
import subprocess
import tempfile
from urllib.parse import quote, urljoin, urlparse

import requests

# Categorically reject any non-http(s) scheme. file://, gopher://, ftp://,
# data:// are never legitimate ingest targets.
ALLOWED_SCHEMES = {"http", "https"}

# Per-call redirect cap. requests' default is 30; we shrink to 10 so a
# malicious URL can't waste 30 socket connects in a chain.
MAX_REDIRECTS = 10


class UnsafeURLError(ValueError):
    """Raised when a URL targets a forbidden host or scheme."""


def _is_blocked_ip(addr: str) -> bool:
    """True iff the resolved address falls in a forbidden range.

    Covers: private (RFC 1918), loopback (127.0.0.0/8, ::1), link-local
    (169.254.0.0/16 — includes cloud metadata), multicast, reserved
    (0.0.0.0/8, 240.0.0.0/4), unspecified (0.0.0.0, ::). Unparseable
    addresses are treated as blocked (fail-closed).

    IPv6-mapped IPv4 (::ffff:a.b.c.d) is unwrapped before the check so
    the v4-side flags apply.
    """
    try:
        ip = ipaddress.ip_address(addr)
    except ValueError:
        return True
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def _validate_url(url: str) -> None:
    """Validate scheme + every resolved IP for the URL's host.

    Resolves via `socket.getaddrinfo` (covers both v4 and v6). Raises
    UnsafeURLError on disallowed scheme, missing host, DNS failure, or
    any returned address falling into a blocked range.
    """
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    if scheme not in ALLOWED_SCHEMES:
        raise UnsafeURLError(f"scheme `{scheme}` not in {sorted(ALLOWED_SCHEMES)}: {url}")
    host = parsed.hostname
    if not host:
        raise UnsafeURLError(f"no host in URL: {url}")
    try:
        infos = socket.getaddrinfo(host, None)
    except (socket.gaierror, UnicodeError) as e:
        # UnicodeError covers IDNA-invalid hosts (e.g. a label >63 chars),
        # which getaddrinfo raises instead of gaierror — fail closed like a
        # DNS failure rather than letting it escape to the caller.
        raise UnsafeURLError(f"DNS resolution failed for {host}: {e}") from e
    for info in infos:
        addr = info[4][0]
        if _is_blocked_ip(addr):
            raise UnsafeURLError(
                f"host `{host}` resolves to blocked IP `{addr}`: {url}"
            )


def safe_get(url: str, *, timeout: int = 15, headers=None, **kwargs) -> requests.Response:
    """`requests.get` replacement with per-hop SSRF validation.

    Returns the final response after manually following redirects. Each
    Location header is re-validated before the next hop fires.
    """
    session = requests.Session()
    if headers:
        session.headers.update(headers)
    return _safe_get_impl(session, url, timeout=timeout, stream=False, **kwargs)


def safe_get_stream(url: str, *, timeout: int = 15, headers=None, **kwargs) -> requests.Response:
    """Streaming variant for binary downloads (PDFs)."""
    session = requests.Session()
    if headers:
        session.headers.update(headers)
    return _safe_get_impl(session, url, timeout=timeout, stream=True, **kwargs)


def _safe_get_impl(
    session: requests.Session, url: str, *, timeout: int, stream: bool, **kwargs
) -> requests.Response:
    """Manual redirect loop. Each hop validates its target URL first.

    Session lifetime: for a non-stream request the body is fully read into
    `resp.content` by the time `session.get` returns, so the session (and its
    connection pool) can be closed immediately. For a stream request the
    session must outlive the call until the caller closes the body, so we
    chain `session.close()` onto the response's `close()` — closing the
    response (e.g. via its context manager) then tears the session down too.
    """
    # `allow_redirects` is enforced False internally — the manual loop
    # owns redirect resolution so it can validate each hop.
    kwargs.pop("allow_redirects", None)
    current = url
    # Any non-return exit (validation failure on a redirect hop, too many
    # redirects, or an unexpected error) must close the still-open session so
    # the connection pool is not leaked. Only the _bind_session return path
    # hands the session off to the caller; everything else closes here.
    try:
        for _ in range(MAX_REDIRECTS):
            _validate_url(current)
            resp = session.get(
                current, timeout=timeout, stream=stream, allow_redirects=False, **kwargs
            )
            if not resp.is_redirect or not resp.headers.get("Location"):
                return _bind_session(resp, session, stream)
            # Drain the previous response body to free the connection before
            # we reuse the session for the next hop. Streaming responses
            # otherwise hold the socket.
            if stream:
                resp.close()
            current = urljoin(current, resp.headers["Location"])
        raise UnsafeURLError(f"too many redirects (>{MAX_REDIRECTS}) starting at {url}")
    except BaseException:
        session.close()
        raise


def _bind_session(
    resp: requests.Response, session: requests.Session, stream: bool
) -> requests.Response:
    """Release `session` at the right time and return `resp`.

    Non-stream: body is already buffered, so close now. Stream: defer until
    the caller closes the response by wrapping `resp.close`."""
    if not stream:
        session.close()
        return resp
    original_close = resp.close

    def _close_both():
        try:
            original_close()
        finally:
            session.close()

    resp.close = _close_both  # type: ignore[method-assign]
    return resp


# ---------------------------------------------------------------------------
# curl-subprocess fallback for WAF / TLS-fingerprint blocks
# ---------------------------------------------------------------------------
# Some WAFs (Cloudflare et al.) fingerprint the TLS ClientHello (JA3) and
# reject `requests`/urllib3's handshake with HTTP 403 *no matter how
# browser-like the HTTP headers are* — `safe_get` with full Sec-Fetch headers
# still 403s on finextra.com, bankautomationnews.com, etc. The system `curl`
# binary presents a different TLS fingerprint that those same WAFs pass, so it
# serves as a zero-dependency fallback (curl.exe ships with Windows 10 1803+).
#
# The fallback MUST preserve `_net.py`'s SSRF contract: untrusted inbox URLs
# get every redirect hop's resolved IP validated. We therefore drive curl with
# `--max-redirs 0` and run the same manual redirect loop as `_safe_get_impl`,
# re-validating each Location before the next hop fires.

# Statuses where a WAF / TLS-fingerprint block is plausible — worth a curl /
# Wayback retry rather than a hard failure.
BLOCKED_STATUSES = frozenset({401, 403, 406, 429, 451})

_CURL_BIN = shutil.which("curl")


class CurlUnavailable(RuntimeError):
    """Raised when the curl binary is not on PATH (fallback unavailable)."""


def _parse_curl_headers(text: str) -> dict[str, str]:
    """Parse a curl `-D -` header dump into a lowercased dict (last wins)."""
    headers: dict[str, str] = {}
    for line in text.splitlines():
        if line.startswith("HTTP/") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        headers[key.strip().lower()] = value.strip()
    return headers


_CURL_STATUS_MARKER = "__CURL_HTTP_STATUS__"


def _curl_one_hop(
    url: str, timeout: int, headers: dict | None
) -> tuple[int, dict[str, str], bytes]:
    """Run one curl GET WITHOUT following redirects.

    Returns (status_code, response_headers, body_bytes). Redirect resolution
    is left to the caller so each hop can be SSRF-validated first — mirroring
    `_safe_get_impl`'s manual loop. `--compressed` lets curl transparently
    decode gzip/br, so the returned bytes are always the decoded body.
    """
    if _CURL_BIN is None:
        raise CurlUnavailable("curl binary not found on PATH")
    fd, body_path = tempfile.mkstemp(prefix="curlbody_")
    os.close(fd)
    try:
        args = [
            _CURL_BIN, "-sS", "--compressed", "--max-redirs", "0",
            "--connect-timeout", str(timeout), "--max-time", str(timeout + 10),
            "-D", "-", "-o", body_path, "-w", f"{_CURL_STATUS_MARKER}%{{http_code}}",
            url,
        ]
        for key, value in (headers or {}).items():
            # `--compressed` owns Accept-Encoding (full br/zstd browser list);
            # forwarding the caller's narrow `gzip, deflate` (chosen so urllib3
            # avoids brotli it can't decode) both conflicts with `--compressed`
            # and trips some WAFs that expect a browser-like encoding list.
            if key.lower() == "accept-encoding":
                continue
            args += ["-H", f"{key}: {value}"]
        proc = subprocess.run(args, capture_output=True, timeout=timeout + 20, check=False)
        if proc.returncode != 0:
            err = proc.stderr.decode("utf-8", "replace").strip()[:200]
            raise OSError(f"curl exited {proc.returncode}: {err}")
        # stdout = <header dump> + marker + <3-digit status>. Headers are
        # latin-1 by RFC 7230, so decode the dump that way; the body itself
        # was written to `body_path` as raw bytes.
        stdout = proc.stdout.decode("iso-8859-1", "replace")
        header_text, _, status_text = stdout.rpartition(_CURL_STATUS_MARKER)
        status = int(status_text) if status_text.strip().isdigit() else 0
        resp_headers = _parse_curl_headers(header_text)
        with open(body_path, "rb") as fh:
            body = fh.read()
        return status, resp_headers, body
    finally:
        try:
            os.unlink(body_path)
        except OSError:
            pass


def _synthesize_response(
    status: int, body: bytes, final_url: str, resp_headers: dict[str, str]
) -> requests.Response:
    """Build a genuine `requests.Response` from curl output so downstream
    code (`.text`, `.apparent_encoding`, `raise_for_status`, context manager)
    works unchanged. `_content` holds the already-decompressed body."""
    resp = requests.Response()
    resp.status_code = status
    resp._content = body
    resp.url = final_url
    ctype = resp_headers.get("content-type")
    if ctype:
        resp.headers["Content-Type"] = ctype
    # Mirror requests' own default (ISO-8859-1 for text/* without charset);
    # callers' encoding fixup then upgrades via chardet where needed.
    resp.encoding = requests.utils.get_encoding_from_headers(resp.headers)
    return resp


def curl_get(url: str, *, timeout: int = 20, headers=None) -> requests.Response:
    """SSRF-safe curl-subprocess GET — fallback for hosts whose WAF blocks
    `requests`' TLS fingerprint while passing curl's.

    Follows redirects manually, re-validating every hop's resolved IP exactly
    like `safe_get`. Returns a synthesized `requests.Response` (status is NOT
    raised — the caller inspects `.status_code`). Raises `UnsafeURLError` on a
    blocked host/redirect or redirect overflow, `CurlUnavailable` if curl is
    missing, `OSError` on subprocess failure.
    """
    current = url
    for _ in range(MAX_REDIRECTS):
        _validate_url(current)
        status, resp_headers, body = _curl_one_hop(current, timeout, headers)
        location = resp_headers.get("location")
        if status in (301, 302, 303, 307, 308) and location:
            current = urljoin(current, location)
            continue
        return _synthesize_response(status, body, current, resp_headers)
    raise UnsafeURLError(f"too many redirects (>{MAX_REDIRECTS}) starting at {url}")


def wayback_snapshot(url: str, *, timeout: int = 15) -> str | None:
    """Return a raw (`id_`) Wayback Machine snapshot URL for `url`, or None.

    For hosts behind a full JS challenge (curl also 403s — e.g. darkreading),
    the Internet Archive's capture is the last resort. The `id_` timestamp
    modifier returns the archived bytes WITHOUT Wayback's injected toolbar/JS
    so extraction sees the original page. The availability API is queried via
    `requests` (it does not fingerprint-block); the snapshot fetch itself
    should go through `curl_get` (web.archive.org rejects some bot handshakes).
    """
    api = "https://archive.org/wayback/available?url=" + quote(url, safe="")
    try:
        with safe_get(api, timeout=timeout) as r:
            r.raise_for_status()
            data = r.json()
    except (requests.exceptions.RequestException, ValueError, UnsafeURLError):
        return None
    snap = (data.get("archived_snapshots") or {}).get("closest") or {}
    if not snap.get("available") or not snap.get("url"):
        return None
    snap_url = str(snap["url"])
    m = re.search(r"/web/(\d+)/", snap_url)
    if m:
        snap_url = snap_url.replace(f"/web/{m.group(1)}/", f"/web/{m.group(1)}id_/", 1)
    return snap_url.replace("http://", "https://", 1)
