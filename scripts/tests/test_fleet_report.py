"""Tests for the fleet dashboard aggregation and HTML report."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fleet_report import main
from seo_content_forge.fleet import (
    build_html,
    discover,
    gate_columns,
    site_report,
)


def _write_history(path: Path, runs: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(runs))


def test_site_report_scores_and_delta() -> None:
    runs: list[dict[str, object]] = [
        {"results": {"a": True, "b": False}, "score": 1},
        {"results": {"a": True, "b": True}, "score": 2},
    ]
    report = site_report("blog", runs)
    assert report.score == 2
    assert report.total == 2
    assert report.delta == 1
    assert report.is_green is True
    assert report.scores == [1, 2]


def test_site_report_rejects_empty_history() -> None:
    with pytest.raises(ValueError, match="empty"):
        site_report("blog", [])
    with pytest.raises(ValueError, match="no results"):
        site_report("blog", [{"score": 0}])


def test_gate_columns_first_appearance_order() -> None:
    first = site_report("a", [{"results": {"x": True, "y": True}}])
    second = site_report("b", [{"results": {"y": False, "z": True}}])
    assert gate_columns([first, second]) == ["x", "y", "z"]


def test_build_html_escapes_and_marks_failures() -> None:
    report = site_report(
        "<evil> & site", [{"results": {"js-budget": False, "links": True}}]
    )
    page = build_html([report])
    assert "&lt;evil&gt; &amp; site" in page
    assert "<evil>" not in page
    assert 'class="fail">FAIL' in page
    assert 'class="pass">PASS' in page
    assert "1 site(s), 0 fully green." in page


def test_build_html_dashes_for_missing_gates() -> None:
    first = site_report("a", [{"results": {"x": True}}])
    second = site_report("b", [{"results": {"y": True}}])
    page = build_html([first, second])
    assert page.count('class="muted">-</td>') == 2


def test_discover_finds_per_site_histories(tmp_path: Path) -> None:
    _write_history(tmp_path / "blog" / ".seo-history.json", [])
    _write_history(tmp_path / "docs" / ".seo-history.json", [])
    (tmp_path / "empty-site").mkdir()
    found = discover(tmp_path)
    assert sorted(found) == ["blog", "docs"]


def test_main_scan_writes_report_and_gates_exit_code(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write_history(
        tmp_path / "sites" / "blog" / ".seo-history.json",
        [{"results": {"a": True}, "score": 1}],
    )
    _write_history(
        tmp_path / "sites" / "docs" / ".seo-history.json",
        [{"results": {"a": False}, "score": 0}],
    )
    output = tmp_path / "fleet.html"
    code = main(["--scan", str(tmp_path / "sites"), "--output", str(output)])
    assert code == 1
    page = output.read_text()
    assert "blog" in page and "docs" in page
    printed = capsys.readouterr().out
    assert "failing: a" in printed

    (tmp_path / "sites" / "docs" / ".seo-history.json").write_text(
        json.dumps([{"results": {"a": True}, "score": 1}])
    )
    assert main(["--scan", str(tmp_path / "sites"), "--output", str(output)]) == 0


def test_main_explicit_history_and_bad_file(tmp_path: Path) -> None:
    good = tmp_path / "blog" / ".seo-history.json"
    _write_history(good, [{"results": {"a": True}}])
    bad = tmp_path / "docs" / ".seo-history.json"
    bad.parent.mkdir()
    bad.write_text("not json")
    output = tmp_path / "fleet.html"
    code = main(
        ["--history", f"blog={good}", "--history", str(bad), "--output", str(output)]
    )
    assert code == 1
    assert output.is_file()
    assert main(["--output", str(output)]) == 2
