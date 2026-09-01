"""Audit regression target tests — catches recurrences of the "copy then edit only
one side" class, such as divergent lint verdicts and F4 lint-ification."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_w2_unmeasurable_is_pass_in_both_paths():
    """A2/F5 regression — an unmeasurable body is PASS (displayed as n/a) identically for L2-3 and L2-4.

    Previously: L2-3 serialized inf→None→⚠️, while L2-4 gave inf→✅, opposite verdicts for the same state.
    """
    import overview  # tools/_lint/ — includes manifest/skill loading (assumes the repo)

    m = {
        "total": 200, "lead_density": 1.0, "body_density": 0.0,
        "lead_body_ratio": None,  # serialized representation of inf = unmeasurable
        "dup_total": 0, "contradiction_refs": 1,
        "r1_hot": [], "r2_violations": [], "b1_hits": [],
        "l1_violations": [], "l2_violations": [], "l3_violations": [],
        "s6_long": [], "s6_para_anti": [],
        "g1_grade_meta": 99, "g2_cite_type_meta": 99,
        "duplicates": [],
    }
    lines = overview._format_metrics_line(m)
    w2_segment = next(seg for seg in lines[0].split("  ") if seg.startswith("W2"))
    assert "ratio=n/a" in w2_segment and "✅" in w2_segment


def test_paragraph_count_is_module_level_single_definition():
    """F5 regression — prevent recurrence of nested duplication (2 copies) of _paragraph_count."""
    import overview

    src = (ROOT / "tools" / "_lint" / "overview.py").read_text(encoding="utf-8")
    assert src.count("def _paragraph_count") == 1
    assert overview._paragraph_count("a\n\nb\n\nc") == 3
    assert overview._paragraph_count("") == 1  # minimum 1 (denominator protection)


def test_skeleton_overview_copies_stay_in_lockstep():
    """Audit regression — `_skeleton_overview` is deliberately duplicated between the
    builder (`_build/clusters.py`, which writes the skeleton) and the lint SoT
    (`_lint/overview.py`, which checks it). The two must emit byte-identical output or
    the lint flags the builder's own product. This asserts the function bodies stay
    identical (docstrings excluded) so a future edit to one copy fails loudly here."""
    import ast

    def _body(path):
        src = path.read_text(encoding="utf-8")
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.FunctionDef) and node.name == "_skeleton_overview":
                if node.body and isinstance(node.body[0], ast.Expr) and isinstance(
                    getattr(node.body[0], "value", None), ast.Constant
                ):
                    node.body = node.body[1:]  # drop the docstring
                return ast.dump(node)
        raise AssertionError(f"_skeleton_overview not found in {path}")

    build = _body(ROOT / "tools" / "_build" / "clusters.py")
    lint = _body(ROOT / "tools" / "_lint" / "overview.py")
    assert build == lint, "_skeleton_overview drifted between the builder and the lint SoT"


def test_demotion_excludes_prose_embedded_hub(tmp_path):
    """measurement-root regression — a hub embedded only in overview/synthesis/timeline/trail
    must be treated as nav-inbound and excluded from demotion candidates even when it rides on no graph edge.

    Previously (2026-06): the graph build did not emit prose-layer origin edges, so a hub embedded
    only in an overview (Appier, Similarweb, etc.) never saw its nav in the demotion lint and
    recurred as a false-strong demotion candidate every sweep. Fixed by scanning `_prose_nav_stems` directly.
    """
    import hub_demotion

    d = tmp_path / "entities"
    d.mkdir()
    hub = d / "테스트오펀.md"
    hub.write_text(
        '---\ntitle: "테스트오펀"\ntype: entity\nkind: org\n'
        "sources: [single-src]\n---\n## Overview\n짧은 본문.\n",
        encoding="utf-8",
    )
    empty_graph = {"inbound": {}, "cluster": {}}

    # no prose embed → detected as an isolated demotion candidate (strong)
    iss, _ = hub_demotion._check_directory(d, "entities", empty_graph, set(), set())
    assert any("테스트오펀" in i for i in iss)

    # the same hub embedded in the prose layer → excluded as nav-inbound (0 omissions)
    iss2, _ = hub_demotion._check_directory(
        d, "entities", empty_graph, set(), {"테스트오펀"}
    )
    assert not any("테스트오펀" in i for i in iss2)


def test_meta_lint_regex_hoisting_check_active():
    """F4 regression — the shared-regex redefinition detection check is alive in the meta lint,
    and there is currently no redefinition in tools/."""
    proc = subprocess.run(
        [sys.executable, "tools/lint.py", "meta"],
        capture_output=True, text=True, encoding="utf-8", cwd=ROOT, timeout=300,
    )
    assert proc.returncode in (0, 1)  # 1 = clone-environment artifacts (.claude/memory/, etc.) allowed
    assert "OK - shared FRONTMATTER*/WIKILINK*/AUTO* regexes defined only in _lib" in proc.stdout


def test_overview_sources_total_matches_catalog_membership():
    """Reground regression — the overview AUTO:SOURCES "N total" and the source
    catalog must apply ONE membership rule.

    Previously `_group_sources_by_cluster` fell back to the primary cluster for a
    source below threshold in every cluster, while `_render_sources_block` counted
    only `weight >= threshold` — so an orphan source appeared in the catalog but
    was missing from the overview total. Both numbers are generated, so no author
    could reconcile them by editing a page; the fix belongs to the build. This
    pins the two rules together, because a membership rule duplicated across two
    functions diverges again (copyeditor.md § Risk Mitigation Design)."""
    from _build import clusters as C

    clusters_data = {
        "source_weight_threshold": 0.3,
        "clusters": [{"slug": "c1", "name": "Cluster One"},
                     {"slug": "c2", "name": "Cluster Two"}],
        "source_assignments": {
            "sources/strong.md": {"primary": "c1", "weights": {"c1": 0.9, "c2": 0.4}},
            # below threshold everywhere → catalog falls back to its primary (c1)
            "sources/orphan.md": {"primary": "c1", "weights": {"c1": 0.2, "c2": 0.1}},
        },
    }
    sources = [
        ("Strong", "sources/strong.md", "", "", "2026-01-01", ""),
        ("Orphan", "sources/orphan.md", "", "", "2026-01-02", ""),
    ]

    cluster_files, _ = C._group_sources_by_cluster(sources, clusters_data)
    for cluster in clusters_data["clusters"]:
        slug = cluster["slug"]
        m = re.search(r"(\d+) total", C._render_sources_block(cluster, clusters_data))
        assert m, f"cluster {slug}: rendered block has no total"
        assert int(m.group(1)) == len(cluster_files.get(slug, [])), (
            f"cluster {slug}: overview total {m.group(1)} != "
            f"catalog membership {len(cluster_files.get(slug, []))}"
        )

    # The orphan is exactly what the divergence used to hide.
    assert len(cluster_files["c1"]) == 2


def test_f2_claim_stat_checked_at_every_occurrence(tmp_path, monkeypatch):
    """Reground regression — a stale restatement of the canonical claim total
    mid-body must fail F2, not only a stale head sentence.

    A delta-only re-ground edits the head and leaves earlier copies behind; the
    previous head-only `.search()` passed such a document."""
    import contradiction as CT

    md = tmp_path / "contradiction.md"

    def _write(head_n, body_n):
        md.write_text(
            f"# Contradictions\n\n"
            f"**{head_n} source-to-source contradictions** across the corpus.\n\n"
            f"## Synopsis\n\n"
            f"Restated later: **{body_n} source-to-source contradictions**.\n",
            encoding="utf-8",
        )

    monkeypatch.setattr(CT, "CONTRADICTIONS_MD_PATH", md)

    # Assert on the claim-stat drift specifically: this fixture is a minimal
    # document, so unrelated criteria (S1 sections, the theme stat) fail anyway.
    _write(7, 7)  # every occurrence agrees with the SoT
    issues, _ = CT._check_contradictions_md(set(), set(), 7, 0)
    assert not any("claims declared" in i for i in issues), issues

    _write(7, 5)  # head correct, mid-body stale — the case head-only checking missed
    issues, _ = CT._check_contradictions_md(set(), set(), 7, 0)
    assert any("claims declared=5 actual=7" in i for i in issues), issues


def test_reground_status_surfaces_superseded_but_open_claims():
    """Reground follow-up trigger — a claim whose own source reports the dispute
    settled (`type: superseded`) while it stays `status: open` is surfaced; every
    other type/status combination stays silent (the surface must be zero-FP)."""
    import contradiction as CT

    assert CT._reground_status_line([]) is None
    assert CT._reground_status_line([{"id": "a", "type": "soft", "status": "open"}]) is None
    assert CT._reground_status_line(
        [{"id": "b", "type": "superseded", "status": "resolved"}]
    ) is None

    line = CT._reground_status_line([
        {"id": "c1", "type": "superseded", "status": "open"},
        {"id": "c2", "type": "real", "status": "open"},
    ])
    assert line is not None
    assert "1 superseded claim(s) still open" in line
    assert "c1" in line and "c2" not in line


def test_valid_link_target_set_has_one_owner(monkeypatch):
    """The "valid wikilink target" set was implemented three times (graph
    structure · link_candidates · the write-time hook). When only one copy
    changed, one check called a link broken and another did not.

    A fake stem is injected rather than asserting the import binding — a test
    that only checks `module.helper is _lib.helper` still passes after someone
    re-inlines the glob at the call site, which is the recurrence this guards.
    """
    import link_candidates
    from pathlib import Path as _P

    sentinel = {"__ONLY_FROM_THE_SHARED_HELPER__": _P("x.md")}
    monkeypatch.setattr(link_candidates, "wiki_page_paths", lambda: sentinel)
    assert link_candidates._index_pages() == sentinel


def test_r1_english_token_boundary():
    """R1 counts a numeric token only where the body actually says it.

    The word units are closed by `\\b`, but `%` was not: the phrase `50%+1 rule`
    yielded a bare `50%` token, so one phrase repeated three times read as a hot
    figure. A percentage followed by a digit or `+` is part of a longer token,
    not a standalone figure.
    """
    from _lint.overview import _r1_hot_tokens

    def toks(t):
        return dict(_r1_hot_tokens(t))

    assert toks("The 50%+1 rule. Under the 50%+1 rule. Debating the 50%+1 rule.") == {}
    # genuine repetition still counts — trailing punctuation and prose both
    assert toks("Share of 94%. About 94% now. Reaching 94%.") == {"94%": 3}
    assert toks("7 billion params. 7 billion again. 7 billion more.") == {"7 billion": 3}


def test_r1_korean_token_boundary(monkeypatch):
    """The same boundary rule under WIKI_LANG=ko — a counter that swallows the
    following syllable invents tokens: `2분기`→`2분`, `2조 4,585억`→`2조`,
    `5대 시중은행`→`5대`. Particles (`94%에`) must still count, so the block is
    scoped to the counter, not to any trailing Hangul.
    """
    import _lint.overview as O

    monkeypatch.setattr(O, "korean_mode", lambda: True)

    def toks(t):
        return dict(O._r1_hot_tokens(t))

    assert toks("2분기 실적. 2분기 매출. 2분기 이익.") == {}
    assert toks("2조 4,585억 원. 2조 2,254억 원. 2조 6,381억 원.") == {}
    assert toks("50%+1 룰이다. 50%+1 룰 적용. 50%+1 룰 논의.") == {}
    assert toks("점유율 94%. 94% 수준. 94%에 달한다.") == {"94%": 3}
    assert toks("9시간 55분. 55분 중단. 55분 지연.") == {"55분": 3}


def _cit_checks():
    """Load the scholarly-citation skill detectors the same way source.py does."""
    import importlib.util

    path = ROOT / ".claude" / "skills" / "scholarly-citation" / "checks.py"
    spec = importlib.util.spec_from_file_location("cit_checks_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_g2_weasel_boundary_keeps_named_claimants():
    """G2 recalibration regression — a denylist without a case boundary drops the very
    names the guideline offers as correct examples (`Free Software Foundation` ends in
    `foundation`). In English the discriminator is the final word's case: a named source
    capitalizes it, a weasel does not.
    """
    w = _cit_checks()._is_weasel_head

    for named in (
        "Free Software Foundation", "Software Freedom Conservancy",
        "Open Source Initiative", "Government Accountability Office",
        "Electronic Frontier Foundation", "The Linux Foundation",
        "AMD", "Ai2", "Pleias", "Bradley Kuhn",
    ):
        assert not w(named), f"named claimant dropped as weasel: {named!r}"

    for weasel in (
        "the government", "the industry", "the foundation", "the community",
        "industry sources", "Government sources", "experts", "the media", "",
    ):
        assert w(weasel), f"weasel let through: {weasel!r}"


def test_g2_accepts_plain_name_rejects_evasion_and_bloat():
    """G2 measures whether the claimant is *named*, not whether it is linked (WP:ASF).
    Plain text passes when the speaker has no page; it fails when a page does exist
    (link evasion) or when content is pushed into the head slot.
    """
    cit = _cit_checks()
    page_index = {"Meta": ("entities/Meta.md", "entity")}

    def g2(line):
        body = f"## Key Claims\n{line}\n\n## Connections\n"
        return cit.evaluate_citation(
            body, page_index=page_index, section_titles_fn=lambda rel: set()
        )["g2"]

    # plain-text name, no page → PASS and counted as plain
    ok = g2("- [fact] Pleias — released a fully open multilingual dataset")
    assert ok[0] is True and ok[4] == 1

    # wikilink → PASS, not counted as plain
    linked = g2("- [fact] [[Meta]] — released Llama under a custom licence")
    assert linked[0] is True and linked[4] == 0

    # plain text naming an existing page → link evasion → FAIL
    assert g2("- [fact] Meta — released Llama under a custom licence")[0] is False

    # content pushed into the head slot → FAIL
    bloat = "x" * (cit.CLAIMANT_HEAD_MAX + 1)
    assert g2(f"- [fact] {bloat} — said something")[0] is False

    # anonymous subject → FAIL even in plain text
    assert g2("- [fact] the industry — expects consolidation")[0] is False


def test_a2_exempts_plain_speaker_and_fails_broken_link():
    """A2 judges whether a speaker is named and whether a link resolves — not whether
    a link is present. A plain-text speaker leaves the denominator (the page may be
    below the creation threshold); a link to a missing page fails.
    """
    cit = _cit_checks()
    page_index = {"Mozilla": ("entities/Mozilla.md", "entity")}

    def a2(quote):
        body = f"## Key Quotes\n{quote}\n\n## Connections\n"
        return cit.evaluate_citation(
            body, page_index=page_index, section_titles_fn=lambda rel: set()
        )["a2"]

    # (pass, linked-and-valid, judged) per input class. Every class below was surfaced by
    # review of this check; the separator rule (the first spaced dash between an
    # even-indexed quote mark and the next mark) is the only one of five candidates that
    # gets all of them right — the four it replaces are enumerated in checks.py.
    cases = [
        # linked speaker, plain speaker, and the two failure modes
        ('> "q" — [[Mozilla]]', (True, 1, 1)),
        ('> "q" — Bruce Perens, OSI co-founder', (True, 0, 0)),
        ('> "q" — [[Perens]]', (False, 0, 1)),          # broken link (pre-fix: passed)
        ('> "q" — Mozilla', (False, 0, 1)),             # evasion, as G2 reads the claimant slot
        # nobody named — none of these may exempt themselves
        ('> "an unattributed line"', (False, 0, 1)),
        ('> "an unattributed line" — ', (False, 0, 1)),
        ('> "the OSD — 26 years old — applies"', (False, 0, 1)),
        ('> "they call it "open source" — a stretch — at best"', (False, 0, 1)),
        ('> "q text here" 2024-10-28', (False, 0, 1)),  # unspaced hyphen is not a separator
        ('> "q text here" (op-ed)', (False, 0, 1)),
        ('> "q text unclosed — [[Mozilla]]', (False, 0, 1)),
        # a link inside the quotation body is never the speaker
        ('> "the OSD — 26 years — applies to [[Mozilla]]" — Perens, co-founder', (True, 0, 0)),
        ('> "— the OSD applies to [[Mozilla]]" — Perens, co-founder', (True, 0, 0)),
        # …nor may it launder a broken speaker link, or a trailing segment
        ('> "they call it "open source" — for [[Mozilla]]" — [[Perens]]', (False, 0, 1)),
        ('> "q" — [[Perens]] — via [[Mozilla]]', (False, 0, 1)),
        ('> "q" — [[Mozilla]] — 2024-10-28', (True, 1, 1)),
        # forms that must stay judged: anchor, alias, en dash, hyphen, nested body term
        ('> "q" — [[Mozilla#Key Quotes]]', (True, 1, 1)),
        ('> "q" — [[Mozilla|the Mozilla Foundation]]', (True, 1, 1)),
        ('> "q" – [[Mozilla]]', (True, 1, 1)),
        ('> "q" - [[Mozilla]]', (True, 1, 1)),
        ('> "q about "openness" here" — [[Mozilla]]', (True, 1, 1)),
        # a quoted work title inside the attribution does not swallow it
        ('> "q" — [[Mozilla]], author of "The OSD"', (True, 1, 1)),
        ('> "q" — Perens, author of "The OSD"', (True, 0, 0)),
        # text between the closing mark and the separator is not "naming nobody"
        ('> "q" (emphasis added) — [[Mozilla]]', (True, 1, 1)),
        ('> "q," she said — Perens, co-founder', (True, 0, 0)),
    ]
    for quote, expected in cases:
        assert a2(quote) == expected, quote

    # several quotes in one section are scored per line: of the first four classes,
    # three are judged (linked·broken·evasion) and one is exempt (plain speaker)
    assert a2("\n".join(q for q, _ in cases[:4])) == (False, 1, 3)


def test_link_display_text_is_not_an_unlinked_mention():
    """`--fix` wrote bogus `[[Target]]` reconnect lines because the mention scan ran
    against raw file text, so a term appearing only inside another link's display
    text counted as an unlinked mention. It cannot be one — a substring of an
    existing link is not linkable."""
    import structure

    h = structure._mention_haystack
    # Display text is dropped; the target survives (a bare `[[hub]]` must still
    # reconnect, which is the whole reason the target is kept rather than removed).
    assert not re.search(r"\bMETR\b", h("see [[Study|the METR productivity claim]]"))
    assert re.search(r"\bMETR\b", h("see [[METR]] on this"))
    assert re.search(r"\bMETR\b", h("see [[METR|the study]]"))
    # An anchor is consumed like an alias.
    assert re.search(r"\bMETR\b", h("see [[METR#Findings]]"))
    # Padding: without it the target fuses with the following character and the
    # word-boundary search that reconnect relies on finds no boundary.
    assert re.search(r"\bMETR\b", h("[[METR|the study]]s showed"))
    # A genuine plain-text mention is untouched.
    assert re.search(r"\bMETR\b", h("METR published a report"))
