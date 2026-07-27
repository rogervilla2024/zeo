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

## Instructions

1. Write a one-paragraph design brief from the niche before touching
   code: the feeling the site should give (e.g. a health-adjacent
   "benefits and harms" site reads calm, clinical, trustworthy - not
   playful; a coffee site reads warm and craft-like), the palette
   direction with concrete hex values, and the typography character.
2. Set the tokens in `site.config.json`:
   - `theme.palette`: primary (the identity color), accent (used
     sparingly), background/surface/text/muted tuned to the same
     temperature; `on-primary` if primary is light.
   - `theme.dark_palette`: same identity in dark; verify contrast.
   - `theme.fonts`: pick stacks that carry the character (system
     stacks are fine; a self-hosted woff2 pair is allowed within the
     theme rules - preloaded, font-display swap).
   - `theme.variant` and `theme.radius` (sharp for technical, soft
     for lifestyle).
3. Regenerate the stylesheet - tokens plus the variant layer come out
   of one command:

   ```bash
   python scripts/generate_theme_css.py --config site.config.json \
       --output src/styles/tokens.css
   ```

4. Add the site-specific layer where the tokens cannot express it:
   `src/styles/site.css` (imported by BaseLayout after tokens.css),
   containing niche touches only - a header device, list markers,
   image treatment, category badge colors. Keep it small; if a rule
   would help every site, it belongs in the variant CSS upstream, not
   here.
5. Every color pair must hold WCAG AA (4.5:1 body text, 3:1 large
   text) in BOTH light and dark modes. Check the pairs actually used:
   text/background, muted/background, on-primary/primary, link/
   background.
6. Hard rules that survive any design: zero JavaScript added; one h1;
   visible focus states kept; the JS and media budgets still pass;
   no external fonts, CSS, or images fetched at runtime.
7. Finish through the visual-review gate: build, screenshot at
   390/768/1440, critique against its checklist, fix, re-shoot until
   it passes. A design that has not passed visual-review does not
   ship - this is the gate that ends "the site looks like a
   skeleton".

## Output

- Updated `site.config.json` theme section, regenerated tokens.css,
  and (when needed) a small `src/styles/site.css`.
- The design brief (one paragraph) recorded in the handoff, so the
  next session restyles deliberately instead of guessing.
- Passing visual-review screenshots at all three widths.

## Quality checklist

- The look expresses the niche; two sites from this toolkit are never
  visually confusable.
- All color pairs pass AA in light and dark.
- Zero-JS preserved; budgets still green; focus states visible.
- visual-review passed at 390/768/1440.
