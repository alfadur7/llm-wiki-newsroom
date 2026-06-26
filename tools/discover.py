"""Discovery entry point for the LLM Wiki.

Only one pass lives here: `surprising` - a composite-score ranking of
bridge hubs that quietly connect disparate clusters
(betweenness * cross-cluster ratio / log-degree).

Other "what's missing?" signals (cross-cutting broken targets,
plain-text mining) were page-gap detection by nature and moved to
`python tools/lint.py hub suggestions`. See CLAUDE.md.

Usage:
  python tools/discover.py                  # surprising (default)
  python tools/discover.py surprising       # explicit
  python tools/discover.py surprising --top 20 --json
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _discover import surprising  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "pass_",
        nargs="?",
        metavar="pass",
        default="surprising",
        choices=["surprising"],
        help="Only `surprising` is available; kept as a subcommand for clarity.",
    )
    ap.add_argument("--json", action="store_true", help="Machine-readable JSON output.")
    ap.add_argument("--top", type=int, default=None, help="Cap results (default per pass)")
    args = ap.parse_args()

    kwargs: dict = {"json_out": args.json}
    if args.top is not None:
        kwargs["top"] = args.top
    return surprising.run(**kwargs)


if __name__ == "__main__":
    sys.exit(main())
