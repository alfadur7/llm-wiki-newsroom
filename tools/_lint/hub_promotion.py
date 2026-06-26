"""L2-2 stub → full hub promotion candidate triage advisory — entities / concepts.

Derived from a PoC (2026-05-24, 43 measured): a high-value stub that should be
grown into a full hub (many citations but a thin body) **cannot be caught without
false negatives by a sources-count threshold alone**.
  * Strong promotion candidates genuinely exist at src5 (IBK기업은행) and
    src6 (RedTeaming) → raising the threshold to ≥10/16 misses them.
  * src17 (CloudMigration) and src8 (한국클라우드CSP) have bodies that already
    completed cross-source integration and are self-sufficient → looking at
    sources alone over-triggers.

The real discriminator is the **intersection of "many citations (inbound) ∩ thin
body (stub)" + inbound cluster spread**, and inbound·cluster are computed
deterministically from the graph. This module handles only that first-pass auto
triage. Promotion is finalized by the desk's lightweight secondary gate (overlap
with an adjacent hub's integration area / possibility of absorption into a parent
concept / skew toward a single subject or event group) — semantic judgment, so
`--fix` is not supported.

Detection conditions (AND):
  * stub — body < STUB_MAX chars after stripping frontmatter + HTML/AUTO
  * sources ≥ SOURCES_MIN (many-citations floor)
  * inbound ≥ INBOUND_HOT  OR  inbound distinct clusters ≥ CLUSTER_SPREAD
    (many citations or cross-cluster integration value)
Grade: strong = both inbound·cluster met / medium = only one.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import read_text_cached  # noqa: E402
from _hub_common import (  # noqa: E402
    HUB_SPECS,
    iter_hub_files,
    body_len as _body_len,
    gate as _gate,
    kind as _kind,
    load_graph as _load_graph,
    sources_count as _sources_count,
)

# Thresholds — PoC 43-item calibration:
#   STUB_MAX 1500: cleanup C bucket boundary (B1/B2 are already fully reviewed).
#   SOURCES_MIN 5: strong candidates genuinely exist in the 5-9 range (IBK src5) → floor 5. <5 almost never promotes.
#   INBOUND_HOT 10: core "many citations but thin body" signal (RedTeaming 13·IBK 10).
#   CLUSTER_SPREAD 3: cross-cluster integration value (SK그룹 4·IBK 3 = promote, single-focus weak).
STUB_MAX = 1500
SOURCES_MIN = 5
INBOUND_HOT = 10
CLUSTER_SPREAD = 3
# "strong (top-priority)" grade — the first-pass floor (zero false negatives) is
# inbound≥10 OR cluster≥3, but stubs hitting that floor are the majority of the
# backlog (many-citation stubs are rife in the wiki), which blurs triage priority.
# "strong" narrows to the triple many-sources ∩ high-inbound ∩ wide spread to make
# the desk secondary gate's top-priority batch clear. The rest that meet the floor are "medium".
STRONG_SOURCES = 10
STRONG_INBOUND = 20
STRONG_CLUSTER = 4


def _check_directory(directory: Path, dir_label: str, graph: dict) -> tuple[list[str], list[str], int]:
    issues: list[str] = []
    person_issues: list[str] = []
    resolved = 0
    if not directory.exists():
        return issues, person_issues, resolved
    for path in iter_hub_files(directory):
        content = read_text_cached(path)
        if _gate(content):
            resolved += 1
            continue  # Desk-gate delegated/absorbed finalized — excluded from triage
        body_len = _body_len(content)
        if body_len >= STUB_MAX:
            continue  # not a stub — B1/B2 already fully reviewed
        nsrc = _sources_count(content)
        if nsrc < SOURCES_MIN:
            continue
        node_id = f"{dir_label}/{path.name}"
        froms = graph["inbound"].get(node_id, [])
        inbound = len(froms)
        clusters = {
            graph["cluster"][f] for f in froms if f in graph["cluster"]
        }
        nclust = len(clusters)
        if not (inbound >= INBOUND_HOT or nclust >= CLUSTER_SPREAD):
            continue  # first-pass floor (zero false negatives): many citations or cross-cluster
        # A person (kind:person) defaults to absorption into their org — full is
        # only for the cross-cluster independent-actor exception (hub.md ②′).
        # Kept separate from the org/product promotion triage.
        if _kind(content) == "person":
            if nclust >= CLUSTER_SPREAD:
                person_issues.append(
                    f"  [full-review] {node_id}: body {body_len} chars·sources {nsrc}·"
                    f"inbound {inbound}·cluster {nclust} — cross-cluster ≥{CLUSTER_SPREAD} full hub review "
                    f"(desk secondary: reducibility to a single org / cross-cluster independence / personal narrative as the main subject)"
                )
            else:
                person_issues.append(
                    f"  [absorb-recommended] {node_id}: body {body_len} chars·sources {nsrc}·"
                    f"inbound {inbound}·cluster {nclust} — absorption into the org hub is default (recommend gate:absorbed)"
                )
            continue
        strong = (
            nsrc >= STRONG_SOURCES
            and inbound >= STRONG_INBOUND
            and nclust >= STRONG_CLUSTER
        )
        grade = "strong" if strong else "medium"
        issues.append(
            f"  [{grade}] {node_id}: body {body_len} chars (stub)·sources {nsrc}·"
            f"inbound {inbound}·cluster {nclust} — full hub promotion candidate "
            f"(desk secondary gate: check adjacent-hub overlap / parent-concept absorption / subject skew)"
        )
    return issues, person_issues, resolved


def run(fix: bool = False) -> int:
    """Entry point for `python tools/lint.py hub promotion`.

    `fix` accepted for signature parity but ignored — promotion is finalized in
    the desk qualitative gate + the columnist full-hub authoring cycle.
    """
    del fix
    graph = _load_graph()
    all_issues: list[str] = []
    all_person: list[str] = []
    total = 0
    resolved = 0
    for directory, dir_label in HUB_SPECS:
        if directory.exists():
            total += len(iter_hub_files(directory))
        iss, persons, res = _check_directory(directory, dir_label, graph)
        all_issues.extend(iss)
        all_person.extend(persons)
        resolved += res

    # Person triage — absorption into the org is the default / cross-cluster full
    # is the exception (hub.md ②′). Shown separately from org/product promotion
    # candidates. Both are advisory since they're desk-secondary-gate territory.
    if all_person:
        full_n = sum(1 for i in all_person if "[full-review]" in i)
        print(
            f"\n[person (kind:person) triage: {len(all_person)} "
            f"(full-review {full_n}·absorb-recommended {len(all_person) - full_n})]"
        )
        for i in all_person:
            print(i)
        print(
            "\nADVISORY — a person defaults to absorption into the org hub (`gate: absorbed`); "
            "a full hub is only for the exception of (irreducible to a single org) ∩ cross-cluster ∩ "
            "personal narrative as the main subject (.claude/layers/hub.md ②′). Finalized in the desk secondary gate."
        )

    resolved_note = (
        f" · gate-resolved {resolved} excluded (Desk-gate finalized: full·delegated·absorbed)"
        if resolved else ""
    )
    if all_issues:
        strong = sum(1 for i in all_issues if "[strong]" in i)
        print(
            f"\n[hub promotion: {len(all_issues)} promotion candidate(s) (strong {strong}) "
            f"across {total} L2-2 entity+concept file(s){resolved_note}]"
        )
        for i in all_issues:
            print(i)
        print(
            "\nADVISORY — stub → full hub promotion candidate first-pass triage "
            "(.claude/layers/hub.md \"stub authoring\" promotion criteria). "
            "Many citations (inbound) ∩ thin body (stub) ∩ cross-cluster. "
            "Promotion finalized in the desk secondary gate — `--fix` not provided."
        )
        return 1

    print(
        f"OK - L2-2 hub promotion: 0 promotion candidates ({total} entity+concept files{resolved_note})"
    )
    return 0


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true")
    args = ap.parse_args()
    sys.exit(run(fix=args.fix))
