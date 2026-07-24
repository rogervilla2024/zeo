# Variant: guide

Documentation-style layout for tutorial and reference-heavy niches.

Layout:

- Two columns on desktop: a left sidebar with the cluster's page tree
  (pillar page as the root, cluster articles nested under it), content
  at `--max-width` on the right. Sidebar collapses to a details
  disclosure on mobile.
- Article page order: Breadcrumbs, h1, ArticleMeta, TableOfContents
  rendered sticky in the right margin on wide screens (falls back to
  in-flow), body with numbered step sections, FaqAccordion,
  prev/next links within the cluster.
- HowTo schema on step-based pages; steps in the markup match the
  HowTo JSON-LD exactly.

Typography and color:

- Monospace token stack for code and command samples; copy-friendly
  code blocks (no line-number gutters in the text flow).
- `--color-primary` marks the active page in the sidebar tree.

Rules:

- The sidebar tree is the cluster's internal-linking map made visible;
  it is generated from the content collection, not hand-maintained.
- Prev/next links stay within the cluster to reinforce topical depth.
