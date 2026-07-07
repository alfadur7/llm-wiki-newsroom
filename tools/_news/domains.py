"""News domain sets for `WebSearch allowed_domains` (gap auto-augmentation).

NOTE: these lists are a reference example carried over from the original
(Korean IT/finance) corpus this engine was built for — they are NOT tuned for
the shipped open-source-AI example corpus. Re-curate both lists (and the
Korean-summary convention below) per deployment; the selection mechanism is
corpus-agnostic, only the domain inventory is corpus-specific.

Two curated lists, selected at search time by the editor-in-chief. The engine
is English-native (tools/_lib.py::korean_mode), so GLOBAL is the default for the
shipped corpus; KOREAN applies only under WIKI_LANG=ko or a Korea-framed
deployment (see wiki-news.md:46,63):

  GLOBAL_IT_FINANCE_NEWS  — default. Global-entity / globally-framed gaps.
                            Cluster-topic authority outlets covering AI coding,
                            LLMs, banking tech, enterprise AI, cloud, data
                            centers, security.
  KOREAN_IT_FINANCE_NEWS  — WIKI_LANG=ko. Korean-entity / Korea-framed gaps.

Selection heuristic (editor applies per gap target, no auto-detection — entity
nationality is an NER problem, kept as editorial judgment):
  - Target entity is a non-Korean org/person, OR the topic is intrinsically
    global (e.g. global-bank AI-coding adoption, foundation-model releases) →
    GLOBAL set (or the KOREAN + GLOBAL union for broad sweeps).
  - Target is a Korean entity / domestic-policy topic → KOREAN set (WIKI_LANG=ko).

Under WIKI_LANG=ko both sets feed Korean-language source PAGES regardless of the
raw's language: the reporter writes a Korean summary/translation of the foreign
primary source (the long-standing pattern for WSJ/Reuters-cited items). On the
English-native default the reporter writes English summaries. Either way this is
distinct from ingesting a raw English vendor blog as-is, which stays out of
auto-scope.

KOREAN list derived from `_source_map.json` 1,351 URL frequency (2026-05-15)
intersected with crawler accessibility; Phase 2C validation (5 queries × 10
results) yielded 68% novel-source rate (cio.com 65% of the novel pool).
GLOBAL list derived from cluster-topic authority + empirical accessibility
probes (2026-05-23): each domain returned results under `allowed_domains`
without a crawler 400.

Maintenance: re-measure `_source_map.json` top 20 once per quarter and adjust.
See `.claude/operations/gap-detection-rollout.md` for the validation procedure;
the exclusion rationale is inlined in the comment block at the bottom of this file.
"""
from __future__ import annotations

# Ranks reference the 2026-05-15 _source_map.json measurement. Position in
# the list is descending priority — earlier domains saw higher hit counts in
# validation, but WebSearch is order-insensitive so the ranking is for human
# review only.
KOREAN_IT_FINANCE_NEWS: list[str] = [
    "kbanker.co.kr",    # 대한금융신문 / Daehan Financial News (measured #5, 64) — banking trade paper
    "cio.com",          # CIO Korea/Global (measured #6, 51) — 65% novel in validation
    "newswire.co.kr",   # 뉴스와이어 / Newswire (measured #7, 45) — press-release distribution
    "ddaily.co.kr",     # 디지털데일리 / Digital Daily (measured #9, 23)
    "etnews.com",       # 전자신문 / Electronic Times (measured #10, 22)
    "zdnet.co.kr",      # ZDNet Korea (measured #12, 18)
    "ciokorea.com",     # CIO Korea (measured #13, 11)
    "hankyung.com",     # 한국경제 / Korea Economic Daily (measured #14, 8)
    "aitimes.com",      # AI타임스 / AI Times (measured #15, 7)
    "dt.co.kr",         # 디지털타임스 / Digital Times (measured #17, 6)
    "bloter.net",       # 블로터 / Bloter (measured #18, 6)
    "aimatters.co.kr",  # AI 매터스 / AI Matters (measured #19, 5)
    "edaily.co.kr",     # 이데일리 / Edaily (measured #20, 5)
]

