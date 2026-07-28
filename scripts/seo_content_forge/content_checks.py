"""Source-level content gates: in-body internal links and categories.

Like the article-images gate, these read the content collection
SOURCE, because the built HTML cannot distinguish a deliberate
editorial choice from a forgotten pipeline step. Internal links and a
category assignment are both mandated by the writing pipeline; a
deterministic check is what keeps them from silently disappearing.
"""

from __future__ import annotations

import re
from datetime import date, timedelta
from pathlib import Path

from seo_content_forge.article_images import parse_frontmatter

_MD_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
# Root-relative markdown links plus root-relative HTML anchors; both
# forms appear in pipeline output. Images are stripped first so a
# hero reference never counts as a link.
_INTERNAL_LINK = re.compile(r"\]\(/|<a\s[^>]*href=\"/", re.IGNORECASE)


def _body(text: str) -> str:
    """Return the markdown body with the frontmatter block removed."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4 :]
    return text


def internal_link_count(text: str) -> int:
    """Count in-body internal (root-relative) links in an article.

    Args:
        text: Full markdown file content.

    Returns:
        Number of internal link occurrences in the body, images
        excluded.
    """
    return len(_INTERNAL_LINK.findall(_MD_IMAGE.sub("", _body(text))))


def check_internal_links(content_dir: Path, min_links: int) -> list[str]:
    """Find articles below the internal-link minimum.

    The requirement scales down on young sites - an article can only
    link to pages that exist - so the effective minimum is
    ``min(min_links, article_count - 1)``: a launch site with two
    articles needs one link each, a single-article site none.

    Args:
        content_dir: Directory of article markdown files.
        min_links: Configured in-body internal link minimum
            (``content.min_internal_links``; 0 disables the gate).

    Returns:
        Human-readable problems sorted by file; empty when clean.
    """
    paths = sorted(content_dir.rglob("*.md"))
    effective = min(min_links, max(len(paths) - 1, 0))
    problems: list[str] = []
    for path in paths:
        count = internal_link_count(path.read_text(encoding="utf-8"))
        if count < effective:
            problems.append(
                f"{path.name}: {count} in-body internal link(s), "
                f"needs at least {effective}"
            )
    return problems


def check_dates(content_dir: Path, today: date) -> list[str]:
    """Find articles whose dates cannot be true.

    Two rules: ``updatedDate`` must not precede ``pubDate`` (a
    refresh that "updated" an article into the past lies to the
    freshness signals), and neither date may sit in the future
    beyond one day of timezone slack (a future-dated article
    corrupts the sitemap's lastmod).

    Args:
        content_dir: Directory of article markdown files.
        today: Reference date (injected for testability).

    Returns:
        Human-readable problems sorted by file; empty when clean.
    """
    limit = today + timedelta(days=1)
    problems: list[str] = []
    for path in sorted(content_dir.rglob("*.md")):
        fields = parse_frontmatter(path.read_text(encoding="utf-8"))
        published = _parse_date(fields.get("pubDate", ""))
        updated = _parse_date(fields.get("updatedDate", ""))
        if published is None:
            problems.append(f"{path.name}: pubDate missing or unparseable")
            continue
        if published > limit:
            problems.append(f"{path.name}: pubDate {published} is in the future")
        if updated is not None:
            if updated < published:
                problems.append(
                    f"{path.name}: updatedDate {updated} precedes "
                    f"pubDate {published}"
                )
            if updated > limit:
                problems.append(
                    f"{path.name}: updatedDate {updated} is in the future"
                )
    return problems


def _parse_date(value: str) -> date | None:
    """Parse the date part of a frontmatter date value, if any."""
    try:
        return date.fromisoformat(value.strip()[:10])
    except ValueError:
        return None


def check_categories(content_dir: Path) -> list[str]:
    """Find articles without a ``category`` frontmatter value.

    Every article should belong to a pillar from the topic map - the
    homepage strips and the category archives only work when the
    field is filled.

    Args:
        content_dir: Directory of article markdown files.

    Returns:
        Human-readable problems sorted by file; empty when clean.
    """
    problems: list[str] = []
    for path in sorted(content_dir.rglob("*.md")):
        fields = parse_frontmatter(path.read_text(encoding="utf-8"))
        if not fields.get("category"):
            problems.append(f"{path.name}: missing category frontmatter")
    return problems
