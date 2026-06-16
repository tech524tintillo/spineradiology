# SpineRadiology Content Editor — prototype

A hidden `/admin` web editor that lets a non-technical editor change article
text and have it land as a **branch + pull request** against the docs Markdown —
the actual source of truth — without ever touching the published pages directly.

> **Status:** prototype. The frontend and the Cloudflare Pages Functions are
> finished code; nothing here is deployed. A zero-dependency **local demo**
> lets you try the whole UX tonight, offline, against your local clone, using
> none of your real accounts.

This implements **Approach 2** from the spec: Cloudflare Access email-OTP on a
hidden `/admin`, plus a Pages Function that commits edited docs Markdown to
GitHub via one scoped bot token, branch-plus-PR.

---

## Why this is safe to drop in

Everything is self-contained under `redesign/editor/` and **non-destructive**:

- It does **not** modify the 220 article pages, the built `site/`, the
  approved Emily templates, `mkdocs.yml`, or the existing Worker.
- The admin UI lives at a **separate `/admin` path** and is `noindex`.
- The editor edits **`docs/<category>/<slug>.md`** (the Markdown source MkDocs
  builds from) — the correct source of truth — never the generated HTML.
- Writes go to a **new branch + PR**; nothing merges automatically, nothing is
  pushed or deployed by the prototype.

---

## What's in here

```
redesign/editor/
├── README.md                       ← you are here
├── package.json                    ← npm scripts (demo / clean)
│
├── admin/                          ← the hidden SPA (static files)
│   ├── index.html                  ← app shell + login gate + save modal
│   └── assets/
│       ├── editor.css              ← dark-teal "Emily" theme
│       ├── editor.js               ← SPA logic (auth, tree, edit, save→PR)
│       └── marked.min.js           ← tiny offline Markdown renderer (preview)
│
├── functions/                      ← Cloudflare Pages Functions (PRODUCTION — not deployed)
│   ├── _middleware.js              ← refuses /admin without a verified Access identity
│   └── admin/api/
│       ├── _lib.js                 ← GitHub helpers: list / read / commit+PR
│       ├── _example.dev.vars       ← example env (NO real token — see "Going live")
│       ├── whoami.js               ← GET  identity + mode
│       ├── files.js                ← GET  list editable docs
│       ├── file.js                 ← GET  one file's markdown
│       └── commit.js               ← POST commit edit → branch → PR
│
└── server/                         ← LOCAL demo only (never deployed)
    ├── demo-server.js              ← serves the SPA + a local-clone API
    └── clean-demo-branches.js      ← deletes the demo's edit/* branches
```

The **same SPA** runs against both backends. It calls `GET /admin/api/whoami`
to discover whether it's in `demo` (local server) or `live` (Cloudflare) mode
and adapts the badge + sign-in accordingly.

---

## Try the demo locally (tonight, no accounts)

Requires only **Node ≥ 18** and that you run it from inside this clone (it uses
your local `git` and the `docs/` folder). Nothing leaves your machine.

```bash
cd /Users/light/Downloads/spineradiology/redesign/editor
npm run demo                 # → http://localhost:8799/admin/
```

Then in the browser:

1. **Sign in** with any email and **any 6-digit code** (the demo simulates
   Cloudflare Access email-OTP; no email is sent).
2. Pick an article from the left (all 220 docs, grouped by category; `⌘K` to
   filter).
3. Edit the Markdown on the left — the right pane live-previews in the site's
   dark-teal theme.
4. Click **Save & open PR** (or `⌘S`), confirm the commit message.

### What the demo's "commit" actually does

Instead of calling GitHub, the demo writes your edit to a **new local git
branch** named `edit/<slug>-<timestamp>`, built entirely through git plumbing
(`hash-object` → a throwaway index → `commit-tree` → `update-ref`). Your
checkout, working tree, and the published files are **never touched**.

The success toast shows you exactly how to inspect or discard it:

```bash
git show edit/cervical-vertebrae-20260616-0705      # see the commit + diff
git branch -D edit/cervical-vertebrae-20260616-0705 # throw it away
```

Clean up everything the demo created at once:

```bash
npm run clean:branches        # deletes all local edit/* branches
```

Prefer it to write *nothing at all*? Run the read-only variant — it validates
and shows the plan (including the `gh pr create` command it would run) without
creating a branch:

```bash
npm run demo:dryrun           # node server/demo-server.js --dryrun
```

Options: `--port <n>` (default 8799), `--dryrun`.

---

## How it maps to production (not wired here)

In production the **exact same `/admin` SPA** is served by Cloudflare Pages, and
the `functions/` directory becomes live Pages Functions:

| Local demo                         | Production                                   |
|------------------------------------|----------------------------------------------|
| `server/demo-server.js` fake OTP   | **Cloudflare Access** email-OTP at the edge  |
| session cookie                     | `Cf-Access-Authenticated-User-Email` header  |
| commit → local `edit/*` branch     | `functions/.../commit.js` → GitHub branch+PR |
| reads local `docs/`                | reads repo via GitHub API on `BASE_BRANCH`   |

Security boundaries already coded in `functions/`:

- `_middleware.js` rejects any `/admin` request lacking a verified Access
  identity (defence-in-depth behind Access itself).
- `safeDocPath()` constrains every edit to `docs/**.md` (no traversal, no
  arbitrary repo paths) — so even a leaked token can't write outside docs.
- Branch names are forced into the `edit/` namespace; empty/oversized content
  is refused; commits never target the base branch and never merge.

---

## Going live (production steps — do NOT run from this prototype)

These are the spec's production steps, in order. None are performed here.

1. **Rotate the exposed token** and mint a **repo-scoped fine-grained PAT**
   (single repo, *Contents: Read/Write* + *Pull requests: Read/Write* only).
2. **Migrate deploy to Cloudflare Pages** with Git integration; make the CI
   build reproducible (this replaces the current Worker `[assets]` deploy).
   The one remaining gap vs. the demo is the **CI rebuild on merge** — that is
   production wiring, not part of this prototype.
3. **Stand up Cloudflare Access** (email-OTP policy) on `/admin`, and use
   **branch-plus-PR with preview deployments**.

Then set these on the Pages project (Settings → Environment variables /
secrets — never commit them; `functions/admin/api/_example.dev.vars` shows the
shape):

```
GITHUB_TOKEN   = <fine-grained PAT, single repo, Contents:RW + PR:RW>
GITHUB_OWNER   = <github owner>
GITHUB_REPO    = spineradiology
BASE_BRANCH    = redesign-templates
DOCS_PREFIX    = docs/
```

To run the Functions locally against real GitHub (optional, not needed for the
offline demo): put the same values in a **gitignored** `.dev.vars` at the Pages
project root and run `npx wrangler pages dev redesign/editor/admin --compatibility-date=2026-04-02`.

---

## How to remove it completely

It is fully self-contained, so removal is a single delete with **zero** impact
on the site, the build, or git history of the articles:

```bash
# 1. stop the demo server if running
pkill -f demo-server.js

# 2. delete any branches the demo created
node redesign/editor/server/clean-demo-branches.js   # or: git branch -D <edit/...>

# 3. delete the editor (this is the only artifact)
rm -rf redesign/editor

# 4. (only if you ever committed this) drop it from the tree
git rm -r redesign/editor && git commit -m "Remove editor prototype"
```

Nothing else references `redesign/editor/`. No build step, Worker, `mkdocs.yml`
entry, or published page depends on it. The temporary git index files the demo
uses live under `.git/` (already gitignored) and are deleted on each commit.
