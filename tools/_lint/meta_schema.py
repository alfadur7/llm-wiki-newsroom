"""Meta-doc schema lint — CLAUDE.md + .claude/commands/*.md + .claude/layers/*.md
conventions.

Paired with content_schema.py (wiki/overviews + wiki/contradictions). Where
content_schema verifies L2-3 content files against their documented formats,
this module verifies the meta-docs that document those formats comply with
their own conventions.

Concerns bundled here because all target meta-docs, all are read-only
(no --fix), and all run in <1 second — no benefit from separate CLI surfaces:

  INTEGRITY — CLAUDE.md self-consistency:
    1. Anchor links `[text](#anchor)` resolve to an existing heading.
    2. Backtick-wrapped file paths (wiki/*, tools/*, graph/*, .claude/*,
       wiki-export/*) exist on disk, skipping placeholders and code blocks.
    3. Every `/wiki-<name>` slash command mentioned in CLAUDE.md has a
       matching `.claude/commands/wiki-<name>.md` definition file.

  LANGUAGE — meta-doc section headers must be English (CLAUDE.md +
             .claude/commands/*.md).
    Rule rationale: Korean section headers weaken the "write the body in Korean"
    output rule for Claude.

  FLAT-PATH guard — stale `python tools/lint.py <flat-subcmd>` invocations
                    must migrate to the post-refactor `<group> [<sub>]` form.

  RESERVED FILENAME — wiki/**/*.md basenames must not case-fold to reserved
                      meta-doc names (CLAUDE.md, README.md). On case-insensitive
                      filesystems (Windows NTFS, default macOS) such files
                      shadow the harness's reserved lookup and get injected
                      as project instructions. Discovered 2026-05-01 via
                      wiki/entities/Claude.md case-folding to CLAUDE.md.

  LOG MONOTONICITY — log.md entries must appear oldest-first with
                     date(entry[i+1]) >= date(entry[i]). The `grep ... | tail -10`
                     idiom in the Log Format spec only works under this
                     convention. Claude sessions occasionally misplaced new
                     entries at the top before this guard existed; a one-off
                     sort restored order (2026-04-21) and this check prevents
                     re-drift. Advisory by default — no auto-sort here, since
                     rewriting audit log ordering is a sensitive operation best
                     kept under explicit human/Claude review.

  HOOK BASH-PREFIX — every settings(.local).json hook `command` that runs a
                     `.sh` script must invoke it through a leading `bash`
                     token. Windows shells cannot execute a bare `.sh` path,
                     so a hook registered without the `bash ` prefix silently
                     no-ops and its guard/advisory never fires — an invisible
                     failure mode. See .claude/policies/platform.md "Hook Execution Environment (Windows)".

  HOOK ADVISORY CHANNEL — a non-blocking hook (no `exit 2` path) that writes
                     its message to stderr never reaches Claude: stderr on
                     exit 0 is shown to the user only. Advisories must emit the
                     message as stdout JSON `hookSpecificOutput.additionalContext`.
                     Blocking guards (with an `exit 2` path) are exempt — exit-2
                     stderr IS delivered to Claude. See platform.md "Hook Execution Environment (Windows)".

  HOOK PYTHON UTF-8 — every hook `python3` invocation must force UTF-8 mode
                     (`PYTHONUTF8=1`). On Windows python3 decodes stdin/stdout
                     as cp949, mangling a hook's Korean output into lone
                     surrogates that poison the session JSON (400) — an
                     unrecoverable crash. See platform.md "Hook Execution Environment (Windows)".

  CRAFT-SKILL INTEGRITY — the craft skill chain (`.claude/skills/<skill>/`
                     {criteria.json, checks.py} + `.claude/layers/_manifest.json`
                     + `.claude/layers/*.md`) must stay referentially closed:
                     every craft dot-id (jrn/con/enc/cit) referenced by the
                     manifest (checks · bundle produces · roster) or by a layers
                     guide must be defined in some skill's criteria.json; every
                     bundle `fn` and every judge=A `algorithm` must be a function
                     in that skill's checks.py; each criterion's judge schema
                     must be well-formed (A → comparator + default_threshold,
                     M → pass_condition). A dangling dot-id silently drops a
                     criterion from evaluation.

  STALE GUIDE REF — pre-merge guide filenames `<x>-authoring.md` /
                     `<x>-rubric.md` (now merged into .claude/layers/<type>.md)
                     must not survive in code or .claude docs (log.md is
                     append-only and exempt). A stale reference points readers
                     at a file that no longer exists.

  OBSIDIAN LINK SAFETY — generated drill-down meta (wiki/index.md +
                     wiki/sources/_catalog*.md) link display text must not carry
                     a raw `[`/`]` (Obsidian Live Preview breaks the link even
                     when escaped — use lenticular 【】 via safe_link_text) or end
                     with a `\\` (escapes the closing `]`). Regression guard for
                     the build pipeline's bracket/quote sanitization.

  NESTED WIKILINK — authored narrative (wiki/overview(s), wiki/contradiction(s),
                     hub pages, syntheses, trails) must not nest `[[` inside a
                     wikilink alias. Obsidian closes the outer link at the first
                     `]]`, rendering a truncated alias + stray `]]`. Fix: flatten
                     the inner link to plain text. sources/ and `_`-prefixed
                     generated files are out of scope.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import CLUSTERS_JSON, REPO_ROOT as ROOT, WIKI as WIKI_DIR, read_text_cached  # noqa: E402

CLAUDE_MD = ROOT / "CLAUDE.md"
COMMANDS_DIR = ROOT / ".claude" / "commands"
LOG_MD = ROOT / "log.md"
SETTINGS_FILES = (
    ROOT / ".claude" / "settings.json",
    ROOT / ".claude" / "settings.local.json",
)
HOOKS_DIR = ROOT / ".claude" / "hooks"

LOG_HEADER_RE = re.compile(r"^## \[(\d{4}-\d{2}-\d{2})\]", re.MULTILINE)

# INTEGRITY patterns
HEADING_RE = re.compile(r'^(#{1,6})\s+(.+?)\s*$')
ANCHOR_LINK_RE = re.compile(r'\]\(#([\w.-]+)\)')
BACKTICK_RE = re.compile(r'`([^`\n]+)`')
SLASH_CMD_RE = re.compile(r'/wiki-[a-z][\w-]*')
PATH_PREFIXES = ("wiki/", "tools/", "graph/", "raw/", ".claude/", "wiki-export/")
PLACEHOLDER_MARKERS = ("<", ">", "*", "...", "{", "}", "YYYY", "MM-", "-DD", "[a-z]")

# LANGUAGE patterns
KOREAN_RE = re.compile(r"[가-힣]")
HEADER_WHITELIST: set[str] = set()

# FLAT-PATH guard — prevents reintroduction of pre-refactor `python tools/lint.py <flat-subcmd>`
# invocations. After the 2026-04-19 group refactor the correct form is
# `python tools/lint.py <group> [<sub>]` where group ∈ {all,graph,hub,meta,overview,contradiction}.
# `overview` and `contradiction` are legitimate group names; they stay allowed.
FLAT_LINT_RE = re.compile(
    r"python tools/lint\.py "
    r"(?!all\b|graph\b|hub\b|meta\b|overview\b|contradiction\b|suggestions --)"
    r"(structure|orphans|clusters|speakers|suggestions|meta-schema|content-schema)\b"
)

# RESERVED meta-doc filenames. On case-insensitive filesystems (Windows NTFS,
# default macOS), a wiki/**/*.md file whose basename case-folds to one of these
# silently shadows the reserved meta-doc lookup — Claude Code treats the entity
# page as a project-instruction CLAUDE.md, injecting its content into every
# session. Discovered 2026-05-01 when wiki/entities/Claude.md (legit Claude LLM
# entity) was case-folded to CLAUDE.md by harness traversal of wiki/entities/.
RESERVED_META_FILENAMES = frozenset({"claude.md", "readme.md"})

# CRAFT-SKILL INTEGRITY patterns
SKILLS_DIR = ROOT / ".claude" / "skills"
MANIFEST_JSON = ROOT / ".claude" / "layers" / "_manifest.json"
LAYERS_DIR = ROOT / ".claude" / "layers"
CRAFT_PREFIXES = ("jrn", "con", "enc", "cit")
# Dot-ids appearing in layers prose. struct.*/house.* live in the layers
# structural/house-style sections (no craft skill) so only craft prefixes are
# cross-checked against criteria.json.
DOT_ID_RE = re.compile(r"\b((?:jrn|con|enc|cit|struct|house)\.[a-z][a-z0-9-]+)\b")
# Pre-merge guide filenames; literal split so the regex source itself is not a hit.
STALE_GUIDE_RE = re.compile(r"[\w-]+-(?:authoring|" + "rubric)\\.md")

# OBSIDIAN LINK SAFETY — display text of an inline Markdown link, captured up to
# the first `](`. Non-greedy match extends past any `]` not followed by `(`,
# so the group holds the full intended display text.
MD_LINK_DISPLAY_RE = re.compile(r"\[(.*?)\]\(")

# NESTED WIKILINK — an outer `[[target|alias]]` whose alias contains another
# `[[`. Obsidian cannot nest wikilinks: it closes the outer link at the first
# `]]`, leaving a truncated alias and a stray `]]`. Authored narrative content
# (overviews/contradictions/hubs) is the only place this arises.
NESTED_WIKILINK_RE = re.compile(r"\[\[[^\[\]|]+\|[^\]\[]*\[\[")


# ---------- INTEGRITY helpers (CLAUDE.md self-consistency) ----------


def _to_anchor(heading: str) -> str:
    s = heading.lower()
    s = re.sub(r'[^\w\s-]', '', s)
    s = s.replace(' ', '-')
    return s


def _iter_non_fenced_lines(text: str):
    in_fence = False
    for i, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        yield i, line


def _extract_headings(text: str) -> set[str]:
    anchors: set[str] = set()
    for _, line in _iter_non_fenced_lines(text):
        m = HEADING_RE.match(line)
        if m:
            anchors.add(_to_anchor(m.group(2)))
    return anchors


def _check_anchors(text: str) -> list[str]:
    headings = _extract_headings(text)
    broken: list[str] = []
    for i, line in _iter_non_fenced_lines(text):
        for anchor in ANCHOR_LINK_RE.findall(line):
            if anchor not in headings:
                broken.append(f"  L{i}: #{anchor} — no matching heading")
    return broken


def _is_placeholder(path: str) -> bool:
    return any(m in path for m in PLACEHOLDER_MARKERS)


def _check_file_refs(text: str) -> list[str]:
    seen: set[tuple[int, str]] = set()
    missing: list[str] = []
    for i, line in _iter_non_fenced_lines(text):
        for raw in BACKTICK_RE.findall(line):
            # Inline code may be a command invocation with args (e.g. "tools/build.py contradictions")
            # Take only the first whitespace-delimited token as the candidate path.
            path = raw.strip().split()[0] if raw.strip() else ""
            if not any(path.startswith(p) for p in PATH_PREFIXES):
                continue
            if _is_placeholder(path):
                continue
            path = path.rstrip(".,;:)")
            if (i, path) in seen:
                continue
            seen.add((i, path))
            full = ROOT / path
            if not full.exists():
                missing.append(f"  L{i}: `{path}` — does not exist")
    return missing


def _check_slash_commands(text: str) -> list[str]:
    mentioned = {m.lstrip("/") for m in SLASH_CMD_RE.findall(text)}
    existing = {p.stem for p in COMMANDS_DIR.glob("*.md")} if COMMANDS_DIR.exists() else set()
    missing: list[str] = []
    for cmd in sorted(mentioned):
        if cmd not in existing:
            missing.append(f"  /{cmd} — .claude/commands/{cmd}.md not found")
    return missing


# ---------- ROSTER COMPLETENESS (forward index — every disk file is listed) ----------
#
# `_check_file_refs` is the *reverse* direction (every referenced path exists on
# disk). The *forward* direction — every disk file is enumerated in its folder's
# index — was previously unchecked, so a new file under .claude/operations/ or
# .claude/policies/ could land without an entry in the CLAUDE.md "Instruction
# Locations" or the folder README and drift silently. Scope is limited to
# operations + policies, the
# two folders where this drift was actually observed (CLAUDE.md listed only 1/5
# operations files; no-plan-bloat.md was absent from policies). agents/commands/
# layers are intentionally out of scope.
#
# Section header per folder in CLAUDE.md, e.g. "### `.claude/policies/` — ...".
_CLAUDE_SECTION_RE_TMPL = r"^###\s+`\.claude/{folder}/`.*?(?=^###\s|\Z)"
# A `<name>.md` token wrapped in backticks (CLAUDE.md bullets) or a
# `[<name>.md](...)` markdown link (README index table).
_MD_BASENAME_RE = re.compile(r"`([\w.-]+\.md)`|\[([\w.-]+\.md)\]")

# Folders whose disk roster must be fully enumerated. README.md is the index
# itself (and is excluded from the roster it lists). has_readme=False means the
# folder has no README, so only the CLAUDE.md list is cross-checked.
ROSTER_FOLDERS = (
    ("operations", False),
    ("policies", True),
)


def _disk_roster(folder: str) -> set[str]:
    """`*.md` basenames on disk under .claude/<folder>/, excluding README.md."""
    d = ROOT / ".claude" / folder
    if not d.exists():
        return set()
    return {
        p.name
        for p in d.glob("*.md")
        if p.name.lower() != "readme.md"
    }


def _md_basenames(text: str) -> set[str]:
    """All `<name>.md` basenames referenced in `text` (backtick or md-link form)."""
    out: set[str] = set()
    for bt, link in _MD_BASENAME_RE.findall(text):
        name = bt or link
        if name:
            out.add(name)
    return out


def _claude_section_basenames(claude_text: str, folder: str) -> set[str] | None:
    """Basenames listed under the `.claude/<folder>/` section in CLAUDE.md.

    Returns None when the section is absent (a separate, louder failure than a
    partial roster — the folder lost its CLAUDE.md entry entirely)."""
    sec_re = re.compile(
        _CLAUDE_SECTION_RE_TMPL.format(folder=re.escape(folder)),
        re.MULTILINE | re.DOTALL,
    )
    m = sec_re.search(claude_text)
    if not m:
        return None
    return _md_basenames(m.group(0))


def _check_roster_completeness(claude_text: str) -> list[str]:
    """Verify every disk file under operations/ + policies/ is enumerated in
    the CLAUDE.md "Instruction Locations" and (where present) the folder README index.

    Reports one line per (file, missing-index) gap so the operator sees both
    the orphaned file and which list it fell out of.
    """
    issues: list[str] = []
    for folder, has_readme in ROSTER_FOLDERS:
        disk = _disk_roster(folder)
        if not disk:
            continue

        claude_listed = _claude_section_basenames(claude_text, folder)
        if claude_listed is None:
            issues.append(
                f"  CLAUDE.md: `.claude/{folder}/` section missing entirely "
                f"({len(disk)} file(s) on disk unlisted)"
            )
        else:
            for name in sorted(disk - claude_listed):
                issues.append(
                    f"  .claude/{folder}/{name}: not in the CLAUDE.md "
                    f"\"Instruction Locations\" list (.claude/{folder}/ section)"
                )

        if has_readme:
            readme = ROOT / ".claude" / folder / "README.md"
            if not readme.exists():
                issues.append(f"  .claude/{folder}/README.md: missing (index file expected)")
                continue
            readme_listed = _md_basenames(
                read_text_cached(readme)
            )
            for name in sorted(disk - readme_listed):
                issues.append(
                    f"  .claude/{folder}/{name}: not in .claude/{folder}/README.md index"
                )
    return issues


# ---------- LANGUAGE helpers (Korean header guard) ----------


# ---------- RUBRIC (Part 1↔Part 2 mirror) monitoring removed ----------
# After the craft extraction (Phase 4), the overview·contradiction Rubric tables
# were reduced to the manifest roster + skill criteria.json, so the Part1/Part2
# mirror duplication vanished → there is no longer a drift/header-count target to
# monitor. The completion counts are owned by `_manifest_counts` (roster computation).


def _check_stale_cluster_slugs() -> list[str]:
    """Detect stale cluster slug literals in CLAUDE.md + .claude/commands/*.md.

    Catches `_catalog-<slug>.md` references whose `<slug>` is not in the
    current `graph/_clusters.json::clusters[].slug` set. After cluster
    boundaries shift through ingest accumulation, slug enumeration literals
    in docs become stale silently — Claude reading the doc will pass an
    invalid slug to /wiki-lint or /wiki-export commands and the lint/build
    will reject it. This detector flags each stale literal with location.

    Placeholder forms (`<cluster-slug>`, `<slug>`) are ignored so the
    Index Format template in CLAUDE.md doesn't false-positive.
    """
    issues: list[str] = []
    if not CLUSTERS_JSON.exists():
        return issues
    try:
        data = json.loads(CLUSTERS_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return issues
    current = {c.get("slug") for c in data.get("clusters", []) if c.get("slug")}
    if not current:
        return issues

    targets: list[Path] = [CLAUDE_MD]
    if COMMANDS_DIR.exists():
        targets.extend(sorted(COMMANDS_DIR.glob("*.md")))

    pat = re.compile(r"_catalog-([a-z][a-z0-9-]+)\.md")
    for path in targets:
        try:
            text = read_text_cached(path)
        except OSError:
            continue
        for m in pat.finditer(text):
            slug = m.group(1)
            # Skip the `_catalog-slug.md` template literal — `<...>`
            # placeholders never match the regex ([a-z] first char).
            if slug == "slug":
                continue
            if slug not in current:
                line = text[:m.start()].count("\n") + 1
                rel = path.relative_to(ROOT).as_posix()
                issues.append(
                    f"{rel}:{line}: stale cluster slug `_catalog-{slug}.md` — "
                    f"not in graph/_clusters.json::clusters[].slug"
                )
    return issues


def _check_language_in_file(path: Path) -> list[tuple[int, str]]:
    violations: list[tuple[int, str]] = []
    text = read_text_cached(path)
    for i, line in _iter_non_fenced_lines(text):
        m = HEADING_RE.match(line)
        if not m:
            continue
        header = m.group(2).strip()
        if header in HEADER_WHITELIST:
            continue
        if KOREAN_RE.search(header):
            violations.append((i, line.rstrip()))
    return violations


CLAUDE_VOICE_PATTERNS = [
    ("decision option name", re.compile(r"옵션\s*[A-Z][+]?(?!\s*입장)")),
    ("reinforcement counter", re.compile(r"(보강|Reinforcement)\s*\d+", re.IGNORECASE)),
    ("introduction timestamp", re.compile(r"\d{4}-\d{2}-\d{2}\s*(도입|시점|적용)")),
    ("external case reference", re.compile(
        r"(Wikipedia|ProCon|BERTopic|Wikidata|Stack\s*Overflow|Kialo)[^\n]{0,80}?(등가|모델|model)",
        re.IGNORECASE,
    )),
    ("benchmark absorption narrative", re.compile(r"외부 벤치마크\s*\d+\s*/\s*\d+")),
    ("changelog section header", re.compile(
        r"^#{2,4}\s*(Changelog|변경\s*이력|변경\s*사항|Change\s*Log)\s*$",
        re.IGNORECASE | re.MULTILINE,
    )),
    ("recurrence prevention narrative", re.compile(r"재발\s*(방지|회피)")),
]

