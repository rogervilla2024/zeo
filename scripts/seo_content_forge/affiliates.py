"""Central affiliate-link management and rel policy enforcement.

Affiliate links are managed in one table per site (``affiliates.json``)
instead of scattered through articles: the table is the record of what
is monetized, the checker enforces Google's paid-link policy
(``rel="sponsored"`` on every affiliate anchor), and the live probe
catches dead or hijacked destinations before readers do.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


@dataclass(slots=True)
class AffiliateLink:
    """One managed affiliate destination.

    Args:
        link_id: Stable identifier used to reference the link.
        url: Full affiliate URL (with the tracking tag).
        merchant: Merchant or network name, for reporting.
    """

    link_id: str
    url: str
    merchant: str = ""


@dataclass(slots=True)
class AffiliateTable:
    """The parsed affiliates.json content.

    Args:
        links: Managed affiliate links.
        domains: Hosts that always count as affiliate destinations
            (e.g. ``amzn.to``), even for links missing from the table.
    """

    links: list[AffiliateLink] = field(default_factory=list)
    domains: list[str] = field(default_factory=list)


def parse_table(data: object) -> AffiliateTable:
    """Parse the affiliates.json payload.

    Args:
        data: Parsed JSON: ``{"links": [...], "domains": [...]}``.

    Returns:
        The affiliate table.

    Raises:
        ValueError: On malformed entries (missing id or url, duplicate
            ids).
    """
    if not isinstance(data, dict):
        raise ValueError("affiliates file must be a JSON object")
    raw_links = data.get("links", [])
    raw_domains = data.get("domains", [])
    if not isinstance(raw_links, list) or not isinstance(raw_domains, list):
        raise ValueError('"links" and "domains" must be lists')
    links: list[AffiliateLink] = []
    seen: set[str] = set()
    for index, entry in enumerate(raw_links):
        if not isinstance(entry, dict):
            raise ValueError(f"links[{index}] is not an object")
        link_id = str(entry.get("id", "")).strip()
        url = str(entry.get("url", "")).strip()
        if not link_id or not url:
            raise ValueError(f"links[{index}] needs both id and url")
        if link_id in seen:
            raise ValueError(f"duplicate link id {link_id!r}")
        seen.add(link_id)
        links.append(
            AffiliateLink(
                link_id=link_id, url=url, merchant=str(entry.get("merchant", ""))
            )
        )
    domains = [str(domain).lower().removeprefix("www.") for domain in raw_domains]
    return AffiliateTable(links=links, domains=domains)


class _AnchorParser(HTMLParser):
    """Collect (href, rel) for every anchor in a page."""

    def __init__(self) -> None:
        super().__init__()
        self.anchors: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        mapping = dict(attrs)
        href = mapping.get("href") or ""
        rel = mapping.get("rel") or ""
        if href:
            self.anchors.append((href, rel))


def page_anchors(html: str) -> list[tuple[str, str]]:
    """Every (href, rel) anchor pair on a page, in document order."""
    parser = _AnchorParser()
    parser.feed(html)
    return parser.anchors


def _host(url: str) -> str:
    host = urlparse(url).netloc.lower()
    return host.removeprefix("www.")


def is_affiliate(href: str, table: AffiliateTable) -> bool:
    """True when a href is an affiliate destination per the table.

    A link counts as affiliate when it starts with a managed URL or its
    host (or a parent domain) appears in the table's domain list.

    Args:
        href: Anchor href from the page.
        table: The parsed affiliate table.

    Returns:
        Whether the href must carry the sponsored rel.
    """
    if any(href.startswith(link.url) for link in table.links):
        return True
    host = _host(href)
    if not host:
        return False
    return any(
        host == domain or host.endswith("." + domain) for domain in table.domains
    )


def is_registered(href: str, table: AffiliateTable) -> bool:
    """True when a href starts with one of the table's managed URLs."""
    return any(href.startswith(link.url) for link in table.links)


@dataclass(slots=True)
class Violation:
    """One affiliate-policy problem found in the build output.

    Args:
        page: HTML file relative to the scanned directory.
        href: The offending anchor href.
        problem: ``missing-rel`` (no ``rel="sponsored"``) or
            ``unregistered`` (affiliate domain not in the table).
    """

    page: str
    href: str
    problem: str


def scan_dist(dist: Path, table: AffiliateTable) -> list[Violation]:
    """Check every page's affiliate anchors against the policy.

    Args:
        dist: Build output directory.
        table: The parsed affiliate table.

    Returns:
        Violations in page order: affiliate links without a
        ``sponsored`` rel token, and affiliate-domain links that are
        not registered in the table.
    """
    violations: list[Violation] = []
    for page in sorted(dist.rglob("*.html")):
        html = page.read_text(encoding="utf-8", errors="replace")
        relative = str(page.relative_to(dist))
        for href, rel in page_anchors(html):
            if not href.startswith(("http://", "https://")):
                continue
            if not is_affiliate(href, table):
                continue
            tokens = rel.lower().split()
            if "sponsored" not in tokens:
                violations.append(Violation(relative, href, "missing-rel"))
            if not is_registered(href, table):
                violations.append(Violation(relative, href, "unregistered"))
    return violations
