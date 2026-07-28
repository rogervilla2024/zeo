"""CLI to build one HTML dashboard from many sites' seo_report histories.

Usage:
    python fleet_report.py --scan ~/sites --output fleet-report.html
    python fleet_report.py --history blog=~/sites/blog/.seo-history.json \
        --history docs=~/sites/docs/.seo-history.json

Collects the ``.seo-history.json`` files that seo_report.py maintains
(one per site), prints a terminal summary, and writes a single
self-contained HTML report for the whole portfolio. Exits 1 when any
site's latest run has a failing gate, so the fleet view can gate a
pipeline the same way the per-site gates do.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import orjson

from seo_content_forge.fleet import (
    SiteReport,
    build_html,
    discover,
    maintenance_order,
    site_report,
)


def _parse_history_arg(value: str) -> tuple[str, Path]:
    """Split a ``name=path`` argument; the name defaults to the parent dir."""
    if "=" in value:
        name, _, raw = value.partition("=")
        return name, Path(raw).expanduser()
    path = Path(value).expanduser()
    return path.parent.name or path.stem, path


def load_reports(entries: dict[str, Path]) -> tuple[list[SiteReport], list[str]]:
    """Load every history file, returning reports and per-site errors.

    Args:
        entries: Site name to ``.seo-history.json`` path.

    Returns:
        The reports that loaded, and error lines for those that did not.
    """
    reports: list[SiteReport] = []
    errors: list[str] = []
    for name, path in entries.items():
        try:
            runs = orjson.loads(path.read_bytes())
            if not isinstance(runs, list):
                raise ValueError("history is not a list of runs")
            reports.append(site_report(name, runs))
        except (OSError, ValueError, orjson.JSONDecodeError) as exc:
            errors.append(f"{name}: {exc}")
    return reports, errors


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when every site is fully green."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scan",
        type=Path,
        help="Directory with one subdirectory per site; picks up each "
        "<site>/.seo-history.json.",
    )
    parser.add_argument(
        "--history",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="Add one history file explicitly (repeatable).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("fleet-report.html"),
        help="Where to write the HTML report.",
    )
    parser.add_argument("--title", default="Fleet SEO report")
    args = parser.parse_args(argv)

    entries: dict[str, Path] = {}
    if args.scan:
        entries.update(discover(args.scan.expanduser()))
    for raw in args.history:
        name, path = _parse_history_arg(raw)
        entries[name] = path
    if not entries:
        print("No history files found; pass --scan or --history.", file=sys.stderr)
        return 2

    reports, errors = load_reports(entries)
    for line in errors:
        print(f"SKIP {line}", file=sys.stderr)
    if not reports:
        print("No usable history files.", file=sys.stderr)
        return 2

    for report in sorted(reports, key=lambda r: r.name):
        failing = sorted(gate for gate, ok in report.gates.items() if not ok)
        status = "green" if report.is_green else f"failing: {', '.join(failing)}"
        print(f"{report.name:24} {report.score}/{report.total}  {status}")

    ranked = maintenance_order(reports)
    if ranked:
        print("\nMaintenance order (regressions first):")
        for position, (report, reason) in enumerate(ranked, start=1):
            print(f"  {position}. {report.name}  {reason}")

    args.output.write_text(build_html(reports, title=args.title), encoding="utf-8")
    print(f"\nReport written: {args.output}")
    return 0 if all(report.is_green for report in reports) and not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
