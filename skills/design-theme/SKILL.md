---
name: design-theme
description: Design a niche-specific visual identity for a site on top of the toolkit's variant baseline: derive palette, typography, and component accents from the site's topic, implement them as token and override changes, and pass the visual-review gate. Use when a new site needs its look, when the user says the site looks generic, bland, or ugly, wants a redesign or restyle, or after bootstrapping - every site gets this pass before it is called done.
---

# Design a niche-specific theme

The toolkit never adopts third-party themes: the AI designs each
site's look, so every site is visually distinct and topically
appropriate while sharing the same tested skeleton. The shipped
variant stylesheets (templates/theme/variants/*.css, appended to
tokens.css by generate_theme_css.py) are the floor - a site can never
render unstyled - and this skill builds the site's identity on top.

## Inputs

- `site.config.json`: niche, audience, brand voice, current theme
  section. The design must express THIS site's topic, not a generic
  "clean blog" default.
- The layout variant (`theme.variant`): minimal, editorial, guide, or
  review. Chosen by content type: reading-first blog -> minimal;
  magazine/feature writing -> editorial; topic-cluster knowledge site
  -> guide; product/comparison site -> review.

## The bar

Design like the strongest publisher in the niche, not like a starter
template with new colors. The variant baseline exists so nothing can
look broken - your job starts ABOVE it. Be bold: a timid pass (default
palette, bare hero, beige cards) fails visual-review's
distinctiveness check. Rough calibration: the site.css of a finished
design is typically 150-400 lines of deliberate, site-specific CSS -
if yours is 30 lines, you restyled nothing.

## Instructions

1. First decide the site ARCHETYPE - what does the visitor come to
   DO? Set `site_type` in site.config.json; the homepage composes
   itself from it:
   - `portal` (default): read across a topic - feature card, latest
     grid, category strips.
   - `product`: see/try ONE game, app, or product - hero CTA (to
     `/demo/` or the pillar guide), `product.facts` quick-facts
     panel, `product.steps` how-it-works strip, then the guides. Put
     any third-party demo embed on a dedicated page with
     EmbedFrame.astro, never the homepage.
   - `directory`: choose among entities (hotels, tools, venues) -
     fill `src/content/entities/` with attribute-typed entries; the
     homepage renders entity cards plus a comparison table, each
     linking to its review article.
   A single-product niche shipped as a generic article portal is a
   composition failure, whatever the colors look like.

2. Write the design brief from the niche before touching code: the
   mood in one sentence, then concrete choices. Anchor on an
   archetype and push it:
   - health/science: calm, clinical, high-trust - cool palette,
     generous whitespace, precise type
   - travel/leisure/entertainment: vivid and atmospheric - saturated
     or dark-luxe palette, large display type, imagery-forward
   - food/craft/lifestyle: warm, textured, inviting - earthy palette,
     soft radius, friendly serif
   - finance/legal/b2b: confident and sober - deep neutrals plus one
     strong accent, sharp radius, structured grids
   - tech/tools: crisp, modern - near-black or paper-white base,
     electric accent, mono details
   The mood must be guessable from a screenshot with the text blurred.
3. Set the tokens in `site.config.json`:
   - `theme.palette`: primary (the identity color), accent (used
     sparingly), background/surface/text/muted tuned to the same
     temperature; `on-primary` if primary is light. Never leave the
     example palette in place - unchanged defaults are a fail.
   - `theme.dark_palette`: same identity in dark; verify contrast.
   - `theme.fonts`: a real pairing that carries the character -
     self-hosted woff2 (e.g. from Fontsource) is encouraged for the
     heading font: preloaded, `font-display: swap`, subset if large.
     System stacks are the fallback, not the goal.
   - `theme.variant` and `theme.radius` (sharp for technical, soft
     for lifestyle).
4. Regenerate the stylesheet - tokens plus the variant layer come out
   of one command:

   ```bash
   python scripts/generate_theme_css.py --config site.config.json \
       --output src/styles/tokens.css
   ```

5. Choose the site's COMPOSITION deliberately - layout is part of the
   identity, and two sites must not share it any more than they share
   a palette:
   - header: nav style from the `nav` array in site.config.json
     (fill it with the site's real sections) - inline links, centered
     masthead, or pill/button links; style `.site-nav` accordingly
   - columns: single column, right sidebar, or left sidebar. The
     `.with-aside` grid utility (tokens.css) plus `Sidebar.astro`
     make two-column pages one wrapper away - fill the aside with
     what serves THIS site: cluster navigation on guide sites,
     popular/recent articles on magazines, category links on review
     sites. Sidebars belong on listing and article pages, never
     forced onto trust pages.
   - density and shape: card-heavy vs airy lists, sharp vs soft
     radius, boxed vs full-bleed hero.
6. Art-direct the site in `src/styles/site.css` (loaded by BaseLayout
   after tokens.css). This is the identity layer - make it as large
   as the design needs. Cover, at minimum:
   - the hero (`.site-hero`): the first screen must look composed -
     background treatment (tint, gradient, or generous negative
     space), display-size title, tagline, CTA
   - the header: brand weight, nav styling, hover/active states
   - the card system (`.post-list li`): surfaces, borders or
     elevation, hover response, category/topic accents
   - the article page: heading treatments, block accents
     (takeaways/toc/faq), image framing
   - the footer: styled, not an afterthought
   Only the SEO mechanics are off-limits; every visual surface is
   yours to redesign.
7. Every color pair must hold WCAG AA (4.5:1 body text, 3:1 large
   text) in BOTH light and dark modes. Check the pairs actually used:
   text/background, muted/background, on-primary/primary, link/
   background.
8. Hard rules that survive any design: zero JavaScript added; one h1;
   visible focus states kept; the JS and media budgets still pass;
   no external fonts, CSS, or images fetched at runtime (self-hosted
   assets only).
9. Finish through the visual-review gate: build, screenshot at
   390/768/1440, critique against its checklist - including the
   distinctiveness check - fix, re-shoot until it passes. A design
   that has not passed visual-review does not ship.

## Output

- Updated `site.config.json` (theme section plus the `nav` array),
  regenerated tokens.css, and the site's identity layer in
  `src/styles/site.css`.
- The design brief (mood, palette, composition) recorded in the
  handoff, so the next session restyles deliberately instead of
  guessing.
- Passing visual-review screenshots at all three widths.

## Quality checklist

- The look AND the composition express the niche; two sites from this
  toolkit are never visually confusable - not in color, not in layout.
- The header carries a real nav; sidebar (if any) serves the content.
- All color pairs pass AA in light and dark.
- Zero-JS preserved; budgets still green; focus states visible.
- visual-review passed at 390/768/1440.
