/* ============================================================
   _lib.js — shared helpers for the SpineRadiology editor
   Cloudflare Pages Functions (production).  NOT DEPLOYED in
   this prototype — kept as files only.  Wiring lives in
   redesign/editor/README.md.

   Environment bindings expected in production (Pages → Settings
   → Environment variables / secrets):
     GITHUB_TOKEN   fine-grained PAT, single repo, Contents:RW + PR:RW
     GITHUB_OWNER   e.g. "kevin-org-or-user"
     GITHUB_REPO    e.g. "spineradiology"
     BASE_BRANCH    e.g. "redesign-templates"   (PR target)
     DOCS_PREFIX    e.g. "docs/"                (path allow-list root)
   Cloudflare Access provides the verified user via the
   Cf-Access-Authenticated-User-Email request header; we never
   trust a client-supplied identity in LIVE mode.
   ============================================================ */

export const GH_API = "https://api.github.com";

export function json(data, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      "Cache-Control": "no-store",
      ...extraHeaders,
    },
  });
}

/* The user is identified by Cloudflare Access. Prefer the plaintext
   Cf-Access-Authenticated-User-Email header; if Access doesn't forward
   it (varies for Pages), fall back to the email claim inside the signed
   Cf-Access-Jwt-Assertion, which Access ALWAYS forwards. Reading the
   claim unverified is safe here because Cloudflare strips any
   client-supplied Cf-Access-* header at the edge — only Access can set
   it — the same trust model the plaintext header already relied on. */
export function accessUser(request) {
  const direct = request.headers.get("Cf-Access-Authenticated-User-Email");
  if (direct) return direct;
  const jwt = request.headers.get("Cf-Access-Jwt-Assertion");
  if (jwt) {
    try {
      const claims = JSON.parse(b64urlDecode(jwt.split(".")[1] || ""));
      if (claims && claims.email) return claims.email;
    } catch { /* fall through */ }
  }
  return null;
}

function b64urlDecode(s) {
  s = s.replace(/-/g, "+").replace(/_/g, "/");
  while (s.length % 4) s += "=";
  const bin = typeof atob === "function" ? atob(s) : Buffer.from(s, "base64").toString("binary");
  try { return decodeURIComponent(escape(bin)); } catch { return bin; }
}

/* Validate that an edit path is inside the docs tree and is a .md
   file with no traversal.  This is the security boundary that keeps
   the bot token from being usable to write arbitrary repo paths. */
export function safeDocPath(path, prefix = "docs/") {
  if (typeof path !== "string") return null;
  const p = path.replace(/^\/+/, "");
  if (p.indexOf("..") !== -1) return null;
  if (!p.startsWith(prefix)) return null;
  if (!p.endsWith(".md")) return null;
  if (!/^[A-Za-z0-9._/-]+$/.test(p)) return null;
  return p;
}

async function gh(env, method, url, body) {
  const res = await fetch(GH_API + url, {
    method,
    headers: {
      "Authorization": `Bearer ${env.GITHUB_TOKEN}`,
      "Accept": "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "spineradiology-editor",
      ...(body ? { "Content-Type": "application/json" } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = { raw: text }; }
  if (!res.ok) {
    const e = new Error(`GitHub ${method} ${url} → ${res.status}`);
    e.status = res.status; e.data = data;
    throw e;
  }
  return data;
}

/* Read a file's current content + blob sha from the base branch. */
export async function getFile(env, path, ref) {
  const r = env.GITHUB_REPO, o = env.GITHUB_OWNER;
  const data = await gh(env, "GET",
    `/repos/${o}/${r}/contents/${encodeURIComponent(path).replace(/%2F/g, "/")}?ref=${encodeURIComponent(ref)}`);
  return {
    sha: data.sha,
    content: typeof atob === "function"
      ? decodeURIComponent(escape(atob(data.content.replace(/\n/g, ""))))
      : Buffer.from(data.content, "base64").toString("utf8"),
  };
}

/* List markdown files in the docs tree (recursive git tree). */
export async function listDocs(env) {
  const r = env.GITHUB_REPO, o = env.GITHUB_OWNER, base = env.BASE_BRANCH;
  const prefix = env.DOCS_PREFIX || "docs/";
  const tree = await gh(env, "GET",
    `/repos/${o}/${r}/git/trees/${encodeURIComponent(base)}?recursive=1`);
  return (tree.tree || [])
    .filter((n) => n.type === "blob" && n.path.startsWith(prefix) && n.path.endsWith(".md"))
    .map((n) => n.path);
}

/* b64 encode utf-8 safely in the Workers runtime. */
function b64(str) {
  if (typeof btoa === "function") return btoa(unescape(encodeURIComponent(str)));
  return Buffer.from(str, "utf8").toString("base64");
}

/* Core: create branch off base, commit the single edited file, open PR.
   Returns { prUrl, branch, commitSha }. */
export async function commitAndPR(env, { path, content, message, branch, author }) {
  const r = env.GITHUB_REPO, o = env.GITHUB_OWNER, base = env.BASE_BRANCH;

  // 1. base branch head sha
  const ref = await gh(env, "GET", `/repos/${o}/${r}/git/ref/heads/${encodeURIComponent(base)}`);
  const baseSha = ref.object.sha;

  // 2. create the edit branch (idempotent-ish: ignore "already exists")
  try {
    await gh(env, "POST", `/repos/${o}/${r}/git/refs`, {
      ref: `refs/heads/${branch}`, sha: baseSha,
    });
  } catch (e) {
    if (!(e.status === 422)) throw e; // 422 = ref exists; reuse it
  }

  // 3. current blob sha on the new branch (needed to update)
  let existingSha = null;
  try {
    const cur = await gh(env, "GET",
      `/repos/${o}/${r}/contents/${path}?ref=${encodeURIComponent(branch)}`);
    existingSha = cur.sha;
  } catch (e) { if (e.status !== 404) throw e; }

  // 4. commit the file onto the branch
  const commit = await gh(env, "PUT", `/repos/${o}/${r}/contents/${path}`, {
    message,
    content: b64(content),
    branch,
    sha: existingSha || undefined,
    committer: { name: "SpineRadiology Editor", email: "editor-bot@spineradiology.com" },
    author: author
      ? { name: author.split("@")[0], email: author }
      : undefined,
  });

  // 5. open the PR (ignore "already exists")
  let prUrl = null;
  try {
    const pr = await gh(env, "POST", `/repos/${o}/${r}/pulls`, {
      title: message,
      head: branch,
      base,
      body: `Automated edit from the SpineRadiology hidden editor.\n\n` +
            `- **File:** \`${path}\`\n- **Editor:** ${author || "unknown"}\n\n` +
            `Review and merge to publish. CI rebuild runs on merge.`,
      maintainer_can_modify: true,
    });
    prUrl = pr.html_url;
  } catch (e) {
    if (e.status === 422 && e.data && /already exists/i.test(JSON.stringify(e.data))) {
      // find existing PR for this head
      const prs = await gh(env, "GET",
        `/repos/${o}/${r}/pulls?head=${o}:${branch}&state=open`);
      if (prs && prs[0]) prUrl = prs[0].html_url;
    } else { throw e; }
  }

  return { prUrl, branch, commitSha: commit.commit && commit.commit.sha };
}
