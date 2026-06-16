/* GET /admin/api/files
   Lists the editable docs markdown files (from the GitHub git tree
   on the base branch). Requires a Cloudflare Access identity. */
import { json, accessUser, listDocs } from "./_lib.js";

function meta(path) {
  const parts = path.replace(/\.md$/, "").split("/");
  const slug = parts[parts.length - 1];
  const category = parts.length >= 3 ? parts[parts.length - 2] : parts[0];
  const title = slug.replace(/-/g, " ").replace(/\b\w/g, (m) => m.toUpperCase());
  return { path, category, slug, title };
}

export async function onRequestGet({ request, env }) {
  if (!accessUser(request)) return json({ error: "Not authenticated" }, 401);
  try {
    const paths = await listDocs(env);
    // skip index.md category pages (frontmatter-driven, not prose)
    const files = paths
      .filter((p) => !/\/index\.md$/.test(p))
      .map(meta)
      .sort((a, b) => (a.category + a.slug).localeCompare(b.category + b.slug));
    return json({ files });
  } catch (e) {
    return json({ error: "Could not list files", detail: String(e) }, 502);
  }
}
