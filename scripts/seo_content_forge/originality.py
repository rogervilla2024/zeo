"""Cross-article originality checking via shingle similarity.

Publishing many articles across many sites risks self-similarity: the
same phrasings, the same section skeletons, the same paragraphs lightly
reworded. Search engines treat scaled, substantially-similar content as
a quality problem, so originality needs an objective gate, not a
feeling.

This module compares an article against a corpus of the site's
already-published articles using word k-gram (shingle) Jaccard
similarity - deterministic, offline, and language-agnostic. It reports
the most similar corpus documents and example shared phrases so the
writer can see exactly what overlaps.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

DEFAULT_SHINGLE_SIZE: int = 8


def _words(text: str) -> list[str]:
    """Lowercase word tokens with markdown syntax and punctuation removed."""
    text = re.sub(r"(?s)```.*?```", " ", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return re.findall(r"[a-z0-9']+", text.lower())


def shingles(text: str, k: int = DEFAULT_SHINGLE_SIZE) -> set[tuple[str, ...]]:
    """Return the set of word ``k``-grams in ``text``.

    Args:
        text: Markdown or plain text.
        k: Shingle length in words; 8 catches copied sentences while
            ignoring incidental short phrase overlap.

    Returns:
        The set of shingles; empty when the text has fewer than ``k``
        words.
    """
    tokens = _words(text)
    return {tuple(tokens[i : i + k]) for i in range(len(tokens) - k + 1)}


def jaccard(first: set[tuple[str, ...]], second: set[tuple[str, ...]]) -> float:
    """Jaccard similarity of two shingle sets (0.0 to 1.0)."""
    if not first or not second:
        return 0.0
    return len(first & second) / len(first | second)


@dataclass(slots=True)
class SimilarityResult:
    """Similarity of the article to one corpus document.

    Args:
        url: Identifier of the corpus document.
        score: Jaccard similarity of the shingle sets.
        shared_phrases: Up to three example phrases appearing in both.
    """

    url: str
    score: float
    shared_phrases: list[str]


def compare(
    article_text: str,
    corpus: dict[str, str],
    k: int = DEFAULT_SHINGLE_SIZE,
    top: int = 5,
) -> list[SimilarityResult]:
    """Compare an article against every corpus document.

    Args:
        article_text: The new article (markdown or plain text).
        corpus: Mapping of document URL/id to its text.
        k: Shingle length in words.
        top: Maximum results to return.

    Returns:
        The ``top`` most similar documents, highest score first,
        excluding zero-similarity documents.
    """
    article_shingles = shingles(article_text, k)
    results: list[SimilarityResult] = []
    for url, text in corpus.items():
        doc_shingles = shingles(text, k)
        score = jaccard(article_shingles, doc_shingles)
        if score == 0.0:
            continue
        shared = sorted(article_shingles & doc_shingles)[:3]
        results.append(
            SimilarityResult(
                url=url,
                score=score,
                shared_phrases=[" ".join(shingle) for shingle in shared],
            )
        )
    results.sort(key=lambda result: -result.score)
    return results[:top]
