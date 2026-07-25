"""Unit tests for the mojibake detector in :mod:`seo_content_forge.llmstxt`."""

from __future__ import annotations

from seo_content_forge.llmstxt import looks_mojibake


def test_clean_turkish_text_passes() -> None:
    assert not looks_mojibake("Kumarın Hükmü ve çok dilli içerik")


def test_double_encoded_text_detected() -> None:
    broken = "Ä°slam'da KumarÄ±n HÃ¼kmÃ¼"
    assert looks_mojibake(broken)


def test_clean_french_and_portuguese_pass() -> None:
    assert not looks_mojibake("Recettes françaises à São Paulo")
