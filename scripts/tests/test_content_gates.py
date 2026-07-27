"""Tests for the internal-links and category source gates."""

from __future__ import annotations

from pathlib import Path

import orjson

from check_article_categories import category_required
from check_article_categories import main as categories_main
from check_internal_links import main as links_main
from check_internal_links import resolve_min
from seo_content_forge.content_checks import (
    check_categories,
    check_internal_links,
    internal_link_count,
)

LINKED = """---
title: "Kekik"
category: "Bitki"
image: "/img/kekik.svg"
---
See [ihlamur](/ihlamur/) and <a href="/adacayi/">adacayi</a>.

![hero](/img/kekik-1.svg)
"""

UNLINKED = """---
title: "Ihlamur"
category: "Bitki"
---
No links here, and [external](https://example.org) does not count.
"""

UNCATEGORIZED = """---
title: "Zencefil"
---
Body.
"""


def test_internal_link_count_shapes() -> None:
    assert internal_link_count(LINKED) == 2
    assert internal_link_count(UNLINKED) == 0
    # Markdown images are not links, even though their syntax nests
    # the same ](/ sequence.
    assert internal_link_count("---\na: b\n---\n![x](/img/x.png)") == 0
    # A frontmatter-less file still counts its body links.
    assert internal_link_count("plain [in](/deep/page/) text") == 1


def test_check_internal_links_scales_with_site_size(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text(UNLINKED)
    # A single-article site has nothing to link to: effective min 0.
    assert check_internal_links(tmp_path, min_links=2) == []
    # A second article raises the effective minimum to 1.
    (tmp_path / "b.md").write_text(LINKED)
    problems = check_internal_links(tmp_path, min_links=2)
    assert problems == ["a.md: 0 in-body internal link(s), needs at least 1"]
    # Three or more articles enforce the configured minimum.
    (tmp_path / "c.md").write_text(LINKED)
    problems = check_internal_links(tmp_path, min_links=2)
    assert problems == ["a.md: 0 in-body internal link(s), needs at least 2"]
    assert check_internal_links(tmp_path, min_links=0) == []


def test_check_categories(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text(LINKED)
    assert check_categories(tmp_path) == []
    (tmp_path / "b.md").write_text(UNCATEGORIZED)
    assert check_categories(tmp_path) == ["b.md: missing category frontmatter"]


def test_resolve_min_and_required_defaults(tmp_path: Path) -> None:
    config = tmp_path / "site.config.json"
    assert resolve_min(config, override=None) == 2
    assert resolve_min(config, override=0) == 0
    config.write_bytes(orjson.dumps({"content": {"min_internal_links": 4}}))
    assert resolve_min(config, override=None) == 4
    # Category requirement defaults to on; only an explicit false
    # opts a site out.
    assert category_required(tmp_path / "missing.json") is True
    config.write_bytes(orjson.dumps({"content": {"require_category": False}}))
    assert category_required(config) is False


def test_cli_exit_codes(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    content = tmp_path / "blog"
    content.mkdir()
    (content / "a.md").write_text(LINKED)
    (content / "b.md").write_text(LINKED)
    (content / "c.md").write_text(UNLINKED)
    assert links_main(["--content", str(content), "--min", "2"]) == 1
    assert "LINKS c.md" in capsys.readouterr().out
    assert links_main(["--content", str(content), "--min", "0"]) == 0
    assert links_main(["--content", str(tmp_path / "absent")]) == 2

    assert categories_main(["--content", str(content)]) == 0
    (content / "d.md").write_text(UNCATEGORIZED)
    assert categories_main(["--content", str(content)]) == 1
    capsys.readouterr()
    config = tmp_path / "site.config.json"
    config.write_bytes(orjson.dumps({"content": {"require_category": False}}))
    argv = ["--content", str(content), "--config", str(config)]
    assert categories_main(argv) == 0
    assert "Skipped" in capsys.readouterr().out
    assert categories_main(["--content", str(tmp_path / "absent")]) == 2
