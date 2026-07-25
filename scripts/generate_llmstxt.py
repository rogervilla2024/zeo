"""CLI to generate an ``llms.txt`` file from a JSON site config.

Usage:
    python generate_llmstxt.py --input site.json --output llms.txt

The ``--input`` file describes the site:

    {
      "site_name": "Example",
      "summary": "What the site is, in one or two sentences.",
      "details": "Optional extra markdown paragraphs.",
      "sections": {
        "Docs": [
          {"title": "Quick start", "url": "https://example.com/start.md",
           "note": "Setup in five minutes"}
        ],
        "Optional": [
          {"title": "Changelog", "url": "https://example.com/changelog.md"}
        ]
      }
    }
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import orjson

from seo_content_forge.llmstxt import LinkEntry, build_llms_txt, looks_mojibake


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns a process exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="JSON site config.")
    parser.add_argument(
        "--output", type=Path, help="Write llms.txt here instead of stdout."
    )
    args = parser.parse_args(argv)

    config = orjson.loads(args.input.read_bytes())
    sections = {
        str(title): [
            LinkEntry(
                title=str(entry["title"]),
                url=str(entry["url"]),
                note=entry.get("note"),
            )
            for entry in entries
        ]
        for title, entries in dict(config["sections"]).items()
    }
    content = build_llms_txt(
        site_name=str(config["site_name"]),
        summary=str(config["summary"]),
        sections=sections,
        details=config.get("details"),
    )

    if looks_mojibake(content):
        print(
            "Input looks double-encoded (mojibake such as A-tilde pairs "
            "instead of accented letters). Regenerate the source JSON as "
            "UTF-8 - on Windows, never create it via shell redirection; "
            "write it from Python with encoding=utf-8 or an editor tool.",
            file=sys.stderr,
        )
        return 1

    if args.output:
        args.output.write_text(content, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        sys.stdout.write(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
