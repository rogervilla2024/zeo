"""Tests for the fleet dashboard aggregation and HTML report."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fleet_report import main
from seo_content_forge.fleet import (
    build_html,
    combo_clashes,
    discover,
    gate_columns,
    site_combo,
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


def test_site_report_rejects_non_dict_latest_and_skips_corrupt_runs() -> None:
    with pytest.raises(ValueError, match="not a mapping"):
        site_report("blog", ["oops"])  # type: ignore[list-item]
    corrupt: list[dict[str, object]] = [
        {"results": {"a": True}},
        "corrupt-run",  # type: ignore[list-item]
        {"results": {"a": False}},
    ]
    report = site_report("blog", corrupt)
    assert report.scores == [1, 0]


def test_main_skips_history_with_corrupt_latest_run(tmp_path: Path) -> None:
    bad = tmp_path / "bad" / ".seo-history.json"
    bad.parent.mkdir(parents=True)
    bad.write_text(json.dumps(["oops"]))
    _write_history(
        tmp_path / "good" / ".seo-history.json",
        [{"results": {"a": True}, "score": 1}],
    )
    output = tmp_path / "fleet.html"
    code = main(["--scan", str(tmp_path), "--output", str(output)])
    assert code == 1
    assert "good" in output.read_text()


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


def test_regressions_and_recoveries_detected() -> None:
    from seo_content_forge.fleet import maintenance_order

    runs: list[dict[str, object]] = [
        {"results": {"a": True, "b": True, "c": False}},
        {"results": {"a": True, "b": False, "c": True}},
    ]
    report = site_report("blog", runs)
    assert report.regressions == ["b"]
    assert report.recoveries == ["c"]
    # A single-run site has nothing to regress against.
    fresh = site_report("new", [{"results": {"a": False}}])
    assert fresh.regressions == [] and fresh.failing == ["a"]

    ranked = maintenance_order([report, fresh])
    # Regressions outrank standing failures.
    assert [entry.name for entry, _ in ranked] == ["blog", "new"]
    assert "1 regressed: b" in ranked[0][1]
    green = site_report("ok", [{"results": {"a": True}}])
    assert maintenance_order([green]) == []


def test_build_html_marks_regressions_and_maintenance() -> None:
    runs: list[dict[str, object]] = [
        {"results": {"a": True, "b": True}},
        {"results": {"a": False, "b": True}},
    ]
    html_out = build_html([site_report("blog", runs)])
    assert "FAIL (new)" in html_out
    assert "Maintenance order" in html_out
    assert "1 regressed: a" in html_out
    # A green fleet renders no maintenance section.
    green = build_html([site_report("ok", [{"results": {"a": True}}])])
    assert "Maintenance order" not in green


def test_site_combo_display_and_key() -> None:
    config: dict[str, object] = {
        "site_type": "directory",
        "theme": {"variant": "review", "recipe": "H3+N1+L2+F3"},
        "homepage": {"blocks": ["directory:list", "latest"]},
    }
    display, key = site_combo(config)
    assert display == "review | H3+N1+L2+F3 | directory:list>latest"
    assert key == "H3+N1+L2+F3|directory:list>latest"

    # Empty blocks fall back to the archetype default marker, so two
    # default-layout sites of the same type stay comparable.
    display, key = site_combo(
        {"site_type": "portal", "theme": {"recipe": "H1+N2+L1+F1"}}
    )
    assert display.endswith("default:portal")
    assert key == "H1+N2+L1+F1|default:portal"

    # Without a recorded recipe uniqueness cannot be judged.
    assert site_combo({"theme": {"variant": "minimal"}})[1] == ""


def test_combo_clashes_and_html_identity_column() -> None:
    a = site_report("alpha", [{"results": {"x": True}}])
    b = site_report("beta", [{"results": {"x": True}}])
    c = site_report("gamma", [{"results": {"x": True}}])
    a.combo = b.combo = "minimal | H1+N1+L1+F1 | default:portal"
    a.combo_key = b.combo_key = "H1+N1+L1+F1|default:portal"
    c.combo = "guide | H2+N2+L2+F2 | default:portal"
    c.combo_key = "H2+N2+L2+F2|default:portal"
    clashes = combo_clashes([a, b, c])
    assert clashes == [("H1+N1+L1+F1|default:portal", ["alpha", "beta"])]

    page = build_html([a, b, c])
    assert "<th>Identity</th>" in page
    assert "Identity clashes" in page
    assert "alpha, beta" in page
    # Reports without combos keep the old table shape.
    plain = build_html([site_report("solo", [{"results": {"x": True}}])])
    assert "<th>Identity</th>" not in plain
    assert "Identity clashes" not in plain


def test_main_reads_config_and_gates_on_identity_clash(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    config = {
        "site_type": "portal",
        "theme": {"variant": "minimal", "recipe": "H1+N1+L1+F1"},
        "homepage": {"blocks": []},
    }
    for site in ("blog", "docs"):
        _write_history(
            tmp_path / site / ".seo-history.json",
            [{"results": {"a": True}, "score": 1}],
        )
        (tmp_path / site / "site.config.json").write_text(json.dumps(config))
    output = tmp_path / "fleet.html"
    code = main(["--scan", str(tmp_path), "--output", str(output)])
    # Both sites green, but they share recipe + block order.
    assert code == 1
    err = capsys.readouterr().err
    assert "IDENTITY CLASH" in err and "blog, docs" in err
    assert "Identity clashes" in output.read_text()

    # Distinct recipes clear the gate.
    config["theme"] = {"variant": "guide", "recipe": "H2+N2+L2+F2"}
    (tmp_path / "docs" / "site.config.json").write_text(json.dumps(config))
    assert main(["--scan", str(tmp_path), "--output", str(output)]) == 0


def test_main_prints_maintenance_order(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    _write_history(
        tmp_path / "blog" / ".seo-history.json",
        [
            {"results": {"a": True, "b": True}},
            {"results": {"a": True, "b": False}},
        ],
    )
    out_file = tmp_path / "fleet.html"
    assert main(["--scan", str(tmp_path), "--output", str(out_file)]) == 1
    printed = capsys.readouterr().out
    assert "Maintenance order (regressions first):" in printed
    assert "1. blog  1 regressed: b" in printed
