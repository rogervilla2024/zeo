# Composition recipes

Named layout recipes for the composition step. Pick ONE from each
group, record the combo (e.g. `H2+N1+L2+F3`) in the design brief, and
never repeat a combo across the fleet - two sites sharing palette OR
layout is a distinctiveness failure; sharing both is unshippable.
Every sketch uses the shipped hooks (`.site-hero`, `header.container`,
`.post-list`, `.site-footer`, `.with-aside`) so it drops into
`src/styles/site.css` and composes with any variant baseline. All
zero-JS.

## Heroes (H)

### H1 - Gradient panel
Rounded card with a layered gradient and a pill CTA. Confident,
product-ish. Good for: guides, tools, product sites.
```css
.site-hero { padding: 3rem 2.5rem; border-radius: calc(var(--radius) * 2);
  background: linear-gradient(135deg,
    color-mix(in srgb, var(--color-primary) 18%, var(--color-background)),
    color-mix(in srgb, var(--color-accent) 8%, var(--color-background))); }
```

### H2 - Split hero
Text left, illustration or search right; two columns collapsing on
mobile. Good for: directories, product sites with a hero image.
```css
.site-hero { display: grid; grid-template-columns: 1.1fr 0.9fr;
  gap: 2rem; align-items: center; }
@media (max-width: 767px) { .site-hero { grid-template-columns: 1fr; } }
```

### H3 - Full-bleed band
Edge-to-edge tinted band, content boxed inside. Big-brand feel.
Good for: magazines, travel, entertainment.
```css
.site-hero { max-width: none; border-radius: 0;
  padding-inline: max(1rem, calc((100% - var(--width-site)) / 2));
  background: color-mix(in srgb, var(--color-primary) 92%, black);
  color: var(--color-on-primary, #fff); }
.site-hero-tagline { color: color-mix(in srgb, var(--color-on-primary, #fff) 75%, transparent); }
```

### H4 - Quiet masthead
Type only, generous whitespace, no box. Understated authority.
Good for: health, finance, editorial essays.
```css
.site-hero { padding: 4rem 0 2.5rem; background: none; border: none; }
.site-hero-title { font-size: clamp(2.4rem, 5vw, 3.4rem); }
```

## Headers (N)

### N1 - Sticky pill bar
Translucent sticky bar, nav links as pills with active state. Modern
knowledge-site feel. (Guide/review variants ship a version of this -
restyle the pills, do not stack a second stickiness.)
```css
body > header.container { position: sticky; top: 0;
  backdrop-filter: blur(10px);
  background: color-mix(in srgb, var(--color-background) 88%, transparent); }
body > header.container nav a { padding: 0.35rem 0.8rem; border-radius: 999px; }
```

### N2 - Centered masthead
Brand centered over the nav, separated by a rule. Newspaper feel.
```css
body > header.container { display: block; text-align: center;
  border-bottom: 4px double color-mix(in srgb, var(--color-text) 55%, transparent); }
```

### N3 - Two-tier bar
Slim top row (brand + theme toggle), full-width nav row under it with
a strong bottom border. Portal density.
```css
body > header.container { display: grid; gap: 0.4rem; }
body > header.container nav { display: flex; gap: 0.25rem; width: 100%;
  border-top: 1px solid color-mix(in srgb, var(--color-muted) 25%, transparent);
  padding-top: 0.4rem; }
```

## Listings (L)

### L1 - Uniform card grid
Equal cards, edge-to-edge thumbnails, hover lift. The safe modern
default - pair it with a bolder hero or footer.
```css
.post-list { grid-template-columns: repeat(auto-fill, minmax(19rem, 1fr)); }
```

### L2 - Featured-lead mosaic
First item spans two columns (the feature-card already does this
job); the rest fall into a tighter grid. Front-page energy.
```css
.post-list { grid-template-columns: repeat(auto-fill, minmax(15rem, 1fr)); gap: 0.9rem; }
.feature-card img { aspect-ratio: 24 / 9; }
```

