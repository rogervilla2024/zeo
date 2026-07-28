# zeo

A site-agnostic Claude Code toolkit for producing original, SEO-complete
content at scale. It packages specialized subagents, skills, slash
commands, and deterministic Python helpers that cover the full workflow:

    research -> brief -> draft -> humanize -> on-page SEO -> fact-check ->
    schema/rich results -> internal linking -> XML sitemaps -> GEO/AEO ->
    test (agent-readiness / PageSpeed / rich results / JS budget /
    visual review) -> fix -> re-test

Nothing here is tied to a specific website or niche. Every agent, skill,
and command takes the target site (domain, niche, audience, brand voice)
as input, so the same toolkit drives one site or a hundred. This directory
is self-contained and can be lifted out into its own repository unchanged.

## What is inside

Subagents (`agents/`, 15) - focused specialists the main agent delegates to:

- `seo-content-strategist` - pillar/cluster maps, editorial calendar, KPIs
- `keyword-researcher` - intent classification, SERP difficulty, clustering
- `serp-competitor-analyst` - content-gap and differentiation analysis
- `content-brief-architect` - detailed writer briefs from a keyword + SERP
- `longform-writer` - original 2000-3000+ word articles from a brief
- `content-humanizer` - removes AI-tell patterns, adds natural voice
- `fact-checker` - verifies claims and adds authoritative citations
- `onpage-seo-optimizer` - title/meta/headings/slug/alt/links per page
- `technical-seo-auditor` - evidence-based audit with a prioritized plan
- `schema-engineer` - schema.org JSON-LD for rich results
- `geo-aeo-optimizer` - structure content to be cited by AI answer engines
- `internal-link-strategist` - site architecture and internal linking
- `sitemap-engineer` - XML/news/image sitemaps and sitemap indexes
- `site-readiness-tester` - runs the objective test suites and drives
  fixes in the codebase until they pass
- `site-bootstrap-architect` - scaffolds brand-new SEO-ready sites that
  pass the checks from day one

Skills (`skills/`, 22) - workflows that auto-trigger from natural language
and orchestrate the subagents:

- `write-article` (flagship, full pipeline), `humanize-content`,
  `fact-check`, `optimize-onpage-seo`, `audit-technical-seo`,
  `build-topic-clusters`, `content-calendar`, `mine-questions`,
  `optimize-geo-aeo`, `generate-schema`, `generate-sitemap`,
  `generate-llms-txt`, `test-site-readiness`, `bootstrap-site`,
  `optimize-images`, `generate-article-images`, `build-author-entity`,
  `translate-article`, `refresh-content`, `generate-trust-pages`,
  `design-theme`, `visual-review`

Themes are never adopted from third-party ecosystems: the
`design-theme` skill designs each site's visual identity from its
niche on top of the shipped variant stylesheets, and the
`visual-review` gate blocks "done" until the screenshots pass - so
every site looks distinct, topical, and finished by construction.

Four gates are mandatory for every article: an FAQ block (3-5
PAA-derived questions mirrored in FAQPage schema), contextual in-body
internal links inserted at creation time (`suggest_internal_links.py`),
a passing AI-pattern lint (`check_ai_patterns.py` - banned phrases are
ship-blocking), and a passing originality check against the site's own
published articles (`check_originality.py`). An article failing any gate
does not ship. `PLAYBOOK.md` describes the full operating cadence
(weekly content, monthly audits and refreshes, quarterly cluster
reviews).

Commands (`commands/`, 8) - explicit entry points:

- `/new-site`, `/write-blog`, `/audit-seo`, `/content-brief`,
  `/competitor-analysis`, `/seo-schema`, `/seo-sitemap`, `/seo-test`

Templates (`templates/`) - deterministic starting points the
bootstrap-site skill copies into new projects:

- `site.config.example.json` - the per-site context file (niche, voice,
  languages, schema defaults) that every skill reads
- `golden/` - the stored perfect `/new-site` output: a complete
  minimal-variant Astro site that passes the offline gates by
  construction, so a new site is a copy of this directory plus a
  site.config.json change; its theme copies are kept byte-identical to
  `theme/` by `scripts/tests/test_golden_template.py`
- `robots.txt` - AI-ready robots template with every major AI crawler
  named explicitly and a Sitemap directive
