"""Suggest fleet-unique design identities for the next site.

fleet_report.py answers "do two sites clash?" AFTER the fact; this
module answers "what should the NEXT site wear?" BEFORE it. It reads
the fleet's site.config.json files, collects what is already in use -
variants, recipe letters (A/H/N/L/F/T/B), finishes, and the hue band
of each site's effective primary color - and proposes identities
that reuse none of it: a fresh variant, a fresh anatomy and recipe
combo, a fresh type pairing, and a primary hue the fleet does not
own yet. Deterministic for a given fleet, so suggestions are
reviewable and testable.
"""

from __future__ import annotations

import colorsys
import re
from dataclasses import dataclass

from seo_content_forge.theme_css import FINISHES, VARIANTS, _identity

# The recipe alphabet, in catalog order (skills/design-theme):
# anatomies A1-A12, heroes H1-H4, headers N1-N6, listings L1-L3,
# footers F1-F3, type pairings T1-T5, block orders B1-B12.
RECIPE_GROUPS: dict[str, tuple[str, ...]] = {
    "A": tuple(f"A{i}" for i in range(1, 13)),
    "H": tuple(f"H{i}" for i in range(1, 5)),
    "N": tuple(f"N{i}" for i in range(1, 7)),
    "L": tuple(f"L{i}" for i in range(1, 4)),
    "F": tuple(f"F{i}" for i in range(1, 4)),
    "T": tuple(f"T{i}" for i in range(1, 6)),
    "B": tuple(f"B{i}" for i in range(1, 13)),
}

_LETTER_RE = re.compile(r"\b([AHNLFTB]\d{1,2})\b")

# Twelve 30-degree hue bands; a fleet of a hundred sites can still
# separate primaries by band before it needs to lean on lightness.
HUE_BANDS = 12
_FINISH_CYCLE: tuple[str, ...] = ("", *sorted(FINISHES))


@dataclass
class FleetUsage:
    """Everything the existing fleet already wears."""

    variants: set[str]
    letters: set[str]
    finishes: set[str]
    hue_bands: set[int]


@dataclass
class Suggestion:
    """One proposed identity for the next site."""

    variant: str
    finish: str
    anatomy: str
    combo: str
    block_order: str
    primary: str
    hue_band: int

    @property
    def recipe(self) -> str:
        """The theme.recipe string the config should record."""
        return f"{self.anatomy} / {self.combo} / {self.block_order}"


def _hex_to_hue(color: str) -> float | None:
    raw = color.strip().lstrip("#")
    if len(raw) == 3:
        raw = "".join(ch * 2 for ch in raw)
    if len(raw) != 6:
        return None
    try:
        r, g, b = (int(raw[i : i + 2], 16) / 255 for i in (0, 2, 4))
    except ValueError:
        return None
    hue, _, saturation = colorsys.rgb_to_hls(r, g, b)
    # Neutrals carry no usable hue; do not count them as a band.
    return hue if saturation > 0.08 else None


def _hue_band(color: str) -> int | None:
    hue = _hex_to_hue(color)
    if hue is None:
        return None
    return int(hue * HUE_BANDS) % HUE_BANDS


def _band_hex(band: int) -> str:
    hue = (band + 0.5) / HUE_BANDS
    r, g, b = colorsys.hls_to_rgb(hue, 0.4, 0.55)
    return "#" + "".join(f"{round(v * 255):02x}" for v in (r, g, b))


def effective_primary(config: dict[str, object]) -> str:
    """A site's rendered primary: its override, else its variant's."""
    theme = config.get("theme")
    theme_map = theme if isinstance(theme, dict) else {}
    palette = theme_map.get("palette")
    palette_map = palette if isinstance(palette, dict) else {}
    override = str(palette_map.get("primary") or "")
    if override:
        return override
    variant = str(theme_map.get("variant") or "")
    identity_palette, _, _, _ = _identity(variant)
    return identity_palette.get("primary", "")


def fleet_usage(configs: list[dict[str, object]]) -> FleetUsage:
    """Collect what the fleet already uses.

    Args:
        configs: Parsed site.config.json contents, one per site.

    Returns:
        The used variants, recipe letters, finishes, and hue bands.
    """
    usage = FleetUsage(set(), set(), set(), set())
    for config in configs:
        theme = config.get("theme")
        theme_map = theme if isinstance(theme, dict) else {}
        variant = str(theme_map.get("variant") or "")
        if variant:
            usage.variants.add(variant)
        usage.letters.update(
            _LETTER_RE.findall(str(theme_map.get("recipe") or ""))
        )
        finish = str(theme_map.get("finish") or "")
        usage.finishes.add(finish)
        primary = effective_primary(config)
        band = _hue_band(primary) if primary else None
        if band is not None:
            usage.hue_bands.add(band)
    return usage


def _pick(options: tuple[str, ...], used: set[str], offset: int) -> str:
    """The offset-th unused option; cycle all options when exhausted."""
    fresh = [option for option in options if option not in used]
    pool = fresh or list(options)
    return pool[offset % len(pool)]


def suggest(
    configs: list[dict[str, object]], count: int = 3
) -> list[Suggestion]:
    """Propose fleet-unique identities for the next sites.

    Args:
        configs: The existing fleet's parsed configs (may be empty -
            a fresh fleet starts from the top of every catalog).
        count: How many suggestions to produce.

    Returns:
        Suggestions whose variant, recipe letters, and hue band avoid
        everything the fleet (and the earlier suggestions) already
        use, falling back to least-recently-cycled options only when
        a catalog is exhausted.
    """
    usage = fleet_usage(configs)
    taken_variants = set(usage.variants)
    taken_letters = set(usage.letters)
    taken_bands = set(usage.hue_bands)
    taken_finishes = set(usage.finishes)
    suggestions: list[Suggestion] = []
    for index in range(count):
        variant = _pick(VARIANTS, taken_variants, index)
        taken_variants.add(variant)
        picks: dict[str, str] = {}
        for group in ("A", "H", "N", "L", "F", "T", "B"):
            choice = _pick(RECIPE_GROUPS[group], taken_letters, index)
            taken_letters.add(choice)
            picks[group] = choice
        finish = _pick(_FINISH_CYCLE, taken_finishes, index)
        taken_finishes.add(finish)
        band = next(
            (b for b in range(HUE_BANDS) if b not in taken_bands),
            index % HUE_BANDS,
        )
        taken_bands.add(band)
        combo = "+".join(picks[g] for g in ("H", "N", "L", "F", "T"))
        suggestions.append(
            Suggestion(
                variant=variant,
                finish=finish,
                anatomy=picks["A"],
                combo=combo,
                block_order=picks["B"],
                primary=_band_hex(band),
                hue_band=band,
            )
        )
    return suggestions
