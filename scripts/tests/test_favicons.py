"""Unit tests for :mod:`seo_content_forge.favicons`."""

from __future__ import annotations

from pathlib import Path

import orjson
import pytest
from PIL import Image

from seo_content_forge.favicons import (
    ICON_SIZES,
    ManifestSpec,
    build_manifest,
    generate_assets,
)


def _logo() -> Image.Image:
    return Image.new("RGBA", (512, 512), (16, 24, 40, 255))


def test_generates_all_icons_and_manifest(tmp_path: Path) -> None:
    # Arrange
    spec = ManifestSpec(name="Example Site", short_name="Example")

    # Act
    written = generate_assets(_logo(), tmp_path, spec)

    # Assert
    assert set(written) == set(ICON_SIZES) | {"site.webmanifest"}
    for filename, size in ICON_SIZES.items():
        with Image.open(tmp_path / filename) as icon:
            assert icon.size == (size, size)


def test_manifest_content(tmp_path: Path) -> None:
    # Arrange / Act
    generate_assets(
        _logo(),
        tmp_path,
        ManifestSpec(name="Example Site", short_name="Example", theme_color="#000000"),
    )
    manifest = orjson.loads((tmp_path / "site.webmanifest").read_bytes())

    # Assert
    assert manifest["name"] == "Example Site"
    assert manifest["theme_color"] == "#000000"
    assert {icon["sizes"] for icon in manifest["icons"]} == {"192x192", "512x512"}


def test_build_manifest_shape() -> None:
    manifest = build_manifest(ManifestSpec(name="N", short_name="S"))
    assert manifest["display"] == "standalone"


def test_empty_name_rejected() -> None:
    with pytest.raises(ValueError, match="required"):
        ManifestSpec(name="", short_name="S")
