"""Build graph/_pages.json — the reading-panel data bundle for graph.html.

graph.html fetches its data as JSON over a web server (file:// is no longer
supported). `_graph.json` and `_clusters.json` are already written by the
graph/clusters phases; this step emits the third file, `_pages.json`, which
powers the in-browser reading panel — selecting a node renders its raw
markdown (via marked.js) so the wiki is readable without Obsidian.

`_pages.json` carries five maps:

  - pages     → {node_id: raw markdown}  for every graph node (ROOT_META
                excluded, matching the node set in _graph.json).
  - idmap     → {wikilink_form: node_id}  so `[[신한은행]]` in body text
                resolves to a clickable node. Built via _lib._build_id_map
                (same resolver the edge builder uses — one source of truth).
  - backlinks → {node_id: [referencing_node_id, ...]}  from
                wiki/_backlinks.json (index step output), restricted to
                ids that are graph nodes.
  - overviews → {"_root": overview.md body, "<cluster slug>": overviews/<slug>.md}
                The 5 meta types are no longer graph nodes, so their bodies
                are not in `pages`. overview binds to the cluster legend: the
                panel shows _root globally and the cluster's overview on select.
  - meta_pages→ {rel: raw markdown}  for the 4 overlay types
                (trails/timelines/syntheses/contradictions) so clicking an
                overlay row renders its page. Active files only (no _archive).

`_pages.json` is .gitignore'd — a pure byproduct of the JSON SoTs and the
wiki/*.md pages. Fresh clones run `python tools/build.py clusters` once to
regenerate it; graph.html shows a helpful error if it is missing.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from _build.graph import ROOT_META  # noqa: E402
from _lib import WIKI, atomic_write_text, _build_id_map  # noqa: E402


def run() -> None:
    graph_path = Path("graph/_graph.json")
    graph_data = json.loads(graph_path.read_text(encoding="utf-8"))

    # Node set mirrors _graph.json exactly (ROOT_META already excluded there,
    # but we guard again so a stale graph can't leak an aggregation file's
    # body into the panel).
    nodes = graph_data["nodes"]
    node_ids = {n["id"] for n in nodes}
    pages: dict[str, str] = {}
    missing = 0
    for n in nodes:
        nid = n["id"]
        if Path(nid).name in ROOT_META:
            continue
        fp = WIKI / nid
        if not fp.exists():
            missing += 1
            continue
        pages[nid] = fp.read_text(encoding="utf-8", errors="replace")

    idmap = _build_id_map(nodes)

    # wiki/_backlinks.json is keyed by stem (e.g. "Stablecoin") with values
    # [{"from": "sources/x.md", "title": ...}, ...]. Resolve each stem to a
    # canonical node id via idmap and keep only "from" paths that are
    # themselves graph nodes — the panel must never offer a click that lands
    # on a non-existent node. Titles are dropped here; the panel reads labels
    # from _graph.json so there is one source of truth for node display names.
    backlinks_path = WIKI / "_backlinks.json"
    backlinks_all: dict = (
        json.loads(backlinks_path.read_text(encoding="utf-8"))
        if backlinks_path.exists() else {}
    )
    backlinks: dict[str, list[str]] = {}
    for stem, refs in backlinks_all.items():
        nid = idmap.get(stem)
        if nid is None or nid not in node_ids:
            continue
        srcs = [r["from"] for r in refs if r.get("from") in node_ids]
        if srcs:
            backlinks[nid] = srcs

    # Meta-page bodies for the reading panel — these pages are no longer graph
    # nodes (graph.py limits nodes to 3 substance types), so the panel cannot
    # read them from `pages`. overview binds to the cluster legend; the other
    # 4 types are clicked from the overlay panel (rel-keyed).
    overviews: dict[str, str] = {}
    root_ov = WIKI / "overview.md"
    if root_ov.exists():
        overviews["_root"] = root_ov.read_text(encoding="utf-8", errors="replace")
    ov_dir = WIKI / "overviews"
    if ov_dir.is_dir():
        for f in sorted(ov_dir.iterdir()):
            if f.is_dir() or not f.name.endswith(".md") or f.name.startswith("_"):
                continue
            overviews[f.name[:-3]] = f.read_text(encoding="utf-8", errors="replace")

    meta_pages: dict[str, str] = {}
    for subdir in ("trails", "timelines", "syntheses", "contradictions"):
        d = WIKI / subdir
        if not d.is_dir():
            continue
        for f in sorted(d.iterdir()):
            if f.is_dir() or not f.name.endswith(".md") or f.name.startswith("_"):
                continue
            meta_pages[f"{subdir}/{f.name}"] = f.read_text(encoding="utf-8", errors="replace")

    pages_data = {"pages": pages, "idmap": idmap, "backlinks": backlinks,
                  "overviews": overviews, "meta_pages": meta_pages}
    pages_path = Path("graph/_pages.json")
    atomic_write_text(pages_path, json.dumps(pages_data, ensure_ascii=False))

    print(
        f"_pages.json ({pages_path.stat().st_size:,} B) — "
        f"{len(pages)} pages, {len(idmap)} idmap, {len(backlinks)} backlinked nodes, "
        f"{len(overviews)} overviews, {len(meta_pages)} meta pages"
        + (f", {missing} pages missing on disk" if missing else "")
    )
