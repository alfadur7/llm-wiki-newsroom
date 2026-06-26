"""Audit regression target tests — catches recurrences of the "copy then edit only
one side" class, such as divergent lint verdicts and F4 lint-ification."""
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
        capture_output=True, text=True, cwd=ROOT, timeout=300,
    )
    assert proc.returncode in (0, 1)  # 1 = clone-environment artifacts (.claude/memory/, etc.) allowed
    assert "OK - shared FRONTMATTER*/WIKILINK*/AUTO* regexes defined only in _lib" in proc.stdout
