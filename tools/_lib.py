"""Shared utilities for tools/ scripts.

Extracted in Phase 1 of the tools refactor to remove duplicated
WIKI path constants, regex patterns, frontmatter parsing, and
markdown-body stripping logic.

Import pattern:

    from _lib import WIKI, WIKILINK_RE, parse_frontmatter, strip_code

Scripts in tools/ can import directly (same directory). Callers from
outside tools/ must add tools/ to sys.path or run with `python -m`.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path


def korean_mode() -> bool:
    """Corpus-language gate. The engine is English-native; the Korean-specific
    heuristics retained as an optional capability (grammar-aware lint lenses,
    Hangul-first sort, Korean web-search query tokens, ko-KR fetch headers)
    fire only when the WIKI_LANG environment variable is set to "ko". The
    default ("en") keeps them off, so they never skew an English corpus.

    Read live (not cached at import) so tests and per-run config can toggle it.
    """
    return os.environ.get("WIKI_LANG", "en").strip().lower() == "ko"


def atomic_write_text(path: Path, content: str, *, encoding: str = "utf-8") -> None:
    """Write `content` to `path` atomically (tmp + os.replace).

    A crash mid-write would otherwise leave a half-written file. For
    SoT JSONs (`_clusters.json`, `_source_map.json`) and other consumed
    artefacts this risks downstream readers picking up corrupted state.
    `os.replace` is atomic on POSIX and Windows when source and target
    sit on the same filesystem (which they do here — both under the
    same `path.parent`).

    Newline-normalize to LF (`newline=""` + manual write) so Windows
    doesn't translate to CRLF, which would change disk bytes and break
    cross-platform diff parity for content-equal output.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding=encoding, newline="") as fh:
        fh.write(content)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def atomic_write_bytes(path: Path, data: bytes) -> None:
    """Binary-data variant of `atomic_write_text`. Used for PDF downloads."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


_SAFE_SLUG_RE = re.compile(r"^[a-z0-9-]+$")


def safe_slug_path(parent: Path, slug: str) -> Path:
    """Validate `slug` then return `parent/<slug>.md`.

    Slug must match `[a-z0-9-]+` (current corpus convention — all cluster
    slugs and theme slugs are pure ASCII kebab-case). Used as a gate at
    every slug → Path conversion site that consumes slugs from JSON
    (cluster_labels.json, _contradictions_themes.json) or hand-edited
    sources, so a `..` or path-separator injection cannot escalate to
    arbitrary unlink/write under wiki/.
    """
    if not slug or not _SAFE_SLUG_RE.match(slug):
        raise ValueError(
            f"unsafe slug: {slug!r} — must match {_SAFE_SLUG_RE.pattern}"
        )
    return parent / f"{slug}.md"


def atomic_write_if_changed(path: Path, content: str, *, encoding: str = "utf-8") -> bool:
    """Atomic write only if on-disk content differs. Returns True if a write
    occurred, False on a no-op.

    Two motivations stack:
      1. Atomicity — same as `atomic_write_text`, no half-written file on crash.
      2. Dirty-check — avoids spurious mtime updates that surface as
         phantom-modified state in `git status` when the build produces
         identical output across runs.
    """
    if path.exists():
        try:
            if path.read_text(encoding=encoding) == content:
                return False
        except OSError:
            pass  # fall through and rewrite
    atomic_write_text(path, content, encoding=encoding)
    return True

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Anchor on the repo root (tools/ → repo) rather than the process cwd. A
# bare `Path("wiki")` only resolves when a script is launched from the repo
# root; `__file__`-based anchoring survives any cwd (memory
# feedback_verify_by_running_not_import — cwd-relative data paths break at
# runtime, not import). fetch_inbox.py already uses this REPO_ROOT pattern.
REPO_ROOT = Path(__file__).resolve().parent.parent
WIKI = REPO_ROOT / "wiki"
GRAPH = REPO_ROOT / "graph"

# --- Hosted graph browser deploy constants ---
# BASE_URL/STANDALONE_SLUG drive the standalone output filename, the RAG
# handoff link template (export.py), and the briefing deeplink base
# (_briefing/render.py) — defined in one place so the deploy path and the
# outgoing links cannot drift.
# Fill once — see .claude/operations/graph-hosting-setup.md. Leave BASE_URL
# empty to skip the handoff block (standalone files are still produced).
#   BASE_URL: Pages root, e.g. "https://USER.github.io/REPO"
#   STANDALONE_SLUG: unguessable filename (minimizes exposure), e.g. "g-7f3a9c2e"
BASE_URL = ''
STANDALONE_SLUG = 'g-7f3a9c2e'

# Wikilink regex family — single definition (meta lint blocks redefinition):
#   WIKILINK_RE        does not match anchored (`[[x#s]]`) links — stem of a non-anchor link
#   WIKILINK_TARGET_RE captures the full target (including #anchor) — normalization is the comparison site's job
#   WIKILINK_STEM_RE   consumes alias/anchor and captures only the bare stem
#   WIKILINK_ANY_RE    link existence itself (no capture — for density counting)
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:\|[^\]]*)?\]\]")
WIKILINK_TARGET_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]")
WIKILINK_STEM_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")
WIKILINK_ANY_RE = re.compile(r"\[\[[^\]]+\]\]")


def real_source_files() -> list[Path]:
    """All 'real' source pages (`wiki/sources/*.md`, excluding `_`-prefixed auto-generated ones).

    Build artifacts like `_catalog*.md` and `_source_map.json` live alongside
    real pages in `wiki/sources/`, so a raw `grep -rl <name> wiki/sources/`
    over-counts frequency (2026-06-24 김태수 claimant 5 → actual 2 miscount
    incident). Claimant/term frequency decisions (entity stub thresholds, etc.)
    use this helper as the single SoT — no raw grep. CLI: `tools/count_mentions.py`.
    """
    d = WIKI / "sources"
    if not d.is_dir():
        return []
    return sorted(fp for fp in d.glob("*.md") if not fp.name.startswith("_"))
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
# Frontmatter block matcher — group(1) = YAML text between the `---` fences.
# Single shared definition: per-module copies of this regex drifted into
# variants before (see codebase-audit carry-forward), so hub/* lint modules
# import this instead of redefining.
FRONTMATTER_BLOCK_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
# AUTO:<name> BEGIN…END block (build.py-regenerated region). Named groups
# name/body for extraction; `\s*` tolerant for stripping via `.sub`. Single
# SoT — the hoisting lint forbids per-module AUTO_* redefinitions (drift class).
AUTO_BLOCK_RE = re.compile(
    r"<!--\s*AUTO:(?P<name>\w+)\s*BEGIN\s*-->(?P<body>.*?)<!--\s*AUTO:\w+\s*END\s*-->",
    re.DOTALL,
)
BLOCKQUOTE_RE = re.compile(r"^\s*>.*$", re.MULTILINE)

# Tool-call markup that must never reach published wiki content. An agent's
# Write/Edit can leak its own function-call closing tags into a file body
# (observed 2026-06-08: a cloud briefing routine committed `</content>` and
# `</invoke>` at a W23 EOF). Link/schema regexes don't catch raw XML, and an
# unmanned pipeline has no human read to spot it — so structure (corpus-wide)
# and synthesis (the routine's scoped path) both guard against it. Scan
# code-stripped text so intentional fenced XML examples stay exempt.
MARKUP_LEAK_RE = re.compile(
    r"</?(?:function_calls|invoke|parameter|content)>|<(?:invoke|parameter)\b|antml:"
)


def strip_frontmatter(text: str) -> str:
    """Return body with YAML frontmatter removed. No-op if absent."""
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 4)
    if end == -1:
        return text
    return text[end + 4:]


def strip_code(text: str) -> str:
    """Drop fenced code blocks and inline code spans."""
    in_fence = False
    out: list[str] = []
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(INLINE_CODE_RE.sub("", line))
    return "\n".join(out)


def strip_blockquotes(text: str) -> str:
    return BLOCKQUOTE_RE.sub("", text)


_LIST_ITEM_RE = re.compile(r"^\s*-\s+(.+?)\s*$")


def _unquote_scalar(val: str) -> str:
    """Strip surrounding YAML quotes and unescape inner escapes.

    A naive `.strip('"')` leaves a dangling backslash when a double-quoted
    value ends with an escaped quote (`"…emphasis\\""` -> `…emphasis\\`), which then
    escapes the closing `]` of any Markdown link built from it and breaks the
    link in Obsidian. Here we unescape `\\"`/`\\\\` for double-quoted scalars and
    `''` for single-quoted ones; `\\n`/`\\t` are left literal so single-line
    title/description fields never sprout a real newline.
    """
    val = val.strip()
    if len(val) >= 2 and val[0] == '"' and val[-1] == '"':
        return re.sub(r'\\(["\\])', r"\1", val[1:-1])
    if len(val) >= 2 and val[0] == "'" and val[-1] == "'":
        return val[1:-1].replace("''", "'")
    return val


def parse_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter into a dict. Supports:
      - Scalars: `key: value` (quotes stripped)
      - Inline lists: `key: [a, b, c]`
      - Block-style lists with or without indentation:
            key:
            - item1
            - item2
        (Obsidian and various editors emit both indented and unindented
        block lists; both map to a Python list under `key`.)

    Returns {} if there's no frontmatter.
    """
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}

    out: dict = {}
    current_list_key: str | None = None

    for line in text[4:end].split("\n"):
        # Block-list continuation: only meaningful when the previous key
        # produced an empty scalar (signals a YAML block list).
        if current_list_key is not None:
            lm = _LIST_ITEM_RE.match(line)
            if lm:
                item = _unquote_scalar(lm.group(1).strip())
                out[current_list_key].append(item)
                continue
            # Empty line inside block list is tolerated; non-list / non-empty
            # line terminates the block.
            if line.strip() == "":
                continue
            current_list_key = None

        m = re.match(r"^(\w+):\s*(.*)$", line)
        if not m:
            continue
        key = m.group(1)
        val = m.group(2).strip()

        if val.startswith("["):
            items = [
                _unquote_scalar(x.strip())
                for x in val.strip("[]").split(",")
                if x.strip()
            ]
            out[key] = items
            current_list_key = None
        elif val == "":
            # Could be a block list or a genuinely empty scalar. Start an
            # empty list; subsequent `- item` lines will populate it. If
            # no list items follow, the value stays as an empty list,
            # which the `not fm[field]` falsy check treats as missing —
            # matching the semantics of a truly absent value.
            out[key] = []
            current_list_key = key
        else:
            out[key] = _unquote_scalar(val)
            current_list_key = None

    return out


