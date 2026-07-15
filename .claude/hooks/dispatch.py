"""Single-process dispatcher for every Write|Edit hook (pre + post).

Replaces six per-event shell hooks (lint-report-guard · minimality-advisory ·
scratch-location-advisory / stub-build-advisory · stub-desk-advisory ·
incremental-lint-advisory) that each spawned 2-3 `python3 -c` JSON parses per
tool call — one stdin parse now serves all of them, and simultaneous
advisories merge into a single additionalContext payload instead of three.

Usage (from dispatch.sh): `python dispatch.py pre|post` with hook JSON on stdin.
Exit codes: 0 advisory/no-op (stdout JSON additionalContext), 2 blocking
(stderr message — lint-report asymmetry guard only).
"""
import json
import re
import sys
from pathlib import Path

import check_bullet_depth

# Per-target drift block (`- 🔴/🟡/🟢 <slug> …`). 🔴/🟡 blocks self-identify by
# their `*_jaccard` metric or `/wiki-lint <group>` action; 🟢-stable blocks carry
# neither (`🟢 <slug> — drift stable`, wiki-lint.md), so they are attributed to the
# section they fall under — see `_drift_group_counts`.
_DRIFT_BLOCK_RE = re.compile(r"^[\s>]*[-*]\s*(?:🔴|🟡|🟢)\s+[a-z][a-z0-9-]+")
_OV_SIGNAL_RE = re.compile(r"member_jaccard|/wiki-lint\s+overview")
_CN_SIGNAL_RE = re.compile(r"claim_jaccard|/wiki-lint\s+contradiction")


def _drift_group_counts(scan: str) -> tuple[int, int]:
    """Count per-target drift blocks per group → (overview, contradiction).

    A 🟢-stable block (`🟢 <slug> — drift stable`) carries no `*_jaccard` metric,
    so the earlier metric-only regexes counted an all-stable group as 0 and
    falsely flagged asymmetry. Here 🔴/🟡 blocks self-identify by their metric or
    `/wiki-lint <group>` action; an unmarked 🟢 block inherits the current section,
    set by the nearest preceding heading/bold-label naming a group.
    """
    ov = cn = 0
    section = None  # 'ov' | 'cn' | None
    for ln in scan.splitlines():
        low = ln.lower()
        is_block = bool(_DRIFT_BLOCK_RE.match(ln))
        stripped = ln.lstrip()
        if not is_block and (stripped.startswith("#") or stripped.startswith("**") or "example (" in low):
            if "overview" in low:
                section = "ov"
            elif "contradiction" in low:
                section = "cn"
        line_group = "ov" if _OV_SIGNAL_RE.search(ln) else ("cn" if _CN_SIGNAL_RE.search(ln) else None)
        if line_group:
            section = line_group
        if is_block:
            g = line_group or section
            if g == "ov":
                ov += 1
            elif g == "cn":
                cn += 1
    return ov, cn
AUTO_MARKER_RE = re.compile(r"<!--\s*AUTO:")
SCRATCH_EXTS = {".py", ".sh", ".tmp", ".scratch", ".ipynb"}
# Repo root derived from this hook's own location (<root>/.claude/hooks/dispatch.py)
# so the scratch advisory fires regardless of the clone directory name.
_REPO_ROOT = Path(__file__).resolve().parents[2].as_posix().lower()
GUIDE_DIRS = ("/.claude/agents/", "/.claude/commands/", "/.claude/layers/",
              "/.claude/policies/", "/.claude/operations/")

# Subset of GUIDE surfaces that is desk-judged wiki-content authoring/review craft
# (NOT lint-scored) — edits here trigger the proposal-validation reflex (2b). Allowlist
# of the content standards + authoring/review roles; editor-in-chief (routing)·
# copyeditor (lint)·README (matrix)·skills (lint-scored path) are deliberately out.
CRAFT_PROSE_DIRS = ("/.claude/layers/",)
CRAFT_PROSE_FILES = ("/agents/desk.md", "/agents/reporter.md", "/agents/columnist.md")