# Self-skip — the policy files list antipatterns by example, not as violations.
CLAUDE_VOICE_SELF_SKIP = {
    ".claude/policies/claude-guideline-voice.md",
    ".claude/policies/language.md",
}


def _check_claude_voice_violations() -> list[str]:
    """Surface decision-history, external-benchmark reference, and changelog-
    section antipatterns across Claude guideline SoT files. Scope covers
    `.claude/commands/*.md`, `.claude/agents/*.md`, `.claude/policies/*.md`,
    `.claude/layers/*.md`, `.claude/operations/*.md`, `.claude/skills/*/SKILL.md`,
    and `CLAUDE.md` — wiki/ is content territory and is unaffected.
    """
    violations: list[str] = []
    targets: list[Path] = [CLAUDE_MD]
    if COMMANDS_DIR.exists():
        targets.extend(sorted(COMMANDS_DIR.glob("*.md")))
    for sub in ("agents", "policies", "layers", "operations"):
        d = ROOT / ".claude" / sub
        if d.exists():
            targets.extend(sorted(d.glob("*.md")))
    # craft skill SKILL.md — the model-context prose is subject to the same voice convention.
    skills_dir = ROOT / ".claude" / "skills"
    if skills_dir.exists():
        targets.extend(sorted(skills_dir.glob("*/*.md")))

    for path in targets:
        rel = path.relative_to(ROOT).as_posix()
        if rel in CLAUDE_VOICE_SELF_SKIP:
            continue
        try:
            text = read_text_cached(path)
        except OSError:
            continue
        for i, line in _iter_non_fenced_lines(text):
            for label, pat in CLAUDE_VOICE_PATTERNS:
                m = pat.search(line)
                if m:
                    violations.append(
                        f"{rel}:{i}: [{label}] '{m.group(0).strip()}'"
                    )
                    break
    return violations


