---
name: build-topic-clusters
description: Builds a pillar-and-cluster content map from a niche or seed keyword, with search intent per page and an internal-linking plan to establish topical authority. Use when the user wants to plan a content strategy, build topic clusters, create a pillar page and supporting posts, map out content around a theme, find content gaps, or design an internal-linking structure for a niche.
---

Turns a niche or seed keyword into a structured pillar/cluster map that builds topical authority, with intent and an internal-linking plan.

## Inputs

- Niche and seed keyword or theme.
- Domain, audience, and brand voice.
- Business goals and priority conversion pages (money pages).
- Existing content inventory, if any (URLs and topics), to avoid duplication.
- Locale/language and competitive context.

You may delegate keyword expansion to the `keyword-researcher` subagent, competitive gap analysis to the `serp-competitor-analyst` subagent, strategy framing to the `seo-content-strategist` subagent, and the linking plan to the `internal-link-strategist` subagent via the Task/Agent mechanism.

## Instructions

1. Define the pillar topics. From the seed, identify 1-5 broad pillar themes the site can own. Each pillar is a comprehensive page targeting a high-level, high-volume head term.
2. Expand into clusters. For each pillar, generate cluster subtopics from long-tail keywords, questions, and subtopics that the pillar links out to and that link back up.
3. Assign search intent to every page (informational, commercial, transactional, navigational) and map each to a stage of the funnel.
4. Deduplicate and detect cannibalization. Merge overlapping ideas so no two pages target the same intent and keyword. Reconcile against existing inventory.
5. Prioritize. Score topics by opportunity: search demand, competition, and business value. Sequence what to publish first.
6. Design the internal-linking plan. Every cluster page links up to its pillar; the pillar links down to each cluster; connect closely related cluster pages laterally. Specify anchor-text themes and route authority toward priority pages.
7. Define page metadata. For each entry, set a working title, primary keyword, secondary keywords, target format (guide, listicle, comparison, how-to, glossary), and rough word-count target.

## Output

- A pillar/cluster map (table or tree): Pillar -> Cluster pages, each with primary keyword, intent, funnel stage, format, and priority.
- An internal-linking plan describing up/down/lateral links and anchor-text themes.
- A prioritized publishing roadmap (first wave, next wave).
- A gap list of topics competitors cover that the site does not.

## Quality checklist

- [ ] Pillars are broad and ownable; clusters are specific and long-tail.
- [ ] Every page has an assigned intent and funnel stage.
- [ ] No two pages cannibalize the same keyword and intent.
- [ ] Existing content is reconciled, not duplicated.
- [ ] Internal-linking plan connects clusters to pillars and to each other.
- [ ] Authority is routed toward priority conversion pages.
- [ ] Roadmap is prioritized by opportunity and business value.
- [ ] Map is site-agnostic and driven by the provided niche inputs.
