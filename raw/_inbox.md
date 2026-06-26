# Inbox

Multi-channel URL queue. One line = one URL, optionally with `  # key=value ...` metadata attached.
Entry channels: mobile share-sheet · `/wiki-news` interactive · `/wiki-news --gap --batch` · background cron.

Emptied by running `python tools/_ingest/fetch_inbox.py` or `/wiki-ingest inbox`
(failed URLs are retained so the next run retries them).

Line format:
  https://example.com/article-A
  https://example.com/article-B  # source=auto-gap gap=single-source hub=AICC ts=2026-05-15T02:00Z

The separator between the URL and the metadata is **two spaces + `#`**. A URL fragment (`#anchor`) attaches with no space, so it stays safe.
A URL without metadata defaults to `source=mobile`.

Guides: [.claude/operations/mobile-inbox-setup.md](../.claude/operations/mobile-inbox-setup.md)
       [.claude/operations/gap-detection-rollout.md](../.claude/operations/gap-detection-rollout.md)

<!-- URLs below this line. Blank lines and lines starting with # are ignored. -->