def _check_flat_lint_paths() -> list[str]:
    """Flag any `python tools/lint.py <flat-subcmd>` reference outside the
    post-refactor group form. Scans meta docs, guides, README, and tools/.

    The refactor collapsed flat subcommands under groups; references to the
    old form in docs/scripts are drift that will confuse future readers and
    silently fail once flat paths are removed from the CLI.
    """
    violations: list[str] = []
    targets: list[Path] = []
    for name in ("CLAUDE.md", "README.md"):
        p = ROOT / name
        if p.exists():
            targets.append(p)
    for sub in ("commands", "agents", "layers"):
        d = ROOT / ".claude" / sub
        if d.exists():
            targets.extend(sorted(d.glob("*.md")))
    tools_dir = ROOT / "tools"
    if tools_dir.exists():
        targets.extend(sorted(tools_dir.rglob("*.py")))

    self_path = Path(__file__).resolve()
    for path in targets:
        if path.resolve() == self_path:
            continue  # don't flag the regex declaration in this file itself
        try:
            text = read_text_cached(path)
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), start=1):
            for m in FLAT_LINT_RE.finditer(line):
                rel = path.relative_to(ROOT).as_posix()
                violations.append(
                    f"{rel}:{i}: flat `{m.group(0).strip()}` — "
                    f"use `python tools/lint.py <group> <sub>` form"
                )
    return violations