def parse_page_meta(content: str, filename: str) -> tuple[str, str, str, str, str, str]:
    """Return (title, type, description, source_file, date, source_url).

    Shared helper for index.py and _build/clusters.py (catalog generation).
    The 5th element (`date`) is the page's chronological key: `published`
    (publication date) when known, else `scraped` (collection date). The
    legacy `date` field was split into those two and removed.
    source_url is the URL frontmatter field set on wiki/sources pages that
    don't inherit URL from a raw markdown clipping.
    """
    description = ""

    # Use the canonical frontmatter boundary (parse_frontmatter / strip_frontmatter
    # both anchor on `find("\n---", 4)`) instead of a `split("---", 2)`. The split
    # form mis-parsed any scalar value containing a literal `---` (title truncated,
    # type swallowing the rest of the line, body lost). Proven equivalent on the
    # happy path: across the full corpus both the extracted fields and the body are
    # byte-identical between the two boundaries (0 mismatches, 2120 pages) — the
    # only behavioral change is removing the latent `---`-in-value trap.
    fm = parse_frontmatter(content)

    def _fm_scalar(key: str, default: str) -> str:
        val = fm.get(key, default)
        return val if isinstance(val, str) else default

    title = _fm_scalar("title", filename.replace(".md", ""))
    page_type = _fm_scalar("type", "unknown")
    source_file = _fm_scalar("source_file", "")
    date = _fm_scalar("published", "") or _fm_scalar("scraped", "")
    source_url = _fm_scalar("source_url", "")

    body = strip_frontmatter(content)

    # Drop HTML comments (abbreviation declarations, AUTO:* markers) before
    # scanning for the description — otherwise a hub whose first body content is
    # a `<!-- abbreviation... -->` block yields the comment's first line as its
    # description, leaking an unclosed `<!--` fragment into index.md/catalogs.
    body = re.sub(r'<!--.*?-->', '', body, flags=re.DOTALL)

    first_list_item = ""
    for line in body.split("\n"):
        line = line.strip()
        if not line or line.startswith("#") or line.startswith(">") or line.startswith("|") or line.startswith("*"):
            continue
        if line.startswith("- "):
            if not first_list_item and len(line) > 10:
                first_list_item = line[2:]
            continue
        if re.match(r'^\d+[.)]\s', line):
            continue
        if len(line) < 10:
            continue
        description = line
        break

    if not description and first_list_item:
        description = first_list_item

    if description:
        description = re.sub(r'\[\[([^|\]]*\|)?([^\]]+)\]\]', r'\2', description)
        for sep in ['. ', '? ', '! ', '.', '?', '!']:
            idx = description.find(sep)
            if idx != -1:
                description = description[:idx + len(sep)].rstrip()
                break
        else:
            if len(description) > 120:
                description = description[:117].rsplit(" ", 1)[0] + "…"

    return title, page_type, description, source_file, date, source_url


