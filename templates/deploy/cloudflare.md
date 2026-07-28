# Deploying to Cloudflare Pages (default host)

Every site built with this toolkit deploys to Cloudflare Pages as a
static build. Two ways to ship; Git integration is the default.

## Option A: Git integration (recommended)

1. Push the site repository to GitHub.
2. Cloudflare dashboard: Workers and Pages -> Create -> Pages ->
   Connect to Git -> pick the repository.
3. Build settings for Astro:
   - Build command: `npm run build`
   - Build output directory: `dist`
   - Node version: set `NODE_VERSION` env var if the build needs a
     specific one.
4. Every push to main deploys automatically; other branches get
   preview URLs.

## Option B: Direct upload with wrangler

```bash
npm run build
npx wrangler pages deploy dist --project-name <site-name>
```

First run prompts a Cloudflare login; CI can use a
`CLOUDFLARE_API_TOKEN` (store it in the environment, never in the
repository).

## Custom domain

Pages project -> Custom domains -> add the domain. With DNS already on
Cloudflare this is one click and TLS is automatic. Keep exactly one
canonical host: redirect `www` to the apex (or the reverse) under
Bulk Redirects or a redirect rule, matching the `domain` in
site.config.json.

## _headers and _redirects

Cloudflare Pages reads two special files from the build output:

- Copy `templates/deploy/_headers` into the static assets directory
  (`public/`) so it lands in `dist/`. It sets immutable caching for
  hashed assets and the security headers.
- `_redirects` (one rule per line, `source destination code`) handles
  moved URLs: `/old-slug /new-slug 301`. Add entries whenever a slug
  changes so link equity survives.

## Post-deploy checks

```bash
python scripts/check_agent_ready.py --url https://example.com
python scripts/check_pagespeed.py --url https://example.com
```

Then submit the sitemap in Google Search Console and Bing Webmaster
Tools. Search Console tracking stays with the operator.

## Notes

- Static output needs no adapter. If a site ever needs server-side
  routes, add `@astrojs/cloudflare` and re-run the test suite.
- Cloudflare's CDN and early hints generally improve field CWV; the
  JS budget and image rules still decide the outcome.

## Cloudflare AI Crawl Control vs. the site's robots.txt

The zone-level "AI Scrapers & Crawlers" / "Manage robots.txt" feature
PREPENDS a managed block to the served robots.txt that disallows
GPTBot, ClaudeBot, CCBot and friends - directly contradicting this
toolkit's AI-ready robots template below it. Which rule wins is
crawler-dependent, so the crawl policy becomes undefined. Turn the
managed robots.txt off (zone -> Settings -> AI Crawl Control) or
align it with the site's policy. The `robots-conflict` live gate
(`seo_report.py --live`) fetches the SERVED robots.txt and fails
while the conflict exists, so a panel change can never silently
reintroduce it.

Also upload `public/_redirects` with `{{DOMAIN}}` replaced so www
301s to the apex - one host, one set of URLs.

## Markdown for Agents

Enable the zone's "Markdown for Agents" feature (AI Crawl Control
area) so requests carrying `Accept: text/markdown` get a markdown
rendering of the HTML while browsers keep getting HTML. Static
hosting cannot do this content negotiation itself; the edge does.
The agent-ready gate's markdown-negotiation check turns green once
the toggle is on.

## Redirect direction: www -> apex, never the reverse

The template's canonicals and sitemap all use the APEX domain
(site.config.json's `domain`). `public/_redirects` therefore 301s
www to the apex. Do NOT add a Cloudflare Redirect Rule sending the
apex to www - that makes every canonical URL redirect away from
itself, which search engines treat as a broken canonical. If a scan
reports "redirected to www", find and remove the apex->www rule in
the Cloudflare dashboard (Rules -> Redirect Rules / Bulk Redirects).