# Auto-generated / immutable targets — hand edits via Write|Edit are silently
# overwritten by the next build or corrupt an immutable SoT. lint --fix and
# build.py reach these through the CLI (not Write|Edit), so they are unaffected.
# NOTE excluded on purpose: _contradictions_themes.json (Claude re-derives it),
# graph/cluster_labels.json (human-edited), raw/_inbox.md·_archive.md (queue append).
PROTECTED_EXACT = (
    "wiki/index.md",                              # build.py — auto stats + listing
    "wiki/_backlinks.json",                       # build.py incoming-link index
    "wiki/sources/_source_map.json",              # build.py url/path dedup map
    "wiki/contradictions/_contradictions.json",   # build.py — source ## Connections extraction
)
PROTECTED_GLOB = (
    re.compile(r"/graph/_[a-z0-9_]+\.json$"),            # _clusters·_graph·_overlays·_dependencies
    re.compile(r"/wiki/sources/_catalog[a-z0-9-]*\.md$"),  # build.py catalog
)
# ---------------------------------------------------------------- messages
# Message bodies are carried over from the individual pre-consolidation hooks
# (incident history preserved; references point at in-repo SoTs).

LINT_REPORT_OV_ONLY = """[lint-report-guard] ASYMMETRY DETECTED

overview group has per-cluster drift blocks (member_jaccard) but contradiction
group lacks per-theme blocks (claim_jaccard).

Required: add per-theme drift blocks for ALL keys in
wiki/contradictions/_contradictions_themes.json::themes before writing.

Format:
  - 🔴/🟡/🟢 <theme-slug> — claim_jaccard=X source_delta=±Y% (srcs A→B) top5_new=N → <action>

Reference: .claude/commands/wiki-lint.md "Required per-target Drift Block"."""

LINT_REPORT_CN_ONLY = """[lint-report-guard] ASYMMETRY DETECTED

contradiction group has per-theme drift blocks (claim_jaccard) but overview
group lacks per-cluster blocks (member_jaccard).

Required: add per-cluster drift blocks for ALL slugs in
graph/_clusters.json::clusters[] before writing.

Format:
  - 🔴/🟡/🟢 <cluster-slug> — member_jaccard=X source_delta=±Y% (srcs A→B) top10_new=N → <action>

Reference: .claude/commands/wiki-lint.md "Required per-target Drift Block"."""

PLAN_MSG = """[minimality-advisory] PLAN FILE WRITE DETECTED

5-step self-check required just before ExitPlanMode (SoT: .claude/skills/guideline-writing/SKILL.md, Bloat control):

  1. New section/table/matrix vs absorb one line into an existing section — absorb by default
  2. Zero duplication of another SoT's table/matrix — replace with a cross-reference
  3. Zero new Risk/invariant/caveat sections by default — prefer attaching a qualifier to an existing section
  4. When changed lines ≥ 50, a minimum-edit re-review is mandatory
  5. Read the full context of every changed file — do not call ExitPlanMode without that read

4 red flags (any single hit forces the 5-step re-review):
  - New sections added ≥ 2
  - Changed lines ≥ 50
  - New table/matrix added
  - The same information already exists in another SoT

T1 naming principle: new memory/policy/hook files default to a prescriptive
`no_X`·`X_to_Y`·`X_not_Y` form. descriptive forms (`*_voice`·`*_posture`) weaken recall.

Reference: .claude/skills/guideline-writing/SKILL.md (Bloat control)."""

GUIDE_MSG = """[minimality-advisory] GUIDELINE EDIT DETECTED

Claude-guideline-change Voice Pass required just before commit
(SoT: .claude/agents/editor-in-chief.md § Claude guideline-change Voice Pass):

  1. python tools/lint.py meta — voice group PASS (regex antipattern detection:
     decision option names·reinforcement round·introduction timestamp·external reference·absorption narrative)
  2. Slimming check — remove redundancy·decorative sentences·self-evident grounds, absorb into existing sections by default,
     keep surrounding bullet voice·depth consistent (no verbose additions)
  3. Qualitative — table-row restatement·self-containment (meaning clear without knowing other docs)·residual decision narrative
     + a blind review pass (diff-only reviewer, substantive/invariant classification —
     skill SoT: .claude/skills/guideline-writing/SKILL.md, Blind review protocol)

Steps 2 and 3 are complete only when the check evidence (edit↔sibling bullet
length/depth comparison, per-item findings) is presented in the reply — a bare
"passed" declaration is incomplete.

Move violating phrasings to log.md + remove them from the body.

Reference: editor-in-chief.md § Voice Pass + skills/guideline-writing/SKILL.md."""

