"""`build.py clusters --anchored` — declared anchors stay in their cluster.

The graph is built so a pure cold run puts A and C together (one heavy A–C
edge); the pinned run must keep A·B and C·D apart, and the non-anchor hubs E·F
must still land by their own links. The prior partition is deliberately wrong,
so a run that warm-started from it instead of pinning would fail too.
"""
import json

import pytest

pytest.importorskip("leidenalg")
pytest.importorskip("igraph")

from _build import clusters  # noqa: E402


def test_anchored_pins_anchors(tmp_path, monkeypatch):
    hubs = [f"concepts/{x}.md" for x in "ABCDEF"]
    A, B, C, D, E, F = hubs
    edges = [(A, B, 2), (C, D, 2), (A, C, 20), (F, C, 1), (F, D, 1), (E, A, 1), (E, B, 1)]
    graph = {"nodes": [{"id": h, "label": h} for h in hubs],
             "edges": [{"from": a, "to": b, "type": "EXTRACTED"}
                       for a, b, n in edges for _ in range(n)]}
    prior = {"clusters": [{"members": [A, C, F]}, {"members": [B, D, E]}], "hub_assignments": {}}
    labels = {"labels": [
        {"slug": "x", "name": "X", "color": "#000000", "anchor_members": [A, B]},
        {"slug": "y", "name": "Y", "color": "#111111", "anchor_members": [C, D]},
    ]}
    gp, op, lp = tmp_path / "g.json", tmp_path / "c.json", tmp_path / "l.json"
    gp.write_text(json.dumps(graph), encoding="utf-8")
    op.write_text(json.dumps(prior), encoding="utf-8")
    lp.write_text(json.dumps(labels), encoding="utf-8")
    monkeypatch.setattr(clusters, "GRAPH_PATH", gp)
    monkeypatch.setattr(clusters, "OUTPUT_PATH", op)
    monkeypatch.setattr(clusters, "LABELS_PATH", lp)
    monkeypatch.setattr(clusters, "WIKI", tmp_path)

    clusters.run(anchored=True)

    asg = json.loads(op.read_text(encoding="utf-8"))["hub_assignments"]
    assert asg[A] == asg[B] == asg[E]
    assert asg[C] == asg[D] == asg[F]
    assert asg[A] != asg[C]
