"""Extract and validate JSON-LD structured data from an HTML page.

This is the offline half of a rich-results test: it pulls every
``<script type="application/ld+json">`` block out of a page, parses it
(expanding ``@graph`` containers and top-level lists), and runs each node
through :mod:`seo_content_forge.validate`. It catches the failures Google
would report - malformed JSON, missing required properties - before the
page ships. Google's hosted Rich Results Test remains the final arbiter.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from html.parser import HTMLParser

import orjson

from seo_content_forge.validate import ValidationResult, validate_node


class _JsonLdParser(HTMLParser):
    """Collect the text content of every JSON-LD script tag."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[str] = []
        self._in_jsonld = False
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "script":
            attr_map = dict(attrs)
            if (attr_map.get("type") or "").strip().lower() == "application/ld+json":
                self._in_jsonld = True
                self._buffer = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._in_jsonld:
            self._in_jsonld = False
            self.blocks.append("".join(self._buffer))

    def handle_data(self, data: str) -> None:
        if self._in_jsonld:
            self._buffer.append(data)


def extract_jsonld_blocks(html: str) -> list[str]:
    """Return the raw text of every JSON-LD script block in ``html``."""
    parser = _JsonLdParser()
    parser.feed(html)
    return parser.blocks


def _flatten(parsed: object) -> list[dict[str, object]]:
    """Expand top-level lists and ``@graph`` containers into flat nodes."""
    if isinstance(parsed, list):
        nodes: list[dict[str, object]] = []
        for item in parsed:
            nodes.extend(_flatten(item))
        return nodes
    if isinstance(parsed, dict):
        graph = parsed.get("@graph")
        if isinstance(graph, list):
            nodes = []
            for item in graph:
                if isinstance(item, dict):
                    # Nodes inside @graph inherit the container's context.
                    item.setdefault("@context", parsed.get("@context"))
                    nodes.append(item)
            return nodes
        return [parsed]
    return []


@dataclass(slots=True)
class PageStructuredData:
    """All structured data found on one page.

    Args:
        parse_errors: Human-readable descriptions of blocks that were not
            valid JSON.
        results: Validation outcome for every JSON-LD node found.
    """

    parse_errors: list[str] = field(default_factory=list)
    results: list[ValidationResult] = field(default_factory=list)
    consistency_errors: list[str] = field(default_factory=list)

    @property
    def eligible_types(self) -> list[str]:
        """Node types that passed validation, in page order."""
        return [result.node_type for result in self.results if result.is_valid]

    @property
    def has_blocking_errors(self) -> bool:
        """Return ``True`` if any block failed to parse or validate."""
        return (
            bool(self.parse_errors)
            or bool(self.consistency_errors)
            or any(not result.is_valid for result in self.results)
        )


def check_page(html: str) -> PageStructuredData:
    """Extract and validate all JSON-LD on an HTML page.

    Args:
        html: Full HTML source of the page.

    Returns:
        A :class:`PageStructuredData` report. An empty ``results`` list
        with no ``parse_errors`` means the page has no structured data at
        all, which makes it ineligible for every rich result.
    """
    report = PageStructuredData()
    visible = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>|<[^>]+>", " ", html)
    visible = " ".join(visible.split()).lower()
    blocks = extract_jsonld_blocks(html)
    total_bytes = sum(len(block.encode()) for block in blocks)
    if total_bytes > 15000:
        report.consistency_errors.append(
            f"JSON-LD totals {total_bytes} bytes (budget 15000); trim it"
        )
    for index, block in enumerate(blocks, start=1):
        try:
            parsed = orjson.loads(block)
        except orjson.JSONDecodeError as exc:
            report.parse_errors.append(f"block {index}: invalid JSON ({exc})")
            continue
        for node in _flatten(parsed):
            report.results.append(validate_node(node))
            if node.get("@type") == "FAQPage":
                entities = node.get("mainEntity")
                for entity in entities if isinstance(entities, list) else []:
                    question = (
                        str(entity.get("name", "")) if isinstance(entity, dict) else ""
                    )
                    if question and question.lower() not in visible:
                        report.consistency_errors.append(
                            f"FAQ question not visible on page: {question[:60]}"
                        )
            rating = node.get("aggregateRating")
            if isinstance(rating, dict):
                value = str(rating.get("ratingValue", ""))
                if value and value not in visible:
                    report.consistency_errors.append(
                        f"ratingValue {value} not visible on page"
                    )
    return report
