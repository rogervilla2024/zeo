"""Unit tests for :mod:`seo_content_forge.theme_css`."""

from __future__ import annotations

from seo_content_forge.theme_css import ThemeTokens, build_css, from_config


def test_defaults_produce_complete_stylesheet() -> None:
    css = build_css(ThemeTokens())
    assert "--color-primary: #0f766e;" in css
    assert "prefers-color-scheme: dark" in css
    assert ':root[data-theme="dark"]' in css
    assert ".skip-link" in css
    assert ":focus-visible" in css


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
    assert tokens.radius == "8px"
    assert "--color-text:" in build_css(tokens)
