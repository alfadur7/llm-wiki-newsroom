#!/bin/bash
# PostToolUse(Bash|PowerShell) launcher — lint_chain_guard.py parses the stdin
# JSON once and flags a pending chain after `tools/lint.py ... --yes|--fix`.
#
# Marker SoT: .claude/commands/wiki-lint.md → "Chain Execution Obligation > Chain Markers"
#   4 markers — CHAIN-REQUIRED · STALE --fix chain · ⚡ ACTION REQUIRED · Claude rewrite instruction block
# Effect: exit 2 → blocking feedback to Claude (stderr surfaced as system-reminder).
#
# Activation: registered in .claude/settings.json as a Bash|PowerShell PostToolUse hook.

set -uo pipefail

# Fallback so the hook is not silently disabled on a shell without the py3 binary
# (some Windows Git Bash installs).
if command -v python3 >/dev/null 2>&1; then exec env PYTHONUTF8=1 python3 "$(dirname "$0")/lint_chain_guard.py"; fi
exec env PYTHONUTF8=1 python "$(dirname "$0")/lint_chain_guard.py"