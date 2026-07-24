---
name: audit-technical-seo
description: Runs an evidence-based technical SEO audit of a site and produces a prioritized action plan with severity, evidence, fix, and effort/impact for each issue. Use when the user wants a technical SEO audit, to check crawlability or indexing, diagnose Core Web Vitals or site speed, fix redirects, canonicals, robots.txt, sitemaps, or structured data, or get a prioritized list of technical fixes.
---

Inspects the technical health of a site and returns a ranked, actionable remediation plan grounded in evidence rather than guesswork.

## Inputs

- Domain and access available (URLs, crawl export, server logs, analytics, Search Console).
- Platform/CMS and hosting stack.
- Priority pages or templates.
- Known symptoms (traffic drop, deindexing, slow pages).
- Locale and whether the site is international (hreflang relevant).

You may delegate the crawl-and-diagnose work to the `technical-seo-auditor` subagent, sitemap issues to `sitemap-engineer`, and structured-data checks to `schema-engineer` via the Task/Agent mechanism.

## Instructions

Audit each area below. For every finding, capture evidence (the exact URL, header, directive, or metric), not just an assertion.

1. Crawlability and indexing. Check robots.txt, meta robots, X-Robots-Tag, canonical tags, index coverage, orphan pages, and crawl-budget waste (faceted URLs, infinite spaces).
2. Site architecture. Assess URL structure, click depth to key pages, breadcrumb and internal-link distribution, and pagination handling.
3. Redirects and status codes. Find 4xx/5xx errors, redirect chains and loops, mixed http/https, and non-canonical duplicates.
4. Sitemaps. Validate XML sitemap presence, freshness, inclusion of only canonical 200 URLs, and reference in robots.txt.
5. Performance and Core Web Vitals. Measure LCP, INP, and CLS on key templates; note render-blocking resources, unoptimized images, and caching gaps.
6. Mobile and rendering. Confirm mobile-friendliness, viewport, and that critical content renders without JS dependence.
7. Structured data. Validate JSON-LD for errors and eligibility, and check for missing schema opportunities.
8. International (if applicable). Verify hreflang reciprocity and correct locale/region codes.
9. Security and hygiene. Confirm HTTPS, valid certificate, HSTS, and no mixed content.

For each issue, assign a severity (Critical, High, Medium, Low), record the evidence, state the concrete fix, and rate effort (S/M/L) and impact (High/Med/Low). Sort the plan by impact-to-effort, Critical first.

## Output

- An executive summary: overall health and the top 3-5 issues.
- A prioritized issue table: Issue | Severity | Evidence | Fix | Effort | Impact.
- Quick wins (high impact, low effort) called out separately.
- Any items needing further data or access before they can be resolved.

## Quality checklist

- [ ] Every finding cites specific evidence (URL, header, directive, or metric).
- [ ] No speculative issues without proof.
- [ ] Each issue has severity, a concrete fix, and effort/impact ratings.
- [ ] Plan is sorted by priority with quick wins highlighted.
- [ ] Crawl, indexing, performance, structure, and schema are all covered.
- [ ] Recommendations are platform-appropriate and site-agnostic to brand.
- [ ] Data gaps are flagged rather than guessed.
