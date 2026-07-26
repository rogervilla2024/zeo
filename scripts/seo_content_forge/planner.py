"""Map the content queue onto dated weeks under the publishing rules.

The queue file (``content-queue.json``) is the site's single backlog of
planned work - new articles from the cluster roadmap and refresh items
for aging pages. This module assigns queued items to calendar weeks
without ever exceeding the pace the PLAYBOOK allows: the
``content.weekly_ramp`` ceiling for the first weeks and
``content.articles_per_week`` as the steady cadence. Publishing faster
than the ramp on a fresh domain matches Google's scaled-content-abuse
pattern, so the planner enforces it instead of trusting memory.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

VALID_TYPES = ("new", "refresh")
VALID_STATUSES = ("queued", "scheduled", "done")


@dataclass(slots=True)
class QueueItem:
    """One planned piece of work in content-queue.json.

    Args:
        topic: Working title or topic of the article.
        item_type: ``"new"`` for a fresh article, ``"refresh"`` for an
            update of an existing page.
        priority: Lower schedules earlier; ties keep queue order.
        status: ``"queued"``, ``"scheduled"``, or ``"done"``.
        keyword: Primary target keyword, if already chosen.
        url: Existing page URL (refresh items).
        source: Where the item came from (cluster-map, refresh-queue,
            manual).
        week_of: ISO date of the scheduled week's first day, set by the
            planner.
    """

    topic: str
    item_type: str = "new"
    priority: int = 100
    status: str = "queued"
    keyword: str = ""
    url: str = ""
    source: str = "manual"
    week_of: str = ""

    def to_json(self) -> dict[str, object]:
        """Serialize for content-queue.json, dropping empty fields."""
        raw: dict[str, object] = {
            "topic": self.topic,
            "type": self.item_type,
            "priority": self.priority,
            "status": self.status,
            "keyword": self.keyword,
            "url": self.url,
            "source": self.source,
            "week_of": self.week_of,
        }
        return {key: value for key, value in raw.items() if value != ""}


@dataclass(slots=True)
class WeekPlan:
    """One calendar week of scheduled work.

    Args:
        start: First day of the week.
        capacity: Maximum items this week may take.
        items: Items assigned to the week.
    """

    start: date
    capacity: int
    items: list[QueueItem] = field(default_factory=list)


def parse_queue(data: object) -> list[QueueItem]:
    """Parse the content-queue.json payload.

    Args:
        data: Parsed JSON; either ``{"queue": [...]}`` or a bare list.

    Returns:
        Queue items in file order.

    Raises:
        ValueError: On a malformed payload, unknown type, or unknown
            status.
    """
    raw = data.get("queue") if isinstance(data, dict) else data
    if not isinstance(raw, list):
        raise ValueError('content queue must be a list or {"queue": [...]}')
    items: list[QueueItem] = []
    for index, entry in enumerate(raw):
        if not isinstance(entry, dict) or not str(entry.get("topic", "")).strip():
            raise ValueError(f"queue item {index} needs a topic")
        raw_priority = entry.get("priority", 100)
        if not isinstance(raw_priority, int):
            raise ValueError(f"queue item {index}: priority must be an integer")
        item = QueueItem(
            topic=str(entry["topic"]),
            item_type=str(entry.get("type", "new")),
            priority=raw_priority,
            status=str(entry.get("status", "queued")),
            keyword=str(entry.get("keyword", "")),
            url=str(entry.get("url", "")),
            source=str(entry.get("source", "manual")),
            week_of=str(entry.get("week_of", "")),
        )
        if item.item_type not in VALID_TYPES:
            raise ValueError(f"queue item {index}: unknown type {item.item_type!r}")
        if item.status not in VALID_STATUSES:
            raise ValueError(f"queue item {index}: unknown status {item.status!r}")
        items.append(item)
    return items


def week_capacity(week_index: int, per_week: int, ramp: list[int]) -> int:
    """Publishing capacity for a week (0-based index from the start).

    The ramp is a ceiling for the first ``len(ramp)`` weeks; the steady
    cadence applies afterwards and is itself never exceeded early on.

    Args:
        week_index: 0 for the first planned week.
        per_week: Steady cadence (``content.articles_per_week``).
        ramp: Early-week ceilings (``content.weekly_ramp``).

    Returns:
        Maximum items for the week, never below zero.
    """
    capacity = min(per_week, ramp[week_index]) if week_index < len(ramp) else per_week
    return max(0, capacity)


def schedule(
    items: list[QueueItem],
    start: date,
    per_week: int,
    ramp: list[int],
    weeks: int,
) -> tuple[list[WeekPlan], list[QueueItem]]:
    """Assign queued items to weeks by priority, respecting capacity.

    Only items with status ``"queued"`` are placed; scheduled and done
    items are left untouched. Placed items get status ``"scheduled"``
    and their ``week_of`` date set.

    Args:
        items: The full queue (mutated in place for placed items).
        start: First day of week one.
        per_week: Steady cadence.
        ramp: Early-week ceilings.
        weeks: Planning horizon in weeks.

    Returns:
        The week plans and the queued items that did not fit.
    """
    plans = [
        WeekPlan(
            start=start + timedelta(weeks=index),
            capacity=week_capacity(index, per_week, ramp),
        )
        for index in range(weeks)
    ]
    pending = sorted(
        (item for item in items if item.status == "queued"),
        key=lambda item: item.priority,
    )
    overflow: list[QueueItem] = []
    plan_iter = iter(plans)
    current = next(plan_iter, None)
    for item in pending:
        while current is not None and len(current.items) >= current.capacity:
            current = next(plan_iter, None)
        if current is None:
            overflow.append(item)
            continue
        item.status = "scheduled"
        item.week_of = current.start.isoformat()
        current.items.append(item)
    return plans, overflow


def render_markdown(plans: list[WeekPlan], overflow: list[QueueItem]) -> str:
    """Render the schedule as a plain markdown calendar."""
    lines = ["# Content calendar", ""]
    for index, plan in enumerate(plans, start=1):
        lines.append(
            f"## Week {index} - {plan.start.isoformat()} "
            f"({len(plan.items)}/{plan.capacity} slots)"
        )
        if not plan.items:
            lines.append("- (open)")
        for item in plan.items:
            marker = "refresh" if item.item_type == "refresh" else "new"
            detail = f" - {item.url}" if item.url else ""
            lines.append(f"- [{marker}] {item.topic}{detail}")
        lines.append("")
    if overflow:
        lines.append(f"## Overflow ({len(overflow)} items beyond the horizon)")
        lines.extend(f"- {item.topic}" for item in overflow)
        lines.append("")
    return "\n".join(lines)
