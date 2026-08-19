"""WCAG contrast math for palette validation.

A palette tweak that drops body text below AA is a silent
accessibility regression; this module makes it computable so the
test suite pins every shipped theme identity and check_contrast.py
validates a site's own overrides the same way.
"""

from __future__ import annotations

from seo_content_forge.theme_css import (
    _DEFAULT_DARK,
    _DEFAULT_PALETTE,
    VARIANT_IDENTITY,
)

# AA thresholds: body text 4.5:1; muted/meta text and UI accents ride
# the large-text/graphics line at 3:1 (they are never long-form copy).
TEXT_MIN = 4.5
MUTED_MIN = 3.0
ON_PRIMARY_MIN = 3.0


def _channel(value: float) -> float:
    value /= 255.0
    if value <= 0.04045:
        return value / 12.92
    return float(((value + 0.055) / 1.055) ** 2.4)


def relative_luminance(color: str) -> float:
    """WCAG relative luminance of a #rrggbb (or #rgb) hex color."""
    raw = color.strip().lstrip("#")
    if len(raw) == 3:
        raw = "".join(ch * 2 for ch in raw)
    if len(raw) != 6:
        raise ValueError(f"not a hex color: {color!r}")
    r, g, b = (int(raw[i : i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast_ratio(one: str, two: str) -> float:
    """WCAG contrast ratio between two hex colors (1.0 - 21.0)."""
    lighter, darker = sorted(
        (relative_luminance(one), relative_luminance(two)), reverse=True
    )
    return (lighter + 0.05) / (darker + 0.05)


def resolved_palettes(variant: str) -> tuple[dict[str, str], dict[str, str]]:
    """The variant's effective light and dark palettes.

    Args:
        variant: Variant name (identity merged over toolkit defaults).

    Returns:
        ``(light, dark)`` - the dark scheme inherits the light values
        for keys it does not override, mirroring build_css.
    """
    raw = VARIANT_IDENTITY.get(variant, {})
    id_palette = raw.get("palette")
    id_dark = raw.get("dark")
    light = {
        **_DEFAULT_PALETTE,
        **(id_palette if isinstance(id_palette, dict) else {}),
    }
    dark = {
        **light,
        **_DEFAULT_DARK,
        **(id_dark if isinstance(id_dark, dict) else {}),
    }
    return light, dark


def palette_problems(palette: dict[str, str], scheme: str) -> list[str]:
    """AA violations in one resolved palette.

    Args:
        palette: Complete palette (text/background/muted/primary/...).
        scheme: Label used in the messages ("light"/"dark").

    Returns:
        Human-readable violations; empty when the palette holds AA.
    """
    problems: list[str] = []
    background = palette["background"]

    def check(name: str, fg: str, bg: str, minimum: float) -> None:
        ratio = contrast_ratio(fg, bg)
        if ratio < minimum:
            problems.append(
                f"{scheme}: {name} {ratio:.2f}:1 < {minimum}:1 "
                f"({fg} on {bg})"
            )

    check("text/background", palette["text"], background, TEXT_MIN)
    check("muted/background", palette["muted"], background, MUTED_MIN)
    check("text/surface", palette["text"], palette["surface"], TEXT_MIN)
    on_primary = palette.get("on-primary", "#ffffff")
    check("on-primary/primary", on_primary, palette["primary"], ON_PRIMARY_MIN)
    return problems
