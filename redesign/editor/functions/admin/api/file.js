/* GET /admin/api/file?path=docs/<cat>/<slug>.md
   Returns the current markdown content from the base branch. */
import { json, accessUser, safeDocPath, getFile } from "./_lib.js";

export async function onRequestGet({ request, env }) {
  if (!accessUser(request)) return json({ error: "Not authenticated" }, 401);
  const url = new URL(request.url);
  const raw = url.searchParams.get("path") || "";
  const path = safeDocPath(raw, env.DOCS_PREFIX || "docs/");
  if (!path) return json({ error: "Invalid path" }, 400);
  try {
    const f = await getFile(env, path, env.BASE_BRANCH);
    return json({ path, content: f.content, sha: f.sha });
  } catch (e) {
    return json({ error: "Could not read file", detail: String(e) }, 502);
  }
}