PROPOSAL_VALIDATION_MSG = """[proposal-validation-advisory] DESK-JUDGED PROSE GUIDELINE EDIT DETECTED

If this edit is a **prose-rule change** affecting wiki content authoring/review quality
(layers authoring standards·rubric prose·desk lenses·reporter·columnist authoring craft),
proposal-validation measurement is required before adoption — fire it as a self-harness
reflex even without an explicit instruction:

  Inject the Control (current passage)·Treatment (strengthening) text into the agent prompt
  (measure with the file unedited)
  → held-in same-mechanism blind raw re-author + held-out over-fire canary
  → desk N≥2 blind scoring → accept = held-in ≥1 improvement ∧ no slice regresses.
  Only on acceptance make the confirmed edit to this file + log the transition (log_defect kind:transition).

Exception (no blind-desk batch needed): lint.py-scored rules (skills craft criteria.json·
quantitative rubric·policies lint) go through the single lint measurement path (separate)·
typo·slimming·structural/editorial·cross-reference fixes·routing·gate rules.

Same applies regardless of origin (evolve session·desk surfacing mid-cycle·self-proposal).

Reference: .claude/operations/proposal-validation-runbook.md "When to Run" +
           .claude/agents/editor-in-chief.md self-evolution workflow steps 6-7."""

SCRATCH_MSG_TMPL = """[scratch-location-advisory] PROJECT ROOT SCRIPT WRITE — {basename}

Project root should only host repo-managed files (README, CLAUDE.md,
.gitignore, settings, requirements). Script-like one-off files belong in:

  - c:/tmp/ or an OS temp directory       (temp scratch)
  - <project root>/tools/                  (when formally adopted — verb-form naming)

If permanent project tool, move under tools/ (verb-form naming).
If one-off scratch, retarget the temp directory.

Reference: 2026-05-08 incident — temp .py at project root;
this advisory is the structural prevention."""

STUB_MSG_TMPL = """[stub-advisory] STUB MUTATION DETECTED — {rel}

L2-2 stub created/edited. Two follow-up obligations:

1. BUILD — the pipeline artifacts are stale:
   - wiki/_backlinks.json (incoming wikilink index)
   - graph/_clusters.json·_graph.json (Leiden topology)
   - wiki/index.md (auto stats) · wiki/sources/_catalog*.md
   Run `python tools/build.py` before the next `/wiki-lint` cycle — otherwise
   graph structure surfaces a false orphan (regression 2026-05-09 SK Shieldus
   — backlinks not refreshed after stub creation, misjudged as orphan despite 4 wikilink refs).
   Build is idempotent — for a stub batch in the same turn, one run after the batch suffices.

2. DESK VERIFY₂ — an L2-2 stub carries a "Copy Editor + Desk" VERIFY obligation in the Layer×Cycle matrix.
   After build·lint (Copy Editor VERIFY₁) completes, invoke the Desk:
     Agent({{ subagent_type: 'desk', prompt: '... desk VERIFY₂ of new L2-2 stub ...' }})
   Byproduct stubs (byproducts of another cycle, e.g. broken-link remediation) get the same treatment —
   2026-05-20 incident: desk VERIFY₂ of 5 byproduct stubs was missed → 11 defects found after the fact.
   Stubs bypassed by explicit wiki-operator approval fall below the quantitative threshold, so review them at the Desk more strictly.

Reference: .claude/agents/README.md "Authoring Responsibilities"·"Verification
Ladder" stage 3·"Standard ADAPT chain" + .claude/layers/hub.md "stub authoring"."""

PROTECTED_MSG_TMPL = """[protected-path-guard] BLOCKED — {rel}

Target: {reason} — editing it directly means the next build·lint overwrites it or breaks an SoT.

  - build artifacts (index.md·_backlinks.json·graph/_*.json·_catalog*·_source_map·
    _contradictions.json): fix the input (source·hub) and regenerate via `python tools/build.py`
  - raw/ originals: immutable — write analysis·interpretation on a wiki/ page

Reference: CLAUDE.md ".claude/hooks/" (protected-path guard) +
           .claude/policies/directory-layout.md (auto-generated vs. human-edited split)."""

