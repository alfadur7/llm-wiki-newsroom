"""QMD content search handlers for `tools/query.py qmd ...`.

Thin wrapper around the QMD binary (https://github.com/tobi/qmd). This is the
human/terminal entry point; agents search via the MCP server (mcp__qmd__query),
which takes structured intent/lex/vec/hyde fields. The CLI takes a single bare
query string — right for terminal ergonomics, and it keeps documentation
examples platform-agnostic.

Subcommands (names chosen for clarity; behavior mirrors QMD):
  hybrid   Hybrid search with auto expansion + reranking (recommended;
           maps to QMD's `query` subcommand)
  search   Full-text BM25 keywords (no LLM)
  vsearch  Vector similarity only
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

DEFAULT_COLLECTION = "wiki"
DEFAULT_LIMIT = 8


def _resolve_qmd_invocation() -> list[str]:
    """Return the argv prefix that invokes QMD on this platform.

    Preference order:
      1. node + qmd.js        (no shell, no .cmd quirks, cleanest)
      2. qmd on PATH          (Unix-style install)

    Raises SystemExit with a helpful message if neither path works.
    """
    # Option 1: node + qmd.js (works on Windows, macOS, Linux)
    candidates: list[Path] = []
    appdata = os.environ.get("APPDATA")  # Windows %APPDATA%
    if appdata:
        candidates.append(Path(appdata) / "npm/node_modules/@tobilu/qmd/dist/cli/qmd.js")
    # Unix-global npm install location
    candidates.append(Path("/usr/local/lib/node_modules/@tobilu/qmd/dist/cli/qmd.js"))
    candidates.append(Path.home() / ".npm-global/lib/node_modules/@tobilu/qmd/dist/cli/qmd.js")

    qmd_js = next((p for p in candidates if p.exists()), None)
    if qmd_js:
        node = shutil.which("node") or shutil.which("node.exe")
        if node:
            return [node, str(qmd_js)]

    # Option 2: qmd on PATH
    qmd_bin = shutil.which("qmd")
    if qmd_bin:
        return [qmd_bin]

    raise SystemExit(
        "qmd not found. Install with: npm install -g @tobilu/qmd\n"
        "Then ensure `node` is on PATH."
    )


def _run_qmd(subcommand: str, args) -> int:
    """Invoke QMD and stream its output to the terminal."""
    cmd = _resolve_qmd_invocation() + [subcommand, args.query,
                                       "-c", args.collection,
                                       "-n", str(args.limit)]
    if args.json:
        cmd.append("--json")
    if args.files:
        cmd.append("--files")
    # Hybrid-only speed knobs; attributes absent on other subcommands.
    if getattr(args, "no_rerank", False):
        cmd.append("--no-rerank")
    cand = getattr(args, "candidate_limit", None)
    if cand is not None:
        cmd += ["-C", str(cand)]
    # Stream output directly (QMD handles its own formatting / encoding).
    result = subprocess.run(cmd, check=False)
    return result.returncode


def cmd_search(args) -> int:
    """Full-text BM25 keywords (no LLM)."""
    return _run_qmd("search", args)


def cmd_vsearch(args) -> int:
    """Vector similarity only."""
    return _run_qmd("vsearch", args)


def cmd_hybrid(args) -> int:
    """Hybrid search with auto expansion + reranking (recommended)."""
    return _run_qmd("query", args)


# ───────────────────────── registration ─────────────────────────

def _add_common(p) -> None:
    p.add_argument("query", help="search query (natural language or keywords)")
    p.add_argument("-c", "--collection", default=DEFAULT_COLLECTION,
                   help=f"QMD collection name (default: {DEFAULT_COLLECTION})")
    p.add_argument("-n", "--limit", type=int, default=DEFAULT_LIMIT,
                   help=f"max results (default: {DEFAULT_LIMIT})")
    p.add_argument("--json", action="store_true", help="machine-readable JSON output")
    p.add_argument("--files", action="store_true",
                   help="output only file paths (one per line)")


def register(subparsers) -> None:
    """Attach search/vsearch/query subsubcommands to the given subparsers group."""
    p_hybrid = subparsers.add_parser(
        "hybrid", help="Hybrid search with auto expansion + reranking (recommended)")
    _add_common(p_hybrid)
    p_hybrid.add_argument("--no-rerank", action="store_true",
                          help="skip LLM reranking (use RRF scores only, much faster on CPU)")
    p_hybrid.add_argument("-C", "--candidate-limit", type=int, metavar="N",
                          help="max candidates to rerank (default QMD 40, lower = faster)")
    p_hybrid.set_defaults(func=cmd_hybrid)

    p_search = subparsers.add_parser(
        "search", help="Full-text BM25 keywords (no LLM)")
    _add_common(p_search)
    p_search.set_defaults(func=cmd_search)

    p_vsearch = subparsers.add_parser(
        "vsearch", help="Vector similarity only")
    _add_common(p_vsearch)
    p_vsearch.set_defaults(func=cmd_vsearch)
