"""Unit tests for :mod:`seo_content_forge.originality`."""

from __future__ import annotations

from seo_content_forge.originality import compare, jaccard, shingles

_BASE = (
    "Getting quality sleep starts with a consistent evening routine that "
    "signals your body it is time to wind down for the night ahead. "
    "Caffeine after mid afternoon delays that signal for many adults."
)


def test_identical_text_scores_one() -> None:
    results = compare(_BASE, {"https://example.com/a": _BASE})
    assert results[0].score == 1.0
    assert results[0].shared_phrases


def test_unrelated_text_excluded() -> None:
    unrelated = (
        "Quantum error correction protects fragile qubit states from "
        "decoherence by encoding logical information redundantly across "
        "many physical qubits inside the processor fabric today."
    )
    assert compare(_BASE, {"https://example.com/q": unrelated}) == []


def test_partial_overlap_scores_between() -> None:
    # Same first sentence, different second half.
    partial = (
        "Getting quality sleep starts with a consistent evening routine that "
        "signals your body it is time to wind down for the night ahead. "
        "Blue light from screens is a separate and well documented problem."
    )
    results = compare(_BASE, {"https://example.com/p": partial})
    assert 0.0 < results[0].score < 1.0


def test_markdown_syntax_ignored() -> None:
    linked = _BASE.replace("evening routine", "[evening routine](https://x.com)")
    results = compare(linked, {"https://example.com/a": _BASE})
    assert results[0].score == 1.0


def test_short_text_has_no_shingles() -> None:
    assert shingles("too short", k=8) == set()
    assert jaccard(set(), shingles(_BASE)) == 0.0


def test_top_limit_and_ordering() -> None:
    corpus = {
        "https://example.com/full": _BASE,
        "https://example.com/half": _BASE.split(".")[0] + ". Entirely new tail "
        "content follows here with different words about another topic now.",
    }
    results = compare(_BASE, corpus, top=2)
    assert [result.url for result in results][0] == "https://example.com/full"
    assert results[0].score > results[1].score
