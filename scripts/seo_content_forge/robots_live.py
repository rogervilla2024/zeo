"""Detect conflicting rules in a served robots.txt.

Field case: Cloudflare's "AI Scrapers & Crawlers" feature silently
prepends a managed block that disallows GPTBot, ClaudeBot, CCBot and
friends - directly contradicting the site's own AI-ready Allow rules
below it. Which rule wins is crawler-dependent, so the site's crawl
policy becomes undefined. This module parses robots.txt into per-agent
rule sets and reports agents that are simultaneously allowed and
disallowed at the root.
"""

from __future__ import annotations


def parse_robots(text: str) -> dict[str, set[str]]:
    """Collect root-level rules per user-agent across the whole file.

    Args:
        text: Raw robots.txt content.

    Returns:
        Mapping of lowercased user-agent token to the set of root
        rules seen for it anywhere in the file: ``"allow"`` for
        ``Allow: /`` and ``"disallow"`` for ``Disallow: /``. Rules for
        specific paths (e.g. ``Disallow: /search?``) are ignored -
        only the all-or-nothing root rules can conflict.
    """
    rules: dict[str, set[str]] = {}
    current_agents: list[str] = []
    previous_was_agent = False
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        key, sep, value = line.partition(":")
        if not sep:
            continue
        key = key.strip().lower()
        value = value.strip()
        if key == "user-agent":
            if not previous_was_agent:
                current_agents = []
            current_agents.append(value.lower())
            previous_was_agent = True
            continue
        previous_was_agent = False
        if key not in ("allow", "disallow") or value != "/":
            continue
        rule = "allow" if key == "allow" else "disallow"
        for agent in current_agents:
            rules.setdefault(agent, set()).add(rule)
    return rules


def find_conflicts(text: str) -> list[str]:
    """Find user-agents that are both allowed and disallowed at root.

    Args:
        text: Raw robots.txt content.

    Returns:
        Human-readable problems, one per conflicted agent (sorted);
        empty when the policy is unambiguous.
    """
    return [
        f"user-agent {agent!r} has both 'Allow: /' and 'Disallow: /' - "
        "crawl policy is undefined (a CDN-managed robots block, e.g. "
        "Cloudflare AI Crawl Control, may be injecting rules; align it "
        "with the site's own policy)"
        for agent, seen in sorted(parse_robots(text).items())
        if "allow" in seen and "disallow" in seen
    ]
