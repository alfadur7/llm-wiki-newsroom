#!/bin/bash
# Write|Edit hook single entry point — dispatch.py ("$1" = pre|post) parses the
# stdin JSON once and handles both the guard (block) and the advisory
# (additionalContext).
# Back when there were 6 individual .sh files (lint-report-guard·minimality·scratch /
# stub-build·stub-desk·incremental-lint), each tool call spawned python ~10 times +
# fired the advisory three times on the same file — this dispatcher consolidates that
# into one spawn and one payload.
#
# Activation: registered in .claude/settings.json —
#   PreToolUse  Write|Edit → `bash .claude/hooks/dispatch.sh pre`
#   PostToolUse Write|Edit → `bash .claude/hooks/dispatch.sh post`

set -uo pipefail

# Fallback so the hook is not silently disabled on a shell without the py3 binary
# (some Windows Git Bash installs).
if command -v python3 >/dev/null 2>&1; then exec env PYTHONUTF8=1 python3 "$(dirname "$0")/dispatch.py" "$1"; fi
exec env PYTHONUTF8=1 python "$(dirname "$0")/dispatch.py" "$1"
