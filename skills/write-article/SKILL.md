---
name: write-article
description: Runs the full original-content pipeline for a single article from keyword research through publish-ready draft with schema. It orchestrates research, briefing, longform drafting (2000-3000+ words), humanization, on-page SEO, fact-checking, and structured data. Use when the user wants to write an article, create a blog post, produce a long-form guide, generate SEO content, or take a topic from idea to publish-ready draft.
---

Flagship orchestration skill. It sequences specialist subagents to turn a topic into a publish-ready article for any site and niche.

## Inputs

HARD RULE: site context (niche, audience, voice, language) comes from
site.config.json when it exists; the target keyword must belong to that
niche. Never take topics from example snippets in toolkit docs or
unrelated earlier prompts - if the requested keyword contradicts the
config niche, stop and ask.

Gather before starting (ask only for what is missing; infer the rest from site context):

- Domain and site name.
- Niche and primary audience.
- Brand voice and tone (formal, conversational, expert, etc.).
- Primary target keyword and any secondary keywords.
- Search intent (informational, commercial, transactional, navigational).
- Target word count (default 2000-3000+; go longer for competitive terms).
- Constraints: mandatory sub-topics, internal URLs to link, do-not-mention list, locale/language.

## Batch and policy rules (non-negotiable)

- Never produce more than `content.max_batch` articles (default 10) in
  one run, regardless of what was asked. For larger requests, stop at
  the cap, report, and continue only on explicit go-ahead. Follow the
  `content.weekly_ramp` publishing pace from PLAYBOOK - publishing 100
  articles onto a fresh domain at once matches Google's scaled content
  abuse pattern even when each article passes the gates.
- Within a batch, run check_originality.py for each new article against
  the OTHER articles of the same batch as well as the published corpus.
- No doorway pages: keyword variations with the same intent ("best X",
  "top X", "X reviews") get ONE comprehensive article, never one page
  per variation. If the requested keyword only differs in phrasing from
  an existing article, update that article instead.

## Instructions

Run the stages in order. Delegate each stage to the named subagent via the Task/Agent mechanism when available; otherwise perform the stage inline using its focus.

1. Keyword and SERP research. Delegate to `keyword-researcher` for the primary keyword, related terms, questions, and search volume signals. Delegate to `serp-competitor-analyst` to analyze the top-ranking pages, their headings, depth, and content gaps. Confirm intent before proceeding.
2. Strategy. Delegate to `seo-content-strategist` to set the angle, unique value proposition, and how this article fits the site's topical authority.
3. Brief. Delegate to `content-brief-architect` to produce an outline: H1, H2/H3 structure, target keyword placement, questions to answer, entities to cover, word-count targets per section, and internal-link opportunities.
4. Draft. Delegate to `longform-writer` to write the full draft against the brief. Enforce the target length, original insight, examples, and natural keyword usage. No fabricated statistics.
5. Humanize, then verify it. Delegate to `content-humanizer` (or invoke the humanize-content skill) to remove AI-tell patterns and match the brand voice while preserving meaning and keywords. Then run the objective gate and fix anything it flags:

   ```bash
   python scripts/check_ai_patterns.py --article draft.md
   ```

   Banned phrases are ship-blocking; structural warnings (repeated sentence openers, uniform paragraph lengths) get one more editing pass.
6. FAQ block (mandatory). Append a "Frequently asked questions" section of 3-5 questions drawn from the People Also Ask questions and related queries surfaced in stage 1. Each answer is 40-80 words, self-contained, and extractable (direct answer in the first sentence). These questions must not duplicate content already covered under an H2; they cover the adjacent questions a reader would search next.
7. On-page SEO. Delegate to `onpage-seo-optimizer` (or invoke the optimize-onpage-seo skill) for title tag, meta description, slug, heading hierarchy, image alt text, and snippet targeting.
8. Internal linking (mandatory - an article does not ship without it). Every article must link contextually from its body text to relevant same-site pages, and this happens at creation time, not as a later cleanup. Build or load the site's content inventory (JSON of published URLs with titles and keywords, derivable from the sitemap or content collection), then run the toolkit's smart linker:

   ```bash
   python scripts/suggest_internal_links.py --article draft.md \
       --inventory inventory.json --apply --output draft-linked.md
   ```

   The linker finds natural anchor phrases inside paragraphs (never headings or code), caps density, and links each target once. Review its insertions, and delegate to `internal-link-strategist` for links back FROM older articles TO the new one (reverse linking), which the strategist should list as edits to existing pages. A brand-new site with no inventory yet links to its pillar pages instead.
9. Fact-check. Delegate to `fact-checker` (or invoke the fact-check skill) to verify claims, add citations, and correct stats, dates, and names. Do not proceed with unresolved flags.
10. Schema. Delegate to `schema-engineer` to generate JSON-LD: Article/BlogPosting (with the author's profile URL when the site has author entities), FAQPage built from the stage-6 questions, and HowTo where relevant, matching the final content.
11. Originality gate. When the site has published articles, verify the new article is not substantially similar to anything already on the site:

   ```bash
   python scripts/check_originality.py --article draft.md --corpus corpus.json
   ```

   A failing score means rewriting the overlapping sections, not tweaking words until the number drops.
12. Assemble and hand off. Return the final draft plus a metadata block (title, meta, slug, target keyword, internal links, schema).

## Output

- Publish-ready article body in markdown, hitting the target word count.
- Metadata block: title tag, meta description, URL slug, primary and secondary keywords.
- Internal and external link list with anchor text.
- JSON-LD schema block.
- Short QA note listing any residual risks or items needing human review.

## Quality checklist

- [ ] Content is original and answers the search intent completely.
- [ ] Meets or exceeds target word count without padding.
- [ ] Primary keyword in title, H1, first 100 words, and slug; secondary keywords used naturally.
- [ ] Heading hierarchy is logical (single H1, ordered H2/H3).
- [ ] Reads as human-written; check_ai_patterns.py passes with no banned phrases.
- [ ] check_originality.py clears the threshold against the site's published articles.
- [ ] Every statistic, date, and name is cited or corrected.
- [ ] FAQ section present: 3-5 PAA-derived questions with extractable answers, mirrored in FAQPage JSON-LD.
- [ ] In-body contextual internal links are present (suggest_internal_links.py applied and reviewed); the article never ships without them.
- [ ] Reverse-link edits (older articles linking to this one) are listed for application.
- [ ] Valid JSON-LD schema matches the visible content.
- [ ] No brand, domain, or niche assumptions beyond the provided inputs.
