"""CLI to score a site's agent-readiness (isitagentready.com style).

Usage:
    python check_agent_ready.py --url https://example.com

Probes robots.txt, llms.txt, the sitemap, markdown content negotiation,
and the homepage HTML, then prints a categorized pass/fail report with a
concrete fix for every failing check. Exits non-zero when the score is
below ``--min-score`` (default 60), so it can gate a pipeline.
"""

from __future__ import annotations

import argparse
import re
import sys
from urllib.parse import urljoin

from seo_content_forge.agent_ready import (
    Check,
    analyze_html,
    analyze_robots,
    discovery_checks,
    presence_checks,
    summarize,
)
from seo_content_forge.fetch import fetch


def collect_checks(base_url: str) -> list[Check]:
    """Run all probes against ``base_url`` and return the checks.

    Args:
        base_url: Site root URL, e.g. ``https://example.com``.

    Returns:
        All agent-readiness checks across categories.
    """
    base = base_url if base_url.endswith("/") else base_url + "/"

    robots = fetch(urljoin(base, "robots.txt"))
    robots_text = robots.text if robots.ok else None

    sitemap_url = urljoin(base, "sitemap.xml")
    if robots_text:
        match = re.search(r"(?im)^\s*sitemap\s*:\s*(\S+)", robots_text)
        if match:
            sitemap_url = match.group(1)

    llms = fetch(urljoin(base, "llms.txt"))
    sitemap = fetch(sitemap_url)
    markdown_probe = fetch(base, accept="text/markdown")
    homepage = fetch(base)
    api_catalog = fetch(urljoin(base, ".well-known/api-catalog"))

    checks = analyze_robots(robots_text)
    checks += presence_checks(
        llms_txt_found=llms.ok,
        sitemap_found=sitemap.ok,
        markdown_negotiation=markdown_probe.ok
        and "markdown" in markdown_probe.content_type,
    )
    checks += discovery_checks(
        homepage.link_header if homepage.ok else None, api_catalog.ok
    )
    checks += analyze_html(homepage.text if homepage.ok else "")
    return checks


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when the score meets the threshold."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="Site root URL.")
    parser.add_argument(
        "--min-score",
        type=int,
        default=60,
        help="Minimum passing score, 0-100 (default 60).",
    )
    args = parser.parse_args(argv)

    checks = collect_checks(args.url)
    passed, total, score = summarize(checks)

    current_category = ""
    for check in sorted(checks, key=lambda item: item.category):
        if check.category != current_category:
            current_category = check.category
            print(f"\n[{current_category}]")
        status = "PASS" if check.passed else "FAIL"
        print(f"  {status}  {check.check_id}: {check.detail}")
        if check.fix:
            print(f"        fix: {check.fix}")

    print(f"\nAgent-readiness score: {score}/100 ({passed}/{total} checks passed)")
    if score < args.min_score:
        print(f"Below threshold {args.min_score}.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
