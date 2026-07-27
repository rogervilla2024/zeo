"""CLI to fetch, optimize, and SEO-name stock photos from Pexels.

Usage:
    python fetch_stock_images.py --query "french press coffee" \
        --slug french-press-brewing --out-dir public/img --count 2
    python fetch_stock_images.py --query "thyme tea glass" \
        --slug kekik-cayi --out-dir public/img --hero

Requires PEXELS_API_KEY in the environment (free key from
pexels.com/api; store in .env, never in the repository). Downloads the
top results, resizes to a sane content width, converts to WebP, names
files for SEO, and prints a JSON manifest (file, width, height,
photographer credit) for the article to embed with alt text and
explicit dimensions. The Pexels license does not require attribution;
the credit field is there for sites that choose to give it.

``--hero`` fetches exactly one landscape photo and cover-crops it to
1600x900 as ``<slug>-hero.webp`` - the article's LCP image when
``images.hero`` is ``photo``.
"""

from __future__ import annotations

import argparse
import io
import os
import re
import sys
import urllib.request
from pathlib import Path

import orjson
from PIL import Image

from seo_content_forge.fetch import fetch

_API = "https://api.pexels.com/v1/search"
MAX_WIDTH = 1600
HERO_SIZE = (1600, 900)


def slugify(text: str) -> str:
    """Lowercase, hyphenated, ascii-only slug for filenames."""
    text = re.sub(r"[^a-z0-9]+", "-", text.lower())
    return text.strip("-") or "image"


def cover_crop(image: Image.Image, size: tuple[int, int] = HERO_SIZE) -> Image.Image:
    """Scale-and-center-crop an image to exactly ``size`` (cover fit).

    Args:
        image: Source image (any aspect ratio).
        size: Target (width, height).

    Returns:
        A new image of exactly ``size`` with the center preserved.
    """
    target_width, target_height = size
    scale = max(target_width / image.width, target_height / image.height)
    scaled = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = (scaled.width - target_width) // 2
    top = (scaled.height - target_height) // 2
    return scaled.crop((left, top, left + target_width, top + target_height))


def output_name(slug: str, index: int, hero: bool) -> str:
    """The SEO filename for one downloaded photo."""
    if hero:
        return f"{slugify(slug)}-hero.webp"
    return f"{slugify(slug)}-{index}.webp"


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when at least one image was written."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True, help="Search query (English).")
    parser.add_argument("--slug", required=True, help="SEO filename base.")
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--count", type=int, default=2)
    parser.add_argument(
        "--hero",
        action="store_true",
        help="Fetch one landscape photo cover-cropped to 1600x900 "
        "as <slug>-hero.webp.",
    )
    args = parser.parse_args(argv)
    if args.hero:
        args.count = 1

    key = os.environ.get("PEXELS_API_KEY", "")
    if not key:
        print("PEXELS_API_KEY is not set (.env).", file=sys.stderr)
        return 2

    orientation = "&orientation=landscape" if args.hero else ""
    result = fetch(
        f"{_API}?query={args.query.replace(' ', '%20')}"
        f"&per_page={args.count}{orientation}",
        headers={"Authorization": key},
    )
    if not result.ok:
        print(f"Pexels search failed (HTTP {result.status})", file=sys.stderr)
        return 2

    photos = orjson.loads(result.text).get("photos", [])
    args.out_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, object]] = []
    for index, photo in enumerate(photos[: args.count], start=1):
        src = str(photo.get("src", {}).get("large2x", ""))
        if not src:
            continue
        request = urllib.request.Request(src, headers={"User-Agent": "zeo/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                image_bytes: bytes = response.read()
        except OSError as exc:
            print(f"download failed: {exc}", file=sys.stderr)
            continue
        with Image.open(io.BytesIO(image_bytes)) as source_image:
            image = source_image.convert("RGB")
            if args.hero:
                image = cover_crop(image)
            elif image.width > MAX_WIDTH:
                ratio = MAX_WIDTH / image.width
                image = image.resize(
                    (MAX_WIDTH, int(image.height * ratio)),
                    Image.Resampling.LANCZOS,
                )
            name = output_name(args.slug, index, args.hero)
            image.save(args.out_dir / name, format="WEBP", quality=82)
            manifest.append(
                {
                    "file": name,
                    "width": image.width,
                    "height": image.height,
                    "credit": str(photo.get("photographer", "")),
                    "source": str(photo.get("url", "")),
                }
            )

    if not manifest:
        print("No image could be downloaded.", file=sys.stderr)
        return 1
    sys.stdout.buffer.write(orjson.dumps(manifest, option=orjson.OPT_INDENT_2))
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
