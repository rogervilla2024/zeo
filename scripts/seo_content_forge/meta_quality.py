"""Title and meta-description quality checks over built HTML.

SERP snippets are decided by the title tag and meta description;
truncated, missing, or duplicated values quietly waste every ranking
the content earns. This scans each indexable page in the build output
for presence, length bounds, and cross-page title duplicates.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_TITLE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_META_DESCRIPTION_TAG = re.compile(
    r"<meta\b[^>]*name=\"description\"[^>]*>", re.IGNORECASE
)
_CONTENT_ATTR = re.compile(r"content=\"([^\"]*)\"", re.IGNORECASE)
_NOINDEX = re.compile(
    r"<meta\b[^>]*name=\"robots\"[^>]*content=\"[^\"]*noindex", re.IGNORECASE
)


@dataclass(slots=True)
class Bounds:
    """Length limits for the two snippet fields (character counts)."""

    title_min: int = 10
    title_max: int = 60
    description_min: int = 40
    description_max: int = 160


def _skip(rel: str) -> bool:
    """Pages that are never snippet candidates."""
    return rel == "404.html" or rel.startswith("pagefind/")


def check_meta(dist: Path, bounds: Bounds | None = None) -> list[str]:
    """Find snippet-quality problems across a build output.

    Args:
        dist: Build output directory (``*.html`` scanned recursively;
            noindex pages, 404.html, and Pagefind internals are
            skipped).
        bounds: Length limits; defaults to :class:`Bounds`.

    Returns:
        Human-readable problems, page problems first (sorted by
        path), then cross-page title duplicates. Empty when clean.
    """
    limits = bounds or Bounds()
    problems: list[str] = []
    titles: dict[str, list[str]] = {}
    for path in sorted(dist.rglob("*.html")):
        rel = path.relative_to(dist).as_posix()
        if _skip(rel):
            continue
        html = path.read_text(encoding="utf-8", errors="replace")
        if _NOINDEX.search(html):
            continue

        match = _TITLE.search(html)
        title = match.group(1).strip() if match else ""
        if not title:
            problems.append(f"{rel}: missing <title>")
        else:
            titles.setdefault(title, []).append(rel)
            if len(title) > limits.title_max:
                problems.append(
                    f"{rel}: title is {len(title)} chars "
                    f"(max {limits.title_max}, truncated in SERPs)"
                )
            elif len(title) < limits.title_min:
                problems.append(
                    f"{rel}: title is {len(title)} chars "
                    f"(min {limits.title_min})"
                )

        tag = _META_DESCRIPTION_TAG.search(html)
        content = _CONTENT_ATTR.search(tag.group(0)) if tag else None
        description = content.group(1).strip() if content else ""
        if not description:
            problems.append(f"{rel}: missing meta description")
        elif len(description) > limits.description_max:
            problems.append(
                f"{rel}: description is {len(description)} chars "
                f"(max {limits.description_max}, truncated in SERPs)"
            )
        elif len(description) < limits.description_min:
            problems.append(
                f"{rel}: description is {len(description)} chars "
                f"(min {limits.description_min}, too thin to win the click)"
            )

    for title, pages in sorted(titles.items()):
        if len(pages) > 1:
            problems.append(f"duplicate title {title!r}: {', '.join(pages)}")
    return problems
