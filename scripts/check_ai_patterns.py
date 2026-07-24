"""CLI to lint an article for AI-tell writing patterns.

Usage:
    python check_ai_patterns.py --article draft.md

Flags banned formulaic phrases (errors) and structural fingerprints such
as repeated sentence openers and uniform paragraph lengths (warnings).
Exits 1 on any banned phrase, making "humanized" a verifiable state in
the publish pipeline rather than an opinion.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from seo_content_forge.ai_patterns import analyze


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when no banned phrase is present."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--article", required=True, type=Path, help="Article markdown file."
    )
    args = parser.parse_args(argv)

    report = analyze(args.article.read_text(encoding="utf-8"))

    for finding in report.findings:
        print(f'line {finding.line}: banned phrase "{finding.phrase}"')
        print(f"    {finding.context}")
    for warning in report.warnings:
        print(f"warning: {warning}")

    if not report.passed:
        print(
            f"\n{len(report.findings)} banned phrase(s): rewrite before "
            "publishing (see the humanize-content skill).",
            file=sys.stderr,
        )
        return 1
    print(
        "No AI-tell phrases found." + (" Review warnings." if report.warnings else "")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
