"""CLI to enforce the theme's JavaScript budget on a built site.

Usage:
    python check_js_budget.py --dist dist
    python check_js_budget.py --dist dist --max-kb 50

Sums every .js/.mjs file in the build output and fails when the total
exceeds the budget (default 30 KB). "Fast theme" is a tested rule here,
not a promise: run this after each build, or wire it into CI next to
the other checkers.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

DEFAULT_BUDGET_KB: int = 30


def collect_js_sizes(dist: Path) -> list[tuple[Path, int]]:
    """Return (path, size in bytes) for every JS file under ``dist``.

    Args:
        dist: Build output directory.

    Returns:
        Files sorted largest first.
    """
    files = [
        (path, path.stat().st_size)
        for pattern in ("*.js", "*.mjs")
        for path in dist.rglob(pattern)
        if path.is_file()
    ]
    files.sort(key=lambda item: -item[1])
    return files


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when the budget holds."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dist", required=True, type=Path, help="Build output directory."
    )
    parser.add_argument(
        "--max-kb",
        type=int,
        default=DEFAULT_BUDGET_KB,
        help=f"Total JS budget in KB (default {DEFAULT_BUDGET_KB}).",
    )
    args = parser.parse_args(argv)

    if not args.dist.is_dir():
        print(f"{args.dist} is not a directory", file=sys.stderr)
        return 2

    files = collect_js_sizes(args.dist)
    total_kb = sum(size for _, size in files) / 1024

    for path, size in files[:10]:
        print(f"{size / 1024:8.1f} KB  {path.relative_to(args.dist)}")
    print(f"\nTotal JavaScript: {total_kb:.1f} KB (budget {args.max_kb} KB)")

    if total_kb > args.max_kb:
        print(
            "Over budget: remove or island-ize scripts; content pages "
            "should ship near-zero JavaScript.",
            file=sys.stderr,
        )
        return 1
    print("Within budget.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
