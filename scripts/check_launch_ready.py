"""CLI: one-shot launch-readiness check for a golden-template site.

Usage:
    python check_launch_ready.py --root .

Run from (or pointed at) the site project root before going live -
the final step of the bootstrap-site checklist. Fails while any
template placeholder, missing asset, unfilled trust page, or short
launch content pack remains. Exits 1 with an itemized list of
blockers, 2 when the root has no site.config.json.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from seo_content_forge.launch import check_launch


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when the site is ready to launch."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Site project root (holds site.config.json).",
    )
    args = parser.parse_args(argv)

    problems = check_launch(args.root)
    if problems == ["site.config.json missing - is this a site root?"]:
        print(f"LAUNCH {problems[0]}")
        return 2
    for problem in problems:
        print(f"LAUNCH {problem}")
    if problems:
        print(f"\n{len(problems)} launch blocker(s).")
        return 1
    print("OK: no launch blockers found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
