"""Regression coverage for the staleness lint hardening — catches recurrence of the
class where a partial edit bumps only the frontmatter last_updated and masks body staleness.

Key point: for derived narrative types (overview / contradiction / synthesis / trail / timeline +
root meta), staleness is judged against the git edit date of the EDITOR body, not the
frontmatter `last_updated`. Since the body date depends on git, it is injected directly into
`_BODY_DATE_CACHE` so the branching logic can be verified without git.
"""
import staleness


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
