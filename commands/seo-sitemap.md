---
description: Generate sitemap XML from a URL list or site config
argument-hint: [URL list, site domain, or config]
---

You are generating an XML sitemap.

Parse $ARGUMENTS for the source of URLs: a pasted URL list, a site domain to base
paths on, or a config describing sections and priorities. If no URLs or domain are
provided, ask the user for the list of URLs (or the domain plus how the URLs should be
gathered) before proceeding. Do NOT assume any brand, domain, or niche.

Orchestrate the following:

1. Invoke the generate-sitemap skill (or delegate to the sitemap-engineer subagent) to
   build a standards-compliant sitemap. Follow the sitemaps.org protocol:
   - Use absolute URLs with a consistent host and scheme.
   - Include loc, and where known lastmod, changefreq, and priority.
   - Exclude non-canonical, noindex, redirected, and error URLs.
   - Split into multiple sitemaps plus a sitemap index if there are more than 50,000
     URLs or the file would exceed 50 MB uncompressed.
2. If image or news entries are relevant and data is provided, include the appropriate
   sitemap extensions.

Deliver:
- The sitemap XML in a fenced code block (and the sitemap index XML if split).
- The recommended file path(s) and the robots.txt Sitemap directive to add.
- Notes on any URLs excluded and why, and any input needed to complete lastmod or
  priority values.
