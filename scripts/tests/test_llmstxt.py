"""Unit tests for :mod:`seo_content_forge.llmstxt`."""

from __future__ import annotations

import pytest

from seo_content_forge.llmstxt import LinkEntry, build_llms_txt


def test_full_document_structure() -> None:
    # Arrange
    sections = {
        "Docs": [
            LinkEntry("Quick start", "https://example.com/start.md", "Setup guide")
        ],
        "Optional": [LinkEntry("Changelog", "https://example.com/changelog.md")],
    }

    # Act
    content = build_llms_txt(
        "Example",
        "A test site.",
        sections,
        details="Extra context paragraph.",
    )

    # Assert
    lines = content.splitlines()
    assert lines[0] == "# Example"
    assert "> A test site." in lines
    assert "Extra context paragraph." in lines
    assert "## Docs" in lines
    assert "- [Quick start](https://example.com/start.md): Setup guide" in lines
    assert "- [Changelog](https://example.com/changelog.md)" in lines
    assert content.endswith("\n")


def test_note_is_optional() -> None:
    entry = LinkEntry("Page", "https://example.com/p.md")
    assert entry.render() == "- [Page](https://example.com/p.md)"


def test_empty_site_name_rejected() -> None:
    with pytest.raises(ValueError, match="required"):
        build_llms_txt("", "Summary", {})


def test_empty_section_rejected() -> None:
    with pytest.raises(ValueError, match="no entries"):
        build_llms_txt("Example", "Summary", {"Docs": []})
