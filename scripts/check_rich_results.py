"""CLI to test a page's structured data for rich-result eligibility.

Usage:
    python check_rich_results.py --url https://example.com/article
    python check_rich_results.py --file page.html

Extracts every JSON-LD block from the page, validates each node against
Google's required/recommended properties, and reports eligible types,
errors, and warnings. Exits non-zero on any blocking error so it can gate
a publishing pipeline. Google's hosted Rich Results Test remains the
final arbiter; this catches the failures before the page ships.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from seo_content_forge.fetch import fetch
from seo_content_forge.richresults import check_page


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when no blocking errors are found."""
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--url", help="Page URL to fetch and test.")
    source.add_argument("--file", type=Path, help="Local HTML file to test.")
    args = parser.parse_args(argv)

    if args.url:
        result = fetch(args.url)
        if not result.ok:
            print(f"Fetch failed (HTTP {result.status})", file=sys.stderr)
            return 2
        html = result.text
    else:
        html = args.file.read_text(encoding="utf-8")

    report = check_page(html)

    if not report.results and not report.parse_errors:
        print("No JSON-LD found: the page is ineligible for all rich results.")
        return 1

    for error in report.consistency_errors:
        print(f"CONSISTENCY  {error}")
    for error in report.parse_errors:
        print(f"PARSE ERROR  {error}")
    for result_item in report.results:
        status = "OK    " if result_item.is_valid else "FAILED"
        print(f"{status} [{result_item.node_type}]")
        for message in result_item.errors:
            print(f"    error: {message}")
        for message in result_item.warnings:
            print(f"    warning: {message}")

    eligible = report.eligible_types
    print(
        f"\nEligible types: {', '.join(eligible) if eligible else 'none'}"
        f" ({len(report.results)} nodes checked)"
    )
    print("Confirm with Google's Rich Results Test before publishing.")
    return 1 if report.has_blocking_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
