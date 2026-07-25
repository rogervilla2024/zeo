"""Tests for question mining, consistency, media budget, host variants."""

from __future__ import annotations

from pathlib import Path

import orjson

from check_canonical_host import host_variants
from check_media_budget import image_sizes, unsafe_svgs
from seo_content_forge.questions import (
    dedupe_questions,
    expand_queries,
    parse_suggestions,
)
from seo_content_forge.richresults import check_page


def test_expand_and_parse_and_dedupe() -> None:
    queries = expand_queries("french press", "en")
    assert "how french press" in queries
    payload = orjson.dumps(
        ["q", ["how to use french press", "french press vs aeropress"]]
    )
    suggestions = parse_suggestions(payload)
    merged = dedupe_questions([suggestions, suggestions], "french press")
    assert merged == ["how to use french press", "french press vs aeropress"]


def test_dedupe_drops_offtopic() -> None:
    merged = dedupe_questions([["weather in london today"]], "french press")
    assert merged == []


def test_faq_consistency_error() -> None:
    html = (
        '<script type="application/ld+json">{"@context":"https://schema.org",'
        '"@type":"FAQPage","mainEntity":[{"@type":"Question","name":"Hidden '
        'question?","acceptedAnswer":{"@type":"Answer","text":"a"}}]}</script>'
        "<body><p>Body without the question.</p></body>"
    )
    report = check_page(html)
    assert report.has_blocking_errors
    assert any("Hidden question" in error for error in report.consistency_errors)


def test_faq_visible_passes() -> None:
    html = (
        '<script type="application/ld+json">{"@context":"https://schema.org",'
        '"@type":"FAQPage","mainEntity":[{"@type":"Question","name":"Seen?",'
        '"acceptedAnswer":{"@type":"Answer","text":"a"}}]}</script>'
        "<body><h3>Seen?</h3></body>"
    )
    assert check_page(html).consistency_errors == []


def test_media_budget_and_svg_lint(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "big.webp").write_bytes(b"x" * 2048)
    (dist / "bad.svg").write_text("<svg><script>evil()</script></svg>")
    (dist / "good.svg").write_text("<svg><rect/></svg>")
    assert image_sizes(dist)[0][1] == 2048
    assert [path.name for path in unsafe_svgs(dist)] == ["bad.svg"]


def test_host_variants() -> None:
    variants = host_variants("https://www.example.com")
    assert "https://example.com/" in variants
    assert "http://www.example.com/" in variants
    assert len(variants) == 4
