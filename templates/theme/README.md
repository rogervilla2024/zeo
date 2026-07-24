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

`check_agent_ready.py` and `check_rich_results.py` test all of the
above, so a theme built from these templates passes the suite by
construction.
