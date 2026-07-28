"""CLI gate: every article receives a contextual link from another.

Usage:
    python check_orphan_pages.py --dist dist
    python check_orphan_pages.py --dist dist --min-articles 6

Mirror of the internal-links gate: outbound links are enforced at the
source; this checks the INBOUND side over the built HTML. Only links
found inside another article's reading column count - hub pages link
everything mechanically and prove nothing. Below --min-articles
(default 4) the check passes vacuously: a two-article site cannot
interlink richly yet. Exits 1 on orphans, 2 when dist is missing.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from seo_content_forge.orphans import find_orphans


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when no article is orphaned."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", required=True, type=Path)
    parser.add_argument(
        "--min-articles",
        type=int,
        default=4,
        help="Skip the check below this many articles (default 4).",
    )
    args = parser.parse_args(argv)

    if not args.dist.is_dir():
        print(f"{args.dist} is not a directory", file=sys.stderr)
        return 2

    problems = find_orphans(args.dist, min_articles=args.min_articles)
    for problem in problems:
        print(f"ORPHAN {problem}")
    if problems:
        print(f"\n{len(problems)} orphaned article(s).")
        return 1
    print("OK: every article receives at least one in-prose link.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
