"""Unified structural lint entry point for the LLM Wiki.

Organized as ten groups mapped onto the wiki's content taxonomy:

  graph         — L2-1↔L2-2 structure, references, and Leiden clusters
                  (structure · orphans · clusters · raw-files · internal-refs)
  hub           — L2-2 hub page coverage (frontmatter + body density + timeline + voice)
                  (speakers · suggestions · schema · voice · body · timeline)
  meta          — meta-doc conventions (CLAUDE.md + .claude/commands/ + .claude/layers/)
                  (schema — integrity + drift + language bundled; future expansion tracked)
  overview      — landscape axis L2-3/L2-4 (wiki/overviews/ + wiki/overview.md)
                  (target-based: <cluster-slug> | aggregate)
  contradiction — conflict axis L2-3 (wiki/contradictions/<theme>.md)
                  (target-based: <theme>; reserved subcmd: `theme`)
  source        — Phase 2 schema (claim atomization + citation type +
                  evidence grade) on wiki/sources/<slug>.md
                  (target-based: <slug>; advisory mode until migration done)
  synthesis     — L2-3 Q-A synthesis schema on wiki/syntheses/<slug>.md
                  (target-based: <slug>; advisory mode until seed calibration)
  trail         — L2-3 associative trail schema on wiki/trails/<slug>.md
                  (target-based: <slug>; advisory mode until seed calibration)
  timeline      — L2-2 standalone timeline schema on wiki/timelines/<slug>.md
                  (source-indexed → path flavor; region-regression guard).
                  Distinct from `hub timeline`, which lints the `## Timeline`
                  section embedded in a hub page (target-based: <slug>; advisory).
  staleness     — uniform layer-cascade staleness (reads graph/_dependencies.json:
                  page STALE ⇔ upstream changed after its last_updated). Runs in
                  `all` as INFORMATIONAL (non-gating) — surfaces the stale backlog
                  every sweep without blocking. Gating is deferred until the
                  backlog is triaged; the existing per-type freshness/drift/anchor
                  checks (orthogonal: metadata-hygiene·set-change·semantic) stay.

  all           — run every pass/fail group above, then suggestions (informational).

Usage:
  python tools/lint.py                              # all groups + suggestions (default)
  python tools/lint.py all                          # explicit
  python tools/lint.py graph                        # every subcommand under graph
  python tools/lint.py graph structure              # single subcommand
  python tools/lint.py graph orphans --fix          # subcommand with --fix
  python tools/lint.py graph drift                  # warm vs cold partition quality (opt-in; expensive)
  python tools/lint.py hub                          # speakers + suggestions + schema + voice + body + timeline
  python tools/lint.py hub speakers --min-quotes 3 --min-sources 3
  python tools/lint.py hub schema
  python tools/lint.py hub voice                    # entity+concept body self-meta voice
  python tools/lint.py hub body                     # body length + `## Connections` link count advisory
  python tools/lint.py hub timeline                 # `## Timeline narrative` ordering·restatement advisory
  python tools/lint.py meta                         # meta schema (integrity + drift + language)
  python tools/lint.py meta schema
  python tools/lint.py overview                     # every overview (L2-3 + L2-4)
  python tools/lint.py overview bank-it-modernization
  python tools/lint.py overview aggregate
  python tools/lint.py overview bank-it-modernization --fix   # rewrite instructions
  python tools/lint.py contradiction                # every theme MD
  python tools/lint.py contradiction ai-coding-productivity-debate
  python tools/lint.py contradiction --fix          # insert AUTO markers across themes
  python tools/lint.py contradiction theme          # _contradictions_themes.json ↔ MD consistency
  python tools/lint.py contradiction theme --fix    # Claude rewrite instructions for JSON regen
  python tools/lint.py source                       # corpus-level Phase 2 schema diagnosis
  python tools/lint.py source <slug>                # per-file Rubric output
  python tools/lint.py synthesis                     # corpus-level L2-3 synthesis schema
  python tools/lint.py synthesis <slug>             # per-file Rubric output
  python tools/lint.py synthesis <slug> --fix       # skeleton (if missing) + Claude rewrite block
  python tools/lint.py trail                         # corpus-level L2-3 trail schema
  python tools/lint.py trail <slug> [--fix]         # per-file Rubric (+ skeleton/rewrite block)
  python tools/lint.py staleness                     # layer-cascade staleness summary (all pages)
  python tools/lint.py staleness <slug>             # per-page staleness detail

--fix semantics (see README → /wiki-lint group table):
  graph --fix          → structure --fix (orphan hub stem ↔ source raw-text
                         matching → append `[[<hub>]]` to matched sources'
                         `## Connections`; non-matching hubs deferred as stub body
                         expansion follow-up)
                         + orphans --fix (source ## Connections → hub `sources:` sync)
                         + clusters --fix (regenerate _graph.json +
                         _clusters.json from current wiki — deterministic
                         Leiden rebuild; downstream MD edits skipped)
  hub --fix            → hub schema --fix only (auto-fill deterministic fields:
                         type from directory, last_updated from git log)
  meta --fix           → unsupported
  overview --fix       → with target: skeleton + AUTO markers + Claude rewrite block.
                         without target (inside all --fix): un-aliased cluster-link
                         auto-correction + skeleton for missing cluster overviews.
  contradiction --fix  → AUTO marker migration + missing H2 section placeholder insertion
                         (optional target filter)
  contradiction theme --fix
                       → Claude rewrite instruction block for regenerating
                         _contradictions_themes.json (Phase 1→2 per Guide). Script
                         never edits the JSON — handoff to Claude only.
  synthesis <slug> --fix
                       → create skeleton if file missing, then Claude rewrite
                         block (authoring handoff w/ roster completion criteria).
  trail <slug> --fix   → same as synthesis (skeleton + Claude rewrite block).
  all --fix            → mechanical repairs that each supporting group allows;
                         overview Claude rewrite + contradiction theme regeneration
                         NOT included (probabilistic-reasoning triggers must be
                         requested explicitly)

Exit codes:
  0 — every group passes
  1 — at least one group reports actionable issues
  2 — argument/usage error
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lint import (  # noqa: E402
    structure,
    source_orphans,
    cited_speakers,
    graph_clusters,
    graph_gaps,
    cluster_drift,
    internal_refs,
    meta_schema,
    hub_schema,
    hub_voice,
    hub_body,
    hub_timeline,
    hub_promotion,
    hub_demotion,
    overview,
    contradiction,
    contradiction_theme,
    raw_file_refs,
    suggestions,
    source,
    synthesis,
    trail,
    timeline,
    staleness,
)


# Group → subcommand dispatch table. Three kinds of subcommand entries:
#   - normal: {"<sub>": (label, fn, accepted-kwargs-set)}
#   - target-based (overview): {"_target": (label, fn, accepted)}
#     where the second positional argument is the target, not a subcommand.
#   - hybrid (contradiction): a literal subcommand (e.g. "theme") AND
#     "_target" coexist. Dispatch tries literal first, falls through to
#     _target. Reserved literal slugs are gated by the contradiction_theme
#     RESERVED_SLUGS set so they cannot collide with real theme filenames.
GROUPS: dict = {
    "graph": {
        "structure": ("Page structure",          structure.run,       {"fix"}),
        "orphans":   ("Source↔hub references",   source_orphans.run,  {"json_out", "fix"}),
        "clusters":  ("Cluster health",          graph_clusters.run,  {"json_out", "fix"}),
        "gaps":      ("Gap inventory",           graph_gaps.run,      {"json_out", "gap_type", "top"}),
        "drift":     ("Cluster drift",           cluster_drift.run,   {"json_out", "threshold"}),
        "raw-files": ("Source→raw references",   raw_file_refs.run,   {"fix"}),
        "internal-refs": ("Content→governance refs", internal_refs.run, set()),
    },
    "hub": {
        "speakers":    ("Cited speakers",       cited_speakers.run,  {"json_out", "min_quotes", "min_sources"}),
        "suggestions": ("Page-gap suggestions", suggestions.run,
                        {"json_out", "min_seeds", "min_mentions", "min_pages", "top"}),
        "schema":      ("L2-2 hub frontmatter", hub_schema.run,      {"fix"}),
        "voice":       ("L2-2 hub self-meta voice", hub_voice.run,   set()),
        "body":        ("L2-2 hub body density",    hub_body.run,    set()),
        "timeline":    ("L2-2 hub timeline narrative", hub_timeline.run, set()),
        "promotion":   ("L2-2 hub promotion candidate triage", hub_promotion.run, set()),
        "demotion":    ("L2-2 hub demotion/deletion candidate triage", hub_demotion.run, set()),
    },
    "meta": {
        "schema": ("Meta-doc schema",           meta_schema.run,     set()),
    },
    "overview": {
        "_target": ("Overview scope",           overview.run,        {"fix", "target", "auto_yes"}),
    },
    "contradiction": {
        "theme":   ("Theme derivation (JSON)",  contradiction_theme.run, {"fix"}),
        "_target": ("Contradiction scope",      contradiction.run,   {"fix", "target", "auto_yes"}),
    },
    "source": {
        "_target": ("Source schema (Phase 2)",  source.run,          {"fix", "target"}),
    },
    "synthesis": {
        "_target": ("Synthesis schema (L2-3)",  synthesis.run,       {"fix", "target"}),
    },
    "trail": {
        "_target": ("Trail schema (L2-3)",       trail.run,           {"fix", "target"}),
    },
    "timeline": {
        "_target": ("Timeline schema (L2-2 path)", timeline.run,      {"fix", "target"}),
    },
    "staleness": {
        "_target": ("Layer-cascade staleness",   staleness.run,       {"target"}),
    },
}

# Order for `all` / default run. `hub suggestions` is informational so we
# surface it last, outside the pass/fail summary — matching the prior UX.
ALL_ORDER = [
    ("graph", "structure"),
    ("graph", "orphans"),
    ("graph", "clusters"),
    ("graph", "raw-files"),
    ("graph", "internal-refs"),
    ("hub", "schema"),
    ("hub", "voice"),
    ("hub", "body"),
    ("hub", "timeline"),
    ("hub", "speakers"),
    ("meta", "schema"),
    ("overview", "_target"),
    ("contradiction", "_target"),
    ("contradiction", "theme"),
    ("source", "_target"),
    ("synthesis", "_target"),
    ("trail", "_target"),
    ("timeline", "_target"),
]
INFORMATIONAL = [("hub", "suggestions"), ("hub", "promotion"), ("hub", "demotion"), ("staleness", "_target")]

# Subcommands skipped during group runs (and `all`) because they re-run an
# expensive computation already implicit in the build pipeline or are
# information-only triggers for a downstream operator decision. Opt-in
# only: `python tools/lint.py graph drift` / `python tools/lint.py graph gaps`.
# `gaps` runs betweenness sampling for bridge and reads every hub MD frontmatter;
# `wiki-discover --gaps` / `wiki-news --gap` are the operator-facing entry
# points so `lint all` would just re-compute the same metrics for no benefit.
OPT_IN = {("graph", "drift"), ("graph", "gaps")}

# Group/sub pairs whose `--fix` action is gated to explicit invocation
# only — when reached through the `all --fix` path, the diagnosis still
# runs but `fix` is forced to False so the trigger emits no probabilistic-
# reasoning instruction block. Matches the overview rule: `overview --fix`
# without a target performs mechanical repairs only, and Claude rewrite
# is reserved for `overview <target> --fix`. For contradiction theme
# there is no target concept, so explicit `contradiction theme --fix`
# is the only path that should emit the regeneration block.
EXPLICIT_FIX_ONLY: set[tuple[str, str]] = {("contradiction", "theme")}


def _kwargs_for(accepted: set, args: argparse.Namespace, target: str | None = None) -> dict:
    kwargs: dict = {}
    if "json_out" in accepted:
        kwargs["json_out"] = args.json
    if "min_quotes" in accepted:
        kwargs["min_quotes"] = args.min_quotes
    if "min_sources" in accepted:
        kwargs["min_sources"] = args.min_sources
    if "fix" in accepted:
        kwargs["fix"] = args.fix
    if "target" in accepted:
        kwargs["target"] = target
    if "auto_yes" in accepted:
        kwargs["auto_yes"] = args.yes
    if "min_seeds" in accepted:
        kwargs["min_seeds"] = args.min_seeds
    if "min_mentions" in accepted:
        kwargs["min_mentions"] = args.min_mentions
    if "min_pages" in accepted:
        kwargs["min_pages"] = args.min_pages
    if "top" in accepted and args.top is not None:
        kwargs["top"] = args.top
    if "threshold" in accepted and args.threshold is not None:
        kwargs["threshold"] = args.threshold
    if "gap_type" in accepted and getattr(args, "gap_type", None):
        kwargs["gap_type"] = args.gap_type
    return kwargs


def _run_one(group: str, sub: str, args: argparse.Namespace, target: str | None = None) -> tuple[str, int]:
    label, fn, accepted = GROUPS[group][sub]
    display_sub = target if sub == "_target" and target else sub
    header = f"{group} {display_sub}" if sub != "_target" or target else group
    print("=" * 72)
    print(f"[{label}]  python tools/lint.py {header}")
    print("=" * 72)
    rc = fn(**_kwargs_for(accepted, args, target))
    print()
    return label, rc


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "group",
        nargs="?",
        default="all",
        choices=["all"] + list(GROUPS.keys()),
        help="Group to run, or 'all' for every group (default).",
    )
    ap.add_argument(
        "subcmd",
        nargs="?",
        default=None,
        help=(
            "For graph/hub/meta: subcommand name (omit to run the whole group). "
            "For overview/contradiction: target (cluster slug / 'aggregate' / theme slug)."
        ),
    )
    ap.add_argument("--json", action="store_true", help="Machine-readable JSON output where supported.")
    ap.add_argument("--min-quotes", type=int, default=3,
                    help="(hub speakers) minimum total quote occurrences (cited multiple times)")
    ap.add_argument("--min-sources", type=int, default=3,
                    help="(hub speakers) minimum distinct source files (appears across several sources)")
    ap.add_argument(
        "--fix", action="store_true",
        help=(
            "Group-scoped mechanical repair. See README → /wiki-lint group table for "
            "what each group's --fix actually does."
        ),
    )
    ap.add_argument(
        "--yes", "-y", action="store_true",
        help=(
            "Skip the create/delete confirmation prompt for `overview --fix` and "
            "`contradiction --fix`. Use only after reviewing the planned changes."
        ),
    )
    ap.add_argument("--min-seeds", type=int, default=2,
                    help="(hub suggestions) minimum distinct hub seeds for cross-cutting candidates")
    ap.add_argument("--min-mentions", type=int, default=10,
                    help="(hub suggestions) minimum total mentions for mined candidates")
    ap.add_argument("--min-pages", type=int, default=5,
                    help="(hub suggestions) minimum distinct pages for mined candidates")
    ap.add_argument("--top", type=int, default=None, help="(hub suggestions) cap results per signal")
    ap.add_argument(
        "--threshold", type=float, default=None,
        help="(graph drift) override the default cold-vs-warm relative quality "
             "gap threshold (default 0.005 = 0.5%%; also overridable via "
             "WIKI_LINT_DRIFT_THRESHOLD env var).",
    )
    ap.add_argument(
        "--gap-type", dest="gap_type",
        choices=graph_gaps.VALID_GAP_TYPES, default=None,
        help="(graph gaps) restrict diagnosis to a single gap slug "
             "(Track A auto-backfill: sparse-cluster·single-source·stale-hub; "
             "Track B operator-decision: bridge; Track C contradiction: orphan-claims·"
             "cap-theme·stale-theme; Track D derivation coverage: synthesis·trail·"
             "timeline. see .claude/operations/gap-detection-rollout.md).",
    )
    args = ap.parse_args()

    if args.group == "all":
        if args.subcmd is not None:
            print("ERROR: `all` does not accept a second positional argument.", file=sys.stderr)
            return 2
        return _run_all(args)

    group_map = GROUPS[args.group]

    # Hybrid group dispatch: a literal subcommand (e.g. `theme` under
    # `contradiction`) takes precedence over the `_target` fallback. This
    # keeps `contradiction theme` / `contradiction theme --fix` behaving
    # like a normal subcommand even though the same group also accepts
    # arbitrary theme slugs as targets.
    if (
        args.subcmd is not None
        and args.subcmd in group_map
        and not args.subcmd.startswith("_")
    ):
        _, rc = _run_one(args.group, args.subcmd, args)
        return rc

    # Target-based groups (overview / contradiction with target slug):
    # second positional = target. With no subcmd, fall through to the
    # group runner so hybrid groups execute every member (literal + _target).
    if "_target" in group_map:
        if args.subcmd is None:
            return _run_group(args.group, args)
        return _run_one(args.group, "_target", args, target=args.subcmd)[1]

    # Normal groups: second positional = subcommand (optional).
    if args.subcmd is None:
        return _run_group(args.group, args)

    if args.subcmd not in group_map:
        print(
            f"ERROR: `{args.subcmd}` is not a valid subcommand under `{args.group}`. "
            f"Valid: {sorted(group_map.keys())}",
            file=sys.stderr,
        )
        return 2

    _, rc = _run_one(args.group, args.subcmd, args)
    return rc


def _run_group(group: str, args: argparse.Namespace) -> int:
    """Run every subcommand under a normal (non-target) group."""
    summary: list[tuple[str, int]] = []
    overall = 0
    for sub in GROUPS[group]:
        # hub suggestions is informational — skip during group run, surface at end.
        if (group, sub) in INFORMATIONAL:
            continue
        if (group, sub) in OPT_IN:
            continue
        label, rc = _run_one(group, sub, args)
        summary.append((label, rc))
        if rc != 0:
            overall = 1

    print("=" * 72)
    print(f"SUMMARY — group `{group}`")
    print("=" * 72)
    for label, rc in summary:
        mark = "OK  " if rc == 0 else "FAIL"
        print(f"  [{mark}] {label}")
    print()

    # Surface informational subs under this group (currently only hub suggestions).
    for g, sub in INFORMATIONAL:
        if g != group:
            continue
        label, fn, accepted = GROUPS[g][sub]
        disp = g if sub == "_target" else f"{g} {sub}"
        print("=" * 72)
        print(f"[{label}]  python tools/lint.py {disp}   (informational — does not affect pass/fail)")
        print("=" * 72)
        fn(**_kwargs_for(accepted, args))
        print()

    return overall


def _run_all(args: argparse.Namespace) -> int:
    """Run every group's pass/fail subcommands + informational suggestions."""
    summary: list[tuple[str, int]] = []
    overall = 0
    original_fix = args.fix
    for group, sub in ALL_ORDER:
        # Target-based entries in all-run: pass None target → full scope.
        target = None
        # Force fix=False for entries whose --fix is reserved for explicit
        # invocation (e.g. probabilistic regeneration prompts).
        args.fix = False if (group, sub) in EXPLICIT_FIX_ONLY else original_fix
        label, rc = _run_one(group, sub, args, target=target)
        summary.append((label, rc))
        if rc != 0:
            overall = 1
    args.fix = original_fix

    # Chain-pending detection — `_lint/contradiction.py` sets a module-level
    # flag when `--fix` hits the stale-themes gate. Distinct from FAIL: the
    # gate emits a Claude rewrite block that MUST be executed before any
    # other lint/build action. SUMMARY surfaces this with a CHAIN label so
    # downstream readers (Claude included) cannot demote it to a generic
    # remaining-work item. `--yes` is the explicit opt-in for chain
    # execution (see `.claude/commands/wiki-lint.md` "Chain Execution
    # Obligation"). Exit code 2 distinguishes from generic FAIL=1.
    chain_reason = contradiction.chain_pending_reason()

    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    for label, rc in summary:
        if chain_reason and label == "Contradiction scope":
            mark = "CHAIN"
        else:
            mark = "OK  " if rc == 0 else "FAIL"
        print(f"  [{mark}] {label}")
    print()
    if chain_reason:
        print("⚡ CHAIN PENDING — Claude must execute the emitted rewrite block above")
        print(f"   (reason: {chain_reason})")
        print("   before authoring lint-report.md or running other lint/build commands.")
        print("   Overall: CHAIN-REQUIRED — exit code 2")
        return 2
    print("Overall: " + ("OK — all checks pass" if overall == 0 else "FAIL — see details above"))

    for group, sub in INFORMATIONAL:
        label, fn, accepted = GROUPS[group][sub]
        disp = group if sub == "_target" else f"{group} {sub}"
        print()
        print("=" * 72)
        print(f"[{label}]  python tools/lint.py {disp}   (informational — does not affect pass/fail)")
        print("=" * 72)
        fn(**_kwargs_for(accepted, args))
        print()

    return overall


if __name__ == "__main__":
    sys.exit(main())
