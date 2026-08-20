"""Tests for the fleet identity suggester."""

from __future__ import annotations

import json
from pathlib import Path

from seo_content_forge.identity import (
    HUE_BANDS,
    effective_primary,
    fleet_usage,
    suggest,
)
from seo_content_forge.theme_css import VARIANTS
from suggest_identity import main


def _config(variant: str, recipe: str = "", primary: str = "") -> dict[str, object]:
    theme: dict[str, object] = {"variant": variant, "recipe": recipe}
    if primary:
        theme["palette"] = {"primary": primary}
    return {"theme": theme}


def test_effective_primary_prefers_override_then_identity() -> None:
    assert effective_primary(_config("noir", primary="#123456")) == "#123456"
    # Without an override the variant's own identity primary counts.
    assert effective_primary(_config("botanic")) == "#166534"


def test_fleet_usage_collects_variants_letters_and_bands() -> None:
    usage = fleet_usage(
        [
            _config("noir", "A2 / H2+N1+L2+F3+T2 / B5"),
            _config("botanic", "H4+N2+L1+F2"),
        ]
    )
    assert usage.variants == {"noir", "botanic"}
    assert {"A2", "H2", "N1", "L2", "F3", "T2", "B5", "H4", "N2", "L1",
            "F2"} <= usage.letters
    # botanic's green identity occupies a hue band.
    assert len(usage.hue_bands) >= 1


def test_suggestions_avoid_everything_the_fleet_uses() -> None:
    fleet = [
        _config("minimal", "A1 / H1+N1+L1+F1+T1 / B1", "#dc2626"),
        _config("noir", "A2 / H2+N2+L2+F2+T2 / B2"),
    ]
    picks = suggest(fleet, count=3)
    assert len(picks) == 3
    used_variants = {"minimal", "noir"}
    seen_variants: set[str] = set()
    seen_bands: set[int] = set()
    for pick in picks:
        assert pick.variant in VARIANTS
        assert pick.variant not in used_variants
        assert pick.variant not in seen_variants, "suggestions must differ"
        seen_variants.add(pick.variant)
        for letter in ("A1", "A2", "H1", "H2", "N1", "N2", "T1", "T2",
                       "B1", "B2"):
            assert letter not in pick.recipe.replace(" ", "+").split("+")
        assert pick.hue_band not in seen_bands
        seen_bands.add(pick.hue_band)
        assert pick.primary.startswith("#") and len(pick.primary) == 7
        assert 0 <= pick.hue_band < HUE_BANDS
    # Deterministic: same fleet, same suggestions.
    assert [p.recipe for p in suggest(fleet, count=3)] == [
        p.recipe for p in picks
    ]


def test_empty_fleet_starts_from_the_top_of_the_catalogs() -> None:
    first = suggest([], count=1)[0]
    assert first.variant == VARIANTS[0]
    assert first.recipe == "A1 / H1+N1+L1+F1+T1 / B1"


def test_cli_scans_a_fleet_and_prints_suggestions(
    tmp_path: Path, capsys: object
) -> None:
    for name, variant, recipe in (
        ("alpha", "minimal", "A1 / H1+N1+L1+F1+T1 / B1"),
        ("beta", "noir", "A2 / H2+N2+L2+F2+T2 / B2"),
    ):
        site = tmp_path / name
        site.mkdir()
        (site / "site.config.json").write_text(
            json.dumps({"theme": {"variant": variant, "recipe": recipe}})
        )
    assert main(["--scan", str(tmp_path), "--count", "2"]) == 0
    out = capsys.readouterr().out  # type: ignore[attr-defined]
    assert "Fleet: 2 site(s)" in out
    assert "minimal" not in out.split("Fleet:")[1].split("1.")[0]
    assert '"recipe":' in out and "variant=" in out
    assert "A1" not in out.split("recipe: ")[1].split("\n")[0]

    assert main(["--scan", str(tmp_path / "missing")]) == 2
