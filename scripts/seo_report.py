"""CLI to run the full offline gate battery and emit a score card.

Usage:
    python seo_report.py --dist dist --history .seo-history.json

Runs every offline checker against the build output, prints a one-page
pass/fail card, appends the result to a JSON history file, and shows
the delta against the previous run. Exits 1 when any gate fails.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import orjson

GATES: tuple[tuple[str, list[str]], ...] = (
    ("rich-results", ["check_rich_results.py", "--file", "{dist}/index.html"]),
    ("js-budget", ["check_js_budget.py", "--dist", "{dist}"]),
    ("broken-links", ["check_broken_links.py", "--dist", "{dist}"]),
    ("media-budget", ["check_media_budget.py", "--dist", "{dist}"]),
)


def run_gates(dist: Path) -> dict[str, bool]:
    """Run every offline gate; True means passed."""
    results: dict[str, bool] = {}
    for name, template in GATES:
        command = [sys.executable] + [
            part.replace("{dist}", str(dist)) for part in template
        ]
        completed = subprocess.run(
            command, capture_output=True, cwd=Path(__file__).parent
        )
        results[name] = completed.returncode == 0
    return results


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when every gate passes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", required=True, type=Path)
    parser.add_argument("--history", type=Path, help="JSON file to append results to.")
    args = parser.parse_args(argv)

    results = run_gates(args.dist)
    passed = sum(results.values())
    print("SEO score card")
    print("=" * 30)
    for name, ok in results.items():
        print(f"{'PASS' if ok else 'FAIL':4}  {name}")
    print(f"\nScore: {passed}/{len(results)} offline gates")

    if args.history:
        history: list[dict[str, object]] = []
        if args.history.is_file():
            history = orjson.loads(args.history.read_bytes())
        if history:
            previous = history[-1].get("results", {})
            changed = [
                name
                for name, ok in results.items()
                if isinstance(previous, dict) and previous.get(name) not in (None, ok)
            ]
            if changed:
                print(f"Changed since last run: {', '.join(changed)}")
        history.append({"results": results, "score": passed})
        args.history.write_bytes(orjson.dumps(history, option=orjson.OPT_INDENT_2))
        print(f"History updated: {args.history}")

    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