def _check_hook_bash_prefix() -> list[str]:
    """Verify every settings(.local).json hook command that runs a `.sh`
    script is invoked through a leading `bash` token.

    Windows shells cannot execute a bare `.sh` path, so a hook registered as
    `.claude/hooks/foo.sh` (without the `bash ` prefix) silently no-ops — the
    guard/advisory never fires and the failure is invisible. Requiring the
    prefix keeps hooks portable across the project's shells.

    Returns one violation string per offending command, plus a parse-error
    line if a settings file exists but cannot be read as JSON.
    """
    violations: list[str] = []
    for path in SETTINGS_FILES:
        if not path.exists():
            continue
        rel = path.relative_to(ROOT).as_posix()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            violations.append(f"{rel}: unreadable as JSON ({e})")
            continue
        hooks = data.get("hooks", {})
        if not isinstance(hooks, dict):
            continue
        for event, groups in hooks.items():
            if not isinstance(groups, list):
                continue
            for group in groups:
                matcher = group.get("matcher", "?")
                for hook in group.get("hooks", []):
                    if hook.get("type") != "command":
                        continue
                    cmd = (hook.get("command") or "").strip()
                    if ".sh" not in cmd:
                        continue
                    first = cmd.split()[0] if cmd else ""
                    if first != "bash":
                        violations.append(
                            f"{rel}: {event}/{matcher} command `{cmd}` runs a "
                            f".sh script without leading `bash` — bare .sh "
                            f"silently no-ops on Windows shells."
                        )
    return violations


def _check_hook_advisory_channel() -> list[str]:
    """Flag advisory hooks that write to stderr but cannot reach Claude.

    On exit 0, a hook's stderr is shown to the user only — it never enters
    Claude's context. So a non-blocking advisory built as `cat >&2 ... ; exit 0`
    (or `print(..., file=sys.stderr)`) silently no-ops as far as Claude is
    concerned. The fix is to emit the message as stdout JSON
    `hookSpecificOutput.additionalContext`.

    Blocking guards are exempt: a hook with an `exit 2` path uses stderr
    legitimately because exit-2 stderr IS delivered to Claude as feedback.

    Heuristic per hook file:
      flag if (writes a message to stderr) AND (no exit-2 path) AND
              (no `additionalContext`).
    """
    violations: list[str] = []
    if not HOOKS_DIR.exists():
        return violations
    for path in sorted(HOOKS_DIR.glob("*.sh")) + sorted(HOOKS_DIR.glob("*.py")):
        text = read_text_cached(path)
        rel = path.relative_to(ROOT).as_posix()
        if path.suffix == ".sh":
            has_stderr_msg = ">&2" in text
            has_block = re.search(r"\bexit\s+2\b", text) is not None
        else:
            has_stderr_msg = "file=sys.stderr" in text
            has_block = re.search(r"(sys\.exit\(2\)|SystemExit\(2\)|return\s+2\b)", text) is not None
        has_additional_context = "additionalContext" in text
        if has_stderr_msg and not has_block and not has_additional_context:
            violations.append(
                f"{rel}: non-blocking hook writes to stderr without "
                f"`additionalContext` — advisory never reaches Claude on exit 0. "
                f"Emit stdout JSON hookSpecificOutput.additionalContext instead."
            )
    return violations


