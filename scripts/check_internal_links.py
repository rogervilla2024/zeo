"""CLI gate: every article carries its in-body internal links.

Usage:
    python check_internal_links.py --content src/content/blog \\
        --config site.config.json
    python check_internal_links.py --content src/content/blog --min 2

Counts root-relative links in the article body SOURCE (markdown links
and HTML anchors, images excluded). The minimum comes from
``content.min_internal_links`` in site.config.json (default 2), and
scales down automatically on young sites: an article can only link to
pages that exist, so a two-article site needs one link each. Exits 1
on any violation, 2 when the content directory does not exist.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import orjson

from seo_content_forge.content_checks import check_internal_links

DEFAULT_MIN = 2


def resolve_min(config_path: Path, override: int | None) -> int:
    """Pick the internal-link minimum for a run.

    Args:
        config_path: site.config.json location; its
            ``content.min_internal_links`` is the default policy.
        override: --min value; wins when given.

    Returns:
        The minimum in-body internal link count to enforce.
    """
    if override is not None:
        return override
    if config_path.is_file():
        config = orjson.loads(config_path.read_bytes())
        section = config.get("content") if isinstance(config, dict) else None
        if isinstance(section, dict):
            value = section.get("min_internal_links")
            if isinstance(value, int) and value >= 0:
                return value
    return DEFAULT_MIN


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
        help="Site config providing content.min_internal_links (optional).",
    )
    parser.add_argument(
        "--min",
        type=int,
        help="Required in-body internal links; overrides the config.",
    )
    args = parser.parse_args(argv)

    if not args.content.is_dir():
        print(f"{args.content} is not a directory", file=sys.stderr)
        return 2

    minimum = resolve_min(args.config, args.min)
    problems = check_internal_links(args.content, minimum)
    for problem in problems:
        print(f"LINKS {problem}")
    total = len(list(args.content.rglob("*.md")))
    if problems:
        print(f"\n{len(problems)} link problem(s) across {total} article(s).")
        return 1
    print(f"OK: {total} article(s) meet the internal-link minimum ({minimum}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
