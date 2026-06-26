"""
Patch the obsidian-qmd plugin after every BRAT update.

Patches applied (all idempotent — re-running is safe):

  1. Show frontmatter `title` in search results (falls back to heading, then filename).
  2. Speed up hybrid (`query`) searches on CPU/iGPU by dropping the two LLM
     stages that dominate cold-call latency:
       - `--no-rerank` skips the reranker (measured ~291s/call on an Intel iGPU).
       - wrapping plain input as a typed `vec:`/`lex:` document bypasses the
         query-expansion LLM (~89s/call); lex+vec RRF fusion is kept.
     Already-typed Advanced-mode queries (intent/lex/vec/hyde/expand) pass
     through untouched. Keyword (`search`) and Semantic (`vsearch`) modes are
     unaffected. (The remaining floor is embedding-model cold-load per call —
     the plugin shells out fresh each search, so sub-embedding-load latency
     needs a warm daemon, which this plugin does not support.)

Then, for the Windows "QMD Binary Not Found" case, it also:
  - copies a node runtime beside qmd.js (the plugin runs `node qmd.js` and finds
    node in that folder; the bare `qmd` shim can't be run via execFile), and
  - prints the absolute Executable Path to paste into the plugin settings.

Usage:
    python tools/patch_obsidian_qmd.py
"""

from __future__ import annotations

import os
import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

# Derive the plugin path from the repo's own vault so it resolves on any
# machine (tools/ → repo root → wiki/.obsidian/...). `--plugin-path` overrides
# for non-standard vault layouts.
_REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_PATH = _REPO_ROOT / "wiki" / ".obsidian" / "plugins" / "obsidian-qmd" / "main.js"

# qmd CLI install dir (npm global). The plugin runs `node qmd.js` and discovers
# the node binary *beside* qmd.js (resolveNodeRuntime → dirname(qmd.js)/node),
# so on Windows a node copy must live here — the bare `qmd`/`qmd.cmd` shim can't
# be run via execFile and the PATH/login-shell lookup fails (no /bin/zsh|bash).
QMD_CLI_DIR = Path(os.environ.get("APPDATA", "")) / "npm" / "node_modules" / "@tobilu" / "qmd" / "dist" / "cli"


@dataclass
class Patch:
    name: str
    orig: str            # exact substring, or regex pattern when is_regex=True
    new: str             # replacement (may use \1.. backrefs when is_regex=True)
    marker: str          # substring whose presence means the patch is already applied
    is_regex: bool = False


# The minified single/two-letter identifiers (result-row var, RRF helper) are
# re-emitted on every esbuild, so the two patches that touch them match stable
# anchors with regex capture groups instead of literals — surviving BRAT
# updates that only churn variable names. The function-injection patch keeps an
# exact target (it anchors on stable API names: toVaultRelativePath etc.).
PATCHES: list[Patch] = [
    Patch(
        name="title-priority",
        orig=r"([A-Za-z$_]\w*)=e\.title\|\|([A-Za-z$_]\w*)\.getResultFallbackTitle\(e\)",
        new=r"\1=\2.getFrontmatterTitle(e)||e.title||\2.getResultFallbackTitle(e)",
        marker=".getFrontmatterTitle(e)||e.title",
        is_regex=True,
    ),
    Patch(
        name="getFrontmatterTitle-inject",
        orig=(
            'getResultFallbackTitle(e){var s,n,a;return(a=(n=((s=this.toVaultRelativePath(e.file))'
            '!=null?s:e.file).split("/").pop())==null?void 0:n.replace(/\\.md$/,""))!=null?a:e.file}'
        ),
        new=(
            'getResultFallbackTitle(e){var s,n,a;return(a=(n=((s=this.toVaultRelativePath(e.file))'
            '!=null?s:e.file).split("/").pop())==null?void 0:n.replace(/\\.md$/,""))!=null?a:e.file}'
            "getFrontmatterTitle(e){try{var s,n;let p=(s=this.toVaultRelativePath(e.file))!=null?s:null;"
            "if(!p)return null;let f=this.app.vault.getAbstractFileByPath(p);if(!f)return null;"
            "let c=this.app.metadataCache.getFileCache(f);"
            "let t=(n=c==null?void 0:c.frontmatter)==null?void 0:n.title;"
            'return typeof t=="string"&&t.trim()?t.trim():null}catch(r){return null}}'
        ),
        marker="getFrontmatterTitle(e){try{",
    ),
    Patch(
        name="hybrid-no-rerank",
        orig=(
            r'(async search\(i,e,t,s\)\{let n=\[i,e,"-c",t,"--json","-n",String\(s\)\]),'
            r'(\{stdout:a\}=await this\.run\(n\);return )(\w+)(\(a\)\})'
        ),
        new=r'\1;if(i==="query")n.push("--no-rerank");let\2\3\4',
        marker='n.push("--no-rerank")',
        is_regex=True,
    ),
    # Skip the query-expansion LLM (qmd-query-expansion-1.7B) for hybrid
    # searches. A bare `qmd query "text"` runs that 1.7B model to expand the
    # query (measured ~89s cold per call on an Intel iGPU); a *typed* query
    # document (vec:/lex: lines) bypasses expansion entirely. So wrap plain
    # input as `vec: <text>\nlex: <text>` — keeps lex+vec RRF fusion, drops the
    # expansion model. Skipped when the user already typed a structured query
    # (Advanced mode: intent/lex/vec/hyde/expand prefix). Anchors on the
    # no-rerank snippet emitted by the patch above, so it upgrades an
    # already-no-rerank-patched plugin and a fresh one alike.
    Patch(
        name="hybrid-skip-expansion",
        orig='if(i==="query")n.push("--no-rerank")',
        new=(
            'if(i==="query"){'
            'if(!/^\\s*(intent|lex|vec|hyde|expand):/im.test(e))'
            'n[1]="vec: "+e+"\\nlex: "+e;'
            'n.push("--no-rerank")}'
        ),
        marker='n[1]="vec: "+e',
    ),
]


