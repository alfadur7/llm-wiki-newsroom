"""Regression coverage for the hub `sources:` sync — the rewrite must leave
`last_updated` alone.

A hub's `last_updated` is its narrative date (`.claude/layers/hub.md`). Bumping
it on a pure `sources:` sync re-dates the hub as freshly authored, which makes
`upstream_max_date > last_updated` structurally impossible and hides a lagging
narrative from the staleness lint. New-source arrival reaches downstream pages
through the composite propagation date in `tools/_build/dependencies.py`.
"""
import source_orphans


def test_sources_sync_does_not_bump_last_updated():
    text = "---\ntitle: X\nsources: [a]\nlast_updated: 2026-06-26\n---\n\n## Overview\n\nBody.\n"
    out = source_orphans._rewrite_sources(text, ["a", "b"])
    assert "sources: [a, b]" in out
    assert "last_updated: 2026-06-26" in out


def test_block_style_sources_normalized_without_touching_date():
    text = "---\ntitle: X\nsources:\n  - a\n  - b\nlast_updated: 2026-06-26\n---\n\nBody.\n"
    out = source_orphans._rewrite_sources(text, ["a", "b", "c"])
    assert "sources: [a, b, c]" in out
    assert "  - a" not in out  # block items consumed, not left orphaned
    assert "last_updated: 2026-06-26" in out


_HUB = "---\ntitle: H\ntype: entity\nsources: [{s}]\n---\n\n## Overview\nBody{cite}\n"


def _git(root, *a):
    import subprocess
    subprocess.run(["git", *a], cwd=root, check=True, capture_output=True)


def test_prune_only_dropped_links(tmp_path, monkeypatch):
    """`--fix` unregisters only a link the uncommitted source edit dropped: a
    pre-existing orphan entry and one the hub body still cites both stay."""
    w = tmp_path / "wiki"
    for d in ("entities", "concepts", "sources"):
        (w / d).mkdir(parents=True)
    (w / "entities" / "A.md").write_text(_HUB.format(s="s1, s2, s3, s4", cite=""), encoding="utf-8")
    (w / "entities" / "B.md").write_text(_HUB.format(s="s1", cite=" [[s1]]"), encoding="utf-8")
    (w / "sources" / "s1.md").write_text("## Connections\n- [[A]] [[B]]\n", encoding="utf-8")
    (w / "sources" / "s2.md").write_text("## Connections\n- no link\n", encoding="utf-8")  # orphan from the start
    (w / "sources" / "s3.md").write_text("## Connections\n- [[A]]\n", encoding="utf-8")
    (w / "sources" / "s4.md").write_text("## Connections\n- [[A]]\n", encoding="utf-8")
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "x")
    (w / "sources" / "s1.md").write_text("## Connections\n- link removed\n", encoding="utf-8")
    (w / "sources" / "s4.md").write_text("Edited.\n\n## Connections\n- [[A]]\n", encoding="utf-8")  # edited, link kept
    monkeypatch.setattr(source_orphans, "WIKI", w)
    assert source_orphans._apply_prune() == 1
    a = source_orphans._hub_sources((w / "entities" / "A.md").read_text(encoding="utf-8"))
    b = source_orphans._hub_sources((w / "entities" / "B.md").read_text(encoding="utf-8"))
    assert a == ["s2", "s3", "s4"]  # only the dropped link (s1) pruned
    assert b == ["s1"]  # hub body cites s1 directly — kept
