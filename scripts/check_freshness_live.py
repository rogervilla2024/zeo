"""CLI live gate: the deployed site published something recently.

Usage:
    python check_freshness_live.py --url https://example.com
    python check_freshness_live.py --url https://example.com --max-age-days 30

Reads the newest content date from the live sitemap's ``lastmod``
entries (falling back to the RSS feed's ``pubDate``) and fails when
it is older than the limit. A site that quietly stops publishing
stops ranking; this makes the stall a red gate instead of a slow
discovery. The default limit (45 days) is deliberately generous
against the PLAYBOOK's weekly cadence - tighten with --max-age-days.
Exits 1 when stale, 2 when neither sitemap nor feed can be fetched.
"""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request
from datetime import date

from seo_content_forge.fetch import decode_body
from seo_content_forge.freshness import (
    latest_feed_date,
    latest_sitemap_date,
    staleness,
)

DEFAULT_MAX_AGE_DAYS = 45


def fetch_text(url: str) -> str | None:
    """Fetch a URL as text; None when it cannot be retrieved."""
    request = urllib.request.Request(
        url, headers={"User-Agent": "zeo-freshness-check/1.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            content_type = response.headers.get("Content-Type", "")
            return decode_body(response.read(), content_type)
    except (urllib.error.URLError, OSError, ValueError):
        return None


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when the live site is fresh."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="Deployed site URL.")
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=DEFAULT_MAX_AGE_DAYS,
        help="Oldest acceptable newest-content age.",
    )
    args = parser.parse_args(argv)

    base = args.url.rstrip("/")
    latest = None
    fetched_any = False
    sitemap = fetch_text(f"{base}/sitemap.xml")
    if sitemap is not None:
        fetched_any = True
        latest = latest_sitemap_date(sitemap)
    if latest is None:
        feed = fetch_text(f"{base}/rss.xml")
        if feed is not None:
            fetched_any = True
            latest = latest_feed_date(feed)
    if not fetched_any:
        print(
            f"could not fetch sitemap.xml or rss.xml from {args.url}",
            file=sys.stderr,
        )
        return 2

    problem = staleness(latest, date.today(), args.max_age_days)
    if problem:
        print(f"FRESHNESS {problem}")
        return 1
    age = (date.today() - latest).days if latest else 0
    print(f"OK: newest content is {age} day(s) old (limit {args.max_age_days}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
