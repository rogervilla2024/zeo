"""Deterministic SVG illustrations for entities and hero covers.

"No images existed" is never a reason a card ships text-only: this
module draws original, topic-aware SVG illustrations from nothing
but the entity's title and a style word. Every drawing is
deterministic (seeded by the title), sized 800x450, self-contained,
and tinted from the site's own palette - so a whole catalog gets
consistent, license-free art in one command
(generate_entity_images.py), and the cover generator
(generate_cover_image.py) fills the A7 "cover" hero the same way.
"""

from __future__ import annotations

import colorsys
import hashlib
import html

STYLES: tuple[str, ...] = (
    "building",  # hotels, venues, places
    "product",   # tools, apps, boxed goods
    "nature",    # plants, food, outdoors
    "abstract",  # everything else: geometric identity art
)

_W, _H = 800, 450


def _seed(title: str) -> int:
    return int(hashlib.sha256(title.encode("utf-8")).hexdigest()[:8], 16)


def _hex_to_hls(color: str) -> tuple[float, float, float]:
    raw = color.strip().lstrip("#")
    if len(raw) == 3:
        raw = "".join(ch * 2 for ch in raw)
    r, g, b = (int(raw[i : i + 2], 16) / 255 for i in (0, 2, 4))
    return colorsys.rgb_to_hls(r, g, b)


def _hls_to_hex(h: float, lightness: float, s: float) -> str:
    r, g, b = colorsys.hls_to_rgb(h % 1.0, min(max(lightness, 0), 1), s)
    return "#" + "".join(f"{round(v * 255):02x}" for v in (r, g, b))


def _tints(primary: str, seed: int) -> tuple[str, str, str, str]:
    """Background, ground, shape, and highlight tints for a drawing.

    Derived from the palette primary with a per-title hue nudge, so a
    catalog reads as one family while no two cards are identical.
    """
    h, lightness, s = _hex_to_hls(primary)
    nudge = ((seed % 13) - 6) / 90.0
    h = (h + nudge) % 1.0
    s = min(max(s, 0.25), 0.7)
    return (
        _hls_to_hex(h, 0.14, s * 0.6),
        _hls_to_hex(h, 0.22, s * 0.5),
        _hls_to_hex(h, 0.45, s),
        _hls_to_hex((h + 0.08) % 1.0, 0.68, s),
    )


def _building(seed: int, shape: str, glow: str) -> str:
    blocks = []
    x = 90
    for i in range(4):
        w = 100 + ((seed >> (i * 3)) % 5) * 18
        hgt = 130 + ((seed >> (i * 4)) % 7) * 22
        blocks.append(
            f'<rect x="{x}" y="{360 - hgt}" width="{w}" height="{hgt}" '
            f'rx="6" fill="{shape}" opacity="{0.55 + (i % 3) * 0.15:.2f}"/>'
        )
        wy = 360 - hgt + 18
        while wy < 330:
            blocks.append(
                f'<rect x="{x + 14}" y="{wy}" width="{w - 28}" height="8" '
                f'rx="2" fill="{glow}" opacity="0.5"/>'
            )
            wy += 26
        x += w + 26
    return "".join(blocks) + (
        f'<circle cx="680" cy="90" r="38" fill="{glow}" opacity="0.9"/>'
    )


def _product(seed: int, shape: str, glow: str) -> str:
    tilt = (seed % 9) - 4
    return (
        f'<g transform="rotate({tilt} 400 240)">'
        f'<rect x="270" y="120" width="260" height="240" rx="18" '
        f'fill="{shape}"/>'
        f'<rect x="270" y="120" width="260" height="70" rx="18" '
        f'fill="{glow}" opacity="0.85"/>'
        f'<circle cx="400" cy="265" r="52" fill="{glow}" opacity="0.55"/>'
        f'<rect x="310" y="330" width="180" height="12" rx="6" '
        f'fill="{glow}" opacity="0.6"/>'
        "</g>"
        f'<circle cx="150" cy="120" r="26" fill="{shape}" opacity="0.5"/>'
        f'<circle cx="660" cy="330" r="34" fill="{shape}" opacity="0.4"/>'
    )


def _nature(seed: int, shape: str, glow: str) -> str:
    leaves = []
    for i in range(5):
        cx = 160 + i * 120 + (seed >> i) % 30
        cy = 250 - ((seed >> (i * 2)) % 6) * 18
        r = 46 + ((seed >> (i * 3)) % 4) * 12
        leaves.append(
            f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{int(r * 1.5)}" '
            f'fill="{shape}" opacity="{0.4 + (i % 3) * 0.2:.2f}" '
            f'transform="rotate({(i - 2) * 16} {cx} {cy})"/>'
        )
    return "".join(leaves) + (
        f'<circle cx="120" cy="100" r="34" fill="{glow}" opacity="0.85"/>'
        f'<path d="M60 380 Q 400 320 740 380" stroke="{glow}" '
        'stroke-width="5" fill="none" opacity="0.6"/>'
    )


