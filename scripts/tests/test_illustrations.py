"""Tests for the entity/cover illustration generators."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from generate_cover_image import main as cover_main
from generate_entity_images import main as entities_main
from seo_content_forge.illustrations import (
    STYLES,
    cover_svg,
    entity_card_svg,
)


def test_cards_are_deterministic_and_distinct() -> None:
    one = entity_card_svg("Harbor View House", "building", "#0f766e")
    two = entity_card_svg("Harbor View House", "building", "#0f766e")
    other = entity_card_svg("Cedar Ridge Lodge", "building", "#0f766e")
    assert one == two, "same title must draw the same card"
    assert one != other, "different titles must draw different cards"
    assert one.startswith("<svg") and 'width="800" height="450"' in one
    assert "Harbor View House" in one
    # Self-contained: no external fetches, captions escaped.
    assert "http" not in one.replace("http://www.w3.org", "")
    escaped = entity_card_svg("A & B <Inn>", "abstract", "#123456")
    assert "&amp; B &lt;Inn&gt;" in escaped


def test_every_style_draws_and_unknown_rejects() -> None:
    for style in STYLES:
        svg = entity_card_svg("Sample", style, "#7c3aed")
        assert "<svg" in svg and "ellipse" in svg or "rect" in svg
    with pytest.raises(ValueError, match="unknown style"):
        entity_card_svg("Sample", "photoreal", "#7c3aed")
    with pytest.raises(ValueError, match="unknown style"):
        cover_svg("Sample", "", "photoreal", "#7c3aed")


def test_cover_is_wide_with_scrim_and_tagline() -> None:
    svg = cover_svg("Field Guide", "Evidence first", "nature", "#166534")
    assert 'width="1600" height="900"' in svg
    assert "Field Guide" in svg and "Evidence first" in svg
    assert "scrim" in svg
    assert "Evidence" not in cover_svg("Field Guide", "", "nature", "#166534")
    # A7 hero backgrounds skip the baked text (the h1 overlays it)
    # but keep the art seeded by the title.
    bare = cover_svg(
        "Field Guide", "Evidence first", "nature", "#166534",
        draw_text=False,
    )
    assert "Field Guide" not in bare and "Evidence first" not in bare
    assert "scrim" in bare
    other = cover_svg("Other Site", "", "nature", "#166534",
                      draw_text=False)
    assert bare != other, "title must still seed the art"


def _site(tmp_path: Path) -> Path:
    root = tmp_path / "site"
    entities = root / "src" / "content" / "entities"
    entities.mkdir(parents=True)
    (root / "site.config.json").write_text(
        json.dumps({"theme": {"variant": "botanic", "palette": {}}})
    )
    (entities / "one.md").write_text('---\ntitle: "One Inn"\n---\n')
    (entities / "two.md").write_text(
        '---\ntitle: "Two Inn"\nimage: "/img/existing.svg"\n---\n'
    )
    return root


def test_entity_cli_draws_imageless_and_patches_frontmatter(
    tmp_path: Path,
) -> None:
    root = _site(tmp_path)
    assert entities_main(["--root", str(root), "--style", "building"]) == 0
    drawn = root / "public" / "img" / "entity-one.svg"
    assert drawn.is_file()
    one = (root / "src" / "content" / "entities" / "one.md").read_text()
    assert 'image: "/img/entity-one.svg"' in one
    # Entities that already have an image are left alone...
    two = (root / "src" / "content" / "entities" / "two.md").read_text()
    assert 'image: "/img/existing.svg"' in two
    # ...unless --force redraws them in place.
    assert entities_main(
        ["--root", str(root), "--style", "building", "--force"]
    ) == 0
    two = (root / "src" / "content" / "entities" / "two.md").read_text()
    assert 'image: "/img/entity-two.svg"' in two

    assert entities_main(["--root", str(root), "--style", "x"]) == 2
    assert entities_main(["--root", str(tmp_path / "empty")]) == 2


def test_cover_cli_writes_and_prints_config(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _site(tmp_path)
    code = cover_main(
        ["--root", str(root), "--title", "Field Guide",
         "--tagline", "Evidence first", "--style", "nature"]
    )
    assert code == 0
    cover = root / "public" / "img" / "cover.svg"
    assert cover.is_file()
    printed = capsys.readouterr().out
    assert '"hero": "cover"' in printed and "/img/cover.svg" in printed
    # Default output is art-only: the A7 hero overlays its own text.
    assert "Field Guide" not in cover.read_text()
    assert cover_main(
        ["--root", str(root), "--title", "Field Guide",
         "--tagline", "Evidence first", "--style", "nature",
         "--with-text"]
    ) == 0
    assert "Field Guide" in cover.read_text()
    assert cover_main(["--root", str(root), "--title", "X",
                       "--style", "nope"]) == 2
