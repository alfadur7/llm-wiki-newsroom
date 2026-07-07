"""Conflict axis lint — `_contradictions_themes.json` derivation integrity.

Sibling to `contradiction.py` (per-theme MD schema + JSON↔MD mapping).
This module is responsible for the **theme derivation result** as a
self-contained JSON document and is intentionally agnostic of the MD
file set:

  * JSON schema conformance (`.claude/commands/wiki-lint.md`
    Output Schema)
  * claim id validity vs `_contradictions.json`
  * exhaustive coverage (Core Principle 1)
  * Phase 2 conditions (`unassigned == []`, theme count cap, lower bound)
  * Freshness — `derived_at` vs `_contradictions.json` last-modified

JSON↔MD mapping (E) and frontmatter↔JSON drift (G) live in
`contradiction.py`, because both originate in MD-side staleness — the
JSON is SoT for "which themes exist" and `contradiction --fix` resolves
divergence by creating MD skeletons from the JSON.

`--fix` does not edit the JSON directly. Theme grouping is probabilistic
domain reasoning (Guide Core Principle 2/5), so the script emits a
"Claude rewrite instruction block" the same way `overview.py --fix` does
— Claude executes the two-phase pipeline against the Guide as SoT.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date as _date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import WIKI  # noqa: E402
sys.path.insert(0, str(Path(__file__).parent))
from _editor_date import last_commit_date  # noqa: E402

CONTRADICTIONS_DIR = WIKI / "contradictions"
CLAIMS_JSON = CONTRADICTIONS_DIR / "_contradictions.json"
THEMES_JSON = CONTRADICTIONS_DIR / "_contradictions_themes.json"
GUIDE_PATH = Path(".claude/commands/wiki-lint.md")

SLUG_RE = re.compile(r"^[a-z0-9-]+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RESERVED_SLUGS = {"theme", "aggregate"}  # reserved targets in `/wiki-lint contradiction <slug>` — both dispatch to non-theme branches (theme subcommand · L2-4 aggregate), so a same-named theme MD would be unreachable

PHASE2_THEME_CAP = 15  # soft recommendation — exceeding it enters the dual approval gate (`.claude/commands/wiki-lint.md` § Dual Approval Gate)
PHASE2_LOWER_BOUND = 5
PHASE2_UPPER_BOUND = 50  # advisory — single-axis exemption always active
OTHER_FRAGMENTARY = "other-fragmentary"


def _load_json(path: Path) -> tuple[object | None, str | None]:
    """Return (parsed, error_message). parsed=None when unreadable/invalid."""
    if not path.exists():
        return None, f"{path} not found"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except json.JSONDecodeError as e:
        return None, f"{path}: invalid JSON — {e}"


def _claims_last_change_date() -> str | None:
    """YYYY-MM-DD of the most recent commit touching `_contradictions.json`.

    Returns None if git is unavailable or the file is untracked.
    """
    return last_commit_date(CLAIMS_JSON)


def _claims_has_uncommitted() -> bool:
    """True if `_contradictions.json` has uncommitted edits."""
    try:
        r = subprocess.run(
            ["git", "status", "--porcelain", "--", str(CLAIMS_JSON)],
            capture_output=True, text=True, timeout=5, check=False,
            encoding="utf-8", errors="replace",
        )
        if r.returncode != 0:
            return False
        return bool(r.stdout.strip())
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return False


def _check_schema(themes_doc: dict) -> list[str]:
    """A. JSON schema conformance — Guide Output Schema."""
    issues: list[str] = []

    required_keys = {"derived_at", "derived_by", "phase", "source_count", "themes", "unassigned"}
    for k in required_keys - set(themes_doc.keys()):
        issues.append(f"  _contradictions_themes.json: missing top-level key `{k}`")

    derived_at = themes_doc.get("derived_at")
    if isinstance(derived_at, str) and not DATE_RE.match(derived_at):
        issues.append(f"  derived_at `{derived_at}` does not match YYYY-MM-DD")

    derived_by = themes_doc.get("derived_by")
    if derived_by != "claude":
        issues.append(f"  derived_by `{derived_by!r}` — expected literal \"claude\"")

    phase = themes_doc.get("phase")
    if phase not in (1, 2):
        issues.append(f"  phase `{phase!r}` — expected integer 1 or 2")

    if not isinstance(themes_doc.get("source_count"), int):
        issues.append(f"  source_count must be integer, got {type(themes_doc.get('source_count')).__name__}")

    themes = themes_doc.get("themes")
    if not isinstance(themes, dict):
        issues.append(f"  themes must be object, got {type(themes).__name__}")
        return issues

    if OTHER_FRAGMENTARY not in themes:
        issues.append(f"  themes missing required `{OTHER_FRAGMENTARY}` bucket (Core Principle 6)")

    for slug, theme in themes.items():
        if not SLUG_RE.match(slug):
            issues.append(f"  theme slug `{slug}` violates [a-z0-9-]+ pattern")
        if slug in RESERVED_SLUGS:
            issues.append(
                f"  theme slug `{slug}` is reserved (collides with "
                f"`/wiki-lint contradiction {slug}` subcommand)"
            )
        if not isinstance(theme, dict):
            issues.append(f"  theme `{slug}` must be object, got {type(theme).__name__}")
            continue
        if "name" not in theme or not isinstance(theme["name"], str) or not theme["name"].strip():
            issues.append(f"  theme `{slug}`.name missing or empty")
        if "claim_ids" not in theme or not isinstance(theme["claim_ids"], list):
            issues.append(f"  theme `{slug}`.claim_ids missing or not a list")
        else:
            for cid in theme["claim_ids"]:
                if not isinstance(cid, str):
                    issues.append(f"  theme `{slug}`.claim_ids contains non-string element {cid!r}")
                    break

    unassigned = themes_doc.get("unassigned")
    if not isinstance(unassigned, list):
        issues.append(f"  unassigned must be array, got {type(unassigned).__name__}")

    return issues


def _check_ids(themes_doc: dict, claim_ids_in_db: set[str]) -> list[str]:
    """B. claim id validity + intra-theme duplicate check."""
    issues: list[str] = []
    themes = themes_doc.get("themes", {})

    for slug, theme in themes.items():
        if not isinstance(theme, dict):
            continue
        cids = theme.get("claim_ids", [])
        if not isinstance(cids, list):
            continue
        seen: set[str] = set()
        for cid in cids:
            if not isinstance(cid, str):
                continue
            if cid not in claim_ids_in_db:
                issues.append(
                    f"  theme `{slug}`.claim_ids contains `{cid}` not in _contradictions.json"
                )
            if cid in seen:
                issues.append(f"  theme `{slug}`.claim_ids has duplicate `{cid}`")
            seen.add(cid)

    for cid in themes_doc.get("unassigned", []):
        if not isinstance(cid, str):
            continue
        if cid not in claim_ids_in_db:
            issues.append(f"  unassigned contains `{cid}` not in _contradictions.json")

    return issues


def _check_coverage(themes_doc: dict, claim_ids_in_db: set[str]) -> list[str]:
    """C. exhaustive coverage — Core Principle 1."""
    issues: list[str] = []
    themes = themes_doc.get("themes", {})

    covered: set[str] = set()
    for theme in themes.values():
        if not isinstance(theme, dict):
            continue
        for cid in theme.get("claim_ids", []) or []:
            if isinstance(cid, str):
                covered.add(cid)
    for cid in themes_doc.get("unassigned", []):
        if isinstance(cid, str):
            covered.add(cid)

    declared = themes_doc.get("source_count")
    if isinstance(declared, int) and declared != len(claim_ids_in_db):
        issues.append(
            f"  source_count={declared} mismatches _contradictions.json record count "
            f"({len(claim_ids_in_db)})"
        )

    missing = claim_ids_in_db - covered
    if missing:
        sample = sorted(missing)[:5]
        more = f" (+{len(missing) - len(sample)} more)" if len(missing) > 5 else ""
        issues.append(
            f"  coverage gap — {len(missing)} claim id(s) absent from both themes and unassigned: "
            f"{sample}{more}"
        )

    extra = covered - claim_ids_in_db
    if extra:
        sample = sorted(extra)[:5]
        more = f" (+{len(extra) - len(sample)} more)" if len(extra) > 5 else ""
        issues.append(
            f"  unknown ids — {len(extra)} id(s) referenced but not in _contradictions.json: "
            f"{sample}{more}"
        )

    return issues


def _check_phase2(themes_doc: dict) -> tuple[list[str], list[str]]:
    """D. Phase 2 conditions — only enforced when phase == 2.

    Returns (hard_issues, advisory_warnings). Hard issues fail the lint;
    advisory warnings (Core Principle 5 lower-bound exception, upper bound)
    print but do not fail.
    """
    if themes_doc.get("phase") != 2:
        return [], []

    issues: list[str] = []
    warnings: list[str] = []

    unassigned = themes_doc.get("unassigned", [])
    if isinstance(unassigned, list) and len(unassigned) > 0:
        sample = unassigned[:5]
        more = f" (+{len(unassigned) - 5} more)" if len(unassigned) > 5 else ""
        issues.append(
            f"  Phase 2 violation — unassigned must be empty, got "
            f"{len(unassigned)} item(s): {sample}{more}"
        )

    themes = themes_doc.get("themes", {})
    if isinstance(themes, dict):
        if len(themes) > PHASE2_THEME_CAP:
            warnings.append(
                f"  themes count {len(themes)} > {PHASE2_THEME_CAP} (soft recommendation). "
                f"Adding a new theme slug enters the dual approval gate (Editor-in-Chief first + wiki operator second); the worker must record the rationale internally — "
                f"`.claude/commands/wiki-lint.md` § Dual Approval Gate"
            )
        for slug, theme in themes.items():
            if slug == OTHER_FRAGMENTARY or not isinstance(theme, dict):
                continue
            cids = theme.get("claim_ids", []) or []
            n = len(cids)
            if n < PHASE2_LOWER_BOUND:
                warnings.append(
                    f"  theme `{slug}` has {n} claim(s) — below Phase 2 lower bound "
                    f"{PHASE2_LOWER_BOUND}. Verify Core Principle 5 (a)/(b)/(c) exception, "
                    f"otherwise absorb into `{OTHER_FRAGMENTARY}`"
                )
            if n > PHASE2_UPPER_BOUND:
                warnings.append(
                    f"  theme `{slug}` has {n} claim(s) — above advisory upper bound "
                    f"{PHASE2_UPPER_BOUND}. Consider sub-axis split, OR verify "
                    f"single-axis exemption — when all sub-axis candidates are just "
                    f"different facets of the same conflict axis, staying above {PHASE2_UPPER_BOUND} is acceptable (Stage 2.7 (c), single-axis exemption always active)"
                )

    return issues, warnings


def is_themes_json_stale() -> tuple[bool, str | None]:
    """Return (stale, reason) for `_contradictions_themes.json` vs claims DB.

    Public helper used by `contradiction.py --fix` to gate destructive MD
    reconciliation: if the SoT JSON is older than the claims DB it was
    derived from, fixing MDs to match it would propagate stale theme
    boundaries. Returns (True, message) when stale, (False, None) when
    fresh or freshness can't be determined.

    A stale signal needs at least one of:
      * source_count snapshot ≠ _contradictions.json current record count
        (record-count drift — most direct staleness signal, independent of
        commit timestamps which can lag behind raw DB regeneration)
      * _contradictions.json has uncommitted edits AND derived_at < today
      * _contradictions.json last commit date > derived_at
    """
    if not THEMES_JSON.exists():
        return False, None
    try:
        themes_doc = json.loads(THEMES_JSON.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False, None
    if not isinstance(themes_doc, dict):
        return False, None

    declared_count = themes_doc.get("source_count")
    if isinstance(declared_count, int):
        try:
            claims_doc = json.loads(CLAIMS_JSON.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError, FileNotFoundError):
            claims_doc = None
        if isinstance(claims_doc, list) and len(claims_doc) != declared_count:
            delta = len(claims_doc) - declared_count
            return True, (
                f"source_count={declared_count} but _contradictions.json has "
                f"{len(claims_doc)} record(s) (drift {delta:+d})"
            )

    derived_at = themes_doc.get("derived_at")
    if not isinstance(derived_at, str) or not DATE_RE.match(derived_at):
        return False, None

    today = _date.today().isoformat()
    if _claims_has_uncommitted() and derived_at < today:
        return True, (
            f"derived_at={derived_at}, but _contradictions.json has "
            f"uncommitted edits (today={today})"
        )

    commit_date = _claims_last_change_date()
    if commit_date and derived_at < commit_date:
        return True, (
            f"derived_at={derived_at}, but _contradictions.json last "
            f"changed on {commit_date}"
        )
    return False, None


def _check_freshness(themes_doc: dict) -> str | None:
    """F. Freshness — derived_at vs _contradictions.json last-change.

    Renders only the two timestamp-based staleness signals (uncommitted
    edits, commit-date drift) as an advisory line. The third signal
    `is_themes_json_stale()` checks — source_count/record-count drift — is
    surfaced separately as a hard issue by `_check_coverage`, so it is
    intentionally not duplicated here. (Unlike `is_themes_json_stale()`,
    this does not re-read THEMES_JSON because the caller already has it parsed.)
    """
    derived_at = themes_doc.get("derived_at")
    if not isinstance(derived_at, str) or not DATE_RE.match(derived_at):
        return None

    today = _date.today().isoformat()
    if _claims_has_uncommitted() and derived_at < today:
        return (
            f"  [Freshness] ⚠️ derived_at={derived_at} but _contradictions.json "
            f"has uncommitted edits (today={today}) — regeneration recommended"
        )

    commit_date = _claims_last_change_date()
    if commit_date and derived_at < commit_date:
        return (
            f"  [Freshness] ⚠️ derived_at={derived_at} but _contradictions.json "
            f"last changed in commit on {commit_date} — theme derivation is stale"
        )
    return None


def _print_rewrite_block() -> None:
    print()
    print("=" * 72)
    print("[/wiki-lint contradiction theme --fix] Claude rewrite instruction block")
    print("=" * 72)
    print("Target: wiki/contradictions/_contradictions_themes.json")
    print()
    print("Execution order (Claude):")
    print(f"  1. Read {GUIDE_PATH.as_posix()} (in full)")
    print(f"  2. Read {CLAIMS_JSON.as_posix()} (Phase 1 input)")
    print("  3. Phase 1 — Filter & Survey")
    print("     → separate fragmentary + identify unassigned (fresh derivation from raw claims)")
    print(f"     → Write {THEMES_JSON.as_posix()} (`phase: 1`)")
    print(f"  4. Read {THEMES_JSON.as_posix()} (Phase 1 output, Phase 2 input)")
    print("  5. Phase 2 — Converge with Source Detail")
    print("     → Priority Source Read (unassigned · ambiguous boundary · soft absorption candidates)")
    print(f"     → Write {THEMES_JSON.as_posix()} (`phase: 2`)")
    print("  6. Pass the entire Self-Validation Checklist (Guide § Self-Validation Checklist)")
    print("  7. Re-diagnose: `python tools/lint.py contradiction theme` → A·B·C·D·F PASS")
    print("  8. log.md append: `## [YYYY-MM-DD] lint | theme regeneration (phase 1→2)`")
    print()
    print("Follow-up guidance (separate invocation — outside this procedure):")
    print("  - If JSON↔MD slug mapping remains: `/wiki-lint contradiction --fix`")
    print("    (JSON-only → create MD skeleton / MD-only → delete orphan MD, with a confirmation prompt)")
    print("  - Rewrite theme MD body: `/wiki-lint contradiction <theme> --fix`")
    print("    (Claude EDITOR rewrite instruction — enters authoring guide Part 1)")


def run(fix: bool = False) -> int:
    """Entry point for `python tools/lint.py contradiction theme [--fix]`.

    fix=False → diagnostics only (read-only).
    fix=True  → diagnostics + Claude rewrite instruction block.

    Exit codes:
      0 — A·B·C pass (D·F warnings do not gate)
      1 — schema / id / coverage violation
      2 — input file unreadable
    """
    claims_doc, claims_err = _load_json(CLAIMS_JSON)
    themes_doc, themes_err = _load_json(THEMES_JSON)

    if claims_err:
        print(f"ERROR: {claims_err}", file=sys.stderr)
        return 2
    if themes_err:
        print(f"ERROR: {themes_err}", file=sys.stderr)
        print(
            "  Hint: run `/wiki-lint contradiction theme --fix` to regenerate",
            file=sys.stderr,
        )
        return 2

    if not isinstance(claims_doc, list):
        print(f"ERROR: {CLAIMS_JSON} top-level must be array", file=sys.stderr)
        return 2
    if not isinstance(themes_doc, dict):
        print(f"ERROR: {THEMES_JSON} top-level must be object", file=sys.stderr)
        return 2

    claim_ids_in_db: set[str] = {
        c["id"] for c in claims_doc if isinstance(c, dict) and isinstance(c.get("id"), str)
    }

    schema_issues = _check_schema(themes_doc)

    # Normalize null/mistyped `themes`/`unassigned` to their empty defaults so the
    # id/coverage checks and the summary line below emit the clean exit-1 diagnostic
    # instead of crashing (_check_schema above already recorded the shape violation).
    # dict.get returns a stored `null` as-is, so an explicit isinstance guard — not a
    # default arg — is required.
    if not isinstance(themes_doc.get("themes"), dict):
        themes_doc["themes"] = {}
    if not isinstance(themes_doc.get("unassigned"), list):
        themes_doc["unassigned"] = []

    id_issues = _check_ids(themes_doc, claim_ids_in_db)
    coverage_issues = _check_coverage(themes_doc, claim_ids_in_db)
    phase2_issues, phase2_warnings = _check_phase2(themes_doc)
    freshness_warning = _check_freshness(themes_doc)

    hard_issues = schema_issues + id_issues + coverage_issues + phase2_issues

    n_themes = len(themes_doc.get("themes", {}))
    n_unassigned = len(themes_doc.get("unassigned", []))
    print(
        f"_contradictions_themes.json: phase={themes_doc.get('phase')} "
        f"derived_at={themes_doc.get('derived_at')} "
        f"themes={n_themes} unassigned={n_unassigned} "
        f"source_count={themes_doc.get('source_count')} "
        f"(_contradictions.json records: {len(claim_ids_in_db)})"
    )

    if hard_issues:
        print(f"\n[contradiction theme: {len(hard_issues)} hard issue(s)]")
        for line in hard_issues:
            print(line)

    if phase2_warnings:
        print(f"\n[contradiction theme: {len(phase2_warnings)} Phase 2 advisory warning(s)]")
        for line in phase2_warnings:
            print(line)

    if freshness_warning:
        print()
        print(freshness_warning)

    # Emit the regeneration chain marker only when there is actual chain
    # work pending — i.e. the theme map is stale or has integrity issues.
    # A fresh, clean, PASSing map must NOT emit the marker, or the
    # lint-chain-guard hook blocks indefinitely (marker ⟺ pending work,
    # per wiki-lint.md § Chain Markers Single SoT). phase2_warnings are
    # soft advisories and do not force regeneration.
    if fix and (freshness_warning or hard_issues):
        _print_rewrite_block()

    if hard_issues:
        print(
            "\nFAIL — _contradictions_themes.json has integrity issues. "
            "See .claude/commands/wiki-lint.md for derivation procedure."
        )
        return 1

    print("\nOK — contradiction theme: schema + ids + coverage")
    return 0


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true")
    args = ap.parse_args()
    sys.exit(run(fix=args.fix))
