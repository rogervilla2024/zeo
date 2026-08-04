"""Unit tests for :mod:`seo_content_forge.theme_css`."""

from __future__ import annotations

from seo_content_forge.theme_css import (
    VARIANT_IDENTITY,
    VARIANTS,
    ThemeTokens,
    build_css,
    from_config,
)


def test_defaults_produce_complete_stylesheet() -> None:
    css = build_css(ThemeTokens())
    assert "--color-primary: #0f766e;" in css
    assert "prefers-color-scheme: dark" in css
    assert ':root[data-theme="dark"]' in css
    assert ".skip-link" in css
    assert ":focus-visible" in css


def test_every_variant_carries_its_own_identity() -> None:
    # A variant IS a theme: forty variants must not render as one
    # teal site forty times. Every variant has an identity entry
    # (minimal keeps the classic defaults for continuity) and the
    # fleet spreads across genuinely different primaries.
    assert set(VARIANT_IDENTITY) == set(VARIANTS)
    primaries = set()
    for variant in VARIANTS:
        css = build_css(ThemeTokens(variant=variant))
        line = next(
            row for row in css.splitlines() if "--color-primary:" in row
        )
        primaries.add(line.strip())
    assert len(primaries) >= 30, (
        f"only {len(primaries)} distinct primaries across {len(VARIANTS)} "
        "variants - the fleet would look samey again"
    )
    # Font pairings and radius also vary across the fleet.
    fonts = {
        build_css(ThemeTokens(variant=v)).split("--font-heading:")[1]
        .split(";")[0]
        for v in VARIANTS
    }
    assert len(fonts) >= 5
    # Dark-native themes exist: at least two variants ship a dark
    # background as their LIGHT scheme.
    dark_native = [
        v
        for v in VARIANTS
        if "--color-background: #0" in build_css(ThemeTokens(variant=v))
        or "--color-background: #1" in build_css(ThemeTokens(variant=v))
    ]
    assert len(dark_native) >= 3


def test_config_palette_beats_variant_identity() -> None:
    # The site's explicit palette always wins over the theme's own;
    # an empty config palette means the theme decides.
    themed = build_css(ThemeTokens(variant="botanic"))
    assert "--color-primary: #166534;" in themed
    overridden = build_css(
        ThemeTokens(variant="botanic", palette={"primary": "#123456"})
    )
    assert "--color-primary: #123456;" in overridden
    assert "#166534" not in overridden.split("@media")[0].split("h1")[0]


def test_config_overrides_apply() -> None:
    config: dict[str, object] = {
        "theme": {
            "palette": {"primary": "#123456"},
            "dark_palette": {"background": "#000000"},
            "fonts": {"heading": "Georgia, serif"},
            "radius": "12px",
            "max_width": "65ch",
        }
    }
    css = build_css(from_config(config))
    assert "--color-primary: #123456;" in css
    assert "--color-background: #000000;" in css
    assert "--font-heading: Georgia, serif;" in css
    assert "--radius: 12px;" in css
    assert "--max-width: 65ch;" in css


def test_missing_theme_section_uses_defaults() -> None:
    tokens = from_config({})
    # Empty radius = "the variant decides"; minimal resolves to 8px.
    assert tokens.radius == ""
    css = build_css(tokens)
    assert "--radius: 8px;" in css
    assert "--color-text:" in css
