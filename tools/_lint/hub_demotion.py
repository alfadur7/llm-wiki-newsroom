"""L2-2 full hub → stub/plain-text demotion/deletion candidate triage advisory — entities / concepts.

The inverse of `hub_promotion.py`. Where promotion surfaces "a stub with many
citations but a thin body" as a grow candidate, this module surfaces hubs with
no independent navigational value — "one-off citation ∩ low inbound ∩ single
cluster" — as plain-text demotion/deletion candidates.

Policy rationale (feedback_no_single_source_stub): a stub's existence is
justified when it has ≥3 citations + multiple clusters + a core narrative role;
single-source / isolated stubs are demoted to plain text. Corpus health is
bidirectional, so anchor promotion and isolated-stub cleanup (demotion) must be
run together to stay balanced.

Detection conditions (AND — isolation holds only when every axis is low):
  * sources ≤ SOURCES_MAX (one-off to few-source based)
  * inbound ≤ INBOUND_MAX (low inbound — few referencing nodes. Excludes `_archive` paths)
  * inbound distinct clusters ≤ CLUSTER_MAX (no cross-cluster navigational value)
  * navigational inbound == 0 (below) — if overview/root/another hub links it, it's not an orphan
Grade: strong = single-source ∩ lowest inbound ∩ single cluster (clear plain-text demotion).
       medium = first-pass floor (zero false negatives).

A person (kind: person) candidate notes whether an absorption-target org hub
exists — if the body links an existing org hub, ②′ absorption (default) is
possible; otherwise the demotion direction. This helps the Desk branch between ②′
absorption vs demotion without grep (the absorption default holds only when the
target hub exists).

navigational inbound: weights inbound by **character**, not count. A link from the
source that defined the hub is not navigational value — being linked by an
overview (L2-3·L2-4 root) or another hub (entity/concept/synthesis/timeline/trail)
is what embeds it in the corpus structure. If nav inbound ≥ 1 it's not an orphan,
so it's excluded from demotion candidates (zero-false-negative safe — an embedded
hub is by definition not an orphan). contradiction theme register / index / log
inbound don't count as nav (a theme co-mention / auto-generated list is not a
selective navigational signal). `_archive`-path inbound is dead, so it's excluded
from all counts (prevents misjudging as orphan due to an archive-move side effect).

The nav decision is made via two paths — (1) graph["inbound"] edges
(`_is_nav_inbound`), and (2) a direct prose-layer scan (`_prose_nav_stems`). Graph
edges are only emitted from entity·concept·source origins and don't carry body
wikilinks originating in the prose layer (overview·synthesis·timeline·trail), so a
hub embedded only in an overview can never be seen as nav via (1) alone and recurs
as false-strong on every sweep (2026-06 measured root correction). (2) closes this
by directly catching the prose embed.

Excluded:
  * navigational inbound ≥ 1 — overview/root/other-hub embed (above)
  * gate: full|delegated|absorbed — Desk-gate-concluded hubs. In particular
    absorbed·delegated are citation anchors with many inbound, so deleting them
    would leave dangling backlinks (not deletion targets).

Demotion/deletion is finalized by the Desk's secondary gate (narrative centrality /
figure importance) + graph-integrity handling (redirect inbound [[wikilink]] or
substitute plain text before deletion), so `--fix` is not supported.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))
from _hub_common import (  # noqa: E402
    ENTITIES_DIR,
    HUB_SPECS,
    iter_hub_files,
    body_len as _body_len,
    gate as _gate,
    kind as _kind,
    load_graph as _load_graph,
    sources_count as _sources_count,
)
from _lib import FRONTMATTER_BLOCK_RE, WIKI, WIKILINK_STEM_RE, read_text_cached  # noqa: E402

# Body wikilink target (alias/anchor prefix only): `[[래블업|신정규]]`→`래블업`.
WIKILINK_RE = WIKILINK_STEM_RE

# Thresholds — distribution calibration (571 hubs: inbound>10 is the healthy core
# of 380, inbound≤2 is the isolated tail of 29 / sources=1 is 40 = one-off policy
# red flag).
#   SOURCES_MAX 2: one-off (1) to few (2). ≥3 is the policy floor for justified existence.
#   INBOUND_MAX 3: referencing nodes ≤3 = scant navigational value (clearly separated from the >10 core).
#   CLUSTER_MAX 1: single cluster = no cross-cutting integration value.
SOURCES_MAX = 2
INBOUND_MAX = 3
CLUSTER_MAX = 1
# "strong (top-priority demotion)" — the triple single-source ∩ lowest inbound ∩ single cluster.
STRONG_SOURCES = 1
STRONG_INBOUND = 2
STRONG_CLUSTER = 1

# navigational inbound = linked by an overview (L2-3·L2-4 root) or another hub = corpus embed.
# Excludes source (hub-defining origin) / contradiction (theme co-mention) / index/log / _archive.
NAV_PREFIXES = ("overviews/", "entities/", "concepts/", "syntheses/", "timelines/", "trails/")


def _is_nav_inbound(frm: str) -> bool:
    # The `_archive` exclusion is done at a single point by the sole caller (run) when building froms — single-point SoT.
    if frm == "overview.md":  # L2-4 root cluster overview
        return True
    return frm.startswith(NAV_PREFIXES)


# Graph edges are only emitted from entity·concept·source origins and don't carry
# body wikilinks originating in the prose layer (overview·synthesis·timeline·trail)
# as edges. So the graph["inbound"]-based nav decision above can never see a prose
# embed — a hub embedded only in an overview recurs as false-strong on every sweep
# (2026-06 measured root). Scanning these layers directly augments nav-inbound
# (contradiction register / index / log don't count as nav).
_PROSE_NAV_DIRS = ("overviews", "syntheses", "timelines", "trails")


def _prose_nav_stems() -> set[str]:
    """Set of hub stems embedded as `[[stem]]` in prose-layer bodies = nav-inbound not emitted by the graph.

    Scans the root `overview.md` + .md files directly under
    `overviews/·syntheses/·timelines/·trails/` (excluding `_*`·`_archive`). An
    entity/concept stem embedded here is lodged in the corpus structure, so it's
    not an orphan — excluded from demotion candidates.
    """
    stems: set[str] = set()
    files: list[Path] = []
    root_ov = WIKI / "overview.md"
    if root_ov.exists():
        files.append(root_ov)
    for sub in _PROSE_NAV_DIRS:
        directory = WIKI / sub
        if not directory.exists():
            continue
        files.extend(iter_hub_files(directory))
    for path in files:
        try:
            content = read_text_cached(path)
        except OSError:
            continue
        for m in WIKILINK_RE.finditer(content):
            stems.add(m.group(1).strip())
    return stems


def _org_hub_stems() -> set[str]:
    """Set of existing `kind: org` entity hub file stems — for deciding person-absorption target candidates."""
    orgs: set[str] = set()
    if not ENTITIES_DIR.exists():
        return orgs
    for path in iter_hub_files(ENTITIES_DIR):
        try:
            if _kind(read_text_cached(path)) == "org":
                orgs.add(path.stem)
        except OSError:
            continue
    return orgs


def _absorb_targets(content: str, org_hubs: set[str]) -> list[str]:
    """Existing org hubs linked by the person's body = ②′ absorption-target candidates (deduped, in order of appearance)."""
    fm = FRONTMATTER_BLOCK_RE.match(content)
    body = content[fm.end():] if fm else content
    seen: list[str] = []
    for m in WIKILINK_RE.finditer(body):
        tgt = m.group(1).strip()
        if tgt in org_hubs and tgt not in seen:
            seen.append(tgt)
    return seen


