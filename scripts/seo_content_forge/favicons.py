"""Generate the full favicon set and web app manifest from one logo.

Search results, browser tabs, bookmarks, and PWA installs each pull a
different icon size; shipping the complete set (plus a manifest) is a
small, one-time SEO and brand win that most sites get wrong. Given a
single square-ish source logo, this module renders every standard size
and the ``site.webmanifest`` that references the large ones.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import orjson
from PIL import Image

# Filename to pixel size, per the de-facto favicon standard set.
ICON_SIZES: dict[str, int] = {
    "favicon-16x16.png": 16,
    "favicon-32x32.png": 32,
    "apple-touch-icon.png": 180,
    "android-chrome-192x192.png": 192,
    "android-chrome-512x512.png": 512,
}

HEAD_SNIPPET: str = "\n".join(
    (
        '<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">',
        '<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">',
        '<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">',
        '<link rel="manifest" href="/site.webmanifest">',
    )
)


@dataclass(slots=True)
class ManifestSpec:
    """Web app manifest values.

    Args:
        name: Full site name.
        short_name: Short name for home-screen labels (12 chars ideal).
        theme_color: Browser UI theme color, hex.
        background_color: Splash background color, hex.
    """

    name: str
    short_name: str
    theme_color: str = "#101828"
    background_color: str = "#ffffff"

    def __post_init__(self) -> None:
        if not self.name or not self.short_name:
            raise ValueError("name and short_name are required")


def build_manifest(spec: ManifestSpec) -> dict[str, object]:
    """Build the ``site.webmanifest`` content for the generated icons."""
    return {
        "name": spec.name,
        "short_name": spec.short_name,
        "icons": [
            {
                "src": "/android-chrome-192x192.png",
                "sizes": "192x192",
                "type": "image/png",
            },
            {
                "src": "/android-chrome-512x512.png",
                "sizes": "512x512",
                "type": "image/png",
            },
        ],
        "theme_color": spec.theme_color,
        "background_color": spec.background_color,
        "display": "standalone",
    }


def generate_assets(logo: Image.Image, out_dir: Path, spec: ManifestSpec) -> list[str]:
    """Write the icon set and manifest into ``out_dir``.

    Args:
        logo: Source logo image; largest square version available.
        out_dir: Directory to write into (created if missing).
        spec: Manifest values.

    Returns:
        The list of filenames written, icons first then the manifest.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    square = logo.convert("RGBA")

    written: list[str] = []
    for filename, size in ICON_SIZES.items():
        resized = square.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(out_dir / filename, format="PNG")
        written.append(filename)

    manifest_path = out_dir / "site.webmanifest"
    manifest_path.write_bytes(
        orjson.dumps(build_manifest(spec), option=orjson.OPT_INDENT_2)
    )
    written.append("site.webmanifest")
    return written
