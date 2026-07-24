"""CLI to find the best open-source Astro themes for a niche.

Usage:
    python find_theme.py --niche "islamic knowledge base" --keywords blog,docs
    python find_theme.py --niche "coffee gear reviews" --top 5 --json out.json

Sweeps GitHub for repositories tagged astro-theme / astro-template
(hundreds of candidates in a few requests), hard-filters by license
(MIT/Apache/BSD family), activity (pushed within 18 months), and
traction (default 50+ stars), then ranks by niche keyword match, stars,
and freshness. Set GITHUB_TOKEN in the environment for a higher rate
limit; anonymous works for occasional runs.
"""

from __future__ import annotations

import argparse
import os
import sys
import urllib.parse
from pathlib import Path

import orjson

from seo_content_forge.fetch import fetch
from seo_content_forge.theme_search import (
    ThemeCandidate,
    parse_search_items,
    rank,
    utcnow,
)

_API = "https://api.github.com/search/repositories"
_TOPICS = ("astro-theme", "astro-template")


def _search(topic: str, pages: int) -> list[ThemeCandidate]:
    """Fetch up to ``pages`` pages of 100 results for one topic."""
    token = os.environ.get("GITHUB_TOKEN", "")
    candidates: list[ThemeCandidate] = []
    for page in range(1, pages + 1):
        params = urllib.parse.urlencode(
            {"q": f"topic:{topic}", "sort": "stars", "per_page": 100, "page": page}
        )
        result = fetch(
            f"{_API}?{params}",
            accept="application/vnd.github+json",
            headers={"Authorization": f"Bearer {token}"} if token else None,
        )
        if not result.ok:
            print(f"GitHub search failed (HTTP {result.status})", file=sys.stderr)
            break
        payload = orjson.loads(result.text)
        items = payload.get("items", [])
        if not isinstance(items, list) or not items:
            break
        candidates.extend(parse_search_items(items))
    return candidates


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when at least one theme is found."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--niche",
        required=True,
        help="Niche description in ENGLISH (theme metadata is English; "
        "translate first and prefer type words like blog/magazine/docs).",
    )
    parser.add_argument(
        "--keywords",
        default="",
        help="Extra comma-separated type words (blog,magazine,docs,review).",
    )
    parser.add_argument("--top", type=int, default=8, help="Finalists to show.")
    parser.add_argument("--min-stars", type=int, default=50)
    parser.add_argument(
        "--pages", type=int, default=3, help="Search pages per topic (100 each)."
    )
    parser.add_argument("--json", type=Path, help="Also write finalists as JSON.")
    args = parser.parse_args(argv)

    keywords = [word for word in args.niche.lower().split() if len(word) > 2]
    keywords += [
        word.strip().lower() for word in args.keywords.split(",") if word.strip()
    ]

    seen: dict[str, ThemeCandidate] = {}
    for topic in _TOPICS:
        for candidate in _search(topic, args.pages):
            seen.setdefault(candidate.full_name, candidate)
    print(f"Swept {len(seen)} unique candidate repositories.")

    finalists = rank(
        list(seen.values()),
        keywords,
        now=utcnow(),
        top=args.top,
        min_stars=args.min_stars,
    )
    if not finalists:
        print("No theme passed the filters; lower --min-stars.", file=sys.stderr)
        return 1

    for candidate, value in finalists:
        print(
            f"\n{value:6.1f}  {candidate.full_name}  "
            f"({candidate.stars} stars, {candidate.license_id})"
        )
        print(f"        {candidate.description[:100]}")
        print(
            f"        {candidate.url}"
            + (f"  demo: {candidate.homepage}" if candidate.homepage else "")
        )

    if args.json:
        args.json.write_bytes(
            orjson.dumps(
                [
                    {
                        "full_name": candidate.full_name,
                        "score": value,
                        "stars": candidate.stars,
                        "license": candidate.license_id,
                        "url": candidate.url,
                        "homepage": candidate.homepage,
                        "description": candidate.description,
                    }
                    for candidate, value in finalists
                ],
                option=orjson.OPT_INDENT_2,
            )
        )
        print(f"\nWrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
