"""CLI to enforce image weight and SVG safety on a built site.

Usage:
    python check_media_budget.py --dist dist --max-kb 5000

Sums raster image bytes in the build output against a budget and lints
every SVG for unsafe content (script, foreignObject, event handlers).
Exits 1 on either failure.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

UNSAFE_SVG = re.compile(r"(?is)<script|<foreignObject|on\w+\s*=")


def image_sizes(dist: Path) -> list[tuple[Path, int]]:
    """Raster image files under dist, largest first."""
    files = [
        (path, path.stat().st_size)
        for pattern in ("*.webp", "*.png", "*.jpg", "*.jpeg", "*.gif", "*.avif")
        for path in dist.rglob(pattern)
        if path.is_file()
    ]
    files.sort(key=lambda item: -item[1])
    return files


def unsafe_svgs(dist: Path) -> list[Path]:
    """SVG files containing scriptable content."""
    return [
        path
        for path in dist.rglob("*.svg")
        if UNSAFE_SVG.search(path.read_text(encoding="utf-8", errors="replace"))
    ]


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when budget and safety both pass."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", required=True, type=Path)
    parser.add_argument("--max-kb", type=int, default=5000)
    args = parser.parse_args(argv)
    if not args.dist.is_dir():
        print(f"{args.dist} is not a directory", file=sys.stderr)
        return 2

    files = image_sizes(args.dist)
    total_kb = sum(size for _, size in files) / 1024
    for path, size in files[:10]:
        print(f"{size / 1024:8.1f} KB  {path.relative_to(args.dist)}")
    print(f"\nTotal raster images: {total_kb:.1f} KB (budget {args.max_kb} KB)")

    bad_svgs = unsafe_svgs(args.dist)
    for path in bad_svgs:
        print(f"UNSAFE SVG: {path.relative_to(args.dist)}")

    if total_kb > args.max_kb or bad_svgs:
        print("Media budget or SVG safety failed.", file=sys.stderr)
        return 1
    print("Media budget and SVG safety pass.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
