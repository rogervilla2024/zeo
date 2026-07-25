"""CLI to verify one canonical host and short redirect chains.

Usage:
    python check_canonical_host.py --domain https://example.com

Probes the four host variants (http/https x www/apex) and verifies each
reaches the canonical URL within one redirect hop, all landing on the
same host. Catches www/apex splits and 301-to-301 chains.
"""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.parse
import urllib.request


def host_variants(domain: str) -> list[str]:
    """The four scheme/host combinations for a domain."""
    parsed = urllib.parse.urlparse(domain)
    host = parsed.netloc or parsed.path
    apex = host.removeprefix("www.")
    return [
        f"{scheme}://{prefix}{apex}/"
        for scheme in ("https", "http")
        for prefix in ("", "www.")
    ]


class _CountingRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self) -> None:
        self.hops = 0

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        self.hops += 1
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def probe(url: str) -> tuple[int, str, int]:
    """Return (status, final_url, redirect_hops) for a URL."""
    handler = _CountingRedirect()
    opener = urllib.request.build_opener(handler)
    try:
        with opener.open(url, timeout=20) as response:
            return int(response.status), str(response.url), handler.hops
    except urllib.error.URLError:
        return 0, "", handler.hops


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when the host is canonical and chains short."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domain", required=True, help="Canonical site URL.")
    parser.add_argument("--max-hops", type=int, default=1)
    args = parser.parse_args(argv)

    finals: set[str] = set()
    failed = False
    for url in host_variants(args.domain):
        status, final, hops = probe(url)
        ok = status == 200 and hops <= args.max_hops
        failed = failed or not ok
        print(
            f"{'ok  ' if ok else 'FAIL'} {url} -> {final or 'unreachable'} "
            f"({hops} hop(s), HTTP {status})"
        )
        if final:
            finals.add(urllib.parse.urlparse(final).netloc)

    if len(finals) > 1:
        print(f"FAIL multiple final hosts: {sorted(finals)}", file=sys.stderr)
        failed = True
    if failed:
        print(
            "Fix redirects so every variant reaches one canonical host "
            "in a single hop.",
            file=sys.stderr,
        )
        return 1
    print("One canonical host, short chains.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
