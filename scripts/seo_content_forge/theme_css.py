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

# Forty aesthetic baselines. Each variants/<name>.css is the
# CHARACTER layer only (type stance, header, hero, cards, footer);
# the functional surfaces every variant shares (archetype blocks,
# directory-pro, forum, pagination, block styles) live once in
# templates/theme/components.css and are composed in between the
# token base and the variant layer.
VARIANTS: tuple[str, ...] = (
    "minimal", "editorial", "guide", "review",
    "magazine", "news", "docs", "landing",
    "luxe", "noir", "pastel", "brutal",
    "terminal", "paper", "atlas", "folio",
    "gazette", "studio", "arcade", "botanic",
    "marine", "alpine", "ember", "velvet",
    "chrome", "retro", "zen", "bazaar",
    "ledger", "clinic", "atelier", "orbit",
    "prairie", "cinema", "forge", "harbor",
    "bloom", "mosaic", "quartz", "tundra",
)
_THEME_DIR = Path(__file__).resolve().parents[2] / "templates" / "theme"
_VARIANT_DIR = _THEME_DIR / "variants"

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

# System-safe font stacks with genuinely different character; the T
# recipes upgrade these to self-hosted woff2 pairings per site.
_F_SYSTEM = "system-ui, -apple-system, sans-serif"
_F_SERIF = "Georgia, 'Times New Roman', serif"
_F_PALATINO = "'Palatino Linotype', Palatino, Georgia, serif"
_F_MONO = "ui-monospace, 'Cascadia Code', Menlo, Consolas, monospace"
_F_HUMANIST = "Seravek, 'Gill Sans Nova', Ubuntu, Calibri, sans-serif"
_F_GEOMETRIC = "Avenir, Montserrat, Corbel, 'URW Gothic', sans-serif"
_F_ROUNDED = "ui-rounded, 'Hiragino Maru Gothic ProN', Quicksand, sans-serif"

