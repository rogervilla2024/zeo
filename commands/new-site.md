---
description: Scaffold a brand-new SEO-ready site (config, SSG framework, schema, robots, llms.txt, sitemap, pillar pages) from a niche and domain
argument-hint: [niche] [domain] [optional: language(s), framework]
---

You are bootstrapping a new website that must pass the toolkit's test suite
from day one.

Parse $ARGUMENTS for the niche, the domain, optional language(s), and an
optional framework preference. Ask for anything essential that is missing
(niche and domain at minimum). Default to a static-first framework (Astro or
Next.js SSG) when none is named; never scaffold a client-side-only app.

Orchestrate the following:

1. Invoke the bootstrap-site skill and follow it end to end: write
   site.config.json (the single source of truth for all later skills),
   scaffold the framework, build the SEO head component, embed validated
   Organization and WebSite JSON-LD, install the AI-ready robots.txt
   template, wire the sitemap, and generate llms.txt.
2. Delegate the heavy scaffolding work to the site-bootstrap-architect
   subagent, and the initial pillar/cluster plan to the
   build-topic-clusters skill. Write the first pillar article with
   write-article unless the user asked for structure only.
3. Verify with the offline checks before finishing: check_rich_results.py
   against the built HTML, and confirm robots.txt, llms.txt, and the
   sitemap exist in the build output. List the post-deploy checks
   (check_agent_ready.py, check_pagespeed.py) as next steps.

Deliver a single response containing:
- What was scaffolded (framework, structure, files) and where.
- The offline test results.
- Deploy steps for the chosen host and the post-deploy test commands.
- The suggested first-month content plan from the pillar/cluster map.
