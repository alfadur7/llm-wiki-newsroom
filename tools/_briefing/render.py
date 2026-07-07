"""Weekly briefing markdown → email HTML/plaintext rendering.

Among the `[[slug|alias]]` wikilinks in the body, those that **exist as graph nodes**
(source/entity/concept) become deep links into the Cloudflare-hosted graph (`<base>#q=<slug>`),
while non-nodes (synthesis / contradiction theme / other briefings) are replaced with the plain
alias. Node detection is done via a `graph/_pages.json::idmap` (slug stem → node id) lookup — only
substance nodes appear in idmap, so a `.get(slug)` of None means it is not a node.

The deep-link base/key encoding is shared with `tools/export.py` via `_lib.graph_deeplink_base` /
`_lib.deeplink_key` (Korean raw, only spaces, parentheses, and `%` encoded), so the two channels
cannot drift. The env var `BRIEFING_GRAPH_BASE`, if set, takes precedence over the base.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # _briefing/ → tools/
from _lib import GRAPH, REPO_ROOT, deeplink_key, graph_deeplink_base, parse_frontmatter, strip_frontmatter  # noqa: E402

import mistune  # noqa: E402

# `[[slug|alias]]` or `[[slug]]` (an anchor `#...` is split off from the slug). group1=slug, group2=alias.
_WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]*))?\]\]")


def load_idmap() -> dict:
    """Return the idmap (slug stem → node id) from graph/_pages.json. {} if absent.

    _pages.json is a byproduct of build.py (pages.run) and is gitignored, so it must be
    brought up to date with `python tools/build.py` before calling (the send-briefing
    workflow guarantees this)."""
    pages = GRAPH / "_pages.json"
    if not pages.exists():
        return {}
    try:
        return json.loads(pages.read_text(encoding="utf-8")).get("idmap", {})
    except (OSError, ValueError):
        return {}


def graph_base() -> str:
    """Return the deep-link base (`<BASE_URL>/<STANDALONE_SLUG>`). '' if the graph is private.

    Priority: env `BRIEFING_GRAPH_BASE` → `_lib.graph_deeplink_base()` (shared with
    export.py — the older approach of regex-extracting from the export.py source was a
    coupling that silently produced empty links whenever the quote style changed, so it
    was reduced to a plain import)."""
    env = os.environ.get("BRIEFING_GRAPH_BASE", "").strip()
    if env:
        return env.rstrip("/")
    return graph_deeplink_base()


def _convert_wikilinks(body: str, idmap: dict, base: str) -> str:
    """`[[slug|alias]]` → `[alias](base#q=key)` if it is a node, else plain `alias`.

    If base is '' (graph private), everything is plain text. A truthy idmap.get(slug) means a substance node."""
    def repl(m: re.Match) -> str:
        slug = m.group(1).strip()
        alias = (m.group(2) or slug).strip()
        if base and idmap.get(slug):
            return f"[{alias}]({base}#q={deeplink_key(slug)})"
        return alias

    return _WIKILINK_RE.sub(repl, body)


def _plain_wikilinks(body: str) -> str:
    """For the text/plain fallback — always render wikilinks as the plain alias."""
    return _WIKILINK_RE.sub(lambda m: (m.group(2) or m.group(1)).strip(), body)


_EMAIL_SHELL = """\
<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f4f5f7;">
<div style="max-width:680px;margin:0 auto;padding:28px 24px;background:#ffffff;
font-family:-apple-system,'Segoe UI',Roboto,'Malgun Gothic','맑은 고딕',sans-serif;
font-size:15px;line-height:1.7;color:#1a1a1a;word-break:keep-all;">
{body}
<hr style="border:none;border-top:1px solid #e2e4e8;margin:32px 0 12px;">
<p style="font-size:12px;color:#8a8f98;margin:0;">This is an automatically generated briefing. If you spot an error, please reply to this email.</p>
</div></body></html>
"""


def render(md_text: str) -> dict:
    """Briefing markdown → {subject, html, text}.

    subject = frontmatter `title` (if absent, the body's first `# ` header; if that is also absent, a default)."""
    fm = parse_frontmatter(md_text)
    body = strip_frontmatter(md_text).strip()

    subject = fm.get("title") if isinstance(fm.get("title"), str) else ""
    if not subject:
        h1 = re.search(r"^#\s+(.+)$", body, re.M)
        subject = h1.group(1).strip() if h1 else "Weekly Wiki Briefing"

    idmap = load_idmap()
    base = graph_base()

    html_body = mistune.html(_convert_wikilinks(body, idmap, base))
    html = _EMAIL_SHELL.format(body=html_body)
    text = _plain_wikilinks(body)
    return {"subject": subject, "html": html, "text": text}
