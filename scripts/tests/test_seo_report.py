"""Tests for the gate score card runner (offline and live)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import seo_report
from seo_report import gate_commands, main, run_gates


def test_run_gates_on_minimal_dist(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text(
        "<html><head><title>Example minimal fixture page</title>"
        '<meta name="description" content="A fixture page description '
        'that sits comfortably inside the snippet bounds.">'
        '<script type="application/ld+json">{"@context":"https://schema.org",'
        '"@type":"Organization","name":"E","url":"https://e.com",'
        '"logo":"https://e.com/l.png","sameAs":["https://x.com/e"]}</script>'
        "</head><body></body></html>"
    )
    results = run_gates(dist)
    assert results["rich-results"] is True
    assert results["js-budget"] is True
    assert results["broken-links"] is True
    assert results["media-budget"] is True
    assert results["meta-quality"] is True
    assert results["image-attrs"] is True
    assert "agent-ready" not in results


def test_gate_commands_offline_only(tmp_path: Path) -> None:
    commands = gate_commands(tmp_path / "dist")
    assert [name for name, _ in commands] == [
        "rich-results",
        "js-budget",
        "broken-links",
        "media-budget",
        "meta-quality",
        "image-attrs",
    ]
    for _, argv in commands:
        assert not any("{dist}" in part or "{live}" in part for part in argv)


def test_gate_commands_with_live_url(tmp_path: Path) -> None:
    commands = dict(gate_commands(tmp_path / "dist", "https://example.com"))
    assert len(commands) == 8
    assert commands["agent-ready"] == [
        "check_agent_ready.py",
        "--url",
        "https://example.com",
    ]
    assert commands["canonical-host"] == [
        "check_canonical_host.py",
        "--domain",
        "https://example.com",
    ]


def test_gate_commands_resolves_relative_dist(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    commands = dict(gate_commands(Path("dist")))
    assert commands["js-budget"] == [
        "check_js_budget.py",
        "--dist",
        str((tmp_path / "dist").resolve()),
    ]


def test_main_offline_history_delta(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    runs = iter(
        [
            {"rich-results": True, "js-budget": True},
            {"rich-results": True, "js-budget": False},
        ]
    )
    monkeypatch.setattr(seo_report, "run_gates", lambda dist, live=None: next(runs))
    history = tmp_path / ".seo-history.json"
    assert main(["--dist", str(tmp_path), "--history", str(history)]) == 0
    first = capsys.readouterr().out
    assert "Score: 2/2 offline gates" in first
    assert "Changed since last run" not in first

    assert main(["--dist", str(tmp_path), "--history", str(history)]) == 1
    second = capsys.readouterr().out
    assert "Changed since last run: js-budget" in second
    saved = json.loads(history.read_text())
    assert [entry["score"] for entry in saved] == [2, 1]
    assert "live_url" not in saved[-1]


def test_main_missing_dist_exits_2(tmp_path: Path) -> None:
    assert main(["--dist", str(tmp_path / "nope")]) == 2


def test_main_live_records_history(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake = {
        "rich-results": True,
        "js-budget": True,
        "broken-links": True,
        "media-budget": True,
        "agent-ready": True,
        "canonical-host": False,
    }
    monkeypatch.setattr(seo_report, "run_gates", lambda dist, live=None: fake)
    history = tmp_path / ".seo-history.json"
    code = main(
        [
            "--dist",
            str(tmp_path),
            "--history",
            str(history),
            "--live",
            "https://example.com",
        ]
    )
    assert code == 1
    printed = capsys.readouterr().out
    assert "Score: 5/6 gates (4 offline + 2 live)" in printed
    assert "FAIL  canonical-host" in printed
    saved = json.loads(history.read_text())
    assert saved[-1]["live_url"] == "https://example.com"
    assert saved[-1]["results"]["canonical-host"] is False
    assert saved[-1]["score"] == 5