def _abstract(seed: int, shape: str, glow: str) -> str:
    parts = []
    for i in range(6):
        x = 90 + ((seed >> (i * 2)) % 10) * 62
        y = 90 + ((seed >> (i * 3)) % 8) * 34
        size = 40 + ((seed >> i) % 5) * 22
        if (seed >> i) % 3 == 0:
            parts.append(
                f'<circle cx="{x}" cy="{y}" r="{size // 2}" '
                f'fill="{shape}" opacity="0.55"/>'
            )
        elif (seed >> i) % 3 == 1:
            parts.append(
                f'<rect x="{x}" y="{y}" width="{size}" height="{size}" '
                f'rx="10" fill="{glow}" opacity="0.5" '
                f'transform="rotate({(i * 17 + seed) % 40 - 20} {x} {y})"/>'
            )
        else:
            parts.append(
                f'<polygon points="{x},{y + size} {x + size // 2},{y} '
                f'{x + size},{y + size}" fill="{shape}" opacity="0.6"/>'
            )
    return "".join(parts) + (
        f'<circle cx="400" cy="240" r="110" fill="none" '
        f'stroke="{glow}" stroke-width="4" opacity="0.7"/>'
    )


_DRAWERS = {
    "building": _building,
    "product": _product,
    "nature": _nature,
    "abstract": _abstract,
}


def _caption_font(title: str) -> int:
    """Caption size that survives a portrait crop.

    List views crop the 800x450 card to roughly its central 40%, so
    the caption must fit that window; long titles shrink, short ones
    keep the full 30px.
    """
    fit = int(_W * 0.4 / (0.58 * max(len(title), 1)))
    return max(16, min(30, fit))


def entity_card_svg(title: str, style: str, primary: str) -> str:
    """One entity's illustrated card (800x450 SVG).

    Args:
        title: Entity title; seeds the per-card variation and is
            drawn as the caption.
        style: One of :data:`STYLES`.
        primary: The site's primary color; tints the whole drawing.

    Returns:
        A self-contained SVG document string.

    Raises:
        ValueError: If the style is unknown.
    """
    if style not in _DRAWERS:
        raise ValueError(f"unknown style {style!r}; choose from {STYLES}")
    seed = _seed(title)
    bg, ground, shape, glow = _tints(primary, seed)
    art = _DRAWERS[style](seed, shape, glow)
    caption = html.escape(title)
    head = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {_W} {_H}" width="{_W}" height="{_H}">'
    )
    label = (
        f'<text x="{_W // 2}" y="418" text-anchor="middle" '
        f'font-family="Arial, sans-serif" font-size="{_caption_font(title)}" '
        f'font-weight="bold" fill="#f8fafc">{caption}</text>'
    )
    return f"""{head}
<rect width="{_W}" height="{_H}" fill="{bg}"/>
<ellipse cx="400" cy="470" rx="520" ry="180" fill="{ground}"/>
{art}
{label}
</svg>
"""


def cover_svg(
    title: str,
    tagline: str,
    style: str,
    primary: str,
    width: int = 1600,
    height: int = 900,
    draw_text: bool = True,
) -> str:
    """A wide hero cover for the A7 "cover" anatomy.

    Args:
        title: Site or page title; always seeds the art, drawn large
            only when draw_text is True.
        tagline: One supporting line (empty skips it).
        style: One of :data:`STYLES` for the backdrop art.
        primary: The site's primary color.
        width: Output width (default 1600).
        height: Output height (default 900).
        draw_text: Bake title/tagline into the image. The A7 hero
            overlays its own h1 and tagline on the cover, so hero
            backgrounds want False; standalone/social images want
            True.

    Returns:
        A self-contained SVG document string.
    """
    if style not in _DRAWERS:
        raise ValueError(f"unknown style {style!r}; choose from {STYLES}")
    seed = _seed(title)
    bg, ground, shape, glow = _tints(primary, seed)
    art = _DRAWERS[style](seed, shape, glow)
    caption = html.escape(title)
    sub = (
        f'<text x="70" y="{height - 90}" font-family="Arial, sans-serif" '
        f'font-size="34" fill="#e2e8f0" opacity="0.85">'
        f"{html.escape(tagline)}</text>"
        if tagline and draw_text
        else ""
    )
    head = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}">'
    )
    title_text = (
        f'<text x="70" y="{height - 150}" '
        'font-family="Arial, sans-serif" font-size="72" '
        f'font-weight="bold" fill="#f8fafc">{caption}</text>'
        if draw_text
        else ""
    )
    return f"""{head}
<rect width="{width}" height="{height}" fill="{bg}"/>
<g transform="scale({width / _W} {height / _H})">
<ellipse cx="400" cy="470" rx="520" ry="180" fill="{ground}"/>
{art}
</g>
<rect y="{height - 300}" width="{width}" height="300" fill="url(#scrim)"/>
<defs><linearGradient id="scrim" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="{bg}" stop-opacity="0"/>
<stop offset="1" stop-color="#07090c" stop-opacity="0.9"/>
</linearGradient></defs>
{title_text}
{sub}
</svg>
"""
