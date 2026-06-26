# Mobile Inbox Setup (Android)

A one-time setup to commit a URL straight from your phone's share sheet into the wiki inbox queue (`raw/_inbox.md`). On the desktop, `/wiki-ingest inbox` then processes the queue.

**Position in the single-queue model** — `_inbox.md` is the shared queue for three channels: mobile, interactive `/wiki-news`, and background auto-enrichment (`/wiki-news --gap --batch`). A mobile entry appends a plain URL with no meta line, and `fetch_inbox.py` gives meta-less entries a `source=mobile` default. The JS shortcut in this guide works regardless of the other channels. The single-queue policy is SoT in [`gap-detection-rollout.md`](gap-detection-rollout.md).

**Architecture** — the mobile side needs no Obsidian or vault sync. HTTP Shortcuts (FOSS) → GitHub Contents API commits directly.

```
phone share sheet → HTTP Shortcuts (JS) → GitHub Contents API
                                              │
                                              ▼
                       <your-username>/<your-repo> · raw/_inbox.md
```

## Prerequisites

- An Android phone (Android 11+)
- The HTTP Shortcuts app (free on the Play Store, FOSS)
- A GitHub fine-grained Personal Access Token

## Step 1: Issue a fine-grained PAT

1. GitHub → Settings → Developer settings → Personal access tokens → **Fine-grained tokens** → "Generate new token"
2. Settings:
   - **Token name**: `mobile-inbox` (for identification)
   - **Expiration**: 6 months (renew on expiry)
   - **Repository access**: "Only select repositories" → select your wiki repo
   - **Repository permissions** → **Contents**: **Read and write**
   - All other permissions: No access (least privilege)
3. Click "Generate token" → copy the token string (shown only once)

## Step 2: Install HTTP Shortcuts + register variables

1. Install "HTTP Shortcuts" from the Play Store (author: Roland Marchand)
2. Open the app → top-left hamburger menu → **Variables**
3. Create these four variables:

| Name | Type | Value | Notes |
|------|------|-------|-------|
| `GH_PAT` | Constant · **Password** | (the token copied in Step 1) | stored encrypted |
| `GH_REPO` | Constant | `<your-username>/<your-repo>` | |
| `GH_PATH` | Constant | `raw/_inbox.md` | |
| `SHARED_URL` | Constant | (leave empty) | **check "Allow Receiving Value from Share Dialog"** + select "text" in the dropdown |

Register `GH_PAT` as the **Password** type (the app stores it encrypted).
`SHARED_URL` is the channel that receives a value from the share dialog — enable the checkbox so a URL coming from the share menu is auto-injected into this variable (the official HTTP Shortcuts mechanism).

## Step 3: Create the shortcut

1. Main screen + button → "Create Shortcut" → **Scripting**
2. **Name**: `Send to Wiki Inbox`
3. **Icon**: anything (e.g. a bookmark)
4. **Description**: leave empty (optional)
5. **Scripting** tab → paste the JS body below:

```javascript
const PAT  = getVariable("GH_PAT");
const REPO = getVariable("GH_REPO");
const PATH = getVariable("GH_PATH");

// SHARED_URL: the value injected by the share dialog (the Step 2 "Allow Receiving Value from Share Dialog" variable).
var url = (getVariable("SHARED_URL") || "").trim();
// When text comes mixed in like "Article title https://...", extract only the first URL.
var m = url.match(/https?:\/\/\S+/);
if (m) url = m[0];

if (!url || !/^https?:\/\//.test(url)) {
    showToast("URL not found in shared text");
    abort();
}

var apiUrl = "https://api.github.com/repos/" + REPO + "/contents/" + PATH;
var headers = {
    "Authorization": "Bearer " + PAT,
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
};

// 1) GET the current file (need its sha + base64 content)
var get = sendHttpRequest(apiUrl, { method: "GET", headers: headers });
if (get.status !== "success") {
    var getCode = get.response ? get.response.statusCode : "(network)";
    showToast("GET failed: " + getCode + (get.networkError ? " · " + get.networkError : ""));
    abort();
}
var file = JSON.parse(get.response.body);
// base64decode returns a Uint8Array → restore to a string with toString()
var decoded = toString(base64decode(file.content.replace(/\n/g, "")));

// Ensure a trailing newline, then append the URL
var newContent = (decoded.charAt(decoded.length - 1) === "\n" ? decoded : decoded + "\n") + url + "\n";

// 2) PUT the updated file
var putHeaders = {
    "Authorization": "Bearer " + PAT,
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "Content-Type": "application/json",
};
var put = sendHttpRequest(apiUrl, {
    method: "PUT",
    headers: putHeaders,
    body: JSON.stringify({
        message: "inbox: append URL from mobile",
        content: base64encode(newContent),
        sha: file.sha,
    }),
});

if (put.status === "success" && (put.response.statusCode === 200 || put.response.statusCode === 201)) {
    showToast("Sent to wiki inbox");
} else {
    var putCode = put.response ? put.response.statusCode : "(network)";
    showToast("PUT failed: " + putCode + (put.networkError ? " · " + put.networkError : ""));
}
```

### Why these JS conventions

HTTP Shortcuts' scripting engine (Rhino-based) is safest with ES5 compatibility. Follow these:

- `sendHttpRequest` — exact name (not `sendHTTPRequest`; mind the casing)
- response shape — `result.status` (success / httpError / networkError) → `result.response.{statusCode, body, headers}`
- `base64encode(str)` — string → base64 string (can pass directly)
- `base64decode(str)` — base64 → returns a **Uint8Array** → restore to a string with `toString(...)` (a common trap)
- `showToast` · `abort` · `getVariable` — camelCase
- use `var` + string concat (`+`) — avoids template literals / spread / `const`, which some Rhino builds may not support

6. **Trigger & Execution Settings** → enable "Enable as Direct Share target" (Android 11+; the shortcut then appears directly in the share sheet).
7. Save

## Step 4: Verify

1. Open any article in your phone browser
2. Share → choose "Send to Wiki Inbox" → confirm the "Sent to wiki inbox" toast
3. On GitHub web, open your repo → `raw/_inbox.md` and confirm a URL line was added
4. On the desktop, `git pull` → run `/wiki-ingest inbox`

## Troubleshooting

| Symptom | Cause / fix |
|------|----------|
| `GET failed: 401` | PAT expired or insufficient permission. Re-issue and update the `GH_PAT` variable |
| `GET failed: 404` | typo in `GH_REPO`/`GH_PATH`, or the repo is private but the PAT belongs to another account |
| `PUT failed: 409` | sha mismatch (rarely, two shares run at once). Share once more and it processes normally |
| no toast | possible permission denial — check that "Display over other apps" is allowed in the Shortcuts app settings |
| URL added to inbox twice | can happen if you share twice in a row. The desktop `fetch_inbox.py` dedups via `_source_map::by_url`, so it fetches only once — no impact |

## Security Notes

- Keep the PAT minimal: fine-grained · single repo · contents:write only. If the phone is lost, revoke it immediately in GitHub Settings.
- HTTP Shortcuts' variable-export feature risks exposing the PAT, so **do not export or share** it.
- If holding a GitHub PAT on a phone conflicts with your security policy, drop this path and fall back to desktop RSS / Web Clipper.
