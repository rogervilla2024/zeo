"""CLI to run the full gate battery and emit a score card.

Usage:
    python seo_report.py --dist dist --history .seo-history.json
    python seo_report.py --dist dist --live https://example.com

Runs every offline checker against the build output - plus the live
gates (agent-readiness, canonical host) against the deployed site when
--live is given - prints a one-page pass/fail card, appends the result
to a JSON history file, and shows the delta against the previous run.
Exits 1 when any gate fails.
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
    ("meta-quality", ["check_meta_quality.py", "--dist", "{dist}"]),
    ("image-attrs", ["check_image_attrs.py", "--dist", "{dist}"]),
)
# Source gates enabled automatically at site roots (dist next to
# src/content/blog/): each reads the content collection, not dist.
SOURCE_GATES: tuple[tuple[str, str], ...] = (
    ("article-images", "check_article_images.py"),
    ("internal-links", "check_internal_links.py"),
    ("category", "check_article_categories.py"),
)
LIVE_GATES: tuple[tuple[str, list[str]], ...] = (
    ("agent-ready", ["check_agent_ready.py", "--url", "{live}"]),
    ("canonical-host", ["check_canonical_host.py", "--domain", "{live}"]),
)


def gate_commands(
    dist: Path, live_url: str | None = None
) -> list[tuple[str, list[str]]]:
    """Resolve the gate command lines for a run.

    Args:
        dist: Build output directory substituted into the offline
            gates.
        live_url: Deployed site URL; adds the live gates when given.

    Returns:
        ``(gate name, argv)`` pairs in run order (offline first).
    """
    # The gate subprocesses run with cwd=scripts/, so a relative --dist
    # must be resolved against the invoker's cwd first.
    resolved_dist = dist.resolve()
    resolved = str(resolved_dist)
    commands = [
        (name, [part.replace("{dist}", resolved) for part in template])
        for name, template in GATES
    ]
    # The source gates read the content collection, not dist: built
    # HTML cannot reveal an image, link, or category that was never
    # added. Auto-enabled whenever the site root (dist's parent) has
    # the golden content layout, so they run without anyone
    # remembering a new flag.
    site_root = resolved_dist.parent
    content = site_root / "src" / "content" / "blog"
    if content.is_dir():
        config_file = site_root / "site.config.json"
        for name, script in SOURCE_GATES:
            command = [script, "--content", str(content)]
            if config_file.is_file():
                command += ["--config", str(config_file)]
            commands.append((name, command))
    if live_url:
        commands += [
            (name, [part.replace("{live}", live_url) for part in template])
            for name, template in LIVE_GATES
        ]
    return commands


def run_gates(dist: Path, live_url: str | None = None) -> dict[str, bool]:
    """Run every gate; True means passed."""
    results: dict[str, bool] = {}
    for name, command in gate_commands(dist, live_url):
        completed = subprocess.run(
            [sys.executable] + command, capture_output=True, cwd=Path(__file__).parent
        )
        results[name] = completed.returncode == 0
    return results


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when every gate passes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", required=True, type=Path)
    parser.add_argument("--history", type=Path, help="JSON file to append results to.")
    parser.add_argument(
        "--live",
        metavar="URL",
        help="Deployed site URL; also runs the live gates "
        "(agent-ready, canonical-host).",
    )
    args = parser.parse_args(argv)

    if not args.dist.is_dir():
        print(f"{args.dist} is not a directory", file=sys.stderr)
        return 2

    results = run_gates(args.dist, args.live)
    passed = sum(results.values())
    print("SEO score card")
    print("=" * 30)
    for name, ok in results.items():
        print(f"{'PASS' if ok else 'FAIL':4}  {name}")
    if args.live:
        offline_count = len(results) - len(LIVE_GATES)
        print(
            f"\nScore: {passed}/{len(results)} gates "
            f"({offline_count} offline + {len(LIVE_GATES)} live)"
        )
    else:
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
        record: dict[str, object] = {"results": results, "score": passed}
        if args.live:
            record["live_url"] = args.live
        history.append(record)
        args.history.write_bytes(orjson.dumps(history, option=orjson.OPT_INDENT_2))
        print(f"History updated: {args.history}")

    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
