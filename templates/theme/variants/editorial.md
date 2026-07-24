# Variant: editorial

Magazine feel for image-led niches (food, travel, lifestyle, visual
how-to).

Layout:

- Home: featured story hero (image + headline overlay or side-by-side),
  then a responsive card grid (image, category label, title, one-line
  description) of recent posts by cluster.
- Article page: full-width hero image (the LCP element: explicit
  dimensions, fetchpriority high, never lazy), then the minimal
  variant's article order beneath at `--max-width`.
- Category label on cards links to the pillar page - visible cluster
  navigation.

Typography and color:

- Heading font gets personality here (a serif or display stack in the
  tokens); body stays highly readable.
- `--color-accent` is used for category labels and small UI accents.

Rules:

- Every card image ships width/height and lazy-loads (they are below
  the fold); only the hero is eager.
- Card grids are CSS grid, no carousel scripts - the JS budget still
  applies unchanged.
- Image discipline is mandatory: descriptive filenames, alt text, and
  entries in the image sitemap (generate_sitemap.py `images`).
