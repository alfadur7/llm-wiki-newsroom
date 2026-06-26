"""Hub-label and tag normalization for gap query construction.

Two helpers — both pure functions, both `lint graph gaps --json` consumers
share the same definitions:

  - `hub_korean_label(label)` strips a trailing parenthetical gloss regardless
    of script so `"테슬라 (Tesla)"` → `"테슬라"` and `"Cortex AI (스노우플레이크)"`
    → `"Cortex AI"`. Labels with no parenthetical (e.g. `"Amazon Q Developer"`,
    `"DGB대구은행"`) are returned untouched so queries still hit on the brand.

  - `normalize_tags(tags)` case-folds + applies a synonym map so
    `["llm", "AI", "LLM"]` collapses to `["LLM", "AI"]` with rank-preserved
    order. The map covers the ~10 English/Korean variants we've actually
    observed in hub frontmatter across the 568-page corpus.
"""
from __future__ import annotations

import re

# Trailing parenthetical (Latin chars optional) — used to strip the English
# gloss from hub labels like "프롬프트 인젝션 (Prompt Injection)".
_TRAILING_PAREN = re.compile(r"^(.+?)\s*\([^)]+\)\s*$")

def hub_korean_label(label: str) -> str:
    """Strip a trailing parenthetical so the label tokenizes cleanly in search.

    - `"테슬라 (Tesla)"` → `"테슬라"`
    - `"프롬프트 인젝션 (Prompt Injection)"` → `"프롬프트 인젝션"`
    - `"Cortex AI (스노우플레이크)"` → `"Cortex AI"`
    - `"MCP (Model Context Protocol)"` → `"MCP"`
    - `"AWS (Amazon Web Services)"` → `"AWS"`
    - `"Amazon Q Developer"` (no parenthetical) → unchanged
    - `"DGB대구은행"` → unchanged

    Removing the parenthetical always wins because Korean news search engines
    tokenize each parenthesized fragment as separate terms (`"Model Context
    Protocol 2026"` ranks tutorial articles over the hub topic). The
    parenthetical is invariably a gloss — either an English transliteration
    or a vendor attribution — and dropping it preserves the head term.
    """
    if not label:
        return label
    m = _TRAILING_PAREN.match(label)
    if not m:
        return label.strip()
    return m.group(1).strip()


# Tag synonym map — maps case-folded variants to a canonical display form.
# Canonical form is the variant most search engines accept and most authors
# write in the wild (uppercase acronyms, English where Korean has no settled
# convention). Add entries as new variants surface in hub frontmatter.
TAG_SYNONYMS: dict[str, str] = {
    "llm": "LLM",
    "ai": "AI",
    "aiops": "AIOps",
    "rag": "RAG",
    "mcp": "MCP",
    "api": "API",
    "ml": "ML",
    "sdk": "SDK",
    "ide": "IDE",
    "ui": "UI",
    "ux": "UX",
    "saas": "SaaS",
    "iaas": "IaaS",
    "paas": "PaaS",
    "cbdc": "CBDC",
    "kyc": "KYC",
}


def normalize_tags(tags: list[str]) -> list[str]:
    """Case-fold + synonym-collapse a tag list, preserving first-occurrence order.

    Example: `["llm", "AI", "LLM", "디지털전환"]` → `["LLM", "AI", "디지털전환"]`

    Tags whose case-folded form is not in `TAG_SYNONYMS` are kept verbatim so
    Korean tags like `"디지털전환"` and uncommon acronyms pass through. Empty
    or whitespace-only entries are dropped.
    """
    seen: set[str] = set()
    out: list[str] = []
    for raw in tags or []:
        if not raw or not raw.strip():
            continue
        key = raw.strip().lower()
        canonical = TAG_SYNONYMS.get(key, raw.strip())
        if canonical in seen:
            continue
        seen.add(canonical)
        out.append(canonical)
    return out
