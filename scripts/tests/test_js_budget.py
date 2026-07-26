"""Unit tests for the JS budget checker."""

from __future__ import annotations

from pathlib import Path

from check_js_budget import collect_js_sizes, main


def _build_dist(tmp_path: Path, sizes: dict[str, int]) -> Path:
    dist = tmp_path / "dist"
    for name, size in sizes.items():
        target = dist / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"x" * size)
    return dist


def test_collects_and_sorts_js_files(tmp_path: Path) -> None:
    dist = _build_dist(
        tmp_path,
        {"a.js": 100, "assets/b.mjs": 300, "styles.css": 9999, "page.html": 50},
    )
    files = collect_js_sizes(dist)
    assert [path.name for path, _ in files] == ["b.mjs", "a.js"]


def test_within_budget_passes(tmp_path: Path) -> None:
    dist = _build_dist(tmp_path, {"a.js": 1024})
    assert main(["--dist", str(dist), "--max-kb", "30"]) == 0


def test_over_budget_fails(tmp_path: Path) -> None:
    dist = _build_dist(tmp_path, {"a.js": 40 * 1024})
    assert main(["--dist", str(dist), "--max-kb", "30"]) == 1


def test_missing_dir_errors(tmp_path: Path) -> None:
    assert main(["--dist", str(tmp_path / "nope")]) == 2


def test_pagefind_excluded_by_default(tmp_path: Path) -> None:
    dist = _build_dist(
        tmp_path,
        {"a.js": 1024, "pagefind/pagefind-ui.js": 400 * 1024},
    )
    files = collect_js_sizes(dist)
    assert [path.name for path, _ in files] == ["a.js"]
    assert main(["--dist", str(dist), "--max-kb", "30"]) == 0
    assert main(["--dist", str(dist), "--max-kb", "30", "--include-pagefind"]) == 1
    included = collect_js_sizes(dist, include_pagefind=True)
    assert [path.name for path, _ in included] == ["pagefind-ui.js", "a.js"]
