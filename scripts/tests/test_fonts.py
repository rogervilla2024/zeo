"""Tests for the self-hosted webfont pairings (T recipes)."""

from __future__ import annotations

from pathlib import Path

from fetch_fonts import main
from seo_content_forge.fonts import (
    PAIRINGS,
    config_fonts,
    fetch_pairing,
    font_face_css,
)


def test_pairings_cover_the_t_recipes() -> None:
    assert set(PAIRINGS) == {"T1", "T2", "T3", "T4", "T5"}
    for pairing in PAIRINGS.values():
        css = font_face_css(pairing)
        assert "@font-face" in css and "font-display: swap" in css
        assert "/fonts/" in css and "woff2" in css
        fonts = config_fonts(pairing)
        # The stack always names the webfont AND a system fallback.
        assert fonts["heading"].count(",") >= 1
        assert pairing.heading.family in fonts["heading"]


def _fixture_cdn(tmp_path: Path) -> str:
    # A file:// CDN mirroring the Fontsource layout.
    cdn = tmp_path / "cdn"
    for spec in (PAIRINGS["T2"].heading, PAIRINGS["T2"].body):
        family = cdn / f"{spec.slug}@latest"
        family.mkdir(parents=True, exist_ok=True)
        for weight in spec.weights:
            (family / f"latin-{weight}-normal.woff2").write_bytes(b"wOF2fake")
    return cdn.as_uri()


def test_fetch_pairing_writes_fonts_and_css(tmp_path: Path) -> None:
    site = tmp_path / "site"
    written = fetch_pairing(PAIRINGS["T2"], site, base_url=_fixture_cdn(tmp_path))
    assert len(written) == 4  # 2 heading weights + 2 body weights
    assert (site / "public" / "fonts" / "inter-400.woff2").read_bytes()
    css = (site / "src" / "styles" / "fonts.css").read_text()
    assert '"Space Grotesk"' in css and '"Inter"' in css


def test_cli_lists_installs_and_rejects_unknown(tmp_path: Path) -> None:
    assert main(["--list"]) == 0
    site = tmp_path / "site"
    code = main([
        "--pairing", "t2", "--root", str(site),
        "--base-url", _fixture_cdn(tmp_path),
    ])
    assert code == 0
    assert (site / "src" / "styles" / "fonts.css").is_file()
    assert main(["--pairing", "T9", "--root", str(site)]) == 2
    # A dead CDN is a clean failure, not a stack trace.
    assert main([
        "--pairing", "T2", "--root", str(site),
        "--base-url", (tmp_path / "missing").as_uri(),
    ]) == 1
