#!/bin/bash
# Write|Edit + commit-gate hook single entry point — dispatch.py ("$1" =
# pre|post|pre-bash) parses the stdin JSON once and handles both the guard
# (block) and the advisory (additionalContext).
# Back when there were 6 individual .sh files (lint-report-guard·minimality·scratch /
# stub-build·stub-desk·incremental-lint), each tool call spawned python ~10 times +
# fired the advisory three times on the same file — this dispatcher consolidates that
# into one spawn and one payload.
#
# Activation: registered in .claude/settings.json —
#   PreToolUse  Write|Edit       → `bash "$CLAUDE_PROJECT_DIR/.claude/hooks/dispatch.sh" pre`
#   PostToolUse Write|Edit       → `bash "$CLAUDE_PROJECT_DIR/.claude/hooks/dispatch.sh" post`
#   PreToolUse  Bash|PowerShell  → `bash "$CLAUDE_PROJECT_DIR/.claude/hooks/dispatch.sh" pre-bash`

set -uo pipefail

# pre-bash fires on every Bash|PowerShell call, so the `git commit` test runs here in
# the shell: spawning python a hundred times a session to answer "not a commit" is the
# cost this branch exists to avoid. Matched against the raw JSON, which is safe — the
# pattern holds no character JSON escapes.
#
# The glob is deliberately WIDER than `GIT_COMMIT_RE`, which stays the authority. A
# prefilter that over-fires costs one python spawn; one that under-fires makes the gate
# silent on a real commit while the suite stays green, since nothing else reaches this
# layer. `*"git commit"*` did exactly that — `git -C . commit`, `git -c user.x=y commit`
# and `git  commit` (two spaces) never got here. Measured on a 130-call session: the
# widening costs 6 extra spawns (~1.5s) and the superset property is pinned by
# `tests/test_hooks_dispatch.py::test_prefilter_never_narrower_than_the_regex`.
if [ "$1" = "pre-bash" ]; then
  payload=$(cat)
  case "$payload" in *git*commit*) ;; *) exit 0 ;; esac
  if command -v python3 >/dev/null 2>&1; then printf '%s' "$payload" | env PYTHONUTF8=1 python3 "$(dirname "$0")/dispatch.py" "$1"; exit $?; fi
  printf '%s' "$payload" | env PYTHONUTF8=1 python "$(dirname "$0")/dispatch.py" "$1"
  exit $?
fi

# Fallback so the hook is not silently disabled on a shell without the py3 binary
# (some Windows Git Bash installs).
if command -v python3 >/dev/null 2>&1; then exec env PYTHONUTF8=1 python3 "$(dirname "$0")/dispatch.py" "$1"; fi
exec env PYTHONUTF8=1 python "$(dirname "$0")/dispatch.py" "$1"
