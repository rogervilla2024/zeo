"""CLI gate: article dates are chronologically honest.

Usage:
    python check_article_dates.py --content src/content/blog

updatedDate must not precede pubDate (a "refresh" dated into the
past lies to every freshness signal), and neither date may sit in
the future beyond one day of timezone slack (future dates corrupt
the sitemap's lastmod and the freshness live gate). Exits 1 on any
violation, 2 when the content directory does not exist.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from seo_content_forge.content_checks import check_dates


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when every article's dates are sane."""
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
        help="Accepted for gate-runner uniformity; unused.",
    )
    args = parser.parse_args(argv)

    if not args.content.is_dir():
        print(f"{args.content} is not a directory", file=sys.stderr)
        return 2

    problems = check_dates(args.content, date.today())
    for problem in problems:
        print(f"DATES {problem}")
    total = len(list(args.content.rglob("*.md")))
    if problems:
        print(f"\n{len(problems)} date problem(s) across {total} article(s).")
        return 1
    print(f"OK: {total} article(s), dates are chronologically sane.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
