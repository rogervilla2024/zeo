"""CLI to render the variant gallery: 40 baselines, light and dark.

Usage:
    python fleet_preview.py --output fleet-preview
    python fleet_preview.py --config ../site.config.json --output preview

Writes one self-contained HTML preview per variant (plus a -dark
twin) and an index.html gallery with every pair side by side, all
from the same canned sample content - so picking theme.variant is a
visual decision, not a guess from a text catalog. Pass --config to
preview with a real site's palette and fonts instead of defaults.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import orjson

from seo_content_forge.preview import write_gallery
from seo_content_forge.theme_css import ThemeTokens, from_config


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 on success."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("fleet-preview"),
        help="Directory for the gallery (default: fleet-preview/).",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Optional site.config.json whose palette/fonts the "
        "previews should use.",
    )
    args = parser.parse_args(argv)

    tokens = ThemeTokens()
    if args.config:
        try:
            tokens = from_config(orjson.loads(args.config.read_bytes()))
        except (OSError, orjson.JSONDecodeError) as exc:
            print(f"Cannot read {args.config}: {exc}", file=sys.stderr)
            return 2

    count = write_gallery(args.output, tokens)
    print(f"Gallery written: {args.output}/index.html ({count} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