# Every variant IS a full theme: its own palette (light AND dark),
# font pairing, and corner language. site.config.json overrides only
# the keys a site explicitly sets - an empty theme.palette means
# "the variant's identity", which is why forty variants look like
# forty different sites before any per-site design pass. Values are
# picked as text/background pairs that hold WCAG AA for body text.
# fonts = (heading, body); dark-native themes carry a dark "light"
# scheme on purpose - that IS their identity.
VARIANT_IDENTITY: dict[str, dict[str, object]] = {
    "minimal": {},  # the classic defaults; continuity for old sites
    "editorial": {
        "palette": {"primary": "#9f1239", "accent": "#0f766e",
                    "background": "#fffdf8", "surface": "#f7f2e9",
                    "text": "#1c1917", "muted": "#78716c"},
        "dark": {"background": "#1c1917", "surface": "#292524"},
        "fonts": (_F_SERIF, _F_SYSTEM), "radius": "2px",
    },
    "guide": {
        "palette": {"primary": "#1d4ed8", "accent": "#f59e0b",
                    "background": "#ffffff", "surface": "#eef2ff",
                    "text": "#111827", "muted": "#6b7280"},
        "fonts": (_F_HUMANIST, _F_SYSTEM), "radius": "6px",
    },
    "review": {
        "palette": {"primary": "#b45309", "accent": "#1d4ed8",
                    "background": "#fffbf5", "surface": "#fef3e2",
                    "text": "#292524", "muted": "#7c6f64"},
        "fonts": (_F_GEOMETRIC, _F_SYSTEM), "radius": "10px",
    },
    "magazine": {
        "palette": {"primary": "#dc2626", "accent": "#111827",
                    "background": "#ffffff", "surface": "#f3f4f6",
                    "text": "#111827", "muted": "#6b7280"},
        "fonts": (_F_SERIF, _F_HUMANIST), "radius": "0px",
    },
    "news": {
        "palette": {"primary": "#0c4a6e", "accent": "#b91c1c",
                    "background": "#fbfbfa", "surface": "#f1f0ee",
                    "text": "#18181b", "muted": "#52525b"},
        "fonts": (_F_SYSTEM, _F_SYSTEM), "radius": "0px",
    },
    "docs": {
        "palette": {"primary": "#7c3aed", "accent": "#059669",
                    "background": "#ffffff", "surface": "#f5f3ff",
                    "text": "#1e1b4b", "muted": "#64748b"},
        "fonts": (_F_SYSTEM, _F_SYSTEM), "radius": "6px",
    },
    "landing": {
        "palette": {"primary": "#4f46e5", "accent": "#f43f5e",
                    "background": "#fafaff", "surface": "#eef2ff",
                    "text": "#111827", "muted": "#6b7280"},
        "fonts": (_F_GEOMETRIC, _F_GEOMETRIC), "radius": "14px",
    },
    "luxe": {
        "palette": {"primary": "#92702a", "accent": "#1c1917",
                    "background": "#faf8f4", "surface": "#f1ece2",
                    "text": "#1c1917", "muted": "#8a7d6a"},
        "dark": {"background": "#171412", "surface": "#211d19",
                 "primary": "#c8a959"},
        "fonts": (_F_PALATINO, _F_HUMANIST), "radius": "0px",
    },
    "noir": {
        "palette": {"primary": "#f43f5e", "accent": "#fbbf24",
                    "background": "#101014", "surface": "#1a1a21",
                    "text": "#f4f4f5", "muted": "#a1a1aa",
                    "on-primary": "#101014"},
        "dark": {"background": "#0a0a0d", "surface": "#141419"},
        "fonts": (_F_SYSTEM, _F_SYSTEM), "radius": "2px",
    },
    "pastel": {
        "palette": {"primary": "#db2777", "accent": "#7c3aed",
                    "background": "#fdf7fb", "surface": "#fce7f3",
                    "text": "#3b0764", "muted": "#86718f"},
        "fonts": (_F_ROUNDED, _F_HUMANIST), "radius": "18px",
    },
    "brutal": {
        "palette": {"primary": "#facc15", "accent": "#dc2626",
                    "background": "#f5f5f4", "surface": "#e7e5e4",
                    "text": "#0c0a09", "muted": "#44403c",
                    "on-primary": "#0c0a09"},
        "fonts": (_F_SYSTEM, _F_MONO), "radius": "0px",
    },
    "terminal": {
        "palette": {"primary": "#15803d", "accent": "#b45309",
                    "background": "#fafdf7", "surface": "#ecf4e7",
                    "text": "#14201a", "muted": "#5b6b60"},
        "dark": {"background": "#0a120d", "surface": "#111a14",
                 "primary": "#4ade80", "text": "#d1fae5",
                 "muted": "#6ee7b7"},
        "fonts": (_F_MONO, _F_MONO), "radius": "2px",
    },
    "paper": {
        "palette": {"primary": "#8a3324", "accent": "#3f6212",
                    "background": "#f8f4ea", "surface": "#efe8d8",
                    "text": "#2c2417", "muted": "#7d715c"},
        "dark": {"background": "#201b12", "surface": "#2a2418"},
        "fonts": (_F_PALATINO, _F_PALATINO), "radius": "4px",
    },
    "atlas": {
        "palette": {"primary": "#0e7490", "accent": "#ca8a04",
                    "background": "#f8fafc", "surface": "#e2e8f0",
                    "text": "#0f172a", "muted": "#64748b"},
        "fonts": (_F_HUMANIST, _F_SYSTEM), "radius": "4px",
    },
    "folio": {
        "palette": {"primary": "#1e293b", "accent": "#b45309",
                    "background": "#ffffff", "surface": "#f8fafc",
                    "text": "#1e293b", "muted": "#94a3b8"},
        "fonts": (_F_SERIF, _F_SERIF), "radius": "0px",
    },
    "gazette": {
        "palette": {"primary": "#171717", "accent": "#b91c1c",
                    "background": "#fcfaf6", "surface": "#f2efe8",
                    "text": "#171717", "muted": "#525252"},
        "fonts": (_F_SERIF, _F_SYSTEM), "radius": "0px",
    },
    "studio": {
        "palette": {"primary": "#ea580c", "accent": "#0f172a",
                    "background": "#ffffff", "surface": "#fafaf9",
                    "text": "#0f172a", "muted": "#78716c"},
        "fonts": (_F_GEOMETRIC, _F_HUMANIST), "radius": "6px",
    },
    "arcade": {
        "palette": {"primary": "#7c3aed", "accent": "#fbbf24",
                    "background": "#fefce8", "surface": "#fef9c3",
                    "text": "#1e1b4b", "muted": "#6d28d9"},
        "fonts": (_F_ROUNDED, _F_SYSTEM), "radius": "12px",
    },
    "botanic": {
        "palette": {"primary": "#166534", "accent": "#a16207",
                    "background": "#f7faf5", "surface": "#e8f2e3",
                    "text": "#1a2e1f", "muted": "#5f7364"},
        "dark": {"background": "#111a13", "surface": "#18241a"},
        "fonts": (_F_HUMANIST, _F_HUMANIST), "radius": "16px",
    },
    "marine": {
        "palette": {"primary": "#0369a1", "accent": "#0d9488",
                    "background": "#f6fbfd", "surface": "#e0f2fe",
                    "text": "#082f49", "muted": "#5a7d91"},
        "fonts": (_F_HUMANIST, _F_SYSTEM), "radius": "8px",
    },
    "alpine": {
        "palette": {"primary": "#334155", "accent": "#0ea5e9",
                    "background": "#fbfdfe", "surface": "#eef4f8",
                    "text": "#1e293b", "muted": "#7d94a5"},
        "fonts": (_F_SYSTEM, _F_SYSTEM), "radius": "2px",
    },
    "ember": {
        "palette": {"primary": "#c2410c", "accent": "#facc15",
                    "background": "#fffaf5", "surface": "#ffedd5",
                    "text": "#3d1d09", "muted": "#9a6b4f"},
        "dark": {"background": "#1c1108", "surface": "#28190d"},
        "fonts": (_F_GEOMETRIC, _F_SYSTEM), "radius": "8px",
    },
    "velvet": {
        "palette": {"primary": "#c084fc", "accent": "#f0abfc",
                    "background": "#1e1030", "surface": "#2a1a40",
                    "text": "#f3e8ff", "muted": "#b39ddb",
                    "on-primary": "#1e1030"},
        "dark": {"background": "#150a24", "surface": "#1f1233"},
        "fonts": (_F_PALATINO, _F_HUMANIST), "radius": "10px",
    },
    "chrome": {
        "palette": {"primary": "#2563eb", "accent": "#64748b",
                    "background": "#f8fafc", "surface": "#eef2f6",
                    "text": "#0f172a", "muted": "#64748b"},
        "fonts": (_F_SYSTEM, _F_SYSTEM), "radius": "10px",
    },
    "retro": {
        "palette": {"primary": "#b45309", "accent": "#65a30d",
                    "background": "#fdf6e3", "surface": "#f5e9c9",
                    "text": "#433519", "muted": "#8c7851"},
        "fonts": (_F_GEOMETRIC, _F_HUMANIST), "radius": "8px",
    },
    "zen": {
        "palette": {"primary": "#57534e", "accent": "#a8a29e",
                    "background": "#fafaf9", "surface": "#f5f5f4",
                    "text": "#292524", "muted": "#a8a29e"},
        "fonts": (_F_SERIF, _F_HUMANIST), "radius": "0px",
    },
    "bazaar": {
        "palette": {"primary": "#be123c", "accent": "#d97706",
                    "background": "#fffbf7", "surface": "#ffe4e6",
                    "text": "#3f1d2b", "muted": "#9f6b7a"},
        "fonts": (_F_SYSTEM, _F_SYSTEM), "radius": "6px",
    },
    "ledger": {
        "palette": {"primary": "#065f46", "accent": "#b45309",
                    "background": "#fbfdfc", "surface": "#ecf5f0",
                    "text": "#0f2921", "muted": "#5f7a6e"},
        "fonts": (_F_SYSTEM, _F_MONO), "radius": "2px",
    },
    "clinic": {
        "palette": {"primary": "#0284c7", "accent": "#059669",
                    "background": "#fcfeff", "surface": "#e8f4fb",
                    "text": "#0c2e42", "muted": "#64879b"},
        "fonts": (_F_SYSTEM, _F_SYSTEM), "radius": "6px",
    },
    "atelier": {
        "palette": {"primary": "#9a3412", "accent": "#4d7c0f",
                    "background": "#faf6f1", "surface": "#f0e7db",
                    "text": "#33251b", "muted": "#84756a"},
        "fonts": (_F_PALATINO, _F_HUMANIST), "radius": "10px",
    },
    "orbit": {
        "palette": {"primary": "#22d3ee", "accent": "#a78bfa",
                    "background": "#0b1026", "surface": "#151b36",
                    "text": "#e2e8f0", "muted": "#8b9bb8",
                    "on-primary": "#0b1026"},
        "dark": {"background": "#070b1c", "surface": "#10152b"},
        "fonts": (_F_GEOMETRIC, _F_SYSTEM), "radius": "8px",
    },
    "prairie": {
        "palette": {"primary": "#78350f", "accent": "#4d7c0f",
                    "background": "#fdfaf3", "surface": "#f5eeda",
                    "text": "#332512", "muted": "#8a7a5c"},
        "fonts": (_F_SERIF, _F_HUMANIST), "radius": "6px",
    },
    "cinema": {
        "palette": {"primary": "#e11d48", "accent": "#fbbf24",
                    "background": "#18181b", "surface": "#232327",
                    "text": "#fafafa", "muted": "#a1a1aa"},
        "dark": {"background": "#101012", "surface": "#1b1b1f"},
        "fonts": (_F_GEOMETRIC, _F_SYSTEM), "radius": "4px",
    },
    "forge": {
        "palette": {"primary": "#ea580c", "accent": "#71717a",
                    "background": "#f4f4f5", "surface": "#e4e4e7",
                    "text": "#18181b", "muted": "#52525b"},
        "dark": {"background": "#151517", "surface": "#1f1f23"},
        "fonts": (_F_SYSTEM, _F_SYSTEM), "radius": "0px",
    },
    "harbor": {
        "palette": {"primary": "#1e40af", "accent": "#b45309",
                    "background": "#f9fbfd", "surface": "#e7eef7",
                    "text": "#172554", "muted": "#64748b"},
        "fonts": (_F_HUMANIST, _F_SYSTEM), "radius": "8px",
    },
    "bloom": {
        "palette": {"primary": "#c026d3", "accent": "#65a30d",
                    "background": "#fefcff", "surface": "#fae8ff",
                    "text": "#4a044e", "muted": "#a67cab"},
        "fonts": (_F_ROUNDED, _F_HUMANIST), "radius": "16px",
    },
    "mosaic": {
        "palette": {"primary": "#0f766e", "accent": "#c2410c",
                    "background": "#fafaf9", "surface": "#e7e5e4",
                    "text": "#1c1917", "muted": "#57534e"},
        "fonts": (_F_SYSTEM, _F_SYSTEM), "radius": "4px",
    },
    "quartz": {
        "palette": {"primary": "#6d28d9", "accent": "#0891b2",
                    "background": "#fdfcff", "surface": "#ede9fe",
                    "text": "#2e1065", "muted": "#7c7493"},
        "fonts": (_F_GEOMETRIC, _F_SYSTEM), "radius": "6px",
    },
    "tundra": {
        "palette": {"primary": "#475569", "accent": "#94a3b8",
                    "background": "#f8fafc", "surface": "#f1f5f9",
                    "text": "#334155", "muted": "#94a3b8"},
        "dark": {"background": "#0f1720", "surface": "#16202b"},
        "fonts": (_F_SYSTEM, _F_HUMANIST), "radius": "2px",
    },
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
    # Empty string / empty dict = "the variant's identity decides".
    heading_font: str = ""
    body_font: str = ""
    radius: str = ""
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
        heading_font=str(fonts.get("heading", "")),
        body_font=str(fonts.get("body", "")),
        radius=str(theme.get("radius", "")),
        max_width=str(theme.get("max_width", _DEFAULT_MAX_WIDTH)),
        site_width=str(theme.get("site_width", _DEFAULT_SITE_WIDTH)),
        variant=raw_variant if raw_variant in VARIANTS else "minimal",
    )


