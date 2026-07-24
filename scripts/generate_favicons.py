"""CLI to generate the favicon set and web manifest from one logo.

Usage:
    python generate_favicons.py --logo logo.png --out-dir ./public \
        --name "Example Site" --short-name "Example"

Writes favicon-16x16.png, favicon-32x32.png, apple-touch-icon.png,
android-chrome-192x192.png, android-chrome-512x512.png, and
site.webmanifest, then prints the head snippet to paste into the layout.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from seo_content_forge.favicons import HEAD_SNIPPET, ManifestSpec, generate_assets


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns a process exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--logo", required=True, type=Path, help="Source logo image (square)."
    )
    parser.add_argument(
        "--out-dir", required=True, type=Path, help="Static assets directory."
    )
    parser.add_argument("--name", required=True, help="Full site name.")
    parser.add_argument("--short-name", required=True, help="Home-screen label.")
    parser.add_argument("--theme-color", default="#101828", help="Theme hex.")
    parser.add_argument(
        "--background-color", default="#ffffff", help="Splash background hex."
    )
    args = parser.parse_args(argv)

    with Image.open(args.logo) as logo:
        written = generate_assets(
            logo,
            args.out_dir,
            ManifestSpec(
                name=args.name,
                short_name=args.short_name,
                theme_color=args.theme_color,
                background_color=args.background_color,
            ),
        )

    print(f"Wrote {len(written)} files to {args.out_dir}: {', '.join(written)}")
    print("\nAdd to the layout <head>:\n" + HEAD_SNIPPET)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
