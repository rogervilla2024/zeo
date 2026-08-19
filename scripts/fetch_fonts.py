"""CLI to install a self-hosted webfont pairing (T recipe) on a site.

Usage:
    python fetch_fonts.py --pairing T2 --root ~/sites/my-site
    python fetch_fonts.py --list

Downloads the pairing's woff2 files (Fontsource CDN, OFL-licensed
families) into <root>/public/fonts/, writes <root>/src/styles/
fonts.css with @font-face rules (font-display: swap), and prints the
theme.fonts values to set in site.config.json. Run once at design
time - the fonts deploy with the site, nothing is fetched at runtime.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from urllib.error import URLError

from seo_content_forge.fonts import (
    DEFAULT_BASE_URL,
    PAIRINGS,
    config_fonts,
    fetch_pairing,
)


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 on success."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pairing",
        help="T recipe code (T1-T5); see --list.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Site project root (default: current directory).",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="Font CDN base URL (override for mirrors or tests).",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List the available pairings and exit.",
    )
    args = parser.parse_args(argv)

    if args.list or not args.pairing:
        for entry in PAIRINGS.values():
            fonts = config_fonts(entry)
            print(
                f"{entry.code}  {entry.name}: "
                f"{entry.heading.family} + {entry.body.family}"
            )
            print(f"    heading: {fonts['heading']}")
            print(f"    body:    {fonts['body']}")
        return 0 if args.list else 2

    pairing = PAIRINGS.get(args.pairing.upper())
    if pairing is None:
        print(
            f"Unknown pairing {args.pairing!r}; choose from "
            f"{', '.join(PAIRINGS)}.",
            file=sys.stderr,
        )
        return 2

    try:
        written = fetch_pairing(pairing, args.root, base_url=args.base_url)
    except (URLError, OSError) as exc:
        print(f"Download failed: {exc}", file=sys.stderr)
        return 1

    fonts = config_fonts(pairing)
    print(f"Installed {len(written)} font file(s) into public/fonts/.")
    print("Wrote src/styles/fonts.css. Set in site.config.json:")
    print(f'  "fonts": {{ "heading": "{fonts["heading"]}",')
    print(f'             "body": "{fonts["body"]}" }}')
    print("Then regenerate tokens.css (generate_theme_css.py).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