- `theme/` - the full theme layer: design tokens rendered from
  site.config.json (`generate_theme_css.py`), `BaseLayout.astro` with
  the speed patterns baked in (zero-JS default, Speculation Rules
  prerendering, dark mode, skip link), the SEO head components
  (`SeoHead.astro`, `next-metadata.ts`), Breadcrumbs and Footer, eleven
  zero-JS content blocks (TableOfContents, KeyTakeaways, FaqAccordion,
  ProsCons, VerdictBox, ArticleMeta, RelatedPosts, Pagefind SearchBox,
  AdSlot, NewsletterCta, AffiliateLink),
  and four layout variants shipped as finished stylesheets
  (`variants/*.css`, appended to tokens.css by
  `generate_theme_css.py`: minimal, editorial, guide, review) so no
  site can render unstyled, and the design-theme skill layers a
  niche-specific identity on top so sites sharing the skeleton do
  not share a look
- `ci/seo-audit.yml` - GitHub Actions workflow for site repos: weekly
  cron runs the three checkers against the live site and opens or
  updates an issue when any suite fails, so every site polices itself
- `deploy/` - Cloudflare Pages deployment (the default host): setup
  guide for Git integration and wrangler direct upload, plus a
  `_headers` file with immutable asset caching and security headers
- `pages/` - trust-page templates (About, Contact, Privacy Policy,
  Terms of Service, Disclaimer) the generate-trust-pages skill fills
  from site.config.json; paired with the `theme/` Footer components
  that link them sitewide

Scripts (`scripts/`) - a small, tested Python package the skills call so
output is deterministic and standards-correct:

- `build_jsonld.py` - build JSON-LD for Article, FAQ, HowTo, Breadcrumb,
  Organization, WebSite SearchAction, Product, Recipe, VideoObject,
  Event, Person (author entities), LocalBusiness (subtypes supported),
  JobPosting (on-site and remote), Course, SoftwareApplication, and
  Speakable (voice/AEO section markup)
- `validate_schema.py` - check JSON-LD for required/recommended properties
- `generate_sitemap.py` - build sitemaps with hreflang, Google image
  sitemap entries, and 50k splitting
- `generate_llmstxt.py` - build an llms.txt (llmstxt.org standard)
- `suggest_internal_links.py` - mandatory smart internal linking: finds
  natural anchor phrases in body paragraphs (never headings, code, or
  existing links), one link per target, capped density, `--apply` mode
- `generate_favicons.py` - full favicon set plus site.webmanifest from
  one logo, with the head snippet to paste
- `check_ai_patterns.py` - deterministic AI-tell lint: banned formulaic
  phrases (errors) plus sentence-opener repetition and uniform paragraph
  lengths (warnings)
- `check_originality.py` - shingle-similarity originality gate against
  the site's published articles, with example shared phrases in the
  report
- `generate_theme_css.py` - render tokens.css (palette, dark mode,
  fonts, radius, a11y helpers) from the config's theme section
- `check_js_budget.py` - enforce the theme's JavaScript budget on the
  build output (default 30 KB total; non-zero exit when over)
- `check_agent_ready.py` - agent-readiness score (isitagentready.com
  style): robots.txt AI-bot rules, llms.txt, sitemap, server-rendered
  content, semantic HTML, structured data, markdown negotiation, html
  lang, viewport, og:image, image alt coverage
- `generate_og_image.py` - render 1200x630 Open Graph share cards
  (background, accent, wrapped title, site name) per page or article
- `check_pagespeed.py` - PageSpeed Insights / Core Web Vitals report with
  prioritized opportunities (optional PAGESPEED_API_KEY via .env)
- `check_rich_results.py` - extract and validate all JSON-LD on a live
  page or local HTML file (offline rich-results test)
- `content_calendar.py` - map `content-queue.json` onto dated weeks by
  priority, capped by `content.weekly_ramp` and
  `content.articles_per_week`; markdown calendar out, `--apply` writes
  the week assignments back
- `queue_refresh_candidates.py` - scan the build output for articles
  whose Article JSON-LD freshness date is older than the cutoff
  (default 6 months) and, with `--apply`, append them to
  content-queue.json as refresh items
- `fleet_report.py` - fold every site's `.seo-history.json` (written by
  `seo_report.py`) into one self-contained HTML dashboard: per-site
  gate matrix, score deltas, and trend; exits non-zero when any site
  is red
- `seo_report.py` - one-page score card over the whole gate battery
  with JSON history and deltas per run; offline gates by default,
  plus the live gates (agent-ready, canonical-host) with
  `--live https://domain` after deploy
- `check_article_images.py` - image completeness gate over the content
  collection source: every article needs its hero frontmatter and at
  least `images.min` body images; seo_report.py runs it automatically
  when dist sits next to `src/content/blog/`.
- `check_internal_links.py` - in-body internal link gate over the
  content source (`content.min_internal_links`, scaling down on young
  sites); auto-run by seo_report.py at site roots.
- `check_article_categories.py` - every article must carry the
  `category` frontmatter that feeds the homepage strips and archives
  (`content.require_category` opts a site out); auto-run by
  seo_report.py at site roots.