def parse_source_alts(content: str) -> tuple[list[str], list[str]]:
    """Extract `source_url_alt` and `source_file_alt` frontmatter into lists.

    Variant share-link fetches (e.g., `share.google/<a>` and `share.google/<b>`
    pointing at the same article) accumulate as alt entries on the canonical
    wiki source page. The dedup map (_source_map.json::by_url + by_path) must
    index every alt key to the same slug, otherwise the next ingest of the
    same variant misses by_url and looks new.

    Each field accepts a single scalar (`source_url_alt: "https://..."`) or a
    YAML list (`source_url_alt: ["a", "b"]` or block form with `- a` lines).
    """
    urls: list[str] = []
    paths: list[str] = []
    # Reuse the canonical frontmatter parser instead of a hand-rolled
    # `split("---", 2)` loop. parse_frontmatter anchors on `find("\n---", 4)`
    # (so a scalar value containing a literal `---` no longer splits the block
    # at the wrong place and silently drops alt entries), handles scalar /
    # inline-list / block-list forms uniformly, and unquotes via _unquote_scalar
    # — the same migration parse_page_meta already made.
    fm = parse_frontmatter(content)
    for key, bucket in (("source_url_alt", urls), ("source_file_alt", paths)):
        val = fm.get(key)
        if isinstance(val, list):
            bucket.extend(v for v in val if isinstance(v, str) and v)
        elif isinstance(val, str) and val:
            bucket.append(val)
    return urls, paths


