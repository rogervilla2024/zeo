---
name: test-site-readiness
description: Run the full site test suite (agent-readiness like isitagentready.com, PageSpeed Insights Core Web Vitals, and rich-results structured data checks) and then fix the site's code based on the failures found. Use when the user wants to test a site, check agent readiness, run PageSpeed, test rich results, audit and auto-fix, or asks whether the site is ready for AI agents and Google.
---

# Test site readiness and fix what fails

Run three objective test suites against a site, turn every failure into a
concrete change, and, when working inside the site's codebase, apply the
fixes and re-run the tests until they pass. Tests decide; opinions do not.

## Inputs

- Site root URL (and optionally specific page URLs to test).
- Access to the site's codebase if fixes should be applied, plus which
  framework it uses (so fixes land in the right files).
- Optional: PAGESPEED_API_KEY in the environment (from .env, never
  hardcoded) for higher PageSpeed API quotas.

## Instructions

1. Run all three checkers from the toolkit's `scripts/` directory:

   ```bash
   python check_agent_ready.py --url https://example.com
   python check_pagespeed.py --url https://example.com
   python check_rich_results.py --url https://example.com/target-page
   # and against the local build output:
   python check_js_budget.py --dist dist
   python check_broken_links.py --dist dist
   python check_media_budget.py --dist dist
   python check_canonical_host.py --domain https://example.com  # post-deploy
   python check_rich_results.py --file dist/index.html
   ```

   For article content also run the content gates where drafts are
   available: check_ai_patterns.py and check_originality.py. Finish
   with the visual-review skill when layout changed.

   Each prints a report and exits non-zero on failure, so the exit codes
   tell you which suites need work.
2. Collect every FAIL line and opportunity into a single fix list, ordered
   by impact:
   - agent-readiness failures each ship with a `fix:` line;
   - PageSpeed opportunities are pre-sorted by estimated savings;
   - rich-results errors name the exact missing property per node.
3. If you have the site's codebase, apply the fixes directly:
   - missing llms.txt: run the generate-llms-txt skill and add the file;
   - missing sitemap or robots.txt issues: run the generate-sitemap skill
     and edit robots.txt (AI bot rules, Sitemap directive);
   - missing or invalid JSON-LD: run the generate-schema skill and embed
     the validated output in the page template;
   - missing title/description/canonical/h1/main: edit the page templates;
   - JavaScript-only content: enable server-side rendering or static
     generation for the affected routes (framework-specific);
   - PageSpeed opportunities: apply the named optimizations (defer
     render-blocking resources, compress images, remove unused CSS/JS).
   Delegate deep work to the matching subagents: technical-seo-auditor,
   schema-engineer, onpage-seo-optimizer, geo-aeo-optimizer.
4. Re-run the failing checkers after fixing. Repeat fix-and-retest until
   all three suites pass or the remaining failures need infrastructure
   the codebase does not control (report those explicitly).
5. If you do not have the codebase, deliver the fix list as a prioritized
   action plan instead, with file-level suggestions per failure.

## Output

- The three test reports (before), the list of fixes applied with file
  paths, and the re-run results (after).
- Any remaining failures with the reason they cannot be fixed from the
  codebase and what would be needed.

## Quality checklist

- Every failing check is either fixed and re-tested or explicitly
  explained; none are silently dropped.
- Fixes are verified by re-running the checker, not assumed correct.
- No fabricated structured data is added to pass a test; markup must
  reflect visible page content.
- Secrets (API keys) stay in the environment and are never printed.
