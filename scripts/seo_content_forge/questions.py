"""Mine real user questions from search autocomplete data.

Articles and FAQ blocks should answer what people actually ask, not
what a writer imagines. Google's public autocomplete endpoint returns
live completions; expanding a seed with question prefixes ("how",
"what", "vs", language-specific equivalents) surfaces the People Also
Ask-style long tail. Parsing and filtering are pure; the CLI does the
fetching.
"""

from __future__ import annotations

import unicodedata

import orjson

QUESTION_PREFIXES: dict[str, tuple[str, ...]] = {
    "en": ("how", "what", "why", "when", "can", "is", "which", "best", "vs"),
    "tr": ("nasil", "nedir", "neden", "ne zaman", "hangi", "en iyi", "mi"),
    "de": ("wie", "was", "warum", "wann", "welche", "beste"),
    "fr": ("comment", "pourquoi", "quel", "quand", "meilleur"),
    "es": ("como", "que", "por que", "cuando", "mejor"),
}


def prefixes_for(lang: str) -> tuple[str, ...]:
    """Question prefixes for a language, falling back to English."""
    return QUESTION_PREFIXES.get(lang.lower(), QUESTION_PREFIXES["en"])


def expand_queries(seed: str, lang: str) -> list[str]:
    """Build the autocomplete queries for a seed topic."""
    seed = seed.strip()
    queries = [f"{prefix} {seed}" for prefix in prefixes_for(lang)]
    queries.append(f"{seed} ")
    return queries


def parse_suggestions(payload: bytes | str) -> list[str]:
    """Parse a Google Suggest response into suggestion strings."""
    try:
        data = orjson.loads(payload)
    except orjson.JSONDecodeError:
        return []
    if isinstance(data, list) and len(data) >= 2 and isinstance(data[1], list):
        return [str(item) for item in data[1]]
    return []


def _fold(text: str) -> str:
    """Casefold and strip diacritics for accent-insensitive matching.

    Turkish seeds and suggestions mix accented and ASCII spellings
    ("sarımsak" vs "sarimsak"); matching on the folded form keeps the
    topic filter working in both directions. Dotless i (U+0131) does
    not decompose under NFKD, so it is mapped explicitly.

    Args:
        text: Text to fold; used for comparison only, never for output.

    Returns:
        Lowercased text with combining marks removed.
    """
    folded = text.casefold().replace("ı", "i")
    decomposed = unicodedata.normalize("NFKD", folded)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def dedupe_questions(batches: list[list[str]], seed: str, limit: int = 40) -> list[str]:
    """Merge suggestion batches: on-topic, deduplicated, order-stable.

    The on-topic filter compares accent-folded forms, so a seed word
    matches suggestions regardless of diacritic spelling differences.
    """
    seed_words = [_fold(word) for word in seed.split() if len(word) > 2]
    seen: set[str] = set()
    merged: list[str] = []
    for batch in batches:
        for suggestion in batch:
            normalized = " ".join(suggestion.lower().split())
            if normalized in seen or len(normalized) < 8:
                continue
            folded = _fold(normalized)
            if seed_words and not any(word in folded for word in seed_words):
                continue
            seen.add(normalized)
            merged.append(normalized)
            if len(merged) >= limit:
                return merged
    return merged
