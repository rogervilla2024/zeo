"""Unit tests for :mod:`seo_content_forge.theme_search`."""

from __future__ import annotations

from datetime import UTC, datetime

from seo_content_forge.theme_search import (
    filter_candidates,
    parse_search_items,
    rank,
)

_NOW = datetime(2026, 7, 24, tzinfo=UTC)


def _item(
    name: str,
    stars: int,
    license_id: str | None = "MIT",
    pushed: str = "2026-06-01T00:00:00Z",
    description: str = "",
) -> dict[str, object]:
    return {
        "full_name": name,
        "description": description,
        "stargazers_count": stars,
        "license": {"spdx_id": license_id} if license_id else None,
        "pushed_at": pushed,
        "html_url": f"https://github.com/{name}",
        "homepage": "",
    }


def test_parse_handles_missing_fields() -> None:
    candidates = parse_search_items([_item("a/b", 100, license_id=None)])
    assert candidates[0].license_id == ""
    assert candidates[0].stars == 100


def test_filters_license_stars_and_age() -> None:
    candidates = parse_search_items(
        [
            _item("ok/theme", 200),
            _item("gpl/theme", 500, license_id="GPL-3.0"),
            _item("tiny/theme", 5),
            _item("dead/theme", 900, pushed="2023-01-01T00:00:00Z"),
        ]
    )
    kept = filter_candidates(candidates, _NOW)
    assert [candidate.full_name for candidate in kept] == ["ok/theme"]


def test_niche_match_beats_raw_stars() -> None:
    candidates = parse_search_items(
        [
            _item("big/generic", 5000, description="A portfolio starter"),
            _item(
                "small/blog",
                200,
                description="Minimal blog and magazine theme for content sites",
            ),
        ]
    )
    ranked = rank(candidates, ["blog", "magazine", "content"], now=_NOW)
    assert ranked[0][0].full_name == "small/blog"


def test_rank_respects_top_limit() -> None:
    candidates = parse_search_items(
        [_item(f"owner/theme{i}", 100 + i) for i in range(10)]
    )
    assert len(rank(candidates, [], now=_NOW, top=3)) == 3
