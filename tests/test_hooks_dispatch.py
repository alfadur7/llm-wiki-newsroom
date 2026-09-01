"""`.claude/hooks/dispatch.py` unit tests — the behavioral contract of the F3 unified dispatcher.

Contract inherited from the 6 legacy hooks: guard (lint-report asymmetry) is exit 2 + stderr,
advisory is exit 0 + a single stdout JSON additionalContext (simultaneous firings merged),
new content with an AUTO marker skips the incremental advisory, `_catalog`/`_archive` excluded.
"""
import fnmatch
import json
import pathlib
import re
import pytest
import shutil
import subprocess

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


# Command position, not the string `commit`, is what the gate anchors on — matching
# the word anywhere fired the payload on a grep, an echo and a documentation body
# eight times across two review rotations.
FIRES = [
    "git commit -m 'x'",
    "git -C . commit -m 'x'",
    "git  commit",                                   # two spaces
    "git add CLAUDE.md && git commit -F /tmp/m.txt",
    "python tools/lint.py meta; git commit -m 'x'",
    # Shell metacharacters inside the message — how often, and why splitting on a
    # regex before the quotes silenced the gate on every one, is in `_lex`'s docstring.
    "git commit -am 'refactor(hooks): tidy the Write|Edit hook'",
    "git commit -m 'fix: a; b'",
    "git commit -m 'feat: a && b'",
    "git add X; git commit -m 'x'",                  # PS 5.1 chain — `;` with no space
    "python tools/lint.py meta\ngit add CLAUDE.md\ngit commit -m fix",  # newline chain
]
SILENT = [
    "git log --oneline -5",
    "git log --grep=commit",                         # `commit` is not its own token
    "grep -rn 'git commit' log.md",                  # the first token is not git
    "echo 'run git commit next'",
    "git commit -m 'docs: how to git commit'",       # the message folds into one token
]


def _segs(command):
    return dispatch._git_segments(command, "commit")


def test_commit_segments_anchor_on_command_position():
    for c in FIRES:
        assert _segs(c), c
    for c in SILENT[:4]:
        assert not _segs(c), c


def test_commit_message_body_is_not_a_second_match():
    """A `git commit` inside an `-m` value must not make its own match — the root of
    the over-fire class."""
    segs = _segs(SILENT[4])
    assert len(segs) == 1, segs


def test_heredoc_body_is_not_scanned():
    """A command writing documentation must not fire on that document's own text."""
    assert not _segs("cat > d.md <<'EOF'\ngit commit -m x\nEOF")


def test_guideline_path_filter():
    got = dispatch._guideline_paths(dispatch._porcelain_paths(
        " M .claude/layers/hub.md\n"
        "M  CLAUDE.md\n"
        "R  old.md -> .claude/policies/naming.md\n"   # rename → the post-rename name
        "?? tools/x.py\n"                             # not a guideline surface
        " M wiki/index.md\n"
        " M .claude/skills/guideline-writing/SKILL.md\n"   # skills is outside GUIDE_DIRS
        " M .claude/agents/notes.txt\n"))                  # not .md
    assert got == [".claude/layers/hub.md", ".claude/policies/naming.md", "CLAUDE.md"]


def test_prefilter_never_narrower_than_the_python_judge():
    """The shell prefilter only decides whether Python runs, so it may over-fire but must
    never reject a command the gate would advise on — an under-firing prefilter leaves the
    gate silent on a real commit while this suite stays green, since the other tests call
    `run_pre_bash` directly and never reach the shell layer. The glob is read out of
    `dispatch.sh` so the two cannot drift apart. This is a sample check: the pattern is
    evaluated with fnmatch rather than bash `case`, so it holds for plain wildcards only."""
    sh = (pathlib.Path(dispatch.__file__).parent / "dispatch.sh").read_text(encoding="utf-8")
    glob = re.search(r'case "\$payload" in (\S+?)\)', sh).group(1)
    for cmd in FIRES:
        payload = json.dumps(_bash(cmd))
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


def test_pre_bash_ignores_a_malformed_payload(capsys):
    assert dispatch.run_pre_bash({"tool_input": []}) == 0
    assert dispatch.run_pre_bash({"tool_input": {"command": None}}) == 0
    assert _payload(capsys) == ""


def test_commit_gate_silent_when_git_is_unavailable(monkeypatch, capsys):
    def _boom(*a, **k):
        raise OSError("no git")
    monkeypatch.setattr(dispatch.subprocess, "run", _boom)
    assert dispatch.run_pre_bash(_bash("git commit -m x")) == 0
    assert _payload(capsys) == ""


