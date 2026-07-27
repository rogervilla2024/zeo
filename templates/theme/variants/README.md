# Theme variants

One skeleton, several looks. Every variant uses the same SEO core
(BaseLayout, SeoHead, Breadcrumbs, Footer, tokens.css) and the same
content blocks; what changes is composition, typography emphasis, and
density. The `theme.variant` key in site.config.json names the
variant; `generate_theme_css.py` appends the matching `*.css` here to
tokens.css automatically, so the variant is applied by construction -
nothing to implement per site. The `.md` file beside each stylesheet
describes its intent for the design-theme skill, which then layers
the site's niche-specific identity (src/styles/site.css) on top.

Why variants matter at portfolio scale: sites sharing one skeleton must
not share one look. Variant plus token palette plus font pair plus the
design-theme pass gives each site a distinct identity with zero extra
maintenance - third-party themes are never adopted.

Picking a variant:

- `minimal` - default for most content sites
- `editorial` - image-led niches (food, travel, lifestyle)
- `guide` - tutorial/documentation-heavy niches
- `review` - comparison and affiliate-style sites

Every variant must still pass the full test suite (`/seo-test`) and the
JS budget (`check_js_budget.py`); a variant never adds scripts, only
layout and CSS.
