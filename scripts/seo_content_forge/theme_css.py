"""Generate the theme's tokens.css from the site config.

Every site built with this toolkit shares one skeleton but must not
share one look: colors, fonts, radius, and layout width come from the
``theme`` section of site.config.json and are emitted as CSS custom
properties. The stylesheet also bakes in the non-negotiables - dark
mode via ``prefers-color-scheme`` with a ``data-theme`` override,
visible focus rings, a skip link, and zero-shift media defaults - so
accessibility and stability ship with the tokens.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

VARIANTS: tuple[str, ...] = ("minimal", "editorial", "guide", "review")
_VARIANT_DIR = (
    Path(__file__).resolve().parents[2] / "templates" / "theme" / "variants"
)

_DEFAULT_PALETTE: dict[str, str] = {
    "primary": "#0f766e",
    "accent": "#f59e0b",
    "background": "#ffffff",
    "surface": "#f6f8fa",
    "text": "#111827",
    "muted": "#6b7280",
    # Text placed on primary-colored surfaces (buttons). The page
    # background is not guaranteed to contrast with primary, and in
    # dark mode it usually does not.
    "on-primary": "#ffffff",
}
_DEFAULT_FONT: str = "system-ui, -apple-system, sans-serif"
_DEFAULT_RADIUS: str = "8px"
_DEFAULT_MAX_WIDTH: str = "72ch"
_DEFAULT_SITE_WIDTH: str = "1200px"

_DEFAULT_DARK: dict[str, str] = {
    "background": "#0b1220",
    "surface": "#131c2e",
    "text": "#e5e7eb",
    "muted": "#9ca3af",
}


@dataclass(slots=True)
class ThemeTokens:
    """Design tokens for one site.

    Args:
        palette: Light-mode colors; missing keys fall back to defaults.
        dark_palette: Dark-mode overrides (background/surface/text/muted;
            primary and accent are shared unless overridden).
        heading_font: CSS font stack for headings.
        body_font: CSS font stack for body text.
        radius: Corner radius, e.g. ``8px``.
        max_width: Prose measure, e.g. ``72ch`` (article text only).
        site_width: Page shell width, e.g. ``1200px`` (header, grids).
        variant: Layout variant whose shipped stylesheet is appended
            (``minimal``, ``editorial``, ``guide``, or ``review``).
    """

    palette: dict[str, str] = field(default_factory=dict)
    dark_palette: dict[str, str] = field(default_factory=dict)
    heading_font: str = _DEFAULT_FONT
    body_font: str = _DEFAULT_FONT
    radius: str = _DEFAULT_RADIUS
    max_width: str = _DEFAULT_MAX_WIDTH
    site_width: str = _DEFAULT_SITE_WIDTH
    variant: str = "minimal"


def from_config(config: dict[str, object]) -> ThemeTokens:
    """Build :class:`ThemeTokens` from a parsed site.config.json."""
    theme = config.get("theme")
    theme = theme if isinstance(theme, dict) else {}
    fonts = theme.get("fonts")
    fonts = fonts if isinstance(fonts, dict) else {}
    palette = theme.get("palette")
    dark = theme.get("dark_palette")
    raw_variant = str(theme.get("variant", "minimal")).lower()
    return ThemeTokens(
        palette=dict(palette) if isinstance(palette, dict) else {},
        dark_palette=dict(dark) if isinstance(dark, dict) else {},
        heading_font=str(fonts.get("heading", _DEFAULT_FONT)),
        body_font=str(fonts.get("body", _DEFAULT_FONT)),
        radius=str(theme.get("radius", _DEFAULT_RADIUS)),
        max_width=str(theme.get("max_width", _DEFAULT_MAX_WIDTH)),
        site_width=str(theme.get("site_width", _DEFAULT_SITE_WIDTH)),
        variant=raw_variant if raw_variant in VARIANTS else "minimal",
    )


def variant_css(variant: str) -> str:
    """The shipped stylesheet for a layout variant.

    Args:
        variant: One of :data:`VARIANTS`.

    Returns:
        The variant stylesheet content.

    Raises:
        ValueError: If the variant has no shipped stylesheet.
    """
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant {variant!r}; choose from {VARIANTS}")
    return (_VARIANT_DIR / f"{variant}.css").read_text(encoding="utf-8")


def compose_css(tokens: ThemeTokens) -> str:
    """Tokens plus the variant layer: the site's complete stylesheet.

    The design baseline ships with the toolkit so no site can render
    as an unstyled skeleton; the per-site design pass (design-theme
    skill) layers niche-specific overrides on top of this output.

    Args:
        tokens: The site's design tokens (including the variant).

    Returns:
        The full tokens.css content.
    """
    return build_css(tokens) + "\n" + variant_css(tokens.variant)


def _vars(colors: dict[str, str]) -> str:
    return "\n".join(f"  --color-{name}: {value};" for name, value in colors.items())


def build_css(tokens: ThemeTokens) -> str:
    """Render the complete tokens.css content.

    Args:
        tokens: The site's design tokens.

    Returns:
        A stylesheet with custom properties, dark mode, and the baked-in
        accessibility and stability rules.
    """
    light = {**_DEFAULT_PALETTE, **tokens.palette}
    dark = {**_DEFAULT_DARK, **tokens.dark_palette}

    return f""":root {{
{_vars(light)}
  --font-heading: {tokens.heading_font};
  --font-body: {tokens.body_font};
  --radius: {tokens.radius};
  --max-width: {tokens.max_width};
  --width-site: {tokens.site_width};
}}

@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
{_vars(dark)}
  }}
}}
:root[data-theme="dark"] {{
{_vars(dark)}
}}

body {{
  margin: 0;
  font-family: var(--font-body);
  color: var(--color-text);
  background: var(--color-background);
  line-height: 1.6;
}}
h1, h2, h3, h4 {{
  font-family: var(--font-heading);
  line-height: 1.25;
}}
a {{
  color: var(--color-primary);
}}
img, video {{
  max-width: 100%;
  height: auto;
}}

:focus-visible {{
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}}
.skip-link {{
  position: absolute;
  left: -9999px;
  top: 0;
  background: var(--color-surface);
  padding: 0.5rem 1rem;
  border-radius: var(--radius);
}}
.skip-link:focus {{
  left: 0.5rem;
  top: 0.5rem;
  z-index: 100;
}}
.container {{
  max-width: var(--width-site);
  margin-inline: auto;
  padding-inline: 1rem;
}}
.prose {{
  max-width: var(--max-width);
  margin-inline: auto;
}}
"""
