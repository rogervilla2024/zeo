---
description: Run a technical SEO audit on a site or URL and return a prioritized action plan
argument-hint: [site domain or page URL]
---

You are running a technical SEO audit.

Parse $ARGUMENTS for the target site domain or specific page URL. If no site or URL
is provided, ask the user for the domain (or URL) and, optionally, whether the scope
is the whole site or a single page. Do NOT assume any brand, domain, or niche.

Orchestrate the audit:

1. Invoke the audit-technical-seo skill (or delegate to the technical-seo-auditor
   subagent) against the provided target. Cover at minimum:
   - Crawlability and indexation (robots.txt, meta robots, canonicals, sitemaps).
   - Site architecture and internal linking depth.
   - Page performance and Core Web Vitals signals.
   - HTTPS, redirects, status codes, and duplicate content.
   - Structured data presence and validity.
   - Mobile usability and rendering.
2. Where structured-data or internal-linking issues surface, pull in the
   schema-engineer or internal-link-strategist subagent for specifics.

Deliver a prioritized action plan:
- A findings table grouped by severity (Critical, High, Medium, Low).
- For each finding: the issue, why it matters, affected URLs or patterns, and the
  concrete fix.
- A short "do these first" list of the highest-impact, lowest-effort items.
- Note any checks that could not be completed and what input is needed to finish them.
