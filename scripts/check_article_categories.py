"""CLI gate: every article belongs to a pillar category.

Usage:
    python check_article_categories.py --content src/content/blog \\
        --config site.config.json

The homepage category strips, the /category/ archives, and the
article breadcrumbs all key off the ``category`` frontmatter field;
an uncategorized article silently drops out of all three. Enforcement
follows ``content.require_category`` in site.config.json (missing key
means required); set it to false to opt a site out. Exits 1 on any
violation, 2 when the content directory does not exist.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import orjson

from seo_content_forge.content_checks import check_categories


def category_required(config_path: Path) -> bool:
    """Read ``content.require_category`` (missing config or key: True)."""
    if not config_path.is_file():
        return True
    config = orjson.loads(config_path.read_bytes())
    section = config.get("content") if isinstance(config, dict) else None
    if isinstance(section, dict):
        value = section.get("require_category")
        if isinstance(value, bool):
            return value
    return True


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when every article has a category."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--content",
        type=Path,
        default=Path("src/content/blog"),
        help="Directory of article markdown files.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("site.config.json"),
        help="Site config providing content.require_category (optional).",
    )
    args = parser.parse_args(argv)

    if not args.content.is_dir():
        print(f"{args.content} is not a directory", file=sys.stderr)
        return 2

    if not category_required(args.config):
        print("Skipped: content.require_category is false for this site.")
        return 0

    problems = check_categories(args.content)
    for problem in problems:
        print(f"CATEGORY {problem}")
    total = len(list(args.content.rglob("*.md")))
    if problems:
        print(f"\n{len(problems)} uncategorized of {total} article(s).")
        return 1
    print(f"OK: {total} article(s), every one categorized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
