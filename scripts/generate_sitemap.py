"""CLI to generate XML sitemaps from a JSON list of URL entries.

Usage:
    python generate_sitemap.py --input urls.json --base-url https://example.com
    python generate_sitemap.py --input urls.json --base-url https://example.com \
        --out-dir ./public

The ``--input`` file is a JSON array of entries. Each entry needs ``loc``
and may include ``lastmod``, ``changefreq``, ``priority``, ``alternates``
(a list of ``{"hreflang": ..., "href": ...}``), and ``images`` (a list of
absolute image URLs, emitted as Google image-sitemap entries). Files are
written to ``--out-dir`` when given, otherwise printed to stdout.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import orjson

from seo_content_forge.sitemap import Alternate, ImageRef, UrlEntry, build_sitemaps


def _parse_entries(raw: object) -> list[UrlEntry]:
    """Convert parsed JSON into validated :class:`UrlEntry` objects."""
    if not isinstance(raw, list):
        raise ValueError("input must be a JSON array of URL entries")
    entries: list[UrlEntry] = []
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError("each URL entry must be a JSON object")
        alternates = [
            Alternate(hreflang=str(alt["hreflang"]), href=str(alt["href"]))
            for alt in item.get("alternates", [])
        ]
        images = [ImageRef(loc=str(image)) for image in item.get("images", [])]
        entries.append(
            UrlEntry(
                loc=str(item["loc"]),
                lastmod=item.get("lastmod"),
                changefreq=item.get("changefreq"),
                priority=item.get("priority"),
                alternates=alternates,
                images=images,
            )
        )
    return entries


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns a process exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="JSON array of URL entries.",
    )
    parser.add_argument(
        "--base-url",
        required=True,
        help="Public base URL where sitemap files are hosted.",
    )
    parser.add_argument(
        "--file-prefix",
        default="sitemap",
        help="Base filename for generated sitemap files.",
    )
    parser.add_argument(
        "--lastmod",
        help="Optional last-modified date for the sitemap index entries.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        help="Directory to write files into; prints to stdout if omitted.",
    )
    args = parser.parse_args(argv)

    entries = _parse_entries(orjson.loads(args.input.read_bytes()))
    files = build_sitemaps(
        entries,
        index_base_url=args.base_url,
        file_prefix=args.file_prefix,
        lastmod=args.lastmod,
    )

    if args.out_dir:
        args.out_dir.mkdir(parents=True, exist_ok=True)
        for filename, content in files.items():
            (args.out_dir / filename).write_text(content, encoding="utf-8")
        print(f"Wrote {len(files)} file(s) to {args.out_dir}")
    else:
        for filename, content in files.items():
            sys.stdout.write(f"===== {filename} =====\n{content}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
