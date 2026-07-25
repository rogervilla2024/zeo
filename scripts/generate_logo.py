"""CLI to generate a site logo from the brand name and token colors.

Usage:
    python generate_logo.py --name "Example Site" --output public/logo.png \
        --background "#0f766e" --text-color "#ffffff"

Renders a 512x512 rounded-square monogram (first letters of the brand)
suitable as the source for generate_favicons.py and as a header logo.
Every new site MUST have a logo and the favicon set generated at
bootstrap; a site without them fails the visual review.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from seo_content_forge.ogimage import _load_font


def monogram(name: str) -> str:
    """First letters of up to two words, uppercased."""
    words = [word for word in name.split() if word]
    letters = "".join(word[0] for word in words[:2])
    return (letters or "S").upper()


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns a process exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Brand name.")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--background", default="#0f766e")
    parser.add_argument("--text-color", default="#ffffff")
    parser.add_argument("--size", type=int, default=512)
    args = parser.parse_args(argv)

    size = args.size
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(
        (0, 0, size - 1, size - 1), radius=size // 5, fill=args.background
    )
    text = monogram(args.name)
    font = _load_font(size // 2 if len(text) == 1 else size // 3)
    box = draw.textbbox((0, 0), text, font=font)
    draw.text(
        ((size - box[2] + box[0]) / 2 - box[0], (size - box[3] + box[1]) / 2 - box[1]),
        text,
        font=font,
        fill=args.text_color,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output, format="PNG")
    print(f"Wrote {args.output} ({size}x{size}, monogram {text})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
