"""Build an ``llms.txt`` file per the llmstxt.org proposal.

``llms.txt`` is a root-level markdown file that tells LLMs and AI agents
what a site is about and which pages matter, in a format they can consume
without crawling the whole site. The format is:

- an H1 with the site name (required)
- a blockquote with a short summary
- optional free-form detail paragraphs
- H2 sections containing markdown link lists, where each entry is
  ``- [title](url): optional note``
- an optional ``## Optional`` section for secondary URLs agents may skip
"""

from __future__ import annotations

from dataclasses import dataclass

# Byte pairs that appear when UTF-8 text is decoded as Latin-1/CP1252
# (e.g. "u with umlaut" becomes "A-tilde 1/4"). Legitimate prose in any
# language essentially never contains these sequences.
_MOJIBAKE_MARKERS: tuple[str, ...] = (
    "\u00c3\u00bc",
    "\u00c3\u00b6",
    "\u00c3\u00a7",
    "\u00c4\u00b1",
    "\u00c5\u009f",
    "\u00c4\u009f",
    "\u00c3\u00a9",
    "\u00c3\u00a8",
    "\u00c2\u00a0",
    "\u00c3\u0083",
)


def looks_mojibake(text: str) -> bool:
    """Return True when text contains double-encoded UTF-8 sequences."""
    return any(marker in text for marker in _MOJIBAKE_MARKERS)


@dataclass(slots=True)
class LinkEntry:
    """One link line inside an ``llms.txt`` section.

    Args:
        title: Human-readable page title.
        url: Absolute URL of the page (a markdown ``.md`` mirror of the
            page where one exists, per the proposal).
        note: Optional short description appended after the link.
    """

    title: str
    url: str
    note: str | None = None

    def render(self) -> str:
        """Render this entry as one markdown list line."""
        line = f"- [{self.title}]({self.url})"
        if self.note:
            line += f": {self.note}"
        return line


def build_llms_txt(
    site_name: str,
    summary: str,
    sections: dict[str, list[LinkEntry]],
    details: str | None = None,
) -> str:
    """Assemble the full ``llms.txt`` content.

    Args:
        site_name: Site or project name for the H1.
        summary: One-or-two sentence description for the blockquote.
        sections: Mapping of section title (H2) to its link entries, in
            insertion order. Use an ``Optional`` section for secondary
            URLs that agents may skip when context is tight.
        details: Optional free-form markdown paragraphs placed between
            the summary and the sections.

    Returns:
        The complete file content, ending with a newline.

    Raises:
        ValueError: If ``site_name`` or ``summary`` is empty, or any
            section has no entries.
    """
    if not site_name or not summary:
        raise ValueError("site_name and summary are required")

    parts: list[str] = [f"# {site_name}", "", f"> {summary}"]
    if details:
        parts += ["", details.strip()]
    for title, entries in sections.items():
        if not entries:
            raise ValueError(f"section {title!r} has no entries")
        parts += ["", f"## {title}", ""]
        parts += [entry.render() for entry in entries]
    return "\n".join(parts) + "\n"
