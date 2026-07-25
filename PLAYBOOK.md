# Operating playbook

The standard loop for running any site built with this toolkit. Every
site in the portfolio follows the same cadence, so quality is a process
property, not a per-site effort.

## Once, per new site

1. `/new-site "<niche>" https://domain <lang>` - scaffold to standard:
   site.config.json, SSG framework, theme components (SeoHead,
   Breadcrumbs, Footer), validated JSON-LD, AI-ready robots.txt,
   llms.txt, sitemap wiring, og-image, favicon set + manifest, and the
   trust pages (About, Contact, Privacy Policy, Terms, Disclaimer via
   generate-trust-pages).
2. The bootstrap includes the launch content pack: `content.launch_articles`
   (default 10) beginner-intent articles from the cluster map, all gates
   applied, before the site is called done.
3. Register authors (`build-author-entity`) so every byline resolves to
   a real Person entity.
4. Copy `templates/ci/seo-audit.yml` into the site repo and replace
   `{{SITE_URL}}` - the site now audits itself weekly and opens an
   issue when a suite fails.
5. Deploy to Cloudflare Pages (templates/deploy/cloudflare.md: Git
   integration or wrangler; _headers file in place), then run the live
   checks once:
   `check_agent_ready.py`, `check_pagespeed.py` against the live URL.
6. Submit the sitemap in Google Search Console and Bing Webmaster
   Tools. Ranking and query data is tracked directly in Search Console
   by the operator.

## Weekly, per site

1. Produce content at the cadence in site.config.json
   (`content.articles_per_week`) with `/write-blog`. The pipeline
   enforces, per article:
   - FAQ block (3-5 PAA-derived questions + FAQPage schema)
   - contextual in-body internal links (`suggest_internal_links.py`,
     ship-blocking) plus reverse links from older articles
   - humanize pass gated by `check_ai_patterns.py` (banned phrases fail)
   - originality gate: `check_originality.py` against the site's own
     published articles
   - fact-check with citations; schema validated before embed
   - a per-article og:image (`generate_og_image.py`)
2. Regenerate the sitemap (with image entries) and llms.txt when pages
   were added.
3. For multilingual sites, localize the week's best performer with
   `translate-article` rather than translating everything.

## Monthly, per site

1. Review the CI audit issues; run `/seo-test` to fix and re-test
   anything red.
2. Review Search Console for pages with declining clicks or position
   (the operator exports or pastes the data) and queue the worst ones
   for `refresh-content`.
3. Check internal-link health after the month's growth: orphaned new
   pages get reverse links (`internal-link-strategist`).

## Quarterly, per site

1. Re-run `build-topic-clusters` against the niche: the SERP moves;
   the cluster map should absorb new subtopics and retire dead ones.
2. Refresh the top 5 traffic pages with `refresh-content` even if not
   yet declining - staying current beats recovering.
3. Re-check `check_agent_ready.py`: agent standards (llms.txt,
   content-signals, markdown negotiation) are still moving; adopt what
   became standard since last quarter.

## Toolkit rules

- One clear niche angle per site; the strategist keeps every article
  inside it so topical authority compounds.
- The toolkit repo is the single source of process; sites do not fork
  their own variants of skills or scripts. Improvements land here and
  every site benefits on its next session.

## Policy guard (Google spam policies, mapped to our gates)

- Scaled content abuse: bulk pages made for rankings. Prevented by
  content.max_batch, the weekly_ramp pace, and the four article gates.
- Doorway pages: near-duplicate pages per keyword variation. Prevented
  by the one-comprehensive-article rule and the originality gate.
- Thin/unoriginal content: prevented by word-depth targets,
  fact-checking, and check_originality.py.
- Site reputation abuse: hosting third-party content to trade on the
  site's authority - out of scope by design; do not add it.
- Every visible claim matches its schema (ratings, dates, authors);
  schema-only data is a policy risk, not a shortcut.
