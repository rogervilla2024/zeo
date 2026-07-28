"""Orphan-article detection over built HTML.

The internal-links gate enforces OUTBOUND links from every article;
this is its mirror: every article should also RECEIVE at least one
contextual link from another article's reading column. Hub pages
(blog index, category archives) link everything mechanically, so
they prove nothing about editorial linking - only links found inside
another article's ``<article class="prose">`` block count. An
article nothing points to is the one Google crawls last and ranks
worst.
"""

from __future__ import annotations

import re
from pathlib import Path

_ARTICLE_MARKER = '<article class="prose"'
_HREF = re.compile(r"href=\"(/[^\"#?]*)\"")


def _prose_segment(html: str) -> str:
    """Return the reading-column markup, empty when not an article."""
    start = html.find(_ARTICLE_MARKER)
    if start == -1:
        return ""
    end = html.find("</article>", start)
    return html[start : end if end != -1 else len(html)]


def _canonical_path(rel: str) -> str:
    """dist-relative index.html path -> site URL path."""
    if rel.endswith("index.html"):
        rel = rel[: -len("index.html")]
    return "/" + rel.strip("/") + "/" if rel.strip("/") else "/"


def find_orphans(dist: Path, min_articles: int = 4) -> list[str]:
    """Find article pages with no incoming in-prose links.

    Args:
        dist: Build output directory.
        min_articles: Below this many articles the check is vacuous
            (a two-article site cannot interlink richly yet) and
            passes.

    Returns:
        Human-readable problems, one per orphaned article, sorted;
        empty when every article is referenced or the site is small.
    """
    articles: dict[str, str] = {}
    for path in sorted(dist.rglob("index.html")):
        rel = path.relative_to(dist).as_posix()
        if rel == "index.html" or rel.startswith("pagefind/"):
            continue
        html = path.read_text(encoding="utf-8", errors="replace")
        segment = _prose_segment(html)
        if segment:
            articles[_canonical_path(rel)] = segment

    if len(articles) < min_articles:
        return []

    incoming: dict[str, int] = {path: 0 for path in articles}
    for source_path, segment in articles.items():
        for href in _HREF.findall(segment):
            target = "/" + href.strip("/") + "/" if href.strip("/") else "/"
            if target != source_path and target in incoming:
                incoming[target] += 1

    return [
        f"{path}: no other article links to it "
        "(add reverse links via suggest_internal_links.py)"
        for path, count in sorted(incoming.items())
        if count == 0
    ]
