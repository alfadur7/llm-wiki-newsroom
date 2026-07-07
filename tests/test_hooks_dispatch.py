"""`.claude/hooks/dispatch.py` unit tests — the behavioral contract of the F3 unified dispatcher.

Contract inherited from the 6 legacy hooks: guard (lint-report asymmetry) is exit 2 + stderr,
advisory is exit 0 + a single stdout JSON additionalContext (simultaneous firings merged),
new content with an AUTO marker skips the incremental advisory, `_catalog`/`_archive` excluded.
"""
import json

import check_bullet_depth
import dispatch


def _payload(capsys) -> str:
    out = capsys.readouterr().out
    if not out.strip():
        return ""
    return json.loads(out)["hookSpecificOutput"]["additionalContext"]


def _input(tool, path, **fields):
    return {"tool_name": tool, "tool_input": {"file_path": path, **fields}}


# ---------------------------------------------------------------- pre phase

def test_lint_report_asymmetry_blocks(capsys):
    rc = dispatch.run_pre(_input(
        "Write", "/x/lint-report.md",
        content="- 🔴 foo — member_jaccard=0.5"))
    assert rc == 2
    assert "ASYMMETRY" in capsys.readouterr().err


def test_lint_report_symmetric_passes(capsys):
    rc = dispatch.run_pre(_input(
        "Write", "/x/lint-report.md",
        content="- 🔴 a — member_jaccard=1\n- 🟢 b — claim_jaccard=1"))
    assert rc == 0
    assert capsys.readouterr().err == ""


def test_lint_report_partial_edit_symmetric_file_no_false_block(tmp_path, capsys):
    # Partial Edit touching only the overview group, on a file that already has
    # BOTH groups on disk → guard reconstructs the full file and must NOT block.
    f = tmp_path / "lint-report.md"
    f.write_text("- 🔴 foo — member_jaccard=1\n- 🟢 bar — claim_jaccard=1\n", encoding="utf-8")
    rc = dispatch.run_pre(_input(
        "Edit", str(f),
        old_string="- 🟢 bar — claim_jaccard=1\n",
        new_string="- 🟢 bar — claim_jaccard=1\n- 🔴 baz — member_jaccard=0.4\n"))
    assert rc != 2
    assert capsys.readouterr().err == ""


def test_lint_report_partial_edit_asymmetric_file_still_blocks(tmp_path, capsys):
    # Disk file has only the overview group → a single-group Edit keeps it
    # genuinely asymmetric, so the guard must still fire.
    f = tmp_path / "lint-report.md"
    f.write_text("- 🔴 foo — member_jaccard=1\n", encoding="utf-8")
    rc = dispatch.run_pre(_input(
        "Edit", str(f),
        old_string="- 🔴 foo — member_jaccard=1\n",
        new_string="- 🔴 foo — member_jaccard=1\n- 🔴 baz — member_jaccard=0.4\n"))
    assert rc == 2
    assert "ASYMMETRY" in capsys.readouterr().err


def test_lint_report_edit_unreadable_file_falls_back_to_fragment(capsys):
    # No file on disk → expected_text returns None → guard falls back to the
    # raw fragment, preserving the long-standing fragment-only behavior.
    rc = dispatch.run_pre(_input(
        "Edit", "/no/such/lint-report.md",
        old_string="x", new_string="- 🔴 foo — member_jaccard=1"))
    assert rc == 2
    assert "ASYMMETRY" in capsys.readouterr().err


