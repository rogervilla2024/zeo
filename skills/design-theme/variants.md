# Variant catalog

Forty aesthetic baselines (`theme.variant`). Each is a CHARACTER
layer - type stance, header, hero, cards, titles, footer - composed
on top of the shared functional layer (components.css), so every
variant supports every archetype, block, and block style. Pick by
the niche's mood, then art-direct on top (site.css); the variant is
the floor, never the finished design. Two fleet sites should not
share a variant unless palette, recipe combo, AND block order all
differ.

## Reading-first

- `minimal` - quiet chronological blog; type does the work.
- `zen` - space as structure; centered, borderless, meditative.
- `tundra` - spare nordic hush; muted contrast, wide leading.
- `paper` - warm print stock; dashed rules, centered masthead.
- `folio` - airy editorial folio; drop cap, generous whitespace.
- `docs` - knowledge-base calm; left-bar headings, reference accents.

## Magazine / news

- `editorial` - magazine features; strong hierarchy.
- `magazine` - image-forward cover stories, dark footer.
- `news` - dense headline desk; datelines, tight rhythm.
- `gazette` - broadsheet with double rules and small caps.
- `ledger` - financial rows; tabular numerics discipline.
- `cinema` - poster-dark drama; marquee uppercase, tall cards.

## Guides / knowledge

- `guide` - topic-cluster knowledge site.
- `atlas` - field-guide wayfinding; dotted borders, wide tracking.
- `alpine` - crisp cold clarity; thin frames, frost tints.
- `clinic` - precise clinical trust; pill labels, 1px rules.
- `harbor` - calm nautical order; rope rules, badge flags.
- `prairie` - earthy roomy homestead; double ground rules.

## Product / conversion

- `review` - product/comparison site; verdicts and pros/cons.
- `landing` - single-purpose conversion; centered hero, big CTA.
- `studio` - portfolio confidence; oversized titles, hover lift.
- `chrome` - glassy precision; translucent panels, 1px highlights.
- `quartz` - faceted cool gradients; clipped hero corner.
- `orbit` - spacefaring dark panel; ringed markers, wide tracking.

## Warm / lifestyle

- `pastel` - soft rounded friendliness; tinted tiles.
- `botanic` - organic growth; leaf-round corners, accent tints.
- `bloom` - light floral lift; pill nav, halo hovers.
- `atelier` - handmade workshop; stitched (dashed) borders.
- `velvet` - deep plush evening; dark band hero, roomy cards.
- `ember` - warm glow; gradient accents, glowing hovers.

## Bold / loud

- `brutal` - raw blocks, hard edges, offset slabs, zero radius.
- `noir` - high-contrast night edition; ink rules.
- `arcade` - playful chunky energy; stepped underlines.
- `retro` - seventies stripes and fat underlines.
- `forge` - industrial heavyweight; riveted separators.
- `bazaar` - busy market chips; two-accent alternating tiles.

## Structured / technical

- `terminal` - mono console readout; prompt markers.
- `luxe` - hairline high-end restraint; tracked uppercase serif.
- `marine` - coastal air; wave rules, tracked nav.
- `mosaic` - tiled rhythm; alternating tile spans.

## Choosing

0. LOOK first: `python scripts/fleet_preview.py --output preview`
   renders all forty (light AND dark, same sample content) into
   preview/index.html - pass `--config site.config.json` to see them
   in the site's own palette.
1. Shortlist 3 by mood group, pick the one whose signature detail
   (each file's last block) matches the niche's temperament - and
   check the shortlist's DARK previews before committing: a
   signature that vanishes on the dark palette disqualifies the
   pick (visual-review fails it later anyway).
2. The palette, T pairing, H/N/L/F recipes, and B block order do the
   rest of the differentiation - a variant shared between two sites
   with different everything-else is acceptable; identical combos
   are not (fleet_report.py flags them).
3. After choosing, regenerate tokens.css; the variant name lands in
   the fleet Identity column via theme.variant automatically.
