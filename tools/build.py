"""Unified builder pipeline for the LLM Wiki.

Five phases, each owned by one module (axis-aligned after the Phase B refactor):

  graph          → graph/_graph.json
                   (graph.run only — graph.html now needs _clusters.json too,
                    so html.run moved to the clusters phase where both SoTs
                    are available)
  clusters       → graph/_clusters.json + wiki/sources/_catalog*.md
                   + wiki/overviews/*.md AUTO blocks + wiki/overview.md AUTO:STATS
                   + graph/_pages.json (pages.run — reading-panel body bundle
                    that graph.html fetches; _graph.json/_clusters.json are
                    fetched directly, no JS wrapper)
                   (landscape axis: clusters.run + run_catalogs + run_pages + pages.run)
  contradictions → wiki/contradictions/_contradictions.json
                   + graph/_overlays.json (overlays.run — meta-page overlay
                    structures for graph.html: trail/timeline/synthesis/
                    contradiction members + reverse map; needs fresh
                    contradiction JSON + _graph.json)
                   (conflict axis: contradictions.run — theme MDs have no
                    AUTO blocks by design, so no run_pages step)
  index          → wiki/index.md + wiki/_backlinks.json
                   + wiki/sources/_source_map.json
                   + graph/_pages.json refresh (pages.run re-runs after
                    _backlinks.json is written so the reading-panel bundle
                    carries the current build's backlinks)
                   (global meta — depends on all prior phases for counts/links)
  dependencies   → graph/_dependencies.json
                   (layer-cascade upstream index: page → {upstream pages it
                    derives from, newest upstream date}. Consumed by the
                    uniform staleness rule, tools/_lint/staleness.py. Additive.)

Dependency chain: graph → clusters → contradictions → index → dependencies.
Within each phase, sub-steps run sequentially (JSON first, then dependent MD pages).

Usage:
  python tools/build.py                 # full pipeline
  python tools/build.py all             # explicit
  python tools/build.py graph           # single phase
  python tools/build.py clusters
  python tools/build.py contradictions  # supports --dry-run
  python tools/build.py index
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _build import graph, index, contradictions, pages, clusters, dependencies, overlays  # noqa: E402

PIPELINE = ["graph", "clusters", "contradictions", "index", "dependencies"]


def _phase_graph() -> None:
    graph.run()


def _phase_clusters(cold: bool = False) -> None:
    clusters.run(cold=cold)
    clusters.run_catalogs()
    clusters.run_pages()
    pages.run()


def _phase_index() -> None:
    index.run()
    # _pages.json backlinks come from wiki/_backlinks.json, which index.run
    # writes just above — refresh the bundle here so a single full build ships
    # current backlinks (the clusters phase already built it once for the
    # single-phase `build.py clusters` contract).
    pages.run()


def _phase_contradictions(dry_run: bool = False) -> None:
    contradictions.run(dry_run=dry_run)
    # _overlays.json depends on the contradiction JSONs written just above
    # (contradiction overlays) + _graph.json (graph phase). Run it here so
    # both inputs are fresh. Skipped on dry-run (no fresh contradiction data).
    if not dry_run:
        overlays.run()


PHASES = {
    "graph":          _phase_graph,
    "clusters":       _phase_clusters,
    "contradictions": _phase_contradictions,
    "index":          _phase_index,
    "dependencies":   dependencies.run,
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "phase",
        nargs="?",
        default="all",
        choices=["all"] + list(PHASES.keys()),
        help="Single phase to run, or 'all' for the full pipeline (default).",
    )
    ap.add_argument("--dry-run", action="store_true",
                    help="(contradictions phase only) classify + report distribution without writing files.")
    ap.add_argument("--cold", action="store_true",
                    help="(clusters phase only) force fresh Leiden start (singleton init). "
                         "Default is warm-start from previous _clusters.json. "
                         "Use periodically to escape stale local optima.")
    args = ap.parse_args()

    phases = PIPELINE if args.phase == "all" else [args.phase]
    for name in phases:
        print(f"\n{'=' * 72}\n[build:{name}]\n{'=' * 72}")
        if name == "contradictions":
            PHASES[name](dry_run=args.dry_run)
        elif name == "clusters":
            PHASES[name](cold=args.cold)
        else:
            PHASES[name]()
    return 0


if __name__ == "__main__":
    sys.exit(main())
