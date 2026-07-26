"""Find built articles whose freshness signal has aged past a cutoff.

Works from the build output, not the source tree: every article page
that meets the toolkit's own standard already carries Article JSON-LD
with ``dateModified``/``datePublished``, so the age check reads the
same signal search engines read, regardless of framework. Stale pages
feed the refresh-content queue (see the content-calendar skill).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import orjson

from seo_content_forge.richresults import extract_jsonld_blocks

ARTICLE_TYPES = ("Article", "BlogPosting", "NewsArticle")


@dataclass(slots=True)
class StaleArticle:
    """One article whose last update is older than the cutoff.

    Args:
        url: Canonical URL from the Article node (or the page path when
            the node has no URL).
        page: HTML file relative to the scanned directory.
        modified: The freshness date the page declares (ISO 8601).
        days_old: Age in days relative to the reference date.
    """

    url: str
    page: str
    modified: str
    days_old: int


def months_ago(reference: date, months: int) -> date:
    """The calendar date ``months`` before ``reference`` (day clamped).

    Args:
        reference: The date to count back from.
        months: Whole months to subtract.

    Returns:
        The resulting date; day-of-month clamps to the target month's
        last day (e.g. Mar 31 minus one month is Feb 28/29).
    """
    total = reference.year * 12 + (reference.month - 1) - months
    year, month = divmod(total, 12)
    month += 1
    for day in (reference.day, 30, 29, 28):
        try:
            return date(year, month, day)
        except ValueError:
            continue
    raise AssertionError("unreachable: day 28 exists in every month")


def _nodes(html: str) -> list[dict[str, object]]:
    """Every JSON-LD node on the page, with @graph containers expanded."""
    nodes: list[dict[str, object]] = []
    for block in extract_jsonld_blocks(html):
        try:
            parsed = orjson.loads(block)
        except orjson.JSONDecodeError:
            continue
        stack = parsed if isinstance(parsed, list) else [parsed]
        for item in stack:
            if not isinstance(item, dict):
                continue
            graph = item.get("@graph")
            if isinstance(graph, list):
                nodes.extend(node for node in graph if isinstance(node, dict))
            else:
                nodes.append(item)
    return nodes


def article_freshness(html: str) -> tuple[str, str] | None:
    """Extract (url, freshness date) from a page's Article JSON-LD.

    Args:
        html: Full HTML source of the page.

    Returns:
        The canonical URL and the ``dateModified`` (falling back to
        ``datePublished``), or ``None`` when the page carries no dated
        Article node.
    """
    for node in _nodes(html):
        raw_type = node.get("@type")
        node_types = raw_type if isinstance(raw_type, list) else [raw_type]
        if not any(
            entry in ARTICLE_TYPES for entry in node_types if isinstance(entry, str)
        ):
            continue
        modified = node.get("dateModified") or node.get("datePublished")
        if not isinstance(modified, str) or not modified:
            continue
        url = node.get("url")
        if not isinstance(url, str) or not url:
            main = node.get("mainEntityOfPage")
            url = main.get("@id", "") if isinstance(main, dict) else ""
        return str(url or ""), modified
    return None


def _parse_iso_date(value: str) -> date | None:
    """Parse the date part of an ISO 8601 date or datetime string."""
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def find_stale(
    dist: Path, reference: date, months: int = 6
) -> tuple[list[StaleArticle], list[str]]:
    """Scan a build output for articles older than ``months`` months.

    Args:
        dist: Build output directory.
        reference: Date to measure age against (usually today).
        months: Staleness cutoff in calendar months.

    Returns:
        Stale articles sorted oldest first, and warnings for article
        pages whose freshness date could not be parsed.
    """
    cutoff = months_ago(reference, months)
    stale: list[StaleArticle] = []
    warnings: list[str] = []
    for page in sorted(dist.rglob("*.html")):
        html = page.read_text(encoding="utf-8", errors="replace")
        found = article_freshness(html)
        if found is None:
            continue
        url, modified = found
        parsed = _parse_iso_date(modified)
        relative = str(page.relative_to(dist))
        if parsed is None:
            warnings.append(f"{relative}: unparseable date {modified!r}")
            continue
        if parsed <= cutoff:
            stale.append(
                StaleArticle(
                    url=url or "/" + relative,
                    page=relative,
                    modified=modified,
                    days_old=(reference - parsed).days,
                )
            )
    stale.sort(key=lambda article: -article.days_old)
    return stale, warnings
