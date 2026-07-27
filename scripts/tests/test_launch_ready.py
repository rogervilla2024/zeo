"""Tests for the launch-readiness checker."""

from __future__ import annotations

from pathlib import Path

import orjson

from check_launch_ready import main
from seo_content_forge.launch import check_launch

CONFIG = {
    "site_name": "Faydalari Zararlari",
    "domain": "https://faydalarizararlari.com",
    "authors": [{"name": "Ayse Yilmaz", "url": "/authors/ayse-yilmaz"}],
    "content": {"launch_articles": 2},
}


def build_ready_site(root: Path) -> None:
    (root / "site.config.json").write_bytes(orjson.dumps(CONFIG))
    public = root / "public"
    public.mkdir()
    (public / "robots.txt").write_text(
        "User-agent: *\nSitemap: https://faydalarizararlari.com/sitemap.xml\n"
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
        "llms.txt missing",
        "no sitemap*.xml",
        "about.astro: unfilled placeholder",
        "1 article(s) in src/content/blog, launch pack is 2",
    )
    for expected in expectations:
        assert any(expected in p for p in problems), (expected, problems)
    assert main(["--root", str(tmp_path)]) == 1


def test_astro_expressions_are_not_placeholders(tmp_path: Path) -> None:
    build_ready_site(tmp_path)
    # Ordinary Astro/JSX braces must not read as unfilled stubs.
    (tmp_path / "src" / "pages" / "about.astro").write_text(
        "<h1>{config.site_name}</h1><p>{items.map((x) => x)}</p>"
    )
    assert check_launch(tmp_path) == []


def test_missing_config_exits_2(tmp_path: Path) -> None:
    assert main(["--root", str(tmp_path)]) == 2
