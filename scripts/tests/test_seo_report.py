"""Test for the offline gate score card runner."""

from __future__ import annotations

from pathlib import Path

from seo_report import run_gates


def test_run_gates_on_minimal_dist(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text(
        '<script type="application/ld+json">{"@context":"https://schema.org",'
        '"@type":"Organization","name":"E","url":"https://e.com",'
        '"logo":"https://e.com/l.png","sameAs":["https://x.com/e"]}</script>'
    )
    results = run_gates(dist)
    assert results["rich-results"] is True
    assert results["js-budget"] is True
    assert results["broken-links"] is True
    assert results["media-budget"] is True
