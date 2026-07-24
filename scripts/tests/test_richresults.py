"""Unit tests for :mod:`seo_content_forge.richresults`."""

from __future__ import annotations

from seo_content_forge.richresults import check_page, extract_jsonld_blocks

_VALID_ARTICLE = """
<html><head>
<script type="application/ld+json">
{"@context": "https://schema.org", "@type": "BlogPosting",
 "headline": "T", "author": {"@type": "Person", "name": "J"},
 "datePublished": "2026-01-15", "image": ["https://example.com/i.png"],
 "dateModified": "2026-01-15", "description": "d",
 "publisher": {"@type": "Organization", "name": "E"}}
</script>
</head><body></body></html>
"""


def test_extracts_only_jsonld_scripts() -> None:
    html = (
        "<script>var x = 1;</script>"
        '<script type="application/ld+json">{"@type": "Thing"}</script>'
        '<script type="APPLICATION/LD+JSON">{"@type": "Other"}</script>'
    )
    blocks = extract_jsonld_blocks(html)
    assert len(blocks) == 2


def test_valid_page_reports_eligible_type() -> None:
    report = check_page(_VALID_ARTICLE)
    assert report.eligible_types == ["BlogPosting"]
    assert not report.has_blocking_errors


def test_graph_container_is_flattened() -> None:
    html = (
        '<script type="application/ld+json">'
        '{"@context": "https://schema.org", "@graph": ['
        '{"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem"}]},'
        '{"@type": "Organization", "name": "E", "url": "https://example.com"}'
        "]}</script>"
    )
    report = check_page(html)
    assert [result.node_type for result in report.results] == [
        "BreadcrumbList",
        "Organization",
    ]
    assert all(result.is_valid for result in report.results)


def test_invalid_json_is_a_parse_error() -> None:
    html = '<script type="application/ld+json">{not json}</script>'
    report = check_page(html)
    assert report.parse_errors
    assert report.has_blocking_errors


def test_page_without_jsonld_is_empty() -> None:
    report = check_page("<html><body><p>text</p></body></html>")
    assert not report.results
    assert not report.parse_errors