def title_sort_key(item: tuple) -> tuple:
    """Case-insensitive alpha sort. Under WIKI_LANG=ko, sort Hangul-titled
    pages ahead of ASCII (the ga-na-da-then-A-Z order the Korean corpus used);
    otherwise plain case-insensitive order."""
    title = item[0] or ""
    first = title[0] if title else ""
    is_korean = korean_mode() and "\uac00" <= first <= "\ud7af"
    return (0 if is_korean else 1, title.lower())


def safe_link_text(text: str) -> str:
    """Make text safe as Markdown/Obsidian link display text.

    Obsidian Live Preview breaks on `[`/`]` inside link display text even when
    they are backslash-escaped, so substitute lenticular brackets (U+3010/3011)
    rather than escaping. This is a rendering workaround independent of corpus
    language, so it always applies.
    """
    return text.replace("[", "【").replace("]", "】")


def normalize_quotes(s: str) -> str:
    """Fold curly quotes to straight ASCII quotes for key matching."""
    return s.replace("\u2018", "'").replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')


def _build_id_map(nodes: list[dict]) -> dict[str, str]:
    """Map every plausible wikilink form (`[[stem]]`, `[[stem.md]]`, full
    path) to the canonical node id. Duplicate stems across subdirectories
    are resolved on first-seen basis via setdefault, so inference / labeling
    stay consistent across the build, query, and discover paths that share
    this resolver.
    """
    id_map: dict[str, str] = {}
    for n in nodes:
        nid = n["id"]
        id_map[nid] = nid
        stem = nid.rsplit("/", 1)[-1].removesuffix(".md")
        id_map.setdefault(stem, nid)
        id_map.setdefault(stem + ".md", nid)
    return id_map


def graph_structure_fingerprint(graph_data: dict) -> str:
    """Content hash of the clustering-relevant slice of `_graph.json` — node ids
    plus edge structure (from/to/type/confidence), excluding labels/titles/
    rationales. Clusters records this; index compares it to decide whether
    `_clusters.json` is genuinely stale. Invariant to label-only edits (which
    bump _graph.json mtime without changing the partition input), sensitive to
    structural edits that warrant a clusters rebuild.
    """
    import hashlib

    nodes = sorted(str(n.get("id", "")) for n in graph_data.get("nodes", []))
    edges = sorted(
        (
            str(e.get("from", "")),
            str(e.get("to", "")),
            str(e.get("type", "")),
            str(e.get("confidence", "")),
        )
        for e in graph_data.get("edges", [])
    )
    h = hashlib.sha256()
    h.update(repr(nodes).encode("utf-8"))
    h.update(repr(edges).encode("utf-8"))
    return h.hexdigest()[:16]


