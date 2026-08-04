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

4. Replace `{{SITE_URL}}` in `public/robots.txt` and
   `public/.well-known/api-catalog`, and `{{DOMAIN}}` in
   `public/_redirects` (www -> apex 301), with the domain.
5. Fill the trust-page stubs (`src/pages/about.astro`, contact,
   privacy-policy, terms-of-service, disclaimer) with the
   generate-trust-pages skill; register authors with
   build-author-entity (the profile pages themselves ship at
   `src/pages/authors/[slug].astro` and render straight from the
   config's `authors` entries - fill name, role, bio, and sameAs).
6. Write the launch content pack (`content.launch_articles` articles)
   through the write-article pipeline into `src/content/blog/` - the
   site never launches with an empty articles section.
7. `sitemap.xml` and `llms.txt` are BUILT IN as dynamic endpoints
   (`src/pages/sitemap.xml.js`, `src/pages/llms.txt.js`): they render
   from the live article list on every build, so they never go stale
   as content grows. Do not hand-write `public/` copies - a static
   file that lists 10 launch articles still lists 10 when the site
   has 100. The generate-llms-txt skill can replace the llms.txt
   endpoint with a hand-curated file when finer control is needed.
8. Build, index search, and gate:

   ```bash
   npm install && npm run build && npm run search:index
   uv run --project "$ZEO/scripts" python "$ZEO/scripts/seo_report.py" \
       --dist dist --history .seo-history.json
   ```

   `search:index` renders the Pagefind index into `dist/pagefind/` -
   the one sanctioned exception to the zero-JS default (it loads only
   on `/search` and is excluded from the JS budget gate).

   Before going live, also clear the launch checklist - it fails
   while any template placeholder, missing asset, or short launch
   pack remains:

   ```bash
   uv run --project "$ZEO/scripts" python "$ZEO/scripts/check_launch_ready.py" \
       --root .
   ```

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

- `CLAUDE.md` - operating rules for any Claude Code session working in
  the site folder: which skill handles which task, and the no-commit-
  while-a-gate-is-red rule. It loads automatically, so the workflow
  survives even when nobody remembers to mention it.
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
  links to. Articles publish at the ROOT (`/<slug>/`, via
  `[...slug].astro`) - short URLs with the keyword right after the
  domain; `/blog/` is only the listing hub, paginated past
  `content.page_size` articles (default 24; /blog/2/, /blog/3/...) so
  it never becomes one enormous page - below the threshold nothing
  changes. A branded, noindexed 404 page ships at `src/pages/404.astro`
  (Cloudflare Pages serves dist/404.html automatically). Renaming the
  search page (e.g. /search -> /arama) means renaming
  `src/pages/search.astro`, updating `seo.search_url_template`, AND
  moving the robots.txt Disallow line - the launch checker blocks the
  halfway state. Static pages win over the
  catch-all route, so /about, /search, and /blog resolve normally.
  Category archives render at `/<seo.category_base>/<category-slug>/`
  (one per distinct `category` frontmatter value); homepage strip
  titles and article breadcrumbs link to them. Set `seo.category_base`
  to a native word on non-English sites (e.g. `kategori`) - just not
  one that collides with an existing top-level page like `blog`.
  `src/lib/slugify.ts` folds accented category names (including
  Turkish dotless i) into ASCII slugs. Author profiles render at
  `/authors/<slug>/` - one per `authors` entry whose `url` starts
  with `/authors/` - with Person JSON-LD, the bio and sameAs links
  from the config, and the author's article list; article bylines
  already point there via `authorUrl`, and every article ends with a
  visible author box (name, role, bio from the matching config
  author) linking to the profile.
- `src/content.config.ts` - blog collection schema; SEO-critical
  frontmatter is required at build time. The optional `category`
  field (the article's pillar from the cluster map) feeds the
  homepage category strips. A second `entities` collection
  (`src/content/entities/`) powers directory sites: attribute-typed
  catalog entries rendered as cards and a comparison table.
- The homepage is archetype-driven via `site_type` in
  site.config.json: `portal` (default - feature card, latest grid,
  category strips), `product` (quick-facts panel and how-it-works
  steps from the `product` config section, hero CTA to the demo),
  `directory` (search hero, entity cards + comparison from the
  entities collection, grouped by the first facet past a dozen
  entries), or `forum` (search hero + thread list with answer
  counts). Flip the key and rebuild - no template surgery. The
  archetype is a default, not a cage: `homepage.blocks` composes
  the whole homepage from 8 orderable blocks on any site_type -
  lead zone `quick_facts` / `how_to` / `directory` / `comparison`
  (full width), main zone `threads` / `feature` / `latest` /
  `strips` (article column) - e.g. a hotel portal adds
  `["directory", "feature", "latest"]` to get the booking surface
  without switching archetypes; an empty list keeps the archetype's
  default and unknown ids are ignored. A block id takes an optional
  `:style` view modifier (`directory:list`, `feature:overlay`,
  `feature:split`, `latest:rows`); the design-theme skill's
  recipes.md names ready-made block orders (B1-B12). Functional
  blocks: `cta_banner` (homepage.cta_banner config; external offer
  links render rel="sponsored nofollow noopener" unless sponsored is
  explicitly false), `newsletter` (renders only when
  config.newsletter.enabled), and `faq` (homepage.faq Q/A pairs,
  mirrored 1:1 into FAQPage JSON-LD). `theme.category_colors` gives
  each category an accent chip on strips and archive headings.
  Page ANATOMY is config too: `homepage.hero` (standard / search /
  compact / none - the h1 stays, visually hidden), `homepage.aside`
  (right / left / none), `header.search` (search bar in the chrome
  on every page), the `feed` block (single-column stream), and
  `directory:shelves` (horizontal scroll shelves) - named presets in
  design-theme recipes.md (A1-A6).
  `theme.variant` picks one of 40 full themes (catalog:
  design-theme variants.md) over the shared component layer - each
  ships its own palette (light+dark), font pairing, and radius;
  empty `theme.palette`/`fonts`/`radius` keys mean "the theme's
  identity" and config overrides only what the site sets.
  `homepage.hero_stats: true` renders a build-time stat line in the
  hero from real counts (entities, first-facet values, articles)
  via the `ui.stat_*` templates. Facet archives additionally
  carry ItemList JSON-LD naming each entry.
  `EmbedFrame.astro` hosts third-party demos on a dedicated page
  (e.g. `/demo/`), never the homepage. Directory entities carry
  `images` (gallery), `price`, an affiliate `cta_url`, and an
  editorial `rating` (surfaced on cards as the editor's score with
  a visible offer CTA button; `badge` is a differentiator like
  "Editor's pick", never the grouping facet); when an
  article is an entity's review, the article page opens with the
  booking-style `EntityPanel` (gallery, attributes, price, offer
  CTA, rel="sponsored nofollow"). Forum threads are articles with
  `replies` frontmatter - rendered as an answer thread and mirrored
  in QAPage JSON-LD; answers are editorial and truthfully
  attributed, never fabricated community members.
- `public/robots.txt` - AI-ready robots template (replace
  `{{SITE_URL}}`).
- `public/_headers` - Cloudflare Pages caching and security headers.
- `public/_redirects` - www -> apex 301 (replace `{{DOMAIN}}`), so
  exactly one host serves content.
- `src/pages/sitemap.xml.js` + `src/pages/llms.txt.js` - dynamic
  sitemap and llms.txt rendered from the article list on every
  build; they cannot go stale. `src/pages/api/articles.json.js` is
  the site's read API for agents (full article index as JSON), and
  `public/.well-known/api-catalog` (RFC 9727; replace `{{SITE_URL}}`)
  advertises it - the homepage's Link headers (`public/_headers`)
  point there. Directory sites also get facet
  archives at `/<directory.base>/<facet>/<value>/` (e.g.
  `/hotels/region/coast/`) - one pre-rendered, crawlable page per
  attribute value listed in `directory.facets`, the zero-JS answer
  to filtering; the homepage links them as chips.
- `src/styles/tokens.css` - design tokens plus the `theme.variant`
  stylesheet, rendered from this directory's `site.config.json`;
  regenerate after editing the config. `src/styles/site.css` is the
  empty niche-identity layer the design-theme skill fills.
