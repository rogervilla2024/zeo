"""Tests for the shipped visual + console gate harness."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "templates" / "ci" / "visual-check.mjs"


def test_visual_check_harness_contract() -> None:
    source = SCRIPT.read_text()
    assert source.isascii()
    # Three widths, both failure channels, and a hard exit code.
    for needle in (
        "390",
        "768",
        "1440",
        'message.type() === "error"',
        "pageerror",
        "requestfailed",
        "process.exit(1)",
        "fullPage: true",
        "/opt/pw-browsers/chromium",
    ):
        assert needle in source, f"visual-check.mjs misses {needle}"


def test_visual_review_skill_requires_the_harness() -> None:
    skill = (ROOT / "skills" / "visual-review" / "SKILL.md").read_text()
    assert "visual-check.mjs" in skill
    assert "automatic fail" in skill
