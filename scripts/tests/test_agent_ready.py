"""Unit tests for :mod:`seo_content_forge.agent_ready`."""

from __future__ import annotations

from seo_content_forge.agent_ready import (
    analyze_html,
    analyze_robots,
    presence_checks,
    summarize,
)

_GOOD_ROBOTS = """
User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

Sitemap: https://example.com/sitemap.xml
"""

_GOOD_HTML = (
    '<html lang="en"><head><title>T</title>'
    '<meta name="viewport" content="width=device-width, initial-scale=1">'
    '<meta name="description" content="d">'
    '<meta property="og:image" content="https://example.com/og.png">'
    '<link rel="canonical" href="https://example.com/">'
    '<script type="application/ld+json">{}</script>'
    "</head><body><main><h1>Heading</h1>"
    '<img src="a.png" alt="described image"><p>'
    + ("word " * 200)
    + "</p></main></body></html>"
)


def _by_id(checks: list[object], check_id: str) -> object:
    return next(check for check in checks if check.check_id == check_id)


def test_good_robots_passes_all() -> None:
    checks = analyze_robots(_GOOD_ROBOTS)
    assert all(check.passed for check in checks)
    ai_check = _by_id(checks, "robots-ai-bot-rules")
    assert "GPTBot" in ai_check.detail and "ClaudeBot" in ai_check.detail


def test_missing_robots_fails_with_fixes() -> None:
    checks = analyze_robots(None)
    assert not any(check.passed for check in checks)
    assert all(check.fix for check in checks)


def test_good_html_passes_all() -> None:
    checks = analyze_html(_GOOD_HTML)
    assert all(check.passed for check in checks)


def test_js_only_page_fails_content_check() -> None:
    html = '<html><body><div id="root"></div><script>app()</script></body></html>'
    checks = analyze_html(html)
    content = _by_id(checks, "server-rendered-content")
    assert not content.passed


def test_image_without_alt_fails_alt_check() -> None:
    html = _GOOD_HTML.replace(
        '<img src="a.png" alt="described image">',
        '<img src="a.png" alt="described image"><img src="b.png">',
    )
    checks = analyze_html(html)
    alt_check = _by_id(checks, "image-alt")
    assert not alt_check.passed
    assert "1/2" in alt_check.detail


def test_page_without_images_passes_alt_check() -> None:
    checks = analyze_html("<html><body><main><h1>H</h1></main></body></html>")
    assert _by_id(checks, "image-alt").passed


def test_presence_checks_map_inputs() -> None:
    checks = presence_checks(
        llms_txt_found=True, sitemap_found=False, markdown_negotiation=False
    )
    assert _by_id(checks, "llms-txt").passed
    assert not _by_id(checks, "sitemap").passed


def test_summarize_scores() -> None:
    checks = analyze_robots(_GOOD_ROBOTS) + analyze_html(_GOOD_HTML)
    passed, total, score = summarize(checks)
    assert passed == total
    assert score == 100
    assert summarize([]) == (0, 0, 0)
