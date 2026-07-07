#!/usr/bin/env python3
"""minimality-advisory.sh helper — diff-scoped bullet depth / multi-item cramming detection.

When editing `.claude/`·CLAUDE.md, surface as an advisory any list bullet entering
in this change (new_string/content) that is "length ≥ LEN_T relative to sibling
median AND multi-item (enum≥2 OR sentence-terminators≥2)". Because it is diff-scoped
rather than exhaustive, it does not touch existing assets (legitimately detailed
principle bullets) — a combination verified in A3 calibration to remove all
false-positives relative to pure length (A1).

stdin: PreToolUse hook JSON. stdout: advisory text (empty output if no violation).
Failure is non-blocking — on exception, silently emit empty output + exit 0.
"""
import re
import statistics
import sys
import json

LEN_T = 3.0
MIN_GROUP = 4

BULLET_RE = re.compile(r"^(?P<indent>\s*)(?:[-*]|\d+\.)\s+(?P<body>.*\S)\s*$")
FENCE_RE = re.compile(r"^\s*```")
ENUM_RE = re.compile(r"\([a-z]\)|\([0-9]+\)|[①②③④⑤⑥⑦⑧⑨⑩]")
SENT_RE = re.compile(r"(?<![0-9])\.(?=\s|$)")  # sentence-terminator estimate (excludes decimal point)


def parse_bullets(text):
    """Yield (lineno, depth, body) for bullet lines, skipping fences/table rows."""
    in_fence = False
    for i, raw in enumerate(text.splitlines(), 1):
        if FENCE_RE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = BULLET_RE.match(raw)
        if not m:
            continue
        body = m.group("body")
        if body.lstrip().startswith("|"):
            continue
        yield i, len(m.group("indent")), body


def sibling_groups(bullets):
    """Group consecutive same-depth bullets (siblings); keep groups ≥ MIN_GROUP."""
    groups, cur, last_line, last_depth = [], [], None, None
    for lineno, depth, body in bullets:
        contiguous = last_line is not None and lineno - last_line <= 2
        if cur and (depth != last_depth or not contiguous):
            groups.append(cur)
            cur = []
        cur.append((lineno, depth, body))
        last_line, last_depth = lineno, depth
    if cur:
        groups.append(cur)
    return [g for g in groups if len(g) >= MIN_GROUP]


def expected_text(tool_input):
    """Reconstruct the post-edit file content. Write → content; Edit → file with
    old_string replaced by new_string. Returns (full_text, changed_bodies)."""
    path = tool_input.get("file_path") or tool_input.get("path") or ""
    content = tool_input.get("content")
    if content is not None:  # Write
        changed = {b for _, _, b in parse_bullets(content)}
        return content, changed
    old = tool_input.get("old_string")
    new = tool_input.get("new_string")
    if new is None or not path:
        return None, set()
    try:
        with open(path, encoding="utf-8") as fh:
            disk = fh.read()
    except (OSError, UnicodeDecodeError):
        return None, set()
    if old and old not in disk:  # Edit would fail — degrade to None, not stale disk
        return None, set()
    if not old:
        full = disk
    elif tool_input.get("replace_all"):
        full = disk.replace(old, new)
    else:
        full = disk.replace(old, new, 1)
    changed = {b for _, _, b in parse_bullets(new)}
    return full, changed


def analyze(data) -> str:
    """hook JSON dict → advisory text (empty string if no violation). The entry
    point dispatch.py calls without re-parsing stdin — main() is the wrapper for
    standalone stdin execution."""
    full, changed = expected_text(data.get("tool_input", {}))
    if not full or not changed:
        return ""

    hits = []
    for group in sibling_groups(list(parse_bullets(full))):
        med = statistics.median(len(b) for _, _, b in group)
        if med == 0:
            continue
        for lineno, depth, body in group:
            if body not in changed:
                continue  # diff-scoped: this change only
            ratio = len(body) / med
            if ratio < LEN_T:
                continue
            enum, sent = len(ENUM_RE.findall(body)), len(SENT_RE.findall(body))
            if enum >= 2 or sent >= 2:
                hits.append((ratio, enum, sent, lineno, body))

    if not hits:
        return ""

    lines = [
        "[depth-check] This change's bullet is oversized relative to the sibling median"
        " (≥%.1fx) and multi-item — consider splitting or slimming (cramming signal):" % LEN_T
    ]
    for ratio, enum, sent, lineno, body in sorted(hits, reverse=True):
        lines.append("  %.1fx (enum%d·sent%d) L%d: %s…" % (ratio, enum, sent, lineno, body[:60]))
    return "\n".join(lines)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    out = analyze(data)
    if out:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
