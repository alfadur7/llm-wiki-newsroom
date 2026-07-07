"""PostToolUse(Bash|PowerShell) — flag pending chain after `tools/lint.py ... --yes|--fix`.

Marker SoT: .claude/commands/wiki-lint.md → "Chain Execution Obligation > Chain Markers"
  4 markers — CHAIN-REQUIRED · STALE --fix chain · ⚡ ACTION REQUIRED · Claude rewrite instruction block
Effect: exit 2 → blocking feedback to Claude (stderr surfaced as system-reminder).

Usage (from lint-chain-guard.sh): hook JSON on stdin — one parse serves both
field extractions (same consolidation as dispatch.py).
"""
import json
import re
import sys

LINT_RE = re.compile(r"tools/lint\.py.*(--yes|--fix)")
YES_RE = re.compile(r"--yes\b|\s-y\b")
MARKER_RE = re.compile(r"CHAIN-REQUIRED|STALE --fix chain|ACTION REQUIRED|Claude rewrite instruction block")

MSG_YES = """[lint-chain-guard] CHAIN PENDING (--yes opt-in)

The lint output contains a chain marker (CHAIN-REQUIRED / STALE / rewrite block)
and the invocation included `--yes` (or `-y`) — chain auto-entry is mandated.
Required action in THIS turn:
  1. Do NOT write lint-report.md yet
  2. Do NOT classify the chain as "Remaining work" in the report
  3. Do NOT request user approval before chain entry — `--yes` already opted in
  4. Perform the indicated chain (rewrite block / Phase 1·2 derivation / etc.)
  5. Re-run the same lint subcommand to verify PASS
  6. Only then write the report

User gate fires ONLY mid-chain on new theme/cluster slug, major rewrite (>50%),
L2-4 root publication, or ADAPT 3rd same-cause FAIL — never as a chain-entry gate.

Reference: .claude/agents/README.md (Universal Cycle) + .claude/commands/wiki-lint.md
           ("Claude behavior contract" — do not request user approval (limited to the `--yes` context))
           + CLAUDE.md (Human Reviewer Gate)."""

MSG_NO_YES = """[lint-chain-guard] CHAIN PENDING (--fix without --yes — chain opt-in deferred)

The lint output contains a chain marker (CHAIN-REQUIRED / STALE / rewrite block)
but the invocation did NOT include `--yes` — user has explicitly declined chain
auto-entry (SoT: wiki-lint.md "Claude behavior contract" — the only case where not acting is correct).
Required action in THIS turn:
  1. Do NOT write lint-report.md yet (block emission until user decides)
  2. Record the rewrite block / chain reason in the report draft + WAIT for user
  3. Do NOT auto-enter the chain — `--yes` was NOT supplied (opt-in declined)
  4. User decides whether to re-invoke with `--yes` to proceed

Reference: .claude/agents/README.md (Universal Cycle) + .claude/commands/wiki-lint.md
           ("Claude behavior contract" — the only case where not acting is correct)."""


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    command = (data.get("tool_input", {}) or {}).get("command", "") or ""
    resp = data.get("tool_response", {})
    if isinstance(resp, dict):
        stdout = resp.get("stdout", "") or resp.get("output", "") or ""
    else:
        stdout = resp if isinstance(resp, str) else ""
    # Only act on lint --yes / --fix invocations with a chain marker in stdout.
    if not LINT_RE.search(command) or not MARKER_RE.search(stdout):
        return 0
    print(MSG_YES if YES_RE.search(command) else MSG_NO_YES, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())