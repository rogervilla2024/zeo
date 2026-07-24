"""CLI to run PageSpeed Insights and report Core Web Vitals.

Usage:
    python check_pagespeed.py --url https://example.com/page
    python check_pagespeed.py --url https://example.com --strategy desktop

Calls the public PageSpeed Insights v5 API. Works without a key for light
use; set PAGESPEED_API_KEY in the environment (loaded from .env, never
hardcoded) for higher quotas. Exits non-zero when the performance score
is below ``--min-score`` (default 50), so it can gate a pipeline.
"""

from __future__ import annotations

import argparse
import os
import sys
import urllib.parse

import orjson

from seo_content_forge.fetch import fetch
from seo_content_forge.pagespeed import parse_report

_API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when the score meets the threshold."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="Page URL to test.")
    parser.add_argument(
        "--strategy",
        choices=("mobile", "desktop"),
        default="mobile",
        help="Analysis strategy (default mobile; Google indexes mobile-first).",
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=50,
        help="Minimum passing Lighthouse performance score (default 50).",
    )
    args = parser.parse_args(argv)

    params: dict[str, str] = {
        "url": args.url,
        "strategy": args.strategy,
        "category": "performance",
    }
    api_key = os.environ.get("PAGESPEED_API_KEY")
    if api_key:
        params["key"] = api_key
    # The key must never be logged; only the target URL is printed.
    print(f"Running PageSpeed Insights ({args.strategy}) for {args.url} ...")

    result = fetch(f"{_API}?{urllib.parse.urlencode(params)}", timeout=120.0)
    if not result.ok:
        print(f"PageSpeed API request failed (HTTP {result.status})", file=sys.stderr)
        return 2

    report = parse_report(orjson.loads(result.text))

    if report.performance_score is not None:
        print(f"\nLighthouse performance score: {report.performance_score}/100")
    if report.field_data:
        print("Field data (real users, 28 days):")
        for metric, category in report.field_data.items():
            print(f"  {metric}: {category}")
        verdict = report.passes_cwv
        print(f"  Core Web Vitals assessment: {'PASS' if verdict else 'FAIL'}")
    else:
        print("No field data (URL not in CrUX); lab data only.")
    if report.lab_metrics:
        print("Lab metrics:")
        for metric, value in report.lab_metrics.items():
            print(f"  {metric}: {value}")
    if report.opportunities:
        print("Top opportunities (estimated savings):")
        for opportunity in report.opportunities[:8]:
            print(f"  {opportunity.savings_ms:>7.0f} ms  {opportunity.title}")

    score = report.performance_score
    if score is not None and score < args.min_score:
        print(f"\nBelow threshold {args.min_score}.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
