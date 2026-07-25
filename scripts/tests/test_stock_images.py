"""Unit test for the stock-image filename slugifier."""

from __future__ import annotations

from fetch_stock_images import slugify


def test_slugify_seo_names() -> None:
    assert slugify("French Press: Brewing!") == "french-press-brewing"
    assert slugify("   ") == "image"
