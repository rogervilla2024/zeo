"""Tests for the shipped variant stylesheets and their wiring."""

from __future__ import annotations

from pathlib import Path

import pytest

from seo_content_forge.theme_css import (
    VARIANTS,
    ThemeTokens,
    build_css,
    components_css,
    compose_css,
    from_config,
    variant_css,
)

ROOT = Path(__file__).resolve().parents[2]
VARIANT_DIR = ROOT / "templates" / "theme" / "variants"

# The aesthetic surfaces every character layer must take a stance on.
CHARACTER_HOOKS = (
    ".site-hero",
    "header.container",
    ".post-list",
    ".section-title",
    ".feature-card",
    ".toc",
    ".takeaways",
    ".site-aside",
    ".site-footer",
)

# The functional surfaces styled ONCE in components.css.
COMPONENT_HOOKS = (
    ".quick-facts",
    ".howto-steps",
    ".entity-card",
    ".comparison",
    ".embed-frame",
    ".hero-search",
    ".hero-stats",
    ".entity-score",
    ".entity-cta",
    ".entity-group",
    ".entity-grid--list",
    ".feature-card--overlay",
    ".feature-card--split",
    ".post-list--rows",
    ".entity-panel",
    ".gallery",
    ".thread-list",
    ".reply-card",
    ".pagination",
    ".not-found",
)


def test_forty_variants_ship_stylesheets() -> None:
    assert len(VARIANTS) == 40
    assert len(set(VARIANTS)) == 40
    for variant in VARIANTS:
        css = variant_css(variant)
        assert len(css) > 1000, f"{variant}.css is too thin to be a real design"
        assert css.isascii(), f"{variant}.css contains non-ASCII bytes"


def test_variant_css_is_zero_js_and_self_contained() -> None:
    for source in (components_css(), *(variant_css(v) for v in VARIANTS)):
        assert "<script" not in source
        assert "@import" not in source
        assert "url(" not in source, "stylesheets must not fetch external assets"


def test_components_layer_styles_functional_surfaces_once() -> None:
    components = components_css()
    for hook in COMPONENT_HOOKS:
        assert hook in components, f"components.css misses {hook}"
    assert "var(--color-" in components


def test_every_variant_takes_an_aesthetic_stance() -> None:
    for variant in VARIANTS:
        css = variant_css(variant)
        for hook in CHARACTER_HOOKS:
            assert hook in css, f"{variant}.css misses {hook}"
        assert "var(--color-" in css, f"{variant}.css ignores the tokens"
    assert ".verdict" in variant_css("review")
    assert ".pros-cons" in variant_css("review")


def test_variants_are_not_clones() -> None:
    # Forty names must be forty designs: no two character layers may
    # be byte-identical, and the fleet needs real spread in the
    # section-title / header / hero treatments.
    sources = {variant: variant_css(variant) for variant in VARIANTS}
    assert len(set(sources.values())) == len(VARIANTS), (
        "two variants ship identical stylesheets"
    )


def test_variant_catalog_documents_every_variant() -> None:
    # variants.md is how a builder picks from forty options - every
    # shipped variant must appear there, so none is undiscoverable.
    catalog = (ROOT / "skills" / "design-theme" / "variants.md").read_text()
    for variant in VARIANTS:
        assert f"`{variant}`" in catalog, f"variants.md misses {variant}"


def test_variant_css_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="unknown variant"):
        variant_css("fancy")


def test_from_config_normalizes_variant() -> None:
    assert from_config({"theme": {"variant": "GUIDE"}}).variant == "guide"
    assert from_config({"theme": {"variant": "fancy"}}).variant == "minimal"
    assert from_config({"theme": {"variant": "cinema"}}).variant == "cinema"
    assert from_config({}).variant == "minimal"


def test_compose_css_layers_tokens_components_variant() -> None:
    tokens = ThemeTokens(variant="guide")
    composed = compose_css(tokens)
    assert composed.startswith(build_css(tokens))
    assert "Variant: guide" in composed
    assert "Shared component layer" in composed
    assert composed.index("Shared component layer") < composed.index(
        "Variant: guide"
    ), "components must be composed before the variant layer"
    assert "Variant: guide" not in build_css(tokens)
