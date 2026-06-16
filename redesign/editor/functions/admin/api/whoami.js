/* GET /admin/api/whoami
   Reports environment + identity. In LIVE (Cloudflare) the user
   comes from the Cloudflare Access header — there is no separate
   login step; Access handled email OTP before the request reached
   this Function. */
import { json, accessUser } from "./_lib.js";

export async function onRequestGet({ request }) {
  const user = accessUser(request);
  return json({
    mode: "live",
    authenticated: !!user,
    user,
  });
}
