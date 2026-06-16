#!/usr/bin/env node
/* ============================================================
   demo-server.js — OFFLINE demo for the SpineRadiology editor.

   Zero dependencies (Node ≥ 18). Serves the hidden /admin SPA and
   implements the same API the Cloudflare Pages Functions expose,
   but backed by your LOCAL clone instead of GitHub:

     GET  /admin/api/whoami     → mode:"demo", auth state (cookie)
     POST /admin/api/login      → fake email-OTP sign-in (any 6 digits)
     POST /admin/api/logout
     GET  /admin/api/files      → walks ./docs for *.md
     GET  /admin/api/file?path= → reads a markdown file
     POST /admin/api/commit     → writes the edit to a NEW LOCAL git
                                  branch + opens nothing (prints the
                                  `gh pr create` command), then RETURNS
                                  to your working branch. Your working
                                  tree and the 220 published pages are
                                  never modified.

   It NEVER calls GitHub, never pushes, never deploys, never needs
   any of Kevin's accounts. The commit lands on a local branch named
   edit/<slug>-<stamp> so you can inspect it with `git log` and throw
   it away with `git branch -D`.

   Two commit backends:
     --safe   (DEFAULT) "git stash"-free worktree commit: writes the
              file, commits it on a temp branch via a throwaway index,
              and restores your checkout — your working tree is left
              exactly as it was.
     --dryrun just validates + reports the plan, writes nothing.

   Usage:
     node redesign/editor/server/demo-server.js
     node redesign/editor/server/demo-server.js --port 8799 --dryrun
   ============================================================ */
"use strict";

const http = require("http");
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { execFileSync } = require("child_process");

// ---------- config ----------
const args = process.argv.slice(2);
function flag(name, def) {
  const i = args.indexOf("--" + name);
  if (i === -1) return def;
  const v = args[i + 1];
  return v && !v.startsWith("--") ? v : true;
}
const PORT = parseInt(flag("port", process.env.PORT || "8799"), 10);
const DRYRUN = !!flag("dryrun", false);
const REPO_ROOT = path.resolve(__dirname, "..", "..", ".."); // → spineradiology/
const DOCS_DIR = path.join(REPO_ROOT, "docs");
const ADMIN_DIR = path.resolve(__dirname, "..", "admin");
const DOCS_PREFIX = "docs/";

// crude in-memory session store (demo only)
const SESSIONS = new Map(); // token -> { user }

