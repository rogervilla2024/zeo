"""CLI to validate a JSON-LD file against rich-result requirements.

Usage:
    python validate_schema.py --input jsonld.json

Reads a JSON-LD object (or list of objects) and reports missing required
and recommended properties. Exits non-zero if any blocking error is found,
so it can gate a publishing pipeline.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import orjson

from seo_content_forge.validate import ValidationResult, validate


def _format(result: ValidationResult) -> str:
    """Render a single validation result as plain text lines."""
    lines = [f"[{result.node_type}] {'OK' if result.is_valid else 'FAILED'}"]
    lines.extend(f"  error: {message}" for message in result.errors)
    lines.extend(f"  warning: {message}" for message in result.warnings)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 when every node is valid, else 1."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="JSON-LD file to validate.",
    )
    args = parser.parse_args(argv)

    data = orjson.loads(args.input.read_bytes())
    results = validate(data)

    report = "\n".join(_format(result) for result in results)
    has_errors = any(not result.is_valid for result in results)
    stream = sys.stderr if has_errors else sys.stdout
    print(report, file=stream)
    return 1 if has_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
