"""Smart contextual internal linking for markdown articles.

Internal links are mandatory in this toolkit: every article must link
from its body text to relevant same-site pages at creation time. This
module finds natural anchor phrases inside paragraphs and turns them
into markdown links, with guardrails an SEO editor would apply by hand:

- anchors live in body paragraphs only - never headings, code blocks,
  blockquotes, or existing links
- each target page is linked at most once per article
- total link count is capped so density stays natural
- longer, more specific phrase matches beat shorter ones
- the article never links to itself

Matching is deterministic (case-insensitive phrase search over the
target pages' titles and keywords), so results are reviewable and
repeatable across a large portfolio.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(slots=True)
class PageRef:
    """One linkable page in the site's content inventory.

    Args:
        url: Absolute or root-relative URL of the page.
        title: Page title.
        keywords: Phrases that may serve as anchors for this page,
            in addition to the title.
    """

    url: str
    title: str
    keywords: list[str]


@dataclass(slots=True)
class LinkSuggestion:
    """One proposed internal link.

    Args:
        anchor: Exact text in the article to wrap in a link.
        url: Target page URL.
        line_index: Zero-based line number of the anchor in the article.
        phrase_words: Word count of the matched phrase (specificity).
    """

    anchor: str
    url: str
    line_index: int
    phrase_words: int


def _candidate_phrases(page: PageRef) -> list[str]:
    """Anchor phrases for a page: keywords first, then the title."""
    phrases = [phrase.strip() for phrase in page.keywords if phrase.strip()]
    title = re.sub(r"\s*[|:-].*$", "", page.title).strip()
    if title:
        phrases.append(title)
    # Longest first so specific phrases win over generic ones.
    return sorted(set(phrases), key=lambda phrase: -len(phrase.split()))


def _linkable_lines(markdown: str) -> dict[int, str]:
    """Return body-paragraph lines eligible to hold links.

    Skips headings, list of code fences and their contents, block
    quotes, tables, and lines that already contain a markdown link.
    """
    eligible: dict[int, str] = {}
    in_code = False
    for index, line in enumerate(markdown.splitlines()):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not stripped:
            continue
        if stripped.startswith(("#", ">", "|", "![")):
            continue
        if "](" in line:
            continue
        eligible[index] = line
    return eligible


def suggest_links(
    article_markdown: str,
    pages: list[PageRef],
    article_url: str | None = None,
    max_links: int = 6,
) -> list[LinkSuggestion]:
    """Find contextual internal-link opportunities in an article.

    Args:
        article_markdown: The article body in markdown.
        pages: Content inventory of linkable pages.
        article_url: URL of the article itself, excluded as a target.
        max_links: Maximum links to suggest (density guardrail).

    Returns:
        At most ``max_links`` suggestions, one per target page, ordered
        by phrase specificity (longest matched phrase first).
    """
    eligible = _linkable_lines(article_markdown)
    suggestions: list[LinkSuggestion] = []
    used_anchors: set[str] = set()

    for page in pages:
        if article_url and page.url.rstrip("/") == article_url.rstrip("/"):
            continue
        for phrase in _candidate_phrases(page):
            pattern = re.compile(rf"\b{re.escape(phrase)}\b", re.IGNORECASE)
            match_found = False
            for index, line in eligible.items():
                match = pattern.search(line)
                if not match:
                    continue
                anchor = match.group(0)
                if anchor.lower() in used_anchors:
                    continue
                suggestions.append(
                    LinkSuggestion(
                        anchor=anchor,
                        url=page.url,
                        line_index=index,
                        phrase_words=len(phrase.split()),
                    )
                )
                used_anchors.add(anchor.lower())
                match_found = True
                break
            if match_found:
                break  # one link per target page

    suggestions.sort(key=lambda item: -item.phrase_words)
    return suggestions[:max_links]


def apply_links(article_markdown: str, suggestions: list[LinkSuggestion]) -> str:
    """Insert the suggested links into the article.

    Args:
        article_markdown: The article body in markdown.
        suggestions: Suggestions from :func:`suggest_links`.

    Returns:
        The article with each suggestion's first anchor occurrence on
        its line wrapped as a markdown link.
    """
    lines = article_markdown.splitlines()
    for suggestion in suggestions:
        line = lines[suggestion.line_index]
        pattern = re.compile(rf"\b{re.escape(suggestion.anchor)}\b")
        lines[suggestion.line_index] = pattern.sub(
            f"[{suggestion.anchor}]({suggestion.url})", line, count=1
        )
    trailing_newline = "\n" if article_markdown.endswith("\n") else ""
    return "\n".join(lines) + trailing_newline
