"""Tests for the article-images gate (module, CLI, seo_report wiring)."""

from __future__ import annotations

from pathlib import Path

import orjson

from check_article_images import main, resolve_min_body
from seo_content_forge.article_images import (
    body_image_count,
    check_articles,
    parse_frontmatter,
)
from seo_report import gate_commands

GOOD = """---
title: "Kekik"
image: "/img/kekik-hero.svg"
---
Intro.

![diagram](/img/kekik-1.svg)

<img src="/img/kekik-2.svg" alt="table">
"""

NO_HERO = """---
title: "Adacayi"
---
Body without any hero.

![one](/img/a.svg)
![two](/img/b.svg)
"""

NO_BODY_IMAGES = """---
title: "Ihlamur"
image: "/img/ihlamur-hero.svg"
---
Text only.
"""


def test_parse_frontmatter_scalars_only() -> None:
    fields = parse_frontmatter(GOOD)
    assert fields["image"] == "/img/kekik-hero.svg"
    assert fields["title"] == "Kekik"
    assert parse_frontmatter("no frontmatter here") == {}
    # List items and indented lines never leak in as keys.
    nested = "---\ntakeaways:\n  - one\n- two\nimage: /x.png\n---\nBody"
    assert parse_frontmatter(nested) == {"takeaways": "", "image": "/x.png"}


def test_body_image_count_excludes_frontmatter_hero() -> None:
    assert body_image_count(GOOD) == 2
    assert body_image_count(NO_BODY_IMAGES) == 0
    # The hero path in frontmatter must not count as a body image.
    assert body_image_count("---\nimage: /img/hero.png\n---\nText.") == 0


def test_check_articles_flags_both_violations(tmp_path: Path) -> None:
    (tmp_path / "good.md").write_text(GOOD)
    (tmp_path / "no-hero.md").write_text(NO_HERO)
    (tmp_path / "no-body.md").write_text(NO_BODY_IMAGES)
    problems = check_articles(tmp_path, min_body_images=2)
    assert problems == [
        "no-body.md: 0 body image(s), config requires at least 2",
        "no-hero.md: missing hero image frontmatter",
    ]
    # With the body minimum disabled only the hero is enforced.
    assert check_articles(tmp_path, min_body_images=0) == [
        "no-hero.md: missing hero image frontmatter"
    ]


def test_check_articles_empty_collection_passes(tmp_path: Path) -> None:
    assert check_articles(tmp_path, min_body_images=2) == []


def test_resolve_min_body_precedence(tmp_path: Path) -> None:
    config = tmp_path / "site.config.json"
    config.write_bytes(orjson.dumps({"images": {"min": 3}}))
    assert resolve_min_body(config, override=None) == 3
    assert resolve_min_body(config, override=1) == 1
    assert resolve_min_body(tmp_path / "missing.json", override=None) == 0
    config.write_bytes(orjson.dumps({"images": {"min": "two"}}))
    assert resolve_min_body(config, override=None) == 0


def test_cli_pass_fail_and_missing_dir(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    content = tmp_path / "blog"
    content.mkdir()
    (content / "good.md").write_text(GOOD)
    assert main(["--content", str(content), "--min-body", "2"]) == 0
    assert "OK: 1 article(s)" in capsys.readouterr().out

    (content / "no-hero.md").write_text(NO_HERO)
    assert main(["--content", str(content), "--min-body", "2"]) == 1
    out = capsys.readouterr().out
    assert "IMAGES no-hero.md: missing hero image frontmatter" in out

    assert main(["--content", str(tmp_path / "absent")]) == 2


def test_cli_reads_min_from_config(tmp_path: Path) -> None:
    content = tmp_path / "blog"
    content.mkdir()
    (content / "no-body.md").write_text(NO_BODY_IMAGES)
    config = tmp_path / "site.config.json"
    config.write_bytes(orjson.dumps({"images": {"min": 2}}))
    argv = ["--content", str(content), "--config", str(config)]
    assert main(argv) == 1
    config.write_bytes(orjson.dumps({"images": {"min": 0}}))
    assert main(argv) == 0


def test_seo_report_auto_enables_gate_at_site_roots(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    # A bare dist (no source tree next to it) keeps the classic gates.
    names = [name for name, _ in gate_commands(dist)]
    assert "article-images" not in names

    content = tmp_path / "src" / "content" / "blog"
    content.mkdir(parents=True)
    (tmp_path / "site.config.json").write_bytes(orjson.dumps({"images": {"min": 2}}))
    commands = dict(gate_commands(dist))
    assert "article-images" in commands
    argv = commands["article-images"]
    assert argv[0] == "check_article_images.py"
    assert str(content) in argv
    assert str(tmp_path / "site.config.json") in argv
    # The gate slots in before the live gates.
    with_live = [name for name, _ in gate_commands(dist, "https://example.com")]
    assert with_live.index("article-images") < with_live.index("agent-ready")
