"""CLI to enforce the affiliate-link policy and find dead destinations.

Usage:
    python check_affiliate_links.py --dist dist --table affiliates.json
    python check_affiliate_links.py --dist dist --table affiliates.json --live

Offline: scans the build output for affiliate anchors (managed URLs
plus anything on the table's affiliate domains) and fails when one is
missing rel="sponsored" or is not registered in the central table.
With --live, also probes every managed URL over HTTP and fails on dead
destinations (redirects are followed; affiliate links redirect by
design). Exits 0 when clean, 1 on violations or dead links, 2 on bad
inputs. A missing table file means the site has no affiliate program:
the check passes with a note.
"""

from __future__ import annotations

import argparse
import http.client
import sys
import urllib.error
import urllib.request
from pathlib import Path

import orjson

from seo_content_forge.affiliates import AffiliateTable, parse_table, scan_dist


def probe(url: str, timeout: float = 20.0) -> int:
    """Final HTTP status for a URL, following redirects; 0 on failure."""
    try:
        request = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (compatible; seo-content-forge)"}
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return int(response.status)
    except urllib.error.HTTPError as exc:
        return int(exc.code)
    except (
        urllib.error.URLError,
        http.client.HTTPException,
        TimeoutError,
        OSError,
        ValueError,
    ):
        # Unreachable, malformed response, or an un-probeable URL: all
        # report as dead rather than aborting the remaining probes.
        return 0


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when the affiliate policy holds."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", required=True, type=Path)
    parser.add_argument(
        "--table",
        type=Path,
        default=Path("affiliates.json"),
        help="Central affiliate table (default: affiliates.json).",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Also probe every managed URL for dead destinations.",
    )
    args = parser.parse_args(argv)

    if not args.dist.is_dir():
        print(f"{args.dist} is not a directory", file=sys.stderr)
        return 2
    if not args.table.is_file():
        print(f"No affiliate table at {args.table}; nothing to check.")
        return 0
    try:
        table: AffiliateTable = parse_table(orjson.loads(args.table.read_bytes()))
    except (ValueError, orjson.JSONDecodeError) as exc:
        print(f"error: {args.table}: {exc}", file=sys.stderr)
        return 2

    failed = False
    violations = scan_dist(args.dist, table)
    for violation in violations:
        if violation.problem == "missing-rel":
            print(
                f'FAIL missing rel="sponsored": {violation.href} '
                f"(on {violation.page})"
            )
        else:
            print(
                f"FAIL not in {args.table.name}: {violation.href} "
                f"(on {violation.page})"
            )
    failed = bool(violations)

    if args.live:
        for link in table.links:
            status = probe(link.url)
            ok = 200 <= status < 400
            label = link.merchant or link.link_id
            print(f"{'ok  ' if ok else 'DEAD'} {link.link_id} ({label}) HTTP {status}")
            failed = failed or not ok

    if failed:
        print(
            "Fix: register every affiliate URL in the table, add "
            'rel="sponsored" (the AffiliateLink component does both), '
            "and replace dead destinations.",
            file=sys.stderr,
        )
        return 1
    print(f"Affiliate policy holds ({len(table.links)} managed link(s)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
