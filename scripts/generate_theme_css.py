"""CLI to generate the theme's tokens.css from site.config.json.

Usage:
    python generate_theme_css.py --config site.config.json --output tokens.css

Reads the ``theme`` section (palette, dark_palette, fonts, radius,
max_width; all optional with sensible defaults) and writes the token
stylesheet the theme components rely on.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import orjson

from seo_content_forge.theme_css import build_css, from_config


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns a process exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config", required=True, type=Path, help="site.config.json path."
    )
    parser.add_argument(
        "--output", type=Path, help="Write tokens.css here instead of stdout."
    )
    args = parser.parse_args(argv)

    css = build_css(from_config(orjson.loads(args.config.read_bytes())))
    if args.output:
        args.output.write_text(css, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        sys.stdout.write(css)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
