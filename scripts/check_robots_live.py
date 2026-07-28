"""CLI live gate: the served robots.txt has an unambiguous policy.

Usage:
    python check_robots_live.py --url https://example.com

Fetches <url>/robots.txt as a crawler would see it and fails when any
user-agent carries both ``Allow: /`` and ``Disallow: /`` - the
signature of a CDN-managed robots block (e.g. Cloudflare's AI
Scrapers & Crawlers feature) fighting the site's own AI-ready rules.
robots.txt in the repository cannot catch this: the conflict only
exists in what the edge actually serves. Exits 1 on conflicts, 2 when
robots.txt cannot be fetched.
"""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request

from seo_content_forge.fetch import decode_body
from seo_content_forge.robots_live import find_conflicts


def fetch_robots(base_url: str) -> str | None:
    """Fetch <base>/robots.txt; None when it cannot be retrieved."""
    url = base_url.rstrip("/") + "/robots.txt"
    request = urllib.request.Request(
        url, headers={"User-Agent": "zeo-robots-check/1.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            content_type = response.headers.get("Content-Type", "")
            return decode_body(response.read(), content_type)
    except (urllib.error.URLError, OSError, ValueError):
        return None


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when the served policy is unambiguous."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="Deployed site URL.")
    args = parser.parse_args(argv)

    text = fetch_robots(args.url)
    if text is None:
        print(f"could not fetch robots.txt from {args.url}", file=sys.stderr)
        return 2

    problems = find_conflicts(text)
    for problem in problems:
        print(f"ROBOTS {problem}")
    if problems:
        print(f"\n{len(problems)} conflicting agent(s) in the served robots.txt.")
        return 1
    print("OK: served robots.txt policy is unambiguous.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
