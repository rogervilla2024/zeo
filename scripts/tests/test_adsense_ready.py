"""Tests for the AdSense-readiness config contract and theme slot."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "templates" / "site.config.example.json"
ADSLOT = ROOT / "templates" / "theme" / "AdSlot.astro"


def test_config_ships_with_ads_disabled() -> None:
    config = json.loads(CONFIG.read_text())
    ads = config["ads"]
    assert ads["enabled"] is False, "templates must never ship with ads on"
    assert ads["client_id"] == ""
    assert isinstance(ads["slots"], list) and ads["slots"]
    assert all(isinstance(slot, str) and slot for slot in ads["slots"])


def test_adslot_component_contract() -> None:
    source = ADSLOT.read_text()
    assert "config.ads" in source, "slot must be driven by the ads config key"
    assert "ads.enabled" in source
    assert "ads.slots.includes(name)" in source
    assert "data-ad-slot={name}" in source
    assert "min-height" in source, "slot must reserve space to avoid CLS"
    assert "<script" not in source, "readiness slot must stay zero-JS"


def test_golden_article_template_wires_a_slot() -> None:
    template = (
        ROOT / "templates" / "golden" / "src" / "pages" / "[...slug].astro"
    ).read_text()
    assert '<AdSlot name="article-end" />' in template