def _identity(
    variant: str,
) -> tuple[dict[str, str], dict[str, str], tuple[str, str], str]:
    """The variant's own palette/dark/fonts/radius identity."""
    raw = VARIANT_IDENTITY.get(variant, {})
    palette = raw.get("palette")
    dark = raw.get("dark")
    fonts = raw.get("fonts")
    radius = raw.get("radius")
    return (
        dict(palette) if isinstance(palette, dict) else {},
        dict(dark) if isinstance(dark, dict) else {},
        (str(fonts[0]), str(fonts[1]))
        if isinstance(fonts, tuple) and len(fonts) == 2
        else (_DEFAULT_FONT, _DEFAULT_FONT),
        str(radius) if isinstance(radius, str) and radius else _DEFAULT_RADIUS,
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


def components_css() -> str:
    """The shared functional layer every variant inherits.

    Archetype blocks, directory-pro, forum, pagination, and block
    styles are identical across variants - they live once here so a
    new feature is styled once, not forty times.

    Returns:
        The components stylesheet content.
    """
    return (_THEME_DIR / "components.css").read_text(encoding="utf-8")


def compose_css(tokens: ThemeTokens) -> str:
    """Tokens + shared components + the variant layer: the complete
    stylesheet.

    The design baseline ships with the toolkit so no site can render
    as an unstyled skeleton; the per-site design pass (design-theme
    skill) layers niche-specific overrides on top of this output.

    Args:
        tokens: The site's design tokens (including the variant).

    Returns:
        The full tokens.css content.
    """
    return (
        build_css(tokens)
        + "\n"
        + components_css()
        + "\n"
        + variant_css(tokens.variant)
    )


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
    # Identity resolution: toolkit defaults < the variant's own
    # identity < whatever the site explicitly set in its config.
    id_palette, id_dark, id_fonts, id_radius = _identity(tokens.variant)
    light = {**_DEFAULT_PALETTE, **id_palette, **tokens.palette}
    dark = {**_DEFAULT_DARK, **id_dark, **tokens.dark_palette}
    heading_font = tokens.heading_font or id_fonts[0]
    body_font = tokens.body_font or id_fonts[1]
    radius = tokens.radius or id_radius

    return f""":root {{
{_vars(light)}
  --font-heading: {heading_font};
  --font-body: {body_font};
  --radius: {radius};
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

html {{
  background: var(--color-background);
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
/* Two-column composition: content plus .site-aside. Add .left to put
   the aside before the content. Collapses on narrow viewports. */
.with-aside {{
  display: grid;
  gap: 2.5rem;
  align-items: start;
}}
@media (min-width: 1024px) {{
  .with-aside {{
    grid-template-columns: minmax(0, 1fr) 280px;
  }}
  .with-aside.left {{
    grid-template-columns: 280px minmax(0, 1fr);
  }}
  .with-aside.left > .site-aside {{
    order: -1;
  }}
  .with-aside > .site-aside {{
    position: sticky;
    top: 1rem;
  }}
}}
"""
