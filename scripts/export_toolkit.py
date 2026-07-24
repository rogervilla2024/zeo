"""CLI to export the seo-content-forge toolkit into its own repository.

Usage:
    python export_toolkit.py --dest ~/repos/seo-content-forge
    python export_toolkit.py --dest ../forge --remote git@github.com:me/forge.git

Copies the toolkit directory (agents, skills, commands, scripts, plugin
manifest) to ``--dest``, excluding virtual environments, caches, and any
git history, then initializes a fresh git repository with an initial
commit. With ``--remote`` it also configures ``origin`` and prints the
push command - it never pushes on its own.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

_EXCLUDE = shutil.ignore_patterns(
    ".venv",
    "venv",
    "__pycache__",
    "*.py[cod]",
    "*.egg-info",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".git",
    "uv.lock",
)


def _git(dest: Path, *args: str) -> None:
    """Run a git command inside ``dest``, raising on failure."""
    subprocess.run(["git", "-C", str(dest), *args], check=True)


def export(dest: Path, remote: str | None = None) -> None:
    """Copy the toolkit to ``dest`` and initialize a git repository.

    Args:
        dest: Target directory; must not already exist.
        remote: Optional git remote URL to configure as ``origin``.

    Raises:
        FileExistsError: If ``dest`` already exists.
        subprocess.CalledProcessError: If a git command fails.
    """
    source = Path(__file__).resolve().parent.parent
    if dest.exists():
        raise FileExistsError(
            f"{dest} already exists; choose a new path so nothing is overwritten"
        )

    shutil.copytree(source, dest, ignore=_EXCLUDE)
    _git(dest, "init", "--initial-branch", "main")
    _git(dest, "add", "-A")
    _git(
        dest,
        "commit",
        "-m",
        "Initial commit: seo-content-forge toolkit exported to standalone repo",
    )
    if remote:
        _git(dest, "remote", "add", "origin", remote)


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns a process exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dest",
        required=True,
        type=Path,
        help="Target directory for the standalone repository (must not exist).",
    )
    parser.add_argument(
        "--remote",
        help="Optional git remote URL to configure as origin (not pushed).",
    )
    args = parser.parse_args(argv)

    dest = args.dest.expanduser().resolve()
    try:
        export(dest, remote=args.remote)
    except FileExistsError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Exported toolkit to {dest} and created the initial commit.")
    if args.remote:
        print(f"Remote 'origin' set to {args.remote}. To publish, run:")
        print(f"  git -C {dest} push -u origin main")
    else:
        print("Add a remote and push when ready:")
        print(f"  git -C {dest} remote add origin <url>")
        print(f"  git -C {dest} push -u origin main")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