_FM_PUBLISHED_RE = re.compile(r"^published:\s*(\d{4}-\d{2}-\d{2})", re.MULTILINE)
_FM_SCRAPED_RE = re.compile(r"^scraped:\s*(\d{4}-\d{2}-\d{2})", re.MULTILINE)


# Process-lifetime text cache — reduces the I/O where `lint all` independently
# re-reads the 1600+ corpus files for every group down to one read. The
# mtime_ns/size check automatically invalidates a `--fix` rewrite (atomic
# replace → mtime change). UTF-8 errors="replace" is fixed — a corrupted file
# on the lint path passes with replacement characters instead of crashing, so
# diagnosis continues.
_TEXT_CACHE: dict[str, tuple[int, int, str]] = {}


def read_text_cached(path: Path | str) -> str:
    """Cached UTF-8 read (errors=replace). OSError propagates the same as read_text."""
    key = str(path)
    st = os.stat(key)
    cached = _TEXT_CACHE.get(key)
    if cached is not None and cached[0] == st.st_mtime_ns and cached[1] == st.st_size:
        return cached[2]
    text = Path(key).read_text(encoding="utf-8", errors="replace")
    _TEXT_CACHE[key] = (st.st_mtime_ns, st.st_size, text)
    return text


_SOURCE_DATE_CACHE: dict[str, str] = {}


def source_date_from_text(text: str) -> str:
    """published (publication date) else scraped (collection date) date from a
    source page's frontmatter `text`, or '' if neither. Single SoT for the
    published→scraped precedence shared by read_source_date and the contradiction
    recency builder (published is blank when unknown — no date match — so it falls
    back to scraped)."""
    pub = _FM_PUBLISHED_RE.search(text)
    scr = _FM_SCRAPED_RE.search(text)
    return (pub.group(1) if pub else "") or (scr.group(1) if scr else "")


def read_source_date(rel_path: str) -> str:
    """Chronological key for a wiki source page at `rel_path` (e.g.
    `sources/foo.md`, relative to WIKI): published (publication date) when
    present, else scraped (collection date), else `''` (which sorts as oldest
    under a descending tie-break). The legacy `date:` frontmatter field was
    split into `published:`/`scraped:` and removed, so reading `date:` always
    missed. Shared by the cluster source-block builder and the contradiction
    recency/staleness checks so the two cannot drift. Process-lifetime cache:
    reduces the I/O where `lint all`/build re-read the same rel for every group
    down to one read (wiki files are assumed immutable within a single run)."""
    cached = _SOURCE_DATE_CACHE.get(rel_path)
    if cached is not None:
        return cached
    try:
        text = (WIKI / rel_path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        _SOURCE_DATE_CACHE[rel_path] = ""
        return ""
    if not text.startswith("---"):
        _SOURCE_DATE_CACHE[rel_path] = ""
        return ""
    end = text.find("\n---", 4)
    if end < 0:
        _SOURCE_DATE_CACHE[rel_path] = ""
        return ""
    head = text[:end]
    val = source_date_from_text(head)
    _SOURCE_DATE_CACHE[rel_path] = val
    return val


# Query params that are append-only marketing tags or presentation variants —
# they never change article identity, so two URLs differing only by these point
# to the same source. Stripping them lets a re-scraped variant (e.g. mobile
# share-sheet appends `&utm_source=...&fbclid=...`) match the clean by_url key
# instead of surfacing as a false "genuine new" candidate every prefilter run.
_TRACKING_PARAMS = frozenset({
    "fbclid", "gclid", "dclid", "_aem", "igshid", "mc_cid", "mc_eid",
    "ntype", "sourcetype", "outputtype",
})
_TRACKING_PREFIXES = ("utm_",)


def canonicalize_url(url: str) -> str:
    """Canonical form of a URL for dedup matching.

    Lowercases scheme/host, drops tracking query params (utm_*, fbclid, ...) and
    the fragment, and sorts the remaining params so order is irrelevant. The path
    is identity-bearing and kept verbatim. Returns the input unchanged on parse
    failure. Additive by design — callers try an exact match first, then fall back
    to comparing canonical forms, so existing exact matches never regress.
    """
    from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

    try:
        parts = urlsplit(url.strip())
    except ValueError:
        return url.strip()
    kept = [
        (k, v)
        for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if k.lower() not in _TRACKING_PARAMS
        and not k.lower().startswith(_TRACKING_PREFIXES)
    ]
    kept.sort()
    return urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), parts.path, urlencode(kept), "")
    )


