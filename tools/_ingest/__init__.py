"""Ingest pipeline helper scripts for /wiki-ingest (no entry point — Claude orchestrates).

Submodules (invoked as CLI steps, mirroring tools/_news/):
  - prefilter_ingest: raw-folder dedup classification (URL/path/genuine-new)
  - fetch_article:    fetch URL → raw markdown/PDF (browser-like headers)
  - fetch_inbox:      process raw/_inbox.md mobile queue (fetch + dedup)
  - suggest_links:    surface unlinked entity/concept mentions in source bodies
  - suggest_tags:     surface frontmatter tag candidates for empty-tag sources (T1 gate companion)
"""
