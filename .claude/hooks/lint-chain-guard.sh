#!/bin/bash
# PostToolUse(Bash) — flag pending chain after `tools/lint.py ... --yes|--fix`.
#
# Marker SoT: .claude/commands/wiki-lint.md → "Chain Execution Obligation > Chain Markers"
#   4 markers — CHAIN-REQUIRED · STALE --fix chain · ⚡ ACTION REQUIRED · Claude rewrite instruction block
# Effect: exit 2 → blocking feedback to Claude (stderr surfaced as system-reminder).
#
# Activation: registered in .claude/settings.json as a Bash PostToolUse hook.

set -uo pipefail

INPUT=$(cat)

COMMAND=$(printf '%s' "$INPUT" | PYTHONUTF8=1 python3 -c '
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get("tool_input", {}).get("command", ""))
except Exception:
    pass
' 2>/dev/null)

STDOUT=$(printf '%s' "$INPUT" | PYTHONUTF8=1 python3 -c '
import sys, json
try:
    d = json.load(sys.stdin)
    r = d.get("tool_response", {})
    if isinstance(r, dict):
        print(r.get("stdout", "") or r.get("output", ""))
    else:
        print(r if isinstance(r, str) else "")
except Exception:
    pass
' 2>/dev/null)

# Only act on lint --yes / --fix invocations
if ! printf '%s' "$COMMAND" | grep -qE 'tools/lint\.py.*(--yes|--fix)'; then
  exit 0
fi

# Detect --yes / -y opt-in (chain auto-entry mandate applies only when present).
HAS_YES=false
if printf '%s' "$COMMAND" | grep -qE '(--yes\b|[[:space:]]-y\b)'; then
  HAS_YES=true
fi

# Detect chain markers in stdout (SoT: .claude/commands/wiki-lint.md → Chain Markers)
if printf '%s' "$STDOUT" | grep -qE '(CHAIN-REQUIRED|STALE --fix chain|ACTION REQUIRED|Claude rewrite instruction block)'; then
  if [ "$HAS_YES" = "true" ]; then
    cat >&2 <<'EOF'
[lint-chain-guard] CHAIN PENDING (--yes opt-in)

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
           + CLAUDE.md (Human Reviewer Gate).
EOF
  else
    cat >&2 <<'EOF'
[lint-chain-guard] CHAIN PENDING (--fix without --yes — chain opt-in deferred)

The lint output contains a chain marker (CHAIN-REQUIRED / STALE / rewrite block)
but the invocation did NOT include `--yes` — user has explicitly declined chain
auto-entry (SoT: wiki-lint.md "Claude behavior contract" — the only case where not acting is correct).
Required action in THIS turn:
  1. Do NOT write lint-report.md yet (block emission until user decides)
  2. Record the rewrite block / chain reason in the report draft + WAIT for user
  3. Do NOT auto-enter the chain — `--yes` was NOT supplied (opt-in declined)
  4. User decides whether to re-invoke with `--yes` to proceed

Reference: .claude/agents/README.md (Universal Cycle) + .claude/commands/wiki-lint.md
           ("Claude behavior contract" — the only case where not acting is correct).
EOF
  fi
  exit 2
fi

exit 0
