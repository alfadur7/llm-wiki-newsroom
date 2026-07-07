"""Weekly briefing email dispatch entry point.

Renders `wiki/syntheses/weekly-briefing-YYYY-wNN.md` to email HTML and sends it via Gmail SMTP.
A deterministic dispatch step separated from generation (the LLM) — send-briefing.yml (GH Action)
invokes it when a briefing is pushed, and locally you can use --dry-run to inspect the rendered
output only.

Usage:
    python tools/send_briefing.py --latest                  # send the latest briefing (env credentials)
    python tools/send_briefing.py --file <path>             # send a specific file
    python tools/send_briefing.py --file <path> --dry-run   # save HTML to the system temp dir without sending
    python tools/send_briefing.py --latest --to me@x.com    # override recipients (testing)

Credential/recipient env: GMAIL_USER · GMAIL_APP_PASSWORD · BRIEFING_RECIPIENTS (see mailer.py).
"""
from __future__ import annotations

import argparse
import re
import smtplib
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tools/ on path
# _lib import also reconfigures stdout/stderr to UTF-8 (Windows cp949 console).
from _lib import WIKI  # noqa: E402
from _briefing import render as render_mod  # noqa: E402
from _briefing import mailer  # noqa: E402

SYNTHESES = WIKI / "syntheses"
_BRIEFING_RE = re.compile(r"^weekly-briefing-(\d{4})-w(\d{1,2})$")


def _week_key(path: Path) -> tuple[int, int] | None:
    """Extract (year, week) integers from the file stem. Avoids string sorting (w9>w23)."""
    m = _BRIEFING_RE.match(path.stem)
    return (int(m.group(1)), int(m.group(2))) if m else None


def latest_briefing() -> Path | None:
    """The weekly-briefing-*.md with the maximum (year, week) integer."""
    candidates = [
        (k, p) for p in SYNTHESES.glob("weekly-briefing-*.md") if (k := _week_key(p))
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda kp: kp[0])[1]


def main() -> int:
    ap = argparse.ArgumentParser(description="Send weekly briefing email")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--latest", action="store_true", help="send the latest weekly-briefing")
    g.add_argument("--file", type=str, help="path to the briefing .md to send")
    ap.add_argument("--dry-run", action="store_true", help="save HTML to the system temp dir without sending")
    ap.add_argument("--to", type=str, help="override recipients (comma-separated, for testing)")
    args = ap.parse_args()

    if args.latest:
        target = latest_briefing()
        if target is None:
            print(f"[FAIL] no weekly-briefing file in {SYNTHESES}.", file=sys.stderr)
            return 1
    else:
        target = Path(args.file)
        if not target.exists():
            print(f"[FAIL] file not found: {target}", file=sys.stderr)
            return 1

    rendered = render_mod.render(target.read_text(encoding="utf-8"))
    print(f"[render] {target.name} → subject: {rendered['subject']}")
    if not render_mod.graph_base():
        print("[render] graph base not set — all wikilinks rendered as plain text (no deep links).")

    if args.dry_run:
        out = Path(tempfile.gettempdir()) / f"{target.stem}.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered["html"], encoding="utf-8")
        print(f"[dry-run] HTML saved: {out}  ({len(rendered['html'])} bytes)")
        return 0

    recipients = (
        [c for a in args.to.split(",") if (c := mailer.clean_addr(a))]
        if args.to
        else mailer.recipients_from_env()
    )
    try:
        mailer.send(rendered["subject"], rendered["html"], rendered["text"], recipients)
    except (smtplib.SMTPException, OSError, ValueError) as e:
        # In the unattended pipeline (GH Actions), emit a diagnosable message + exit 1
        # instead of a raw traceback — credential/config/network failures (ValueError
        # covers missing GMAIL_* secrets or empty recipients) are identifiable
        # straight from the log.
        print(f"[error] SMTP send failed: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    print(f"[sent] sent to {len(recipients)}: {', '.join(recipients)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
