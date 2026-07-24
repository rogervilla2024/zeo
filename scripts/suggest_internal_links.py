"""CLI for mandatory smart internal linking of a markdown article.

Usage:
    python suggest_internal_links.py --article draft.md --inventory pages.json
    python suggest_internal_links.py --article draft.md --inventory pages.json \
        --apply --output draft-linked.md

The ``--inventory`` file is the site's content inventory: a JSON array of
``{"url": ..., "title": ..., "keywords": [...]}`` objects (derivable from
the sitemap or the content collection). Without ``--apply`` the tool
prints the suggestions for review; with ``--apply`` it writes the article
with the links inserted. Exits 1 when no link opportunity is found, since
articles in this toolkit must not ship without internal links.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import orjson

from seo_content_forge.interlink import PageRef, apply_links, suggest_links


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when at least one link was found."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--article", required=True, type=Path, help="Article markdown file."
    )
    parser.add_argument(
        "--inventory", required=True, type=Path, help="Content inventory JSON."
    )
    parser.add_argument(
        "--article-url", help="URL of this article, excluded as a link target."
    )
    parser.add_argument(
        "--max-links", type=int, default=6, help="Density cap (default 6)."
    )
    parser.add_argument(
        "--apply", action="store_true", help="Insert the links into the article."
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Where to write the linked article (with --apply); defaults to "
        "overwriting --article.",
    )
    args = parser.parse_args(argv)

    markdown = args.article.read_text(encoding="utf-8")
    pages = [
        PageRef(
            url=str(item["url"]),
            title=str(item.get("title", "")),
            keywords=[str(keyword) for keyword in item.get("keywords", [])],
        )
        for item in orjson.loads(args.inventory.read_bytes())
    ]

    suggestions = suggest_links(
        markdown, pages, article_url=args.article_url, max_links=args.max_links
    )
    if not suggestions:
        print(
            "No internal-link opportunity found. Articles must not ship "
            "without internal links: extend the inventory keywords or add "
            "links to pillar pages manually.",
            file=sys.stderr,
        )
        return 1

    for suggestion in suggestions:
        print(
            f"line {suggestion.line_index + 1}: "
            f'"{suggestion.anchor}" -> {suggestion.url}'
        )

    if args.apply:
        target = args.output or args.article
        target.write_text(apply_links(markdown, suggestions), encoding="utf-8")
        print(f"Applied {len(suggestions)} link(s) to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
