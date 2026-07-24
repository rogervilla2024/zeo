---
description: Build a detailed writer brief for a target keyword using research and SERP analysis
argument-hint: [target keyword] [site domain or niche]
---

You are producing a detailed content brief for a writer.

Parse $ARGUMENTS for the target keyword and the site/niche context. If the keyword is
missing, ask for it. If no site or niche is provided, ask for the site domain or a
one-line description of the audience and topic focus. Do NOT assume any brand or niche.

Orchestrate the following:

1. Delegate to the keyword-researcher subagent to establish search intent, primary and
   secondary keywords, related entities, and question variants.
2. Delegate to the serp-competitor-analyst subagent to analyze the top-ranking pages
   for the keyword: their structure, depth, angle, and coverage gaps.
3. Optionally invoke build-topic-clusters to place the keyword within a cluster and
   identify supporting/pillar links for the provided site.
4. Delegate to the content-brief-architect subagent to assemble the final brief.

Deliver a single brief containing:
- Working title options and the target URL slug.
- Search intent and the audience the piece must satisfy.
- Primary keyword, secondary keywords, and entities to include.
- A recommended heading outline (H1 through H3) with notes on what each section covers.
- Target word count and suggested content format (guide, listicle, comparison, etc.).
- Content gaps and angles that beat the current SERP.
- Internal-linking targets scoped to the provided site and suggested external sources.
- People-also-ask style questions to answer and a suggested FAQ block.
