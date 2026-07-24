"""Parse PageSpeed Insights API responses into an actionable report.

The caller (``check_pagespeed.py``) performs the HTTP request against
``https://www.googleapis.com/pagespeedonline/v5/runPagespeed``; this
module turns the raw response into Core Web Vitals field data, lab
metrics, and a prioritized list of improvement opportunities. Keeping the
parsing pure makes it unit-testable without network access.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Core Web Vitals assessment keys in the loadingExperience field data.
_FIELD_METRICS: dict[str, str] = {
    "LARGEST_CONTENTFUL_PAINT_MS": "LCP",
    "INTERACTION_TO_NEXT_PAINT": "INP",
    "CUMULATIVE_LAYOUT_SHIFT_SCORE": "CLS",
}
_LAB_AUDITS: dict[str, str] = {
    "largest-contentful-paint": "LCP (lab)",
    "cumulative-layout-shift": "CLS (lab)",
    "total-blocking-time": "TBT (lab)",
    "first-contentful-paint": "FCP (lab)",
    "speed-index": "Speed Index (lab)",
}


@dataclass(slots=True)
class Opportunity:
    """One improvement opportunity from the Lighthouse audit.

    Args:
        title: Audit title, e.g. "Eliminate render-blocking resources".
        savings_ms: Estimated milliseconds saved by fixing it.
        description: Audit description text.
    """

    title: str
    savings_ms: float
    description: str


@dataclass(slots=True)
class PageSpeedReport:
    """Parsed PageSpeed Insights result.

    Args:
        performance_score: Lighthouse performance category score, 0-100,
            or ``None`` when absent.
        field_data: Real-user CWV metric name to category
            (FAST/AVERAGE/SLOW), empty when the URL lacks CrUX data.
        lab_metrics: Lab metric name to display value.
        opportunities: Improvement opportunities sorted by estimated
            savings, largest first.
    """

    performance_score: int | None = None
    field_data: dict[str, str] = field(default_factory=dict)
    lab_metrics: dict[str, str] = field(default_factory=dict)
    opportunities: list[Opportunity] = field(default_factory=list)

    @property
    def passes_cwv(self) -> bool | None:
        """Whether all field CWV metrics are FAST; ``None`` without data."""
        if not self.field_data:
            return None
        return all(category == "FAST" for category in self.field_data.values())


def _as_dict(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def parse_report(response: dict[str, object]) -> PageSpeedReport:
    """Parse a raw PageSpeed Insights v5 API response.

    Args:
        response: Decoded JSON from the ``runPagespeed`` endpoint.

    Returns:
        A :class:`PageSpeedReport`. Missing sections yield empty fields
        rather than raising, since PSI omits data it does not have.
    """
    report = PageSpeedReport()

    metrics = _as_dict(_as_dict(response.get("loadingExperience")).get("metrics"))
    for api_key, label in _FIELD_METRICS.items():
        category = _as_dict(metrics.get(api_key)).get("category")
        if isinstance(category, str):
            report.field_data[label] = category

    lighthouse = _as_dict(response.get("lighthouseResult"))
    score = _as_dict(_as_dict(lighthouse.get("categories")).get("performance")).get(
        "score"
    )
    if isinstance(score, int | float):
        report.performance_score = round(float(score) * 100)

    audits = _as_dict(lighthouse.get("audits"))
    for audit_id, label in _LAB_AUDITS.items():
        display = _as_dict(audits.get(audit_id)).get("displayValue")
        if isinstance(display, str):
            report.lab_metrics[label] = display

    for audit in audits.values():
        audit_map = _as_dict(audit)
        details = _as_dict(audit_map.get("details"))
        if details.get("type") != "opportunity":
            continue
        savings = details.get("overallSavingsMs")
        title = audit_map.get("title")
        if not isinstance(savings, int | float) or savings <= 0:
            continue
        report.opportunities.append(
            Opportunity(
                title=title if isinstance(title, str) else "(untitled audit)",
                savings_ms=float(savings),
                description=str(audit_map.get("description") or ""),
            )
        )
    report.opportunities.sort(key=lambda item: item.savings_ms, reverse=True)
    return report
