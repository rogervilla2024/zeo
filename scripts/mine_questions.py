"""CLI to mine real user questions for a topic from autocomplete.

Usage:
    python mine_questions.py --seed "french press" --lang en
    python mine_questions.py --seed "kahve demleme" --lang tr --json out.json

Expands the seed with question prefixes, queries Google's public
autocomplete endpoint, and prints a deduplicated on-topic question
list. Feed the output to build-topic-clusters (launch pack topics) and
write-article (FAQ blocks answering real queries).
"""

from __future__ import annotations

import argparse
import sys
import urllib.parse
from pathlib import Path

import orjson

from seo_content_forge.fetch import fetch
from seo_content_forge.questions import (
    dedupe_questions,
    expand_queries,
    parse_suggestions,
)

_API = "https://suggestqueries.google.com/complete/search"


def suggest_url(query: str, lang: str) -> str:
    """The autocomplete request URL for one query.

    ``ie``/``oe`` pin both directions to UTF-8: without ``oe=utf-8``
    the endpoint answers some languages in a legacy charset (e.g.
    ISO-8859-9 for ``hl=tr``), which corrupts every non-ASCII
    character downstream.

    Args:
        query: The expanded autocomplete query.
        lang: Interface language code, e.g. ``tr``.

    Returns:
        The full request URL.
    """
    params = urllib.parse.urlencode(
        {
            "client": "firefox",
            "hl": lang,
            "ie": "utf-8",
            "oe": "utf-8",
            "q": query,
        }
    )
    return f"{_API}?{params}"


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when at least one question was found."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", required=True, help="Topic or keyword.")
    parser.add_argument("--lang", default="en", help="Language code (en, tr, ...).")
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--json", type=Path, help="Also write the list as JSON.")
    args = parser.parse_args(argv)

    batches: list[list[str]] = []
    for query in expand_queries(args.seed, args.lang):
        result = fetch(suggest_url(query, args.lang))
        if result.ok:
            batches.append(parse_suggestions(result.text))

    questions = dedupe_questions(batches, args.seed, limit=args.limit)
    if not questions:
        print("No suggestions returned; check network or seed.", file=sys.stderr)
        return 1
    for question in questions:
        print(question)
    if args.json:
        args.json.write_bytes(orjson.dumps(questions, option=orjson.OPT_INDENT_2))
        print(f"\nWrote {args.json}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