INCR_LINT_MSG_TMPL = """[incremental-lint-advisory] {scope_label} EDIT DETECTED — {rel}

self-VERIFY₀ recommended before handoff to VERIFY₁ (Copy Editor):
  python tools/lint.py {group} {target}

Surface defects early while writing so they are remedied before the Desk handoff.
Quantitative scope only — qualitative self-review is still the Desk's domain
(.claude/agents/desk.md).

After ≤ 2 self-attempts for the same reason, PASS or force the handoff (blocks an infinite self-loop).

Reference: .claude/agents/columnist.md "self-VERIFY₀" + .claude/agents/README.md
           "Standard ADAPT chain" + .claude/agents/copyeditor.md "invocation contract"."""

PONYTAIL_MSG_TMPL = """[ponytail-advisory] tools/ PYTHON AUTHORING — {rel}

Before writing/editing this file, load and apply the `ponytail-coding` skill via the Skill tool.
The gist: the code you didn't write is best — reuse an existing helper before writing new code.
Full discipline (the ladder·root-cause·output restraint) SoT: .claude/skills/ponytail-coding/SKILL.md.

Non-blocking advisory (generation-time recommendation). Divides labor with karpathy (assumptions·success criteria)·/simplify (after-the-fact cleanup)."""

# ---------------------------------------------------------------- helpers


def _emit(event_name: str, messages: list[str]) -> None:
    if not messages:
        return
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": "\n\n---\n\n".join(messages),
        }
    }))


def _rel_wiki(path: str) -> str:
    m = re.search(r"(wiki/.*)", path)
    return m.group(1) if m else path


def _protected_path(path: str, tool_name: str = "", content: str = "") -> str | None:
    """Return a reason string if `path` is an auto-generated/immutable target
    that must not be hand-edited via Write|Edit, else None. `path` is slash-
    normalized.

    Inbox WebFetch-fallback exception: the 2nd-stage fetch (wiki-ingest.md
    Inbox Mode) legitimately Writes a NEW raw/ file whose frontmatter keeps
    the `source:` URL — a Write to a not-yet-existing raw path with a
    `source: http...` line passes; Edits and URL-less writes stay blocked.
    """
    if any(("/" + path).endswith("/" + p) for p in PROTECTED_EXACT):
        return "build artifact"
    if any(rx.search(path) for rx in PROTECTED_GLOB):
        return "build artifact"
    m = re.search(r"/raw/(.+)$", path)
    if m and m.group(1) not in ("_inbox.md", "_archive.md"):
        if (tool_name == "Write" and not Path(path).exists()
                and re.search(r"^source:\s*['\"]?https?://", content, re.MULTILINE)):
            return None
        return "raw/ original (immutable)"
    return None


def _incremental_target(path: str) -> tuple[str, str, str] | None:
    """Columnist-layer path → (group, target, scope_label). None = no advisory."""
    if path.endswith("wiki/overview.md"):
        return "overview", "aggregate", "L2-4 root overview"
    if path.endswith("wiki/contradiction.md"):
        return "contradiction", "aggregate", "L2-4 root contradiction"
    slug = path.rsplit("/", 1)[-1].removesuffix(".md")
    if "/wiki/overviews/" in path:
        return "overview", slug, "L2-3 cluster overview"
    if "/wiki/contradictions/" in path:
        return "contradiction", slug, "L2-3 theme contradiction"
    if "/wiki/entities/" in path or "/wiki/concepts/" in path:
        return "hub", "body", "L2-2 hub body"
    if "/wiki/timelines/" in path:
        return "hub", "timeline", "L2-2 timeline"
    if "/wiki/syntheses/" in path:
        return "synthesis", slug, "L2-3 Q-A synthesis"
    if "/wiki/trails/" in path:
        return "trail", slug, "L2-3 associative trail"
    return None


# ---------------------------------------------------------------- phases


