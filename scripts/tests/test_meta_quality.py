"""Tests for the SERP snippet quality gate."""

from __future__ import annotations

from pathlib import Path

from check_meta_quality import main
from seo_content_forge.meta_quality import Bounds, check_meta


def page(title: str, description: str, noindex: bool = False) -> str:
    robots = '<meta name="robots" content="noindex, nofollow">' if noindex else ""
    return (
        f"<html><head><title>{title}</title>{robots}"
        f'<meta name="description" content="{description}">'
        "</head><body>x</body></html>"
    )


GOOD_TITLE = "A perfectly sized page title here"
GOOD_DESC = (
    "A meta description that is comfortably inside the bounds Google "
    "will actually display."
)


def test_clean_dist_passes(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text(page(GOOD_TITLE, GOOD_DESC))
    sub = tmp_path / "about"
    sub.mkdir()
    (sub / "index.html").write_text(page("Another distinct title", GOOD_DESC))
    assert check_meta(tmp_path) == []


def test_length_and_presence_problems(tmp_path: Path) -> None:
    (tmp_path / "long.html").write_text(page("t" * 61, GOOD_DESC))
    (tmp_path / "short.html").write_text(page("tiny", "d" * 39))
    (tmp_path / "none.html").write_text("<html><head></head><body></body></html>")
    problems = check_meta(tmp_path)
    assert "long.html: title is 61 chars (max 60, truncated in SERPs)" in problems
    assert "short.html: title is 4 chars (min 10)" in problems
    assert any("short.html: description is 39 chars" in p for p in problems)
    assert "none.html: missing <title>" in problems
    assert "none.html: missing meta description" in problems


def test_duplicate_titles_and_skips(tmp_path: Path) -> None:
    (tmp_path / "a.html").write_text(page(GOOD_TITLE, GOOD_DESC))
    (tmp_path / "b.html").write_text(page(GOOD_TITLE, GOOD_DESC))
    # Noindex pages, 404.html, and pagefind internals never count.
    (tmp_path / "search.html").write_text(page("tiny", "x", noindex=True))
    (tmp_path / "404.html").write_text("<html><head></head></html>")
    pagefind = tmp_path / "pagefind"
    pagefind.mkdir()
    (pagefind / "frag.html").write_text("<html></html>")
    problems = check_meta(tmp_path)
    assert problems == [f"duplicate title {GOOD_TITLE!r}: a.html, b.html"]


def test_bounds_are_adjustable(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text(page("t" * 65, GOOD_DESC))
    assert check_meta(tmp_path, Bounds(title_max=70)) == []


def test_cli_exit_codes(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text(page(GOOD_TITLE, GOOD_DESC))
    assert main(["--dist", str(dist)]) == 0
    (dist / "bad.html").write_text(page("tiny", GOOD_DESC))
    assert main(["--dist", str(dist)]) == 1
    assert "META bad.html" in capsys.readouterr().out
    assert main(["--dist", str(dist), "--title-min", "3"]) == 0
    assert main(["--dist", str(tmp_path / "absent")]) == 2
