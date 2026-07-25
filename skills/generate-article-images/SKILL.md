---
name: generate-article-images
description: Give every article its images: original SVG diagrams generated from the article's own content (default), stock photos via the Pexels adapter where photography is required, all optimized and wired into alt text, dimensions, lazy loading, and the image sitemap. Use when articles lack images, when the user asks for article visuals, diagrams, or stock photos, or when visual-review fails an imageless article.
---

# Generate article images

An article never ships imageless. Strategy comes from site.config.json
`images.strategy` (default `svg-first`).

## Instructions

1. Read the article and pick `images.min` to `images.max` (default 2-4)
   visual opportunities: the concept a diagram explains better than a
   paragraph, steps as a flow, comparisons as a visual table, key stats
   as a stat card.
2. SVG-first (default): author original SVGs yourself from the article
   content - step flows, comparison cards, process diagrams, stat
   cards. Use the site's token colors (site.config theme palette), a
   1200x675 default viewBox, system-font text, no scripts. Original,
   zero-copyright, kilobytes in size, unique to the site.
3. Stock photos (`strategy: stock` or `mixed`, for niches needing real
   photography):

   ```bash
   python scripts/fetch_stock_images.py --query "english query" \
       --slug article-slug --out-dir public/img --count 2
   ```

   Requires PEXELS_API_KEY in .env. Use the printed manifest for
   dimensions and add a discreet photographer credit near the image or
   in the footer per Pexels guidelines.
4. Wire every image per optimize-images rules: descriptive alt in the
   article language, explicit width/height, lazy below the fold (hero
   eager + fetchpriority high), descriptive filename, entry in the
   image sitemap (`images` field of generate_sitemap.py input).
5. The og-image card (generate_og_image.py) is separate and still
   per-article.

## Google-optimal size standards

- Hero/featured: 1600x900 (16:9), the LCP element, eager +
  fetchpriority high.
- Content images: at least 1200px wide (Google Discover large-preview
  eligibility; SeoHead already emits max-image-preview:large).
- SVG diagrams: viewBox 1200x675 default.
- og-image: 1200x630. Favicons: the standard five-size set.
- WebP for photos (fetch_stock_images.py outputs 1600px WebP), SVG for
  diagrams; every image with explicit width/height.

## Quality checklist

- Every article has at least `images.min` images; visual-review fails
  imageless articles.
- SVGs are original and content-derived, never decorative filler.
- Stock photos carry credit; no image ships without alt and dimensions.
