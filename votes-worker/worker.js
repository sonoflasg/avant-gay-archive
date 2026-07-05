/**
 * Avant Gay Archive — vote counter.
 * Cloudflare Worker + KV. Anonymous thumbs up/down, one vote per entry
 * per IP per day.
 *
 * Deploy (Cloudflare dashboard, no command line needed):
 *   1. Workers & Pages → Create → Worker → paste this file → Deploy
 *   2. Storage & Databases → KV → Create namespace, e.g. "avant-gay-votes"
 *   3. Your worker → Settings → Bindings → Add → KV namespace,
 *      variable name: VOTES, namespace: avant-gay-votes
 *   4. Copy the worker URL into VOTES_URL in scripts/build.py and push.
 */

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json", ...CORS },
  });

export default {
  async fetch(req, env) {
    const url = new URL(req.url);

    if (req.method === "OPTIONS") return new Response(null, { headers: CORS });

    // GET /votes → { "<entry id>": { up: n, down: n }, ... }
    if (url.pathname === "/votes" && req.method === "GET") {
      const counts = (await env.VOTES.get("counts", "json")) || {};
      return json(counts);
    }

    // POST /vote  body: { id: "<entry id>", dir: "up" | "down" }
    if (url.pathname === "/vote" && req.method === "POST") {
      let body;
      try {
        body = await req.json();
      } catch {
        return json({ error: "bad json" }, 400);
      }
      const { id, dir } = body || {};
      if (typeof id !== "string" || id.length === 0 || id.length > 200 ||
          (dir !== "up" && dir !== "down")) {
        return json({ error: "bad request" }, 400);
      }

      // one vote per entry per IP per day
      const ip = req.headers.get("cf-connecting-ip") || "unknown";
      const rlKey = `rl:${ip}:${id}`;
      if (await env.VOTES.get(rlKey)) {
        return json({ error: "already voted" }, 429);
      }
      await env.VOTES.put(rlKey, "1", { expirationTtl: 86400 });

      const counts = (await env.VOTES.get("counts", "json")) || {};
      const c = counts[id] || { up: 0, down: 0 };
      c[dir] += 1;
      counts[id] = c;
      await env.VOTES.put("counts", JSON.stringify(counts));
      return json(c);
    }

    return json({ error: "not found" }, 404);
  },
};
