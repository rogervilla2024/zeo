"""Tests for the speakable builder and its validation rules."""

from __future__ import annotations

import pytest

from seo_content_forge.jsonld import BUILDERS, speakable
from seo_content_forge.validate import validate_node


def test_speakable_css_selectors_validates_clean() -> None:
    node = speakable(
        name="How to store coffee",
        url="https://e.com/blog/store-coffee/",
        css_selectors=[".article-summary", ".key-takeaways"],
    )
    assert node["@type"] == "WebPage"
    spec = node["speakable"]
    assert isinstance(spec, dict)
    assert spec["cssSelector"] == [".article-summary", ".key-takeaways"]
    assert "xpath" not in spec
    result = validate_node(node)
    assert result.is_valid
    assert result.warnings == []


def test_speakable_xpath_and_page_type() -> None:
    node = speakable(
        name="T",
        url="https://e.com/",
        xpaths=["/html/head/title"],
        page_type="NewsArticle",
    )
    assert node["@type"] == "NewsArticle"
    spec = node["speakable"]
    assert isinstance(spec, dict) and spec["xpath"] == ["/html/head/title"]


def test_speakable_requires_a_selector() -> None:
    with pytest.raises(ValueError, match="css_selectors or xpaths"):
        speakable(name="T", url="https://e.com/")


def test_validate_flags_malformed_speakable() -> None:
    node: dict[str, object] = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": "T",
        "url": "https://e.com/",
        "speakable": {"@type": "SpeakableSpecification", "cssSelector": []},
    }
    result = validate_node(node)
    assert not result.is_valid
    assert any("cssSelector or xpath" in error for error in result.errors)

    node["speakable"] = {"cssSelector": [".summary"]}
    result = validate_node(node)
    assert any("SpeakableSpecification" in error for error in result.errors)

    node["speakable"] = ["not an object"]
    result = validate_node(node)
    assert any("not an object" in error for error in result.errors)


def test_validate_accepts_speakable_list_and_string_selector() -> None:
    node: dict[str, object] = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "T",
        "author": {"@type": "Person", "name": "A"},
        "datePublished": "2026-01-01",
        "speakable": [
            {"@type": "SpeakableSpecification", "cssSelector": ".summary"},
            {"@type": "SpeakableSpecification", "xpath": ["/html/head/title"]},
        ],
    }
    assert validate_node(node).is_valid


def test_speakable_registered() -> None:
    assert BUILDERS["speakable"] is speakable