# Global cluster-topic authority outlets. Position is grouped by the wiki
# cluster each one most authoritatively covers (a domain may serve several).
# All verified accessible under `allowed_domains` on 2026-05-23 — no crawler
# 400. Use for global-entity / globally-framed gaps (see module docstring).
GLOBAL_IT_FINANCE_NEWS: list[str] = [
    # AI coding · harness engineering
    "thenewstack.io",          # The New Stack — cloud-native·agentic engineering
    "infoworld.com",           # InfoWorld — developer·AI coding tools
    "leaddev.com",             # LeadDev — engineering leadership·AI coding
    # LLMs · foundation models
    "technologyreview.com",    # MIT Technology Review — AI/LLM authority
    "venturebeat.com",         # VentureBeat — AI·enterprise AI
    "techcrunch.com",          # TechCrunch — AI startup funding·M&A·VC deal beat
                               #   (an area other outlets don't cover — for the
                               #    ARR·investment·neocloud capital-cycle narrative.
                               #    Editor-curated: focus on competitive-landscape-
                               #    shifting deals, exclude one-off small rounds)
    # Banking IT · digital banking
    "finextra.com",            # Finextra — global fintech·banking-tech standard-bearer
    "americanbanker.com",      # American Banker — U.S. banking authority
    "evidentinsights.com",     # Evident — bank AI Index benchmarking
    "bankautomationnews.com",  # Bank Automation News — banking automation·AI
    # Enterprise AI adoption · cloud·infrastructure
    "siliconangle.com",        # SiliconANGLE/theCUBE — enterprise AI·cloud
    "theregister.com",         # The Register — enterprise IT·cloud·security·dev
    "computerweekly.com",      # Computer Weekly — UK enterprise IT
    # AI data centers · power
    "datacenterdynamics.com",  # DCD — AI data center·power authority
    "datacenterknowledge.com", # Data Center Knowledge — DC infrastructure·power
    # Security · governance
    "therecord.media",         # The Record (Recorded Future) — cybersecurity journalism
    "bleepingcomputer.com",    # BleepingComputer — security·breach analysis
    "darkreading.com",         # Dark Reading — enterprise security
]

# Excluded from `allowed_domains` despite being high-frequency or otherwise
# attractive — rationale per entry below:
#
#   bikorea.net (measured #1, 200)
#     Outlet published by this wiki's operator — self-reference avoidance policy.
#
#   biz.chosun.com / mk.co.kr
#     The Anthropic WebSearch crawler returns a 400 (if the domain is included in
#     allowed_domains the whole query fails). However, `fetch_article.py` can
#     still fetch them normally via bot headers + the chosun.com
#     `?outputType=amp` URL-variant fallback — our script works around the block
#     at the fetch stage.
#
#   news.naver.com · v.daum.net · n.news.naver.com
#     Aggregators (534 total, but absent from the Anthropic index — including
#     them in allowed_domains yields 0 results. They appear often in our
#     _source_map only because mobile share-sheet redirect pages were saved
#     as-is).
#
#   aws.amazon.com · cloud.google.com · gemini.google.com
#     English primary sources (vendor blogs). Ingesting English raw as-is is out
#     of auto-augmentation scope. (Secondary coverage on GLOBAL_IT_FINANCE_NEWS
#     is allowed for writing Korean-summary sources — see the module docstring.
#     This item is limited to vendor primary blogs.)
#
#   arstechnica.com · thebanker.com · zdnet.com (global)
#     Confirmed an Anthropic crawler 400 during GLOBAL candidate validation on
#     2026-05-23 (if included in allowed_domains the whole query fails).
#     thebanker.com is an FT-family paywall. arstechnica/zdnet are authoritative
#     but crawler-blocked, so permanently excluded — the same area is covered by
#     theregister·thenewstack·siliconangle·technologyreview instead.
