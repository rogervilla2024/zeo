---
name: adopt-theme
description: Adopt a ready-made open-source theme as the site's design and transplant the toolkit's SEO spine into it: strip demo content, inject schema/robots/llms.txt/sitemap/trust pages, re-tokenize colors from site.config, and pass every gate. Use when the user picked a theme (via find-theme or by URL) and wants it wired into a toolkit site.
---

# Adopt a ready-made theme

Professional design from the ecosystem, SEO spine from the toolkit.

## Inputs

- The chosen theme repository URL and its license (must be permissive:
  MIT/Apache/BSD family - verify before touching it; keep the license
  file and attribution as the license requires).
- site.config.json (palette, fonts, variant intent, legal, authors).

## Instructions

1. Clone the theme into the site project and remove its demo content
   (posts, placeholder images, example authors), keeping layouts,
   components, and styles. Keep LICENSE and add attribution if required.
2. Transplant the SEO spine - the theme's own head is usually weak:
   - replace or augment its head with SeoHead.astro semantics (title
     suffix, canonical, OG/Twitter, hreflang, JSON-LD injection)
   - wire Article + BreadcrumbList JSON-LD into its article layout,
     Organization + WebSite into its base layout (build_jsonld.py +
     validate_schema.py)
   - install robots.txt (AI bots), llms.txt, sitemap wiring, favicons,
     og-image, trust pages + footer links, exactly as bootstrap-site
     specifies
3. Re-tokenize the look: map the theme's colors/fonts to the
   site.config theme tokens (or set the config from the theme's
   palette, then adjust) so the same theme looks different per site.
   Keep the theme's layout quality - do not flatten its design into
   the fallback skeleton.
4. Wire the toolkit content blocks where the theme lacks them (FAQ
   accordion, ArticleMeta with visible updated date, RelatedPosts);
   reuse the theme's own equivalents when they are better.
5. Run every gate and fix until green: check_rich_results.py on built
   pages, check_js_budget.py (themes often carry dead scripts - remove
   them), check_agent_ready.py post-deploy, and the visual-review
   skill's screenshot pass.

## Output

- The adopted theme integrated and passing all gates, plus a note on
  what was stripped, injected, and re-tokenized, and the license
  attribution status.

## Quality checklist

- License verified permissive; LICENSE file and required attribution
  retained.
- No demo/placeholder content survives anywhere (grep for it).
- All schema validates on built pages; robots/llms/sitemap present.
- JS budget passes after dead-script removal.
- visual-review passed at all three viewports.
