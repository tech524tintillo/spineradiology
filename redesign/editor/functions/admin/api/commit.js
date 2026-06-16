/* POST /admin/api/commit
   Body: { path, content, message, branch }
   Commits the edited markdown to a NEW branch and opens a PR
   against BASE_BRANCH using the scoped bot token. Never writes
   directly to the base branch; never merges.

   Security boundaries:
     - Cloudflare Access identity required (verified header).
     - path is constrained to docs/**.md (no traversal).
     - branch name is sanitised to a safe slug.
     - the GitHub token is fine-grained: single repo, Contents:RW +
       Pull requests:RW — it CANNOT merge or touch other repos. */
import { json, accessUser, safeDocPath, commitAndPR } from "./_lib.js";

function safeBranch(b) {
  const s = String(b || "").replace(/[^A-Za-z0-9._/-]/g, "-").replace(/^-+|-+$/g, "");
  if (!s || s.length > 120) return null;
  if (!/^edit\//.test(s)) return "edit/" + s; // force the edit/ namespace
  return s;
}

export async function onRequestPost({ request, env }) {
  const user = accessUser(request);
  if (!user) return json({ error: "Not authenticated" }, 401);

  let body;
  try { body = await request.json(); } catch { return json({ error: "Bad JSON" }, 400); }

  const path = safeDocPath(body.path, env.DOCS_PREFIX || "docs/");
  if (!path) return json({ error: "Invalid path" }, 400);
  if (typeof body.content !== "string" || body.content.length === 0)
    return json({ error: "Empty content refused" }, 400);
  if (body.content.length > 500_000)
    return json({ error: "Content too large" }, 413);

  const branch = safeBranch(body.branch);
  if (!branch) return json({ error: "Invalid branch" }, 400);

  const message = (String(body.message || "").trim() || `Edit ${path}`).slice(0, 200);

  try {
    const r = await commitAndPR(env, {
      path, content: body.content, message, branch, author: user,
    });
    return json({ ok: true, ...r });
  } catch (e) {
    return json({ ok: false, error: "Commit failed", detail: String(e), data: e.data || null }, 502);
  }
}