def test_lint_report_all_stable_group_no_false_block(capsys):
    # Real-world format (wiki-lint.md): 🟢-stable blocks are `🟢 <slug> — drift
    # stable` with NO *_jaccard metric. A contradiction group that is entirely
    # stable still wrote per-target blocks (under its section heading) and must
    # NOT be flagged as a missing/asymmetric group.
    content = (
        "### overview drift\n"
        "- 🔴 licensing-open-washing — member_jaccard=0.64 → `/wiki-lint overview licensing-open-washing --fix`\n"
        "- 🟢 open-source-ai-definition — drift stable\n"
        "\n"
        "### contradiction drift\n"
        "- 🟢 open-training-data-requirement — drift stable\n"
        "- 🟢 other-fragmentary — drift stable\n"
    )
    rc = dispatch.run_pre(_input("Write", "/x/lint-report.md", content=content))
    assert rc == 0
    assert capsys.readouterr().err == ""


def test_lint_report_summarized_group_still_blocks(capsys):
    # Genuine asymmetry: overview detailed per-target, contradiction collapsed to
    # a prose summary ("N drifts") with no per-target blocks → still blocks.
    content = (
        "### overview drift\n"
        "- 🔴 licensing-open-washing — member_jaccard=0.64 → `/wiki-lint overview licensing-open-washing --fix`\n"
        "\n"
        "### contradiction drift\n"
        "3 themes drifted (summary)\n"
    )
    rc = dispatch.run_pre(_input("Write", "/x/lint-report.md", content=content))
    assert rc == 2
    assert "ASYMMETRY" in capsys.readouterr().err


def test_guideline_edit_advisory(capsys):
    rc = dispatch.run_pre(_input("Edit", "/r/.claude/commands/wiki-lint.md", new_string="- a"))
    assert rc == 0
    assert "[minimality-advisory] GUIDELINE EDIT" in _payload(capsys)


def test_proposal_validation_advisory_craft_prose(capsys):
    # layers file + desk/reporter/columnist agents fire the reflex (merges with the
    # guideline minimality advisory since layers ⊂ GUIDE_DIRS).
    for p in ("/r/.claude/layers/hub.md", "/r/.claude/agents/desk.md",
              "/r/.claude/agents/reporter.md", "/r/.claude/agents/columnist.md"):
        dispatch.run_pre(_input("Edit", p, new_string="- a"))
        assert "[proposal-validation-advisory]" in _payload(capsys), p


def test_proposal_validation_advisory_scope(capsys):
    # editor-in-chief (routing)·copyeditor (lint)·README (matrix) are deliberately out.
    for p in ("/r/.claude/agents/editor-in-chief.md", "/r/.claude/agents/copyeditor.md",
              "/r/.claude/agents/README.md"):
        dispatch.run_pre(_input("Edit", p, new_string="- a"))
        assert "[proposal-validation-advisory]" not in _payload(capsys), p


def test_plan_file_advisory(capsys):
    dispatch.run_pre(_input("Write", "/r/plans/x.md", content="plan"))
    assert "5-step self-check" in _payload(capsys)


def test_scratch_advisory_write_only(capsys, monkeypatch):
    # _REPO_ROOT is derived from the hook's own location, so pin it to the fake
    # root here to test the exact-match regardless of the real clone directory.
    monkeypatch.setattr(dispatch, "_REPO_ROOT", "/home/u/llm-wiki-newsroom")
    dispatch.run_pre(_input("Write", "/home/u/llm-wiki-newsroom/tmp.py", content="x"))
    assert "[scratch-location-advisory]" in _payload(capsys)
    # Edit does not trigger scratch (the legacy hook was limited to PreToolUse Write).
    dispatch.run_pre(_input("Edit", "/home/u/llm-wiki-newsroom/tmp.py", new_string="x"))
    assert _payload(capsys) == ""


def test_unrelated_file_silent(capsys):
    assert dispatch.run_pre(_input("Write", "/x/src/app.ts", content="x")) == 0
    assert capsys.readouterr().out == ""


def test_ponytail_advisory_tools_python(capsys):
    # .py under tools/ injects the ponytail skill-load instruction on both Write and Edit (rel label = after tools/).
    dispatch.run_pre(_input("Write", "/r/tools/_lint/new_check.py", content="x=1"))
    ctx = _payload(capsys)
    assert "[ponytail-advisory]" in ctx and "_lint/new_check.py" in ctx
    dispatch.run_pre(_input("Edit", "/r/tools/export.py", new_string="y=2"))
    assert "[ponytail-advisory]" in _payload(capsys)


