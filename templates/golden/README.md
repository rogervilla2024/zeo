# Golden template

The stored "perfect output" of `/new-site`: a complete, minimal-variant
Astro site that passes the toolkit's offline gates by construction.
Bootstrapping a new site is a copy plus a `site.config.json` change -
no scaffolding decisions, no drift between sites.

The theme files under `src/layouts/` and `src/components/`, plus
`public/robots.txt`, `public/_headers`, and `site.config.json`, are
byte-identical copies of their sources under `templates/` (enforced by
`scripts/tests/test_golden_template.py`). Improve the originals, re-copy
here, and the test keeps the two in sync.

## Use it

1. Copy this directory to the new project root:

   ```bash
   cp -r templates/golden ~/sites/my-site && cd ~/sites/my-site
   ```

2. Edit `site.config.json` - the only file that must change per site
   (name, domain, niche, audience, voice, authors, theme palette).
3. Regenerate the derived assets from the config:

   ```bash
   python scripts/generate_theme_css.py --config site.config.json \
       --output src/styles/tokens.css
   python scripts/generate_logo.py --name "Site name" \
       --output public/logo.png --background "#0f766e"
   python scripts/generate_og_image.py --title "Site name" \
       --site-name "example.com" --output public/og-image.png
   python scripts/generate_favicons.py --logo public/logo.png \
       --out-dir public --name "Site name" --short-name "Site"
   ```

4. Replace `{{SITE_URL}}` in `public/robots.txt` with the domain.
5. Fill the trust-page stubs (`src/pages/about.astro`, contact,
   privacy-policy, terms-of-service, disclaimer) with the
   generate-trust-pages skill; register authors with
   build-author-entity.
6. Write the launch content pack (`content.launch_articles` articles)
   through the write-article pipeline into `src/content/blog/` - the
   site never launches with an empty articles section.
7. Generate `llms.txt` (generate-llms-txt skill) and the sitemap
   (`scripts/generate_sitemap.py`, or point robots.txt at the sitemap
   your framework integration emits) into `public/`.
8. Build and gate:

   ```bash
   npm install && npm run build
   python scripts/seo_report.py --dist dist --history .seo-history.json
   ```

   Optional static search: `npm run search:index` renders the Pagefind
   index into `dist/pagefind/`. Run it after `seo_report.py`, or raise
   `check_js_budget.py --max-kb` accordingly - Pagefind's UI script is
   the one sanctioned exception to the zero-JS default and loads only
   on `/search`.

9. Deploy (Cloudflare Pages; `public/_headers` ships the caching and
   security headers) and re-run the card with the live gates included,
   plus PageSpeed:

   ```bash
   python scripts/seo_report.py --dist dist \
       --live https://example.com --history .seo-history.json
   python scripts/check_pagespeed.py --url https://example.com
   ```

## What is inside

- `site.config.json` - copy of `templates/site.config.example.json`;
  the single source of truth every skill reads.
- `src/layouts/BaseLayout.astro` + `src/components/` - the full theme
  layer copied from `templates/theme/` (SEO head, breadcrumbs, footer,
  content blocks, search box).
- `src/pages/` - homepage and blog index (minimal variant), the article
  template with Article + BreadcrumbList + FAQPage JSON-LD, RSS feed,
  noindexed search page, and the five trust-page stubs the Footer
  links to.
- `src/content.config.ts` - blog collection schema; SEO-critical
  frontmatter is required at build time.
- `public/robots.txt` - AI-ready robots template (replace
  `{{SITE_URL}}`).
- `public/_headers` - Cloudflare Pages caching and security headers.
- `src/styles/tokens.css` - design tokens rendered from this
  directory's `site.config.json`; regenerate after editing the config.
