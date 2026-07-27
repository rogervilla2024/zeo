---
name: visual-review
description: Screenshot-driven design gate: build the site, capture Playwright screenshots at mobile/tablet/desktop widths, critique them against a design checklist, fix, and re-shoot until they pass. Use after bootstrapping or adopting a theme, when the user says the site looks bad or unpolished, or before calling any site visually done.
---

# Visual review gate

Design is a tested gate here, like schema and speed. A site is not
done because it builds; it is done when its screenshots pass review.

## Inputs

- A buildable site project. Playwright with Chromium (install if
  missing: `npm i -D playwright && npx playwright install chromium`).

## Instructions

1. Build the site and serve the output locally (`npx astro preview`
   or a static server on the dist directory).
2. Capture full-page screenshots of the homepage AND one article page
   at three widths, and collect the DevTools console at the same time.
   The toolkit ships the harness - it screenshots 390/768/1440 into
   shots/ and fails on any console error, page exception, or failed
   network request (Chrome DevTools Protocol via Playwright):

   ```bash
   node <toolkit>/templates/ci/visual-check.mjs / /<one-article-slug>/
   ```

   A red console is an automatic fail even when the pixels look fine;
   fix the errors before critiquing the screenshots.

3. Read every screenshot and critique it against the checklist below.
   Be harsh: "acceptable" is not the bar; "a designer shipped this" is.
4. Fix what failed, rebuild, re-shoot, re-review. Iterate until every
   checklist item passes at every width. Then show the user the final
   screenshots.

## Design checklist

- Desktop uses the width: page shell at --width-site (~1200px), only
  article prose at 72ch. A narrow centered column on a 1440px canvas
  is an automatic fail.
- Clear visual hierarchy: one dominant element per screen; heading
  sizes step down meaningfully (fluid scale, not all near body size).
- The header looks designed: aligned nav, spacing, active state - not
  a row of bare links. A header with no navigation menu at all (brand
  only) is an automatic fail.
- Cards and grids align to a consistent gutter; imagery (or icon
  blocks) present where the variant expects them; no large empty
  white voids.
- Spacing rhythm is consistent (multiples of the spacing unit); no
  cramped or orphaned blocks.
- Text contrast passes at a glance in light AND dark mode; accent
  color appears sparingly but visibly.
- Mobile: no horizontal scroll, tap targets comfortable, nav usable.
- Nothing overlaps, wraps awkwardly, or renders as unstyled HTML.
- The article page shows real images (diagrams or photos) in the body;
  an imageless article body is an automatic fail.
- Distinctiveness: the design expresses THIS site's niche - a
  stranger seeing the homepage with the text blurred should sense the
  topic's mood from color, type, and composition. A look
  interchangeable with a starter template, or a palette left at the
  toolkit defaults, is an automatic fail.
- The homepage opens with a designed hero (`.site-hero` composed:
  background treatment, display title, tagline), never a bare h1
  above a list.

## Output

- The final passing screenshots (all six), the list of fixes applied
  across iterations, and any items accepted with a stated reason.

## Quality checklist

- Every checklist item verified on screenshots, not assumed from code.
- Both light and dark mode checked at least on desktop.
- The user sees the final screenshots, not a text claim that it looks
  good.
