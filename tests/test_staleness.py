"""Regression coverage for the staleness lint hardening — catches recurrence of the
class where a partial edit bumps only the frontmatter last_updated and masks body staleness.

Key point: for derived narrative types (overview / contradiction / synthesis / trail / timeline +
root meta), staleness is judged against the git edit date of the EDITOR body, not the
frontmatter `last_updated`. Since the body date depends on git, it is injected directly into
`_BODY_DATE_CACHE` so the branching logic can be verified without git.
"""
import json

import pytest

import staleness
from _editor_date import editor_hash


@pytest.fixture(autouse=True)
def _isolate_body_date_cache():
    # _BODY_DATE_CACHE is module-level and process-lifetime; restore it so the
    # fake dates seeded for real corpus rels don't leak into later tests.
    saved = dict(staleness._BODY_DATE_CACHE)
    yield
    staleness._BODY_DATE_CACHE.clear()
    staleness._BODY_DATE_CACHE.update(saved)


def _seed_body(rel: str, date: str | None) -> None:
    """Inject the body edit date without calling git (prime the cache)."""
    staleness._BODY_DATE_CACHE[rel] = date


def test_inflated_frontmatter_does_not_mask_stale_body():
    """Regression — even if the overview last_updated is inflated to 06-13, when the body is
    04-30 and upstream is 06-22 it must be flagged STALE (partial-edit masking prevention)."""
    rel = "overviews/llm-foundation.md"
    rec = {"last_updated": "2026-06-13", "upstream_max_date": "2026-06-22"}
    _seed_body(rel, "2026-04-30")
    assert staleness._effective_date(rel, rec) == "2026-04-30"
    assert staleness._is_stale(rec, rel) is True
    assert staleness._is_inflated(rec, "2026-04-30") is True


def test_frontmatter_only_path_would_have_hidden_it():
    """Contrast — looking at frontmatter only (no rel passed), 06-13 >= 06-22 is false, so it is
    misjudged as FRESH. That is, the body-date correction is what actually uncovers the masking."""
    rec = {"last_updated": "2026-06-13", "upstream_max_date": "2026-06-12"}
    # upstream(06-12) < fm(06-13) → FRESH under the frontmatter criterion
    assert staleness._is_stale(rec, rel=None) is False
    # if the body is 04-30, the same upstream is STALE
    rel = "overviews/x.md"
    _seed_body(rel, "2026-04-30")
    assert staleness._is_stale(rec, rel) is True


def test_non_narrative_type_keeps_frontmatter_date():
    """Types where body == edit (entity/concept, etc.) are not subject to git correction and
    use the frontmatter last_updated as-is."""
    rel = "entities/Anthropic.md"
    rec = {"last_updated": "2026-06-13", "upstream_max_date": "2026-06-20"}
    assert staleness._is_body_dated(rel) is False
    assert staleness._effective_date(rel, rec) == "2026-06-13"


def test_root_meta_null_last_updated_is_in_scope_not_inflated():
    """root meta (overview.md) has last_updated=None, so it used to be out of scope.
    It is brought in by its body date, but None is not 'inflation'."""
    rel = "overview.md"
    rec = {"last_updated": None, "upstream_max_date": "2026-06-13"}
    _seed_body(rel, "2026-04-07")
    assert staleness._is_body_dated(rel) is True
    assert staleness._effective_date(rel, rec) == "2026-04-07"
    assert staleness._is_stale(rec, rel) is True
    assert staleness._is_inflated(rec, "2026-04-07") is False  # None is not inflation


def test_body_date_is_truth_even_when_newer_than_frontmatter():
    """Regression — when the body is newer than the frontmatter, as with a re-grounded trail
    (created=04-13 unchanged, body git=06-23), use the body date and treat it as FRESH. Past bug:
    'substitute only when the body is older' returned the trail's old created, causing permanent STALE misjudgment."""
    rel = "trails/x.md"
    rec = {"last_updated": "2026-04-13", "upstream_max_date": "2026-06-20"}
    _seed_body(rel, "2026-06-23")  # body git date after re-grounding
    assert staleness._effective_date(rel, rec) == "2026-06-23"
    assert staleness._is_stale(rec, rel) is False  # 06-20 < 06-23 → FRESH
    assert staleness._is_inflated(rec, "2026-06-23") is False  # body is newer = not inflation


def test_editor_hash_ignores_frontmatter():
    """Regression — `editor_hash` must exclude frontmatter, or it is self-referential:
    a commit that only appends a `sources:` entry and bumps `last_updated` changes the
    hash and re-dates the page as freshly authored, masking a lagging body. Observed on
    `concepts/OpenWashing.md` (2026-07-01 commit, frontmatter-only, body actually 06-26)."""
    body = "\n# Title\n\nNarrative prose that did not change.\n"
    before = "---\nsources: [a]\nlast_updated: 2026-06-26\n---" + body
    after = "---\nsources: [a, b]\nlast_updated: 2026-07-01\n---" + body
    assert editor_hash(before) == editor_hash(after)
    # a real body edit still moves the hash
    assert editor_hash(after) != editor_hash(after.replace("did not change", "changed"))


def _empty_deps(tmp_path, monkeypatch) -> None:
    """Point the lint at a freshly-built EMPTY wiki's `_dependencies.json` — a valid file
    whose `pages` is `{}` (what `build.py dependencies` emits with no pages to index)."""
    deps = tmp_path / "_dependencies.json"
    deps.write_text(json.dumps({"_meta": {"phase": "dependencies", "page_count": 0},
                                "pages": {}}), encoding="utf-8")
    monkeypatch.setattr(staleness, "_DEPS_PATH", deps)


def test_empty_pages_dict_is_exit_0_not_build_error(tmp_path, monkeypatch, capsys):
    """Regression — `build.py dependencies` on an empty (or source-only) wiki legitimately
    emits `{"pages": {}}`. `_load()` used to collapse that into the same `{}` as a missing
    file, so `lint staleness` exited 2 with "run build.py first" on a freshly-built empty
    wiki — a valid state must not read as a build-step failure."""
    _empty_deps(tmp_path, monkeypatch)
    assert staleness.run() == 0
    out = capsys.readouterr().out
    assert "0 dated pages, 0 STALE" in out
    assert "build.py" not in out


def test_empty_wiki_still_errors_on_an_unknown_target(tmp_path, monkeypatch, capsys):
    """The empty-wiki exit 0 must not swallow the target branch — a targeted query for a page
    with no dependency record stays exit 2 whether or not the corpus is empty. Pins the
    ordering: an empty-pages guard placed before `if target:` returns 0 here (false clean)."""
    _empty_deps(tmp_path, monkeypatch)
    assert staleness.run(target="anything") == 2
    assert "no dependency record" in capsys.readouterr().err


def test_missing_deps_file_still_exits_2(tmp_path, monkeypatch, capsys):
    """Contrast — a genuinely missing/unreadable _dependencies.json is a real error:
    exit 2 with the actionable message (behavior unchanged by the empty-wiki fix)."""
    monkeypatch.setattr(staleness, "_DEPS_PATH", tmp_path / "nope.json")
    assert staleness.run() == 2
    err = capsys.readouterr().err
    assert "build.py dependencies" in err
