"""Tests for stale-article detection and the refresh queue CLI."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from queue_refresh_candidates import main, merge_into_queue
from seo_content_forge.planner import QueueItem
from seo_content_forge.stale import article_freshness, find_stale, months_ago


def _article_html(url: str, modified: str, node_type: str = "BlogPosting") -> str:
    node = {
        "@context": "https://schema.org",
        "@type": node_type,
        "headline": "T",
        "url": url,
        "dateModified": modified,
    }
    return f'<script type="application/ld+json">{json.dumps(node)}</script>'


def test_months_ago_clamps_short_months() -> None:
    assert months_ago(date(2026, 7, 26), 6) == date(2026, 1, 26)
    assert months_ago(date(2026, 3, 31), 1) == date(2026, 2, 28)
    assert months_ago(date(2026, 1, 15), 13) == date(2024, 12, 15)


def test_article_freshness_reads_url_and_date() -> None:
    html = _article_html("https://e.com/a/", "2026-01-01T09:00:00Z")
    assert article_freshness(html) == ("https://e.com/a/", "2026-01-01T09:00:00Z")
    assert article_freshness("<p>no schema</p>") is None
    graph = (
        '<script type="application/ld+json">'
        '{"@context":"https://schema.org","@graph":[{"@type":"Article",'
        '"mainEntityOfPage":{"@id":"https://e.com/g/"},'
        '"datePublished":"2025-05-01"}]}</script>'
    )
    assert article_freshness(graph) == ("https://e.com/g/", "2025-05-01")


def test_find_stale_sorts_oldest_first_and_warns(tmp_path: Path) -> None:
    (tmp_path / "old").mkdir()
    (tmp_path / "old" / "index.html").write_text(
        _article_html("https://e.com/old/", "2025-06-01")
    )
    (tmp_path / "older.html").write_text(
        _article_html("https://e.com/older/", "2024-12-31")
    )
    (tmp_path / "fresh.html").write_text(
        _article_html("https://e.com/fresh/", "2026-07-01")
    )
    (tmp_path / "bad.html").write_text(_article_html("https://e.com/bad/", "soon"))
    (tmp_path / "page.html").write_text("<h1>no article schema</h1>")

    stale, warnings = find_stale(tmp_path, date(2026, 7, 26), months=6)
    assert [article.url for article in stale] == [
        "https://e.com/older/",
        "https://e.com/old/",
    ]
    assert stale[0].days_old == (date(2026, 7, 26) - date(2024, 12, 31)).days
    assert warnings == ["bad.html: unparseable date 'soon'"]


def test_article_freshness_accepts_list_valued_type() -> None:
    node = {
        "@context": "https://schema.org",
        "@type": ["BlogPosting", "Article"],
        "url": "https://e.com/multi/",
        "dateModified": "2025-01-01",
    }
    html = f'<script type="application/ld+json">{json.dumps(node)}</script>'
    assert article_freshness(html) == ("https://e.com/multi/", "2025-01-01")


def test_find_stale_boundary_is_inclusive(tmp_path: Path) -> None:
    (tmp_path / "edge.html").write_text(
        _article_html("https://e.com/edge/", "2026-01-26")
    )
    stale, _ = find_stale(tmp_path, date(2026, 7, 26), months=6)
    assert [article.url for article in stale] == ["https://e.com/edge/"]


def test_merge_into_queue_skips_pending_duplicates() -> None:
    existing = [
        QueueItem(topic="Refresh: /a", item_type="refresh", url="/a"),
        QueueItem(
            topic="Refresh: /b", item_type="refresh", url="/b", status="done"
        ),
        QueueItem(topic="new article about /c", item_type="new", url=""),
    ]
    candidates = [
        QueueItem(topic="Refresh: /a", item_type="refresh", url="/a"),
        QueueItem(topic="Refresh: /b", item_type="refresh", url="/b"),
    ]
    merged, added = merge_into_queue(existing, candidates)
    assert added == 1
    assert [item.url for item in merged if item.item_type == "refresh"] == [
        "/a",
        "/b",
        "/b",
    ]


def test_main_dry_run_then_apply(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "old.html").write_text(_article_html("https://e.com/old/", "2025-01-01"))
    queue = tmp_path / "content-queue.json"

    assert (
        main(["--dist", str(dist), "--now", "2026-07-26", "--queue", str(queue)]) == 0
    )
    assert not queue.exists()

    code = main(
        [
            "--dist",
            str(dist),
            "--now",
            "2026-07-26",
            "--queue",
            str(queue),
            "--apply",
        ]
    )
    assert code == 0
    saved = json.loads(queue.read_text())
    assert saved["queue"][0]["type"] == "refresh"
    assert saved["queue"][0]["url"] == "https://e.com/old/"
    assert saved["queue"][0]["source"] == "refresh-queue"
    assert saved["queue"][0]["priority"] == 50

    # Re-applying does not duplicate the pending item.
    assert (
        main(
            [
                "--dist",
                str(dist),
                "--now",
                "2026-07-26",
                "--queue",
                str(queue),
                "--apply",
            ]
        )
        == 0
    )
    saved = json.loads(queue.read_text())
    assert len(saved["queue"]) == 1


def test_main_malformed_queue_exits_2(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "old.html").write_text(_article_html("https://e.com/old/", "2025-01-01"))
    queue = tmp_path / "content-queue.json"
    queue.write_text("not json")
    code = main(
        [
            "--dist",
            str(dist),
            "--now",
            "2026-07-26",
            "--queue",
            str(queue),
            "--apply",
        ]
    )
    assert code == 2
    assert queue.read_text() == "not json"


def test_main_nothing_stale(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "fresh.html").write_text(
        _article_html("https://e.com/fresh/", "2026-07-01")
    )
    assert main(["--dist", str(dist), "--now", "2026-07-26"]) == 0
    assert main(["--dist", str(tmp_path / "missing")]) == 2
