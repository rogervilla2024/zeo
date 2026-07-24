"""Render Open Graph share images (1200x630) for pages and articles.

Social platforms and chat apps render a link preview card from the
``og:image`` tag; pages without one get a bare text link and measurably
lower click-through. This module renders a clean, deterministic card -
background, accent bar, wrapped title, site name - so every generated
page can ship an image without a design tool in the loop.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

_FONT_PATHS: tuple[str, ...] = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
)


@dataclass(slots=True)
class OgImageSpec:
    """Parameters for one Open Graph image.

    Args:
        title: Page or article title (wrapped automatically).
        site_name: Brand line shown under the accent bar.
        width: Image width in pixels (1200 is the OG standard).
        height: Image height in pixels (630 is the OG standard).
        background: Background color, hex.
        accent: Accent bar and site-name color, hex.
        text_color: Title color, hex.
    """

    title: str
    site_name: str
    width: int = 1200
    height: int = 630
    background: str = "#101828"
    accent: str = "#38bdf8"
    text_color: str = "#ffffff"

    def __post_init__(self) -> None:
        if not self.title or not self.site_name:
            raise ValueError("title and site_name are required")


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a bold TrueType font, falling back to the PIL default."""
    for path in _FONT_PATHS:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _wrap(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    max_width: int,
) -> list[str]:
    """Greedily wrap ``text`` so each line fits within ``max_width``."""
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def render_og_image(spec: OgImageSpec) -> Image.Image:
    """Render the Open Graph image described by ``spec``.

    Args:
        spec: Image parameters.

    Returns:
        The rendered image, ready to be saved as PNG.
    """
    image = Image.new("RGB", (spec.width, spec.height), spec.background)
    draw = ImageDraw.Draw(image)

    margin = spec.width // 12
    title_font = _load_font(size=64)
    site_font = _load_font(size=32)

    draw.rectangle(
        (margin, margin, margin + spec.width // 10, margin + 10), fill=spec.accent
    )

    max_text_width = spec.width - 2 * margin
    lines = _wrap(draw, spec.title, title_font, max_text_width)[:5]
    y = margin + 60
    for line in lines:
        draw.text((margin, y), line, font=title_font, fill=spec.text_color)
        y += 80

    draw.text(
        (margin, spec.height - margin - 40),
        spec.site_name,
        font=site_font,
        fill=spec.accent,
    )
    return image
