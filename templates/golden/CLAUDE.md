# Working on this site

This site is built and operated with the zeo toolkit (a Claude Code
plugin; checkout commonly at `~/tools/zeo`, referred to as `$ZEO`
below). Do not hand-roll what the toolkit already does: every task has
a skill or script, and deterministic gates - not judgement - decide
when work is done. If unsure where the toolkit lives, ask; then run
`uv run --project "$ZEO/scripts" python
"$ZEO/scripts/check_toolkit_version.py"` to confirm it is fresh.

## Non-negotiable rules

1. New articles go through the write-article skill, never ad hoc
   markdown pasted into `src/content/blog/`. The pipeline covers
   keyword mapping, structure, schema, internal links, originality,
   and images - skipping steps produces exactly the thin content this
   toolkit exists to prevent.
2. An article never ships imageless: one topic-depicting hero
   (`images.hero`, default an original AI-authored illustration via
   the generate-article-images skill) plus at least `images.min`
   in-body images.
3. No commit while a gate is red. Before every commit:

   ```bash
   npm run build && npm run search:index
   uv run --project "$ZEO/scripts" python "$ZEO/scripts/seo_report.py" \
       --dist dist --history .seo-history.json
   ```

   Every line of the card must be PASS - including `meta-quality`
   (title/description bounds, duplicate titles), `image-attrs`
   (every img needs alt plus width/height), `orphan-pages` (every
   article must RECEIVE an in-prose link from another article), and
   the source gates `article-images`, `internal-links`, `category`,
   and `dates` (updatedDate never precedes pubDate, no future
   dates). A red gate is the to-do list, not a warning.
4. Theme and layout changes go through the design-theme skill and end
   with the visual-review gate (`$ZEO/templates/ci/visual-check.mjs`
   screenshots at 3 widths, zero console errors). Never edit
   `src/styles/tokens.css` by hand - change `site.config.json` and
   regenerate with `generate_theme_css.py`.
5. `site.config.json` is the single source of truth: name, domain,
   nav, ui strings, palette, authors, ads, newsletter, image policy.
   Components read it at build time - fix the config, not the
   components.
6. Follow the weekly rhythm in the toolkit's PLAYBOOK.md: publish per
   `content.articles_per_week` (content-calendar skill), queue 6+
   month old articles for refresh (`queue_refresh_candidates.py`),
   and re-run the score card after every batch.

## Task -> tool map

| Task | Use |
| --- | --- |
| Homepage archetype | `site_type` in site.config.json: portal / product (`product` config: facts, steps, demo CTA) / directory (`src/content/entities/` catalog + `directory.facets` filter archives + gallery/price/cta per entity) / forum (threads via `replies` frontmatter - editorial answers, truthfully attributed, QAPage schema) |
| Sitemap / llms.txt | built-in dynamic endpoints (`src/pages/sitemap.xml.js`, `llms.txt.js`) - NEVER hand-write public/ copies, they go stale |
| Agent discovery | built-in: `/api/articles.json` read API, `/.well-known/api-catalog` (replace `{{SITE_URL}}`), Link headers in `public/_headers` |
| New article | write-article skill (ends by running the gates) |
| Article images | generate-article-images skill |
| Topic planning | build-topic-clusters skill (seasonal planner included) |
| Publishing schedule | content-calendar skill |
| Theme / design | design-theme skill + visual-review gate |
| Authors | fill `authors` in site.config.json - profile pages and article author boxes render automatically |
| Categories | set `category` frontmatter - homepage strips and `/category/` archives render automatically |
| Trust pages | generate-trust-pages skill |
| Structured data | generate-schema skill / `$ZEO/scripts/build_jsonld.py` |
| Pre-publish check | `$ZEO/scripts/seo_report.py --dist dist` |
| Launch readiness | `$ZEO/scripts/check_launch_ready.py --root .` before going live |
| Post-deploy check | `seo_report.py --live https://<domain>` + `check_pagespeed.py` |
| Refresh old content | `queue_refresh_candidates.py` + refresh-content skill |
| Monetization | ads/newsletter keys in site.config.json; affiliate manager in the toolkit |
