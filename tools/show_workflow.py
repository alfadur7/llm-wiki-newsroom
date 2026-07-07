#!/usr/bin/env python3
"""Show a snapshot of Workflow (Workflow tool) execution status.

Used as a fallback monitor in environments where the `/workflows` slash command does not work.
A Workflow that Claude Code launched in the background records its progress in these two files:

  ~/.claude/projects/<project>/<session>/subagents/workflows/wf_*/journal.jsonl
      per-agent started/result events (JSON Lines)
  agent-<id>.meta.json in the same folder — metadata such as agentType

Rather than hardcoding the session path, this script auto-discovers workflow run folders
under ~/.claude/projects (default: this project, newest journal first).

Usage:
  python tools/show_workflow.py                # status of the most recent run
  python tools/show_workflow.py --list         # list of recent runs only
  python tools/show_workflow.py wf_1c0d509e    # a specific run id (prefix match)
  python tools/show_workflow.py <path>          # point at a wf_* folder directly
  python tools/show_workflow.py --all-projects # target all projects
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import _lib  # noqa: F401  # reconfigures stdout/stderr to UTF-8 (Windows cp949 console)

PROJECTS = Path.home() / ".claude" / "projects"
# Identifying token common to this project's session folder names (default filter).
PROJECT_HINT = "llm-wiki-newsroom"
_MD_RE = re.compile(r"(?:wiki/)?(?:overviews|contradictions|syntheses|trails|timelines|sources|entities|concepts)/[\w\-가-힣]+\.md")


def find_runs(all_projects: bool) -> list[Path]:
    """Return workflow run folders (wf_*) sorted by journal.jsonl, newest first."""
    pattern = str(PROJECTS / "*" / "*" / "subagents" / "workflows" / "wf_*")
    runs = [Path(p) for p in glob.glob(pattern) if (Path(p) / "journal.jsonl").is_file()]
    if not all_projects:
        scoped = [r for r in runs if PROJECT_HINT in str(r).lower()]
        runs = scoped or runs  # fall back to all runs if this project has none
    return sorted(runs, key=lambda r: (r / "journal.jsonl").stat().st_mtime, reverse=True)


def resolve_run(arg: str | None, all_projects: bool) -> Path | None:
    if arg:
        p = Path(arg)
        if p.is_dir() and (p / "journal.jsonl").is_file():
            return p
        # run id (prefix) match
        for r in find_runs(all_projects=True):
            if r.name.startswith(arg) or r.name.startswith(f"wf_{arg}".replace("wf_wf_", "wf_")):
                return r
        return None
    runs = find_runs(all_projects)
    return runs[0] if runs else None


def _agent_types(run: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for f in run.glob("*.meta.json"):
        aid = f.name.split(".")[0].replace("agent-", "")
        try:
            out[aid] = json.loads(f.read_text(encoding="utf-8")).get("agentType", "?")
        except (OSError, ValueError):
            pass
    return out


def _as_text(x: object) -> str:
    """In the schema stage, result may be a dict (structured output) — normalize to a string."""
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    try:
        return json.dumps(x, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(x)


def _target_of(run: Path, aid: str, result: object) -> str:
    """Infer the target file/slug the agent handles — from the completed result or the transcript prompt."""
    for text in (_as_text(result), _first_prompt(run, aid)):
        if not text:
            continue
        m = _MD_RE.search(text)
        if m:
            return m.group(0).removeprefix("wiki/")
    return ""


def _first_prompt(run: Path, aid: str) -> str | None:
    """Part of the first user prompt from the agent-<id>.jsonl transcript (for target identification)."""
    fp = run / f"agent-{aid}.jsonl"
    if not fp.is_file():
        return None
    try:
        with fp.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if '"role": "user"' in line or '"role":"user"' in line:
                    return line[:2000]
    except OSError:
        return None
    return None


def show(run: Path) -> None:
    atype = _agent_types(run)
    events = []
    for line in (run / "journal.jsonl").read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip():
            try:
                events.append(json.loads(line))
            except ValueError:
                pass
    started_order: list[str] = []
    done: dict[str, str] = {}
    for e in events:
        aid = e.get("agentId")
        if not aid:
            continue
        if e.get("type") == "started" and aid not in started_order:
            started_order.append(aid)
        elif e.get("type") == "result":
            done[aid] = e.get("result", "") or ""

    mtime = datetime.fromtimestamp((run / "journal.jsonl").stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    print(f"run: {run.name}   (journal updated {mtime})")
    print(f"agents: {len(started_order)} started · {len(done)} done · {len(started_order) - len(done)} running")
    print("-" * 72)
    for aid in started_order:
        t = atype.get(aid, "?")
        tgt = _target_of(run, aid, done.get(aid))
        if aid in done:
            first = next((ln for ln in _as_text(done[aid]).splitlines() if ln.strip()), "")[:64]
            print(f"  [DONE] {t:10} {tgt:34} {first}")
        else:
            print(f"  [RUN ] {t:10} {tgt:34} (in progress {aid[:12]})")


def main() -> int:
    ap = argparse.ArgumentParser(description="Snapshot of Workflow execution status")
    ap.add_argument("run", nargs="?", help="run id (prefix) or wf_* folder path (defaults to latest)")
    ap.add_argument("--list", action="store_true", help="print the list of recent runs only")
    ap.add_argument("--all-projects", action="store_true", help="target all projects")
    args = ap.parse_args()

    if args.list:
        runs = find_runs(args.all_projects)
        if not runs:
            print("No workflow runs found.", file=sys.stderr)
            return 1
        for r in runs[:15]:
            mt = datetime.fromtimestamp((r / "journal.jsonl").stat().st_mtime).strftime("%m-%d %H:%M")
            print(f"  {mt}  {r.name}")
        return 0

    run = resolve_run(args.run, args.all_projects)
    if not run:
        print("No workflow runs found (check with --list).", file=sys.stderr)
        return 1
    show(run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
