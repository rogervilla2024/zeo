# Variant: minimal

Reading-first blog. The default when no variant is chosen.

Layout:

- Single column at `--max-width` (72ch default); generous line height.
- Header: site name left, 2-4 nav links plus theme toggle right.
- Article page order: Breadcrumbs, h1, ArticleMeta, KeyTakeaways,
  TableOfContents (only when 4+ h2s), body, FaqAccordion, author box,
  RelatedPosts.
- Home: intro paragraph, then a plain chronological post list
  (title, one-line description, date). No cards, no thumbnails.

Typography and color:

- Body and headings from the token font stacks; headings may use the
  heading font at 600-700 weight.
- Color is used sparingly: links and the KeyTakeaways border carry
  `--color-primary`; everything else is text on background.

Rules:

- No hero images on articles unless the content genuinely needs one;
  when present it is the LCP element (fetchpriority high, never lazy).
- No sidebar. Related content lives at the end of the article.
