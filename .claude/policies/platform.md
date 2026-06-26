# Platform Rules

## Windows Non-Latin (e.g. Korean) Filename Handling

This applies only when a `raw/` source has a non-Latin filename — it is not a routine step for the English-native corpus. On Windows, reading a non-Latin filename (e.g. Korean) directly with the Read tool can hit a shell-encoding (CP949) conflict. In that case, **read the file with Python from Bash** instead of the Read tool:

```bash
python -c "print(open('raw/NewsScrap/한글파일명.md', encoding='utf-8').read())"
```

The Python call above is the standard — patterns that work around it by creating intermediate files like `tmp_reads/` or `batch*.txt` are forbidden (intermediate files get missed by the dedup and lint checks, and responsibility for cleaning them up becomes ambiguous).

## Windows Python UTF-8 Output (global)

The default stdout encoding of Windows `python`/`python3` is cp949 — printing UTF-8 non-ASCII to the console breaks it as mojibake or corrupts it into lone surrogates that contaminate the whole session. `PYTHONUTF8=1` in the `env` of [`settings.json`](../settings.json) forces UTF-8 stdout for **all** python calls in Bash and PowerShell (ad-hoc `python -c` · `tools/*.py` · analysis scripts · hooks) — global and automatic, no need to memorize a per-call prefix. The `PYTHONUTF8=1 python3` prefix in hook scripts is kept as a double safeguard against environments where env is not applied (a different device, a missing env key), and `python tools/lint.py meta` checks for it.

## PowerShell vs Bash

Per the Claude Code environment memo, this project's Primary Shell is PowerShell. Run POSIX scripts with the Bash tool, but general system calls (file listing, git, python, etc.) can use either. Read non-Latin filenames via the Bash + Python workaround above.

## Bash-Tool Redirect/Path Arguments Must Use Forward Slashes

When invoking a command with the Bash tool, redirect targets (`>` `2>&1` `>>`) and file-path arguments **must use forward slashes** (`/`). Passing a Windows backslash path (`c:\tmp\file.txt`) unquoted causes Bash (MSYS, Git Bash, etc.) to interpret the backslash as an escape character and the characters disappear — e.g., `c:\tmp\theme_verify.txt` collapses to `c:tmptheme_verify.txt` and gets created with a malformed filename in the working directory (the wiki project root).

```bash
# ✅ Correct
python tools/lint.py overview > c:/tmp/lint_full.txt 2>&1

# ❌ Forbidden — backslash escaping creates 'c:tmplint_full.txt' in cwd
python tools/lint.py overview > c:\tmp\lint_full.txt 2>&1

# ✅ Quoting preserves the backslashes, but forward slashes are simpler and safer
python tools/lint.py overview > "c:\tmp\lint_full.txt" 2>&1
```

When invoking via the PowerShell tool, both backslashes and forward slashes are handled correctly — this policy is **Bash-tool only**.

## Hook Execution Environment (Windows)

[`.claude/hooks/`](../hooks/) are bash scripts. The `command` for the `PreToolUse`/`PostToolUse` hooks in [`.claude/settings.json`](../settings.json) is registered in the form `bash .claude/hooks/<name>.sh` — **the `bash` prefix is required**. A Windows shell cannot execute a bare `.sh` path directly, so without the prefix that hook silently becomes a no-op, weakening guards and advisories to the level of a natural-language request. `python tools/lint.py meta` checks that a hook command running a `.sh` starts with `bash`.

In environments where the hooks are not registered (no `hooks` key in `settings.json`, or a different path), the guards are silent too, so the configuration must be checked. No separate pre-install of WSL or Git Bash is required — the Bash tool itself already depends on that environment, so this project imposes no additional requirement.

**python3 UTF-8 forcing**: when a hook calls `python3`, it must be in the form `PYTHONUTF8=1 python3` (env-prefix on the pipe segment; the `exec` form is `exec env PYTHONUTF8=1 python3`). Windows `python3` decodes stdin/stdout as cp949, so the hook's UTF-8 non-ASCII output corrupts into lone surrogates and every API request in that session fails permanently with `400 invalid high surrogate` (unrecoverable). `python tools/lint.py meta` checks this.

**Output-channel convention**: the path by which a hook message reaches Claude depends on the exit code. On exit 0 (non-blocking), stderr is shown only to the user and does not enter Claude's context, so a **non-blocking advisory must be emitted as stdout JSON `{"hookSpecificOutput":{"hookEventName":...,"additionalContext":...}}`** to reach Claude. A blocking guard uses stderr + `exit 2` — the stderr of exit 2 is delivered to Claude as feedback. An advisory that emits its message via stderr + exit 0 (without additionalContext) is nullified, and `python tools/lint.py meta` checks for this.
