"""Tests for the image alt/dimensions gate."""

from __future__ import annotations

from pathlib import Path

from check_image_attrs import main
from seo_content_forge.image_attrs import check_image_attrs

CLEAN = (
    '<p><img src="/img/hero.webp" alt="Thyme tea in a cup" '
    'width="1600" height="900"></p>'
    '<img src="/img/deco.svg" alt="" width="640" height="360" loading="lazy">'
)


def test_clean_pages_pass(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text(f"<html><body>{CLEAN}</body></html>")
    (tmp_path / "plain.html").write_text("<html><body>no images</body></html>")
    assert check_image_attrs(tmp_path) == []


def test_missing_alt_and_dimensions_flagged(tmp_path: Path) -> None:
    (tmp_path / "a.html").write_text(
        '<img src="/img/one.png" width="640" height="360">'
        '<img src="/img/two.png" alt="chart" width="640">'
    )
    problems = check_image_attrs(tmp_path)
    assert len(problems) == 2
    assert any("one.png> has no alt" in p for p in problems)
    assert any("two.png> is missing width/height" in p for p in problems)


def test_markdown_style_img_without_dimensions_fails(tmp_path: Path) -> None:
    # What Astro renders for markdown image syntax: alt present,
    # dimensions absent - exactly the case the gate exists for.
    (tmp_path / "post.html").write_text('<img src="/img/x.png" alt="diagram">')
    problems = check_image_attrs(tmp_path)
    assert problems == [
        "post.html: <img /img/x.png> is missing width/height "
        "(layout shifts while it loads)"
    ]


def test_pagefind_skipped_but_404_checked(tmp_path: Path) -> None:
    pagefind = tmp_path / "pagefind"
    pagefind.mkdir()
    (pagefind / "frag.html").write_text('<img src="/x.png">')
    (tmp_path / "404.html").write_text('<img src="/y.png">')
    problems = check_image_attrs(tmp_path)
    assert all("404.html" in p for p in problems)
    assert len(problems) == 2


def test_cli_exit_codes(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text(f"<html>{CLEAN}</html>")
    assert main(["--dist", str(dist)]) == 0
    (dist / "bad.html").write_text('<img src="/img/naked.png">')
    assert main(["--dist", str(dist)]) == 1
    assert "IMG bad.html" in capsys.readouterr().out
    assert main(["--dist", str(tmp_path / "absent")]) == 2
