"""CLI to draw a hero cover image for the A7 "cover" anatomy.

Usage:
    python generate_cover_image.py --root . --title "Site name" \
        --tagline "one line" --style nature

Draws a wide (1600x900) self-contained SVG cover tinted from the
site's palette into public/img/cover.svg and prints the config lines
to switch the homepage to the cover anatomy. Deterministic per
title; original art, no stock, no licenses. The A7 hero overlays its
own h1 and tagline, so by default the image carries art and scrim
only; pass --with-text to bake the words in for standalone or social
use.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from generate_entity_images import _primary_color
from seo_content_forge.illustrations import STYLES, cover_svg


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 on success, 2 on bad input."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Site project root (default: current directory).",
    )
    parser.add_argument("--title", required=True, help="Cover headline.")
    parser.add_argument(
        "--tagline", default="", help="Supporting line under the title."
    )
    parser.add_argument(
        "--style",
        default="abstract",
        help=f"Drawing style: one of {', '.join(STYLES)}.",
    )
    parser.add_argument(
        "--output",
        default="cover.svg",
        help="File name under public/img/ (default: cover.svg).",
    )
    parser.add_argument(
        "--with-text",
        action="store_true",
        help=(
            "Bake the title/tagline into the image. Leave off for the "
            "A7 hero, which overlays its own h1 and tagline."
        ),
    )
    args = parser.parse_args(argv)

    if args.style not in STYLES:
        print(
            f"Unknown style {args.style!r}; choose from {', '.join(STYLES)}.",
            file=sys.stderr,
        )
        return 2

    primary = _primary_color(args.root)
    img_dir = args.root / "public" / "img"
    img_dir.mkdir(parents=True, exist_ok=True)
    target = img_dir / args.output
    target.write_text(
        cover_svg(
            args.title,
            args.tagline,
            args.style,
            primary,
            draw_text=args.with_text,
        ),
        encoding="utf-8",
    )
    print(f"Cover written: {target}")
    print("Switch the homepage to the cover anatomy in site.config.json:")
    print(f'  "homepage": {{ "hero": "cover", "hero_image": "/img/{args.output}" }}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
