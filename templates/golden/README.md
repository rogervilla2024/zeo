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

All commands below run from the new site's root. `$ZEO` is the path
to your toolkit checkout; its Python helpers run through the
toolkit's own environment (`uv run --project "$ZEO/scripts"`).

1. Copy this directory to the new project root:

   ```bash
   export ZEO=~/tools/zeo   # your toolkit checkout
   cp -r "$ZEO/templates/golden" ~/sites/my-site && cd ~/sites/my-site
   ```

2. Edit `site.config.json` - the only file that must change per site.
   Replace every `example.com` and `Example Site` value: name,
   domain, niche, audience, voice, authors, theme palette, and the
   `seo` section (og_image and search_url_template are safe as
   shipped only because they are root-relative paths). Then run the
   design-theme skill: it turns the niche into a real visual identity
   (palette, fonts, variant, `src/styles/site.css` overrides) on top
   of the shipped variant baseline, and the site is not done until
   the visual-review gate passes its screenshots.
3. Regenerate the derived assets from the config:

   ```bash
   uv run --project "$ZEO/scripts" python "$ZEO/scripts/generate_theme_css.py" \
       --config site.config.json --output src/styles/tokens.css
   uv run --project "$ZEO/scripts" python "$ZEO/scripts/generate_logo.py" \
       --name "Site name" --output public/logo.png --background "#0f766e"
   uv run --project "$ZEO/scripts" python "$ZEO/scripts/generate_og_image.py" \
       --title "Site name" --site-name "example.com" --output public/og-image.png
   uv run --project "$ZEO/scripts" python "$ZEO/scripts/generate_favicons.py" \
       --logo public/logo.png --out-dir public --name "Site name" \
       --short-name "Site"
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
   (`$ZEO/scripts/generate_sitemap.py`, or point robots.txt at the
   sitemap your framework integration emits) into `public/`.
8. Build, index search, and gate:

   ```bash
   npm install && npm run build && npm run search:index
   uv run --project "$ZEO/scripts" python "$ZEO/scripts/seo_report.py" \
       --dist dist --history .seo-history.json
   ```

   `search:index` renders the Pagefind index into `dist/pagefind/` -
   the one sanctioned exception to the zero-JS default (it loads only
   on `/search` and is excluded from the JS budget gate).

9. Deploy (Cloudflare Pages; `public/_headers` ships the caching and
   security headers) and re-run the card with the live gates included,
   plus PageSpeed:

   ```bash
   uv run --project "$ZEO/scripts" python "$ZEO/scripts/seo_report.py" \
       --dist dist --live https://example.com --history .seo-history.json
   uv run --project "$ZEO/scripts" python "$ZEO/scripts/check_pagespeed.py" \
       --url https://example.com
   ```

## What is inside

- `site.config.json` - copy of `templates/site.config.example.json`;
  the single source of truth every skill reads.
- `src/layouts/BaseLayout.astro` + `src/components/` - the theme
  layer copied from `templates/theme/` (SEO head, breadcrumbs, footer,
  content blocks, search box, ad slot, newsletter CTA). The one
  exception is `AffiliateLink.astro`, which imports an
  `affiliates.json` this skeleton does not ship - copy the component
  and `templates/affiliates.example.json` together when monetizing.
- `src/pages/` - homepage and blog index (minimal variant), the article
  template with Article + BreadcrumbList + FAQPage JSON-LD, RSS feed,
  noindexed search page, and the five trust-page stubs the Footer
  links to.
- `src/content.config.ts` - blog collection schema; SEO-critical
  frontmatter is required at build time.
- `public/robots.txt` - AI-ready robots template (replace
  `{{SITE_URL}}`).
- `public/_headers` - Cloudflare Pages caching and security headers.
- `src/styles/tokens.css` - design tokens plus the `theme.variant`
  stylesheet, rendered from this directory's `site.config.json`;
  regenerate after editing the config. `src/styles/site.css` is the
  empty niche-identity layer the design-theme skill fills.
