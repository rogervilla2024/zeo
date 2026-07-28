"""Tests for the live freshness gate."""

from __future__ import annotations

from datetime import date

import check_freshness_live
from check_freshness_live import main
from seo_content_forge.freshness import (
    latest_feed_date,
    latest_sitemap_date,
    staleness,
)

SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>https://e.com/</loc></url>
<url><loc>https://e.com/a/</loc><lastmod>2026-07-01</lastmod></url>
<url><loc>https://e.com/b/</loc><lastmod>2026-07-20T10:00:00Z</lastmod></url>
<url><loc>https://e.com/c/</loc><lastmod>not-a-date</lastmod></url>
</urlset>
"""

RSS = """<rss><channel>
<item><pubDate>Mon, 06 Jul 2026 00:00:00 GMT</pubDate></item>
<item><pubDate>Tue, 21 Jul 2026 00:00:00 GMT</pubDate></item>
<item><pubDate>garbage</pubDate></item>
</channel></rss>
"""


def test_latest_dates_parse_and_ignore_garbage() -> None:
    assert latest_sitemap_date(SITEMAP) == date(2026, 7, 20)
    assert latest_feed_date(RSS) == date(2026, 7, 21)
    assert latest_sitemap_date("<urlset/>") is None
    assert latest_feed_date("<rss/>") is None


def test_staleness_rules() -> None:
    today = date(2026, 7, 28)
    assert staleness(date(2026, 7, 20), today, 45) is None
    problem = staleness(date(2026, 5, 1), today, 45)
    assert problem is not None and "88 days old" in problem
    assert staleness(None, today, 45) is not None
    # Exactly at the limit still passes; one past fails.
    assert staleness(date(2026, 6, 13), today, 45) is None
    assert staleness(date(2026, 6, 12), today, 46) is None


def test_cli_uses_sitemap_then_feed(monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    fresh_day = date.today().isoformat()
    fresh_sitemap = (
        f"<urlset><url><lastmod>{fresh_day}</lastmod></url></urlset>"
    )
    responses = {"https://e.com/sitemap.xml": fresh_sitemap}
    monkeypatch.setattr(
        check_freshness_live, "fetch_text", lambda url: responses.get(url)
    )
    assert main(["--url", "https://e.com"]) == 0
    assert "OK: newest content is 0 day(s) old" in capsys.readouterr().out

    # Sitemap without dates falls back to the feed.
    old_feed = (
        "<rss><item><pubDate>Mon, 01 Jan 2001 00:00:00 GMT"
        "</pubDate></item></rss>"
    )
    responses = {
        "https://e.com/sitemap.xml": "<urlset/>",
        "https://e.com/rss.xml": old_feed,
    }
    monkeypatch.setattr(
        check_freshness_live, "fetch_text", lambda url: responses.get(url)
    )
    assert main(["--url", "https://e.com"]) == 1
    assert "publishing rhythm has stalled" in capsys.readouterr().out

    # Nothing fetchable is a hard error, not a pass.
    monkeypatch.setattr(check_freshness_live, "fetch_text", lambda url: None)
    assert main(["--url", "https://e.com"]) == 2
