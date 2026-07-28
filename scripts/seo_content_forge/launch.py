"""Launch-readiness checks for a site built from the golden template.

Bootstrapping leaves deliberate placeholders (config example values,
robots ``{{SITE_URL}}``, trust-page stubs) that must all be replaced
before the site goes live. Each item here is a one-time launch
blocker rather than a per-publish gate, which is why this runs from
the bootstrap-site checklist instead of seo_report's card.
"""

from __future__ import annotations

import re
from pathlib import Path

import orjson

# Values copied verbatim from site.config.example.json that must not
# survive into a real site's config.
_CONFIG_PLACEHOLDERS = ("example.com", "Example Site", "Jane Doe")
# Trust-page stubs mark unfilled spots as {{LIKE_THIS}}.
_PAGE_PLACEHOLDER = re.compile(r"\{\{[A-Z0-9_]+\}\}")


def _has_any(directory: Path, patterns: tuple[str, ...]) -> bool:
    return directory.is_dir() and any(
        next(directory.glob(pattern), None) for pattern in patterns
    )


def check_launch(root: Path) -> list[str]:
    """Find everything still blocking a site launch.

    Args:
        root: Site project root (the directory holding
            site.config.json, public/, and src/).

    Returns:
        Human-readable launch blockers; empty when the site is ready.
    """
    config_path = root / "site.config.json"
    if not config_path.is_file():
        return ["site.config.json missing - is this a site root?"]

    problems: list[str] = []
    raw = config_path.read_text(encoding="utf-8")
    for marker in _CONFIG_PLACEHOLDERS:
        if marker in raw:
            problems.append(
                f"site.config.json still contains the template value {marker!r}"
            )
    config = orjson.loads(raw)
    authors = config.get("authors") if isinstance(config, dict) else None
    if not authors:
        problems.append("no authors registered in site.config.json")

    public = root / "public"
    robots = public / "robots.txt"
    if not robots.is_file():
        problems.append("public/robots.txt missing")
    elif "{{SITE_URL}}" in robots.read_text(encoding="utf-8"):
        problems.append("public/robots.txt still contains {{SITE_URL}}")
    redirects = public / "_redirects"
    if redirects.is_file() and "{{DOMAIN}}" in redirects.read_text(
        encoding="utf-8"
    ):
        problems.append("public/_redirects still contains {{DOMAIN}}")
    # Dynamic endpoints (src/pages/*.js) satisfy the llms/sitemap
    # checks: they render into dist on every build, so they can never
    # go stale the way a hand-written public/ copy does.
    pages = root / "src" / "pages"
    if (
        not (public / "llms.txt").is_file()
        and not (pages / "llms.txt.js").is_file()
        and not (root / "dist" / "llms.txt").is_file()
    ):
        problems.append(
            "no llms.txt (src/pages/llms.txt.js endpoint or public/llms.txt)"
        )
    if (
        not _has_any(public, ("sitemap*.xml",))
        and not _has_any(root / "dist", ("sitemap*.xml",))
        and not (pages / "sitemap.xml.js").is_file()
    ):
        problems.append(
            "no sitemap (src/pages/sitemap.xml.js endpoint or a sitemap*.xml)"
        )
    if not _has_any(public, ("favicon.ico", "favicon.svg")):
        problems.append("no favicon in public/ (generate_favicons.py)")
    for asset in ("logo.png", "og-image.png"):
        if not (public / asset).is_file():
            problems.append(f"public/{asset} missing")

    if pages.is_dir():
        for page in sorted(pages.glob("*.astro")):
            if _PAGE_PLACEHOLDER.search(page.read_text(encoding="utf-8")):
                problems.append(
                    f"src/pages/{page.name}: unfilled placeholder "
                    "(generate-trust-pages skill)"
                )

    content = root / "src" / "content" / "blog"
    count = len(list(content.rglob("*.md"))) if content.is_dir() else 0
    target = 0
    if isinstance(config, dict):
        section = config.get("content")
        if isinstance(section, dict):
            value = section.get("launch_articles")
            if isinstance(value, int) and value > 0:
                target = value
    if count < target:
        problems.append(
            f"{count} article(s) in src/content/blog, "
            f"launch pack is {target} (content.launch_articles)"
        )
    return problems
