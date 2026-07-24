---
name: optimize-onpage-seo
description: Optimizes a single page's on-page SEO elements: title tag, meta description, URL slug, heading hierarchy, image alt text, internal links, and featured-snippet targeting. Produces a clear before/after. Use when the user wants to optimize on-page SEO, improve a title or meta description, fix headings, target a featured snippet, add alt text or internal links, or make one page rank better for a keyword.
---

Tunes the on-page signals of one page for a target keyword and intent, and returns a before/after diff plus the reasoning.

## Inputs

- The page content or URL, including current title, meta, headings, and body.
- Primary target keyword and secondary keywords.
- Search intent and the audience.
- Brand voice and character limits or CMS constraints (title/meta length).
- Available internal link targets on the same site (URL plus topic).
- Any snippet type worth targeting (paragraph, list, table, definition).

You may delegate to the `onpage-seo-optimizer` subagent for the core rewrite and to the `internal-link-strategist` subagent for link selection via the Task/Agent mechanism.

## Instructions

1. Assess the current state. Record the existing title, meta, slug, H1-H3 structure, alt text, and internal links so the before/after is concrete.
2. Title tag. Write a compelling title ~50-60 characters with the primary keyword near the front and a reason to click. One idea, no keyword stuffing.
3. Meta description. Write ~140-160 characters that includes the keyword, matches intent, and earns the click. Not a ranking factor directly, but drives CTR.
4. URL slug. Propose a short, lowercase, hyphenated slug containing the primary keyword and no stop-word clutter.
5. Headings. Ensure one H1 that reflects the query, logical H2/H3 nesting, and secondary keywords or questions surfaced in subheads. Fix skipped levels.
6. Keyword placement. Confirm the primary keyword appears in the H1, first 100 words, at least one subhead, and naturally through the body. Keep density natural; flag stuffing.
7. Image alt text. Write descriptive, keyword-aware alt text for each image without keyword stuffing.
8. Internal links. Recommend contextual internal links to relevant same-site pages with descriptive anchor text; note any orphaned-page opportunities.
9. Snippet targeting. Add or restructure a concise, extractable answer block (40-60 word paragraph, ordered/unordered list, or comparison table) matched to the query type.
10. Present before/after for each element with a one-line rationale.

## Output

- A before/after table for title, meta, slug, and headings.
- Final recommended values for each on-page element.
- Alt-text list per image.
- Internal link recommendations with anchor text and target URLs.
- The snippet-target block, ready to paste.

## Quality checklist

- [ ] Title within length and keyword-forward with a clear hook.
- [ ] Meta within length, includes keyword, matches intent.
- [ ] Slug short, hyphenated, keyword-bearing.
- [ ] Single H1; heading levels are ordered with no skips.
- [ ] Primary keyword in H1, first 100 words, and a subhead; no stuffing.
- [ ] Every image has descriptive alt text.
- [ ] Internal links are relevant with descriptive anchors.
- [ ] Snippet block is concise and extractable for its query type.
- [ ] Before/after is explicit for each change.
