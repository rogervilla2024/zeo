"""Rank open-source Astro themes for a niche from GitHub metadata.

The theme funnel evaluates the whole ecosystem without cloning it:
hundreds of candidates arrive as GitHub search metadata, hard filters
drop unusable ones (bad license, abandoned, too obscure), and a score
combining niche keyword match, stars, and freshness ranks the rest.
Only the few finalists ever get cloned and built.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import UTC, datetime

ALLOWED_LICENSES: frozenset[str] = frozenset(
    {"mit", "apache-2.0", "bsd-2-clause", "bsd-3-clause", "isc", "0bsd", "cc0-1.0"}
)
MAX_AGE_DAYS: int = 548  # ~18 months without a push means abandoned


@dataclass(slots=True)
class ThemeCandidate:
    """One theme repository from the GitHub search API.

    Args:
        full_name: ``owner/repo``.
        description: Repository description (may be empty).
        stars: Stargazer count.
        license_id: SPDX id, lowercased, or empty when unlicensed.
        pushed_at: Last push, ISO 8601.
        url: Repository HTML URL.
        homepage: Demo URL when set.
    """

    full_name: str
    description: str
    stars: int
    license_id: str
    pushed_at: str
    url: str
    homepage: str


def _as_int(value: object) -> int:
    return int(value) if isinstance(value, int | float | str) and value else 0


def parse_search_items(items: list[dict[str, object]]) -> list[ThemeCandidate]:
    """Convert GitHub search API items into candidates."""
    candidates: list[ThemeCandidate] = []
    for item in items:
        raw_license = item.get("license")
        license_id = ""
        if isinstance(raw_license, dict):
            license_id = str(raw_license.get("spdx_id") or "").lower()
        candidates.append(
            ThemeCandidate(
                full_name=str(item.get("full_name", "")),
                description=str(item.get("description") or ""),
                stars=_as_int(item.get("stargazers_count")),
                license_id=license_id,
                pushed_at=str(item.get("pushed_at") or ""),
                url=str(item.get("html_url") or ""),
                homepage=str(item.get("homepage") or ""),
            )
        )
    return candidates


def _age_days(pushed_at: str, now: datetime) -> float:
    try:
        pushed = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
    except ValueError:
        return float("inf")
    return (now - pushed).total_seconds() / 86400


def filter_candidates(
    candidates: list[ThemeCandidate],
    now: datetime,
    min_stars: int = 50,
    max_age_days: int = MAX_AGE_DAYS,
) -> list[ThemeCandidate]:
    """Apply the hard filters: license, activity, minimum traction."""
    return [
        candidate
        for candidate in candidates
        if candidate.license_id in ALLOWED_LICENSES
        and candidate.stars >= min_stars
        and _age_days(candidate.pushed_at, now) <= max_age_days
    ]


def score(candidate: ThemeCandidate, niche_keywords: list[str], now: datetime) -> float:
    """Score a candidate: niche match dominates, then stars, then freshness.

    Args:
        candidate: The theme.
        niche_keywords: Lowercased niche/type words ("blog", "magazine",
            "docs", "review", plus topic words).
        now: Current time (passed in for testability).

    Returns:
        Higher is better.
    """
    haystack = f"{candidate.full_name} {candidate.description}".lower()
    keyword_hits = sum(1 for keyword in niche_keywords if keyword in haystack)
    freshness = max(0.0, 1.0 - _age_days(candidate.pushed_at, now) / MAX_AGE_DAYS)
    return keyword_hits * 10.0 + math.log10(max(candidate.stars, 1)) * 3.0 + freshness


def rank(
    candidates: list[ThemeCandidate],
    niche_keywords: list[str],
    now: datetime,
    top: int = 8,
    min_stars: int = 50,
) -> list[tuple[ThemeCandidate, float]]:
    """Filter and rank candidates, best first."""
    filtered = filter_candidates(candidates, now, min_stars=min_stars)
    scored = [
        (candidate, score(candidate, niche_keywords, now)) for candidate in filtered
    ]
    scored.sort(key=lambda pair: -pair[1])
    return scored[:top]


def utcnow() -> datetime:
    """Current UTC time (isolated for tests)."""
    return datetime.now(UTC)
