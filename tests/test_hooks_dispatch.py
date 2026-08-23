"""`.claude/hooks/dispatch.py` unit tests — the behavioral contract of the F3 unified dispatcher.

Contract inherited from the 6 legacy hooks: guard (lint-report asymmetry) is exit 2 + stderr,
advisory is exit 0 + a single stdout JSON additionalContext (simultaneous firings merged),
new content with an AUTO marker skips the incremental advisory, `_catalog`/`_archive` excluded.
"""
import fnmatch
import json
import pathlib
import re

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


def test_broken_link_advisory_fires_and_stays_silent(tmp_path, capsys):
    """Write-time detection of an unresolved wikilink. The probe re-reads from
    disk (an Edit's new_string is only the changed hunk) and is fully guarded —
    on any failure the safe direction is silence, not blocking the edit."""
    vault = tmp_path / "wiki" / "concepts"
    vault.mkdir(parents=True)
    page = vault / "X.md"

    def _post(p):
        dispatch.run_post({"tool_name": "Edit", "tool_input": {"file_path": str(p)}})
        return capsys.readouterr().out

    page.write_text("## Overview\n\nSee [[GhostPage]].\n", encoding="utf-8")
    out = _post(page)
    # tmp_path has no tools/, so the guarded import fails -> silent, never a crash
    assert "Traceback" not in out

    # against the real vault the advisory fires and names the unresolved target
    real = pathlib.Path(__file__).resolve().parent.parent / "wiki" / "concepts" / "_hooktest.md"
    real.write_text("## Overview\n\nSee [[NoSuchPageXYZ]].\n", encoding="utf-8")
    try:
        out = _post(real)
        assert "broken-link-advisory" in out
        assert "NoSuchPageXYZ" in out
    finally:
        real.unlink(missing_ok=True)


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


def test_ponytail_advisory_hook_scripts(capsys):
    # The hook layer itself is in scope — .py and .sh under .claude/hooks/.
    dispatch.run_pre(_input("Edit", "/r/.claude/hooks/dispatch.py", new_string="x"))
    ctx = _payload(capsys)
    assert "[ponytail-advisory]" in ctx and ".claude/hooks/dispatch.py" in ctx
    dispatch.run_pre(_input("Write", "/r/.claude/hooks/new-guard.sh", content="#!/bin/sh"))
    assert "[ponytail-advisory]" in _payload(capsys)


def test_ponytail_advisory_scope(capsys):
    # .py outside tools//hooks and non-script files inside them do not fire.
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


def test_raw_webfetch_fallback_write_passes(tmp_path, capsys):
    # Inbox 2nd-stage fallback: a Write of a NEW raw file whose frontmatter
    # keeps the `source:` URL is the sanctioned fetch path — not blocked.
    p = tmp_path / "raw" / "NewsScrap" / "new-article.md"
    rc = dispatch.run_pre(_input(
        "Write", str(p),
        content="---\nsource: https://example.com/a\n---\nbody"))
    assert rc == 0
    assert capsys.readouterr().err == ""


def test_raw_write_without_source_url_still_blocked(tmp_path, capsys):
    p = tmp_path / "raw" / "NewsScrap" / "no-url.md"
    rc = dispatch.run_pre(_input("Write", str(p), content="---\ntitle: x\n---\nbody"))
    assert rc == 2
    assert "immutable" in capsys.readouterr().err


def test_raw_edit_with_source_url_still_blocked(tmp_path, capsys):
    # Only NEW Writes are excused — an Edit to an existing raw stays blocked.
    p = tmp_path / "raw" / "NewsScrap" / "existing.md"
    p.parent.mkdir(parents=True)
    p.write_text("---\nsource: https://example.com/a\n---\nbody", encoding="utf-8")
    rc = dispatch.run_pre(_input(
        "Edit", str(p), new_string="source: https://example.com/a\nmore"))
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


# ------------------------------------------------- pre-bash phase (commit gate)

def _bash(command):
    return {"tool_name": "Bash", "tool_input": {"command": command}}


def _fake_git(monkeypatch, porcelain):
    """Stand in for `git status --porcelain` so the gate is tested, not the repo."""
    class _R:
        stdout = porcelain
    monkeypatch.setattr(dispatch.subprocess, "run", lambda *a, **k: _R())


