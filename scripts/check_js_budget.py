"""CLI to enforce the theme's JavaScript budget on a built site.

Usage:
    python check_js_budget.py --dist dist
    python check_js_budget.py --dist dist --max-kb 50

Sums every .js/.mjs file in the build output and fails when the total
exceeds the budget (default 30 KB). "Fast theme" is a tested rule here,
not a promise: run this after each build, or wire it into CI next to
the other checkers.

``dist/pagefind/`` is excluded by default: Pagefind static search is
the theme's one sanctioned JavaScript exception, and its assets load
only on the /search page, never on content pages. Pass
``--include-pagefind`` to count it anyway.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

DEFAULT_BUDGET_KB: int = 30
PAGEFIND_DIR: str = "pagefind"


def collect_js_sizes(
    dist: Path, include_pagefind: bool = False
) -> list[tuple[Path, int]]:
    """Return (path, size in bytes) for every JS file under ``dist``.

    Args:
        dist: Build output directory.
        include_pagefind: Also count files under ``dist/pagefind/``
            (excluded by default as the search-page-only exception).

    Returns:
        Files sorted largest first.
    """
    files = [
        (path, path.stat().st_size)
        for pattern in ("*.js", "*.mjs")
        for path in dist.rglob(pattern)
        if path.is_file()
        and (include_pagefind or path.relative_to(dist).parts[0] != PAGEFIND_DIR)
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
    parser.add_argument(
        "--include-pagefind",
        action="store_true",
        help="Count dist/pagefind/* too (excluded by default).",
    )
    args = parser.parse_args(argv)

    if not args.dist.is_dir():
        print(f"{args.dist} is not a directory", file=sys.stderr)
        return 2

    files = collect_js_sizes(args.dist, include_pagefind=args.include_pagefind)
    if not args.include_pagefind and (args.dist / PAGEFIND_DIR).is_dir():
        print(
            "note: dist/pagefind/* excluded (search-page-only exception); "
            "pass --include-pagefind to count it."
        )
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
