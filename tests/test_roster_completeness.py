"""Regression: every .claude/ file in a rostered folder stays enumerated.

`layers/` joined `operations/` and `policies/` in the check's scope. The gap it
closes is silent — an unlisted layer file works fine, it is simply invisible to
the CLAUDE.md index an agent reads to decide where a rule belongs.
"""
import meta_schema as M


def test_rostered_folders_are_currently_complete():
    assert M._check_roster_completeness((M.ROOT / "CLAUDE.md").read_text(encoding="utf-8")) == []


def test_layers_is_rostered():
    assert "layers" in dict(M.ROSTER_FOLDERS), "layers dropped from ROSTER_FOLDERS"


def test_skills_is_rostered():
    """skills/ is the folder whose roster unit is a directory name, not an .md
    basename — the reason it sat outside the check until the unit was made
    folder-aware. A regression that reverts either half re-opens a silent gap."""
    assert "skills" in dict(M.ROSTER_FOLDERS), "skills dropped from ROSTER_FOLDERS"
    assert M._disk_roster("skills"), "skills roster is empty — the unit is folder names"


def test_unlisted_skill_is_reported(monkeypatch):
    real = M._disk_roster
    monkeypatch.setattr(
        M, "_disk_roster",
        lambda folder: (real(folder) | {"ghost-skill"}) if folder == "skills" else real(folder),
    )
    issues = M._check_roster_completeness((M.ROOT / "CLAUDE.md").read_text(encoding="utf-8"))
    assert any("ghost-skill" in i for i in issues), issues


def test_unlisted_file_is_reported(monkeypatch):
    monkeypatch.setattr(M, "_disk_roster", lambda folder: {"ghost-runbook.md"})
    issues = M._check_roster_completeness((M.ROOT / "CLAUDE.md").read_text(encoding="utf-8"))
    assert any("ghost-runbook.md" in i for i in issues), issues
