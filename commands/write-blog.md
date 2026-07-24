---
description: Produce a publish-ready SEO blog article end-to-end from a target keyword and site context
argument-hint: [target keyword] [site domain or niche]
---

You are running the end-to-end article production pipeline.

Parse $ARGUMENTS to extract the target keyword and the site/niche context (domain,
audience, or vertical). If the target keyword is missing, ask for it. If no site or
niche context is provided, ask for the site domain or a one-line description of the
site's audience and topic focus before proceeding. Do NOT assume any brand or niche.

Orchestrate the following steps in order:

1. Strategy and research. Delegate to the keyword-researcher subagent to confirm
   search intent, related terms, and SERP angle for the keyword. Delegate to the
   seo-content-strategist to position the piece against the site's goals.
2. Brief. Delegate to content-brief-architect to produce an outline, target intent,
   headings, entities, and internal-linking targets scoped to the provided site.
3. Draft. Invoke the write-article skill (or the longform-writer subagent) to write
   the full draft from the brief.
4. Fact-check. Invoke the fact-check skill (or fact-checker subagent) to verify
   claims, statistics, and citations. Flag anything unverifiable.
5. Humanize. Invoke the humanize-content skill (or content-humanizer subagent) to
   improve tone, rhythm, and readability without changing meaning.
6. On-page SEO. Invoke the optimize-onpage-seo skill (or onpage-seo-optimizer) to
   tune the title tag, meta description, headings, keyword placement, and internal
   links. Invoke optimize-geo-aeo for answer-engine and AI-overview readiness.
7. Schema. Invoke the generate-schema skill to output Article/BlogPosting JSON-LD.

Deliver a single response containing:
- The final publish-ready article in markdown.
- A meta block: proposed title tag, meta description, URL slug, and primary/secondary
  keywords.
- Suggested internal links relevant to the provided site.
- Valid JSON-LD in a fenced code block.
- A short note listing any fact-check flags or open questions.
