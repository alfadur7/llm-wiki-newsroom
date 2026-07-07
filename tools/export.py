"""Export wiki to merged files for Claude.ai Project Knowledge.

Produces `wiki-export/` with three categories of files:

  Root meta copies
    overview.md, contradiction.md, index.md — one-to-one copies from wiki/.

  Sub-folder merges
    all-overviews.md, all-contradictions.md, all-concepts.md, all-entities.md,
    all-timelines.md, all-syntheses.md, all-trails.md — each merges every
    regular page in the matching sub-folder (underscore-prefixed files skipped).

  Source locator index (hub-centric RAG)
    all-sources-index.md — a single file listing every source as one line
    (slug + title + date + summary snippet), grouped by primary cluster from
    graph/_clusters.json. Source *bodies* are not exported: the hosted graph
    browser already carries every source as a full-text node (graph/_pages.json,
    reachable via #q=<slug>), and every source is referenced by ≥1 hub's
    frontmatter `sources:` list (0 orphans). So the RAG corpus holds the
    synthesized hubs plus this locator, and Claude.ai deep-links source originals
    into the graph by slug. Two-tier model: RAG = synthesis, graph = evidence.

Run: `python tools/export.py`.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import BASE_URL, GRAPH, REPO_ROOT, STANDALONE_SLUG, WIKI, deeplink_key, graph_deeplink_base, korean_mode, parse_page_meta  # noqa: E402
from _export.site import stage_site  # noqa: E402

OUT = REPO_ROOT / 'wiki-export'
CLUSTERS_JSON = GRAPH / '_clusters.json'

ROOT_META = ['overview.md', 'contradiction.md', 'index.md']

# entities·concepts hub bodies are deliberately NOT merged for RAG. Their full
# text is already a graph node (graph/_pages.json, reachable via #q=), and the
# two files alone are ~1.24M tokens — far past Claude.ai's project context. The
# directory of every entity·concept (one-line desc + deep-link) lives in
# index.md, and detail is reached by deep-linking into the graph. So the export
# carries only the synthesis + directory layer.
FOLDER_MERGES = [
    ('overviews', 'all-overviews.md'),
    ('contradictions', 'all-contradictions.md'),
    ('timelines', 'all-timelines.md'),
    ('syntheses', 'all-syntheses.md'),
    ('trails', 'all-trails.md'),
]


def _deeplink_protocol() -> str:
    """Canonical graph deep-link protocol shared by the in-file handoff block and
    wiki-export/README.md, so the two channels never drift. Covers BOTH hub and
    source links: hubs are deep-linked for original-page verification (connections,
    backlinks, full body), sources for primary-evidence drill-down. Empty when
    BASE_URL is unset."""
    if not BASE_URL:
        return ''
    # Use the extension-less form (/slug) — Cloudflare Pages 308-redirects
    # /slug.html to /slug, and on mobile in-app web views a redirect risks
    # dropping the #q= fragment, which we want to avoid.
    link = graph_deeplink_base()
    return (
        'Every entity, concept, and source is a node in the graph browser, and '
        f'the address `{link}#q=<key>` opens that node directly (`<key>` is used '
        'verbatim, without URL encoding — non-Latin titles too). The RAG corpus holds '
        'only the synthesis layer (overview, synthesis, etc.) and the directory '
        '(index); the detailed bodies of entities, concepts, and sources live in '
        'the graph. When answering, follow these rules:\n'
        '\n'
        '1. Build the answer body from the synthesis layer and `index` — entity, '
        'concept, and source detail is not in the RAG corpus; it is in the graph.\n'
        f'2. Add a deep-link for every entity/concept you cite: `[<title>]({link}#q=<title>)`. '
        '`<title>` is the entity/concept title (e.g. `Meta`, `AgenticAI`). '
        'This lets the reader verify the page\'s full body, connections, and '
        'backlinks in the graph.\n'
        f'3. When pointing to the primary source of a specific claim, add a source deep-link: `[View original]({link}#q=<source-slug>)`. '
        'Find `<source-slug>` in `all-sources-index.md` or in the wikilinks of the '
        'synthesis body (e.g. `osi-open-source-ai-definition`).\n'
        '4. **The `[[title]]` / `[[slug|alias]]` wikilinks inside the synthesis body '
        'are themselves the deep-link targets.** The target inside the brackets '
        '(`title` or `slug`) is exactly the `#q=` key, so no separate lookup is '
        'needed — if a cited sentence came from such a wikilink reference, deep-link '
        'to that target (e.g. body text `[[osi-open-source-ai-definition|OSI definition]]` → '
        f'`[OSI definition]({link}#q=osi-open-source-ai-definition)`). Do not '
        'put the raw wikilink notation `[[...]]` in the answer; convert it to this '
        'deep-link.\n'
        '\n'
        'Add at least one deep-link to every key claim. Body = synthesis, links = '
        'verify detail and originals in the graph.'
    )


# The deep-link protocol is no longer prepended per-file. It lives in
# wiki-export/README.md (the operator pastes it into the Claude.ai Project
# custom-instructions field — always in context), so a per-file blockquote
# fallback would just be ~9K tokens of 11× redundancy in a budget-bound corpus.


# Folders whose pages are graph nodes (resolvable by stem via #q=). Timelines are
# excluded — they are not emitted as graph nodes.
_NODE_FOLDERS = {
    'sources', 'entities', 'concepts', 'overviews', 'contradictions',
    'syntheses', 'trails',
}
_MD_LINK_RE = re.compile(r'\[([^\]]*)\]\(([^)]+?\.md)(#[^)]*)?\)')


def _rewrite_links(text: str) -> str:
    """Rewrite repo-relative `.md` markdown links for the RAG export.

    Individual pages are not exported as files (hubs are merged; sources are
    replaced by an index), so a `(entities/X.md)` link is dead in Project
    Knowledge. Convert links whose target is a graph node to a clickable graph
    deep-link (`#q=<stem>`); drop the rest to plain text — catalogs, `_`-prefixed,
    guides, and root-meta self-links have no graph node. With BASE_URL unset there
    is no graph to point to, so every such link becomes plain text.

    `[[wikilinks]]` are deliberately NOT converted here. Hub bodies carry ~13k of
    them (신한은행 / Shinhan Bank alone: 100 source refs); turning each into a full markdown URL
    would add hundreds of KB and bury the prose in URLs, hurting retrieval. They
    stay compact, and the deep-link protocol tells the LLM the `[[target]]` is
    itself the `#q=` key — so only the few references actually cited in an answer
    become deep-links. Flat listings (index.md) are the opposite case: one link
    per line, low noise, high value — those we convert here."""
    link = graph_deeplink_base()

    def repl(m: re.Match) -> str:
        label, path = m.group(1), m.group(2)
        if '://' in path:  # external URL ending in .md — leave the link intact
            return m.group(0)
        segs = path.split('/')
        folder = segs[-2] if len(segs) >= 2 else ''
        stem = segs[-1][:-3]  # drop '.md'
        if link and folder in _NODE_FOLDERS and not stem.startswith('_'):
            return f'[{label}]({link}#q={deeplink_key(stem)})'
        return label

    return _MD_LINK_RE.sub(repl, text)


# HTML comments in wiki pages are authoring/tooling artifacts, never reader
# content: abbreviation declarations (redundant with the inline `abbreviation(gloss)`
# the body already carries), `AUTO:* BEGIN/END` machine markers, and editorial
# sourcing memos. All are noise in RAG, so the export strips them.
_HTML_COMMENT_RE = re.compile(r'<!--.*?-->', re.DOTALL)


def _strip_comment(m: re.Match) -> str:
    """Blank an HTML comment — unless it appears to have swallowed real content.
    A genuine comment (abbreviation map, AUTO:* marker) carries no links; if a
    match contains a markdown link `](` or a wikilink `[[`, an unclosed `<!--`
    spanned into page content, so keep it rather than delete the content.
    (Abbreviation maps may use `- ` bullets, so a bare list item is not a tell.)"""
    span = m.group(0)
    if '](' in span or '[[' in span:
        return span
    return ''


def _clean_body(text: str) -> str:
    """Prepare a wiki page body for the RAG export: drop non-content HTML
    comments, then rewrite repo-relative links. Collapses the blank-line runs
    left where stripped comments sat."""
    text = _HTML_COMMENT_RE.sub(_strip_comment, text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return _rewrite_links(text)


# Per-file one-liners for the Project Knowledge structure table. Keyed by output
# filename; the table is generated from ROOT_META + FOLDER_MERGES + the source
# index so the file *set* can never drift from what export actually produces.
_FILE_DESC: dict[str, tuple[str, str]] = {
    'overview.md': ('Topic-by-topic synthesis analysis (root landscape)', 'Grasp overall context · frame the answer'),
    'contradiction.md': ('Contradiction synthesis (root)', 'Overview of conflicting issues'),
    'index.md': ('Directory of all entities·concepts (one line + deep-link) + source catalog', 'What exists + starting point for graph deep-links'),
    'all-overviews.md': ('Per-cluster field landscapes, merged', 'Field overview · synthesis'),
    'all-contradictions.md': ('Per-theme contradiction analyses, merged', 'Conflicting-issue detail'),
    'all-timelines.md': ('Timelines, merged', 'Chronological progression'),
    'all-syntheses.md': ('Analysis reports, merged', 'In-depth analysis'),
    'all-trails.md': ('Associative trails, merged', 'Explore cross-topic connections'),
    'all-sources-index.md': ('One-line source index (title · date)', 'Which originals exist + obtain the deep-link slug'),
}


def _file_structure_table() -> str:
    names = ROOT_META + [out for _, out in FOLDER_MERGES] + ['all-sources-index.md']
    rows = ['| File | Content | Use |', '|---|---|---|']
    for n in names:
        content, use = _FILE_DESC.get(n, ('—', '—'))
        rows.append(f'| {n} | {content} | {use} |')
    return '\n'.join(rows)


# Rough token estimate (≈ tokens per character) for the upload-budget guide — an
# order-of-magnitude aid, not an exact count. English averages ~0.25 tok/char;
# Korean (WIKI_LANG=ko) is denser at ~0.75 (Hangul tokenizes to more sub-tokens),
# calibrated against the Claude.ai context-overflow error on the Korean corpus.
_TOK_PER_CHAR = 0.75 if korean_mode() else 0.25
# Claude.ai project context ceiling (knowledge is loaded whole, not retrieved).
# The core tier must fit under this with headroom for the query + instructions;
# the budget guide flags an overrun instead of always claiming "safe".
_CONTEXT_LIMIT = 200_000
# Single priority order over all RAG files (most load-bearing first). The Core
# tier is filled greedily from this list under _CONTEXT_LIMIT; whatever doesn't
# fit drops to Optional. So Core membership auto-adjusts as the corpus grows —
# no hardcoded tier can drift past the limit. index (directory/deeplinks) and the
# root meta come first; among the soft synthesis files, all-syntheses is the large
# deep-dive placed last so it's the swing item that moves to Optional first; the
# ~100K+ aggregates trail at the end and only join Core if budget is left.
_TIER_PRIORITY = [
    'index.md', 'overview.md', 'contradiction.md',
    'all-timelines.md', 'all-trails.md', 'all-syntheses.md',
    'all-overviews.md', 'all-contradictions.md', 'all-sources-index.md',
]


def _est_tokens(name: str) -> int:
    p = OUT / name
    if not p.exists():
        return 0
    return int(len(p.read_text(encoding='utf-8')) * _TOK_PER_CHAR)


def _partition_tiers() -> tuple[list[str], list[str]]:
    """Greedily fill Core in priority order under _CONTEXT_LIMIT; the rest go to
    Optional. Files not generated this run (est 0) are skipped from both tiers."""
    core: list[str] = []
    optional: list[str] = []
    running = 0
    for name in _TIER_PRIORITY:
        est = _est_tokens(name)
        if est == 0:
            continue
        if running + est <= _CONTEXT_LIMIT:
            core.append(name)
            running += est
        else:
            optional.append(name)
    return core, optional


def _budget_guide() -> str:
    """Upload-budget guide: per-file token estimates + a core/optional split.

    Claude.ai loads project knowledge into context (no retrieval), so the full
    wiki (entity·concept bodies included) overflowed. RAG must stay within the
    ~200K project context, hence the tiering."""
    core, optional = _partition_tiers()
    core_total = sum(_est_tokens(n) for n in core)
    if core_total <= _CONTEXT_LIMIT:
        core_status = (
            '**Core — upload these first (total ~{:,} tok, within the ~{:,} limit):**'
            .format(core_total, _CONTEXT_LIMIT)
        )
    else:
        # Only reachable if the single top-priority file alone exceeds the limit.
        core_status = (
            '**Core — even the single highest-priority file alone totals ~{:,} tok, '
            'over the limit (~{:,}). The corpus needs to be trimmed:**'.format(core_total, _CONTEXT_LIMIT)
        )
    lines = [
        '## Upload Guide (Context Budget)\n',
        'A Claude.ai project loads knowledge files **whole into context, not via '
        'retrieval**. The limit is about 200K tokens, so uploading everything '
        'overflows it. Upload within the estimated token counts (approximate) below. '
        '(The Core/Optional split is determined automatically by filling up to the '
        'limit in priority order.)\n',
        core_status,
    ]
    for n in core:
        lines.append(f'- `{n}` (~{_est_tokens(n):,} tok)')
    lines.append(
        '\n**Optional — add selectively if the budget allows (large files; uploading '
        'them all together risks overflow):**'
    )
    for n in optional:
        lines.append(f'- `{n}` (~{_est_tokens(n):,} tok)')
    lines.append(
        '\nEntity/concept bodies and source originals are not in the RAG corpus at '
        'all (graph-only). If a question triggers a "context limit exceeded" error, '
        'trim the Optional files first.\n'
    )
    return '\n'.join(lines)


def _write_export_readme() -> str:
    """Write wiki-export/README.md — the complete Claude.ai Project instructions
    document. The operator pastes the whole file into the project's custom-
    instructions field (the reliable channel: always in context, unlike the in-file
    handoff block which retrieval can chunk past). It carries the corpus structure,
    answer rules, and the deep-link protocol so retrieval+answer quality holds, not
    just the deep-links. Generated from the same constants as the export, so the
    file table and protocol can never drift from reality."""
    has_graph = bool(_deeplink_protocol())
    cite_rule = (
        'Cite the supporting hub/original via a **graph deep-link** (see the '
        '"Graph Deep-Link Convention" below). The target of a `[[title]]` / '
        '`[[slug|alias]]` wikilink in the body is exactly the `#q=` key, so do not '
        'put the wikilink notation in the answer; deep-link to that target instead.'
        if has_graph else
        'Cite the supporting page in `[[page title]]` form.'
    )
    parts = [
        '# LLM Wiki Knowledge Base — Claude.ai Project Instructions\n',
        'This project is a wiki knowledge base built from collected source documents. '
        '**Upload the files in the `wiki-export/` '
        'folder as Project Knowledge**, and **paste this entire document into the '
        'project\'s custom-instructions field.**'
        + (' (Re-paste whenever `BASE_URL` changes.)\n' if has_graph else '\n'),

        '## Project Knowledge File Structure\n',
        'This project runs on **two tiers** — the RAG corpus (the synthesis and '
        'directory files uploaded here) synthesizes the answer, and the original '
        'detail is served by the graph browser (deep-links). Individual entity/concept '
        'bodies and source originals are **not in the RAG corpus**: the corpus would '
        'exceed the context limit, and the full text all lives as nodes in the graph. '
        '`index.md` is the directory holding every entity/concept as a one-line '
        'description + deep-link. The count on the first line of each file reflects '
        'the latest status.\n',
        _file_structure_table() + '\n',
        '**Detail is in the graph**: when you need the full content, quotes, '
        'connections, or backlinks of a specific entity/concept/source, find the key '
        'in the corresponding entry of `index.md` / `all-sources-index.md` or in a '
        'wikilink of the synthesis body, and build a graph deep-link (convention '
        'below).\n',

        _budget_guide(),

        '## Answer Rules\n',
        ('1. Answer **in Korean, using polite/honorific speech to the operator**.\n'
         if korean_mode() else
         '1. Answer **in English**.\n') +
        '2. Exploration order: `overview` · `contradiction` · `all-overviews` '
        '(context · synthesis) → `index` (what exists · deep-link starting point) → '
        '`all-syntheses` · `all-contradictions` (in-depth) → detail via graph deep-link.\n'
        '3. Build the answer body from the synthesis layer (overview, synthesis, '
        'contradiction, etc.) and `index`. Entity/concept/source detail is not in the '
        'RAG corpus, so send the reader to the graph deep-link.\n'
        f'4. {cite_rule}\n'
        '5. **Wiki first, verify and supplement with the web when needed.** Build the '
        'answer from the wiki (synthesis layer + graph) first, but for (a) content not '
        'in the wiki, (b) information that may have gone stale with time (recent events, '
        'changing figures, current officeholders, prices, etc.), or (c) cases where a '
        'key claim needs fact-checking, **verify with web search and fill the gaps** '
        '(the web-search tool must be enabled). The wiki is an accumulation up to a '
        'certain point in time, so the latest trends may need web supplementation.\n'
        '6. **Distinguish your sources** — mark wiki-based content with graph deep-links '
        'and web-search-based content with that web source\'s link, so it is clear where '
        'each came from. When the wiki and the web disagree, present both with their '
        'timestamps. If neither the wiki nor the web confirms something, state it as '
        '"unverifiable".\n'
        '7. When sources contradict each other, present both sides.\n'
        '8. Answer concisely, but when detail is requested, include the relevant '
        'original-source deep-links.\n',
    ]
    protocol = _deeplink_protocol()
    if protocol:
        parts.append(f'## Graph Deep-Link Convention\n\n{protocol}\n')
    parts.append(
        '## Wiki Structure Notes\n\n'
        '- entity/concept entries in `index.md`: `[title](deep-link) — one-line '
        'description`. The title is the `#q=` key.\n'
        '- In synthesis bodies (overview, synthesis, etc.), the target of a '
        '`[[title]]` / `[[slug|alias]]` wikilink is the entity/concept title or '
        'source slug = the `#q=` key.\n'
        '- Use each entity/concept title verbatim as the deep-link `#q=` key '
        '(English TitleCase by default, e.g. Microsoft; a non-Latin-script title '
        'is used as-is when the entity has no standard Latin form).\n'
    )
    name = 'README.md'
    (OUT / name).write_text('\n'.join(parts), encoding='utf-8')
    return name


def _copy_root_meta() -> list[str]:
    produced: list[str] = []
    for name in ROOT_META:
        src = WIKI / name
        if not src.exists():
            continue
        (OUT / name).write_text(
            _clean_body(src.read_text(encoding='utf-8')), encoding='utf-8',
        )
        produced.append(name)
    return produced


def _merge_folder(folder: str, outname: str) -> tuple[str, int] | None:
    folder_path = WIKI / folder
    if not folder_path.is_dir():
        return None
    files = sorted(
        p for p in folder_path.iterdir()
        if p.suffix == '.md' and not p.name.startswith('_')
    )
    if not files:
        return None
    parts = [f'# All {folder.upper()} ({len(files)})\n']
    for f in files:
        parts.append(f'---\n\n{_clean_body(f.read_text(encoding="utf-8"))}\n')
    (OUT / outname).write_text('\n'.join(parts), encoding='utf-8')
    return outname, len(files)


def _source_locator_line(src: Path) -> str:
    """One index line for a source: `slug` — title (date).

    The slug is the #q= deep-link target into the graph browser; the title (a
    news headline) identifies it. Summary snippets were dropped — they added
    ~118K tokens (the dominant share of this index) for marginal value over the
    headline, and the full summary is one deep-link away in the graph.

    Title/date come from the canonical `parse_page_meta` (the same extractor
    index.py and clusters.py use) — `date` is the published date, else the scraped
    date, and the title falls back to the slug when absent."""
    text = src.read_text(encoding='utf-8')
    title, _ptype, _desc, _sf, date, _url = parse_page_meta(text, src.name)
    return f'- `{src.stem}` — {title} ({date or "date unknown"})'


def _write_source_index() -> tuple[str, int]:
    """Write a single all-sources-index.md: one locator line per source, grouped
    by primary cluster. Source bodies are not exported — they live in the graph
    (reachable via #q=<slug>), and this index lets the LLM resolve a claim to the
    right source slug for a deep link."""
    data = json.loads(CLUSTERS_JSON.read_text(encoding='utf-8'))
    cluster_name = {c['slug']: c['name'] for c in data['clusters']}
    assignments = data.get('source_assignments', {})

    by_cluster: dict[str, list[Path]] = defaultdict(list)
    for rel_path, info in assignments.items():
        primary = info.get('primary') or '_unassigned'
        src = WIKI / rel_path
        if src.exists():
            by_cluster[primary].append(src)

    # Clean up per-cluster body files from older exports (and any prior index).
    for stale in OUT.glob('all-sources*.md'):
        stale.unlink(missing_ok=True)

    total = sum(len(v) for v in by_cluster.values())
    parts = [
        f'# SOURCES Index — originals are in the graph browser ({total})\n',
        'This file is an **index**, not the source originals. Individual source '
        'bodies, quotes, connections, and backlinks are in the graph browser. Open '
        'an original via each entry\'s `slug` (`#q=<slug>`). Use this slug when '
        'pointing to a supporting original in an answer.\n',
    ]
    for slug in sorted(by_cluster):
        sources = sorted(by_cluster[slug], key=lambda p: p.name)
        name = cluster_name.get(slug, slug if slug != '_unassigned' else 'Unclassified')
        parts.append(f'\n## {name} ({slug}, {len(sources)})\n')
        parts.extend(_source_locator_line(s) for s in sources)
    outname = 'all-sources-index.md'
    (OUT / outname).write_text('\n'.join(parts) + '\n', encoding='utf-8')
    return outname, total


def _prune_stale(keep: set[str]) -> list[str]:
    """Remove any *.md in the export folder not produced by this run — e.g. a
    pre-rename `contradictions.md`, or `all-entities.md`/`all-concepts.md` after
    those merges were dropped. Keeps the folder == exactly what export emits."""
    dropped: list[str] = []
    for p in OUT.glob('*.md'):
        if p.name not in keep:
            p.unlink(missing_ok=True)
            dropped.append(p.name)
    return sorted(dropped)


def main() -> int:
    OUT.mkdir(exist_ok=True)
    root_meta = _copy_root_meta()
    folder_results = [r for r in (_merge_folder(f, o) for f, o in FOLDER_MERGES) if r]
    index_name, index_count = _write_source_index()
    # Keep only what this run actually produced (a missing root-meta source or an
    # emptied sub-folder yields no file), so a now-stale prior output is pruned.
    # README.md is written after _prune_stale, so keep it by name.
    keep = (set(root_meta) | {name for name, _ in folder_results}
            | {index_name, 'README.md'})
    dropped = _prune_stale(keep)

    print('wiki-export/ regenerated')
    if dropped:
        print(f'  dropped stale: {", ".join(dropped)}')
    print(f'  root meta ({len(root_meta)}): {", ".join(root_meta)}')
    for name, count in folder_results:
        print(f'  {name}: {count}')
    index_kb = (OUT / index_name).stat().st_size / 1024
    print(f'  {index_name}: {index_count} indexed, {index_kb:.0f} KB (source bodies are in the graph)')
    readme_name = _write_export_readme()
    print(f'  {readme_name}: instructions doc + upload budget guide (for the Claude.ai instructions field)')
    md_files = list(OUT.glob('*.md'))
    total = sum(f.stat().st_size for f in md_files)
    print(f'  total: {total / 1024 / 1024:.2f} MB across {len(md_files)} files')
    core, optional = _partition_tiers()
    core_tok = sum(_est_tokens(n) for n in core)
    opt_tok = sum(_est_tokens(n) for n in optional)
    print(f'  RAG budget (est.): core ~{core_tok:,} tok ({len(core)} files), '
          f'optional ~{opt_tok:,} tok ({len(optional)} files) '
          f'(Claude.ai limit ~{_CONTEXT_LIMIT // 1000}K, entity/concept bodies not generated = graph-only)')
    print(f'    core auto-selected: {", ".join(core)}')

    # Stage the hosted graph browser into _site/ with obscured filenames
    # (HTML + the four JSONs graph.html fetches), from the same snapshot.
    print('_site/ (deploy assets, obscured filenames):')
    for name, size in stage_site(REPO_ROOT / '_site', STANDALONE_SLUG):
        print(f'  {name}: {size / 1024 / 1024:.2f} MB')
    return 0


if __name__ == '__main__':
    sys.exit(main())