- `check_meta_quality.py` - SERP snippet gate over dist: title and
  meta-description presence and length bounds, plus cross-page
  duplicate titles; part of seo_report.py's offline battery.
- `check_image_attrs.py` - every `<img>` in dist must carry alt text
  (empty alt is the decorative marker) and explicit width/height so
  layouts never shift while images load; part of seo_report.py's
  offline battery.
- `check_launch_ready.py` - one-shot launch checklist for a site root:
  template placeholders gone, robots/llms/sitemap/favicons/logo/OG
  image present, trust pages filled, launch content pack complete.
- `check_affiliate_links.py` - enforce the affiliate policy from the
  central `affiliates.json` table: every affiliate anchor needs
  `rel="sponsored"` and a table entry; `--live` probes managed URLs
  for dead destinations
- `check_robots_live.py` - live gate: fetch the SERVED robots.txt and
  fail when any user-agent is both allowed and disallowed at root
  (the signature of a CDN-managed robots block, e.g. Cloudflare AI
  Crawl Control, fighting the site's own AI-ready rules); part of
  seo_report.py's `--live` battery.
- `check_freshness_live.py` - live gate: newest content date from the
  live sitemap's lastmod (RSS pubDate fallback) must be within
  `--max-age-days` (default 45); a stalled publishing rhythm becomes
  a red gate instead of a slow discovery. Part of `--live`.
- `check_toolkit_version.py` - warn when this toolkit clone is behind
  upstream (commit count, plugin version, optional HEAD age), so
  process improvements actually reach every site
- `export_toolkit.py` - lift this directory into its own standalone git
  repository (`--dest`, optional `--remote`)

Every `check_*` script exits non-zero on failure, so the
`test-site-readiness` skill (or `/seo-test`) runs them, fixes the site's
code based on the failures, and re-tests until green.

## Install

Option A - as a Claude Code plugin (recommended):

```bash
# From a checkout of this directory's repository:
/plugin marketplace add <owner>/<repo>
/plugin install zeo
```

Option B - copy into your user config:

```bash
cp -r agents/*   ~/.claude/agents/
cp -r skills/*   ~/.claude/skills/
cp -r commands/* ~/.claude/commands/
```

## Set up the Python helpers

```bash
cd scripts
uv venv
uv pip install -e .
uv run pytest
```

The schema and sitemap skills call these scripts from the `scripts/`
directory. Run them directly if you like:

```bash
uv run python build_jsonld.py --type article --input params.json --output out.json
uv run python validate_schema.py --input out.json
uv run python generate_sitemap.py --input urls.json --base-url https://example.com --out-dir ./public
uv run python generate_llmstxt.py --input site.json --output llms.txt
uv run python check_agent_ready.py --url https://example.com
uv run python check_pagespeed.py --url https://example.com
uv run python check_rich_results.py --url https://example.com/article
```

## Move the toolkit to its own repository

```bash
cd scripts
uv run python export_toolkit.py --dest ~/repos/seo-content-forge \
    --remote git@github.com:<owner>/seo-content-forge.git
```

This copies the toolkit (without venvs, caches, or git history) to the
destination, creates the initial commit, and prints the push command.

## Usage

The primary workflow for a portfolio: keep this toolkit in its own GitHub
repository, and when starting a new site tell Claude Code to use it -
"take <owner>/seo-content-forge, build the new site to this architecture
and these SEO standards". Then:

```
/new-site "home coffee brewing" https://example.com en
```

scaffolds a static-first site with the SEO head component, validated
JSON-LD, AI-ready robots.txt, llms.txt, sitemap wiring, and pillar pages,
verified against the offline checks before handoff.

For an existing site, drive it with a command or plain language:

```
/write-blog "how to store coffee beans at home" example.com (home-coffee niche)
/audit-seo https://example.com
/content-brief "best running shoes for flat feet" example.com
/seo-schema article for https://example.com/blog/coffee-storage
/seo-sitemap from ./urls.json for https://example.com
/seo-test https://example.com ./path/to/site-codebase
```

Skills also trigger without a command - for example, "write an SEO
article about X for my site" invokes the `write-article` pipeline, and
"generate JSON-LD for this page" invokes `generate-schema`.

## Design notes

- Site-agnostic by construction: site context is always an input.
- Plain ASCII throughout; no emoji.
- Structured data and sitemaps are generated and validated by code, not
  hand-written, to avoid invalid markup and protocol-limit violations.
- Grounded in current practice: search intent, E-E-A-T, SERP analysis,
  schema.org rich results, GEO/AEO, Core Web Vitals, hreflang.