def _repo(tmp_path):
    """A throwaway repo — the gate reads the index and the worktree, so a fake
    subprocess would test the stub rather than the branch that picks between them."""
    r = tmp_path / "repo"
    (r / ".claude" / "policies").mkdir(parents=True)
    for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(r), *a], check=True, capture_output=True)
    (r / "CLAUDE.md").write_text("x", encoding="utf-8")
    (r / ".claude" / "policies" / "naming.md").write_text("x", encoding="utf-8")
    (r / "README.md").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(r), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(r), "commit", "-qm", "base"], check=True, capture_output=True)
    return r


def test_pre_bash_names_the_staged_guideline_file(tmp_path, capsys, monkeypatch):
    r = _repo(tmp_path)
    (r / ".claude" / "policies" / "naming.md").write_text("edited", encoding="utf-8")
    subprocess.run(["git", "-C", str(r), "add", ".claude/policies/naming.md"],
                   check=True, capture_output=True)
    monkeypatch.setattr(dispatch, "ROOT", r)
    assert dispatch.run_pre_bash(_bash("git commit -m 'x'")) == 0
    out = _payload(capsys)
    assert "[commit-gate]" in out and ".claude/policies/naming.md" in out
    assert "Blind review (mandatory)" in out          # the shared rung list is carried


def test_pre_bash_silent_when_the_commit_carries_no_guideline(tmp_path, capsys, monkeypatch):
    """Naming a dirty CLAUDE.md while an unrelated file is being committed re-fires on
    every commit until that file is itself committed — the real price of a repo-wide read."""
    r = _repo(tmp_path)
    (r / "CLAUDE.md").write_text("dirty but not in this commit", encoding="utf-8")
    (r / "README.md").write_text("edited", encoding="utf-8")
    subprocess.run(["git", "-C", str(r), "add", "README.md"], check=True, capture_output=True)
    monkeypatch.setattr(dispatch, "ROOT", r)
    dispatch.run_pre_bash(_bash("git commit -m 'x'"))
    assert _payload(capsys) == ""


def test_pre_bash_reads_the_worktree_when_the_command_stages(tmp_path, capsys, monkeypatch):
    """`git add X && git commit` in one call has an empty index at hook time."""
    r = _repo(tmp_path)
    (r / "CLAUDE.md").write_text("edited", encoding="utf-8")
    monkeypatch.setattr(dispatch, "ROOT", r)
    dispatch.run_pre_bash(_bash("git add CLAUDE.md && git commit -m 'x'"))
    assert "CLAUDE.md" in _payload(capsys)


def test_pre_bash_silent_for_another_repository(tmp_path, capsys, monkeypatch):
    """`git -C <other repo> commit` must not be answered with this repo's staged files."""
    r, other = _repo(tmp_path), _repo(tmp_path / "b")
    (r / "CLAUDE.md").write_text("edited", encoding="utf-8")
    subprocess.run(["git", "-C", str(r), "add", "CLAUDE.md"], check=True, capture_output=True)
    monkeypatch.setattr(dispatch, "ROOT", r)
    dispatch.run_pre_bash(_bash(f"git -C {other.as_posix()} commit -m 'x'"))
    assert _payload(capsys) == ""


def test_pre_bash_commit_all_reads_the_whole_repo(tmp_path, capsys, monkeypatch):
    """`git commit -am` names no path — with nothing to narrow by, the whole repo is right."""
    r = _repo(tmp_path)
    (r / "CLAUDE.md").write_text("edited", encoding="utf-8")
    monkeypatch.setattr(dispatch, "ROOT", r)
    dispatch.run_pre_bash(_bash("git commit -am 'x'"))
    assert "CLAUDE.md" in _payload(capsys)


def test_metachar_in_the_message_fires_end_to_end(tmp_path, capsys, monkeypatch):
    """A real guideline commit whose message carries `|` — the gate went silent on these."""
    r = _repo(tmp_path)
    (r / "CLAUDE.md").write_text("edited", encoding="utf-8")
    monkeypatch.setattr(dispatch, "ROOT", r)
    dispatch.run_pre_bash(_bash("git commit -am 'refactor(hooks): tidy the Write|Edit hook'"))
    assert "CLAUDE.md" in _payload(capsys)


def test_quoted_metachar_does_not_forge_a_commit_segment():
    """A command whose quotes span an operator must not forge a commit segment — without
    quote handling first, a read-only loop calls the gate down on itself."""
    c = ("""for x in "git commit -m 'a'" "git add CLAUDE.md && git commit"; """
         """do echo "$x"; done""")
    assert _segs(c) == []


