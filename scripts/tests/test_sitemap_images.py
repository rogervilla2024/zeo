"""Unit tests for image-sitemap support in :mod:`seo_content_forge.sitemap`."""

from __future__ import annotations

import pytest

from seo_content_forge.sitemap import ImageRef, UrlEntry, render_urlset


def test_images_rendered_with_namespace() -> None:
    # Arrange
    entry = UrlEntry(
        loc="https://example.com/article",
        images=[
            ImageRef(loc="https://example.com/img/hero.webp"),
            ImageRef(loc="https://example.com/img/step-1.webp"),
        ],
    )

    # Act
    xml = render_urlset([entry])

    # Assert
    assert 'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"' in xml
    assert xml.count("<image:image>") == 2
    assert "<image:loc>https://example.com/img/hero.webp</image:loc>" in xml


def test_entry_without_images_has_no_image_tags() -> None:
    xml = render_urlset([UrlEntry(loc="https://example.com/")])
    assert "<image:image>" not in xml


def test_empty_image_loc_rejected() -> None:
    with pytest.raises(ValueError, match="loc"):
        ImageRef(loc="")


def test_image_limit_enforced() -> None:
    images = [ImageRef(loc=f"https://example.com/{i}.png") for i in range(1001)]
    with pytest.raises(ValueError, match="1000"):
        UrlEntry(loc="https://example.com/", images=images)
