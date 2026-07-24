---
description: Run the full site test suite (agent-readiness, PageSpeed, rich results) and fix the site based on the failures
argument-hint: [site URL] [optional: page URLs, path to codebase]
---

You are running the objective site test suite and acting on its results.

Parse $ARGUMENTS for the site root URL, optional specific page URLs, and an
optional path to the site's codebase. If no URL is provided, ask for the site
root URL before proceeding. If a codebase path is present (or the current
working directory is the site's project), fixes are in scope; otherwise
deliver a prioritized action plan only.

Orchestrate the following:

1. Invoke the test-site-readiness skill, which runs the three checkers from
   the toolkit's scripts/ directory:
   - check_agent_ready.py (discoverability, AI bot access, content
     accessibility, machine readability)
   - check_pagespeed.py (Lighthouse performance, Core Web Vitals)
   - check_rich_results.py (JSON-LD extraction and rich-result validation)
   For multi-template sites, run check_rich_results.py against one URL per
   page template, not only the homepage.
2. If fixes are in scope, delegate the fix-and-retest loop to the
   site-readiness-tester subagent: apply each fix in the codebase, re-run
   the failing checker, and iterate until the suites pass or the remaining
   failures are external (CDN, hosting, CrUX lag).
3. Where a fix needs a generated artifact, use the matching skill:
   generate-llms-txt for a missing llms.txt, generate-sitemap for sitemap
   issues, generate-schema for missing or invalid JSON-LD.

Deliver a single response containing:
- Before/after results for each of the three suites.
- The list of fixes applied with file paths (or the prioritized action plan
  when no codebase is available).
- Any remaining failures that require action outside the codebase, with the
  concrete requirement for each.
