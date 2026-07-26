"""CLI to warn when this toolkit clone has fallen behind upstream.

Usage:
    python check_toolkit_version.py
    python check_toolkit_version.py --root ~/tools/zeo --no-fetch
    python check_toolkit_version.py --remote-version 0.25.0

Reads the clone's plugin version, fetches the remote (skip with
--no-fetch), and compares HEAD against the upstream default branch.
Exits 1 when the clone is behind upstream (commits or version) or when
HEAD is older than --max-age-days; exits 2 when the root is not a
toolkit clone. Sites run this at session start so process improvements
actually reach them (PLAYBOOK: the toolkit repo is the single source
of process).
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from seo_content_forge.version_check import (
    behind_ahead,
    head_age_days,
    local_version,
    parse_version,
    upstream_ref,
    upstream_version,
)
from seo_content_forge.version_check import (
    git as run_git,
)


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when the clone is current."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Toolkit clone root; defaults to this script's checkout.",
    )
    parser.add_argument(
        "--no-fetch",
        action="store_true",
        help="Compare against already-fetched remote refs only.",
    )
    parser.add_argument(
        "--remote-version",
        help="Known upstream version to compare against (skips git).",
    )
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=0,
        help="Also fail when HEAD is older than this many days (0 = off).",
    )
    args = parser.parse_args(argv)
    root = args.root.expanduser()

    version = local_version(root)
    if version is None:
        print(f"{root} is not a toolkit clone (no plugin manifest).", file=sys.stderr)
        return 2
    print(f"Local toolkit version: {version} ({root})")

    stale = False
    if args.remote_version:
        if parse_version(args.remote_version) > parse_version(version):
            print(f"STALE  upstream is {args.remote_version}; run git pull.")
            stale = True
        else:
            print("Version is current against the given upstream version.")
    else:
        if not args.no_fetch and run_git(root, "fetch", "--quiet", "origin") is None:
            print("note: git fetch failed; comparing against last-known remote.")
        ref = upstream_ref(root)
        if ref is None:
            print(
                "note: no upstream ref found; pass --remote-version to compare.",
                file=sys.stderr,
            )
        else:
            counts = behind_ahead(root, ref)
            if counts is None:
                print(f"note: could not compare HEAD with {ref}.", file=sys.stderr)
            else:
                behind, ahead = counts
                if behind:
                    print(f"STALE  {behind} commit(s) behind {ref}; run git pull.")
                    stale = True
                else:
                    print(f"Up to date with {ref}.")
                if ahead:
                    print(
                        f"note: {ahead} local commit(s) not upstream - sites do "
                        "not fork their own toolkit variants; upstream them."
                    )
            remote = upstream_version(root, ref)
            if remote and parse_version(remote) > parse_version(version):
                print(f"STALE  upstream plugin version is {remote}.")
                stale = True

    if args.max_age_days:
        age = head_age_days(root, date.today())
        if age is not None and age > args.max_age_days:
            print(f"STALE  HEAD is {age} days old (limit {args.max_age_days}).")
            stale = True

    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
