"""CLI to turn content-queue.json into a dated publishing calendar.

Usage:
    python content_calendar.py --queue content-queue.json \
        --config site.config.json --start 2026-08-03
    python content_calendar.py --queue content-queue.json \
        --config site.config.json --start 2026-08-03 --apply \
        --output content-calendar.md

Assigns queued items to weeks by priority, capping every week at the
pace the PLAYBOOK allows (content.weekly_ramp early, then
content.articles_per_week). Prints the calendar as markdown; --apply
writes the week assignments back into the queue file, --output saves
the markdown. Exits 2 on malformed inputs.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

import orjson

from seo_content_forge.planner import parse_queue, render_markdown, schedule


def _load_pace(config_path: Path | None) -> tuple[int, list[int]]:
    """Read (articles_per_week, weekly_ramp) from site.config.json."""
    per_week, ramp = 2, [10, 15, 20, 30]
    if config_path is None:
        return per_week, ramp
    config = orjson.loads(config_path.read_bytes())
    raw_content = config.get("content") if isinstance(config, dict) else None
    content = raw_content if isinstance(raw_content, dict) else {}
    raw_per_week = content.get("articles_per_week")
    if isinstance(raw_per_week, int) and raw_per_week > 0:
        per_week = raw_per_week
    raw_ramp = content.get("weekly_ramp")
    if isinstance(raw_ramp, list) and all(isinstance(n, int) for n in raw_ramp):
        ramp = list(raw_ramp)
    return per_week, ramp


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns a process exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", required=True, type=Path)
    parser.add_argument(
        "--config", type=Path, help="site.config.json for the pace rules."
    )
    parser.add_argument(
        "--start",
        type=date.fromisoformat,
        default=None,
        help="First day of week one (YYYY-MM-DD); defaults to today.",
    )
    parser.add_argument("--weeks", type=int, default=12, help="Planning horizon.")
    parser.add_argument(
        "--per-week", type=int, help="Override content.articles_per_week."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write week assignments back into the queue file.",
    )
    parser.add_argument("--output", type=Path, help="Also save the markdown here.")
    args = parser.parse_args(argv)

    try:
        items = parse_queue(orjson.loads(args.queue.read_bytes()))
        per_week, ramp = _load_pace(args.config)
    except (OSError, ValueError, orjson.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.per_week is not None:
        per_week = args.per_week

    start = args.start or date.today()
    plans, overflow = schedule(items, start, per_week, ramp, max(1, args.weeks))
    markdown = render_markdown(plans, overflow)
    print(markdown)

    if args.output:
        args.output.write_text(markdown, encoding="utf-8")
        print(f"Calendar written: {args.output}", file=sys.stderr)
    if args.apply:
        payload = {"queue": [item.to_json() for item in items]}
        args.queue.write_bytes(orjson.dumps(payload, option=orjson.OPT_INDENT_2))
        print(f"Queue updated: {args.queue}", file=sys.stderr)
    if overflow:
        print(
            f"{len(overflow)} item(s) beyond the {max(1, args.weeks)}-week "
            "horizon; extend --weeks or trim the queue.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
