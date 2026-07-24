"""CLI to check an article's originality against a content corpus.

Usage:
    python check_originality.py --article draft.md --corpus corpus.json
    python check_originality.py --article draft.md --corpus corpus.json \
        --threshold 0.10

The ``--corpus`` file is a JSON array of ``{"url": ..., "text": ...}``
documents: the site's already-published articles. Exits 1 when any
document's shingle similarity meets the threshold, so the publish
pipeline stops before shipping substantially-similar content.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import orjson

from seo_content_forge.originality import compare


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when the article clears the threshold."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--article", required=True, type=Path, help="Article markdown file."
    )
    parser.add_argument("--corpus", required=True, type=Path, help="Corpus JSON file.")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.15,
        help="Failing Jaccard similarity (default 0.15).",
    )
    parser.add_argument(
        "--shingle-size", type=int, default=8, help="Shingle length in words."
    )
    args = parser.parse_args(argv)

    corpus = {
        str(item["url"]): str(item["text"])
        for item in orjson.loads(args.corpus.read_bytes())
    }
    results = compare(
        args.article.read_text(encoding="utf-8"), corpus, k=args.shingle_size
    )

    if not results:
        print("No overlap with the corpus. Article is original by this measure.")
        return 0

    failed = False
    for result in results:
        status = "FAIL" if result.score >= args.threshold else "ok  "
        failed = failed or result.score >= args.threshold
        print(f"{status} {result.score:.3f}  {result.url}")
        for phrase in result.shared_phrases:
            print(f'         shared: "...{phrase}..."')

    if failed:
        print(
            f"\nSimilarity >= {args.threshold}: rewrite the overlapping "
            "sections before publishing.",
            file=sys.stderr,
        )
        return 1
    print("\nAll similarities below threshold.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
