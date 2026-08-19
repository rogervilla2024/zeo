"""Tests pinning WCAG AA across every shipped theme identity."""

from __future__ import annotations

from pathlib import Path

from check_contrast import main
from seo_content_forge.contrast import (
    contrast_ratio,
    palette_problems,
    resolved_palettes,
)
from seo_content_forge.theme_css import VARIANTS


def test_contrast_ratio_matches_known_values() -> None:
    assert contrast_ratio("#000000", "#ffffff") == 21.0
    assert contrast_ratio("#ffffff", "#000000") == 21.0
    assert abs(contrast_ratio("#777777", "#ffffff") - 4.48) < 0.02
    # Short hex form resolves.
    assert contrast_ratio("#000", "#fff") == 21.0


def test_every_shipped_identity_holds_aa() -> None:
    # A palette tweak that drops body text below AA is an
    # accessibility regression; all forty identities are pinned in
    # BOTH schemes, so a future identity edit cannot ship one.
    failures: list[str] = []
    for variant in VARIANTS:
        light, dark = resolved_palettes(variant)
        for scheme, palette in (("light", light), ("dark", dark)):
            for problem in palette_problems(palette, scheme):
                failures.append(f"{variant} {problem}")
    assert failures == []


def test_cli_validates_overrides(tmp_path: Path) -> None:
    good = tmp_path / "good.json"
    good.write_text('{"theme": {"variant": "botanic"}}')
    assert main(["--config", str(good)]) == 0

    # A pale-grey-on-white override is exactly the regression the
    # gate exists to catch.
    bad = tmp_path / "bad.json"
    bad.write_text(
        '{"theme": {"variant": "botanic",'
        ' "palette": {"text": "#bbbbbb"}}}'
    )
    assert main(["--config", str(bad)]) == 1

    assert main(["--config", str(tmp_path / "missing.json")]) == 2
