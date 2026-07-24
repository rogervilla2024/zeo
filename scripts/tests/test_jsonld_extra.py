"""Unit tests for the Recipe, VideoObject, and Event JSON-LD builders."""

from __future__ import annotations

import pytest

from seo_content_forge import jsonld
from seo_content_forge.validate import validate


def test_recipe_builds_and_validates() -> None:
    # Arrange / Act
    node = jsonld.recipe(
        name="Test dish",
        image=["https://example.com/dish.jpg"],
        ingredients=["1 cup flour", "2 eggs"],
        instructions=["Mix everything.", "Bake for 30 minutes."],
        author_name="Jane Doe",
        prep_time="PT10M",
        cook_time="PT30M",
    )

    # Assert
    assert node["@type"] == "Recipe"
    steps = node["recipeInstructions"]
    assert [step["position"] for step in steps] == [1, 2]
    assert validate(node)[0].is_valid


def test_recipe_requires_ingredients() -> None:
    with pytest.raises(ValueError, match="ingredients"):
        jsonld.recipe(
            name="X",
            image=["https://example.com/i.jpg"],
            ingredients=[],
            instructions=["Step"],
        )


def test_video_builds_and_validates() -> None:
    node = jsonld.video(
        name="Test video",
        thumbnail_url=["https://example.com/t.jpg"],
        upload_date="2026-01-15",
        duration="PT8M32S",
        content_url="https://example.com/v.mp4",
    )
    assert node["@type"] == "VideoObject"
    assert validate(node)[0].is_valid


def test_event_offline_location_shape() -> None:
    node = jsonld.event(
        name="Test conference",
        start_date="2026-09-01T09:00:00+00:00",
        location_name="Venue Hall",
        location_address="1 Main Street, Springfield",
        end_date="2026-09-01T17:00:00+00:00",
        organizer_name="Example Org",
    )
    location = node["location"]
    assert location["@type"] == "Place"
    assert node["eventAttendanceMode"].endswith("OfflineEventAttendanceMode")
    assert validate(node)[0].is_valid


def test_event_online_uses_virtual_location() -> None:
    node = jsonld.event(
        name="Test webinar",
        start_date="2026-09-01T09:00:00+00:00",
        location_name="Webinar page",
        location_address="https://example.com/webinar",
        is_online=True,
    )
    location = node["location"]
    assert location["@type"] == "VirtualLocation"
    assert location["url"] == "https://example.com/webinar"


def test_registry_includes_new_types() -> None:
    assert {"recipe", "video", "event"} <= set(jsonld.BUILDERS)


def test_missing_required_recipe_property_fails_validation() -> None:
    node = {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "name": "Incomplete",
    }
    result = validate(node)[0]
    assert not result.is_valid
    assert any("recipeIngredient" in error for error in result.errors)
