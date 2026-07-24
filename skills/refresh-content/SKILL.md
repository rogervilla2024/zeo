---
name: refresh-content
description: Update a decaying or outdated article to recover rankings: refresh stats and dates, close new content gaps, re-optimize metadata, update dateModified schema and sitemap lastmod honestly. Use when the user says an article lost traffic or rankings, content is outdated or stale, mentions content decay or refresh, or shares Search Console data showing a declining page.
---

# Refresh a decaying article

Rankings decay as content ages and the SERP moves on. A refresh is a
measured update driven by what changed in the query landscape, not a
cosmetic date bump - search engines detect and discount lastmod
inflation.

## Inputs

- The article URL and source file.
- Why it was flagged: Search Console data the user exports (queries,
  position, CTR trend) or their observation. The user tracks Search
  Console directly; this skill consumes what they share.
- Its original target keyword and metadata.

## Instructions

1. Re-read the SERP: delegate to `serp-competitor-analyst` for what now
   ranks for the target keyword - new subtopics, changed intent, new
   formats (video, tools, updated years). The refresh plan is the delta
   between the article and the current SERP.
2. Update substance, not cosmetics:
   - refresh every stat, price, date, and version number, re-verified
     by `fact-checker`
   - add sections for subtopics the SERP now expects; remove or merge
     sections that no longer earn their place
   - update the FAQ block against current People Also Ask
   - re-run internal linking both ways: new links from this article to
     newer pages, and links from newer pages back to it
3. Re-optimize metadata if the data says so: a low-CTR title gets
   rewritten against the current SERP (delegate to
   `onpage-seo-optimizer`); a fine one stays.
4. Update the freshness signals honestly and only because substance
   changed: `dateModified` in the Article JSON-LD and `lastmod` in the
   sitemap entry. Never bump either without a substantive change.
5. Run the standard gates: `check_ai_patterns.py`, `check_originality.py`
   (against the site corpus), and `check_rich_results.py` on the built
   page.
6. Record what changed and why in the handoff, so the next review can
   judge whether the refresh worked from the user's Search Console data.

## Output

- The refreshed article, the change log (what was added, removed,
  re-verified), updated metadata and schema, and the sitemap lastmod
  update.

## Quality checklist

- Every change traces to SERP movement, data the user shared, or a
  stale fact; no padding to look updated.
- All stats and dates re-verified; nothing older left contradicting the
  new content.
- dateModified/lastmod updated only alongside substantive changes.
- All gates pass; internal links refreshed in both directions.
