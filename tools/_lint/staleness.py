"""Uniform layer-cascade staleness lint — one rule for every content type.

The wiki is a dependency DAG (L1 raw → L2-1 source → L2-2 hub → L2-3 → L2-4).
A page is **stale** when anything it derives from changed after it was last
authored. This rule adds a *uniform upstream-content freshness* signal across
all derived content types (previously only overview/contradiction had partial,
per-type freshness). It is **orthogonal to**, not a replacement for, the
existing checks: set-change (overview AUTO-drift·contradiction claims-drift —
member/claim set added/removed), within-page metadata hygiene (overview/
contradiction freshness), and semantic (anchor invasion) measure different
things a date cascade cannot capture. Those checks stay.

Rule (consumes `graph/_dependencies.json`, built by `tools/_build/dependencies.py`):

    page is STALE  ⇔  upstream_max_date > page.effective_date

`upstream_max_date` is the newest `last_updated` among the page's upstream
(the layer it derives from). A stale page may be referencing superseded
members/sources and should be re-checked by its author.

`effective_date` is the page's authored freshness. For most pages this is the
frontmatter `last_updated` stored in `_dependencies.json`. **For derived
narrative types** (overview·contradiction·synthesis·trail·timeline + the L2-4
root meta files) it is instead the EDITOR-body last-commit date
(`_editor_date.editor_last_commit_date`, git-derived, AUTO-block churn excluded)
whenever that is OLDER than the frontmatter date. Rationale: a partial edit that
touches only AUTO blocks or a non-narrative section (e.g. the 2026-06-13 recency
batch that added a `## Recent Changes` section to every overview) bumps frontmatter
`last_updated` WITHOUT re-grounding the narrative. Keying staleness on that
inflated date masks a body that is months behind its sources — the very gap this
lint exists to catch. Using the EDITOR-body date as the baseline closes it; when
the two diverge the report names both (`body=<git date>` vs `last_updated=<fm>`).

Rollout: **advisory mode** — reports but does not gate the exit code (the
138-stale backlog precludes gating until triaged). Coverage limits: L2-4 root
meta files (overview.md/contradiction.md) and upstream-less pages have no
frontmatter `last_updated` and are out of scope here — a git/log-based root
timestamp is a future addition, not yet implemented.
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import GRAPH, WIKI  # noqa: E402
sys.path.insert(0, str(Path(__file__).parent))
from _editor_date import editor_last_commit_date  # noqa: E402

ADVISORY_MODE = True
_DEPS_PATH = GRAPH / "_dependencies.json"

# Derived narrative types whose frontmatter `last_updated` can be inflated by
# non-narrative edits (AUTO rebuilds, recency-section batches, roster syncs).
# For these the EDITOR-body git date is the authored-freshness baseline. Other
# types (source = content date; entity/concept hub = edit IS body) keep their
# stored date. Keyed by `_dependencies.json` rel prefix; root meta files added.
_BODY_DATED_PREFIXES = ("overviews/", "contradictions/", "syntheses/", "trails/", "timelines/")
_BODY_DATED_ROOTS = ("overview.md", "contradiction.md")

_BODY_DATE_CACHE: dict[str, str | None] = {}


def _load() -> dict:
    try:
        return json.loads(_DEPS_PATH.read_text(encoding="utf-8")).get("pages", {})
    except (OSError, json.JSONDecodeError):
        return {}


def _is_body_dated(rel: str) -> bool:
    return rel.startswith(_BODY_DATED_PREFIXES) or rel in _BODY_DATED_ROOTS


def _body_date(rel: str) -> str | None:
    """EDITOR-body last-commit date for a derived narrative page (cached).
    None when git is unavailable or the file is missing."""
    if rel not in _BODY_DATE_CACHE:
        fp = WIKI / rel
        _BODY_DATE_CACHE[rel] = editor_last_commit_date(fp) if fp.is_file() else None
    return _BODY_DATE_CACHE[rel]


def _effective_date(rel: str, rec: dict) -> str | None:
    """Authored-freshness baseline for staleness. For derived narrative types
    the EDITOR-body git date IS the truth of when the narrative was last
    authored — use it directly (frontmatter only as fallback when git is
    unavailable). This handles BOTH failure modes a frontmatter date has:
    inflation (a non-narrative edit bumped `last_updated` PAST the body — body
    is older, must not be hidden) AND staleness of an immutable field (trails
    carry `created`, never bumped — the body can be far NEWER after a
    re-ground; trusting `created` would mark a fresh page stale forever)."""
    lu = rec.get("last_updated")
    if not _is_body_dated(rel):
        return lu
    return _body_date(rel) or lu


def _is_inflated(rec: dict, eff: str | None) -> bool:
    """Frontmatter last_updated is a real date NEWER than the effective body
    date — a partial edit bumped it past the narrative. (A null last_updated is
    not inflation; the body date merely brought the page into scope.)"""
    lu = rec.get("last_updated")
    return bool(lu and eff and eff < lu)


def _is_stale(rec: dict, rel: str | None = None) -> bool:
    eff = _effective_date(rel, rec) if rel is not None else rec.get("last_updated")
    um = rec.get("upstream_max_date")
    return bool(eff and um and um > eff)


def _newest_upstream(rec: dict, pages: dict) -> list[str]:
    """Upstream rels whose last_updated == upstream_max_date (what went newer)."""
    um = rec.get("upstream_max_date")
    return [u for u in rec.get("upstream", []) if pages.get(u, {}).get("last_updated") == um]


def run(target: str | None = None, fix: bool = False, **_kwargs) -> int:
    pages = _load()
    if not pages:
        print(f"ERROR: {_DEPS_PATH} not found or empty — run `python tools/build.py dependencies` first.",
              file=sys.stderr)
        return 2

    if target:
        # Resolve a slug/path to dependency key(s) (accept stem, rel, or rel.md).
        # A bare stem can match multiple subdirs (e.g. entities/X.md AND
        # timelines/X.md) — show ALL matches so a STALE layer is never hidden
        # behind a FRESH same-named page.
        cand = sorted(k for k in pages if k == target or k.endswith(f"/{target}.md") or k == f"{target}.md")
        if not cand:
            print(f"ERROR: no dependency record for target '{target}'.", file=sys.stderr)
            return 2
        if len(cand) > 1:
            print(f"[{len(cand)} pages match '{target}' — showing all]")
        for rel in cand:
            rec = pages[rel]
            eff = _effective_date(rel, rec)
            stale = _is_stale(rec, rel)
            mark = "🔴 STALE" if stale else ("— (root/no date)" if not eff else "✅ FRESH")
            print(f"{rel}: {mark}")
            line = (f"  last_updated={rec.get('last_updated')}  upstream_max_date={rec.get('upstream_max_date')}  "
                    f"upstream={len(rec.get('upstream', []))}")
            if _is_inflated(rec, eff):
                line += f"  body={eff} (frontmatter last_updated inflated)"
            elif eff and eff != rec.get("last_updated"):
                line += f"  body={eff}"
            print(line)
            if stale:
                newest = _newest_upstream(rec, pages)
                print(f"  [Staleness] upstream newer than this page — re-check against: {newest[:8]}")
        return 0

    # Corpus summary. `effective_date` (body date for derived narrative types,
    # else frontmatter last_updated) is the staleness baseline — a page with no
    # effective date (upstream-less, undated) is out of scope.
    rated = [(rel, rec, _effective_date(rel, rec)) for rel, rec in pages.items()]
    rated = [(rel, rec, eff) for rel, rec, eff in rated if eff]
    stale = [(rel, rec, eff) for rel, rec, eff in rated if _is_stale(rec, rel)]
    by_type: dict[str, int] = {}
    inflated = 0
    for rel, rec, eff in stale:
        seg = rel.split("/")[0] if "/" in rel else "root"
        by_type[seg] = by_type.get(seg, 0) + 1
        if _is_inflated(rec, eff):
            inflated += 1

    print(f"Layer-cascade staleness — {len(rated)} dated pages, {len(stale)} STALE "
          f"(upstream changed after authored date)")
    if by_type:
        print("  by layer: " + " · ".join(f"{k}={v}" for k, v in sorted(by_type.items())))
    if inflated:
        print(f"  ⚠️ {inflated} of these have an inflated frontmatter last_updated "
              f"(partial edit bumped the date past the EDITOR body — staleness keyed on body date)")
    if stale:
        # Surface the largest actual gap (upstream_max_date − effective_date) first.
        def _gap_days(item: tuple[str, dict, str]) -> int:
            _rel, rec, eff = item
            try:
                return (date.fromisoformat(rec["upstream_max_date"]) - date.fromisoformat(eff)).days
            except Exception:
                return 0
        for rel, rec, eff in sorted(stale, key=_gap_days, reverse=True)[:20]:
            tag = f" (fm last_updated={rec['last_updated']} inflated)" if _is_inflated(rec, eff) else ""
            print(f"    🔴 {rel} — authored {eff} < upstream {rec['upstream_max_date']}{tag}")
        if len(stale) > 20:
            print(f"    ... and {len(stale) - 20} more")
    if ADVISORY_MODE:
        print("\n  [Advisory mode] orthogonal upstream-freshness signal — runs alongside the "
              "per-type freshness/drift checks (overview/contradiction), which stay authoritative. Exit 0.")
    return 0
