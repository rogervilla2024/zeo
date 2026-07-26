---
name: content-calendar
description: Turn the site's content queue into a dated weekly publishing calendar that respects the weekly_ramp ceiling and articles_per_week cadence. Use when the user wants an editorial or content calendar, asks what to publish next or which article is due this week, wants to schedule the backlog, plan publishing dates, or connect the cluster roadmap to actual weeks.
---

# Content calendar

Binds the two halves of the publishing process together: the backlog
(`content-queue.json`) and the pace rules (`content.weekly_ramp` and
`content.articles_per_week` in site.config.json). The deterministic
planner does the date math; this skill keeps the queue honest and
drives the weekly loop from it.

## Inputs

- `site.config.json` (pace rules; single source of truth).
- `content-queue.json` at the site root - created here if missing.
- The prioritized roadmap from build-topic-clusters (first wave, next
  wave), and any refresh candidates.
- The start date (default: today) and planning horizon.

## The queue file

`content-queue.json` holds `{"queue": [...]}` where each item has:
`topic` (required), `type` (`new` or `refresh`), `priority` (lower
schedules earlier), `status` (`queued`, `scheduled`, `done`),
optional `keyword`, `url` (refresh items), `source`, and `week_of`
(set by the planner).

## Instructions

1. Build or update the queue. Seed `new` items from the
   build-topic-clusters roadmap (priority follows the roadmap wave;
   keyword from the cluster map). Add `refresh` items for decaying
   pages: `queue_refresh_candidates.py --dist dist --apply` queues
   every article not updated in 6 months, plus whatever Search
   Console data flags. Never delete `done` items - they are the
   record the originality and interlinking passes rely on.
2. Run the planner and review the calendar with the user:

   ```bash
   python scripts/content_calendar.py --queue content-queue.json \
       --config site.config.json --start <monday> --weeks 12
   ```

   The planner caps every week at the ramp ceiling and the configured
   cadence. Do not work around an overflow by raising --per-week past
   the ramp: the pace rules exist to stay outside Google's
   scaled-content-abuse pattern (PLAYBOOK policy guard).
3. Persist once agreed: re-run with `--apply` (writes `week_of` and
   `status: scheduled` back into the queue) and `--output
   content-calendar.md` for a human-readable copy in the repo.
4. Drive the weekly loop from the calendar: each week, take that
   week's items - `new` items go through /write-blog (full pipeline,
   all gates), `refresh` items through the refresh-content skill -
   then set their status to `done` in the queue.
5. Re-plan when reality changes (missed week, new cluster map,
   seasonal push): reset affected items to `queued` and re-run with
   `--apply`. Scheduled dates are a plan, not history; only `done`
   is permanent.

## Output

- An updated `content-queue.json` with week assignments.
- `content-calendar.md`: the dated weekly calendar, open slots and
  overflow visible.
- A short note on pace: which weeks are full, where the ramp is the
  binding constraint, and what falls beyond the horizon.

## Quality checklist

- Every scheduled week respects weekly_ramp and articles_per_week.
- Priorities came from the roadmap, not insertion order.
- Refresh items carry the target URL.
- The user saw the calendar before --apply.
