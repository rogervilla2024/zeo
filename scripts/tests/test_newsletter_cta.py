"""Tests for the zero-JS newsletter CTA contract."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "templates" / "site.config.example.json"
CTA = ROOT / "templates" / "theme" / "NewsletterCta.astro"
WORKER_DOC = ROOT / "templates" / "deploy" / "newsletter-worker.md"


def test_config_ships_with_newsletter_disabled() -> None:
    config = json.loads(CONFIG.read_text())
    newsletter = config["newsletter"]
    assert newsletter["enabled"] is False
    assert newsletter["action"].startswith("/")


def test_cta_component_is_zero_js_with_honeypot() -> None:
    source = CTA.read_text()
    assert "<script" not in source, "newsletter CTA must stay zero-JS"
    assert 'method="post"' in source
    assert "config.newsletter" in source
    assert "newsletter.enabled" in source
    assert 'action={newsletter.action}' in source
    assert 'type="email"' in source and "required" in source
    assert 'name="website"' in source, "honeypot field missing"
    assert 'aria-hidden="true"' in source


def test_worker_example_covers_the_contract() -> None:
    doc = WORKER_DOC.read_text()
    assert "formData" in doc
    assert "303" in doc, "worker must redirect after POST (no JS fallback)"
    assert "honeypot" in doc.lower()
    assert "SUBSCRIBERS" in doc, "KV storage binding documented"
    assert "wrangler" in doc
    assert "Double opt-in" in doc


def test_golden_article_template_wires_the_cta() -> None:
    template = (
        ROOT / "templates" / "golden" / "src" / "pages" / "blog" / "[...slug].astro"
    ).read_text()
    assert "<NewsletterCta />" in template