# Display labels for create/delete actions inside the confirm_changes box.
# English action keys are mapped to these labels at print time; unknown keys
# fall back to upper().
_CONFIRM_ACTION_LABELS = {
    "create": "create",
    "delete": "delete",
    "update": "update",
    "rename": "rename",
}


def confirm_changes(plan: dict, context: str = "", auto_yes: bool = False) -> bool:
    """Prompt for confirmation before executing a create/delete plan.

    plan: ordered dict-like mapping action label (e.g. "create", "delete")
          to lists of file paths affected. Empty values are skipped.
          English action keys are mapped to display labels at print time
          via _CONFIRM_ACTION_LABELS; unknown keys fall back to upper().
    context: short headline shown in the warning box (caller decides
             the wording of user-facing context lines).
    auto_yes: when True, skip the prompt and return True (used for the
              `--yes` CLI flag).

    Behavior:
      * empty plan (nothing to do) → returns True silently
      * auto_yes=True → prints plan, prints "--yes proceed" notice, returns True
      * stdin is a TTY → prints plan + interactive prompt, returns True
        only on `y`/`yes` (case-insensitive). Empty/Ctrl-C/Ctrl-D = False.
      * stdin is not a TTY → prints plan + abort hint, returns False.
        This protects automated callers (Claude Code Bash invocations,
        CI) — re-invoke explicitly with --yes after human review.

    The warning box uses ⚠️ markers so it stands out in lint output and is
    unambiguous for the human reader being asked to confirm. File deletes are
    irreversible without VCS, so the prompt is always opt-in.
    """
    total = sum(len(v) for v in plan.values() if v)
    if total == 0:
        return True

    print()
    print("⚠️  " + "=" * 70)
    print("⚠️  File changes require confirmation")
    if context:
        print(f"⚠️  {context}")
    print("⚠️  " + "-" * 67)
    for action, items in plan.items():
        if not items:
            continue
        label = _CONFIRM_ACTION_LABELS.get(action, action.upper())
        print(f"⚠️  {label} ({len(items)}):")
        for item in items:
            print(f"⚠️    - {item}")
    print("⚠️  " + "=" * 70)
    print("⚠️  Without version control (git), deletions cannot be undone.")
    print("⚠️  " + "=" * 70)
    print()

    if auto_yes:
        print("  (--yes flag set — proceeding without confirmation)")
        return True

    try:
        is_tty = sys.stdin.isatty()
    except (AttributeError, ValueError):
        is_tty = False

    if not is_tty:
        print(
            "  Aborted: cannot read a confirmation response in an automated "
            "environment (stdin is not a terminal). Review the changes above, "
            "then re-run with the --yes option."
        )
        return False

    try:
        response = input("Apply the changes above? [y/N]: ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\n  (cancelled)")
        return False
    return response in ("y", "yes")