def test_ponytail_advisory_scope(capsys):
    # .py outside tools/ and non-.py inside tools/ do not fire.
    assert dispatch.run_pre(_input("Write", "/r/scratch/foo.py", content="x")) == 0
    assert capsys.readouterr().out == ""
    dispatch.run_pre(_input("Write", "/r/tools/README.md", content="x"))
    assert capsys.readouterr().out == ""


def test_protected_path_blocks_build_output(capsys):
    for p in ("/r/wiki/index.md", "/r/graph/_clusters.json",
              "/r/wiki/_backlinks.json", "/r/wiki/sources/_catalog-bank.md",
              "/r/wiki/contradictions/_contradictions.json"):
        rc = dispatch.run_pre(_input("Edit", p, new_string="x"))
        assert rc == 2, p
        assert "[protected-path-guard] BLOCKED" in capsys.readouterr().err


def test_protected_path_blocks_raw_originals(capsys):
    rc = dispatch.run_pre(_input("Edit", "/r/raw/NewsScrap/foo.md", new_string="x"))
    assert rc == 2
    assert "immutable" in capsys.readouterr().err


def test_protected_path_allows_exceptions(capsys):
    # Allowed: themes JSON re-derived by Claude, human-edited cluster_labels, and queue append files.
    for p in ("/r/wiki/contradictions/_contradictions_themes.json",
              "/r/graph/cluster_labels.json",
              "/r/raw/_inbox.md", "/r/raw/_archive.md"):
        rc = dispatch.run_pre(_input("Edit", p, new_string="x"))
        assert rc == 0, p
        assert capsys.readouterr().err == ""


# ---------------------------------------------------------------- post phase

def test_entity_stub_merged_payload(capsys):
    rc = dispatch.run_post(_input("Write", "/r/wiki/entities/테스트.md", content="본문"))
    assert rc == 0
    ctx = _payload(capsys)
    assert "[stub-advisory]" in ctx and "[incremental-lint-advisory]" in ctx
    assert ctx.count("\n\n---\n\n") == 1  # two advisories merged into a single payload


def test_auto_marker_content_skips_incremental(capsys):
    dispatch.run_post(_input("Edit", "/r/wiki/overviews/foo.md",
                             new_string="<!-- AUTO:STATS BEGIN -->"))
    assert capsys.readouterr().out == ""  # overview is not a stub + AUTO → no firing


def test_synthesis_target_command(capsys):
    dispatch.run_post(_input("Edit", "/r/wiki/syntheses/foo.md", new_string="a"))
    assert "python tools/lint.py synthesis foo" in _payload(capsys)


def test_catalog_and_archive_excluded(capsys):
    dispatch.run_post(_input("Write", "/r/wiki/sources/_catalog.md", content="a"))
    dispatch.run_post(_input("Write", "/r/wiki/entities/_archive/x.md", content="a"))
    assert capsys.readouterr().out == ""


# ---------------------------------------------------------------- bullet depth

def test_bullet_depth_analyze_flags_stuffed_bullet():
    long_item = "- " + "항목 (a) 첫째다. (b) 둘째다. (c) 셋째다. " * 6
    siblings = "\n".join(["- 짧은 형제"] * 5)
    data = {"tool_input": {"file_path": "/x/CLAUDE.md",
                           "content": siblings + "\n" + long_item + "\n"}}
    assert "[depth-check]" in check_bullet_depth.analyze(data)


def test_bullet_depth_analyze_clean():
    data = {"tool_input": {"file_path": "/x/CLAUDE.md",
                           "content": "- a\n- b\n- c\n- d\n"}}
    assert check_bullet_depth.analyze(data) == ""