def _check_hook_python_utf8() -> list[str]:
    """Flag hook `python3` invocations that do not force UTF-8 mode.

    On Windows, `python3` decodes stdin/stdout with the locale code page
    (cp949), not UTF-8. A hook that pipes Korean through `python3`
    (`printf '%s' "$MSG" | python3 -c '... sys.stdin.read()'`) then mangles
    the UTF-8 bytes into lone surrogates, which poison the session's JSON
    request body (`400 invalid high surrogate`) — an unrecoverable crash.
    Every hook `python3` call must opt into UTF-8 via `PYTHONUTF8=1`
    (or `PYTHONIOENCODING=utf-8`, or the `-X utf8` flag).

    Heuristic per line: flag a `python3` token unless the same line carries
    `PYTHONUTF8`, `PYTHONIOENCODING`, or a `-X utf8` flag.
    """
    violations: list[str] = []
    if not HOOKS_DIR.exists():
        return violations
    for path in sorted(HOOKS_DIR.glob("*.sh")):
        rel = path.relative_to(ROOT).as_posix()
        for lineno, line in enumerate(
            read_text_cached(path).splitlines(), 1
        ):
            if "python3" not in line:
                continue
            if re.search(r"PYTHONUTF8|PYTHONIOENCODING|-X\s*utf8", line):
                continue
            violations.append(
                f"{rel}:{lineno}: `python3` invoked without UTF-8 mode — "
                f"prefix with `PYTHONUTF8=1` (cp949 mis-decode corrupts Korean "
                f"output into lone surrogates → session JSON 400)."
            )
    return violations


_SHARED_REGEX_DEF_RE = re.compile(r"^(?:FRONTMATTER|WIKILINK|AUTO)\w*\s*=\s*re\.compile")


def _check_shared_regex_hoisting() -> list[str]:
    """Flag per-module redefinitions of the shared regex families.

    `_lib` is the single SoT for the `FRONTMATTER*`·`WIKILINK*`·`AUTO*` regexes —
    per-module copies have diverged into variants and spread the same bug across
    several files before (code-audit carry-forward: hoisting the shared helper
    closes the bug class). If a module-specific variant is needed, add it to `_lib`
    under a distinct name and import it. Intentional local variants with an
    underscore prefix (e.g. `_FIRST_WIKILINK_RE`) or a different prefix naming
    (`UNALIASED_*`·`HYBRID_*`) are not checked.
    """
    violations: list[str] = []
    tools_dir = ROOT / "tools"
    if not tools_dir.exists():
        return violations
    for path in sorted(tools_dir.rglob("*.py")):
        if path.name == "_lib.py" or "__pycache__" in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        for lineno, line in enumerate(
            read_text_cached(path).splitlines(), 1
        ):
            if _SHARED_REGEX_DEF_RE.match(line):
                violations.append(
                    f"{rel}:{lineno}: `{line.strip()[:60]}` — import the "
                    f"FRONTMATTER*/WIKILINK*/AUTO* regexes from the single _lib "
                    f"definition (no module redefinition)."
                )
    return violations


# ---------- CRAFT-SKILL INTEGRITY helpers ----------


def _is_craft_dot(cid: str) -> bool:
    return cid.split(".", 1)[0] in CRAFT_PREFIXES


def _check_craft_skill_integrity() -> list[str]:
    """Verify the craft skill chain stays referentially closed.

    Loads every `.claude/skills/<skill>/criteria.json` + `checks.py` (AST,
    no import side effects) and the manifest, then asserts:
      - manifest checks/bundle-produces/roster craft dot-ids ∈ some criteria.json
      - bundle `fn` and judge=A `algorithm` ∈ that skill's checks.py functions
      - judge schema well-formed (A → comparator+default_threshold, M → pass_condition)
      - layers/*.md craft dot-ids ∈ some criteria.json
    Returns one violation string per gap. Empty list (and silent return) if the
    skills/manifest scaffold is absent — this lint is a no-op outside this wiki.
    """
    import ast

    issues: list[str] = []
    if not (SKILLS_DIR.exists() and MANIFEST_JSON.exists()):
        return issues

    all_ids: set[str] = set()
    checks_funcs: dict[str, set[str]] = {}
    for skdir in sorted(SKILLS_DIR.glob("*")):
        if not skdir.is_dir():
            continue
        cj, ck = skdir / "criteria.json", skdir / "checks.py"
        if not cj.exists():
            continue
        try:
            crit = json.loads(cj.read_text(encoding="utf-8")).get("criteria", {})
        except (OSError, json.JSONDecodeError) as e:
            issues.append(f".claude/skills/{skdir.name}/criteria.json: unreadable ({e})")
            continue
        all_ids.update(crit.keys())
        funcs: set[str] = set()
        if ck.exists():
            try:
                tree = ast.parse(ck.read_text(encoding="utf-8"))
                funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
            except SyntaxError as e:
                issues.append(f".claude/skills/{skdir.name}/checks.py: syntax error ({e})")
        checks_funcs[skdir.name] = funcs
        for cid, cdef in crit.items():
            j = cdef.get("judge")
            if j == "A":
                if "comparator" not in cdef or "default_threshold" not in cdef:
                    issues.append(f"{skdir.name}:{cid}: judge=A missing comparator/default_threshold")
                algo = cdef.get("algorithm")
                if algo and algo not in funcs:
                    issues.append(f"{skdir.name}:{cid}: algorithm `{algo}` not defined in checks.py")
            elif j == "M":
                if "pass_condition" not in cdef:
                    issues.append(f"{skdir.name}:{cid}: judge=M missing pass_condition")
            else:
                issues.append(f"{skdir.name}:{cid}: judge must be 'A' or 'M' (got {j!r})")

    try:
        manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        issues.append(f".claude/layers/_manifest.json: unreadable ({e})")
        return issues

    for ct, blk in manifest.items():
        if ct.startswith("_") or not isinstance(blk, dict):
            continue
        for cid in blk.get("checks", {}):
            if _is_craft_dot(cid) and cid not in all_ids:
                issues.append(f"manifest[{ct}].checks: `{cid}` not in any skill criteria.json")
        for sk, bdef in blk.get("bundles", {}).items():
            fn = bdef.get("fn")
            if fn and fn not in checks_funcs.get(sk, set()):
                issues.append(f"manifest[{ct}].bundles.{sk}: fn `{fn}` not in {sk}/checks.py")
            for cid in bdef.get("produces", []):
                if _is_craft_dot(cid) and cid not in all_ids:
                    issues.append(f"manifest[{ct}].bundles.{sk}.produces: `{cid}` not in skill criteria.json")
        ros = blk.get("roster", {})
        for cid in ros.get("required", []) + ros.get("optional", []):
            if _is_craft_dot(cid) and cid not in all_ids:
                issues.append(f"manifest[{ct}].roster: `{cid}` not in any skill criteria.json")

    for p in sorted(LAYERS_DIR.glob("*.md")):
        try:
            text = read_text_cached(p)
        except OSError:
            continue
        rel = p.relative_to(ROOT).as_posix()
        for i, line in enumerate(text.splitlines(), 1):
            for tok in set(DOT_ID_RE.findall(line)):
                if _is_craft_dot(tok) and tok not in all_ids:
                    issues.append(f"{rel}:{i}: craft dot-id `{tok}` not in any skill criteria.json")
    return issues


