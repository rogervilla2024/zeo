"""Unit tests for :mod:`seo_content_forge.pagespeed` (parsing only).

The PageSpeed Insights API itself is an external dependency; per project
guidelines it is not called in tests. These tests feed a synthetic API
response into the pure parser.
"""

from __future__ import annotations

from seo_content_forge.pagespeed import parse_report

_SYNTHETIC_RESPONSE: dict[str, object] = {
    "loadingExperience": {
        "metrics": {
            "LARGEST_CONTENTFUL_PAINT_MS": {"category": "FAST"},
            "INTERACTION_TO_NEXT_PAINT": {"category": "AVERAGE"},
            "CUMULATIVE_LAYOUT_SHIFT_SCORE": {"category": "FAST"},
        }
    },
    "lighthouseResult": {
        "categories": {"performance": {"score": 0.87}},
        "audits": {
            "largest-contentful-paint": {"displayValue": "2.1 s"},
            "render-blocking-resources": {
                "title": "Eliminate render-blocking resources",
                "description": "Resources block first paint.",
                "details": {"type": "opportunity", "overallSavingsMs": 450},
            },
            "unused-css-rules": {
                "title": "Reduce unused CSS",
                "description": "Remove dead rules.",
                "details": {"type": "opportunity", "overallSavingsMs": 900},
            },
            "uses-http2": {
                "title": "Not an opportunity",
                "details": {"type": "table"},
            },
        },
    },
}


def test_parse_full_response() -> None:
    # Act
    report = parse_report(_SYNTHETIC_RESPONSE)

    # Assert
    assert report.performance_score == 87
    assert report.field_data == {"LCP": "FAST", "INP": "AVERAGE", "CLS": "FAST"}
    assert report.lab_metrics == {"LCP (lab)": "2.1 s"}
    assert [item.title for item in report.opportunities] == [
        "Reduce unused CSS",
        "Eliminate render-blocking resources",
    ]


def test_cwv_fails_when_any_metric_not_fast() -> None:
    report = parse_report(_SYNTHETIC_RESPONSE)
    assert report.passes_cwv is False


def test_empty_response_yields_empty_report() -> None:
    report = parse_report({})
    assert report.performance_score is None
    assert report.passes_cwv is None
    assert not report.field_data
    assert not report.opportunities