def run_pre(data: dict) -> int:
    tool_input = data.get("tool_input", {}) or {}
    path = (tool_input.get("file_path") or tool_input.get("path") or "").replace("\\", "/")
    content = tool_input.get("content") or tool_input.get("new_string") or ""

    # 0) protected-path guard — blocking (exit 2). Auto-gen/immutable targets.
    reason = _protected_path(path, data.get("tool_name", ""), content)
    if reason:
        print(PROTECTED_MSG_TMPL.format(rel=_rel_wiki(path), reason=reason), file=sys.stderr)
        return 2

    # 1) lint-report.md asymmetry guard — blocking (exit 2). Gate on key
    #    presence, not truthiness — a deletion Edit (new_string="") can strip one
    #    group from a symmetric file and must still be counted.
    if path.endswith("lint-report.md") and ("content" in tool_input or "new_string" in tool_input):
        # Count drift groups over the reconstructed post-edit *full file*, not the
        # raw Edit fragment — a partial Edit touching one group on an already-
        # symmetric file would otherwise be miscounted as asymmetric and falsely
        # blocked. expected_text degrades to None (→ fragment) on a non-matching
        # old_string or unreadable file, so no new false block is introduced.
        full, _ = check_bullet_depth.expected_text(tool_input)
        scan = full if full is not None else content
        ov, cn = _drift_group_counts(scan)
        if ov > 0 and cn == 0:
            print(LINT_REPORT_OV_ONLY, file=sys.stderr)
            return 2
        if cn > 0 and ov == 0:
            print(LINT_REPORT_CN_ONLY, file=sys.stderr)
            return 2

    messages: list[str] = []

    # 2) minimality advisory — plan files / guideline SoT.
    if "/plans/" in path and path.endswith(".md"):
        messages.append(PLAN_MSG)
    elif path.endswith(".md") and (
        path.endswith("/CLAUDE.md") or any(d in path for d in GUIDE_DIRS)
    ):
        msg = GUIDE_MSG
        try:
            depth = check_bullet_depth.analyze(data)
        except Exception:
            depth = ""
        if depth:
            msg = msg + "\n\n" + depth
        messages.append(msg)

    # 2b) proposal-validation reflex — desk-judged content craft (see CRAFT_PROSE_*).
    if path.endswith(".md") and (
        any(d in path for d in CRAFT_PROSE_DIRS)
        or path.endswith(CRAFT_PROSE_FILES)
    ):
        messages.append(PROPOSAL_VALIDATION_MSG)

    # 3) scratch-location advisory — Write only, project-root script files.
    if data.get("tool_name") == "Write" and path:
        parent = path.rsplit("/", 1)[0] if "/" in path else ""
        basename = path.rsplit("/", 1)[-1]
        ext = ("." + basename.rsplit(".", 1)[-1]).lower() if "." in basename else ""
        if parent.lower() == _REPO_ROOT and ext in SCRATCH_EXTS:
            messages.append(SCRATCH_MSG_TMPL.format(basename=basename))

    # 4) ponytail advisory — tools/ Python authoring (generation-time reflex).
    if re.search(r"/tools/.*\.py$", path):
        messages.append(PONYTAIL_MSG_TMPL.format(rel=path.rsplit("/tools/", 1)[-1]))

    _emit("PreToolUse", messages)
    return 0


def run_post(data: dict) -> int:
    tool_input = data.get("tool_input", {}) or {}
    path = (tool_input.get("file_path") or tool_input.get("path") or "").replace("\\", "/")
    if not path.endswith(".md") or "_catalog" in path or "_archive" in path:
        return 0

    messages: list[str] = []
    rel = _rel_wiki(path)

    # 1) stub build + desk advisory (entities·concepts·timelines).
    if re.search(r"wiki/(entities|concepts|timelines)/[^/]+\.md$", path):
        messages.append(STUB_MSG_TMPL.format(rel=rel))

    # 2) incremental self-VERIFY₀ advisory (columnist layers). If the new content
    #    has an AUTO marker it is a separate boundary-crossing region, so the
    #    advisory is skipped (parity with the old hook).
    content = tool_input.get("new_string") or tool_input.get("content") or ""
    if not AUTO_MARKER_RE.search(content):
        hit = _incremental_target(path)
        if hit:
            group, target, scope_label = hit
            messages.append(INCR_LINT_MSG_TMPL.format(
                scope_label=scope_label, rel=rel, group=group, target=target))

    _emit("PostToolUse", messages)
    return 0


def main() -> int:
    phase = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if phase == "pre":
        return run_pre(data)
    if phase == "post":
        return run_post(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
