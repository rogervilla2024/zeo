---
name: optimize-images
description: Image SEO for a page or site: descriptive alt text, SEO-friendly filenames, explicit dimensions to prevent layout shift, modern formats, lazy loading, and generated Open Graph share images. Use when the user wants image SEO, alt text written or audited, og:image or social share cards, image compression guidance, or an image-related fix from a readiness or PageSpeed report.
---

# Optimize images for SEO

Make every image pull its weight: discoverable in image search, readable
by agents, fast to load, and rendering a proper share card.

## Inputs

- The page(s) or codebase to work on, and the site context
  (site.config.json when present: brand name, colors, domain).
- The failing checks that triggered this, if any (image-alt from
  check_agent_ready.py, image-related PageSpeed opportunities, missing
  og:image).

## Instructions

1. Audit current images: find `<img>` tags (and CSS backgrounds holding
   content images) across the page or templates. Record for each:
   filename, alt text, dimensions attributes, format, loading attribute.
2. Write alt text where missing or weak. Rules:
   - Describe what the image shows in context, one sentence, no
     "image of" prefix and no keyword stuffing.
   - Decorative images get empty `alt=""`, not a description.
   - The alt should make sense read aloud in place of the image.
3. Fix filenames at the source where practical: descriptive, hyphenated,
   lowercase (`french-press-brewing-steps.webp`, not `IMG_4021.jpg`).
   Update references; add redirects only if the old URLs were indexed.
4. Enforce layout stability and speed:
   - Explicit `width` and `height` (or aspect-ratio CSS) on every
     content image to prevent layout shift.
   - `loading="lazy"` below the fold; never on the LCP (hero) image.
   - Prefer WebP/AVIF with the framework's image component or a build
     step; keep source images under version control, generate variants
     at build time.
5. Generate the Open Graph card for pages that lack one, using the
   toolkit script with the site's colors from site.config.json:

   ```bash
   python scripts/generate_og_image.py --title "Article title" \
       --site-name "Example" --output public/og/article-slug.png
   ```

   Reference it absolutely in the page's og:image (the theme components
   in templates/theme/ do this given the path).
6. Re-run the checks that were failing (check_agent_ready.py for
   image-alt and og-image, check_pagespeed.py for image opportunities)
   and confirm they pass.

## Output

- The list of images changed: alt text written, filenames fixed,
  attributes added, og:image files generated with their paths.
- Re-run check results for anything that was previously failing.

## Quality checklist

- Every content image has descriptive alt; every decorative image has
  empty alt.
- No image ships without dimensions; the LCP image is not lazy-loaded.
- og:image files are 1200x630 PNG and referenced with absolute URLs.
- Alt text reads naturally; no keyword lists.
