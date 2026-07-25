---
name: bootstrap-site
description: Scaffold a brand-new, SEO-ready website from just a niche and a domain, following the toolkit's architecture and standards. Use when the user wants to create a new site, start a new website, bootstrap or scaffold a project, says "make a site according to this toolkit", or opens an empty repository intended to become a content site.
---

# Bootstrap a new SEO-ready site

Create a new site that passes the toolkit's test suite from day one:
server-rendered content, AI-ready robots.txt, llms.txt, sitemap, JSON-LD,
and an initial content plan. The site config file written in step 1 is the
single source of truth every other skill reads later.

## Inputs

Gather before scaffolding (ask only for what is missing):

- Niche and audience (one line each).
- Domain (e.g. `https://example.com`) and site/brand name.
- Primary language, plus additional languages if multilingual.
- Framework preference. Default when unstated: a static-first framework
  (Astro or Next.js with static generation). Client-side-only rendering
  is never acceptable: it fails the server-rendered-content check.
- Hosting target. Default: Cloudflare Pages (static build via Git
  integration or wrangler; see templates/deploy/cloudflare.md).

## Instructions

1. Write `site.config.json` at the project root, copied from the
   toolkit's `templates/site.config.example.json` and filled in with the
   gathered values. All later skills (write-article, generate-schema,
   generate-llms-txt, test-site-readiness) read site context from here.
   HARD RULE: from this point on, the niche and every article topic come
   EXCLUSIVELY from site.config.json. Example topics appearing in
   toolkit docs, README samples, or the user's earlier prompts (coffee,
   grinders, etc.) are illustrations only - generating content about
   them when they are not this site's niche is a failure.
2. Scaffold the framework project with its official generator via Bash
   (e.g. `npm create astro@latest`, `npx create-next-app`). Choose the
   static/SSG configuration.
3. Choose the theme path. Default when the user has no preference:
   run the find-theme skill for the niche and propose adopting the top
   ready-made theme (adopt-theme skill) - professional design day one.
   Fall back to the custom path below when no theme fits or the user
   wants a bespoke look.
   Custom path - build the theme from the toolkit's templates (see
   `templates/theme/README.md` for the full rules):
   - generate the design tokens from the config's `theme` section:

     ```bash
     python scripts/generate_theme_css.py --config site.config.json \
         --output src/styles/tokens.css
     ```

   - install `BaseLayout.astro` (tokens, SeoHead, skip link, dark-mode
     toggle, Speculation Rules prerendering, Footer) plus the SEO head
     component (`SeoHead.astro` for Astro, `next-metadata.ts` for
     Next.js)
   - implement the layout variant named by `theme.variant`
     (`templates/theme/variants/`: minimal, editorial, guide, review)
   - wire the content blocks into the article template: ArticleMeta,
     KeyTakeaways, TableOfContents, FaqAccordion, RelatedPosts (plus
     ProsCons and VerdictBox for the review variant)
   - add Pagefind static search (`SearchBox.astro`, `pagefind --site
     dist` appended to the build) and an RSS feed at /rss.xml
   One h1 per page; primary content inside `<main>`/`<article>`;
   `<html lang>` set from the page language.
   Generate the default share card and the favicon set plus manifest
   from the site logo:

   ```bash
   python scripts/generate_og_image.py --title "Site name" \
       --site-name "example.com" --output public/og-image.png
   python scripts/generate_favicons.py --logo logo.png --out-dir public \
       --name "Site name" --short-name "Site"
   ```

   Add the breadcrumb component (templates/theme/Breadcrumbs.astro or
   Breadcrumbs.tsx) to the content-page layout, paired with
   BreadcrumbList JSON-LD. Install the footer (templates/theme/
   Footer.astro or Footer.tsx) in the base layout and run the
   generate-trust-pages skill so About, Contact, Privacy Policy, Terms,
   and Disclaimer exist from day one. If authors are known, register
   them in site.config.json and run the build-author-entity skill.
4. Add sitewide structured data. Generate Organization and
   WebSite+SearchAction JSON-LD with the toolkit scripts and embed them
   in the base layout; wire an Article+BreadcrumbList template into the
   content-page layout:

   ```bash
   python scripts/build_jsonld.py --type organization --input org.json --output org.jsonld
   python scripts/validate_schema.py --input org.jsonld
   ```

5. Copy `templates/robots.txt` into the static assets directory and
   replace `{{SITE_URL}}` with the domain. Review the AI-bot Allow lines
   with the user if they have opinions about training crawlers.
6. Wire the sitemap into the build: the framework's sitemap integration
   if solid, otherwise `scripts/generate_sitemap.py` invoked from the
   build script. Confirm robots.txt points at it.
7. Plan the initial information architecture and write the launch
   content pack. Delegate to the build-topic-clusters skill for a
   pillar and cluster map derived from the site.config.json niche, then
   create the pillar pages and navigation. From that map, select
   `content.launch_articles` topics (default 10): 1-2 pillar guides
   plus basic, beginner-intent cluster articles (the "what is",
   "how to", "common mistakes", "X vs Y" queries of the niche - the
   questions every newcomer searches first). Write every one of them
   through the full write-article pipeline with all gates (FAQ,
   internal links between the pack's articles, AI-pattern lint,
   originality, schema, per-article og-image), in the site's content
   language. The site launches with a filled articles section, never a
   single lonely post or placeholder cards.
8. Generate `llms.txt` with the generate-llms-txt skill once the initial
   pages exist, and place it in the static assets directory.
9. Test before calling it done. Build the site and run the offline
   checks against the build output, then the live checks after deploy:

   ```bash
   python scripts/check_rich_results.py --file dist/index.html
   python scripts/check_js_budget.py --dist dist
   # then run the visual-review skill: build, screenshot at 390/768/1440,
   # critique against the design checklist, fix, re-shoot until it passes
   python scripts/check_agent_ready.py --url https://example.com   # post-deploy
   python scripts/check_pagespeed.py --url https://example.com     # post-deploy
   ```

   Fix failures per the test-site-readiness skill and re-run until green.
10. Initialize git with a first commit. Copy templates/deploy/_headers
    into public/ (immutable asset caching + security headers) and write
    the deploy steps from templates/deploy/cloudflare.md: Git
    integration (build `npm run build`, output `dist`) or
    `npx wrangler pages deploy dist`.

## Output

- A buildable project with: `site.config.json`, SEO head component,
  sitewide and per-template JSON-LD, AI-ready robots.txt, llms.txt,
  sitemap wiring, pillar pages, and passing offline checks.
- A short handoff note: what was scaffolded, test results, deploy steps,
  and which post-deploy checks to run.

## Quality checklist

- `check_rich_results.py --file` passes on the built homepage and one
  content page.
- Built HTML contains the page text (view-source test), not an empty
  JavaScript shell.
- robots.txt names the AI crawlers and points at the sitemap.
- site.config.json exists and matches what was actually scaffolded.
- No secrets in the repository; anything sensitive goes in `.env`
  (gitignored from the start).
