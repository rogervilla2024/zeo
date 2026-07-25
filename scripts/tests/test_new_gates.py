"""Tests for heading, content-image, and broken-link gates."""

from __future__ import annotations

from pathlib import Path

from test_agent_ready import _GOOD_HTML, _by_id

from check_broken_links import scan
from seo_content_forge.agent_ready import analyze_html


def test_good_html_passes_new_checks() -> None:
    checks = analyze_html(_GOOD_HTML)
    assert _by_id(checks, "single-h1").passed
    assert _by_id(checks, "heading-hierarchy").passed


def test_two_h1_fail() -> None:
    html = _GOOD_HTML.replace("<h1>Heading</h1>", "<h1>A</h1><h1>B</h1>")
    assert not _by_id(analyze_html(html), "single-h1").passed


def test_skipped_heading_level_fails() -> None:
    html = _GOOD_HTML.replace("<h1>Heading</h1>", "<h1>A</h1><h4>Deep</h4>")
    assert not _by_id(analyze_html(html), "heading-hierarchy").passed


def test_long_text_without_images_fails() -> None:
    html = _GOOD_HTML.replace('<img src="a.png" alt="described image">', "")
    html = html.replace("word " * 200, "word " * 600)
    assert not _by_id(analyze_html(html), "content-images").passed


def test_broken_links_detected(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    (dist / "good").mkdir(parents=True)
    (dist / "good" / "index.html").write_text("<a href='/missing'>x</a>")
    (dist / "index.html").write_text("<a href='/good/'>ok</a>")
    broken = scan(dist)
    assert [href for _, href in broken] == ["/missing"]


def test_date_modified_needs_visible_time() -> None:
    schema = (
        '<script type="application/ld+json">'
        '{"dateModified": "2026-03-02T10:00:00Z"}</script>'
    )
    html = _GOOD_HTML.replace("</head>", schema + "</head>")
    assert not _by_id(analyze_html(html), "visible-updated-date").passed
    with_time = html.replace(
        "<h1>Heading</h1>",
        '<h1>Heading</h1><time datetime="2026-03-02">Updated</time>',
    )
    assert _by_id(analyze_html(with_time), "visible-updated-date").passed


def test_lazy_alt_text_fails() -> None:
    html = _GOOD_HTML.replace(
        '<img src="a.png" alt="described image">',
        '<img src="french-press.png" alt="french press"><img src="b.png" alt="image">',
    )
    assert not _by_id(analyze_html(html), "alt-quality").passed


def test_descriptive_alt_passes() -> None:
    assert _by_id(analyze_html(_GOOD_HTML), "alt-quality").passed
