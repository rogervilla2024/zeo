# Variant: review

Comparison and review layout for evaluation-driven niches.

Layout:

- Article page order: Breadcrumbs, h1, ArticleMeta, VerdictBox
  immediately after the intro (the answer first), KeyTakeaways,
  TableOfContents, body with comparison tables, ProsCons per evaluated
  option, FaqAccordion, RelatedPosts.
- Home: current top picks section (small cards with scores), then
  recent reviews by category.
- Comparison tables are plain markdown tables styled by tokens.css:
  sticky header row, first column bold, horizontal scroll on mobile.

Typography and color:

- Scores and verdicts carry `--color-primary`; cons and cautions use
  `--color-accent`. Nothing else competes for attention.

Rules:

- Every visible score is mirrored in schema (Product aggregateRating
  or Review) and vice versa; no schema-only ratings, ever.
- Affiliate links, when present, are `rel="sponsored"` and visually
  disclosed near the top of the article; the disclaimer page covers
  the policy.
- Verdicts must be justified in the body: the VerdictBox summarizes
  what the article demonstrates, it never replaces it.
