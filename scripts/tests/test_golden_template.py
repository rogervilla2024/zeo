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
        "src/lib/slugify.ts",
        "src/styles/site.css",
        "src/pages/index.astro",
        "src/pages/blog/index.astro",
        "src/pages/[...slug].astro",
        "src/pages/[category_base]/[slug].astro",
        "src/pages/authors/[slug].astro",
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


def test_ui_strings_config_and_wiring() -> None:
    config = json.loads((GOLDEN / "site.config.json").read_text())
    ui = config["ui"]
    required = {
        "latest_articles", "key_takeaways", "on_this_page", "faq_title",
        "read_next", "by", "published", "updated", "min_read",
        "footer_explore", "footer_trust", "rights", "search",
        "search_placeholder", "home", "skip_to_content", "theme_toggle",
        "about", "contact", "privacy_policy", "terms_of_service", "disclaimer",
        "blog", "popular", "category_description", "author_articles",
    }
    assert required <= set(ui), f"missing ui keys: {required - set(ui)}"
    # The category page substitutes the category name into the text.
    assert "{category}" in ui["category_description"]
    assert "{author}" in ui["author_articles"]
    assert all(isinstance(v, str) and v for v in ui.values())
    # The visible component labels must be driven by config.ui, so a
    # Turkish site never leaks English chrome.
    pages = GOLDEN / "src" / "pages"
    assert "ui.latest_articles" in (pages / "index.astro").read_text()
    article = (pages / "[...slug].astro").read_text()
    for key in ("ui.key_takeaways", "ui.faq_title", "ui.read_next", "ui.by"):
        assert key in article, f"article template misses {key}"
    assert "ui.search" in (pages / "search.astro").read_text()
    footer = (GOLDEN / "src" / "components" / "Footer.astro").read_text()
    assert "ui.footer_explore" in footer and "ui.rights" in footer
    layout = (GOLDEN / "src" / "layouts" / "BaseLayout.astro").read_text()
    assert "ui.skip_to_content" in layout


def test_homepage_portal_composition() -> None:
    index = (GOLDEN / "src" / "pages" / "index.astro").read_text()
    for hook in ("feature-card", "category-strip", "PostCard", "Sidebar"):
        assert hook in index, f"homepage misses {hook}"
    # Strip titles must link to the category archives.
    assert '<a href={strip.url}>' in index
    assert "slugify" in index
    schema = (GOLDEN / "src" / "content.config.ts").read_text()
    assert "category" in schema, "content schema misses the category field"


def test_category_archive_pages() -> None:
    config = json.loads((GOLDEN / "site.config.json").read_text())
    # The URL segment is config-driven so non-English sites get a
    # native path (e.g. /kategori/...).
    base = config["seo"]["category_base"]
    assert isinstance(base, str) and base and "/" not in base

    route = (GOLDEN / "src" / "pages" / "[category_base]" / "[slug].astro")
    text = route.read_text()
    for hook in (
        "getStaticPaths", "BreadcrumbList", "PostCard", "category_base",
        "slugify", "ui.category_description", "canonical",
    ):
        assert hook in text, f"category route misses {hook}"

    # The slug helper must fold Turkish dotless i explicitly - NFD
    # normalization alone cannot, so its absence breaks Turkish sites.
    helper = (GOLDEN / "src" / "lib" / "slugify.ts").read_text()
    assert "\\u0131" in helper and "\\u0130" in helper
    assert 'normalize("NFD")' in helper

    # Article breadcrumbs climb to the category archive when set.
    article = (GOLDEN / "src" / "pages" / "[...slug].astro").read_text()
    assert "parentCrumb" in article
    assert "post.data.category" in article


def test_author_profile_pages() -> None:
    config = json.loads((GOLDEN / "site.config.json").read_text())
    # Config authors must resolve to the shipped route, so bylines and
    # article JSON-LD never point at a 404.
    for author in config["authors"]:
        assert author["url"].startswith("/authors/")
        assert author["bio"], "example author needs a bio placeholder"

    route = (GOLDEN / "src" / "pages" / "authors" / "[slug].astro")
    text = route.read_text()
    for hook in (
        "getStaticPaths", '"Person"', "BreadcrumbList", "PostCard",
        "ui.author_articles", "canonical", "sameAs", "jobTitle",
        "authorUrl",
    ):
        assert hook in text, f"author route misses {hook}"
    # Only authors published under /authors/ get a page; a config
    # author pointing elsewhere (e.g. an external profile) must not
    # break the build.
    assert 'startsWith("/authors/")' in text


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
