"""Retrieval CLI for the LLM Wiki.

Two command groups:

  graph   Structural queries over graph/_graph.json (path, explain, neighbors).
          Answers "how are these connected?" and "what cluster is X in?".

  qmd     Content search via QMD. Subcommands:
            hybrid   Hybrid search with auto expansion + reranking (recommended)
            search   Full-text BM25 keywords (no LLM)
            vsearch  Vector similarity only

Examples:
  python tools/query.py graph explain Meta --budget 40
  python tools/query.py graph path Meta OpenSourceInitiative
  python tools/query.py graph neighbors OpenWeights --json

  python tools/query.py qmd hybrid "open weights vs open source"
  python tools/query.py qmd search "OpenSourceInitiative"
  python tools/query.py qmd vsearch "a model that publishes weights but not training data"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _query import graph as _graph
from _query import qmd as _qmd


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    groups = ap.add_subparsers(dest="group", required=True, metavar="{graph,qmd}")

    graph_parser = groups.add_parser(
        "graph",
        help="structural queries over the knowledge graph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    graph_sub = graph_parser.add_subparsers(dest="cmd", required=True,
                                            metavar="{path,explain,neighbors}")
    _graph.register(graph_sub)

    qmd_parser = groups.add_parser(
        "qmd",
        help="content search via QMD (BM25, vector, hybrid)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    qmd_sub = qmd_parser.add_subparsers(dest="cmd", required=True,
                                        metavar="{hybrid,search,vsearch}")
    _qmd.register(qmd_sub)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