def test_powershell_semicolon_and_windows_path_are_named(tmp_path, capsys, monkeypatch):
    """PS 5.1 chaining (`;` with no space) and a backslash path — neither loses the path."""
    r = _repo(tmp_path)
    (r / ".claude" / "policies" / "naming.md").write_text("edited", encoding="utf-8")
    monkeypatch.setattr(dispatch, "ROOT", r)
    for cmd in (r"git add .claude/policies/naming.md; git commit -m 'x'",
                r"git add .claude\policies\naming.md && git commit -m 'x'"):
        dispatch.run_pre_bash(_bash(cmd))
        assert "naming.md" in _payload(capsys), cmd


def test_add_all_reads_the_whole_guideline_scope(tmp_path, capsys, monkeypatch):
    """`-A` and `.` stage everything — there is nothing to narrow by, so the whole
    guideline scope is right."""
    r = _repo(tmp_path)
    (r / "CLAUDE.md").write_text("edited", encoding="utf-8")
    monkeypatch.setattr(dispatch, "ROOT", r)
    for cmd in ("git add -A && git commit -m 'x'", "git add . && git commit -m 'x'"):
        dispatch.run_pre_bash(_bash(cmd))
        assert "CLAUDE.md" in _payload(capsys), cmd


def test_a_staged_directory_scopes_to_that_directory(tmp_path, capsys, monkeypatch):
    """A directory argument is broad only *inside* that directory. Reading it as
    whole-repo names every dirty guideline file on a commit that carries none of them —
    the re-fire this gate exists to prevent, and it was pinned as intended behaviour."""
    r = _repo(tmp_path)
    (r / "tools").mkdir()
    (r / "tools" / "x.py").write_text("x", encoding="utf-8")
    (r / "CLAUDE.md").write_text("dirty but not in this commit", encoding="utf-8")
    (r / ".claude" / "policies" / "naming.md").write_text("edited", encoding="utf-8")
    monkeypatch.setattr(dispatch, "ROOT", r)

    dispatch.run_pre_bash(_bash("git add .claude && git commit -m 'x'"))
    out = _payload(capsys)
    assert "naming.md" in out and "CLAUDE.md" not in out   # CLAUDE.md is not under .claude

    dispatch.run_pre_bash(_bash("git add tools/ && git commit -m 'x'"))
    assert _payload(capsys) == ""


def test_commit_all_does_not_name_an_untracked_file(tmp_path, capsys, monkeypatch):
    """`git commit -a` stages tracked modifications and nothing else, so an untracked
    guideline file is one this commit cannot carry."""
    r = _repo(tmp_path)
    (r / ".claude" / "policies" / "_untracked.md").write_text("new", encoding="utf-8")
    (r / "CLAUDE.md").write_text("edited", encoding="utf-8")
    monkeypatch.setattr(dispatch, "ROOT", r)
    dispatch.run_pre_bash(_bash("git commit -am 'x'"))
    out = _payload(capsys)
    assert "CLAUDE.md" in out and "_untracked.md" not in out


def test_broad_add_does_not_fire_on_an_unrelated_narrow_commit(tmp_path, capsys, monkeypatch):
    """The widening must not bring back "names CLAUDE.md on every unrelated commit"."""
    r = _repo(tmp_path)
    (r / "CLAUDE.md").write_text("dirty but not in this commit", encoding="utf-8")
    (r / "README.md").write_text("edited", encoding="utf-8")
    monkeypatch.setattr(dispatch, "ROOT", r)
    dispatch.run_pre_bash(_bash("git add README.md && git commit -m 'x'"))
    assert _payload(capsys) == ""


def test_newline_separates_commands(tmp_path, capsys, monkeypatch):
    """`run lint → commit` on two lines is the very flow this gate is for — without the
    newline as a separator it goes silent the moment the first token is not git."""
    r = _repo(tmp_path)
    (r / "CLAUDE.md").write_text("edited", encoding="utf-8")
    monkeypatch.setattr(dispatch, "ROOT", r)
    dispatch.run_pre_bash(_bash("python tools/lint.py meta\ngit add CLAUDE.md\ngit commit -m fix"))
    assert "CLAUDE.md" in _payload(capsys)


