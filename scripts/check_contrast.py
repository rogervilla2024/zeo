"""CLI to validate a site's effective palette against WCAG AA.

Usage:
    python check_contrast.py --config site.config.json

Resolves the site's effective light and dark palettes exactly like
generate_theme_css.py does (toolkit defaults < the variant's identity
< the site's explicit overrides) and checks the pairs that carry
text: text/background, muted/background, text/surface, and
on-primary/primary. Exits 1 on any violation - run it after every
palette tweak so a color change can never silently break reading
contrast.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import orjson

from seo_content_forge.contrast import palette_problems, resolved_palettes
from seo_content_forge.theme_css import from_config


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when both schemes hold AA."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("site.config.json"),
        help="Path to site.config.json (default: ./site.config.json).",
    )
    args = parser.parse_args(argv)

    try:
        config = orjson.loads(args.config.read_bytes())
    except (OSError, orjson.JSONDecodeError) as exc:
        print(f"Cannot read {args.config}: {exc}", file=sys.stderr)
        return 2

    tokens = from_config(config if isinstance(config, dict) else {})
    light, dark = resolved_palettes(tokens.variant)
    light = {**light, **tokens.palette}
    dark = {**dark, **tokens.palette, **tokens.dark_palette}

    problems = palette_problems(light, "light") + palette_problems(
        dark, "dark"
    )
    for problem in problems:
        print(f"CONTRAST {problem}")
    if problems:
        print(f"\n{len(problems)} contrast violation(s).")
        return 1
    print(f"Contrast OK: variant '{tokens.variant}', light and dark hold AA.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
