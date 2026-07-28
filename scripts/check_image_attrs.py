"""CLI gate: every <img> ships alt text and explicit dimensions.

Usage:
    python check_image_attrs.py --dist dist

Scans the build output for ``<img>`` tags without an ``alt``
attribute (empty alt is allowed - the explicit decorative marker) or
without both ``width`` and ``height`` (the browser cannot reserve
space, so the layout shifts while images load). Markdown ``![]()``
syntax renders without dimensions - write body images as raw
``<img>`` tags, as the generate-article-images skill does. Exits 1
on any violation, 2 when the dist directory does not exist.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from seo_content_forge.image_attrs import check_image_attrs


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when every image passes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", required=True, type=Path)
    args = parser.parse_args(argv)

    if not args.dist.is_dir():
        print(f"{args.dist} is not a directory", file=sys.stderr)
        return 2

    problems = check_image_attrs(args.dist)
    for problem in problems:
        print(f"IMG {problem}")
    if problems:
        print(f"\n{len(problems)} image attribute problem(s).")
        return 1
    print("OK: every <img> has alt and explicit dimensions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
