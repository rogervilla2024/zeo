"""Tests for the affiliate table, rel policy scan, and checker CLI."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import check_affiliate_links
from check_affiliate_links import main
from seo_content_forge.affiliates import (
    is_affiliate,
    page_anchors,
    parse_table,
    scan_dist,
)

ROOT = Path(__file__).resolve().parents[2]

TABLE = {
    "links": [
        {
            "id": "acme",
            "url": "https://merchant.example/acme?tag=site-20",
            "merchant": "Acme",
        }
    ],
    "domains": ["amzn.to"],
}


def test_parse_table_valid_and_invalid() -> None:
    table = parse_table(TABLE)
    assert table.links[0].link_id == "acme"
    assert table.domains == ["amzn.to"]
    with pytest.raises(ValueError, match="JSON object"):
        parse_table([])
    with pytest.raises(ValueError, match="id and url"):
        parse_table({"links": [{"id": "x"}]})
    with pytest.raises(ValueError, match="duplicate"):
        parse_table({"links": [{"id": "a", "url": "u"}, {"id": "a", "url": "v"}]})


def test_is_affiliate_by_url_prefix_and_domain() -> None:
    table = parse_table(TABLE)
    assert is_affiliate("https://merchant.example/acme?tag=site-20&x=1", table)
    assert is_affiliate("https://amzn.to/3xYz", table)
    assert is_affiliate("https://www.amzn.to/3xYz", table)
    assert is_affiliate("https://sub.amzn.to/3xYz", table)
    assert not is_affiliate("https://merchant.example/other", table)
    assert not is_affiliate("/blog/post/", table)


def test_page_anchors_reads_href_and_rel() -> None:
    html = '<a href="/x">i</a><a rel="sponsored nofollow" href="https://a.b/">e</a>'
    assert page_anchors(html) == [
        ("/x", ""),
        ("https://a.b/", "sponsored nofollow"),
    ]


def _write_page(dist: Path, name: str, body: str) -> None:
    dist.mkdir(parents=True, exist_ok=True)
    (dist / name).write_text(f"<html><body>{body}</body></html>")


def test_scan_dist_flags_missing_rel_and_unregistered(tmp_path: Path) -> None:
    table = parse_table(TABLE)
    _write_page(
        tmp_path,
        "good.html",
        '<a href="https://merchant.example/acme?tag=site-20" '
        'rel="sponsored nofollow">ok</a>'
        '<a href="/internal">internal</a>'
        '<a href="https://other.example/">plain external</a>',
    )
    _write_page(
        tmp_path,
        "bad.html",
        '<a href="https://merchant.example/acme?tag=site-20">no rel</a>'
        '<a href="https://amzn.to/3xYz" rel="sponsored">unregistered</a>',
    )
    violations = scan_dist(tmp_path, table)
    problems = {(v.page, v.problem) for v in violations}
    assert problems == {("bad.html", "missing-rel"), ("bad.html", "unregistered")}


def test_main_missing_table_passes(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    assert main(["--dist", str(dist), "--table", str(tmp_path / "none.json")]) == 0
    assert main(["--dist", str(tmp_path / "missing")]) == 2


def test_main_offline_violations_fail(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    _write_page(
        dist, "a.html", '<a href="https://merchant.example/acme?tag=site-20">x</a>'
    )
    table_path = tmp_path / "affiliates.json"
    table_path.write_text(json.dumps(TABLE))
    assert main(["--dist", str(dist), "--table", str(table_path)]) == 1


def test_main_live_probe(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    dist = tmp_path / "dist"
    _write_page(
        dist,
        "a.html",
        '<a href="https://merchant.example/acme?tag=site-20" '
        'rel="sponsored">x</a>',
    )
    table_path = tmp_path / "affiliates.json"
    table_path.write_text(json.dumps(TABLE))

    monkeypatch.setattr(check_affiliate_links, "probe", lambda url: 404)
    assert main(["--dist", str(dist), "--table", str(table_path), "--live"]) == 1
    monkeypatch.setattr(check_affiliate_links, "probe", lambda url: 200)
    assert main(["--dist", str(dist), "--table", str(table_path), "--live"]) == 0


def test_example_table_and_component_contract() -> None:
    example = json.loads((ROOT / "templates" / "affiliates.example.json").read_text())
    table = parse_table(example)
    assert table.links and table.domains
    component = (ROOT / "templates" / "theme" / "AffiliateLink.astro").read_text()
    assert 'rel="sponsored nofollow"' in component
    assert "affiliates.json" in component
    assert "<script" not in component
