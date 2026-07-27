"""CLI gate: SERP snippet quality over the build output.

Usage:
    python check_meta_quality.py --dist dist
    python check_meta_quality.py --dist dist --title-max 65

Every indexable page needs a title (10-60 chars) and a meta
description (40-160 chars), and no two pages may share a title.
Noindex pages, 404.html, and Pagefind internals are skipped. Exits 1
on any violation, 2 when the dist directory does not exist.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from seo_content_forge.meta_quality import Bounds, check_meta

_DEFAULTS = Bounds()


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when every page passes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", required=True, type=Path)
    parser.add_argument("--title-min", type=int, default=_DEFAULTS.title_min)
    parser.add_argument("--title-max", type=int, default=_DEFAULTS.title_max)
    parser.add_argument(
        "--desc-min", type=int, default=_DEFAULTS.description_min
    )
    parser.add_argument(
        "--desc-max", type=int, default=_DEFAULTS.description_max
    )
    args = parser.parse_args(argv)

    if not args.dist.is_dir():
        print(f"{args.dist} is not a directory", file=sys.stderr)
        return 2

    bounds = Bounds(
        title_min=args.title_min,
        title_max=args.title_max,
        description_min=args.desc_min,
        description_max=args.desc_max,
    )
    problems = check_meta(args.dist, bounds)
    for problem in problems:
        print(f"META {problem}")
    if problems:
        print(f"\n{len(problems)} snippet problem(s).")
        return 1
    print("OK: titles and descriptions within bounds, no duplicates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
