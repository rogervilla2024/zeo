"""Self-hosted webfont pairings for the T recipes.

System font stacks read as "unstyled 90s page" next to modern sites;
real character needs real typefaces. This module turns the T recipes
(design-theme recipes.md) into shipped assets: download the open
(OFL) families from the Fontsource CDN once at design time, write
them into the site's public/fonts/, and emit src/styles/fonts.css
with @font-face rules (font-display: swap) plus the theme.fonts
values to paste into site.config.json. Zero runtime fetches: the
woff2 files deploy with the site.
"""

from __future__ import annotations

import urllib.request
from dataclasses import dataclass
from pathlib import Path

# Fontsource CDN layout: <base>/<family>@latest/latin-<weight>-normal.woff2
DEFAULT_BASE_URL = "https://cdn.jsdelivr.net/fontsource/fonts"


@dataclass(frozen=True, slots=True)
class FontSpec:
    """One family to fetch: slug on the CDN, CSS name, weights."""

    slug: str
    family: str
    weights: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class Pairing:
    """A T recipe: heading + body families and their fallbacks."""

    code: str
    name: str
    heading: FontSpec
    body: FontSpec
    heading_fallback: str
    body_fallback: str


PAIRINGS: dict[str, Pairing] = {
    "T1": Pairing(
        "T1", "Classic authority",
        FontSpec("playfair-display", "Playfair Display", (500, 700)),
        FontSpec("source-serif-4", "Source Serif 4", (400, 600)),
        "Georgia, serif", "Georgia, serif",
    ),
    "T2": Pairing(
        "T2", "Modern product",
        FontSpec("space-grotesk", "Space Grotesk", (500, 700)),
        FontSpec("inter", "Inter", (400, 600)),
        "system-ui, sans-serif", "system-ui, sans-serif",
    ),
    "T3": Pairing(
        "T3", "Terminal precision",
        FontSpec("jetbrains-mono", "JetBrains Mono", (500, 700)),
        FontSpec("inter", "Inter", (400, 600)),
        "ui-monospace, monospace", "system-ui, sans-serif",
    ),
    "T4": Pairing(
        "T4", "Humanist comfort",
        FontSpec("source-sans-3", "Source Sans 3", (600, 700)),
        FontSpec("charis-sil", "Charis SIL", (400, 700)),
        "system-ui, sans-serif", "Georgia, serif",
    ),
    "T5": Pairing(
        "T5", "Display punch",
        FontSpec("archivo-black", "Archivo Black", (400,)),
        FontSpec("archivo", "Archivo", (400, 600)),
        "system-ui, sans-serif", "system-ui, sans-serif",
    ),
}


def font_face_css(pairing: Pairing) -> str:
    """The fonts.css content for a pairing (paths under /fonts/)."""
    faces: list[str] = [
        "/* Self-hosted webfonts (fetch_fonts.py, Fontsource, OFL).",
        f"   Pairing {pairing.code} - {pairing.name}. Regenerate with:",
        f"   python fetch_fonts.py --pairing {pairing.code} --root . */",
    ]
    for spec in (pairing.heading, pairing.body):
        for weight in spec.weights:
            faces.append(
                "@font-face {\n"
                f'  font-family: "{spec.family}";\n'
                "  font-style: normal;\n"
                f"  font-weight: {weight};\n"
                "  font-display: swap;\n"
                f'  src: url("/fonts/{spec.slug}-{weight}.woff2")'
                ' format("woff2");\n'
                "}"
            )
    return "\n".join(faces) + "\n"


def config_fonts(pairing: Pairing) -> dict[str, str]:
    """The theme.fonts values a site should set for the pairing."""
    return {
        "heading": f'"{pairing.heading.family}", '
        f"{pairing.heading_fallback}",
        "body": f'"{pairing.body.family}", {pairing.body_fallback}',
    }


def fetch_pairing(
    pairing: Pairing, root: Path, base_url: str = DEFAULT_BASE_URL
) -> list[Path]:
    """Download a pairing's woff2 files and write fonts.css.

    Args:
        pairing: The T recipe to install.
        root: Site project root (holding public/ and src/).
        base_url: CDN base; override (e.g. file://...) for tests
            and mirrors.

    Returns:
        The written font file paths.
    """
    fonts_dir = root / "public" / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    seen: set[tuple[str, int]] = set()
    for spec in (pairing.heading, pairing.body):
        for weight in spec.weights:
            if (spec.slug, weight) in seen:
                continue
            seen.add((spec.slug, weight))
            url = f"{base_url}/{spec.slug}@latest/latin-{weight}-normal.woff2"
            target = fonts_dir / f"{spec.slug}-{weight}.woff2"
            with urllib.request.urlopen(url) as response:  # noqa: S310
                target.write_bytes(response.read())
            written.append(target)
    styles = root / "src" / "styles"
    styles.mkdir(parents=True, exist_ok=True)
    (styles / "fonts.css").write_text(font_face_css(pairing), encoding="utf-8")
    return written
