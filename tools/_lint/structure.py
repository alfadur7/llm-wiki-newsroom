"""Structural wiki checks: broken links, orphan hubs, missing entities, Korean-naming.

Scope of valid link targets (Obsidian resolves by filename globally):
  - Subdirectory pages: entities/, concepts/, syntheses/, trails/, timelines/, sources/, overviews/, contradictions/
  - Root meta pages: wiki/*.md (overview, index, contradictions)

Root pages are excluded from the orphan check (they are top-level navigation, not hubs).
log.md and lint-report.md live at the repo root, so they are neither scanned
nor valid wikilink targets here.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import WIKI, MARKUP_LEAK_RE, parse_frontmatter, read_text_cached, real_source_files, strip_code  # noqa: E402

LINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$")

ENGLISH_STANDARD = {
    "openai", "anthropic", "microsoft", "google", "aws", "meta", "tesla",
    "ibm", "nvidia", "apple", "amazon", "salesforce", "sap", "oracle",
    "databricks", "mongodb", "redhat", "vmware", "broadcom", "hashicorp",
    "cohesity", "cnapp", "cncf", "rag", "llm", "gpu", "a2a",
    "deepseek", "circle", "idc", "jpmorgan", "lambdalabs",
    "openstack", "kubernetes", "amazoneks", "amazonaurora",
    "amazonq", "amazonbedrock", "azure", "copilot", "container",
    "mainframe", "api", "csp", "msp", "poc", "gpt", "vm",
    "kaist", "postech", "lgcns", "nhn", "skcc", "skax", "exaone",
    "githubcopilot",
    # Global banks / financial firms (English standard)
    "dxc", "ing", "bbva", "lseg", "hsbc", "natwest", "citi", "dbs",
    "itauunibanco", "bradesco",
    # Global IT English brands / open source
    "thoughtmachine", "mistral", "docker", "nutanix", "paloalto",
    "citrix", "devin", "avalabs", "kubevirt", "edb",
    "huggingface", "gemini", "cursor", "kiro", "purestorage",
    "intel", "amd", "arm",
    "satyanadella", "jensenhuang", "darioamodei", "jamiedimon",
    "markbenioff", "markzuckerberg", "charleslamanna", "sanjaypoonen",
    "christiankleinerman", "fidelmarusso", "andrejkarpathy",
    "danielaamodei", "larryellison", "mattgarman",
    # Entities whose English abbreviation is the Korean/global standard (an English filename is fine even with Korean body text)
    "kisa", "nist", "lh", "idcresearch", "dell", "solanafoundation",
    "hitachivantara", "pxd", "vibraniumlabs", "caisi", "xai",
    "mythos", "openbsd", "kt", "claudellm", "snowflake",
}


def _extract_headings(text: str) -> set[str]:
    """Return the set of heading texts (H1-H6) in the page, ignoring code blocks."""
    headings: set[str] = set()
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING_RE.match(line)
        if m:
            headings.add(m.group(1).strip())
    return headings


def _extract_title_alias(hub_path: Path) -> str | None:
    """Pull a Korean alias term from the hub's frontmatter `title`.

    Used as a secondary match term when the hub's filename (stem) is Latin
    but the Korean body of sources references the entity by its Hangul
    name. Example: `entities/Citrix.md` with `title: "시트릭스"` lets the
    orphan-hub reconnect catch sources mentioning "시트릭스" in plain
    Korean prose.

    Cleanup rules:
      - Strip parenthetical annotations: "시트릭스(Citrix)" → "시트릭스"
      - Strip quotes
      - Return None if empty after cleanup, or identical to the stem,
        or shorter than 2 chars
      - Return None when the alias is purely Latin (stem already covers it)
    """
    try:
        head = read_text_cached(hub_path)[:400]
    except OSError:
        return None
    m = re.search(r'^title:\s*"?([^"\n]+?)"?\s*$', head, re.MULTILINE)
    if not m:
        return None
    title = m.group(1).strip()
    # Remove parenthetical content (Latin/Korean both handled).
    title = re.sub(r"\s*[\(（][^\)）]*[\)）]\s*", " ", title).strip()
    if not title or len(title) < 2:
        return None
    if title == hub_path.stem:
        return None
    # Only useful when the alias contains Hangul — Latin aliases are
    # already reachable via the stem match.
    if not re.search(r"[가-힣]", title):
        return None
    return title


def _reconnect_orphan_hubs(orphan_stems: list[str], fix: bool) -> dict[str, list[str]]:
    """Match each orphan hub's stem (and optional Korean title alias)
    against raw text in `wiki/sources/*.md` and (in --fix mode) append
    `[[<hub>]]` or `[[<hub>|<alias>]]` to each hit source's `## Connections`
    section. Returns {hub: [source_stem, ...]} — matched sources per hub.

    Match rules:
      - Hub stem with Latin letters: word-boundary regex (`\\b{stem}\\b`)
      - Hub stem with Hangul / other: plain substring
      - Hangul stems allowed at length ≥2 (covers "안랩"-style names);
        Latin stems stay at ≥3 to avoid catching generic acronyms
      - Hangul title alias (from frontmatter) is tried as a secondary
        match term when the stem is Latin-only. Inserted wikilink uses
        the alias form (`[[<stem>|<alias>]]`) for readability.
      - Sources where `[[<hub>]]` or `[[<hub>|` already appears are skipped

    Insertion: appended to the end of the existing `## Connections` block (before
    the next H2). If no `## Connections` section exists, one is created at the end
    of the file.
    """
    results: dict[str, list[str]] = {}
    src_dir = WIKI / "sources"
    if not src_dir.exists():
        return results

    source_files: dict[str, Path] = {p.stem: p for p in real_source_files()}

    # Cache source contents so we don't re-read per hub.
    src_cache: dict[str, str] = {
        stem: read_text_cached(path)
        for stem, path in source_files.items()
    }

    # Pre-resolve each hub's Path so we can read its title for aliases.
    hub_paths: dict[str, Path] = {}
    for sub in ("entities", "concepts"):
        d = WIKI / sub
        if not d.exists():
            continue
        for p in d.glob("*.md"):
            if p.name.startswith("_"):
                continue
            hub_paths[p.stem] = p

    for hub_stem in orphan_stems:
        has_hangul = bool(re.search(r"[가-힣]", hub_stem))
        has_latin = bool(re.search(r"[a-zA-Z]", hub_stem))
        # Ambiguity guard: Korean 2-char names (e.g. 안랩·KT계열) are common
        # organization tokens, so allow length ≥2 when Hangul is present.
        # Latin stems stay at ≥3 to avoid catching acronyms like "SK"/"AI".
        min_len = 2 if has_hangul else 3
        if len(hub_stem) < min_len:
            continue

        # Build the ordered match-term list. The stem is always first;
        # a Hangul title alias is appended when the stem itself is
        # Latin-only (so we can catch Korean prose mentions).
        alias: str | None = None
        if not has_hangul:
            hub_path = hub_paths.get(hub_stem)
            if hub_path:
                alias = _extract_title_alias(hub_path)

        # (term, is_alias) tuples — is_alias flag decides the wikilink
        # form that gets appended to `## Connections`.
        match_terms: list[tuple[str, bool]] = [(hub_stem, False)]
        if alias:
            match_terms.append((alias, True))

        # For each source, record the first term that matches. Skip only
        # when `[[<hub>]]` is already present inside the `## Connections` section
        # — elsewhere-linked cases must still be re-added there so the
        # downstream orphans --fix step can populate the hub's `sources:`
        # frontmatter. (orphans --fix only scans `## Connections`.)
        conn_re = re.compile(r"^## Connections\n(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)
        hits: list[tuple[str, bool]] = []  # (src_stem, use_alias_form)
        for src_stem, content in src_cache.items():
            conn_match = conn_re.search(content)
            conn_section = conn_match.group(1) if conn_match else ""
            # Skip if the hub is already referenced in any of the canonical
            # wikilink forms: bare `[[hub]]`, aliased `[[hub|alias]]`, or
            # anchor-suffixed `[[hub#섹션]]` (the anchor case was previously
            # missed and caused duplicate reconnection).
            if (
                f"[[{hub_stem}]]" in conn_section
                or f"[[{hub_stem}|" in conn_section
                or f"[[{hub_stem}#" in conn_section
            ):
                continue
            matched_alias = None
            for term, is_alias in match_terms:
                term_has_latin = bool(re.search(r"[a-zA-Z]", term))
                term_re = (
                    re.compile(r"\b" + re.escape(term) + r"\b")
                    if term_has_latin
                    else re.compile(re.escape(term))
                )
                if term_re.search(content):
                    matched_alias = is_alias
                    break
            if matched_alias is None:
                continue
            hits.append((src_stem, matched_alias))

        if not hits:
            continue
        results[hub_stem] = sorted(s for s, _ in hits)

        if not fix:
            continue

        for src_stem, use_alias in hits:
            link_text = (
                f"[[{hub_stem}|{alias}]]" if (use_alias and alias) else f"[[{hub_stem}]]"
            )
            new_line = f"- references: {link_text} — auto-linked based on body mention"
            content = src_cache[src_stem]
            conn_match = re.search(r"(^## Connections\s*\n)", content, re.MULTILINE)
            if conn_match:
                start = conn_match.end()
                next_h2 = re.search(r"^## ", content[start:], re.MULTILINE)
                section_end = start + (next_h2.start() if next_h2 else len(content) - start)
                section = content[start:section_end]
                new_section = section.rstrip() + f"\n{new_line}\n\n"
                new_content = content[:start] + new_section + content[section_end:]
            else:
                # No `## Connections` section — append at end of file.
                insertion = f"\n## Connections\n{new_line}\n\n"
                new_content = content.rstrip() + "\n" + insertion
            source_files[src_stem].write_text(new_content, encoding="utf-8")
            src_cache[src_stem] = new_content

    return results


def run(fix: bool = False) -> int:
    all_pages: dict[str, Path] = {}

    for p in WIKI.glob("*.md"):
        if p.name.startswith("_"):
            continue
        all_pages[p.stem] = p

    for subdir in ("entities", "concepts", "syntheses", "trails", "timelines", "sources", "overviews", "contradictions"):
        d = WIKI / subdir
        if not d.exists():
            continue
        for p in d.glob("*.md"):
            if p.name.startswith("_"):
                continue
            all_pages[p.stem] = p

    hubs: set[str] = set()
    for sub in ("entities", "concepts"):
        for p in (WIKI / sub).glob("*.md"):
            if not p.name.startswith("_"):
                hubs.add(p.stem)

    # Source page stems — the missing-entity-candidate tally counts *distinct
    # sources* per naming.md ("≥3 distinct source"), so only links originating
    # in wiki/sources/ pages count. A target linked by 3 concepts but 0 sources
    # is hub↔hub navigation, not a source-grounding signal.
    source_stems: set[str] = {p.stem for p in real_source_files()}

    forward: dict[str, set[str]] = defaultdict(set)
    broken: dict[str, list[str]] = defaultdict(list)
    broken_anchors: dict[str, list[str]] = defaultdict(list)
    markup_leaks: dict[str, list[str]] = defaultdict(list)
    headings_cache: dict[str, set[str]] = {}

    # log.md moved to the repo root (outside the walked vault), so its append-only
    # history — which inevitably references renamed/removed slugs — is no longer
    # scanned and can no longer produce perma-broken-link false positives.
    for stem, path in all_pages.items():
        raw = read_text_cached(path)
        text = strip_code(raw)
        for leak in MARKUP_LEAK_RE.findall(text):
            markup_leaks[path.relative_to(WIKI).as_posix()].append(leak)
        for m in LINK_RE.findall(text):
            target = m.strip()
            # Obsidian section anchors: [[Page#Heading]] — split into page + anchor parts.
            # Trailing "\" can leak in when authors escape the pipe (\|) for table rows.
            page_part, _, anchor_part = target.partition("#")
            page_part = page_part.rstrip("\\").strip()
            anchor_part = anchor_part.rstrip("\\").strip()
            forward[stem].add(page_part)
            if page_part and page_part not in all_pages:
                broken[f"{path.relative_to(WIKI).as_posix()}"].append(target)
                continue
            if anchor_part and page_part in all_pages:
                if page_part not in headings_cache:
                    tgt_text = read_text_cached(all_pages[page_part])
                    headings_cache[page_part] = _extract_headings(tgt_text)
                if anchor_part not in headings_cache[page_part]:
                    rel = path.relative_to(WIKI).as_posix()
                    broken_anchors[rel].append(f"{page_part}#{anchor_part}")

    bl_path = WIKI / "_backlinks.json"
    backlinks = json.loads(bl_path.read_text(encoding="utf-8")) if bl_path.exists() else {}

    orphans: list[str] = []
    source_only_orphans: list[tuple[str, int]] = []  # hub-in only, source-in zero
    for stem in hubs:
        refs = backlinks.get(stem, [])
        if not refs:
            orphans.append(stem)
            continue
        # source-only inbound check: hub has hub-to-hub inbound but 0 source inbound.
        # Signals coverage gap — a concept/entity referenced only by other concepts but
        # never grounded in a primary source. M9 from review report 2026-05-07.
        src_in = sum(1 for r in refs if isinstance(r, dict) and r.get("from", "").startswith("sources/"))
        if src_in == 0:
            source_only_orphans.append((stem, len(refs)))

    # mention_count[target] = number of distinct source pages (forward[page] is a
    # set, so multiple citations within a single page dedup to 1). Aligns with the
    # policy `naming.md` threshold "≥3 distinct source" — multiple citations within
    # a single source are just a narrative-anchor signal, not a hub threshold.
    source_count: Counter = Counter()
    for stem, targets in forward.items():
        if stem not in source_stems:
            continue
        for t in targets:
            if t not in all_pages:
                source_count[t] += 1
    missing = [(n, c) for n, c in source_count.items() if c >= 3]
    missing.sort(key=lambda x: -x[1])

    korean_suspect: list[tuple[str, int]] = []
    entity_stems = {p.stem for p in (WIKI / "entities").glob("*.md") if not p.name.startswith("_")}
    for stem in entity_stems:
        if re.search(r"[가-힣]", stem):
            continue
        p = all_pages[stem]
        text = read_text_cached(p)
        kor_signals = len(re.findall(r"한국|서울|은행|공사|청|그룹|보험", text))
        if kor_signals >= 3 and stem.lower() not in ENGLISH_STANDARD:
            korean_suspect.append((stem, kor_signals))

    print("=== LINT RESULTS ===")
    print(f"Total pages (scan scope): {len(all_pages)}")
    print(f"  root meta: {sum(1 for p in all_pages.values() if p.parent == WIKI)}")
    print(f"  subdirectory: {sum(1 for p in all_pages.values() if p.parent != WIKI)}")
    print(f"Broken links: {sum(len(v) for v in broken.values())} across {len(broken)} files")
    for f, ts in broken.items():
        print(f"  {f}: {ts[:5]}")
    total_bad_anchors = sum(len(v) for v in broken_anchors.values())
    print(f"Broken anchors: {total_bad_anchors} across {len(broken_anchors)} files")
    for f, ts in broken_anchors.items():
        print(f"  {f}: {ts[:5]}")
    total_markup = sum(len(v) for v in markup_leaks.values())
    print(f"Tool-call markup leaks: {total_markup} across {len(markup_leaks)} files")
    for f, ts in markup_leaks.items():
        print(f"  {f}: {ts[:5]}")
    print(f"Orphan hubs (entities/concepts): {len(orphans)}")
    for o in sorted(orphans)[:15]:
        print(f"  {o}")
    print(f"Source-only orphan hubs (hub-in>0, source-in=0): {len(source_only_orphans)}")
    for stem, hub_in in sorted(source_only_orphans, key=lambda x: -x[1])[:15]:
        print(f"  {stem} (hub-in={hub_in})")

    # Hub auto-reconnect: orphans (no backlinks) PLUS hubs whose
    # `sources:` frontmatter is empty even if backlinks exist. The second
    # set catches hubs referenced only via hub↔hub wikilinks but never
    # tied to a source — common for concept stubs (API / MSP / PoC etc.).
    # Both sets share the same reconnect logic (raw-text match + append
    # to `## Connections`; subsequent orphans --fix populates hub `sources:`).
    sources_empty: list[str] = []
    for sub in ("entities", "concepts"):
        d = WIKI / sub
        if not d.exists():
            continue
        for p in d.glob("*.md"):
            if p.name.startswith("_"):
                continue
            fm = parse_frontmatter(read_text_cached(p))
            if not fm.get("sources"):
                sources_empty.append(p.stem)

    reconnect_targets = sorted(set(orphans) | set(sources_empty))
    if reconnect_targets:
        reconnect = _reconnect_orphan_hubs(reconnect_targets, fix)
        if fix and reconnect:
            total_edits = sum(len(v) for v in reconnect.values())
            print(
                f"\n  [--fix] hubs auto-reconnected: "
                f"{len(reconnect)}/{len(reconnect_targets)} candidates "
                f"(orphans:{len(orphans)} + sources-empty:{len(sources_empty)}), "
                f"{total_edits} source edits"
            )
            for hub, hits in reconnect.items():
                print(f"    {hub}: +{len(hits)} source(s)")
            print("    Run `python tools/lint.py graph orphans --fix` next to update hub `sources:`.")
        elif reconnect and not fix:
            print(
                f"\n  [--fix candidates] {len(reconnect)}/{len(reconnect_targets)} hubs "
                f"(orphans + sources-empty) have source raw-text hits:"
            )
            for hub, hits in reconnect.items():
                print(f"    {hub}: {len(hits)} source(s)")
    print(f"Missing entity candidates (≥3 distinct sources): {len(missing)}")
    for n, c in missing[:15]:
        print(f"  {n} ({c} sources)")
    print(f"Korean entity w/ English filename suspects: {len(korean_suspect)}")
    for stem, signals in korean_suspect[:15]:
        print(f"  {stem} (kor-signals={signals})")

    issues = (sum(len(v) for v in broken.values()) + total_bad_anchors + total_markup
              + len(orphans) + len(missing) + len(korean_suspect))
    return 1 if issues else 0
