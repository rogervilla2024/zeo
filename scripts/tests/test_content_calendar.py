"""Tests for the content queue parser, week planner, and calendar CLI."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from content_calendar import main
from seo_content_forge.planner import (
    QueueItem,
    parse_queue,
    render_markdown,
    schedule,
    week_capacity,
)


def test_parse_queue_accepts_wrapper_and_bare_list() -> None:
    entry = {"topic": "brew ratios", "type": "refresh", "priority": 1}
    assert parse_queue([entry])[0].item_type == "refresh"
    items = parse_queue({"queue": [entry]})
    assert items[0].topic == "brew ratios"
    assert items[0].priority == 1


def test_parse_queue_rejects_bad_payloads() -> None:
    with pytest.raises(ValueError, match="must be a list"):
        parse_queue({"queue": "nope"})
    with pytest.raises(ValueError, match="needs a topic"):
        parse_queue([{"priority": 1}])
    with pytest.raises(ValueError, match="unknown type"):
        parse_queue([{"topic": "x", "type": "update"}])
    with pytest.raises(ValueError, match="unknown status"):
        parse_queue([{"topic": "x", "status": "later"}])
    with pytest.raises(ValueError, match="priority must be an integer"):
        parse_queue([{"topic": "x", "priority": "high"}])


def test_week_capacity_ramp_is_a_ceiling() -> None:
    ramp = [1, 2, 30]
    assert week_capacity(0, 5, ramp) == 1
    assert week_capacity(1, 5, ramp) == 2
    assert week_capacity(2, 5, ramp) == 5
    assert week_capacity(3, 5, ramp) == 5
    assert week_capacity(0, 5, []) == 5


def test_schedule_by_priority_within_capacity() -> None:
    items = [
        QueueItem(topic="late", priority=9),
        QueueItem(topic="first", priority=1),
        QueueItem(topic="done", status="done"),
        QueueItem(topic="second", priority=2),
    ]
    plans, overflow = schedule(items, date(2026, 8, 3), 2, [1], weeks=2)
    assert [item.topic for item in plans[0].items] == ["first"]
    assert [item.topic for item in plans[1].items] == ["second", "late"]
    assert overflow == []
    assert plans[0].items[0].status == "scheduled"
    assert plans[0].items[0].week_of == "2026-08-03"
    assert plans[1].start == date(2026, 8, 10)
    assert items[2].status == "done"


def test_schedule_overflow_beyond_horizon() -> None:
    items = [QueueItem(topic=f"t{i}") for i in range(3)]
    plans, overflow = schedule(items, date(2026, 8, 3), 1, [], weeks=2)
    assert len(plans[0].items) == 1 and len(plans[1].items) == 1
    assert [item.topic for item in overflow] == ["t2"]
    assert overflow[0].status == "queued"


def test_render_markdown_lists_weeks_and_overflow() -> None:
    items = [
        QueueItem(topic="a", priority=1),
        QueueItem(topic="b", item_type="refresh", url="/blog/old/"),
        QueueItem(topic="c"),
    ]
    plans, overflow = schedule(items, date(2026, 8, 3), 2, [], weeks=1)
    text = render_markdown(plans, overflow)
    assert "## Week 1 - 2026-08-03 (2/2 slots)" in text
    assert "- [new] a" in text
    assert "- [refresh] b - /blog/old/" in text
    assert "## Overflow (1 items beyond the horizon)" in text


def test_main_apply_writes_assignments_back(tmp_path: Path) -> None:
    queue = tmp_path / "content-queue.json"
    queue.write_text(
        json.dumps(
            {
                "queue": [
                    {"topic": "a", "priority": 1},
                    {"topic": "b", "priority": 2},
                ]
            }
        )
    )
    config = tmp_path / "site.config.json"
    config.write_text(
        json.dumps({"content": {"articles_per_week": 1, "weekly_ramp": [1]}})
    )
    output = tmp_path / "calendar.md"
    code = main(
        [
            "--queue",
            str(queue),
            "--config",
            str(config),
            "--start",
            "2026-08-03",
            "--apply",
            "--output",
            str(output),
        ]
    )
    assert code == 0
    saved = json.loads(queue.read_text())
    assert saved["queue"][0]["status"] == "scheduled"
    assert saved["queue"][0]["week_of"] == "2026-08-03"
    assert saved["queue"][1]["week_of"] == "2026-08-10"
    assert "# Content calendar" in output.read_text()


def test_main_rejects_malformed_queue(tmp_path: Path) -> None:
    queue = tmp_path / "content-queue.json"
    queue.write_text(json.dumps([{"topic": ""}]))
    assert main(["--queue", str(queue), "--start", "2026-08-03"]) == 2
