"""Tests for the toolkit staleness check."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import date
from pathlib import Path

import pytest

from check_toolkit_version import main
from seo_content_forge.version_check import (
    behind_ahead,
    head_age_days,
    local_version,
    parse_version,
    upstream_ref,
    upstream_version,
)

needs_git = pytest.mark.skipif(shutil.which("git") is None, reason="git not found")

# Pinned so commit-age assertions never depend on the wall clock.
_COMMIT_DATE = "2026-01-01T12:00:00+00:00"


def _git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        env={
            **os.environ,
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@e.com",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@e.com",
            "GIT_AUTHOR_DATE": _COMMIT_DATE,
            "GIT_COMMITTER_DATE": _COMMIT_DATE,
            "HOME": str(root),
            "GIT_CONFIG_NOSYSTEM": "1",
        },
    )


def _write_manifest(root: Path, version: str) -> None:
    manifest = root / ".claude-plugin" / "plugin.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps({"name": "zeo", "version": version}))


def _make_upstream_and_clone(tmp_path: Path) -> tuple[Path, Path]:
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    _git(upstream, "init", "-q", "-b", "main")
    _write_manifest(upstream, "0.1.0")
    _git(upstream, "add", "-A")
    _git(upstream, "commit", "-q", "-m", "v0.1.0")
    clone = tmp_path / "clone"
    _git(tmp_path, "clone", "-q", str(upstream), str(clone))
    return upstream, clone


def test_parse_version_handles_junk() -> None:
    assert parse_version("0.17.0") == (0, 17, 0)
    # A pre-release suffix must never sort above the final release.
    assert parse_version("1.2.3-rc1") == (1, 2, 3)
    assert parse_version("v2.0") == (2, 0)
    assert parse_version("") == (0,)
    assert parse_version("0.9.0") < parse_version("0.10.0")


def test_local_version_reads_manifest(tmp_path: Path) -> None:
    assert local_version(tmp_path) is None
    _write_manifest(tmp_path, "0.5.0")
    assert local_version(tmp_path) == "0.5.0"
    (tmp_path / ".claude-plugin" / "plugin.json").write_text("nope")
    assert local_version(tmp_path) is None


@needs_git
def test_behind_ahead_and_upstream_version(tmp_path: Path) -> None:
    upstream, clone = _make_upstream_and_clone(tmp_path)
    ref = upstream_ref(clone)
    assert ref is not None
    assert behind_ahead(clone, ref) == (0, 0)

    _write_manifest(upstream, "0.2.0")
    _git(upstream, "add", "-A")
    _git(upstream, "commit", "-q", "-m", "v0.2.0")
    _git(clone, "fetch", "-q", "origin")
    assert behind_ahead(clone, ref) == (1, 0)
    assert upstream_version(clone, ref) == "0.2.0"
    assert head_age_days(clone, date(2026, 1, 4)) == 3


@needs_git
def test_main_flags_stale_clone(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    upstream, clone = _make_upstream_and_clone(tmp_path)
    assert main(["--root", str(clone), "--no-fetch"]) == 0

    _write_manifest(upstream, "0.2.0")
    _git(upstream, "add", "-A")
    _git(upstream, "commit", "-q", "-m", "v0.2.0")
    _git(clone, "fetch", "-q", "origin")
    code = main(["--root", str(clone), "--no-fetch"])
    printed = capsys.readouterr().out
    assert code == 1
    assert "behind" in printed
    assert "upstream plugin version is 0.2.0" in printed


@needs_git
def test_main_max_age_days(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _, clone = _make_upstream_and_clone(tmp_path)
    # HEAD is pinned to 2026-01-01, far past any small limit.
    code = main(["--root", str(clone), "--no-fetch", "--max-age-days", "5"])
    printed = capsys.readouterr().out
    assert code == 1
    assert "days old (limit 5)" in printed
    assert (
        main(["--root", str(clone), "--no-fetch", "--max-age-days", "1000000"]) == 0
    )


def test_main_remote_version_and_bad_root(tmp_path: Path) -> None:
    _write_manifest(tmp_path, "0.5.0")
    assert main(["--root", str(tmp_path), "--remote-version", "0.5.0"]) == 0
    assert main(["--root", str(tmp_path), "--remote-version", "0.6.0"]) == 1
    assert main(["--root", str(tmp_path / "nowhere")]) == 2