def print_delete_cleanup_advisory(
    deleted_slugs: list[str],
    kind: str,
    check_cluster_labels: bool = False,
) -> None:
    """Print post-delete cleanup advisory for slugs removed by --fix.

    When `overview --fix` or `contradiction --fix` deletes an MD file (MD-only
    slug without a matching SoT entry), several downstream artifacts remain
    inconsistent and must be reconciled manually:

      1. `graph/cluster_labels.json` may still carry the deleted slug as a
         label (overview case only — cluster_labels.json is a human-edited
         naming registry, not auto-maintained).
      2. Other wiki pages may still contain `[[<slug>]]` or `[[<slug>|alias]]`
         wikilinks that now resolve to nothing → broken-link lint failures.
      3. Graph/clusters/index must be rebuilt to refresh backlinks and
         catalog tables.

    This helper scans for (1) and (2) and prints a consolidated advisory
    block. It does NOT auto-edit — downstream fixes may be plain-text
    conversion, re-pointing to a surviving sibling, or deliberate removal;
    those are editorial decisions left to the operator.

    Called unconditionally after deletion (both `--yes` bypass and prompt-
    accepted paths) because `confirm_changes()` shows file paths but not
    downstream ripple impact.

    Args:
        deleted_slugs: file stems (without `.md`) that were just unlinked.
        kind: label for the advisory header — e.g., "overview",
              "contradiction theme".
        check_cluster_labels: when True, also scan `graph/cluster_labels.json`
              for orphan label entries (use for overview deletions).
    """
    if not deleted_slugs:
        return

    # (1) cluster_labels.json orphan labels
    orphan_labels: list[str] = []
    if check_cluster_labels:
        try:
            import json
            labels_path = GRAPH / "cluster_labels.json"
            if labels_path.exists():
                data = json.loads(labels_path.read_text(encoding="utf-8"))
                registry_slugs = {l.get("slug") for l in data.get("labels", [])}
                orphan_labels = [s for s in deleted_slugs if s in registry_slugs]
        except (OSError, ValueError, KeyError):
            pass

    # (2) wikilink references across wiki/**/*.md
    ref_counts_by_file: dict[str, int] = {}
    # Build one combined regex for all deleted slugs to scan in one pass
    if WIKI.exists():
        escaped = [re.escape(s) for s in deleted_slugs]
        combined = re.compile(r"\[\[(" + "|".join(escaped) + r")(\|[^\]]+)?\]\]")
        for md_path in WIKI.rglob("*.md"):
            if md_path.name.startswith("_"):
                continue
            try:
                text = md_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            matches = combined.findall(text)
            if matches:
                rel = md_path.relative_to(WIKI.parent).as_posix()
                ref_counts_by_file[rel] = len(matches)

    total_refs = sum(ref_counts_by_file.values())
    if not orphan_labels and total_refs == 0:
        # Clean delete — no downstream advisory needed.
        return

    print()
    print("⚠️  " + "=" * 70)
    print(f"⚠️  Manual cleanup needed after deleting {kind}")
    print("⚠️  " + "-" * 67)

    if orphan_labels:
        print("⚠️  · Labels remaining in graph/cluster_labels.json:")
        for s in orphan_labels:
            print(f"⚠️      - '{s}' (if not removed, the registry ↔ _clusters.json sync breaks)")

    if total_refs:
        total_files = len(ref_counts_by_file)
        print(f"⚠️  · [[<slug>|alias]] wikilinks remaining — {total_refs} total / {total_files} file(s):")
        # Sort by count desc, then path asc
        for rel in sorted(ref_counts_by_file, key=lambda p: (-ref_counts_by_file[p], p)):
            print(f"⚠️      {rel:<60s} {ref_counts_by_file[rel]:>3d}")
        print("⚠️    Remap each reference to plain text or an adjacent hub alias (editor's call)")

    print("⚠️  · Finishing steps:")
    print("⚠️      python tools/build.py graph clusters index")
    print("⚠️      python tools/lint.py graph structure")
    print("⚠️  " + "=" * 70)
    print()


def update_auto_block(content: str, name: str, new_body: str) -> tuple[str, bool]:
    """Replace the body inside <!-- AUTO:name BEGIN --> ... <!-- AUTO:name END -->.

    Returns (updated_content, found). If markers absent, returns content unchanged
    with found=False — caller decides whether to skip, warn, or create a new file.
    new_body is inserted verbatim between marker lines (no added surrounding blanks).
    """
    pattern = re.compile(
        rf"<!--\s*AUTO:{re.escape(name)}\s*BEGIN\s*-->.*?<!--\s*AUTO:{re.escape(name)}\s*END\s*-->",
        re.DOTALL,
    )
    if not pattern.search(content):
        return content, False
    replacement = f"<!-- AUTO:{name} BEGIN -->\n{new_body}\n<!-- AUTO:{name} END -->"
    # Pass the replacement through a lambda so re.sub treats new_body as a
    # literal — a `\1`/`\g<0>` sequence in catalog content (e.g. a Windows
    # path or title fragment) would otherwise be parsed as a group reference
    # and crash the build (re.PatternError) or silently corrupt the block.
    return pattern.sub(lambda _m: replacement, content), True