def _check_directory(
    directory: Path, dir_label: str, graph: dict, org_hubs: set[str],
    prose_nav: set[str],
) -> tuple[list[str], int]:
    issues: list[str] = []
    resolved = 0
    if not directory.exists():
        return issues, resolved
    for path in iter_hub_files(directory):
        content = read_text_cached(path)
        if _gate(content):
            resolved += 1
            continue  # Desk-gate concluded — excluded from triage
        nsrc = _sources_count(content)
        if nsrc > SOURCES_MAX:
            continue
        node_id = f"{dir_label}/{path.name}"
        # _archive-path inbound is dead — excluded from all counts
        froms = [f for f in graph["inbound"].get(node_id, []) if "_archive" not in f]
        if any(_is_nav_inbound(f) for f in froms) or path.stem in prose_nav:
            continue  # overview/root/other-hub embed = not an orphan, excluded from demotion
            # (prose_nav = the directly-scanned prose-layer embeds not emitted by the graph)
        inbound = len(froms)
        if inbound > INBOUND_MAX:
            continue
        clusters = {
            graph["cluster"][f] for f in froms if f in graph["cluster"]
        }
        nclust = len(clusters)
        if nclust > CLUSTER_MAX:
            continue
        body_len = _body_len(content)
        strong = (
            nsrc <= STRONG_SOURCES
            and inbound <= STRONG_INBOUND
            and nclust <= STRONG_CLUSTER
        )
        grade = "strong" if strong else "medium"
        # A person candidate notes whether an absorption-target org hub exists —
        # lets the Desk branch ②′ absorption vs demotion without grep (the
        # absorption default holds only when the target hub exists).
        hint = ""
        if _kind(content) == "person":
            targets = _absorb_targets(content, org_hubs)
            hint = (
                f" · absorption-target org hub exists: "
                f"{', '.join(f'[[{t}]]' for t in targets[:3])} → consider ②′ absorption"
                if targets
                else " · no absorption-target org hub → demotion direction"
            )
        issues.append(
            f"  [{grade}] {node_id}: sources {nsrc}·inbound {inbound}·"
            f"cluster {nclust}·body {body_len} chars — plain-text demotion/deletion candidate "
            f"(desk secondary gate: narrative centrality / figure importance / redirect inbound on deletion)"
            f"{hint}"
        )
    return issues, resolved


