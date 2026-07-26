"""Unit tests for :mod:`seo_content_forge.jsonld`."""

from __future__ import annotations

import pytest

from seo_content_forge import jsonld


def test_article_defaults_date_modified_and_drops_empty() -> None:
    # Arrange / Act
    node = jsonld.article(
        headline="Test",
        url="https://example.com/post",
        author_name="Jane Doe",
        publisher_name="Example",
        publisher_logo="https://example.com/logo.png",
        date_published="2026-01-15T00:00:00Z",
    )

    # Assert
    assert node["@type"] == "BlogPosting"
    assert node["dateModified"] == "2026-01-15T00:00:00Z"
    assert "description" not in node  # empty values are dropped


def test_faq_page_builds_questions() -> None:
    node = jsonld.faq_page([("Q1?", "A1"), ("Q2?", "A2")])
    entities = node["mainEntity"]
    assert isinstance(entities, list)
    assert entities[0]["acceptedAnswer"]["text"] == "A1"


def test_faq_page_empty_rejected() -> None:
    with pytest.raises(ValueError, match="at least one"):
        jsonld.faq_page([])


def test_how_to_positions_are_sequential() -> None:
    node = jsonld.how_to("Do it", [("Step one", "text"), ("Step two", "text")])
    steps = node["step"]
    assert [s["position"] for s in steps] == [1, 2]


def test_breadcrumb_positions() -> None:
    node = jsonld.breadcrumb([("Home", "https://example.com/")])
    assert node["itemListElement"][0]["position"] == 1


def test_product_with_rating() -> None:
    node = jsonld.product(
        name="Widget",
        description="A widget",
        image=["https://example.com/w.png"],
        price="29.99",
        currency="USD",
        rating_value="4.6",
        review_count=12,
    )
    assert node["aggregateRating"]["reviewCount"] == 12
    assert node["offers"]["priceCurrency"] == "USD"


def test_website_search_action_shape() -> None:
    node = jsonld.website_search(
        "Example",
        "https://example.com",
        "https://example.com/s?q={search_term_string}",
    )
    assert node["potentialAction"]["@type"] == "SearchAction"


def test_builders_registry_is_complete() -> None:
    assert set(jsonld.BUILDERS) == {
        "article",
        "faq",
        "howto",
        "breadcrumb",
        "organization",
        "website",
        "product",
        "recipe",
        "video",
        "event",
        "person",
        "localbusiness",
        "jobposting",
        "course",
        "softwareapp",
        "speakable",
    }
