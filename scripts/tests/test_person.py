"""Unit tests for the Person builder and Article author wiring."""

from __future__ import annotations

from seo_content_forge import jsonld
from seo_content_forge.validate import validate


def test_person_builds_and_validates() -> None:
    # Arrange / Act
    node = jsonld.person(
        name="Jane Doe",
        url="https://example.com/authors/jane-doe",
        description="Editor covering the niche for eight years.",
        image="https://example.com/img/jane.jpg",
        job_title="Senior Editor",
        same_as=["https://www.linkedin.com/in/janedoe"],
        works_for="Example Site",
    )

    # Assert
    assert node["@type"] == "Person"
    assert node["worksFor"]["@type"] == "Organization"
    result = validate(node)[0]
    assert result.is_valid


def test_person_minimal_warns_on_sameas() -> None:
    node = jsonld.person(name="Jane Doe", url="https://example.com/authors/jane")
    result = validate(node)[0]
    assert result.is_valid
    assert any("sameAs" in warning for warning in result.warnings)


def test_article_author_url_wires_person() -> None:
    node = jsonld.article(
        headline="T",
        url="https://example.com/post",
        author_name="Jane Doe",
        publisher_name="Example",
        publisher_logo="https://example.com/logo.png",
        date_published="2026-01-15",
        author_url="https://example.com/authors/jane-doe",
    )
    author = node["author"]
    assert author["url"] == "https://example.com/authors/jane-doe"


def test_article_without_author_url_unchanged() -> None:
    node = jsonld.article(
        headline="T",
        url="https://example.com/post",
        author_name="Jane Doe",
        publisher_name="Example",
        publisher_logo="https://example.com/logo.png",
        date_published="2026-01-15",
    )
    assert "url" not in node["author"]


def test_person_in_registry() -> None:
    assert "person" in jsonld.BUILDERS
