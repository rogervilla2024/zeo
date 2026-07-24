"""Unit tests for :mod:`seo_content_forge.interlink`."""

from __future__ import annotations

from seo_content_forge.interlink import PageRef, apply_links, suggest_links

_ARTICLE = """# Guide to better sleep

Getting enough rest starts with your evening routine.

## Habits

A consistent bedtime routine helps you fall asleep faster. Many people
also find that sleep hygiene improvements pay off within a week.

```
sleep hygiene inside code must not be linked
```

> sleep hygiene in a quote must not be linked

Read our [existing guide](https://example.com/old) about sleep hygiene too.

Caffeine timing matters more than most people think.
"""

_PAGES = [
    PageRef(
        url="https://example.com/sleep-hygiene",
        title="Sleep Hygiene: The Complete Guide",
        keywords=["sleep hygiene"],
    ),
    PageRef(
        url="https://example.com/caffeine",
        title="Caffeine and Sleep",
        keywords=["caffeine timing"],
    ),
    PageRef(
        url="https://example.com/unrelated",
        title="Completely Different Topic",
        keywords=["quantum computing"],
    ),
]


def test_suggests_links_from_body_paragraphs_only() -> None:
    # Act
    suggestions = suggest_links(_ARTICLE, _PAGES)

    # Assert
    urls = {suggestion.url for suggestion in suggestions}
    assert "https://example.com/sleep-hygiene" in urls
    assert "https://example.com/caffeine" in urls
    assert "https://example.com/unrelated" not in urls
    lines = _ARTICLE.splitlines()
    for suggestion in suggestions:
        line = lines[suggestion.line_index]
        assert not line.strip().startswith(("#", ">", "```"))
        assert "](" not in line


def test_one_link_per_target_page() -> None:
    suggestions = suggest_links(_ARTICLE, _PAGES)
    urls = [suggestion.url for suggestion in suggestions]
    assert len(urls) == len(set(urls))


def test_self_link_excluded() -> None:
    suggestions = suggest_links(
        _ARTICLE, _PAGES, article_url="https://example.com/sleep-hygiene/"
    )
    assert all(
        suggestion.url != "https://example.com/sleep-hygiene"
        for suggestion in suggestions
    )


def test_max_links_cap() -> None:
    suggestions = suggest_links(_ARTICLE, _PAGES, max_links=1)
    assert len(suggestions) == 1


def test_apply_links_inserts_markdown() -> None:
    # Arrange
    suggestions = suggest_links(_ARTICLE, _PAGES)

    # Act
    linked = apply_links(_ARTICLE, suggestions)

    # Assert
    assert "[sleep hygiene](https://example.com/sleep-hygiene)" in linked
    assert "[Caffeine timing](https://example.com/caffeine)" in linked
    # Code block and quote remain untouched.
    assert "sleep hygiene inside code must not be linked" in linked
    assert "> sleep hygiene in a quote must not be linked" in linked


def test_no_pages_yields_no_suggestions() -> None:
    assert suggest_links(_ARTICLE, []) == []
