"""Unit tests for :mod:`seo_content_forge.ai_patterns`."""

from __future__ import annotations

from seo_content_forge.ai_patterns import analyze

_CLEAN = """# A guide

Strong openings name the reader's problem. This one does exactly that,
with detail and a concrete promise the body then keeps fully.

Some paragraphs run long because the material demands it, stacking
evidence, examples, and edge cases until the point is properly earned
and the reader has what they need to act on it with confidence today.

Short ones do not.

Varied rhythm reads as human. Specifics beat abstractions every single
time, and numbers beat adjectives in almost every sentence you write.
"""


def test_clean_article_passes() -> None:
    report = analyze(_CLEAN)
    assert report.passed
    assert report.findings == []


def test_banned_phrase_is_flagged_with_line() -> None:
    text = _CLEAN + "\nIn conclusion, sleep matters in today's fast-paced world.\n"
    report = analyze(text)
    assert not report.passed
    phrases = {finding.phrase for finding in report.findings}
    assert "in conclusion" in phrases
    assert "in today's fast-paced world" in phrases
    assert all(finding.line > 0 for finding in report.findings)


def test_repeated_openers_warned() -> None:
    sentences = " ".join(
        f"The point number {i} is about writing with more variety." for i in range(12)
    )
    report = analyze(sentences)
    assert report.passed
    assert any("opener" in warning for warning in report.warnings)


def test_uniform_paragraphs_warned() -> None:
    paragraph = (
        "This paragraph has exactly the same number of words as its "
        "siblings which makes the rhythm feel mechanical to readers "
        "and pattern detectors alike in practice overall."
    )
    text = "\n\n".join([paragraph] * 6)
    report = analyze(text)
    assert any("uniform" in warning for warning in report.warnings)


def test_code_blocks_do_not_feed_metrics() -> None:
    report = analyze("```\n" + "Same start of a sentence repeated. " * 20 + "\n```\n")
    assert report.warnings == []
