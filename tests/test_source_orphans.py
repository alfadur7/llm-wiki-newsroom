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
