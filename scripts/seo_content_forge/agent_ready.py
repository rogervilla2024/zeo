"""Agent-readiness analysis, in the spirit of isitagentready.com.

AI agents and answer engines consume sites differently from browsers:
they read ``robots.txt`` for bot rules, ``llms.txt`` for orientation,
structured data for facts, and raw HTML (often without executing
JavaScript) for content. This module scores a site against those
expectations across four categories:

- discoverability: robots.txt, sitemap, llms.txt
- bot access: explicit rules for the major AI crawlers
- content accessibility: server-rendered text, semantic HTML, markdown
  content negotiation
- machine readability: structured data, canonical, core meta tags

Every function is pure - callers (see ``check_agent_ready.py``) fetch the
inputs and pass them in - so the analysis is unit-testable offline.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

AI_BOTS: tuple[str, ...] = (
    "GPTBot",
    "OAI-SearchBot",
    "ClaudeBot",
    "Claude-SearchBot",
    "anthropic-ai",
    "PerplexityBot",
    "Google-Extended",
    "CCBot",
    "Bytespider",
    "meta-externalagent",
    "Applebot-Extended",
)


@dataclass(slots=True)
class Check:
    """One agent-readiness check outcome.

    Args:
        check_id: Stable identifier, e.g. ``robots-txt``.
        category: One of ``discoverability``, ``bot-access``,
            ``content-accessibility``, ``machine-readability``.
        passed: Whether the site meets this expectation.
        detail: What was observed.
        fix: Concrete remediation when ``passed`` is ``False``.
    """

    check_id: str
    category: str
    passed: bool
    detail: str
    fix: str


def _check(check_id: str, category: str, passed: bool, detail: str, fix: str) -> Check:
    return Check(check_id, category, passed, detail, "" if passed else fix)


def analyze_robots(robots_txt: str | None) -> list[Check]:
    """Analyze ``robots.txt`` for presence, sitemap, and AI-bot rules.

    Args:
        robots_txt: File content, or ``None`` when the file is missing
            (non-200 response).

    Returns:
        Discoverability and bot-access checks.
    """
    checks = [
        _check(
            "robots-txt",
            "discoverability",
            robots_txt is not None,
            "robots.txt found" if robots_txt is not None else "robots.txt missing",
            "Publish a robots.txt at the site root.",
        )
    ]
    text = robots_txt or ""
    has_sitemap = bool(re.search(r"(?im)^\s*sitemap\s*:", text))
    checks.append(
        _check(
            "robots-sitemap-directive",
            "discoverability",
            has_sitemap,
            "Sitemap: directive present" if has_sitemap else "no Sitemap: directive",
            "Add 'Sitemap: <absolute sitemap URL>' to robots.txt.",
        )
    )
    named = [bot for bot in AI_BOTS if re.search(rf"(?i)\b{re.escape(bot)}\b", text)]
    checks.append(
        _check(
            "robots-ai-bot-rules",
            "bot-access",
            bool(named),
            (
                f"explicit rules for: {', '.join(named)}"
                if named
                else "no AI crawler is named; access is implicit"
            ),
            "Add explicit User-agent rules for the major AI crawlers "
            f"({', '.join(AI_BOTS[:4])}, ...) so access is a decision, "
            "not an accident.",
        )
    )
    return checks


def analyze_html(html: str) -> list[Check]:
    """Analyze a page's raw HTML as a non-JS agent would receive it.

    Args:
        html: Raw HTML source (before any JavaScript execution).

    Returns:
        Content-accessibility and machine-readability checks.
    """

    def present(pattern: str) -> bool:
        return re.search(pattern, html, re.IGNORECASE | re.DOTALL) is not None

    visible = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>|<[^>]+>", " ", html)
    text_length = len(" ".join(visible.split()))

    img_tags = re.findall(r"(?is)<img\b[^>]*>", html)
    imgs_with_alt = [tag for tag in img_tags if re.search(r"(?i)\balt\s*=", tag)]
    alt_ok = len(imgs_with_alt) == len(img_tags)

    checks = [
        _check(
            "server-rendered-content",
            "content-accessibility",
            text_length >= 500,
            f"{text_length} characters of text without JavaScript",
            "Server-render or statically generate the main content; "
            "agents and most crawlers do not execute JavaScript.",
        ),
        _check(
            "semantic-structure",
            "content-accessibility",
            present(r"<h1[\s>]") and present(r"<(main|article)[\s>]"),
            "h1 plus main/article landmarks"
            if present(r"<h1[\s>]") and present(r"<(main|article)[\s>]")
            else "missing h1 or main/article landmarks",
            "Use one h1 and wrap primary content in <main> or <article>.",
        ),
        _check(
            "structured-data",
            "machine-readability",
            present(r'type\s*=\s*["\']application/ld\+json["\']'),
            "JSON-LD present"
            if present(r'type\s*=\s*["\']application/ld\+json["\']')
            else "no JSON-LD found",
            "Embed schema.org JSON-LD (see the generate-schema skill).",
        ),
        _check(
            "title-and-description",
            "machine-readability",
            present(r"<title[\s>]") and present(r'name\s*=\s*["\']description["\']'),
            "title and meta description present"
            if present(r"<title[\s>]") and present(r'name\s*=\s*["\']description["\']')
            else "missing title or meta description",
            "Add a unique <title> and meta description to every page.",
        ),
        _check(
            "canonical",
            "machine-readability",
            present(r'rel\s*=\s*["\']canonical["\']'),
            "canonical link present"
            if present(r'rel\s*=\s*["\']canonical["\']')
            else "no canonical link",
            'Add <link rel="canonical"> so agents cite one URL.',
        ),
        _check(
            "html-lang",
            "machine-readability",
            present(r"<html[^>]*\slang\s*="),
            "html lang attribute present"
            if present(r"<html[^>]*\slang\s*=")
            else "html tag has no lang attribute",
            'Set <html lang="..."> so engines and agents know the language.',
        ),
        _check(
            "viewport",
            "content-accessibility",
            present(r'name\s*=\s*["\']viewport["\']'),
            "viewport meta present"
            if present(r'name\s*=\s*["\']viewport["\']')
            else "no viewport meta",
            "Add the responsive viewport meta tag; Google indexes mobile-first.",
        ),
        _check(
            "og-image",
            "machine-readability",
            present(r'property\s*=\s*["\']og:image["\']'),
            "og:image present"
            if present(r'property\s*=\s*["\']og:image["\']')
            else "no og:image",
            "Add an og:image (1200x630) so shares and previews render "
            "a card; see generate_og_image.py.",
        ),
        _check(
            "image-alt",
            "content-accessibility",
            alt_ok,
            (
                "no images on page"
                if not img_tags
                else f"{len(imgs_with_alt)}/{len(img_tags)} images have alt text"
            ),
            "Add descriptive alt text to every content image; agents and "
            "image search read alt, not pixels.",
        ),
    ]
    return checks


def presence_checks(
    llms_txt_found: bool,
    sitemap_found: bool,
    markdown_negotiation: bool,
) -> list[Check]:
    """Build checks for resources probed by the caller.

    Args:
        llms_txt_found: ``/llms.txt`` returned 200.
        sitemap_found: The sitemap URL (from robots.txt or
            ``/sitemap.xml``) returned 200.
        markdown_negotiation: Requesting the homepage with
            ``Accept: text/markdown`` returned a markdown content type.

    Returns:
        Discoverability and content-accessibility checks.
    """
    return [
        _check(
            "llms-txt",
            "discoverability",
            llms_txt_found,
            "llms.txt found" if llms_txt_found else "llms.txt missing",
            "Publish /llms.txt (see the generate-llms-txt skill).",
        ),
        _check(
            "sitemap",
            "discoverability",
            sitemap_found,
            "sitemap reachable" if sitemap_found else "sitemap not reachable",
            "Publish an XML sitemap (see the generate-sitemap skill).",
        ),
        _check(
            "markdown-negotiation",
            "content-accessibility",
            markdown_negotiation,
            "serves markdown on Accept: text/markdown"
            if markdown_negotiation
            else "no markdown content negotiation",
            "Optionally serve text/markdown variants; agents prefer "
            "markdown over rendered HTML. This is an emerging standard, "
            "not a blocker.",
        ),
    ]


def summarize(checks: list[Check]) -> tuple[int, int, int]:
    """Summarize check outcomes.

    Args:
        checks: All collected checks.

    Returns:
        Tuple of (passed count, total count, score as 0-100 int).
    """
    passed = sum(1 for check in checks if check.passed)
    total = len(checks)
    return passed, total, round(100 * passed / total) if total else 0
