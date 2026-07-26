# Newsletter endpoint on Cloudflare Workers

The NewsletterCta.astro block is a plain HTML form that POSTs to
`newsletter.action` from site.config.json. This worker is the matching
endpoint: it validates the submission, drops honeypot spam, stores the
address in Workers KV, and redirects back to a thank-you URL - no
JavaScript on the site, no third-party embed.

## Worker

```js
// worker.js - newsletter subscribe endpoint (zero-JS form handler).
// POST form fields: email (required), website (honeypot, must be empty).

const SUCCESS_URL = "/subscribed";
const ERROR_URL = "/subscribe-error";

export default {
  async fetch(request, env) {
    if (request.method !== "POST") {
      return new Response("Method not allowed", { status: 405 });
    }
    const form = await request.formData();
    const email = (form.get("email") || "").toString().trim().toLowerCase();
    const honeypot = (form.get("website") || "").toString();

    // Bots fill the hidden field; humans cannot see it. Pretend success.
    if (honeypot !== "") {
      return Response.redirect(new URL(SUCCESS_URL, request.url), 303);
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return Response.redirect(new URL(ERROR_URL, request.url), 303);
    }

    // Store with a timestamp; overwriting an existing key keeps the
    // list deduplicated for free.
    await env.SUBSCRIBERS.put(email, new Date().toISOString());

    // Optional: forward to a provider (Buttondown, Mailchimp, Listmonk)
    // instead of - or in addition to - KV:
    // await fetch("https://api.buttondown.email/v1/subscribers", {
    //   method: "POST",
    //   headers: {
    //     Authorization: `Token ${env.BUTTONDOWN_TOKEN}`,
    //     "Content-Type": "application/json",
    //   },
    //   body: JSON.stringify({ email }),
    // });

    return Response.redirect(new URL(SUCCESS_URL, request.url), 303);
  },
};
```

## wrangler.toml

```toml
name = "newsletter"
main = "worker.js"
compatibility_date = "2026-01-01"

kv_namespaces = [
  { binding = "SUBSCRIBERS", id = "<kv-namespace-id>" }
]

[[routes]]
pattern = "example.com/api/subscribe"
zone_name = "example.com"
```

Create the KV namespace once with `npx wrangler kv namespace create
SUBSCRIBERS`, paste the id above, then `npx wrangler deploy`.

## Wiring the site

1. Set in site.config.json (and keep `legal.has_newsletter` true so
   the privacy page discloses the signup):

   ```json
   "newsletter": { "enabled": true, "action": "/api/subscribe" }
   ```

2. Add static `/subscribed` and `/subscribe-error` pages so the
   redirects land on real content (a one-line confirmation each).
3. Export the list anytime:
   `npx wrangler kv key list --binding SUBSCRIBERS`.

## Rules

- Double opt-in where the audience's jurisdiction expects it (GDPR):
  send a confirmation email via the provider before adding the
  address to any sending list. KV storage alone is a signup record,
  not consent to arbitrary mail.
- The form stays zero-JS: progressive enhancement is allowed, but the
  plain POST must always work.
- Never buy, import, or merge third-party lists.
