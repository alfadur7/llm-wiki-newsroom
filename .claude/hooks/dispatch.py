"""Single-process dispatcher for the Write|Edit hooks (pre + post) and the
PreToolUse(Bash|PowerShell) commit gate.

Replaces six per-event shell hooks (lint-report-guard · minimality-advisory ·
scratch-location-advisory / stub-build-advisory · stub-desk-advisory ·
incremental-lint-advisory) that each spawned 2-3 `python3 -c` JSON parses per
tool call — one stdin parse now serves all of them, and simultaneous
advisories merge into a single additionalContext payload instead of three.

Usage (from dispatch.sh): `python dispatch.py pre|post|pre-bash` with hook JSON
on stdin.
Exit codes: 0 advisory/no-op (stdout JSON additionalContext), 2 blocking
(stderr message — lint-report asymmetry guard only).
"""
import json
import os
import re
import shlex
import subprocess
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
# Ponytail advisory scope — project scripts: tools/ Python + the hook layer
# itself (.claude/hooks/ py|sh); hook code is as prone to accretion as tools/.
PONYTAIL_RE = re.compile(r"/tools/.*\.py$|/\.claude/hooks/.*\.(py|sh)$")
SCRATCH_EXTS = {".py", ".sh", ".tmp", ".scratch", ".ipynb"}
# Repo root derived from this hook's own location (<root>/.claude/hooks/dispatch.py)
# so the scratch advisory fires regardless of the clone directory name.
ROOT = Path(__file__).resolve().parents[2]
_REPO_ROOT = ROOT.as_posix().lower()
GUIDE_DIRS = ("/.claude/agents/", "/.claude/commands/", "/.claude/layers/",
              "/.claude/policies/", "/.claude/operations/")

# Subset of GUIDE surfaces that is desk-judged wiki-content authoring/review craft
# (NOT lint-scored) — edits here trigger the proposal-validation reflex (2b). Allowlist
# of the content standards + authoring/review roles; editor-in-chief (routing)·
# copyeditor (lint)·README (matrix)·skills (lint-scored path) are deliberately out.
# Behavioral-rule surfaces are also absent on purpose: whether an edit is
# substantive vs formal cannot be told from a file event — that classification
# belongs to the ladder's blind-review rung, which routes substantive behavioral
# changes to the runbook's probe-task variant.
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

# The five rungs, defined once — the edit-time advisory and the commit-time gate
# both print them and would otherwise drift apart.
LADDER_RUNGS = """  1. Quantitative lint — python tools/lint.py meta PASS (guideline-writing skill
     deliberation-narrative detectors + project voice patterns)
  2. Minimal-edit self-check — skill § Pruning + Bloat control; keep sibling
     voice/depth; present the check evidence (a bare "passed" is incomplete)
  3. Blind review (mandatory) — diff-only reviewer, substantive/invariant
     classification per hunk + gdl.* defects. Severity rule: critical/high fix
     now + re-pass; medium/low carry to the corpus (log_defect batch)
  4. Effect-measurement gate — substantive ∧ measurement-obligated type →
     an accept transition must exist before commit; otherwise revert the edit
     and measure (temporary isolation — re-applied on acceptance; 3 variants)
  5. Deliberation narrative to log.md — decision history, option comparisons and
     measurement narratives move to log.md; the body keeps operative rules only"""

GUIDE_MSG = """[minimality-advisory] GUIDELINE EDIT DETECTED

Guideline Verification Ladder required just before commit
(SoT: .claude/agents/editor-in-chief.md § Guideline Verification Ladder):

""" + LADDER_RUNGS + """

Reference: editor-in-chief.md § Guideline Verification Ladder +
           skills/guideline-writing/SKILL.md."""

COMMIT_GATE_HEAD = """[commit-gate] GUIDELINE FILE DIRTY AT COMMIT

"""
COMMIT_GATE_TAIL = """

The Guideline Verification Ladder is mandatory right before commit. This is not a
block — the hook cannot see whether the ladder ran, and this reminder may be read
*after* the commit command has already executed.

  · If the ladder has already run for the files above, proceed.
  · If it has not, stop here and run it now. If the commit already landed, do not
    revert it (the revert scope is the wiki operator's call) — carry the result
    into a follow-up commit.

""" + LADDER_RUNGS + """

Reference: .claude/agents/editor-in-chief.md § Guideline Verification Ladder +
           .claude/skills/guideline-writing/SKILL.md."""

