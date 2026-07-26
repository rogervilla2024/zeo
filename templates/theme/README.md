# Theme SEO components

Drop-in pieces the bootstrap-site skill copies into every new site so the
theme itself enforces SEO compliance, instead of relying on each page
remembering to do it.

## Files

- `SeoHead.astro` - Astro head component: title with configured suffix,
  meta description, canonical, robots, Open Graph + Twitter card,
  hreflang alternates with x-default, and JSON-LD injection. Reads
  sitewide values from `site.config.json`, per-page values from props.
- `next-metadata.ts` - Next.js App Router equivalent: `buildMetadata()`
  returns the `Metadata` object for a page, and `JsonLd` renders
  structured-data script tags in the body.
- `Breadcrumbs.astro` / `Breadcrumbs.tsx` - visible breadcrumb trail
  with `aria-label` and `aria-current`. Pair with the BreadcrumbList
  JSON-LD from `scripts/build_jsonld.py`; Google shows the breadcrumb
  rich result when the visible trail and the schema agree.
- `Footer.astro` / `Footer.tsx` - sitewide footer linking the trust
  pages (About, Contact, Privacy Policy, Terms, Disclaimer) generated
  by the generate-trust-pages skill from `../pages/`.
- `BaseLayout.astro` - the composition root: tokens.css, SeoHead,
  favicon/manifest/RSS links, skip link, dark-mode toggle (stored
  preference applied before paint), Speculation Rules prerendering,
  and the Footer. Zero framework JavaScript.
- Design tokens: `scripts/generate_theme_css.py` renders `tokens.css`
  from the `theme` section of site.config.json (palette, dark palette,
  fonts, radius, max width). Every component styles itself from these
  custom properties, so sites sharing the skeleton do not share a look.
- Layout variants (`variants/`): `minimal`, `editorial`, `guide`,
  `review` - composition specs implemented on top of BaseLayout. Set
  `theme.variant` in site.config.json.
- Content blocks (all zero-JS or native HTML behavior):
  - `TableOfContents.astro` - anchor list Google can surface as jump
    links
  - `KeyTakeaways.astro` - extractable 3-5 point summary for the top
    of articles
  - `FaqAccordion.astro` - native details/summary; visible text must
    match the FAQPage JSON-LD
  - `ProsCons.astro` / `VerdictBox.astro` - review blocks; visible
    scores must mirror the schema
  - `ArticleMeta.astro` - author link, visible published/updated dates
    (matching the Article schema), reading time
  - `RelatedPosts.astro` - the visible half of the internal-linking
    rule; feed it same-cluster pages
  - `SearchBox.astro` - Pagefind static search; makes the WebSite
    SearchAction real (point it at /search?q={search_term_string})
  - `AdSlot.astro` - AdSense-readiness slot: reserves layout-stable
    space per named slot but renders nothing until `ads.enabled` in
    site.config.json is true and the slot name is listed in
    `ads.slots`. Going live is a config flip plus pasting the ad unit
    (and disclosing the provider via legal.ad_provider on the privacy
    page). Never place a slot above the h1 or between the h1 and the
    first paragraph.

## Rules the theme must keep (framework-independent)

- One `h1` per page; primary content inside `<main>` or `<article>`.
- `<html lang="...">` set from the page language.
- Responsive viewport meta in the base layout.
- Every content image gets descriptive `alt` text and explicit
  `width`/`height` (prevents layout shift, feeds image search).
- Below-the-fold images use `loading="lazy"`; the LCP image does not.
- Each page template ships its JSON-LD (Article + BreadcrumbList for
  content pages) generated and validated by the toolkit scripts.
- The og:image is generated per article with
  `scripts/generate_og_image.py` (1200x630 PNG) and referenced
  absolutely.
- The favicon set and `site.webmanifest` come from
  `scripts/generate_favicons.py` (run once per site from the logo); the
  head includes the four link tags it prints.
- Article pages show an author box (photo, name, role, profile link)
  whose Person entity matches the Article schema's `author.url`
  (see the build-author-entity skill).
- Every article body carries contextual internal links inserted at
  creation time via `scripts/suggest_internal_links.py`; an article
  without internal links does not ship.
- JavaScript budget: content pages ship near-zero JS; the build is
  gated by `scripts/check_js_budget.py` (default 30 KB total). New
  scripts must earn their bytes; prefer native HTML behavior.
- Fonts: default to the system stacks in the tokens. A webfont, if
  added, is self-hosted woff2, preloaded, `font-display: swap`.
- The site ships an RSS feed at `/rss.xml` (BaseLayout advertises it);
  Astro sites use @astrojs/rss fed from the content collection.
- Dark mode respects `prefers-color-scheme` and the user's stored
  toggle choice; both palettes come from the tokens and keep readable
  contrast.

`check_agent_ready.py`, `check_rich_results.py`, and
`check_js_budget.py` test all of the above, so a theme built from these
templates passes the suite by construction.
