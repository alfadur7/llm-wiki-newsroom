"""L2-2 hub body density advisory lint — entities / concepts.

Promotes two patterns observed cumulatively across pages in the B1 batch 2 Desk
review into deterministic detection. A concept hub is navigational-anchor in
nature, so when its body bloats to deep-dive-report scale the separation of
responsibilities blurs and the `## Connections` section loses its nav-anchor
function and degenerates into a reference list.

Detected items:
  * Body length advisory — advisory when the body ≥ 12,000 chars after stripping
    frontmatter + HTML comments. Recommends distributing via sub-hub delegation
    (referencing `[[related hub]]`).
  * `## Connections` link count advisory — advisory when the connections section
    has ≥ 50 wikilinks. Recommends category grouping or removing multiple entries
    for a single entity.

`--fix` not supported — which H2 to delegate to a sub-hub and which links to
prune are semantic-judgment territory (handled in the columnist ADAPT cycle).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))
from _lib import WIKI, read_text_cached  # noqa: E402
from _hub_common import iter_hub_files, load_graph  # noqa: E402

import importlib.util as _ilu  # noqa: E402
# Measuring hub body density and `## Connections` grouping (the encyclopedic
# nav-anchor format) is owned by the encyclopedia-writing skill. central_anchor
# (inbound / whether it's an entity) is wiki-wide, so the orchestrator injects it.
_REPO_ROOT = Path(__file__).resolve().parents[2]
_MANIFEST = json.loads((_REPO_ROOT / ".claude" / "layers" / "_manifest.json").read_text(encoding="utf-8"))
_HUB_BUNDLE = _MANIFEST["hub"]["bundles"]["encyclopedia-writing"]
_enc_spec = _ilu.spec_from_file_location(
    "enc_checks_hub", _REPO_ROOT / ".claude" / "skills" / "encyclopedia-writing" / "checks.py"
)
enc_skill = _ilu.module_from_spec(_enc_spec)
_enc_spec.loader.exec_module(enc_skill)
_HUB_FN = _HUB_BUNDLE["fn"]
_HUB_PARAMS = _HUB_BUNDLE["params"]

ENTITIES_DIR = WIKI / "entities"
CONCEPTS_DIR = WIKI / "concepts"

HUB_SPECS = [
    (ENTITIES_DIR, "entities"),
    (CONCEPTS_DIR, "concepts"),
]

# The regex and stripping for measuring body density and `## Connections`
# grouping were moved into the encyclopedia-writing skill (evaluate_hub_body).
# This module handles only inbound / central_anchor / issue formatting.

# Thresholds — advisory lines set from B1 batch 1·2 measurements.
# Body 12,000 chars: a deep-dive range 4x the cleanup A bucket (≥3,000 chars)
# average. Connections section 50 links: observed the nav anchor → reference list
# degeneration in the FinancialAI 65-link case. 50 is a conservative hard advisory
# line. The actual threshold is SoT in the manifest (_HUB_PARAMS) — the advisory
# message also interpolates the manifest value directly so the threshold and the
# output cannot desync.

# Centrality recalibration — the body-length advisory targets hubs bloating
# PAST their navigational-anchor role. But two hub classes are legitimately
# content-rich and splitting them fragments coherent units:
#   1. entity hubs — single-subject pages (a company/bank/agency); length
#      reflects the subject's coverage breadth, not bloat.
#   2. top-centrality concept anchors — the most-linked concepts ARE the
#      navigational core, so breadth is expected.
# So the prose advisory is skipped for entity hubs and for any hub whose
# inbound EXTRACTED link count ≥ CENTRALITY_EXEMPT. The signal then focuses
# on lower-centrality concept hubs where sub-hub delegation genuinely helps.
CENTRALITY_EXEMPT = 100

def _check_body(content: str, path: Path, dir_label: str) -> list[str]:
    # Measuring body density and `## Connections` grouping was moved into the
    # encyclopedia-writing skill. central_anchor (entity or inbound≥CENTRALITY_EXEMPT)
    # is wiki-wide, so the orchestrator computes and injects it. Issue formatting
    # stays with the orchestrator.
    issues: list[str] = []
    inbound = len(load_graph()["inbound"].get(f"{dir_label}/{path.name}", []))
    central_anchor = dir_label == "entities" or inbound >= CENTRALITY_EXEMPT
    m = enc_skill.evaluate_hub_body(content, central_anchor=central_anchor, **_HUB_PARAMS)
    if m["body_fires"]:
        issues.append(
            f"  {dir_label}/{path.name}: body length {m['body_len']} chars "
            f"≥ {_HUB_PARAMS['body_len_advisory']:,} chars advisory — review separation "
            f"of the navigational-anchor responsibility (recommend sub-hub delegation)"
        )
    if m["link_fires"]:
        issues.append(
            f"  {dir_label}/{path.name}: `## Connections` wikilinks {m['yeongyeol_link_count']} "
            f"≥ {_HUB_PARAMS['yeongyeol_link_advisory']} (flat) advisory — recommend category "
            f"grouping (`###` subsections)"
        )
    return issues


def _check_directory(directory: Path, dir_label: str) -> list[str]:
    issues: list[str] = []
    if not directory.exists():
        return issues
    for path in iter_hub_files(directory):
        content = read_text_cached(path)
        issues.extend(_check_body(content, path, dir_label))
    return issues


def run(fix: bool = False) -> int:
    """Entry point for `python tools/lint.py hub body`.

    `fix` is accepted for signature parity but ignored — sub-hub delegation
    and link curation require semantic judgment (columnist ADAPT cycle).
    """
    del fix  # signature parity only; not actionable here.

    all_issues: list[str] = []
    total_files = 0
    for directory, dir_label in HUB_SPECS:
        if directory.exists():
            total_files += len(iter_hub_files(directory))
        all_issues.extend(_check_directory(directory, dir_label))

    if all_issues:
        print(
            f"\n[hub body: {len(all_issues)} advisory issue(s) across "
            f"{total_files} L2-2 entity+concept file(s)]"
        )
        for i in all_issues:
            print(i)
        print(
            f"\nADVISORY — L2-2 hub body density signals "
            f"(.claude/layers/hub.md \"body length / connections advisory\")."
        )
        print(
            f"       Body ≥ {_HUB_PARAMS['body_len_advisory']:,} chars → consider sub-hub delegation; "
            f"`## Connections` ≥ {_HUB_PARAMS['yeongyeol_link_advisory']} links → consider category grouping. "
            f"`--fix` not provided — semantic judgment required."
        )
        return 1

    print(
        f"OK - L2-2 hub body density: 0 advisories "
        f"({total_files} entity+concept files)"
    )
    return 0


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true")
    args = ap.parse_args()
    sys.exit(run(fix=args.fix))