def test_unbalanced_quote_keeps_the_prefix(tmp_path, capsys, monkeypatch):
    """Dropping every token on an unbalanced quote makes the gate vanish for PowerShell
    here-strings and heredoc-substituted messages — the `git commit` was already read."""
    r = _repo(tmp_path)
    (r / "CLAUDE.md").write_text("edited", encoding="utf-8")
    monkeypatch.setattr(dispatch, "ROOT", r)
    for cmd in ("git add CLAUDE.md && git commit -m @'\nfix: don't break\n'@",
                "git add CLAUDE.md && git commit -m \"$(cat <<'EOF'\nfix: x\nEOF\n)\""):
        dispatch.run_pre_bash(_bash(cmd))
        assert "CLAUDE.md" in _payload(capsys), cmd


def test_a_message_mentioning_a_path_does_not_name_it(tmp_path, capsys, monkeypatch):
    """A commit *message* that mentions a path must not name an unrelated file — only
    `git add` arguments and the pathspec are read, never the raw command."""
    r = _repo(tmp_path)
    (r / ".claude" / "policies" / "naming.md").write_text("dirty", encoding="utf-8")
    (r / "README.md").write_text("edited", encoding="utf-8")
    monkeypatch.setattr(dispatch, "ROOT", r)
    dispatch.run_pre_bash(_bash(
        "git add README.md && git commit -m 'docs: mirror .claude/policies/naming.md wording'"))
    assert _payload(capsys) == ""


def test_commit_dash_C_is_not_a_repo_path(tmp_path, capsys, monkeypatch):
    """`git commit -C HEAD` reuses a message; reading it as a repo path empties the
    toplevel lookup and silences the gate."""
    r = _repo(tmp_path)
    (r / "CLAUDE.md").write_text("edited", encoding="utf-8")
    monkeypatch.setattr(dispatch, "ROOT", r)
    dispatch.run_pre_bash(_bash("git add -A && git commit -C HEAD"))
    assert "CLAUDE.md" in _payload(capsys)


def test_backslash_directory_is_still_a_directory(tmp_path, capsys, monkeypatch):
    """PowerShell directory staging — a posix lexer that eats the backslash breaks the
    directory test."""
    r = _repo(tmp_path)
    (r / ".claude" / "policies" / "naming.md").write_text("edited", encoding="utf-8")
    monkeypatch.setattr(dispatch, "ROOT", r)
    dispatch.run_pre_bash(_bash(r"git add .claude\policies && git commit -m 'x'"))
    assert "naming.md" in _payload(capsys)


def test_update_flag_stages_tracked_only(tmp_path, capsys, monkeypatch):
    """`git add -u`/`--update` restage tracked modifications and nothing else, so an
    untracked guideline file under them is one the commit cannot carry — and the long
    form must reach the gate at all, or a real guideline commit gets no ladder."""
    r = _repo(tmp_path)
    (r / ".claude" / "policies" / "_untracked.md").write_text("new", encoding="utf-8")
    (r / "CLAUDE.md").write_text("edited", encoding="utf-8")
    monkeypatch.setattr(dispatch, "ROOT", r)
    for cmd in ("git add -u && git commit -m 'x'", "git add --update && git commit -m 'x'"):
        dispatch.run_pre_bash(_bash(cmd))
        out = _payload(capsys)
        assert "CLAUDE.md" in out, cmd
        assert "_untracked.md" not in out, cmd


def test_broad_flag_is_broad_only_inside_its_own_pathspec(tmp_path, capsys, monkeypatch):
    """`git add -A tools/` stages nothing outside `tools/`."""
    r = _repo(tmp_path)
    (r / "tools").mkdir()
    (r / "tools" / "x.py").write_text("x", encoding="utf-8")
    (r / "CLAUDE.md").write_text("dirty but not in this commit", encoding="utf-8")
    monkeypatch.setattr(dispatch, "ROOT", r)
    dispatch.run_pre_bash(_bash("git add -A tools/ && git commit -m 'x'"))
    assert _payload(capsys) == ""


def test_commit_pathspec_narrows_what_the_add_staged(tmp_path, capsys, monkeypatch):
    """`git commit -- <paths>` commits those paths and nothing else, whatever is staged."""
    r = _repo(tmp_path)
    (r / "tools").mkdir()
    (r / "tools" / "x.py").write_text("x", encoding="utf-8")
    (r / ".claude" / "policies" / "naming.md").write_text("edited", encoding="utf-8")
    monkeypatch.setattr(dispatch, "ROOT", r)
    dispatch.run_pre_bash(_bash("git add .claude && git commit -m 'x' -- tools/x.py"))
    assert _payload(capsys) == ""