def run(fix: bool = False) -> int:
    """Entry point for `python tools/lint.py hub demotion`.

    `fix` accepted for signature parity but ignored — demotion/deletion is
    finalized in the desk qualitative gate + graph-integrity handling (inbound
    redirect / plain-text substitution).
    """
    del fix
    graph = _load_graph()
    org_hubs = _org_hub_stems()
    prose_nav = _prose_nav_stems()
    all_issues: list[str] = []
    total = 0
    resolved = 0
    for directory, dir_label in HUB_SPECS:
        if directory.exists():
            total += len(iter_hub_files(directory))
        iss, res = _check_directory(directory, dir_label, graph, org_hubs, prose_nav)
        all_issues.extend(iss)
        resolved += res

    resolved_note = (
        f" · gate-resolved {resolved} excluded (Desk-gate finalized: full·delegated·absorbed)"
        if resolved else ""
    )
    if all_issues:
        strong = sum(1 for i in all_issues if "[strong]" in i)
        print(
            f"\n[hub demotion: {len(all_issues)} demotion/deletion candidate(s) (strong {strong}) "
            f"across {total} L2-2 entity+concept file(s){resolved_note}]"
        )
        for i in all_issues:
            print(i)
        print(
            "\nADVISORY — full hub → plain-text demotion/deletion candidate first-pass triage "
            "(feedback_no_single_source_stub: a stub is justified only with ≥3 citations, "
            "multiple clusters, and a core narrative role; single-source/isolated ones are demoted). "
            "Single-source ∩ low inbound ∩ single cluster. Finalized in the desk secondary gate + "
            "graph-integrity handling — `--fix` not provided."
        )
        return 1

    print(
        f"OK - L2-2 hub demotion: 0 demotion/deletion candidates ({total} entity+concept files{resolved_note})"
    )
    return 0


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true")
    args = ap.parse_args()
    sys.exit(run(fix=args.fix))
