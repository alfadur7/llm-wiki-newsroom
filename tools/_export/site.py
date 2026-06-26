"""Stage the hosted graph browser into a deploy dir with obscured filenames.

graph.html fetches its data (`_graph.json`/`_clusters.json`/`_overlays.json`/
`_pages.json`) over a web server. For the public Cloudflare deploy we copy the
shell + those four JSONs into `out_dir`, renaming every asset with the
unguessable `<slug>-` prefix so the data is not reachable at a predictable path
either, and inject into the HTML:

  - `<meta name="robots" content="noindex,nofollow">` so it is not indexed;
  - a classic `<script>window.ASSET_PREFIX="<slug>-"</script>` (runs before
    the deferred module) so graph.html fetches `<slug>-graph.json` etc.
    instead of the local `_graph.json` defaults.

Outputs into out_dir: <slug>.html, <slug>-graph.json, <slug>-clusters.json,
<slug>-overlays.json, <slug>-pages.json.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))  # _export/ → tools/ root (shared modules)
from _lib import GRAPH as GRAPH_DIR  # noqa: E402

SHELL = GRAPH_DIR / "graph.html"
# graph.html fetches `${PFX}<name>`; locally PFX is "_" → these committed/built
# files, on deploy PFX is "<slug>-" → the renamed copies below. This list MUST
# stay in sync with every `${PFX}<name>` graph.html fetches — a missing entry
# (e.g. overlays.json) 404s on deploy and silently degrades to empty data.
ASSETS = ["graph.json", "clusters.json", "overlays.json", "pages.json"]

ROBOTS_META = '<meta name="robots" content="noindex,nofollow">'


def stage_site(out_dir: Path, slug: str) -> list[tuple[str, int]]:
    """Write <slug>.html + <slug>-{graph,clusters,overlays,pages}.json into out_dir.

    Returns [(filename, size_bytes), ...]. Raises if any input is missing
    (the caller is expected to have run the build pipeline first)."""
    sources = {name: GRAPH_DIR / f"_{name}" for name in ASSETS}
    for p in [SHELL, *sources.values()]:
        if not p.exists():
            raise FileNotFoundError(
                f"{p} missing — run `python tools/build.py` before export"
            )
    out_dir.mkdir(parents=True, exist_ok=True)

    shell = SHELL.read_text(encoding="utf-8")
    # Inject noindex + asset prefix where the deferred module can read them
    # first. Piggyback on the viewport meta to keep head order sensible.
    inject = ROBOTS_META + f'\n<script>window.ASSET_PREFIX = "{slug}-";</script>'
    viewport = '<meta name="viewport" content="width=device-width, initial-scale=1">'
    if viewport in shell:
        shell = shell.replace(viewport, viewport + "\n" + inject)
    else:
        shell = shell.replace("</head>", inject + "\n</head>", 1)

    produced: list[tuple[str, int]] = []
    html_out = out_dir / f"{slug}.html"
    html_out.write_text(shell, encoding="utf-8")
    produced.append((html_out.name, html_out.stat().st_size))
    for name, src in sources.items():
        dst = out_dir / f"{slug}-{name}"
        shutil.copyfile(src, dst)
        produced.append((dst.name, dst.stat().st_size))
    return produced