def ensure_node_runtime() -> None:
    """Copy a node binary next to qmd.js (idempotent) so the plugin can run it.

    The plugin checks `dirname(qmd.js)/node` (no extension) and falls back to a
    Unix login-shell lookup that doesn't exist on Windows. Copying node there
    makes `node qmd.js` work. Both `node` and `node.exe` are written: the plugin
    looks for `node`, while `node.exe` matches the Windows convention.
    """
    if not QMD_CLI_DIR.exists():
        print(f"[!] qmd CLI dir not found: {QMD_CLI_DIR}", file=sys.stderr)
        print("    install qmd first: npm install -g @tobilu/qmd", file=sys.stderr)
        return
    node_src = shutil.which("node")
    if not node_src:
        print("[!] node not found on PATH — install Node.js, then re-run", file=sys.stderr)
        return
    copied = []
    for name in ("node.exe", "node"):
        dest = QMD_CLI_DIR / name
        if dest.exists():
            continue
        shutil.copy2(node_src, dest)
        copied.append(name)
    if copied:
        print(f"[+] copied node runtime into qmd dist/cli: {', '.join(copied)}")
    else:
        print("[=] node runtime already present beside qmd.js")


def print_executable_path_hint() -> None:
    """Print the absolute Executable Path to paste into the qmd plugin settings."""
    print()
    print("Obsidian -> qmd plugin settings -> 'Executable Path':")
    print(f"    {QMD_CLI_DIR / 'qmd.js'}")
    print("    (absolute path skips the failing Windows shell lookup; the .js")
    print("     target is run by the node copied beside it)")


def main() -> int:
    ap = argparse.ArgumentParser(description="Patch obsidian-qmd main.js")
    ap.add_argument(
        "--plugin-path", type=Path, default=PLUGIN_PATH,
        help="path to .obsidian/plugins/obsidian-qmd/main.js inside the vault "
             "(defaults to this repo's wiki/.obsidian vault; override for a non-standard layout)")
    args = ap.parse_args()
    plugin_path = args.plugin_path
    if not plugin_path.exists():
        print(f"[x] plugin not found: {plugin_path}", file=sys.stderr)
        print("    (specify the vault path with --plugin-path)", file=sys.stderr)
        return 1

    content = plugin_path.read_text(encoding="utf-8")
    applied: list[str] = []
    for p in PATCHES:
        if p.marker in content:
            continue  # already applied
        if p.is_regex:
            content, n = re.subn(p.orig, p.new, content, count=1)
            found = n > 0
        else:
            found = p.orig in content
            if found:
                content = content.replace(p.orig, p.new, 1)
        if not found:
            print(f"[x] patch '{p.name}' target not found", file=sys.stderr)
            print("    plugin may have changed; inspect main.js and update this script.",
                  file=sys.stderr)
            return 2
        applied.append(p.name)

    if applied:
        plugin_path.write_text(content, encoding="utf-8")
        print(f"[+] patched {plugin_path.name}: {', '.join(applied)}")
        print("    -> reload Obsidian (Ctrl+P -> 'Reload app without saving')")
    else:
        print("[=] already patched, no changes needed")

    ensure_node_runtime()
    print_executable_path_hint()
    return 0


if __name__ == "__main__":
    sys.exit(main())