PROPOSAL_VALIDATION_MSG = """[proposal-validation-advisory] DESK-JUDGED PROSE GUIDELINE EDIT DETECTED

If this edit is a **prose-rule change** affecting wiki content authoring/review quality
(layers authoring standards·rubric prose·desk lenses·reporter·columnist authoring craft),
proposal-validation measurement is required before adoption — fire it as a self-harness
reflex even without an explicit instruction:

  Inject the Control (current passage)·Treatment (strengthening) text into the agent prompt
  (measure with the file unedited)
  → held-in same-mechanism blind raw re-author + held-out over-fire canary
  → desk N≥2 blind scoring → judge acceptance by the step 6 rule (referenced below).
  Only on acceptance make the confirmed edit to this file + log the transition (log_defect kind:transition).

Measurement variant by guideline type (runbook): desk-judged prose → the blind batch
above · behavioral rule → probe task · lint-scored rule → deterministic before/after.
Exempt (no measurement): typo·slimming·structural/editorial·cross-reference fixes —
the ladder's blind-review rung classifies these invariant.

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

BROKEN_LINK_MSG_TMPL = """[broken-link-advisory] UNRESOLVED WIKILINK — {rel}

Unresolved: {hits}

Resolve each before hand-off — only the author knows which applies:
  - wrong target (typo · alias · rename) → correct the link
  - the page is planned for later this cycle → leave it; ingest fanout writes
    sources before stubs, so an unresolved link here is expected mid-cycle
  - entity/concept candidate → threshold check (`python tools/count_mentions.py
    <name>` + .claude/policies/naming.md): demote `[[X]]` to plain `X`, or
    propose the stub (creating one needs the operator gate)
  - any other page type → create it through its own command (.claude/commands/
    README.md Task Index), or demote the link

Non-blocking advisory; `lint graph structure` is the batch backstop and resolves
link targets against the same `tools/_lib.py` page set. Anchors (`[[Page#H]]`)
are checked only there.

Reference: .claude/policies/naming.md (entity/concept stub thresholds) +
CLAUDE.md "Human Reviewer Gate"."""

STUB_MSG_TMPL = """[stub-advisory] STUB MUTATION DETECTED — {rel}

L2-2 stub created/edited. Three follow-up obligations:

1. RECONNECT — the links coming *into* a new hub do not live in this file. Appending
   `[[<hub>]]` to the citing source's `## Connections` and syncing the hub's own
   `sources:` are two separate edits, and two commands do them as a pair
   (entities·concepts only — `structure --fix` does not scan timelines):
     python tools/lint.py graph structure --fix   # source `## Connections` <- [[hub]]
     python tools/lint.py graph orphans --fix     # hub `sources:` <- source
   The first prints this follow-up itself on success. Stopping after it leaves the hub's
   `sources:` out of step with the link just appended — and if that field was empty,
   `hub schema` FAILs too. Both commands are corpus-wide — neither takes a target, so
   one run can rewrite several source pages.
   Skip the pair and the new stub escapes as an isolated hub all the way to batch lint.
   Procedure and where it sits in the cycle: .claude/commands/wiki-ingest.md step 10.

2. BUILD — the pipeline artifacts are stale:
   - wiki/_backlinks.json (incoming wikilink index)
   - graph/_clusters.json·_graph.json (Leiden topology)
   - wiki/index.md (auto stats) · wiki/sources/_catalog*.md
   Run `python tools/build.py` before the next `/wiki-lint` cycle — otherwise
   graph structure surfaces a false orphan (regression 2026-05-09 SK Shieldus
   — backlinks not refreshed after stub creation, misjudged as orphan despite 4 wikilink refs).
   Build is idempotent — for a stub batch in the same turn, one run after the batch suffices.

3. DESK VERIFY₂ — an L2-2 stub carries a "Copy Editor + Desk" VERIFY obligation in the Layer×Cycle matrix.
   After build·lint (Copy Editor VERIFY₁) completes, invoke the Desk:
     Agent({{ subagent_type: 'desk', prompt: '... desk VERIFY₂ of new L2-2 stub ...' }})
   Byproduct stubs (byproducts of another cycle, e.g. broken-link remediation) get the same treatment —
   2026-05-20 incident: desk VERIFY₂ of 5 byproduct stubs was missed → 11 defects found after the fact.
   Stubs bypassed by explicit wiki-operator approval fall below the quantitative threshold, so review them at the Desk more strictly.

