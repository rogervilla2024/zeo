"""CLI to render the variant gallery: 40 baselines, light and dark.

Usage:
    python fleet_preview.py --output fleet-preview
    python fleet_preview.py --config ../site.config.json --output preview
    python fleet_preview.py --anatomy --variant noir --output anatomies

Writes one self-contained HTML preview per variant (plus a -dark
twin) and an index.html gallery with every pair side by side, all
from the same canned sample content - so picking theme.variant is a
visual decision, not a guess from a text catalog. Pass --config to
preview with a real site's palette and fonts instead of defaults.
Pass --anatomy to render the OTHER axis: the twelve A recipes
(recipes.md "Page anatomies") on one variant, so picking
homepage.hero / aside / rail is a visual decision too.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import orjson

from seo_content_forge.preview import write_anatomy_gallery, write_gallery
from seo_content_forge.theme_css import (
    FINISHES,
    VARIANTS,
    ThemeTokens,
    from_config,
)


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
    parser.add_argument(
        "--finish",
        default="",
        help="Render every preview with a surface finish: glass, "
        "gradient, or soft (default: flat).",
    )
    parser.add_argument(
        "--anatomy",
        action="store_true",
        help="Render the anatomy gallery instead: the twelve A "
        "recipes on one variant (see --variant).",
    )
    parser.add_argument(
        "--variant",
        default="minimal",
        help="Variant the anatomy gallery renders with "
        "(default: minimal; only used with --anatomy).",
    )
    args = parser.parse_args(argv)

    if args.anatomy and args.variant not in VARIANTS:
        print(
            f"Unknown variant {args.variant!r}; run without --anatomy "
            "to browse the variant catalog.",
            file=sys.stderr,
        )
        return 2
    if args.finish and args.finish not in FINISHES:
        print(
            f"Unknown finish {args.finish!r}; choose from "
            f"{', '.join(FINISHES)}.",
            file=sys.stderr,
        )
        return 2

    tokens = ThemeTokens()
    if args.config:
        try:
            tokens = from_config(orjson.loads(args.config.read_bytes()))
        except (OSError, orjson.JSONDecodeError) as exc:
            print(f"Cannot read {args.config}: {exc}", file=sys.stderr)
            return 2

    if args.finish:
        tokens.finish = args.finish
    if args.anatomy:
        count = write_anatomy_gallery(args.output, tokens, args.variant)
        print(
            f"Anatomy gallery written: {args.output}/index.html "
            f"({count} files, variant {args.variant})"
        )
        return 0
    count = write_gallery(args.output, tokens)
    print(f"Gallery written: {args.output}/index.html ({count} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
