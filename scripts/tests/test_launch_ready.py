"""Tests for the launch-readiness checker."""

from __future__ import annotations

from pathlib import Path

import orjson

from check_launch_ready import main
from seo_content_forge.launch import check_launch

CONFIG = {
    "site_name": "Orchard Notes",
    "domain": "https://sample-orchard.com",
    "authors": [{"name": "Sam Rivers", "url": "/authors/sam-rivers"}],
    "content": {"launch_articles": 2},
}


def build_ready_site(root: Path) -> None:
    (root / "site.config.json").write_bytes(orjson.dumps(CONFIG))
    public = root / "public"
    public.mkdir()
    (public / "robots.txt").write_text(
        "User-agent: *\nSitemap: https://sample-orchard.com/sitemap.xml\n"
    )
    (public / "llms.txt").write_text("# Site\n")
    (public / "sitemap.xml").write_text("<urlset/>")
    (public / "favicon.svg").write_text("<svg/>")
    (public / "logo.png").write_bytes(b"png")
    (public / "og-image.png").write_bytes(b"png")
    pages = root / "src" / "pages"
    pages.mkdir(parents=True)
    (pages / "about.astro").write_text("<h1>Hakkimizda</h1>")
    content = root / "src" / "content" / "blog"
    content.mkdir(parents=True)
    (content / "a.md").write_text("---\ntitle: a\n---\nBody")
    (content / "b.md").write_text("---\ntitle: b\n---\nBody")


def test_ready_site_has_no_blockers(tmp_path: Path) -> None:
    build_ready_site(tmp_path)
    assert check_launch(tmp_path) == []
    assert main(["--root", str(tmp_path)]) == 0


def test_each_blocker_is_itemized(tmp_path: Path) -> None:
    build_ready_site(tmp_path)
    config = dict(CONFIG)
    config["domain"] = "https://example.com"
    config["authors"] = []
    (tmp_path / "site.config.json").write_bytes(orjson.dumps(config))
    (tmp_path / "public" / "robots.txt").write_text("Sitemap: {{SITE_URL}}/sitemap.xml")
    (tmp_path / "public" / "llms.txt").unlink()
    (tmp_path / "public" / "sitemap.xml").unlink()
    (tmp_path / "src" / "pages" / "about.astro").write_text(
        ':{"{{MISSION_ONE_SENTENCE}}"} placeholder'
    )
    (tmp_path / "src" / "content" / "blog" / "b.md").unlink()

    problems = check_launch(tmp_path)
    expectations = (
        "template value 'example.com'",
        "no authors registered",
        "{{SITE_URL}}",
        "no llms.txt",
        "no sitemap",
        "about.astro: unfilled placeholder",
        "1 article(s) in src/content/blog, launch pack is 2",
    )
    for expected in expectations:
        assert any(expected in p for p in problems), (expected, problems)
    assert main(["--root", str(tmp_path)]) == 1


def test_dynamic_endpoints_satisfy_sitemap_and_llms(tmp_path: Path) -> None:
    build_ready_site(tmp_path)
    # Golden sites ship llms.txt and the sitemap as dynamic endpoints
    # instead of static public/ files; both must satisfy the checks.
    (tmp_path / "public" / "llms.txt").unlink()
    (tmp_path / "public" / "sitemap.xml").unlink()
    pages = tmp_path / "src" / "pages"
    (pages / "llms.txt.js").write_text("export async function GET() {}")
    (pages / "sitemap.xml.js").write_text("export async function GET() {}")
    assert check_launch(tmp_path) == []


def test_redirects_placeholder_blocks_launch(tmp_path: Path) -> None:
    build_ready_site(tmp_path)
    (tmp_path / "public" / "_redirects").write_text(
        "https://www.{{DOMAIN}}/* https://{{DOMAIN}}/:splat 301\n"
    )
    problems = check_launch(tmp_path)
    assert any("_redirects still contains {{DOMAIN}}" in p for p in problems)
    (tmp_path / "public" / "_redirects").write_text(
        "https://www.sample-orchard.com/* "
        "https://sample-orchard.com/:splat 301\n"
    )
    assert check_launch(tmp_path) == []


