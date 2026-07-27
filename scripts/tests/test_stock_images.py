"""Unit tests for stock-image naming, hero cropping, and config default."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from fetch_stock_images import HERO_SIZE, cover_crop, output_name, slugify

ROOT = Path(__file__).resolve().parents[2]


def test_slugify_seo_names() -> None:
    assert slugify("French Press: Brewing!") == "french-press-brewing"
    assert slugify("   ") == "image"


def test_output_name_hero_and_body() -> None:
    assert output_name("Kekik Cayi", 1, hero=True) == "kekik-cayi-hero.webp"
    assert output_name("Kekik Cayi", 2, hero=False) == "kekik-cayi-2.webp"


def test_cover_crop_landscape_and_portrait_to_16x9() -> None:
    wide = cover_crop(Image.new("RGB", (4000, 1000), "red"))
    assert (wide.width, wide.height) == HERO_SIZE
    tall = cover_crop(Image.new("RGB", (900, 1600), "blue"))
    assert (tall.width, tall.height) == HERO_SIZE
    small = cover_crop(Image.new("RGB", (800, 450), "green"))
    assert (small.width, small.height) == HERO_SIZE


def test_config_example_defaults_to_illustration_hero() -> None:
    config = json.loads(
        (ROOT / "templates" / "site.config.example.json").read_text()
    )
    assert config["images"]["hero"] == "illustration"
    assert config["images"]["strategy"] == "svg-first"
