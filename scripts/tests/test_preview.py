"""Tests for the variant preview gallery."""

from __future__ import annotations

from pathlib import Path

from fleet_preview import main
from seo_content_forge.preview import (
    ANATOMIES,
    anatomy_body,
    build_anatomy_index,
    build_index,
    build_variant_preview,
    sample_body,
    write_anatomy_gallery,
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

    # The finish dimension: every preview renders with the surface
    # treatment applied, and unknown finishes are a clean error.
    glass = tmp_path / "glass"
    assert main(["--output", str(glass), "--finish", "glass"]) == 0
    assert "Finish: glass" in (glass / "noir.html").read_text()
    assert main(["--output", str(glass), "--finish", "chrome-x"]) == 2


def test_anatomy_bodies_compose_the_shipped_structure() -> None:
    # Twelve A recipes, matching the recipes.md catalog.
    assert len(ANATOMIES) == 12
    # A2 booking funnel: the search box IS the hero, catalog as rows.
    a2 = anatomy_body("minimal", "A2")
    assert "hero--search" in a2 and "entity-grid--list" in a2
    assert "comparison" in a2
    # A3 marketplace: no hero (hidden h1), search in the chrome.
    a3 = anatomy_body("minimal", "A3")
    assert "visually-hidden" in a3 and "header-search" in a3
    assert "entity-grid--shelves" in a3
    # A7 cover story: the image-first hero.
    assert "hero--cover" in anatomy_body("minimal", "A7")
    # A8 signup hero carries the newsletter box inside the hero.
    a8 = anatomy_body("minimal", "A8")
    assert "hero--signup" in a8 and "newsletter-cta" in a8
    # A9 wire: ticker over a compact feed.
    a9 = anatomy_body("minimal", "A9")
    assert "ticker" in a9 and "feed--compact" in a9
    # A10 filter rail: lead-only blocks dock the rail beside them,
    # on the left, holding the facet filters.
    a10 = anatomy_body("minimal", "A10")
    assert 'class="rail-beside left"' in a10 and "Filters" in a10
    # Offer links in the sample stay honestly marked.
    assert 'rel="sponsored nofollow noopener"' in a2


def test_anatomy_gallery_and_cli(tmp_path: Path) -> None:
    out = tmp_path / "anat"
    count = write_anatomy_gallery(out, ThemeTokens(), "noir")
    assert count == len(ANATOMIES) + 1
    a12 = (out / "A12.html").read_text()
    assert "Variant: noir" in a12, "frames must carry the chosen variant"
    assert "post-list--tiles" in a12
    index = build_anatomy_index("noir")
    for code in ANATOMIES:
        assert f'src="{code}.html"' in index

    cli = tmp_path / "cli-anat"
    assert main(["--output", str(cli), "--anatomy", "--variant",
                 "botanic"]) == 0
    assert (cli / "index.html").is_file()
    assert "Variant: botanic" in (cli / "A1.html").read_text()
    assert main(["--output", str(cli), "--anatomy", "--variant",
                 "not-a-theme"]) == 2
