"""CLI to find broken internal links in a built static site.

Usage:
    python check_broken_links.py --dist dist

Scans every HTML file, collects internal hrefs, and verifies each
resolves to a file in the build output. Exits 1 on any broken link.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def resolve(dist: Path, href: str) -> bool:
    """True when an internal href maps to a file in dist."""
    path = href.split("#")[0].split("?")[0]
    if not path:
        return True
    target = dist / path.lstrip("/")
    return (
        target.is_file()
        or (target / "index.html").is_file()
        or target.with_suffix(".html").is_file()
    )


def scan(dist: Path) -> list[tuple[Path, str]]:
    """Return (page, href) pairs for every broken internal link."""
    broken: list[tuple[Path, str]] = []
    for page in dist.rglob("*.html"):
        html = page.read_text(encoding="utf-8", errors="replace")
        for href in re.findall(r'href=["\']([^"\']+)["\']', html):
            if href.startswith(("http", "mailto:", "tel:", "#", "//")):
                continue
            if not resolve(dist, href):
                broken.append((page, href))
    return broken


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when no internal link is broken."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", required=True, type=Path)
    args = parser.parse_args(argv)
    if not args.dist.is_dir():
        print(f"{args.dist} is not a directory", file=sys.stderr)
        return 2
    broken = scan(args.dist)
    for page, href in broken[:20]:
        print(f"BROKEN {href}  (on {page.relative_to(args.dist)})")
    print(f"\n{len(broken)} broken internal link(s).")
    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main())
