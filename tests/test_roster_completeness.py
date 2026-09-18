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


# ── The policies README index vs. each policy file's sections (same family: an index ages silently) ──

def test_policy_index_currently_covers_every_section():
    assert M._check_policy_index_coverage() == []


def test_missing_policy_section_is_reported(tmp_path, monkeypatch):
    pol = tmp_path / ".claude" / "policies"
    pol.mkdir(parents=True)
    (pol / "README.md").write_text(
        "| File | Sections held |\n|---|---|\n| [ghost.md](ghost.md) | Listed Section |\n",
        encoding="utf-8")
    (pol / "ghost.md").write_text("# Ghost\n\n## Listed Section\n\n## Omitted Section\n",
                                  encoding="utf-8")
    monkeypatch.setattr(M, "ROOT", tmp_path)
    issues = M._check_policy_index_coverage()
    assert any("Omitted Section" in i for i in issues), issues
    assert not any("Listed Section" in i for i in issues), issues


def test_fenced_heading_is_not_required(tmp_path, monkeypatch):
    """`index-log-format.md` carries the template headers of the generated index in a
    code block — without the fence skip those become permanent gaps and the whole
    check gets ignored."""
    pol = tmp_path / ".claude" / "policies"
    pol.mkdir(parents=True)
    (pol / "README.md").write_text(
        "| File | Sections held |\n|---|---|\n| [ghost.md](ghost.md) | Real Section |\n",
        encoding="utf-8")
    (pol / "ghost.md").write_text(
        "# Ghost\n\n## Real Section\n\n```\n## Template Header\n```\n", encoding="utf-8")
    monkeypatch.setattr(M, "ROOT", tmp_path)
    assert M._check_policy_index_coverage() == []
