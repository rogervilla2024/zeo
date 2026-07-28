"""Tests for the orphan-article gate."""

from __future__ import annotations

from pathlib import Path

from check_orphan_pages import main
from seo_content_forge.orphans import find_orphans


def article(body_links: list[str]) -> str:
    links = "".join(f'<a href="{href}">x</a>' for href in body_links)
    return (
        "<html><body><nav><a href=\"/blog/\">hub</a></nav>"
        f'<article class="prose"><h1>t</h1><p>{links}</p></article>'
        "</body></html>"
    )


def hub(links: list[str]) -> str:
    anchors = "".join(f'<a href="{href}">x</a>' for href in links)
    return f"<html><body><ul>{anchors}</ul></body></html>"


def _write(dist: Path, rel: str, content: str) -> None:
    path = dist / rel / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def test_orphan_found_and_hub_links_do_not_count(tmp_path: Path) -> None:
    # a <-> b link each other; c and d link into the cycle but nothing
    # links to d; the hub linking EVERYTHING must not rescue d.
    _write(tmp_path, "a", article(["/b/"]))
    _write(tmp_path, "b", article(["/a/", "/c/"]))
    _write(tmp_path, "c", article(["/a/"]))
    _write(tmp_path, "d", article(["/a/", "/b/"]))
    _write(tmp_path, "blog", hub(["/a/", "/b/", "/c/", "/d/"]))
    problems = find_orphans(tmp_path)
    assert len(problems) == 1 and problems[0].startswith("/d/:")


def test_small_sites_pass_vacuously(tmp_path: Path) -> None:
    _write(tmp_path, "a", article([]))
    _write(tmp_path, "b", article([]))
    assert find_orphans(tmp_path) == []
    # Threshold is adjustable.
    assert len(find_orphans(tmp_path, min_articles=2)) == 2


def test_self_links_and_query_links_ignored(tmp_path: Path) -> None:
    _write(tmp_path, "a", article(["/a/", "/b/"]))
    _write(tmp_path, "b", article(["/a/"]))
    _write(tmp_path, "c", article(["/a/", "/b/"]))
    _write(tmp_path, "d", article(["/a/", "/b/", "/c/"]))
    problems = find_orphans(tmp_path)
    # d receives nothing; a's self-link never counted for a.
    assert [p.split(":")[0] for p in problems] == ["/d/"]


def test_cli_exit_codes(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    dist = tmp_path / "dist"
    for name in ("a", "b", "c", "d"):
        _write(dist, name, article(["/a/", "/b/", "/c/", "/d/"]))
    assert main(["--dist", str(dist)]) == 0
    _write(dist, "e", article([]))
    assert main(["--dist", str(dist)]) == 1
    assert "ORPHAN /e/:" in capsys.readouterr().out
    assert main(["--dist", str(tmp_path / "absent")]) == 2