Reference: .claude/agents/README.md "Authoring Responsibilities"·"Content
Verification Ladder" stage 3·"Standard ADAPT chain" + .claude/layers/hub.md "stub authoring"."""

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

`graph`·`hub`·`meta` are corpus-wide groups — there, self-VERIFY₀ is satisfied by
0 items naming this file, not by a clean global run.

After ≤ 2 self-attempts for the same reason, resolve or force the handoff (blocks an infinite self-loop).

Reference: .claude/agents/columnist.md "self-VERIFY₀" + .claude/agents/README.md
           "Standard ADAPT chain" + .claude/agents/copyeditor.md "invocation contract"."""

PONYTAIL_MSG_TMPL = """[ponytail-advisory] SCRIPT AUTHORING — {rel}

Before writing/editing this file, load and apply the `ponytail-coding` skill via the Skill tool.
Ladder rung 1 first: does this need to exist at all? A no-op beats the cleverest implementation.
The gist: the code you didn't write is best — reuse an existing helper before writing new code.
Full discipline (the ladder·root-cause·output restraint) SoT: .claude/skills/ponytail-coding/SKILL.md.

Non-blocking advisory (generation-time recommendation). Divides labor with /simplify (after-the-fact cleanup)."""

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

    # 4) ponytail advisory — project-script authoring (generation-time reflex).
    if PONYTAIL_RE.search(path):
        rel = re.split(r"/(?=tools/|\.claude/hooks/)", path)[-1]
        messages.append(PONYTAIL_MSG_TMPL.format(rel=rel))

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

    # 3) broken wikilink advisory — deterministic detection at write time.
    #    Re-read from disk: an Edit's `new_string` is only the changed hunk, so it
    #    cannot see the file's other links. The tools/ import and file IO must
    #    never kill the hook, so the whole probe is guarded — the safe direction
    #    on a check failure is silence, not blocking the edit (batch is backstop).
    if "/wiki/" in path:
        bad: list = []
        try:
            # rpartition: the repo path itself may contain `/wiki/`, so the LAST
            # occurrence is the real vault boundary (`…/wiki/repo/wiki/x.md`).
            sys.path.insert(0, os.path.join(path.rpartition("/wiki/")[0], "tools"))
            from _lib import unresolved_wikilinks  # noqa: PLC0415
            with open(path, encoding="utf-8", errors="replace") as fh:
                bad = unresolved_wikilinks(fh.read())
        except Exception:
            bad = []
        # Message assembly sits OUTSIDE the guard — swallowing a template typo
        # (KeyError) too would make this advisory permanently silent.
        if bad:
            # Name the overflow — a silent cap reads as "these are all of them",
            # so an author clears 8 of 12 and believes the page is clean.
            hits = ", ".join(f"`[[{b}]]`" for b in bad[:8])
            if len(bad) > 8:
                hits += f" (+{len(bad) - 8} more)"
            messages.append(BROKEN_LINK_MSG_TMPL.format(rel=rel, hits=hits))

    _emit("PostToolUse", messages)
    return 0


# ------------------------------------------- commit-time ladder surface (pre-bash)

# Characters that form a shell operator. The newline belongs in here: `run lint →
# commit` on two lines is the very flow this gate exists for, and if a newline does
# not separate commands the gate goes silent the moment the first token is not
# `git`. The same characters inside quotes are already folded into a token by the
# lexer, so a commit subject is unaffected.
_OP_CHARS = "();<>|&\n"
# `git add` forms that stage more than their arguments name. `-u`/`--update` restage
# tracked modifications only — the same restriction `git commit -a` carries — so an
# untracked file under them is one the commit cannot carry.
_ADD_ALL = frozenset({"-A", "--all", "."})
_ADD_TRACKED = frozenset({"-u", "--update"})
# Commit options whose value is the next token.
_VALUE_OPTS = ("--message", "--file", "--author", "--date",
               "--reuse-message", "--reedit-message")
# Where a guideline file can live — the pathspec used when the command narrows to nothing.
GUIDE_SCOPE = ("CLAUDE.md", ".claude")


def _is_op(tok: str) -> bool:
    return bool(tok) and all(c in _OP_CHARS for c in tok)


def _lex(command: str) -> list[str]:
    """Shell tokens of a command; operators (`&&`·`;`·`|`·newline) come out as tokens.

    The load-bearing property is that `punctuation_chars` splits operators only
    **after** quotes are handled. Splitting on a regex first cuts a message like
    `-m 'fix: a; b'` in two, and both halves then die on an unbalanced quote —
    silencing the gate on exactly the commits it is for. Most of this repo's commit
    subjects carry `()` and a few carry `;`·`&`·`|`·`<`·`>` — reproduce with
    `git log --format=%s | grep -cE '[;|&<>]'`. A count written here goes stale on
    the next commit, which is how it got 5 out of date the first time.

    An unbalanced quote keeps what was read rather than dropping everything: in a
    PowerShell here-string or a heredoc-substituted message, the `git commit` has
    already been read by the time the imbalance appears. `escape=""` stops a
    Windows path's backslash from being eaten as an escape character.
    """
    lx = shlex.shlex(command, posix=True, punctuation_chars=_OP_CHARS)
    lx.whitespace_split = True
    lx.whitespace = " \t\r"
    lx.escape = ""
    toks: list[str] = []
    try:
        for t in lx:
            toks.append(t)
    except ValueError:          # unbalanced quote — the command is what came before it
        pass
    return toks


def _git_segments(command: str, sub: str) -> list[list[str]]:
    """Shell segments whose first token is git and that carry `sub` as its own token.

    Matching the string `commit` anywhere calls the payload down on a grep, an echo
    or a documentation body — measured here at eight over-fires across two review
    rotations, which is why the gate anchors on **command position** instead. A
    commit message body drops out for free: the lexer folds a quoted string into
    one token.

    A `<` operator **stops the scan**, at a known cost: a heredoc writing a
    document that contains `git commit` cannot forge a segment, but a real commit
    following a heredoc in the same call is lost along with it.
    """
    segs, cur = [], []
    for t in [*_lex(command), ";"]:
        if "<" in t and _is_op(t):
            break
        if _is_op(t):
            if cur and os.path.basename(cur[0]).removesuffix(".exe") == "git" and sub in cur:
                segs.append(cur)
            cur = []
        else:
            cur.append(t)
    return segs


def _guideline_paths(paths) -> list[str]:
    """Keep only guideline files — used for porcelain lines and command arguments alike."""
    return sorted({
        p for p in paths
        if p == "CLAUDE.md" or (p.endswith(".md") and any(d in "/" + p for d in GUIDE_DIRS))
    })


def _porcelain_paths(porcelain: str, tracked_only: bool = False) -> list[str]:
    """Paths out of `git status --porcelain`. On a rename the new name is the edit.

    `tracked_only` drops `??` lines — `git commit -a` stages tracked modifications and
    nothing else, so an untracked file listed there is a file that commit cannot carry.

    No backslash conversion: porcelain always emits forward slashes, so the only
    backslashes this could meet are `core.quotePath` C-escapes, which converting
    mangles into a garbage path that still fires. `_git` disables that quoting.
    """
    out = []
    for line in porcelain.splitlines():
        if tracked_only and line[:2] == "??":
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        out.append(path)
    return out


def _staged_scope(command: str) -> tuple[list[str], bool]:
    """(pathspec this command's `git add`s cover, whether they can stage an untracked file).

    Each `git add` contributes its own scope and they union: a broad flag with a pathspec
    is broad only inside it (`git add -A tools/`), a broad flag alone covers everything,
    and a later narrow add does not cancel an earlier broad one. Returns ([], _) when no
    `git add` in the command names anything.
    """
    paths: list[str] = []
    untracked = False
    for seg in _git_segments(command, "add"):
        named = [tok.replace("\\", "/") for tok in seg[1:]
                 if tok[:1] != "-" and tok != "add" and tok not in _ADD_ALL]
        broad = any(tok in _ADD_ALL or tok in _ADD_TRACKED for tok in seg)
        untracked = untracked or not any(tok in _ADD_TRACKED for tok in seg)
        paths += named or (list(GUIDE_SCOPE) if broad else [])
    return paths, untracked


def _commit_flags(seg: list[str]) -> list[str]:
    """Flag tokens of a commit segment, with option values skipped.

    A quoted `-m` value is one token, so a message of `-a quick fix` is read as the `-a`
    flag unless the value is skipped — measured naming three files on a command that
    stages nothing. The paths decision already excludes the message body; this is the
    flags decision.
    """
    out, skip = [], False
    for tok in seg[1:]:
        if skip:
            skip = False
        elif tok[:1] == "-":
            out.append(tok)
            # `-m`/`-F`/`-C`/`-c` and their combined short forms (`-am`) take the next
            # token as their value; `--message` and friends take it in the long form.
            skip = (tok in _VALUE_OPTS
                    or (tok[:2] != "--" and tok[-1:] in "mFCc"))
    return out


def _commit_pathspec(seg: list[str]) -> list[str]:
    """Paths after `--` in the commit segment — what the commit restricts itself to."""
    return ([tok.replace("\\", "/") for tok in seg[seg.index("--") + 1:]]
            if "--" in seg else [])


def _git(root, *args: str) -> str | None:
    try:
        return subprocess.run(
            ["git", "-C", str(root), "-c", "core.quotePath=false", *args],
            capture_output=True, text=True, encoding="utf-8", timeout=5,
        ).stdout
    except Exception:
        return None        # a guard that cannot read git stays silent rather than noisy


def run_pre_bash(data: dict) -> int:
    """PreToolUse(Bash|PowerShell) — surface the ladder when a commit carries a guideline edit.

    Every guard and advisory in this file hangs off the Write|Edit matcher, so a
    file fixed with a heredoc or `sed` passes none of them — including the hook the
    ladder itself cites as its "no memory dependence" basis (the 2026-08-22
    incident, where three rungs went unrun).

    Advisory, never a block: the hook cannot observe whether the ladder already ran,
    and blocking would stop the compliant commit along with the careless one. The
    price of that is measured — the hook runs *before* the command, but its
    additionalContext enters the context *after* the tool result, so the commit can
    land first and the ladder become after-the-fact. Hence the message names the
    not-yet-run branch too.
    """
    ti = data.get("tool_input")
    command = ti.get("command") if isinstance(ti, dict) else None
    if not isinstance(command, str):
        return 0
    segs = _git_segments(command, "commit")
    if not segs:
        return 0

    # `git -C <dir> commit` can commit a different repository, and pinning to this
    # hook's own location answers it with *this* repo's dirty files (confirmed here
    # by running the hook from another repo). Ask for the toplevel and stay silent
    # unless it is this repo. The `-C` search stops at the subcommand: reading
    # `git commit -C HEAD` (message reuse) as a path empties the lookup and
    # silences the gate.
    seg = segs[0]
    head = seg[:seg.index("commit")]
    at = head.index("-C") + 1 if "-C" in head else None
    root = _git(head[at] if at and at < len(head) else ROOT, "rev-parse", "--show-toplevel")
    if not root or Path(root.strip()) != ROOT:
        return 0

    # What the commit actually carries — the index first. A `git add X && git commit`
    # in one call has an empty index at this point, so the working tree is narrowed
    # to the paths the command named. Reading the whole repo names CLAUDE.md on every
    # unrelated commit and re-fires until that file is itself committed. The
    # exceptions are `-a` (all tracked files) and `git add -A`/a directory — nothing
    # to narrow by, so the whole repo is right.
    flags = _commit_flags(seg)
    commit_all = any(t == "--all" or (t[:2] != "--" and "a" in t) for t in flags)
    # A commit pathspec decides alone — those paths are committed and nothing else is,
    # whatever the index holds and whatever `git add` staged before it.
    pathspec = _commit_pathspec(seg)
    staged = _git(ROOT, "diff", "--cached", "--name-only", "--", *(pathspec or GUIDE_SCOPE))
    hits = _guideline_paths((staged or "").splitlines())
    if not hits:
        if pathspec:
            # A commit pathspec carries tracked paths only — `git commit -- <untracked>`
            # is an error, and over a directory it commits the tracked changes alone.
            scope, untracked = pathspec, False
        elif commit_all:
            scope, untracked = list(GUIDE_SCOPE), False
        else:
            scope, untracked = _staged_scope(command)
        if scope:
            # `-uall`: without it git collapses an untracked directory to a single `??
            # <dir>/` line, so a new guideline file in a new directory is never named.
            dirty = _git(ROOT, "status", "--porcelain", "-uall", "--", *scope)
            hits = _guideline_paths(_porcelain_paths(dirty or "", tracked_only=not untracked))
    if "--amend" in flags:
        # An amend rewrites the commit it replaces, so that commit's files are carried
        # too — without this the gate is silent on an amend of a guideline commit.
        head = _git(ROOT, "show", "--name-only", "--format=", "HEAD")
        hits = sorted(set(hits) | set(_guideline_paths((head or "").split())))
    if not hits:
        return 0
    _emit("PreToolUse", [COMMIT_GATE_HEAD + "\n".join("  " + h for h in hits)
                          + COMMIT_GATE_TAIL])
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
    if phase == "pre-bash":
        return run_pre_bash(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