def _check_stale_guide_refs() -> list[str]:
    """Flag pre-merge guide filenames (`<x>-authoring.md` / `<x>-rubric.md`)
    in code and .claude docs. Those guides were merged into
    `.claude/layers/<content-type>.md`; a surviving reference points readers at
    a file that no longer exists. log.md is append-only (historical
    filenames persist there legitimately) and is not scanned.
    """
    issues: list[str] = []
    targets: list[Path] = []
    for sub in ("commands", "agents", "layers", "skills"):
        d = ROOT / ".claude" / sub
        if d.exists():
            targets.extend(sorted(d.rglob("*.md")))
    tools_dir = ROOT / "tools"
    if tools_dir.exists():
        targets.extend(sorted(tools_dir.rglob("*.py")))

    self_path = Path(__file__).resolve()
    for path in targets:
        if path.resolve() == self_path:
            continue  # the regex declaration in this file is not a real reference
        try:
            text = read_text_cached(path)
        except OSError:
            continue
        rel = path.relative_to(ROOT).as_posix()
        for i, line in enumerate(text.splitlines(), 1):
            for m in STALE_GUIDE_RE.finditer(line):
                issues.append(
                    f"{rel}:{i}: stale guide ref `{m.group(0)}` — "
                    f"merged into .claude/layers/<content-type>.md"
                )
    return issues


def _check_obsidian_link_safety() -> list[str]:
    """Flag link display text that breaks Obsidian rendering in generated meta.

    Obsidian Live Preview breaks an inline `[display](target)` link when the
    display text contains a raw `[`/`]` (even backslash-escaped) or ends with a
    backslash (which escapes the closing `]`). The build pipeline keeps these
    clean — `safe_link_text()` substitutes lenticular brackets and
    `parse_frontmatter` unescapes YAML `\\"` so a quoted title never leaves a
    dangling `\\`. This guard catches a regression that reintroduces either.

    Scoped to the auto-generated drill-down meta (wiki/index.md +
    wiki/sources/_catalog*.md) where the failure originated and would recur.
    """
    issues: list[str] = []
    targets: list[Path] = []
    idx = WIKI_DIR / "index.md"
    if idx.exists():
        targets.append(idx)
    sources_dir = WIKI_DIR / "sources"
    if sources_dir.exists():
        targets.extend(sorted(sources_dir.glob("_catalog*.md")))

    for path in targets:
        try:
            text = read_text_cached(path)
        except OSError:
            continue
        rel = path.relative_to(ROOT).as_posix()
        for i, line in enumerate(text.splitlines(), 1):
            for disp in MD_LINK_DISPLAY_RE.findall(line):
                if "[" in disp or "]" in disp:
                    issues.append(
                        f"{rel}:{i}: raw bracket in link display text `{disp}` — "
                        f"use safe_link_text() (lenticular 【】)"
                    )
                elif disp.endswith("\\"):
                    issues.append(
                        f"{rel}:{i}: link display text ends with `\\` (`{disp}`) — "
                        f"escapes the closing `]` and breaks the link"
                    )
    return issues


def _check_nested_wikilinks() -> list[str]:
    """Flag wikilinks whose alias contains a nested `[[` in authored content.

    Obsidian does not support nesting wikilinks: `[[A|text [[B]] more]]` closes
    the outer link at the first `]]`, rendering a truncated alias plus a stray
    `]]`. Catalogs use Markdown links (covered by _check_obsidian_link_safety),
    so this scans the authored narrative surface — wiki/overview(s) +
    wiki/contradiction(s) + hub pages (entities/concepts/timelines) + syntheses
    + trails — skipping sources/ (article clippings) and `_`-prefixed
    generated/index files. The flatten fix: drop the inner `[[ ]]`, keep the
    entity name as plain alias text.
    """
    issues: list[str] = []
    if not WIKI_DIR.exists():
        return issues
    skip_dirs = {"sources"}
    for md in WIKI_DIR.rglob("*.md"):
        if md.name.startswith("_") or md.relative_to(WIKI_DIR).parts[0] in skip_dirs:
            continue
        try:
            text = read_text_cached(md)
        except OSError:
            continue
        rel = md.relative_to(ROOT).as_posix()
        for i, line in enumerate(text.splitlines(), 1):
            for m in NESTED_WIKILINK_RE.finditer(line):
                issues.append(f"{rel}:{i}: nested wikilink in alias `{m.group(0)[:50]}…`")
    return issues


# ---------- entrypoint ----------


def _check_reserved_filename_collisions() -> list[str]:
    """Detect wiki/**/*.md files whose basename case-folds to a reserved
    meta-doc filename (CLAUDE.md, README.md). On case-insensitive filesystems
    (Windows NTFS, default macOS) such files shadow the reserved lookup and
    get injected as harness project instructions, leaking entity content into
    every Claude Code session.

    Returns one violation string per offending path with a rename hint.
    """
    violations: list[str] = []
    if not WIKI_DIR.exists():
        return violations
    for md in WIKI_DIR.rglob("*.md"):
        if md.name.lower() in RESERVED_META_FILENAMES:
            rel = md.relative_to(ROOT).as_posix()
            reserved = md.name.lower()
            violations.append(
                f"{rel}: case-folds to reserved `{reserved.upper()}` — "
                f"rename to disambiguate (e.g., add a suffix like LLM, _Anthropic)."
            )
    return violations


