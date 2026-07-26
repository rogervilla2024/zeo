"""Tests for the LocalBusiness/JobPosting/Course/SoftwareApplication builders."""

from __future__ import annotations

from seo_content_forge.jsonld import (
    BUILDERS,
    course,
    job_posting,
    local_business,
    software_application,
)
from seo_content_forge.validate import validate_node


def test_local_business_full_node_validates() -> None:
    node = local_business(
        name="Roast House",
        url="https://roast.example/",
        street_address="1 Bean St",
        address_locality="Portland",
        postal_code="97201",
        address_country="US",
        address_region="OR",
        telephone="+1-503-555-0100",
        price_range="$$",
        image=["https://roast.example/shop.jpg"],
        latitude="45.52",
        longitude="-122.68",
        opening_hours=["Mo-Fr 07:00-18:00", "Sa 08:00-16:00"],
        same_as=["https://maps.example/roast-house"],
    )
    assert node["@type"] == "LocalBusiness"
    address = node["address"]
    assert isinstance(address, dict)
    assert address["addressCountry"] == "US"
    geo = node["geo"]
    assert isinstance(geo, dict) and geo["latitude"] == "45.52"
    result = validate_node(node)
    assert result.is_valid and result.warnings == []


def test_local_business_subtype_and_minimal_shape() -> None:
    node = local_business(
        name="Dr. Smile",
        url="https://smile.example/",
        street_address="2 Tooth Ave",
        address_locality="Austin",
        postal_code="73301",
        address_country="US",
        business_type="Dentist",
    )
    assert node["@type"] == "Dentist"
    assert "geo" not in node and "telephone" not in node
    minimal: dict[str, object] = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": "X",
    }
    result = validate_node(minimal)
    assert not result.is_valid
    assert any("address" in error for error in result.errors)


def test_job_posting_onsite_validates() -> None:
    node = job_posting(
        title="Barista",
        description="<p>Make coffee.</p>",
        date_posted="2026-07-01",
        organization_name="Roast House",
        organization_url="https://roast.example/",
        address_locality="Portland",
        address_region="OR",
        address_country="US",
        employment_type="FULL_TIME",
        valid_through="2026-09-01T00:00:00Z",
        salary_value="45000",
        salary_currency="USD",
    )
    location = node["jobLocation"]
    assert isinstance(location, dict)
    address = location["address"]
    assert isinstance(address, dict) and address["addressLocality"] == "Portland"
    salary = node["baseSalary"]
    assert isinstance(salary, dict)
    value = salary["value"]
    assert isinstance(value, dict) and value["unitText"] == "YEAR"
    result = validate_node(node)
    assert result.is_valid and result.warnings == []


def test_job_posting_remote_uses_telecommute() -> None:
    node = job_posting(
        title="Editor",
        description="<p>Edit articles.</p>",
        date_posted="2026-07-01",
        organization_name="Example Media",
        is_remote=True,
        address_country="US",
    )
    assert node["jobLocationType"] == "TELECOMMUTE"
    requirements = node["applicantLocationRequirements"]
    assert isinstance(requirements, dict) and requirements["name"] == "US"
    assert validate_node(node).is_valid


def test_course_minimal_and_full() -> None:
    minimal = course(name="SEO 101", description="Basics.", provider_name="Example")
    result = validate_node(minimal)
    assert result.is_valid
    assert any("offers" in warning for warning in result.warnings)
    full = course(
        name="SEO 101",
        description="Basics.",
        provider_name="Example",
        provider_url="https://example.com",
        url="https://example.com/seo-101",
        course_mode="online",
        price="0",
        currency="USD",
    )
    instance = full["hasCourseInstance"]
    assert isinstance(instance, dict) and instance["courseMode"] == "online"
    assert validate_node(full).warnings == []


def test_software_application_rating_and_offer() -> None:
    node = software_application(
        name="SiteAudit",
        operating_system="Windows, macOS",
        application_category="DeveloperApplication",
        price="19.99",
        currency="USD",
        rating_value="4.7",
        rating_count=213,
        description="Desktop SEO auditor.",
    )
    offers = node["offers"]
    assert isinstance(offers, dict) and offers["price"] == "19.99"
    rating = node["aggregateRating"]
    assert isinstance(rating, dict) and rating["ratingCount"] == 213
    assert validate_node(node).is_valid
    free = software_application(
        name="SiteAudit",
        operating_system="ANDROID",
        application_category="DeveloperApplication",
    )
    assert "aggregateRating" not in free
    warnings = validate_node(free).warnings
    assert any("aggregateRating" in warning for warning in warnings)


def test_new_builders_registered() -> None:
    for key, builder in (
        ("localbusiness", local_business),
        ("jobposting", job_posting),
        ("course", course),
        ("softwareapp", software_application),
    ):
        assert BUILDERS[key] is builder
