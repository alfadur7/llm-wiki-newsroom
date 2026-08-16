"""Native-free clustering path — artefact reuse + Louvain fallback.

Deliberately does NOT assert that the fallback reproduces the committed
partition. This corpus's hub subgraph is 11 nodes / 3 clusters, a size at
which every modularity optimiser agrees — an equality assertion there passes
for a badly broken implementation while reading as verification. What is
genuinely checkable at this size: the reuse guard rejects an artefact that no
longer describes the graph, and the fallback returns a complete, deterministic
partition. Backend *quality* is not a unit-test question; `lint graph drift`
owns that, and it deliberately refuses to run without the native backend.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def no_native(monkeypatch):
    """Simulate a platform with no igraph/leidenalg wheels (e.g. Termux)."""
    for name in ("igraph", "leidenalg"):
        monkeypatch.setitem(sys.modules, name, None)


def test_backend_reports_louvain_without_native(no_native):
    from _build.clusters import _leiden_backend

    assert _leiden_backend() == "louvain"


def test_committed_partition_reused_when_graph_unchanged():
    from _build.clusters import _committed_partition, build_hub_graph

    G, _labels, data, *_ = build_hub_graph(verbose=False)
    committed = json.loads(
        (ROOT / "graph" / "_clusters.json").read_text(encoding="utf-8")
    )

    reused = _committed_partition(G, data)
    assert reused is not None, "unchanged graph should reuse the committed partition"
    assert {frozenset(c) for c in reused} == {
        frozenset(c["members"]) for c in committed["clusters"]
    }


def test_committed_partition_rejected_when_graph_changed():
    """The guard is the whole point of the reuse path — a structurally changed
    graph must fall through to a real partition run, never reuse a stale one."""
    from _build.clusters import _committed_partition, build_hub_graph

    G, _labels, data, *_ = build_hub_graph(verbose=False)
    changed = {**data, "edges": data["edges"][:-1]}

    assert _committed_partition(G, changed) is None


def test_committed_partition_rejected_when_membership_incomplete():
    """Fingerprint match is not enough — a hand-edited or partially written
    artefact that no longer covers every hub must not become the answer."""
    from _build.clusters import _committed_partition, build_hub_graph

    G, _labels, data, *_ = build_hub_graph(verbose=False)
    G.add_node("entities/_not-in-the-committed-partition.md")

    assert _committed_partition(G, data) is None


def test_louvain_fallback_partitions_every_hub(no_native):
    from _build.clusters import RESOLUTION, SEED, _run_leiden, build_hub_graph

    G, *_ = build_hub_graph(verbose=False)
    comms = _run_leiden(G, resolution=RESOLUTION, seed=SEED)

    assert {n for c in comms for n in c} == set(G.nodes()), "fallback dropped hubs"
    assert sum(len(c) for c in comms) == G.number_of_nodes(), "hub in two communities"
    assert comms == _run_leiden(
        G, resolution=RESOLUTION, seed=SEED
    ), "same seed must give the same partition"