# --- the oracle: the named list must equal what the commit actually carries ----------
# Predicting what `git add`/`git commit` will stage from the command string was got wrong
# four times running, twice in the direction where the gate goes silent, each repair
# closing one flag combination and opening the next. So the scope logic is checked
# against git itself: every shape below is executed for real in a throwaway repo and the
# gate's list is compared with the guideline files the resulting commit contains.
#
# What it does NOT cover — the asserted cases above are not redundant, and removing one
# removes the only coverage of what it names:
#   · the classifier. Both sides run `_guideline_paths`, so a wrong classifier agrees
#     with itself here; `test_guideline_path_filter` is what pins it.
#   · branches no shape reaches: the index-first read (a shape cannot pre-stage), the
#     other-repository guard, and rename handling in `_porcelain_paths`.
#   · under-fire on a shape whose command makes no commit — `carried` is empty then, so
#     only an over-fire can disagree.
#   · PowerShell forms. Shapes run through `bash`, which eats a backslash path, so such
#     a shape would fail a correct implementation.

SHAPES = [
    "git commit -am m",
    "git add -A && git commit -m m",
    "git add . && git commit -m m",
    "git add -u && git commit -m m",
    "git add --update && git commit -m m",
    "git add .claude && git commit -m m",
    "git add tools && git commit -m m",
    "git add -A tools && git commit -m m",
    "git add CLAUDE.md && git commit -m m",
    "git add .claude && git commit -m m -- tools/x.py",
    "git commit -m m -- .claude/agents",
    "git commit -m m -- .claude",                        # pathspec spanning an untracked file
    "git add -A && git add tools/x.py && git commit -m m",
    "git add README.md && git commit -m m",
    "git commit -m m",                                   # nothing staged — no commit
    "git commit -m '-a quick fix'",                      # a message must not read as a flag
    "git commit --amend -m m",                           # rewrites the commit it replaces
    "git add CLAUDE.md && git commit --amend -m m",
    "git add .claude/policies/naming.md && git commit -m m",
]


def _oracle_repo(tmp_path):
    """A repo with tracked-modified and untracked files on both sides of the guideline
    line, so every shape below has something it should and should not name."""
    r = tmp_path / "o"
    for d in (".claude/policies", ".claude/agents", ".claude/layers", "tools"):
        (r / d).mkdir(parents=True)
    for f in ("CLAUDE.md", ".claude/policies/naming.md", ".claude/agents/reporter.md",
              "README.md", "tools/x.py"):
        (r / f).write_text("base\n", encoding="utf-8")
    for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"],
              ["add", "-A"], ["commit", "-qm", "base"]):
        subprocess.run(["git", "-C", str(r), *a], check=True, capture_output=True)
    for f in ("CLAUDE.md", ".claude/policies/naming.md", ".claude/agents/reporter.md",
              "README.md", "tools/x.py"):
        (r / f).write_text("edited\n", encoding="utf-8")          # tracked, modified
    (r / ".claude/layers/new.md").write_text("new\n", encoding="utf-8")   # untracked
    (r / "tools/y.py").write_text("new\n", encoding="utf-8")              # untracked
    return r


def _named(capsys):
    """The paths the gate printed, or [] when it stayed silent."""
    body = _payload(capsys)
    if not body:
        return []
    mid = body.split(dispatch.COMMIT_GATE_HEAD, 1)[1].split(dispatch.COMMIT_GATE_TAIL, 1)[0]
    return sorted(line.strip() for line in mid.splitlines() if line.strip())


def _carried(repo, command):
    """Guideline files the command's commit actually contains — [] if it made none."""
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    subprocess.run(["bash", "-c", command], cwd=str(repo), capture_output=True, text=True)
    new = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                         capture_output=True, text=True).stdout.strip()
    if new == head:
        return []
    out = subprocess.run(["git", "-C", str(repo), "show", "--name-only", "--format=", "HEAD"],
                         capture_output=True, text=True).stdout
    return dispatch._guideline_paths(out.split())


@pytest.mark.skipif(shutil.which("bash") is None, reason="the oracle runs the shape in a shell")
@pytest.mark.parametrize("shape", SHAPES)
def test_the_gate_names_what_the_commit_carries(shape, tmp_path, capsys, monkeypatch):
    repo = _oracle_repo(tmp_path)
    monkeypatch.setattr(dispatch, "ROOT", repo)
    dispatch.run_pre_bash(_bash(shape))
    predicted = _named(capsys)
    assert predicted == _carried(repo, shape), shape
