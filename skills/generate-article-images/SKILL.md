---
name: generate-article-images
description: Give every article its images: a topic-depicting hero illustration authored by the AI (default), original SVG diagrams generated from the article's own content, optional stock photos via the Pexels adapter, all optimized and wired into alt text, dimensions, lazy loading, and the image sitemap. Use when articles lack images or a hero, when the user asks for article visuals, illustrations, diagrams, or stock photos, or when visual-review fails an imageless article.
---

# Generate article images

An article never ships imageless, and it never ships without a hero:
one image that depicts the TOPIC itself, at the top of the article.
Body strategy comes from site.config.json `images.strategy` (default
`svg-first`); the hero mode comes from `images.hero` (default
`illustration`).

## Instructions

1. Hero first (`images.hero`, default `illustration`). Exactly one per
   article, rendered as the first visual, eager-loaded as the LCP
   (raw `<img>` in the markdown with width/height and
   `fetchpriority="high"`, never `loading="lazy"`).
   - `illustration` (default): author an original SVG scene that
     DEPICTS the subject - a steaming tea glass with a thyme sprig,
     not a chart about it. Concrete subject imagery, the site's token
     palette, 1600x900 viewBox, little or no text, no scripts.
     Original, zero-license, kilobytes, and visually consistent with
     the design-theme identity. Illustration heroes stay in-page:
     leave the frontmatter `image` unset so og:image and the Article
     JSON-LD keep using the generated raster og card.
   - `photo`: fetch one real photograph instead:

     ```bash
     python scripts/fetch_stock_images.py --query "english query" \
         --slug article-slug --out-dir public/img --hero
     ```

     Outputs `<slug>-hero.webp` cover-cropped to 1600x900. Set it as
     the frontmatter `image` (raster, so og:image and Article JSON-LD
     may use it) and add it to the image sitemap. Falls back to
     `illustration` when PEXELS_API_KEY is missing or no result
     genuinely matches the subject - never block shipping, never use
     an off-topic photo.
2. Read the article and pick `images.min` to `images.max` (default 2-4)
   visual opportunities beyond the hero: the concept a diagram explains
   better than a paragraph, steps as a flow, comparisons as a visual
   table, key stats as a stat card.
3. SVG-first (default): author original SVGs yourself from the article
   content - step flows, comparison cards, process diagrams, stat
   cards. Use the site's token colors (site.config theme palette), a
   1200x675 default viewBox, system-font text, no scripts. Original,
   zero-copyright, kilobytes in size, unique to the site.
4. Stock photos (`strategy: stock` or `mixed`, for niches needing real
   photography in the body):

   ```bash
   python scripts/fetch_stock_images.py --query "english query" \
       --slug article-slug --out-dir public/img --count 2
   ```

   Requires PEXELS_API_KEY in .env. Use the printed manifest for
   dimensions. The Pexels license does not require attribution; add a
   discreet photographer credit only if the site chooses to.
5. Wire every image per optimize-images rules: descriptive alt in the
   article language, explicit width/height, lazy below the fold (hero
   eager + fetchpriority high), descriptive filename, entry in the
   image sitemap (`images` field of generate_sitemap.py input).
6. The og-image card (generate_og_image.py) is separate and still
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

- Every article has a hero that depicts the topic itself (illustration
  by default, photo when configured), eager-loaded as the LCP.
- Every article has at least `images.min` images; visual-review fails
  imageless articles.
- SVGs are original and content-derived, never decorative filler;
  hero illustrations depict the subject, not a diagram of it.
- No image ships without alt and dimensions; photographer credit is
  optional (Pexels requires none).
