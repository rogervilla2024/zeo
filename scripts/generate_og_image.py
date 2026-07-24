"""CLI to render an Open Graph share image (1200x630 PNG).

Usage:
    python generate_og_image.py --title "Article title" \
        --site-name "Example" --output og-article.png
    python generate_og_image.py --title "T" --site-name "S" \
        --output og.png --background "#101828" --accent "#38bdf8"

Renders a deterministic card (background, accent bar, wrapped title,
site name) so every page can ship an ``og:image`` without a design tool.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from seo_content_forge.ogimage import OgImageSpec, render_og_image


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns a process exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True, help="Page or article title.")
    parser.add_argument("--site-name", required=True, help="Brand line.")
    parser.add_argument("--output", required=True, type=Path, help="PNG file to write.")
    parser.add_argument("--background", default="#101828", help="Background hex.")
    parser.add_argument("--accent", default="#38bdf8", help="Accent hex.")
    parser.add_argument("--text-color", default="#ffffff", help="Title hex.")
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=630)
    args = parser.parse_args(argv)

    spec = OgImageSpec(
        title=args.title,
        site_name=args.site_name,
        width=args.width,
        height=args.height,
        background=args.background,
        accent=args.accent,
        text_color=args.text_color,
    )
    image = render_og_image(spec)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output, format="PNG")
    print(f"Wrote {args.output} ({args.width}x{args.height})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
