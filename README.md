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

Skills (`skills/`, 20) - workflows that auto-trigger from natural language
and orchestrate the subagents:

- `write-article` (flagship, full pipeline), `humanize-content`,
  `fact-check`, `optimize-onpage-seo`, `audit-technical-seo`,
  `build-topic-clusters`, `content-calendar`, `optimize-geo-aeo`,
  `generate-schema`, `generate-sitemap`, `generate-llms-txt`,
  `test-site-readiness`, `bootstrap-site`, `optimize-images`,
  `build-author-entity`, `translate-article`, `refresh-content`,
  `generate-trust-pages`, `find-theme`, `adopt-theme`, `visual-review`

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
  `theme/` by `tests/test_golden_template.py`
- `robots.txt` - AI-ready robots template with every major AI crawler
  named explicitly and a Sitemap directive
- `theme/` - the full theme layer: design tokens rendered from
  site.config.json (`generate_theme_css.py`), `BaseLayout.astro` with
  the speed patterns baked in (zero-JS default, Speculation Rules
  prerendering, dark mode, skip link), the SEO head components
  (`SeoHead.astro`, `next-metadata.ts`), Breadcrumbs and Footer, eight
  zero-JS content blocks (TableOfContents, KeyTakeaways, FaqAccordion,
  ProsCons, VerdictBox, ArticleMeta, RelatedPosts, Pagefind SearchBox),
  and four layout variants (`variants/`: minimal, editorial, guide,
  review) so sites sharing the skeleton do not share a look
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
  JobPosting (on-site and remote), Course, SoftwareApplication
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
- `find_theme.py` - sweep GitHub's astro-theme/astro-template ecosystem
  (hundreds of candidates in seconds), hard-filter by permissive
  license, activity, and stars, rank by niche fit; finalists feed the
  find-theme/adopt-theme skills
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
- `export_toolkit.py` - lift this directory into its own standalone git
  repository (`--dest`, optional `--remote`)

The three `check_*` scripts exit non-zero on failure, so the
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
