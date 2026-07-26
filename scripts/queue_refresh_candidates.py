"""CLI to queue articles not updated in months for refresh-content.

Usage:
    python queue_refresh_candidates.py --dist dist
    python queue_refresh_candidates.py --dist dist \
        --queue content-queue.json --apply

Scans the build output for pages whose Article JSON-LD declares a
dateModified (or datePublished) older than the cutoff (default 6
months), lists them oldest first, and with --apply appends them to
content-queue.json as type "refresh" items for the content-calendar
skill to schedule. Already queued or scheduled refresh items are not
duplicated. Exits 2 on bad inputs, otherwise 0.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

import orjson

from seo_content_forge.planner import QueueItem, parse_queue
from seo_content_forge.stale import find_stale


def merge_into_queue(
    items: list[QueueItem], candidates: list[QueueItem]
) -> tuple[list[QueueItem], int]:
    """Append candidates whose URL is not already pending in the queue.

    Args:
        items: Current queue content.
        candidates: Refresh items to add.

    Returns:
        The merged queue and how many candidates were actually added.
    """
    pending = {
        item.url
        for item in items
        if item.item_type == "refresh" and item.status in ("queued", "scheduled")
    }
    added = 0
    merged = list(items)
    for candidate in candidates:
        if candidate.url in pending:
            continue
        merged.append(candidate)
        pending.add(candidate.url)
        added += 1
    return merged, added


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns a process exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", required=True, type=Path)
    parser.add_argument(
        "--months", type=int, default=6, help="Staleness cutoff in months."
    )
    parser.add_argument(
        "--now",
        type=date.fromisoformat,
        default=None,
        help="Reference date (YYYY-MM-DD); defaults to today.",
    )
    parser.add_argument(
        "--queue",
        type=Path,
        default=Path("content-queue.json"),
        help="Queue file to merge into with --apply.",
    )
    parser.add_argument(
        "--priority",
        type=int,
        default=50,
        help="Priority for the queued refresh items (lower = earlier).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Append the candidates to the queue file.",
    )
    args = parser.parse_args(argv)

    if not args.dist.is_dir():
        print(f"{args.dist} is not a directory", file=sys.stderr)
        return 2

    reference = args.now or date.today()
    stale, warnings = find_stale(args.dist, reference, months=args.months)
    for warning in warnings:
        print(f"WARN {warning}", file=sys.stderr)

    if not stale:
        print(f"No articles older than {args.months} month(s). Nothing to queue.")
        return 0

    for article in stale:
        print(f"{article.days_old:5d} days  {article.modified[:10]}  {article.url}")
    print(f"\n{len(stale)} refresh candidate(s).")

    if not args.apply:
        print("Dry run; pass --apply to add them to the queue.")
        return 0

    items: list[QueueItem] = []
    if args.queue.is_file():
        try:
            items = parse_queue(orjson.loads(args.queue.read_bytes()))
        except (ValueError, orjson.JSONDecodeError) as exc:
            print(f"error: {args.queue}: {exc}", file=sys.stderr)
            return 2
    candidates = [
        QueueItem(
            topic=f"Refresh: {article.url}",
            item_type="refresh",
            priority=args.priority,
            url=article.url,
            source="refresh-queue",
        )
        for article in stale
    ]
    merged, added = merge_into_queue(items, candidates)
    payload = {"queue": [item.to_json() for item in merged]}
    args.queue.write_bytes(orjson.dumps(payload, option=orjson.OPT_INDENT_2))
    print(f"Added {added} item(s) to {args.queue} ({len(stale) - added} duplicate).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
