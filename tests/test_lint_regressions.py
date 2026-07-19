"""Audit regression target tests — catches recurrences of the "copy then edit only
one side" class, such as divergent lint verdicts and F4 lint-ification."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_w2_unmeasurable_is_pass_in_both_paths():
    """A2/F5 regression — an unmeasurable body is PASS (displayed as n/a) identically for L2-3 and L2-4.

    Previously: L2-3 serialized inf→None→⚠️, while L2-4 gave inf→✅, opposite verdicts for the same state.
    """
    import overview  # tools/_lint/ — includes manifest/skill loading (assumes the repo)

    m = {
        "total": 200, "lead_density": 1.0, "body_density": 0.0,
        "lead_body_ratio": None,  # serialized representation of inf = unmeasurable
        "dup_total": 0, "contradiction_refs": 1,
        "r1_hot": [], "r2_violations": [], "b1_hits": [],
        "l1_violations": [], "l2_violations": [], "l3_violations": [],
        "s6_long": [], "s6_para_anti": [],
        "g1_grade_meta": 99, "g2_cite_type_meta": 99,
        "duplicates": [],
    }
    lines = overview._format_metrics_line(m)
    w2_segment = next(seg for seg in lines[0].split("  ") if seg.startswith("W2"))
    assert "ratio=n/a" in w2_segment and "✅" in w2_segment


def test_paragraph_count_is_module_level_single_definition():
    """F5 regression — prevent recurrence of nested duplication (2 copies) of _paragraph_count."""
    import overview

    src = (ROOT / "tools" / "_lint" / "overview.py").read_text(encoding="utf-8")
    assert src.count("def _paragraph_count") == 1
    assert overview._paragraph_count("a\n\nb\n\nc") == 3
    assert overview._paragraph_count("") == 1  # minimum 1 (denominator protection)


def test_skeleton_overview_copies_stay_in_lockstep():
    """Audit regression — `_skeleton_overview` is deliberately duplicated between the
    builder (`_build/clusters.py`, which writes the skeleton) and the lint SoT
    (`_lint/overview.py`, which checks it). The two must emit byte-identical output or
    the lint flags the builder's own product. This asserts the function bodies stay
    identical (docstrings excluded) so a future edit to one copy fails loudly here."""
    import ast

    def _body(path):
        src = path.read_text(encoding="utf-8")
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.FunctionDef) and node.name == "_skeleton_overview":
                if node.body and isinstance(node.body[0], ast.Expr) and isinstance(
                    getattr(node.body[0], "value", None), ast.Constant
                ):
                    node.body = node.body[1:]  # drop the docstring
                return ast.dump(node)
        raise AssertionError(f"_skeleton_overview not found in {path}")

    build = _body(ROOT / "tools" / "_build" / "clusters.py")
    lint = _body(ROOT / "tools" / "_lint" / "overview.py")
    assert build == lint, "_skeleton_overview drifted between the builder and the lint SoT"


def test_demotion_excludes_prose_embedded_hub(tmp_path):
    """measurement-root regression — a hub embedded only in overview/synthesis/timeline/trail
    must be treated as nav-inbound and excluded from demotion candidates even when it rides on no graph edge.

    Previously (2026-06): the graph build did not emit prose-layer origin edges, so a hub embedded
    only in an overview (Appier, Similarweb, etc.) never saw its nav in the demotion lint and
    recurred as a false-strong demotion candidate every sweep. Fixed by scanning `_prose_nav_stems` directly.
    """
    import hub_demotion

    d = tmp_path / "entities"
    d.mkdir()
    hub = d / "테스트오펀.md"
    hub.write_text(
        '---\ntitle: "테스트오펀"\ntype: entity\nkind: org\n'
        "sources: [single-src]\n---\n## Overview\n짧은 본문.\n",
        encoding="utf-8",
    )
    empty_graph = {"inbound": {}, "cluster": {}}

    # no prose embed → detected as an isolated demotion candidate (strong)
    iss, _ = hub_demotion._check_directory(d, "entities", empty_graph, set(), set())
    assert any("테스트오펀" in i for i in iss)

    # the same hub embedded in the prose layer → excluded as nav-inbound (0 omissions)
    iss2, _ = hub_demotion._check_directory(
        d, "entities", empty_graph, set(), {"테스트오펀"}
    )
    assert not any("테스트오펀" in i for i in iss2)


def test_meta_lint_regex_hoisting_check_active():
    """F4 regression — the shared-regex redefinition detection check is alive in the meta lint,
    and there is currently no redefinition in tools/."""
    proc = subprocess.run(
        [sys.executable, "tools/lint.py", "meta"],
        capture_output=True, text=True, encoding="utf-8", cwd=ROOT, timeout=300,
    )
    assert proc.returncode in (0, 1)  # 1 = clone-environment artifacts (.claude/memory/, etc.) allowed
    assert "OK - shared FRONTMATTER*/WIKILINK*/AUTO* regexes defined only in _lib" in proc.stdout


def test_overview_sources_total_matches_catalog_membership():
    """Reground regression — the overview AUTO:SOURCES "N total" and the source
    catalog must apply ONE membership rule.

    Previously `_group_sources_by_cluster` fell back to the primary cluster for a
    source below threshold in every cluster, while `_render_sources_block` counted
    only `weight >= threshold` — so an orphan source appeared in the catalog but
    was missing from the overview total. Both numbers are generated, so no author
    could reconcile them by editing a page; the fix belongs to the build. This
    pins the two rules together, because a membership rule duplicated across two
    functions diverges again (copyeditor.md § Risk Mitigation Design)."""
    from _build import clusters as C

    clusters_data = {
        "source_weight_threshold": 0.3,
        "clusters": [{"slug": "c1", "name": "Cluster One"},
                     {"slug": "c2", "name": "Cluster Two"}],
        "source_assignments": {
            "sources/strong.md": {"primary": "c1", "weights": {"c1": 0.9, "c2": 0.4}},
            # below threshold everywhere → catalog falls back to its primary (c1)
            "sources/orphan.md": {"primary": "c1", "weights": {"c1": 0.2, "c2": 0.1}},
        },
    }
    sources = [
        ("Strong", "sources/strong.md", "", "", "2026-01-01", ""),
        ("Orphan", "sources/orphan.md", "", "", "2026-01-02", ""),
    ]

    cluster_files, _ = C._group_sources_by_cluster(sources, clusters_data)
    for cluster in clusters_data["clusters"]:
        slug = cluster["slug"]
        m = re.search(r"(\d+) total", C._render_sources_block(cluster, clusters_data))
        assert m, f"cluster {slug}: rendered block has no total"
        assert int(m.group(1)) == len(cluster_files.get(slug, [])), (
            f"cluster {slug}: overview total {m.group(1)} != "
            f"catalog membership {len(cluster_files.get(slug, []))}"
        )

    # The orphan is exactly what the divergence used to hide.
    assert len(cluster_files["c1"]) == 2


def test_f2_claim_stat_checked_at_every_occurrence(tmp_path, monkeypatch):
    """Reground regression — a stale restatement of the canonical claim total
    mid-body must fail F2, not only a stale head sentence.

    A delta-only re-ground edits the head and leaves earlier copies behind; the
    previous head-only `.search()` passed such a document."""
    import contradiction as CT

    md = tmp_path / "contradiction.md"

    def _write(head_n, body_n):
        md.write_text(
            f"# Contradictions\n\n"
            f"**{head_n} source-to-source contradictions** across the corpus.\n\n"
            f"## Synopsis\n\n"
            f"Restated later: **{body_n} source-to-source contradictions**.\n",
            encoding="utf-8",
        )

    monkeypatch.setattr(CT, "CONTRADICTIONS_MD_PATH", md)

    # Assert on the claim-stat drift specifically: this fixture is a minimal
    # document, so unrelated criteria (S1 sections, the theme stat) fail anyway.
    _write(7, 7)  # every occurrence agrees with the SoT
    issues, _ = CT._check_contradictions_md(set(), set(), 7, 0)
    assert not any("claims declared" in i for i in issues), issues

    _write(7, 5)  # head correct, mid-body stale — the case head-only checking missed
    issues, _ = CT._check_contradictions_md(set(), set(), 7, 0)
    assert any("claims declared=5 actual=7" in i for i in issues), issues


def test_reground_status_surfaces_superseded_but_open_claims():
    """Reground follow-up trigger — a claim whose own source reports the dispute
    settled (`type: superseded`) while it stays `status: open` is surfaced; every
    other type/status combination stays silent (the surface must be zero-FP)."""
    import contradiction as CT

    assert CT._reground_status_line([]) is None
    assert CT._reground_status_line([{"id": "a", "type": "soft", "status": "open"}]) is None
    assert CT._reground_status_line(
        [{"id": "b", "type": "superseded", "status": "resolved"}]
    ) is None

    line = CT._reground_status_line([
        {"id": "c1", "type": "superseded", "status": "open"},
        {"id": "c2", "type": "real", "status": "open"},
    ])
    assert line is not None
    assert "1 superseded claim(s) still open" in line
    assert "c1" in line and "c2" not in line
