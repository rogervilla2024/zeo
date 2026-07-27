"""Tests for the shipped variant stylesheets and their wiring."""

from __future__ import annotations

from pathlib import Path

import pytest

from seo_content_forge.theme_css import (
    VARIANTS,
    ThemeTokens,
    build_css,
    compose_css,
    from_config,
    variant_css,
)

ROOT = Path(__file__).resolve().parents[2]
VARIANT_DIR = ROOT / "templates" / "theme" / "variants"


def test_every_variant_ships_a_stylesheet() -> None:
    assert set(VARIANTS) == {"minimal", "editorial", "guide", "review"}
    for variant in VARIANTS:
        css = variant_css(variant)
        assert len(css) > 1000, f"{variant}.css is too thin to be a real design"
        assert css.isascii(), f"{variant}.css contains non-ASCII bytes"


def test_variant_css_is_zero_js_and_self_contained() -> None:
    for variant in VARIANTS:
        css = variant_css(variant)
        assert "<script" not in css
        assert "@import" not in css
        assert "url(" not in css, f"{variant}.css must not fetch external assets"


def test_variant_css_targets_shipped_hooks() -> None:
    for variant in VARIANTS:
        css = variant_css(variant)
        for hook in (
            ".post-list",
            ".toc",
            ".takeaways",
            ".site-hero",
            ".site-aside",
            ".site-footer",
            "header.container",
        ):
            assert hook in css, f"{variant}.css misses {hook}"
        assert "var(--color-" in css, f"{variant}.css ignores the tokens"
    assert ".verdict" in variant_css("review")
    assert ".pros-cons" in variant_css("review")


def test_variant_css_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="unknown variant"):
        variant_css("fancy")


def test_from_config_normalizes_variant() -> None:
    assert from_config({"theme": {"variant": "GUIDE"}}).variant == "guide"
    assert from_config({"theme": {"variant": "fancy"}}).variant == "minimal"
    assert from_config({}).variant == "minimal"


def test_compose_css_appends_variant_layer() -> None:
    tokens = ThemeTokens(variant="guide")
    composed = compose_css(tokens)
    assert composed.startswith(build_css(tokens))
    assert "Variant: guide" in composed
    assert "Variant: guide" not in build_css(tokens)
