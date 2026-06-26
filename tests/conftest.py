"""Shared tests/ setup — puts tools/ and .claude/hooks/ on the import path.

Assumes `python -m pytest` is run from the repo root. Follows the same sys.path
convention as the lint modules (direct import of tools/).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "_lint"))
sys.path.insert(0, str(ROOT / ".claude" / "hooks"))
