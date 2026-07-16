"""Unit tests for the agent tool-permission parity check (meta_schema).

Guards the X-list ↔ frontmatter `disallowedTools` bidirectional contract:
a governed tool named in a role SoT's X-list must be disallowed in that
file's frontmatter, and every disallowed tool must be justified by an
X-list mention. FP-averse: only exact tool tokens with word boundaries
count — restriction prose like "editing"/"external search" never matches.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "_lint"))

from meta_schema import (  # noqa: E402
    _check_agent_tool_permissions,
    check_agent_tool_permissions,
)


# --- pure function: parity holds ---

def test_parity_both_named_and_disallowed():
    xlist = "- External lookup (WebSearch·WebFetch) — Reporter's area\n"
    assert check_agent_tool_permissions(
        "columnist", ["WebSearch", "WebFetch"], xlist) == []


def test_no_tools_named_no_disallowed():
    xlist = "- Authoring L2-3 content (Columnist territory)\n"
    assert check_agent_tool_permissions("reporter", [], xlist) == []


# --- pure function: missing direction ---

def test_named_but_not_disallowed_flags_missing():
    xlist = "- External lookup (WebSearch·WebFetch)\n"
    out = check_agent_tool_permissions("columnist", ["WebSearch"], xlist)
    assert len(out) == 1 and "WebFetch" in out[0] and "omits" in out[0]


def test_write_edit_named_but_not_disallowed():
    xlist = "- Direct output edits (Write·Edit) — Columnist territory\n"
    out = check_agent_tool_permissions("desk", [], xlist)
    assert len(out) == 2
    assert any("Write" in v for v in out) and any("Edit" in v for v in out)


# --- pure function: unjustified direction ---

def test_disallowed_but_not_named_flags_unjustified():
    xlist = "- Qualitative review (Desk's area)\n"
    out = check_agent_tool_permissions("copyeditor", ["WebSearch"], xlist)
    assert len(out) == 1 and "no X-list entry names it" in out[0]


def test_unknown_frontmatter_tool_still_checked():
    out = check_agent_tool_permissions("desk", ["NotebookEdit"], "- nothing\n")
    assert len(out) == 1 and "NotebookEdit" in out[0]


# --- pure function: FP-aversion ---

def test_prose_words_do_not_match_tool_tokens():
    xlist = ("- Editing AUTO blocks directly (deterministic-tools area)\n"
             "- External search·verifying new facts\n"
             "- Writing timeline narrative\n")
    assert check_agent_tool_permissions("columnist", [], xlist) == []


def test_own_artifacts_exception_excuses_copyeditor():
    # The Copy Editor writes lint-report.md via the lint CLI, so an X-list
    # bullet naming Write/Edit does not force disallowing them.
    xlist = "- No hand Write·Edit of wiki content — --fix only\n"
    assert check_agent_tool_permissions("copyeditor", [], xlist) == []


def test_own_artifacts_exception_is_per_role():
    xlist = "- No hand Write·Edit of wiki content\n"
    out = check_agent_tool_permissions("desk", [], xlist)
    assert len(out) == 2  # desk gets no excuse


# --- disk wrapper: the real role SoTs must hold parity ---

def test_repo_role_sots_pass():
    assert _check_agent_tool_permissions() == []
