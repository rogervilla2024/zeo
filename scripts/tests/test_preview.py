"""Tests for the variant preview gallery."""

from __future__ import annotations

from pathlib import Path

from fleet_preview import main
from seo_content_forge.preview import (
    build_index,
    build_variant_preview,
    sample_body,
    write_gallery,
)
from seo_content_forge.theme_css import VARIANTS, ThemeTokens


def test_sample_body_exercises_the_shipped_hooks() -> None:
    body = sample_body("minimal")
    # The preview only earns trust if it renders the surfaces a real
    # homepage renders - card grid, chips, entity cards, banner, FAQ,
    # newsletter, search - so a variant is judged on everything.
    for hook in (
        'class="site-nav"', "site-hero", "hero-stats", "hero-search",
        "cta-banner", "feature-card", "section-title", "post-list",
        "post-category", "entity-card", "entity-score", "entity-cta",
        'rel="sponsored nofollow noopener"', 'class="faq"',
        "newsletter-cta", "site-aside", "site-footer",
    ):
        assert hook in body, f"sample body misses {hook}"
    # Self-contained: images are data URIs, no network fetches.
    assert "http://" not in body.replace("http://www.w3.org", "")
    assert "data:image/svg+xml" in body


def test_variant_preview_is_self_contained_and_themed() -> None:
    light = build_variant_preview("noir", ThemeTokens())
    dark = build_variant_preview("noir", ThemeTokens(), dark=True)
    assert light.startswith("<!doctype html>")
    assert "Variant: noir" in light, "composed CSS must include the variant"
    assert "Shared component layer" in light
    assert 'data-theme="light"' in light
    assert 'data-theme="dark"' in dark
    assert "noindex" in light
    assert "<script" not in light


def test_index_lists_every_variant_light_and_dark() -> None:
    index = build_index()
    for variant in VARIANTS:
        assert f'src="{variant}.html"' in index
        assert f'src="{variant}-dark.html"' in index
    assert str(len(VARIANTS)) in index


def test_write_gallery_and_cli(tmp_path: Path) -> None:
    count = write_gallery(tmp_path / "gallery", ThemeTokens())
    # 40 variants x light/dark + index.
    assert count == len(VARIANTS) * 2 + 1
    assert (tmp_path / "gallery" / "index.html").is_file()
    assert (tmp_path / "gallery" / "tundra-dark.html").is_file()

    out = tmp_path / "cli"
    assert main(["--output", str(out)]) == 0
    assert (out / "index.html").is_file()

    # A palette config flows into every preview.
    config = tmp_path / "site.config.json"
    config.write_text(
        '{"theme": {"variant": "guide", "palette": {"primary": "#123456"}}}'
    )
    assert main(["--output", str(out), "--config", str(config)]) == 0
    assert "#123456" in (out / "guide.html").read_text()

    missing = tmp_path / "nope.json"
    assert main(["--output", str(out), "--config", str(missing)]) == 2