// ---------- helpers ----------
function sh(args, opts) {
  return execFileSync("git", args, { cwd: REPO_ROOT, encoding: "utf8", ...opts }).trim();
}
function json(res, data, status = 200, headers = {}) {
  const body = JSON.stringify(data);
  res.writeHead(status, {
    "Content-Type": "application/json",
    "Cache-Control": "no-store",
    ...headers,
  });
  res.end(body);
}
function parseCookies(req) {
  const out = {};
  (req.headers.cookie || "").split(";").forEach((c) => {
    const i = c.indexOf("=");
    if (i > -1) out[c.slice(0, i).trim()] = decodeURIComponent(c.slice(i + 1).trim());
  });
  return out;
}
function session(req) {
  const t = parseCookies(req).sr_editor;
  return t && SESSIONS.has(t) ? { token: t, ...SESSIONS.get(t) } : null;
}
function readBody(req) {
  return new Promise((resolve) => {
    let d = "";
    req.on("data", (c) => (d += c));
    req.on("end", () => { try { resolve(JSON.parse(d || "{}")); } catch { resolve({}); } });
  });
}
function safeDocPath(p) {
  if (typeof p !== "string") return null;
  const q = p.replace(/^\/+/, "");
  if (q.indexOf("..") !== -1) return null;
  if (!q.startsWith(DOCS_PREFIX)) return null;
  if (!q.endsWith(".md")) return null;
  if (!/^[A-Za-z0-9._/-]+$/.test(q)) return null;
  return q;
}
function metaFor(rel) {
  const parts = rel.replace(/\.md$/, "").split("/");
  const slug = parts[parts.length - 1];
  const category = parts.length >= 3 ? parts[parts.length - 2] : parts[1] || parts[0];
  // prefer the real H1 title from the file if present
  let title = slug.replace(/-/g, " ").replace(/\b\w/g, (m) => m.toUpperCase());
  try {
    const first = fs.readFileSync(path.join(REPO_ROOT, rel), "utf8")
      .split("\n").find((l) => /^#\s+/.test(l));
    if (first) title = first.replace(/^#\s+/, "").replace(/\s*\(.*$/, "").trim() || title;
  } catch {}
  return { path: rel, category, slug, title };
}
function walkDocs() {
  const out = [];
  (function rec(dir) {
    for (const name of fs.readdirSync(dir)) {
      const full = path.join(dir, name);
      const st = fs.statSync(full);
      if (st.isDirectory()) rec(full);
      else if (name.endsWith(".md") && name !== "index.md") {
        out.push(path.relative(REPO_ROOT, full));
      }
    }
  })(DOCS_DIR);
  return out.sort();
}

// ---------- the demo commit (local branch, non-destructive) ----------
function demoCommit({ relPath, content, message, branch, user }) {
  // sanitise branch
  let b = String(branch || "").replace(/[^A-Za-z0-9._/-]/g, "-");
  if (!/^edit\//.test(b)) b = "edit/" + b;

  if (DRYRUN) {
    return { ok: true, branch: b, note: "dry-run: no branch created", prUrl: null,
      ghCommand: `gh pr create --base redesign-templates --head ${b}` };
  }

  // Work entirely through git plumbing so the user's checkout/working
  // tree is never touched. We build a tree from the current base
  // commit with the single file replaced, then commit it onto a new
  // local branch ref.
  const base = sh(["rev-parse", "HEAD"]);
  const baseBranch = sh(["rev-parse", "--abbrev-ref", "HEAD"]);

  // 1. write the blob
  const blobSha = execFileSync("git", ["hash-object", "-w", "--stdin"], {
    cwd: REPO_ROOT, input: content, encoding: "utf8",
  }).trim();

  // 2. read base tree into a TEMP index, update the one path, write tree
  const tmpIndex = path.join(REPO_ROOT, ".git", "sr-editor-index." + crypto.randomBytes(4).toString("hex"));
  const env = { ...process.env, GIT_INDEX_FILE: tmpIndex };
  try {
    sh(["read-tree", base], { env });
    sh(["update-index", "--add", "--cacheinfo", "100644", blobSha, relPath], { env });
    const treeSha = sh(["write-tree"], { env });

    // 3. commit the tree (parent = base) with the editor identity
    const authorName = "SpineRadiology Editor (demo)";
    const authorEmail = user || "editor@spineradiology.local";
    const commitSha = execFileSync("git",
      ["commit-tree", treeSha, "-p", base, "-m", message],
      { cwd: REPO_ROOT, encoding: "utf8", input: "",
        env: { ...process.env,
          GIT_AUTHOR_NAME: authorName, GIT_AUTHOR_EMAIL: authorEmail,
          GIT_COMMITTER_NAME: authorName, GIT_COMMITTER_EMAIL: authorEmail } }
    ).trim();

    // 4. point the new branch ref at the commit (force = update if exists)
    sh(["update-ref", "refs/heads/" + b, commitSha]);

    return {
      ok: true,
      branch: b,
      commitSha,
      baseBranch,
      prUrl: null,
      note: `committed locally on ${b} (base ${base.slice(0, 7)}); inspect: git show ${b} — discard: git branch -D ${b}`,
      ghCommand: `gh pr create --base redesign-templates --head ${b} --title "${message.replace(/"/g, '\\"')}"`,
    };
  } finally {
    try { fs.unlinkSync(tmpIndex); } catch {}
  }
}

// ---------- static ----------
const MIME = {
  ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8", ".json": "application/json",
  ".svg": "image/svg+xml", ".png": "image/png", ".ico": "image/x-icon",
};
function serveStatic(res, file) {
  fs.readFile(file, (err, buf) => {
    if (err) { res.writeHead(404); res.end("Not found"); return; }
    res.writeHead(200, {
      "Content-Type": MIME[path.extname(file)] || "application/octet-stream",
      "Cache-Control": "no-store",
      "X-Robots-Tag": "noindex, nofollow",
    });
    res.end(buf);
  });
}

// ---------- router ----------
const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, "http://localhost");
  const p = url.pathname;

  // root → /admin/
  if (p === "/" || p === "/admin") { res.writeHead(302, { Location: "/admin/" }); res.end(); return; }

  // ---- API ----
  if (p.startsWith("/admin/api/")) {
    const ep = p.replace("/admin/api/", "");

    if (ep === "whoami") {
      const s = session(req);
      return json(res, { mode: "demo", authenticated: !!s, user: s ? s.user : null });
    }
    if (ep === "login" && req.method === "POST") {
      const b = await readBody(req);
      if (!/^\d{6}$/.test(String(b.otp || ""))) return json(res, { ok: false, error: "Enter any 6-digit code" }, 400);
      const token = crypto.randomBytes(16).toString("hex");
      const user = (b.email || "editor@spineradiology.com").trim();
      SESSIONS.set(token, { user });
      return json(res, { ok: true, user }, 200, {
        "Set-Cookie": `sr_editor=${token}; Path=/; HttpOnly; SameSite=Lax`,
      });
    }
    if (ep === "logout" && req.method === "POST") {
      const s = session(req); if (s) SESSIONS.delete(s.token);
      return json(res, { ok: true }, 200, { "Set-Cookie": "sr_editor=; Path=/; Max-Age=0" });
    }

    // everything below requires a session
    if (!session(req)) return json(res, { error: "Not authenticated" }, 401);

    if (ep === "files") {
      try { return json(res, { files: walkDocs().map(metaFor) }); }
      catch (e) { return json(res, { error: "Could not list files", detail: String(e) }, 500); }
    }
    if (ep === "file") {
      const rel = safeDocPath(url.searchParams.get("path"));
      if (!rel) return json(res, { error: "Invalid path" }, 400);
      try { return json(res, { path: rel, content: fs.readFileSync(path.join(REPO_ROOT, rel), "utf8") }); }
      catch (e) { return json(res, { error: "Could not read file", detail: String(e) }, 500); }
    }
    if (ep === "commit" && req.method === "POST") {
      const b = await readBody(req);
      const rel = safeDocPath(b.path);
      if (!rel) return json(res, { ok: false, error: "Invalid path" }, 400);
      if (typeof b.content !== "string" || !b.content.length) return json(res, { ok: false, error: "Empty content refused" }, 400);
      const s = session(req);
      try {
        const r = demoCommit({
          relPath: rel, content: b.content,
          message: (String(b.message || "").trim() || "Edit " + rel).slice(0, 200),
          branch: b.branch, user: s.user,
        });
        console.log(`  [commit] ${rel} → ${r.branch}${r.commitSha ? " @ " + r.commitSha.slice(0, 8) : ""}`);
        return json(res, r);
      } catch (e) {
        console.error("  [commit] FAILED:", e.message);
        return json(res, { ok: false, error: "Local commit failed", detail: String(e.message || e) }, 500);
      }
    }
    return json(res, { error: "Unknown endpoint" }, 404);
  }

  // ---- static admin assets ----
  if (p.startsWith("/admin/")) {
    let rel = p.replace("/admin/", "");
    if (rel === "" ) rel = "index.html";
    // prevent traversal out of admin dir
    const file = path.normalize(path.join(ADMIN_DIR, rel));
    if (!file.startsWith(ADMIN_DIR)) { res.writeHead(403); res.end("Forbidden"); return; }
    return serveStatic(res, fs.existsSync(file) && fs.statSync(file).isFile() ? file : path.join(ADMIN_DIR, "index.html"));
  }

  res.writeHead(404); res.end("Not found");
});

// ---------- preflight ----------
function preflight() {
  if (!fs.existsSync(DOCS_DIR)) {
    console.error(`\n  ✗ docs/ not found at ${DOCS_DIR}\n    Run this from inside the spineradiology clone.\n`);
    process.exit(1);
  }
  try { sh(["rev-parse", "--git-dir"]); }
  catch { console.error("\n  ✗ Not a git repo — local commit demo needs git.\n"); process.exit(1); }
}

preflight();
server.listen(PORT, () => {
  const n = walkDocs().length;
  console.log(`\n  ◇  SpineRadiology editor — DEMO server`);
  console.log(`     mode:    ${DRYRUN ? "DRY-RUN (writes nothing)" : "local-branch commit (non-destructive)"}`);
  console.log(`     repo:    ${REPO_ROOT}`);
  console.log(`     docs:    ${n} markdown articles`);
  console.log(`     open:    http://localhost:${PORT}/admin/`);
  console.log(`     sign in: any email + any 6-digit code\n`);
});
