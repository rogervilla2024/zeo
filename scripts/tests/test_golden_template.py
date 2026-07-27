"""Tests keeping templates/golden in sync with its template sources."""

from __future__ import annotations

import json
from pathlib import Path

from seo_content_forge.theme_css import compose_css, from_config

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = ROOT / "templates" / "golden"
THEME = ROOT / "templates" / "theme"

# Golden file -> source of truth it must stay byte-identical to.
SYNCED: dict[str, Path] = {
    "src/layouts/BaseLayout.astro": THEME / "BaseLayout.astro",
    "public/robots.txt": ROOT / "templates" / "robots.txt",
    "public/_headers": ROOT / "templates" / "deploy" / "_headers",
    "site.config.json": ROOT / "templates" / "site.config.example.json",
}


def test_component_copies_match_theme_sources() -> None:
    components = sorted((GOLDEN / "src" / "components").glob("*.astro"))
    assert components, "golden template has no components"
    for copy in components:
        source = THEME / copy.name
        assert source.is_file(), f"{copy.name} has no source in templates/theme"
        assert copy.read_bytes() == source.read_bytes(), (
            f"{copy.name} drifted from templates/theme; re-copy the original"
        )


def test_synced_files_match_sources() -> None:
    for relative, source in SYNCED.items():
        copy = GOLDEN / relative
        assert copy.is_file(), f"golden template is missing {relative}"
        assert copy.read_bytes() == source.read_bytes(), (
            f"{relative} drifted from {source.relative_to(ROOT)}"
        )


def test_tokens_css_regenerates_from_golden_config() -> None:
    config = json.loads((GOLDEN / "site.config.json").read_text())
    expected = compose_css(from_config(config))
    actual = (GOLDEN / "src" / "styles" / "tokens.css").read_text()
    assert actual == expected, (
        "tokens.css is stale; regenerate with generate_theme_css.py "
        "--config templates/golden/site.config.json"
    )


def test_required_skeleton_files_exist() -> None:
    required = [
        "README.md",
        "package.json",
        "astro.config.mjs",
        "tsconfig.json",
        ".gitignore",
        "src/content.config.ts",
        "src/styles/site.css",
        "src/pages/index.astro",
        "src/pages/blog/index.astro",
        "src/pages/[...slug].astro",
        "src/pages/search.astro",
        "src/pages/rss.xml.js",
        "src/pages/about.astro",
        "src/pages/contact.astro",
        "src/pages/privacy-policy.astro",
        "src/pages/terms-of-service.astro",
        "src/pages/disclaimer.astro",
    ]
    for relative in required:
        assert (GOLDEN / relative).is_file(), f"missing {relative}"


def test_package_json_is_zero_js_static_build() -> None:
    package = json.loads((GOLDEN / "package.json").read_text())
    assert package["scripts"]["build"] == "astro build"
    assert "astro" in package["dependencies"]


_BINARY_SUFFIXES = {".png", ".ico", ".jpg", ".jpeg", ".webp", ".svg", ".woff2"}


def test_golden_files_are_ascii() -> None:
    checked = 0
    for path in GOLDEN.rglob("*"):
        if path.is_file() and path.suffix not in _BINARY_SUFFIXES:
            content = path.read_bytes()
            assert content.isascii(), f"{path} contains non-ASCII bytes"
            checked += 1
    assert checked > 20, "ASCII sweep unexpectedly skipped most files"
