"""Image attribute checks over built HTML: alt and dimensions.

Every ``<img>`` must carry an ``alt`` attribute (empty is allowed -
that is the explicit decorative marker) and explicit ``width`` and
``height`` so the browser reserves space before the file loads
(no layout shift). This is already the pipeline standard - the
generate-article-images skill writes body images as raw ``<img>``
tags with dimensions precisely because markdown ``![]()`` syntax
renders without them - and this gate is what keeps the standard from
eroding one forgotten attribute at a time.
"""

from __future__ import annotations

import re
from pathlib import Path

_IMG_TAG = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
_SRC = re.compile(r"src=\"([^\"]*)\"", re.IGNORECASE)
_ALT = re.compile(r"\balt\s*=", re.IGNORECASE)
_WIDTH = re.compile(r"\bwidth\s*=", re.IGNORECASE)
_HEIGHT = re.compile(r"\bheight\s*=", re.IGNORECASE)


def _label(tag: str) -> str:
    """A short identifier for a tag in problem messages (its src)."""
    match = _SRC.search(tag)
    return match.group(1) if match else tag[:60]


def check_image_attrs(dist: Path) -> list[str]:
    """Find ``<img>`` tags missing alt or explicit dimensions.

    Args:
        dist: Build output directory (``*.html`` scanned recursively;
            Pagefind internals are skipped - accessibility applies to
            every other page, 404 included).

    Returns:
        Human-readable problems sorted by page; empty when clean.
    """
    problems: list[str] = []
    for path in sorted(dist.rglob("*.html")):
        rel = path.relative_to(dist).as_posix()
        if rel.startswith("pagefind/"):
            continue
        html = path.read_text(encoding="utf-8", errors="replace")
        for tag in _IMG_TAG.findall(html):
            label = _label(tag)
            if not _ALT.search(tag):
                problems.append(
                    f"{rel}: <img {label}> has no alt attribute "
                    '(use alt="" only for decorative images)'
                )
            if not (_WIDTH.search(tag) and _HEIGHT.search(tag)):
                problems.append(
                    f"{rel}: <img {label}> is missing width/height "
                    "(layout shifts while it loads)"
                )
    return problems
