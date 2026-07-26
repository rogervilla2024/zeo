"""Detect when a site's toolkit clone has fallen behind upstream.

The PLAYBOOK rule is that the toolkit repo is the single source of
process: improvements land upstream and every site benefits on its next
session. That only holds if each site's clone actually pulls. These
helpers read the clone's plugin version and its git position relative
to the upstream default branch, so a small check can warn before a
stale clone quietly diverges from the standard.
"""

from __future__ import annotations

import re
import subprocess
from datetime import date
from pathlib import Path

import orjson

PLUGIN_MANIFEST = Path(".claude-plugin") / "plugin.json"


def local_version(root: Path) -> str | None:
    """Read the toolkit version from the clone's plugin manifest.

    Args:
        root: Toolkit clone root (the directory holding
            ``.claude-plugin/plugin.json``).

    Returns:
        The version string, or ``None`` when the manifest is missing or
        malformed.
    """
    try:
        raw = (root / PLUGIN_MANIFEST).read_bytes()
    except OSError:
        return None
    return _manifest_version(raw)


def _manifest_version(raw: bytes) -> str | None:
    try:
        data = orjson.loads(raw)
    except orjson.JSONDecodeError:
        return None
    version = data.get("version") if isinstance(data, dict) else None
    return version if isinstance(version, str) and version else None


def parse_version(version: str) -> tuple[int, ...]:
    """Parse ``"0.17.0"`` into ``(0, 17, 0)``.

    Only the leading digit run of each dot-part counts (``"3-rc1"``
    reads as 3, ``"v2"`` as 2), so a pre-release suffix can never sort
    a version above its final release.

    Args:
        version: Dotted version string.

    Returns:
        Numeric tuple suitable for comparison.
    """
    parts: list[int] = []
    for part in version.strip().split("."):
        match = re.search(r"\d+", part)
        parts.append(int(match.group()) if match else 0)
    return tuple(parts)


def git(root: Path, *args: str) -> str | None:
    """Run a git command in ``root``; return stripped stdout or ``None``.

    Args:
        root: Repository directory.
        *args: Git arguments, e.g. ``("rev-parse", "HEAD")``.

    Returns:
        Command output, or ``None`` when git fails or is unavailable.
    """
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def upstream_ref(root: Path) -> str | None:
    """The upstream default-branch ref, e.g. ``origin/main``.

    Args:
        root: Repository directory.

    Returns:
        The first of ``origin/HEAD``'s target, ``origin/main``, or
        ``origin/master`` that exists; ``None`` when there is no
        usable remote ref.
    """
    symbolic = git(root, "symbolic-ref", "refs/remotes/origin/HEAD")
    if symbolic and symbolic.startswith("refs/remotes/"):
        return symbolic.removeprefix("refs/remotes/")
    for candidate in ("origin/main", "origin/master"):
        if git(root, "rev-parse", "--verify", "--quiet", candidate) is not None:
            return candidate
    return None


def behind_ahead(root: Path, ref: str) -> tuple[int, int] | None:
    """Commits (behind, ahead) of HEAD relative to ``ref``.

    Args:
        root: Repository directory.
        ref: Upstream ref to compare against.

    Returns:
        ``(behind, ahead)`` counts, or ``None`` when git cannot tell.
    """
    output = git(root, "rev-list", "--left-right", "--count", f"HEAD...{ref}")
    if output is None:
        return None
    try:
        ahead_text, behind_text = output.split()
        return int(behind_text), int(ahead_text)
    except ValueError:
        return None


def upstream_version(root: Path, ref: str) -> str | None:
    """The plugin version at ``ref`` in the upstream history.

    Args:
        root: Repository directory.
        ref: Upstream ref, e.g. ``origin/main``.

    Returns:
        The version string, or ``None`` when unavailable.
    """
    manifest = git(root, "show", f"{ref}:{PLUGIN_MANIFEST.as_posix()}")
    if manifest is None:
        return None
    return _manifest_version(manifest.encode())


def head_age_days(root: Path, today: date) -> int | None:
    """Days since the clone's HEAD commit.

    Args:
        root: Repository directory.
        today: Reference date.

    Returns:
        Whole days, or ``None`` when git cannot tell.
    """
    output = git(root, "log", "-1", "--format=%cI")
    if not output:
        return None
    try:
        committed = date.fromisoformat(output[:10])
    except ValueError:
        return None
    return (today - committed).days
