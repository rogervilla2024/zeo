---
name: generate-sitemap
description: Generate standards-compliant XML sitemaps and sitemap indexes from a list of URLs, including hreflang alternates, lastmod, and automatic splitting at the 50,000-URL limit. Use when the user wants a sitemap, sitemap.xml, sitemap index, XML sitemap, hreflang sitemap, or to help search engines discover and index pages.
---

# Generate XML sitemaps

Turn a set of site URLs into valid sitemap files a search engine can
consume, backed by a helper script so the XML is always well-formed and
within protocol limits.

## Inputs

Gather from the user or the site:

- The list of indexable URLs (absolute). Exclude noindex, canonicalized-
  away, redirected, and blocked URLs.
- Public base URL where the sitemap files will be hosted (used to build
  absolute references in a sitemap index).
- Optional per-URL metadata: `lastmod`, `changefreq`, `priority`.
- For internationalized sites: hreflang alternates per URL
  (`{"hreflang": "en", "href": "..."}`), including an `x-default`.

## Instructions

1. Build a JSON array of URL entries. Each entry needs `loc` and may add
   `lastmod`, `changefreq`, `priority`, and `alternates`. Example:

   ```json
   [
     {
       "loc": "https://example.com/",
       "lastmod": "2026-01-15",
       "changefreq": "daily",
       "priority": 1.0,
       "alternates": [
         {"hreflang": "en", "href": "https://example.com/"},
         {"hreflang": "de", "href": "https://example.com/de/"},
         {"hreflang": "x-default", "href": "https://example.com/"}
       ]
     }
   ]
   ```

2. Generate the sitemap(s) with the helper script from the toolkit's
   `scripts/` directory:

   ```bash
   python scripts/generate_sitemap.py --input urls.json \
       --base-url https://example.com --out-dir ./public
   ```

   Inputs over 50,000 URLs are split automatically into numbered files
   plus a `sitemap-index.xml`.
3. Add a `Sitemap:` directive to `robots.txt` pointing at the sitemap (or
   the index) absolute URL.
4. For strategy decisions (news/image/video sitemaps, splitting scheme,
   lastmod discipline, submission), delegate to the `sitemap-engineer`
   subagent.
5. Tell the user to submit the sitemap in Google Search Console and Bing
   Webmaster Tools.

## Output

- The generated sitemap file(s), or an index plus child files for large
  sites.
- The `robots.txt` `Sitemap:` line to add.

## Quality checklist

- Every `loc` is absolute and returns 200 (no redirects or noindex URLs).
- hreflang sets are reciprocal and include `x-default`.
- No single file exceeds 50,000 URLs or 50 MB uncompressed.
- `lastmod` values are accurate, not blanket-stamped to today.
- The sitemap is referenced from `robots.txt`.
