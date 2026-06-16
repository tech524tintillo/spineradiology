/* _middleware.js — runs before every Function/asset request.
   In production this is a defence-in-depth check: even though
   Cloudflare Access protects the /admin route at the edge, we
   refuse any /admin request lacking the verified Access header.
   Static assets outside /admin pass straight through. */
export async function onRequest(context) {
  const { request, next } = context;
  const url = new URL(request.url);

  if (url.pathname.startsWith("/admin")) {
    const user = request.headers.get("Cf-Access-Authenticated-User-Email");
    // whoami is allowed through so the SPA can detect "not signed in"
    const isWhoami = url.pathname === "/admin/api/whoami";
    if (!user && !isWhoami) {
      return new Response(
        JSON.stringify({ error: "Cloudflare Access required" }),
        { status: 403, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } }
      );
    }
    // prevent the admin UI from being indexed / cached
    const res = await next();
    const h = new Headers(res.headers);
    h.set("X-Robots-Tag", "noindex, nofollow");
    h.set("Cache-Control", "no-store");
    return new Response(res.body, { status: res.status, headers: h });
  }
  return next();
}
