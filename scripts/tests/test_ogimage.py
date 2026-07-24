"""Unit tests for :mod:`seo_content_forge.ogimage`."""

from __future__ import annotations

from pathlib import Path

import pytest

from seo_content_forge.ogimage import OgImageSpec, render_og_image


def test_renders_standard_og_size() -> None:
    # Arrange
    spec = OgImageSpec(title="A test article title", site_name="Example")

    # Act
    image = render_og_image(spec)

    # Assert
    assert image.size == (1200, 630)
    assert image.mode == "RGB"


def test_long_title_wraps_without_error() -> None:
    spec = OgImageSpec(
        title=" ".join(["longword"] * 40),
        site_name="Example",
        width=600,
        height=315,
    )
    image = render_og_image(spec)
    assert image.size == (600, 315)


def test_empty_title_rejected() -> None:
    with pytest.raises(ValueError, match="required"):
        OgImageSpec(title="", site_name="Example")


def test_saved_png_is_valid(tmp_path: Path) -> None:
    # Arrange
    spec = OgImageSpec(title="Save test", site_name="Example")
    output = tmp_path / "og.png"

    # Act
    render_og_image(spec).save(output, format="PNG")

    # Assert
    assert output.exists()
    assert output.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
