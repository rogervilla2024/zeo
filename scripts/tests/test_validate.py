"""Unit tests for :mod:`seo_content_forge.validate`."""

from __future__ import annotations

from seo_content_forge import jsonld
from seo_content_forge.validate import validate


def test_valid_article_passes() -> None:
    # Arrange
    node = jsonld.article(
        headline="Test",
        url="https://example.com/post",
        author_name="Jane Doe",
        publisher_name="Example",
        publisher_logo="https://example.com/logo.png",
        date_published="2026-01-15T00:00:00Z",
        description="A summary",
        image=["https://example.com/i.png"],
    )

    # Act
    results = validate(node)

    # Assert
    assert results[0].is_valid
    assert results[0].errors == []


def test_missing_required_property_fails() -> None:
    # Arrange: Article without headline
    node = {
        "@context": "https://schema.org",
        "@type": "Article",
        "author": {"@type": "Person", "name": "Jane"},
        "datePublished": "2026-01-15",
    }

    # Act
    result = validate(node)[0]

    # Assert
    assert not result.is_valid
    assert any("headline" in error for error in result.errors)


def test_missing_type_reports_error() -> None:
    result = validate({"@context": "https://schema.org"})[0]
    assert not result.is_valid
    assert result.node_type == "unknown"


def test_recommended_property_is_warning_not_error() -> None:
    # Arrange: valid required fields, missing recommended image
    node = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": "Test",
        "author": {"@type": "Person", "name": "Jane"},
        "datePublished": "2026-01-15",
    }

    # Act
    result = validate(node)[0]

    # Assert
    assert result.is_valid
    assert any("image" in warning for warning in result.warnings)


def test_list_input_returns_result_per_node() -> None:
    nodes = [
        jsonld.breadcrumb([("Home", "https://example.com/")]),
        jsonld.organization(
            "Example", "https://example.com", "https://example.com/l.png"
        ),
    ]
    results = validate(nodes)
    assert len(results) == 2
    assert all(result.is_valid for result in results)


def test_qapage_rules() -> None:
    from seo_content_forge.validate import validate_node

    good = {
        "@context": "https://schema.org",
        "@type": "QAPage",
        "mainEntity": {
            "@type": "Question",
            "name": "Is it safe?",
            "answerCount": 2,
        },
    }
    assert validate_node(good).is_valid
    missing = {"@context": "https://schema.org", "@type": "QAPage"}
    result = validate_node(missing)
    assert not result.is_valid
    assert any("mainEntity" in error for error in result.errors)
