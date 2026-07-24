# Theme variants

One skeleton, several looks. Every variant uses the same SEO core
(BaseLayout, SeoHead, Breadcrumbs, Footer, tokens.css) and the same
content blocks; what changes is composition, typography emphasis, and
density. The `theme.variant` key in site.config.json names the variant;
the site-bootstrap-architect implements the chosen spec on top of
BaseLayout.

Why variants matter at portfolio scale: sites sharing one skeleton must
not share one look. Variant plus token palette plus font pair gives
each site a distinct identity with zero extra maintenance.

Picking a variant:

- `minimal` - default for most content sites
- `editorial` - image-led niches (food, travel, lifestyle)
- `guide` - tutorial/documentation-heavy niches
- `review` - comparison and affiliate-style sites

Every variant must still pass the full test suite (`/seo-test`) and the
JS budget (`check_js_budget.py`); a variant never adds scripts, only
layout and CSS.