def test_api_catalog_placeholder_blocks_launch(tmp_path: Path) -> None:
    build_ready_site(tmp_path)
    well_known = tmp_path / "public" / ".well-known"
    well_known.mkdir()
    catalog = well_known / "api-catalog"
    catalog.write_text('{"linkset": [{"anchor": "{{SITE_URL}}/api"}]}')
    problems = check_launch(tmp_path)
    assert any("api-catalog still contains {{SITE_URL}}" in p for p in problems)
    catalog.write_text(
        '{"linkset": [{"anchor": "https://sample-orchard.com/api"}]}'
    )
    assert check_launch(tmp_path) == []


def test_astro_expressions_are_not_placeholders(tmp_path: Path) -> None:
    build_ready_site(tmp_path)
    # Ordinary Astro/JSX braces must not read as unfilled stubs.
    (tmp_path / "src" / "pages" / "about.astro").write_text(
        "<h1>{config.site_name}</h1><p>{items.map((x) => x)}</p>"
    )
    assert check_launch(tmp_path) == []


def test_missing_config_exits_2(tmp_path: Path) -> None:
    assert main(["--root", str(tmp_path)]) == 2


def _write_entity(root: Path, name: str, frontmatter: str) -> None:
    entities = root / "src" / "content" / "entities"
    entities.mkdir(parents=True, exist_ok=True)
    (entities / name).write_text(f"---\n{frontmatter}\n---\n")


def test_directory_site_requires_entity_conversion_data(tmp_path: Path) -> None:
    build_ready_site(tmp_path)
    config = dict(CONFIG)
    config["site_type"] = "directory"
    (tmp_path / "site.config.json").write_bytes(orjson.dumps(config))

    # No entities at all: the homepage would render an empty catalog.
    problems = check_launch(tmp_path)
    assert any("no entries" in p for p in problems)

    # A bare entity ships a card with no conversion surface - the
    # empty fields are itemized by name.
    _write_entity(tmp_path, "bare.md", 'title: "Bare Inn"')
    problems = check_launch(tmp_path)
    assert any(
        "bare.md" in p and "rating, price, cta_url" in p for p in problems
    )

    # rating plus at least one of price/cta_url clears the gate.
    _write_entity(
        tmp_path,
        "bare.md",
        'title: "Bare Inn"\nrating: "8.4"\nprice: "from 90 EUR"',
    )
    assert check_launch(tmp_path) == []

    # rating alone is not enough - there is nothing to convert to.
    _write_entity(tmp_path, "scoreless.md", 'title: "Quiet Inn"\nrating: "7.9"')
    problems = check_launch(tmp_path)
    assert any(
        "scoreless.md" in p and "price, cta_url" in p for p in problems
    )


def test_entity_audit_only_runs_when_directory_is_active(tmp_path: Path) -> None:
    build_ready_site(tmp_path)
    # A portal keeping an unused entities folder must not be blocked.
    _write_entity(tmp_path, "draft.md", 'title: "Draft"')
    assert check_launch(tmp_path) == []

    # Mixing the directory block in via homepage.blocks activates it.
    config = dict(CONFIG)
    config["homepage"] = {"blocks": ["directory", "latest"]}
    (tmp_path / "site.config.json").write_bytes(orjson.dumps(config))
    problems = check_launch(tmp_path)
    assert any("draft.md" in p for p in problems)


def test_search_rename_requires_matching_robots_disallow(tmp_path: Path) -> None:
    build_ready_site(tmp_path)
    config = dict(CONFIG)
    config["seo"] = {"search_url_template": "/arama?q={search_term_string}"}
    (tmp_path / "site.config.json").write_bytes(orjson.dumps(config))
    problems = check_launch(tmp_path)
    assert any("Disallow: /arama" in p for p in problems)
    (tmp_path / "public" / "robots.txt").write_text(
        "User-agent: *\nDisallow: /arama?\n"
        "Sitemap: https://sample-orchard.com/sitemap.xml\n"
    )
    assert check_launch(tmp_path) == []
