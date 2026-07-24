"""CLI to build a schema.org JSON-LD block from a parameters file.

Usage:
    python build_jsonld.py --type article --input params.json
    python build_jsonld.py --type faq --input params.json --output faq.json

The ``--input`` file holds the keyword arguments for the chosen builder as
a JSON object. For builders that take tuple lists (``faq``, ``howto``,
``breadcrumb``), pass JSON arrays of two-element arrays.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import orjson

from seo_content_forge import jsonld


def _to_tuples(value: object) -> list[tuple[str, str]]:
    """Coerce a JSON array of two-element arrays into a list of tuples."""
    if not isinstance(value, list):
        raise ValueError("expected a JSON array of two-element arrays")
    return [(str(pair[0]), str(pair[1])) for pair in value]


def build(node_type: str, params: dict[str, object]) -> dict[str, object]:
    """Dispatch to the matching builder in :mod:`seo_content_forge.jsonld`.

    Args:
        node_type: One of the keys in :data:`jsonld.BUILDERS`.
        params: Keyword arguments for the builder.

    Returns:
        The JSON-LD node.

    Raises:
        ValueError: If ``node_type`` is unknown.
    """
    builder = jsonld.BUILDERS.get(node_type)
    if builder is None:
        raise ValueError(
            f"unknown type {node_type!r}; choose from {sorted(jsonld.BUILDERS)}"
        )

    if node_type in {"faq", "howto", "breadcrumb"}:
        key = {"faq": "questions", "howto": "steps", "breadcrumb": "items"}[node_type]
        params = {**params, key: _to_tuples(params[key])}

    node: dict[str, object] = builder(**params)
    return node


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns a process exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--type",
        required=True,
        choices=sorted(jsonld.BUILDERS),
        help="Rich-result type to build.",
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="JSON file of builder parameters.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write JSON-LD here instead of stdout.",
    )
    args = parser.parse_args(argv)

    params = orjson.loads(args.input.read_bytes())
    node = build(args.type, params)
    payload = orjson.dumps(node, option=orjson.OPT_INDENT_2)

    if args.output:
        args.output.write_bytes(payload)
    else:
        sys.stdout.buffer.write(payload + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
