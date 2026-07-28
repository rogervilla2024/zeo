"""Live freshness signals from a deployed site's sitemap or feed.

Sites rarely die loudly; they die by silently going stale when the
publishing rhythm stalls. The dynamic sitemap carries a ``lastmod``
per article and the RSS feed a ``pubDate``, so the deployed site
itself proves when content last moved - no local state needed. The
freshness live gate turns a stalled rhythm into a red line on the
score card instead of a slow discovery months later.
"""

from __future__ import annotations

import re
from datetime import date
from email.utils import parsedate_to_datetime

_LASTMOD = re.compile(r"<lastmod>([^<]+)</lastmod>", re.IGNORECASE)
_PUBDATE = re.compile(r"<pubDate>([^<]+)</pubDate>", re.IGNORECASE)


def latest_sitemap_date(xml: str) -> date | None:
    """Newest ``<lastmod>`` date in a sitemap.

    Args:
        xml: Raw sitemap XML.

    Returns:
        The most recent date, or ``None`` when no entry parses
        (W3C datetime values are read by their date part).
    """
    dates: list[date] = []
    for raw in _LASTMOD.findall(xml):
        try:
            dates.append(date.fromisoformat(raw.strip()[:10]))
        except ValueError:
            continue
    return max(dates, default=None)


def latest_feed_date(xml: str) -> date | None:
    """Newest ``<pubDate>`` in an RSS feed (RFC 822 dates).

    Args:
        xml: Raw RSS XML.

    Returns:
        The most recent date, or ``None`` when no entry parses.
    """
    dates: list[date] = []
    for raw in _PUBDATE.findall(xml):
        try:
            dates.append(parsedate_to_datetime(raw.strip()).date())
        except (TypeError, ValueError):
            continue
    return max(dates, default=None)


def staleness(latest: date | None, today: date, max_age_days: int) -> str | None:
    """Judge whether the newest content is recent enough.

    Args:
        latest: Newest content date found on the live site.
        today: Reference date (injected for testability).
        max_age_days: Oldest acceptable age in days.

    Returns:
        A human-readable problem, or ``None`` when fresh.
    """
    if latest is None:
        return (
            "no dated entries in the sitemap or feed - "
            "freshness cannot be proven"
        )
    age = (today - latest).days
    if age > max_age_days:
        return (
            f"newest content is {age} days old (limit {max_age_days}) - "
            "the publishing rhythm has stalled"
        )
    return None