def _check_log_monotonicity() -> list[str]:
    """Verify log.md headers are chronologically ascending.

    Empty list on pass. Each violation cites both offending header lines
    with their dates so the operator can locate the stray entry quickly.
    Returns empty list if log.md is missing (not an error — logs are
    optional in fresh wikis).
    """
    violations: list[str] = []
    if not LOG_MD.exists():
        return violations
    try:
        text = read_text_cached(LOG_MD)
    except OSError:
        return violations
    entries: list[tuple[str, int]] = []
    for m in LOG_HEADER_RE.finditer(text):
        date = m.group(1)
        line_no = text[: m.start()].count("\n") + 1
        entries.append((date, line_no))
    rel = LOG_MD.relative_to(ROOT).as_posix()
    for i in range(len(entries) - 1):
        cur_date, cur_line = entries[i]
        nxt_date, nxt_line = entries[i + 1]
        if nxt_date < cur_date:
            violations.append(
                f"{rel}:{nxt_line}: [{nxt_date}] entry follows "
                f"[{cur_date}] at :{cur_line} (dates must be ascending)"
            )
    return violations


def run() -> int:
    if not CLAUDE_MD.exists():
        print(f"CLAUDE.md not found at {CLAUDE_MD}")
        return 1

    # INTEGRITY pass
    text = read_text_cached(CLAUDE_MD)
    broken_anchors = _check_anchors(text)
    missing_files = _check_file_refs(text)
    missing_cmds = _check_slash_commands(text)
    unlisted_files = _check_roster_completeness(text)

    if broken_anchors:
        print(f"\n[Broken anchors: {len(broken_anchors)}]")
        for b in broken_anchors:
            print(b)
    if missing_files:
        print(f"\n[Missing file references: {len(missing_files)}]")
        for m in missing_files:
            print(m)
    if missing_cmds:
        print(f"\n[Missing slash command files: {len(missing_cmds)}]")
        for m in missing_cmds:
            print(m)
    if unlisted_files:
        print(f"\n[Unlisted roster files (operations + policies): {len(unlisted_files)}]")
        for u in unlisted_files:
            print(u)
        print(
            "Rule: every .claude/operations/*.md and .claude/policies/*.md file "
            "must be enumerated in the CLAUDE.md \"Instruction Locations\" and (policies) the "
            "folder README index. Add the missing entry."
        )

    integrity_total = (
        len(broken_anchors) + len(missing_files) + len(missing_cmds) + len(unlisted_files)
    )
    if integrity_total == 0:
        print("OK - CLAUDE.md integrity (anchors, file refs, slash commands, roster completeness)")

    # The Rubric Part1↔Part2 mirror was reduced to the manifest roster, so
    # drift/header-count monitoring is unnecessary (completion counts are computed
    # by `_manifest_counts`). total_drift is accumulated by the stale-slug pass, so
    # it's only initialized here.
    total_drift = 0

    # STALE CLUSTER SLUG pass — detect _catalog-<slug>.md literals whose
    # <slug> no longer matches graph/_clusters.json::clusters[].slug
    stale_slug_issues = _check_stale_cluster_slugs()
    if stale_slug_issues:
        print(f"\n[Stale cluster slug literals: {len(stale_slug_issues)}]")
        for s in stale_slug_issues:
            print(s)
        total_drift += len(stale_slug_issues)
    else:
        print("OK - cluster slug literals all resolve in graph/_clusters.json")

    # LANGUAGE pass
    targets: list[Path] = [CLAUDE_MD]
    targets.extend(sorted(COMMANDS_DIR.glob("*.md")) if COMMANDS_DIR.exists() else [])
    print(f"\nMeta-Doc Language Convention ({len(targets)} files)")

    language_total = 0
    for path in targets:
        vs = _check_language_in_file(path)
        if not vs:
            continue
        language_total += len(vs)
        for line_no, line in vs:
            print(f"{path.as_posix()}:{line_no}: {line}")

    if language_total == 0:
        print("OK - no Korean characters in meta-doc section headers")
    else:
        print(f"FAIL - {language_total} Korean header violation(s)")
        print("Rule: section headers in CLAUDE.md and .claude/commands/*.md must be English.")

    # CLAUDE VOICE pass — guideline antipattern (decision option / reinforcement
    # counter / introduction timestamp / external case reference / benchmark
    # absorption narrative). See .claude/policies/claude-guideline-voice.md.
    voice_issues = _check_claude_voice_violations()
    if voice_issues:
        print(f"\n[Claude guideline voice violations: {len(voice_issues)}]")
        for v in voice_issues:
            print(v)
        print(
            "Rule: .claude/commands/*.md, .claude/agents/*.md, CLAUDE.md must "
            "express current policy only — decision history, external case "
            "reference, introduction timestamps belong in log.md. "
            "See .claude/policies/claude-guideline-voice.md."
        )
    else:
        print("OK - no Claude guideline voice antipatterns")

    # FLAT-PATH guard pass — catch stale `python tools/lint.py <flat>` refs.
    flat_issues = _check_flat_lint_paths()
    if flat_issues:
        print(f"\n[Flat lint-path references: {len(flat_issues)}]")
        for v in flat_issues:
            print(v)
        print("Rule: post-refactor form is `python tools/lint.py <group> [<sub>]` "
              "with group ∈ {all, graph, hub, meta, overview, contradiction}.")
    else:
        print("OK - no flat `python tools/lint.py <subcmd>` references")

    # RESERVED FILENAME pass — case-fold collisions with meta-doc lookups.
    reserved_issues = _check_reserved_filename_collisions()
    if reserved_issues:
        print(f"\n[Reserved meta-doc filename collisions: {len(reserved_issues)}]")
        for v in reserved_issues:
            print(v)
        print(
            "Rule: wiki/**/*.md basenames must not case-fold to reserved "
            "meta-doc names (CLAUDE.md, README.md). On case-insensitive "
            "filesystems such files get injected as project instructions."
        )
    else:
        print("OK - no wiki/ filename collisions with reserved meta-docs")

    # LOG MONOTONICITY pass — log.md entries must be date-ascending.
    log_issues = _check_log_monotonicity()
    if log_issues:
        print(f"\n[Log ordering violations: {len(log_issues)}]")
        for v in log_issues:
            print(v)
        print(
            "Rule: log.md entries must appear oldest-first. New entries "
            "go at the bottom with a date >= the previous entry's date. "
            "To repair, move the offending entry block (from its `## [date]` "
            "header to the next header) to its chronological position."
        )
    else:
        print("OK - log.md entries are chronologically ordered")

    # HOOK BASH-PREFIX pass — settings.json hook `.sh` commands must lead with `bash`.
    hook_prefix_issues = _check_hook_bash_prefix()
    if hook_prefix_issues:
        print(f"\n[Hook bash-prefix violations: {len(hook_prefix_issues)}]")
        for v in hook_prefix_issues:
            print(v)
        print(
            "Rule: settings(.local).json hook commands that run a .sh script "
            "must lead with `bash` (e.g. `bash .claude/hooks/foo.sh`). A bare "
            ".sh path silently no-ops on Windows shells. "
            "See .claude/policies/platform.md \"Hook execution environment\"."
        )
    else:
        print("OK - settings.json .sh hook commands all lead with `bash`")

    # HOOK ADVISORY CHANNEL pass — non-blocking advisories must use additionalContext.
    hook_channel_issues = _check_hook_advisory_channel()
    if hook_channel_issues:
        print(f"\n[Hook advisory-channel violations: {len(hook_channel_issues)}]")
        for v in hook_channel_issues:
            print(v)
        print(
            "Rule: a non-blocking hook (no `exit 2`) must deliver its message "
            "via stdout JSON `hookSpecificOutput.additionalContext`. stderr on "
            "exit 0 reaches the user only, not Claude. Blocking guards (exit 2) "
            "are exempt. See .claude/policies/platform.md \"Hook execution environment\"."
        )
    else:
        print("OK - advisory hooks deliver via additionalContext (no stderr-on-exit-0)")

    # HOOK PYTHON UTF-8 pass — hook python3 calls must force UTF-8 (cp949 corrupts Korean).
    regex_hoist_issues = _check_shared_regex_hoisting()
    if regex_hoist_issues:
        print(f"\n[Shared-regex redefinitions: {len(regex_hoist_issues)}]")
        for v in regex_hoist_issues:
            print(v)
        print(
            "Rule: FRONTMATTER*/WIKILINK*/AUTO* regexes live only in tools/_lib.py — "
            "import (or alias) the shared definition instead of re.compile-ing "
            "a module copy. Variants get a distinct name in _lib."
        )
    else:
        print("OK - shared FRONTMATTER*/WIKILINK*/AUTO* regexes defined only in _lib")

    hook_utf8_issues = _check_hook_python_utf8()
    if hook_utf8_issues:
        print(f"\n[Hook python3 UTF-8 violations: {len(hook_utf8_issues)}]")
        for v in hook_utf8_issues:
            print(v)
        print(
            "Rule: every hook `python3` invocation must force UTF-8 mode "
            "(`PYTHONUTF8=1 python3`, or `PYTHONIOENCODING=utf-8`, or `-X utf8`). "
            "On Windows python3 decodes stdin/stdout as cp949, mangling Korean "
            "into lone surrogates that crash the session (JSON 400). "
            "See .claude/policies/platform.md \"Hook execution environment\"."
        )
    else:
        print("OK - hook python3 calls force UTF-8 mode")

    # CRAFT-SKILL INTEGRITY pass — manifest/layers dot-ids ↔ skill criteria.json
    # and checks.py functions stay referentially closed.
    craft_issues = _check_craft_skill_integrity()
    if craft_issues:
        print(f"\n[Craft-skill integrity violations: {len(craft_issues)}]")
        for v in craft_issues:
            print(v)
        print(
            "Rule: every craft dot-id (jrn/con/enc/cit) in .claude/layers/_manifest.json "
            "or .claude/layers/*.md must be defined in a .claude/skills/<skill>/criteria.json; "
            "bundle fns and judge=A algorithms must exist in that skill's checks.py."
        )
    else:
        print("OK - craft skill chain referentially closed (manifest·layers·criteria·checks)")

    # STALE GUIDE REF pass — pre-merge `<x>-authoring.md`/`-rubric.md` filenames.
    stale_guide_issues = _check_stale_guide_refs()
    if stale_guide_issues:
        print(f"\n[Stale guide-file references: {len(stale_guide_issues)}]")
        for v in stale_guide_issues:
            print(v)
        print(
            "Rule: `<x>-authoring.md`/`<x>-rubric.md` guides were merged into "
            ".claude/layers/<content-type>.md — reference the merged file instead."
        )
    else:
        print("OK - no stale `-authoring.md`/`-rubric.md` guide references")

    # OBSIDIAN LINK SAFETY pass — generated catalogs/index must not carry raw
    # brackets or a dangling backslash in link display text.
    link_issues = _check_obsidian_link_safety()
    if link_issues:
        print(f"\n[Obsidian link-safety violations: {len(link_issues)}]")
        for v in link_issues:
            print(v)
        print(
            "Rule: generated meta (wiki/index.md, wiki/sources/_catalog*.md) link "
            "display text must not contain a raw `[`/`]` (use lenticular 【】 via "
            "safe_link_text()) or end with `\\` (escapes the closing `]`)."
        )
    else:
        print("OK - generated meta link display text is Obsidian-safe")

    # NESTED WIKILINK pass — authored narrative must not nest `[[` inside a
    # wikilink alias (Obsidian closes the outer link at the first `]]`).
    nested_issues = _check_nested_wikilinks()
    if nested_issues:
        print(f"\n[Nested-wikilink-in-alias violations: {len(nested_issues)}]")
        for v in nested_issues:
            print(v)
        print(
            "Rule: a wikilink alias must not contain a nested `[[` — Obsidian "
            "cannot nest wikilinks and breaks the render. Flatten the inner "
            "link to plain text (keep the entity name without `[[ ]]`)."
        )
    else:
        print("OK - no nested wikilinks in authored content aliases")

    total = integrity_total + language_total + total_drift + len(flat_issues) + len(reserved_issues) + len(log_issues) + len(voice_issues) + len(hook_prefix_issues) + len(hook_channel_issues) + len(hook_utf8_issues) + len(regex_hoist_issues) + len(craft_issues) + len(stale_guide_issues) + len(link_issues) + len(nested_issues)
    if total == 0:
        return 0
    print(f"\nFAIL - {total} meta-schema issue(s)")
    return 1


if __name__ == "__main__":
    sys.exit(run())
