"""CLI to illustrate every imageless catalog entity on a site.

Usage:
    python generate_entity_images.py --root ~/sites/my-site --style building
    python generate_entity_images.py --root . --style product --force

Reads src/content/entities/*.md, draws a deterministic SVG card for
each entity that has no image yet (tinted from the site's palette,
seeded by the title so no two cards match), writes it to
public/img/entity-<slug>.svg, and sets the entity's ``image``
frontmatter to point at it. With --force existing images are
replaced too. Pairs with the launch checker's entity-image audit:
after this command no card ships text-only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import orjson

from seo_content_forge.article_images import parse_frontmatter
from seo_content_forge.illustrations import STYLES, entity_card_svg


def _primary_color(root: Path) -> str:
    config_path = root / "site.config.json"
    try:
        config = orjson.loads(config_path.read_bytes())
    except (OSError, orjson.JSONDecodeError):
        return "#0f766e"
    theme = config.get("theme") if isinstance(config, dict) else None
    palette = theme.get("palette") if isinstance(theme, dict) else None
    if isinstance(palette, dict) and palette.get("primary"):
        return str(palette["primary"])
    from seo_content_forge.theme_css import _identity

    variant = str(theme.get("variant", "minimal")) if isinstance(
        theme, dict
    ) else "minimal"
    id_palette, _, _, _ = _identity(variant)
    return id_palette.get("primary", "#0f766e")


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 on success, 2 on bad input."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Site project root (default: current directory).",
    )
    parser.add_argument(
        "--style",
        default="abstract",
        help=f"Drawing style: one of {', '.join(STYLES)}.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Redraw entities that already have an image.",
    )
    args = parser.parse_args(argv)

    if args.style not in STYLES:
        print(
            f"Unknown style {args.style!r}; choose from {', '.join(STYLES)}.",
            file=sys.stderr,
        )
        return 2
    entities_dir = args.root / "src" / "content" / "entities"
    entity_files = (
        sorted(entities_dir.glob("*.md")) if entities_dir.is_dir() else []
    )
    if not entity_files:
        print(f"No entities under {entities_dir}.", file=sys.stderr)
        return 2

    primary = _primary_color(args.root)
    img_dir = args.root / "public" / "img"
    img_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    for entity in entity_files:
        text = entity.read_text(encoding="utf-8")
        fields = parse_frontmatter(text)
        if fields.get("image") and not args.force:
            continue
        title = fields.get("title") or entity.stem
        target = img_dir / f"entity-{entity.stem}.svg"
        target.write_text(
            entity_card_svg(title, args.style, primary), encoding="utf-8"
        )
        image_path = f"/img/entity-{entity.stem}.svg"
        if re.search(r"^image:.*$", text, re.MULTILINE):
            text = re.sub(
                r"^image:.*$",
                f'image: "{image_path}"',
                text,
                count=1,
                flags=re.MULTILINE,
            )
        else:
            text = text.replace(
                "---\n", f'---\nimage: "{image_path}"\n', 1
            )
        entity.write_text(text, encoding="utf-8")
        written += 1
        print(f"DRAWN {entity.name} -> {image_path}")

    print(f"{written} entity image(s) written ({args.style} style).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