### L3 - Dense board rows
Full-width rows with meta lines instead of cards (the forum
archetype's .thread-list look, usable on any dense portal).
```css
.post-list { display: block; }
.post-list li { display: flex; align-items: baseline; gap: 1rem;
  border-bottom: 1px solid color-mix(in srgb, var(--color-muted) 20%, transparent); }
.post-list li img { display: none; }
```

## Footers (F)

### F1 - Tinted band
Primary-tinted background, three columns, strong top border. Shipped
by the guide variant; tune the tint toward the palette.
```css
.site-footer { background: color-mix(in srgb, var(--color-primary) 8%, var(--color-background));
  border-top: 3px solid var(--color-primary); }
```

### F2 - Masthead echo
Repeats the header treatment (rule style, centered type) so the page
closes the way it opened. Editorial.
```css
.site-footer { background: none; text-align: center;
  border-top: 4px double color-mix(in srgb, var(--color-text) 55%, transparent); }
```

### F3 - Deep footer
Dark (or near-black) band, light text, four columns plus the
newsletter CTA row. Big-portal feel.
```css
.site-footer { background: color-mix(in srgb, var(--color-text) 92%, var(--color-primary));
  color: var(--color-background); }
.site-footer a { color: color-mix(in srgb, var(--color-background) 85%, transparent); }
```

## Block orders (B)

Named homepage.blocks sequences for site.config.json. The B recipe
composes WHAT the homepage is; H/N/L/F compose how it looks. Pick
one (or write a custom list), record it with the combo (e.g.
`H2+N1+L2+F3 / B5`), and set `theme.recipe` in site.config.json so
fleet_report.py can flag two sites sharing both a recipe combo and a
block order. `id:style` modifiers vary a block's view: `directory:list`
(booking rows), `feature:overlay` (title on image), `feature:split`
(half image, half text), `latest:rows` (dense digest).

### B1 - Classic portal
`["feature", "latest", "strips"]` - feature card, latest grid, one
strip per category. The portal default.

### B2 - Magazine lead
`["feature:overlay", "latest", "strips"]` - full-bleed cover story
with the title on the image, then the grid.

### B3 - Dense digest
`["latest:rows", "strips"]` - no feature, straight into a compact
text list. News-wire feel.

### B4 - Booking home
`["directory", "comparison", "feature", "latest"]` - catalog first,
comparison table, then editorial. The directory default.

### B5 - Booking list
`["directory:list", "feature", "latest"]` - entities as full-width
rows with photo left, booking-results style.

### B6 - Comparison-first review
`["comparison", "feature:split", "latest"]` - the table IS the
pitch; a split feature card follows.

### B7 - Product tour
`["quick_facts", "how_to", "feature", "latest"]` - the product
default: facts panel, steps, then guides.

### B8 - Product magazine
`["quick_facts", "feature:overlay", "latest", "strips"]` - facts up
top, then magazine-style editorial.

### B9 - Answer board
`["threads"]` - the forum default: nothing but the board.

### B10 - Board with context
`["quick_facts", "threads"]` - a facts panel above the threads;
good when the niche has hard rules worth pinning.

### B11 - Hybrid portal catalog
`["directory", "feature:split", "latest", "strips"]` - a portal
that sells: catalog lead, split feature, full editorial body.

### B12 - Catalog digest
`["directory:list", "comparison", "latest:rows"]` - all inventory,
minimal editorial; for pure comparison plays.

## Using the recipes

1. Pick H + N + L + F from the niche's mood (step 2 brief), not at
   random: a casino resort site might run H3+N1+L2+F3; a clinical
   health site H4+N2+L1+F2. Then pick the B block order the same
   way - what the visitor DOES decides B, the mood decides the rest.
2. Record the combo in the design brief and the handoff note, and
   write it into `theme.recipe` in site.config.json (e.g.
   `"H3+N1+L2+F3"`) - fleet_report.py reads it and flags identity
   clashes across the portfolio automatically.
3. Check the fleet: if another site already uses the same combo,
   change at least two letters or the block order.
4. The sketches are STARTING points - the identity layer (site.css)
   still restyles surfaces, spacing, and accents on top. A recipe
   combo with the example palette is still a distinctiveness fail.
