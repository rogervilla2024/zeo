"""Tests for served-robots.txt conflict detection."""

from __future__ import annotations

from seo_content_forge.robots_live import find_conflicts, parse_robots

# The field case: Cloudflare's managed AI-crawler block prepended
# above the site's own AI-ready rules.
CLOUDFLARE_CONFLICT = """\
# Managed by Cloudflare
User-agent: GPTBot
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: CCBot
User-agent: Google-Extended
Disallow: /

# --- site's own rules below ---
User-agent: *
Allow: /
Disallow: /search?

User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Google-Extended
Allow: /

Sitemap: https://example.com/sitemap.xml
"""

CLEAN = """\
User-agent: *
Allow: /
Disallow: /search?

User-agent: GPTBot
Allow: /
"""


def test_conflicts_detected_per_agent() -> None:
    problems = find_conflicts(CLOUDFLARE_CONFLICT)
    conflicted = [p.split("'")[1] for p in problems]
    assert conflicted == ["claudebot", "google-extended", "gptbot"]
    # CCBot is only disallowed - no conflict; the wildcard agent is
    # only allowed - no conflict.
    assert not any("ccbot" in p for p in problems)
    assert not any("'*'" in p for p in problems)


def test_clean_policy_passes() -> None:
    assert find_conflicts(CLEAN) == []


def test_parse_groups_and_path_rules() -> None:
    rules = parse_robots(CLOUDFLARE_CONFLICT)
    # Stacked User-agent lines share the group's rules.
    assert rules["ccbot"] == {"disallow"}
    assert rules["google-extended"] == {"disallow", "allow"}
    # Path-specific rules (Disallow: /search?) never count as root.
    assert rules["*"] == {"allow"}
    # Comments and case are normalized away.
    assert parse_robots("User-Agent: GPTBot # trailing\nDISALLOW: /") == {
        "gptbot": {"disallow"}
    }
    assert parse_robots("") == {}
