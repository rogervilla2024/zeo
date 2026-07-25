"""CLI to fetch, optimize, and SEO-name stock photos from Pexels.

Usage:
    python fetch_stock_images.py --query "french press coffee" \
        --slug french-press-brewing --out-dir public/img --count 2

Requires PEXELS_API_KEY in the environment (free key from
pexels.com/api; store in .env, never in the repository). Downloads the
top results, resizes to a sane content width, converts to WebP, names
files for SEO, and prints a JSON manifest (file, width, height,
photographer credit) for the article to embed with alt text and
explicit dimensions.
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
MAX_WIDTH = 1280


def slugify(text: str) -> str:
    """Lowercase, hyphenated, ascii-only slug for filenames."""
    text = re.sub(r"[^a-z0-9]+", "-", text.lower())
    return text.strip("-") or "image"


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when at least one image was written."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True, help="Search query (English).")
    parser.add_argument("--slug", required=True, help="SEO filename base.")
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--count", type=int, default=2)
    args = parser.parse_args(argv)

    key = os.environ.get("PEXELS_API_KEY", "")
    if not key:
        print("PEXELS_API_KEY is not set (.env).", file=sys.stderr)
        return 2

    result = fetch(
        f"{_API}?query={args.query.replace(' ', '%20')}&per_page={args.count}",
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
            if image.width > MAX_WIDTH:
                ratio = MAX_WIDTH / image.width
                image = image.resize(
                    (MAX_WIDTH, int(image.height * ratio)),
                    Image.Resampling.LANCZOS,
                )
            name = f"{slugify(args.slug)}-{index}.webp"
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