def test_guideline_dirty_filter():
    got = dispatch._guideline_dirty(
        " M .claude/layers/hub.md\n"
        "M  CLAUDE.md\n"
        "R  old.md -> .claude/policies/naming.md\n"   # rename → the post-rename name
        "?? tools/x.py\n"                             # not a guideline surface
        " M wiki/index.md\n"
        " M .claude/skills/guideline-writing/SKILL.md\n"   # skills is outside GUIDE_DIRS
        " M .claude/agents/notes.txt\n")                   # not .md
    assert got == [".claude/layers/hub.md", ".claude/policies/naming.md", "CLAUDE.md"]


def test_commit_gate_fires_on_dirty_guideline(monkeypatch, capsys):
    _fake_git(monkeypatch, " M .claude/layers/hub.md\n")
    assert dispatch.run_pre_bash(_bash("git add x && git commit -F -")) == 0
    body = _payload(capsys)
    assert "[commit-gate]" in body
    assert ".claude/layers/hub.md" in body
    assert "Blind review (mandatory)" in body     # the shared rung list is carried


def test_commit_gate_silent_when_not_a_commit(monkeypatch, capsys):
    _fake_git(monkeypatch, " M .claude/layers/hub.md\n")
    assert dispatch.run_pre_bash(_bash("git log --oneline | grep commit")) == 0
    assert _payload(capsys) == ""


def test_commit_gate_silent_when_nothing_guideline_dirty(monkeypatch, capsys):
    _fake_git(monkeypatch, " M tools/lint.py\n M wiki/index.md\n")
    assert dispatch.run_pre_bash(_bash("git commit -m x")) == 0
    assert _payload(capsys) == ""


def test_commit_gate_silent_when_git_unavailable(monkeypatch, capsys):
    def _boom(*a, **k):
        raise OSError("no git")
    monkeypatch.setattr(dispatch.subprocess, "run", _boom)
    assert dispatch.run_pre_bash(_bash("git commit -m x")) == 0
    assert _payload(capsys) == ""


def test_prefilter_never_narrower_than_the_regex():
    """The shell prefilter only decides whether Python runs, so it may over-fire but must
    never reject a command `GIT_COMMIT_RE` would advise on — an under-firing prefilter
    leaves the gate silent on a real commit while this suite stays green, since the other
    tests call `run_pre_bash` directly and never reach the shell layer. The glob is read
    out of `dispatch.sh` so the two cannot drift apart."""
    sh = (pathlib.Path(dispatch.__file__).parent / "dispatch.sh").read_text(encoding="utf-8")
    glob = re.search(r'case "\$payload" in (\S+?)\)', sh).group(1)
    for cmd in ("git commit -m x", "git add a && git commit -F -", "git -C . commit -m x",
                "git -c user.name=x commit", "git --no-pager commit", "git  commit",
                "ls -la", "git log --oneline", "echo hello"):
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}})
        if dispatch.GIT_COMMIT_RE.search(cmd):
            assert fnmatch.fnmatchcase(payload, glob), f"prefilter rejects a real commit: {cmd}"


def test_ladder_rungs_match_the_sot():
    """`LADDER_RUNGS` is a hand-copy of the ladder in `editor-in-chief.md`, and both
    payloads announce that ladder as mandatory — so a rung missing from the copy tells an
    executor there are fewer obligations than there are. That happened: the extraction
    stopped at four of five and no test noticed, because the only rung a test named was
    rung 3. Titles are matched with any parenthetical stripped, so rewording a rung in the
    SoT does not fail this, but dropping one does."""
    sot = (pathlib.Path(dispatch.__file__).parents[2] / ".claude" / "agents"
           / "editor-in-chief.md").read_text(encoding="utf-8")
    section = sot.split("## Guideline Verification Ladder", 1)[1].split("\n## ", 1)[0]
    titles = re.findall(r"^(\d+)\. \*\*(.+?)\*\*", section, re.M)
    assert titles, "ladder section not found — the heading or rung format moved"
    assert re.findall(r"^\s*(\d+)\. ", dispatch.LADDER_RUNGS, re.M) == [n for n, _ in titles]
    for _, title in titles:
        stem = title.split("(")[0].strip()
        assert stem in dispatch.LADDER_RUNGS, f"rung missing from the payload: {stem}"
