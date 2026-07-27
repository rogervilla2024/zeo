"""CLI gate: every article ships its hero and minimum body images.

Usage:
    python check_article_images.py --content src/content/blog \\
        --config site.config.json
    python check_article_images.py --content src/content/blog --min-body 2

Checks the content collection SOURCE (frontmatter ``image`` plus
in-body markdown/HTML images), because the built HTML cannot reveal an
image that was never added. The body minimum comes from
``images.min`` in site.config.json unless --min-body overrides it;
without either, only the hero is enforced. Exits 1 on any violation,
2 when the content directory does not exist.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import orjson

from seo_content_forge.article_images import check_articles


def resolve_min_body(config_path: Path, override: int | None) -> int:
    """Pick the body-image minimum for a run.

    Args:
        config_path: site.config.json location; its ``images.min`` is
            the default policy.
        override: --min-body value; wins when given.

    Returns:
        The minimum in-body image count to enforce (0 when neither
        source provides one).
    """
    if override is not None:
        return override
    if config_path.is_file():
        config = orjson.loads(config_path.read_bytes())
        images = config.get("images") if isinstance(config, dict) else None
        if isinstance(images, dict):
            value = images.get("min")
            if isinstance(value, int) and value >= 0:
                return value
    return 0


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when every article passes."""
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
        help="Site config providing images.min (optional).",
    )
    parser.add_argument(
        "--min-body",
        type=int,
        help="Required in-body images per article; overrides images.min.",
    )
    args = parser.parse_args(argv)

    if not args.content.is_dir():
        print(f"{args.content} is not a directory", file=sys.stderr)
        return 2

    min_body = resolve_min_body(args.config, args.min_body)
    problems = check_articles(args.content, min_body)
    for problem in problems:
        print(f"IMAGES {problem}")
    total = len(list(args.content.rglob("*.md")))
    if problems:
        print(f"\n{len(problems)} image problem(s) across {total} article(s).")
        return 1
    print(f"OK: {total} article(s), hero present, body minimum {min_body} met.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
