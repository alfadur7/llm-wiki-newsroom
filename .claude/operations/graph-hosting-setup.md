# Graph Browser Hosting Setup

A one-time setup to publicly deploy the graph browser (the `_site/` bundle: `<slug>.html` + `<slug>-{graph,clusters,overlays,pages}.json`) to **Cloudflare Pages**, so you can browse it from a phone and so a RAG answer's source links open the original in one tap. `graph.html` loads its data via `fetch`, so a web server is required — opening it as a `file://` double-click does not work.

Cloudflare Pages lets you keep the source repo private while exposing only the built artifact. (GitHub Pages does not enable on a private repo for free accounts — it needs Pro or higher.) If your repo is already public, plain GitHub Pages also works; the steps below assume Cloudflare Pages.

## Prerequisites

- Accept that the entire content (including analyses and syntheses) is exposed at a public URL. The single-file build inlines every body, so partial exposure is not possible. A `noindex` tag plus an unguessable slug only blocks search indexing and casual discovery — it is **not** authentication.
- A free Cloudflare account.

## Steps

### 1. Create the Cloudflare Pages project

Dashboard → **Workers & Pages → Create → Pages → Upload assets** (Direct Upload) → project name (e.g. `wiki-graph`). Create it empty. After creation the production URL is `https://<project-name>.pages.dev`. Set the project's production branch to `main`.

### 2. Set the export constants

Fill in the two deploy constants in [`tools/_lib.py`](../../tools/_lib.py) (there is no separate config file — `export.py` and `_briefing/render.py` import the same definitions):

```python
BASE_URL = 'https://<project-name>.pages.dev'
STANDALONE_SLUG = 'g-7f3a9c2e'   # an unguessable value
```

- `BASE_URL`: the Pages production URL from step 1.
- `STANDALONE_SLUG`: an unguessable filename. e.g. `openssl rand -hex 4` → `g-<hex>`. This value determines both the output filename (`<slug>.html`) and the RAG handoff link template at once, so the two never drift.

### 3. Build and deploy

```bash
python tools/build.py        # refresh graph data
python tools/export.py       # stages _site/ with the <slug>-prefixed obscure filenames
```

`export.py`'s `stage_site()` copies `graph/graph.html` + `_graph.json`·`_clusters.json`·`_overlays.json`·`_pages.json` into `_site/` with a `<slug>-` prefix and injects `<meta robots noindex>` + `window.ASSET_PREFIX="<slug>-"`. The RAG `.md` merge stays in `wiki-export/` only and is **not** placed in `_site/`, so it is never published.

Then upload `_site/` to the Pages project — either via the dashboard (Direct Upload) or the CLI:

```bash
npx wrangler pages deploy _site --project-name <project-name> --branch main
```

(`wrangler` needs a Cloudflare API token with the **"Cloudflare Pages: Edit"** permission and your Account ID, set as `CLOUDFLARE_API_TOKEN` / `CLOUDFLARE_ACCOUNT_ID` env vars. If you prefer CI, wire the same two values as GitHub Actions secrets and add a deploy workflow — not included here by default.)

### 4. Verify access

- Browser: `<BASE_URL>/<slug>` (Cloudflare Pages 308-redirects `.html` to the extension-less URL; use the extension-less form to avoid the redirect dropping the `#q=` fragment).
- Deep link: `<BASE_URL>/<slug>#q=<page-slug>` opens a specific node directly.

## Update

After changing content, re-run `python tools/build.py && python tools/export.py` and re-deploy `_site/`. The RAG merge and the `_site/` deploy assets are regenerated together from the same snapshot.
