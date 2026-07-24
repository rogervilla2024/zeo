"""Unit tests for :mod:`seo_content_forge.sitemap`."""

from __future__ import annotations

import pytest

from seo_content_forge.sitemap import (
    MAX_URLS_PER_FILE,
    Alternate,
    UrlEntry,
    build_sitemaps,
    render_index,
    render_urlset,
)


def test_render_urlset_includes_all_fields() -> None:
    # Arrange
    entry = UrlEntry(
        loc="https://example.com/a?x=1&y=2",
        lastmod="2026-01-15",
        changefreq="daily",
        priority=0.8,
        alternates=[Alternate("de", "https://example.com/de/a")],
    )

    # Act
    xml = render_urlset([entry])

    # Assert
    assert "<loc>https://example.com/a?x=1&amp;y=2</loc>" in xml
    assert "<changefreq>daily</changefreq>" in xml
    assert "<priority>0.8</priority>" in xml
    assert 'hreflang="de"' in xml
    assert xml.startswith('<?xml version="1.0" encoding="UTF-8"?>')


def test_invalid_changefreq_rejected() -> None:
    # Arrange / Act / Assert
    with pytest.raises(ValueError, match="changefreq"):
        UrlEntry(loc="https://example.com/", changefreq="often")


def test_priority_out_of_range_rejected() -> None:
    with pytest.raises(ValueError, match="priority"):
        UrlEntry(loc="https://example.com/", priority=1.5)


def test_empty_loc_rejected() -> None:
    with pytest.raises(ValueError, match="loc"):
        UrlEntry(loc="")


def test_build_sitemaps_single_file() -> None:
    # Arrange
    entries = [UrlEntry(loc=f"https://example.com/{i}") for i in range(3)]

    # Act
    files = build_sitemaps(entries, index_base_url="https://example.com")

    # Assert
    assert set(files) == {"sitemap.xml"}


def test_build_sitemaps_splits_and_indexes() -> None:
    # Arrange
    entries = [
        UrlEntry(loc=f"https://example.com/{i}") for i in range(MAX_URLS_PER_FILE + 5)
    ]

    # Act
    files = build_sitemaps(entries, index_base_url="https://example.com/")

    # Assert
    assert "sitemap-index.xml" in files
    assert "sitemap-1.xml" in files
    assert "sitemap-2.xml" in files
    assert "https://example.com/sitemap-1.xml" in files["sitemap-index.xml"]


def test_build_sitemaps_empty_rejected() -> None:
    with pytest.raises(ValueError, match="at least one"):
        build_sitemaps([], index_base_url="https://example.com")


def test_render_urlset_over_limit_rejected() -> None:
    entries = [
        UrlEntry(loc=f"https://example.com/{i}") for i in range(MAX_URLS_PER_FILE + 1)
    ]
    with pytest.raises(ValueError, match="per-file limit"):
        render_urlset(entries)


def test_render_index_with_lastmod() -> None:
    xml = render_index(["https://example.com/sitemap-1.xml"], lastmod="2026-01-01")
    assert "<sitemapindex" in xml
    assert "<lastmod>2026-01-01</lastmod>" in xml
