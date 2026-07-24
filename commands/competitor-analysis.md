---
description: Analyze the SERP competitors for a query or URL and return a content-gap and differentiation plan
argument-hint: [search query or competitor URL] [site domain or niche]
---

You are running a SERP competitor analysis.

Parse $ARGUMENTS for the target search query or competitor URL, plus the site/niche
context the analysis is for. If no query or URL is provided, ask for one. If no site or
niche context is provided, ask for the site domain or a one-line description so the
differentiation plan is grounded. Do NOT assume any brand, domain, or niche.

Orchestrate the following:

1. Delegate to the serp-competitor-analyst subagent to examine the top-ranking results
   for the query (or the peer set around the provided competitor URL). Capture for each
   competitor: content type and angle, structure and depth, headings covered, word
   count, entities and keywords targeted, schema used, and apparent strengths.
2. Where useful, pull in the keyword-researcher subagent to surface keyword and entity
   gaps, and build-topic-clusters to identify adjacent topics competitors own.

Deliver a differentiation plan:
- A comparison table of the analyzed competitors across the captured dimensions.
- Content gaps: subtopics, questions, formats, and entities competitors miss or cover
  weakly.
- Differentiation angles the provided site can own, with rationale.
- Concrete recommendations: outline changes, sections to add, schema and format moves,
  and internal-linking opportunities.
- A prioritized "quick wins vs. long plays" summary.
