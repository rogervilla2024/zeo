"""Validate schema.org JSON-LD against Google rich-result requirements.

This performs a lightweight structural check, not a full schema.org
validation: it confirms ``@context`` and ``@type`` are present and that
the required and recommended properties Google documents for each
rich-result type are populated. It complements, and does not replace, the
Rich Results Test.
"""

from __future__ import annotations

from dataclasses import dataclass

# Required and recommended properties per rich-result type. Nested objects
# are checked for presence only; their internal shape is left to the
# builders in :mod:`seo_content_forge.jsonld`.
_REQUIRED: dict[str, tuple[str, ...]] = {
    "Article": ("headline", "author", "datePublished"),
    "BlogPosting": ("headline", "author", "datePublished"),
    "NewsArticle": ("headline", "author", "datePublished"),
    "FAQPage": ("mainEntity",),
    "HowTo": ("name", "step"),
    "BreadcrumbList": ("itemListElement",),
    "Organization": ("name", "url"),
    "WebSite": ("name", "url"),
    "Product": ("name", "offers"),
    "Recipe": ("name", "image", "recipeIngredient", "recipeInstructions"),
    "VideoObject": ("name", "thumbnailUrl", "uploadDate"),
    "Event": ("name", "startDate", "location"),
    "Person": ("name", "url"),
    "LocalBusiness": ("name", "address"),
    "JobPosting": ("title", "description", "datePosted", "hiringOrganization"),
    "Course": ("name", "description"),
    "SoftwareApplication": ("name", "offers"),
    "WebPage": ("name", "url"),
}
_RECOMMENDED: dict[str, tuple[str, ...]] = {
    "Article": ("image", "dateModified", "publisher", "description"),
    "BlogPosting": ("image", "dateModified", "publisher", "description"),
    "NewsArticle": ("image", "dateModified", "publisher", "description"),
    "Organization": ("logo", "sameAs"),
    "Product": ("image", "description", "aggregateRating"),
    "WebSite": ("potentialAction",),
    "Recipe": ("author", "description", "prepTime", "cookTime", "aggregateRating"),
    "VideoObject": ("description", "duration", "contentUrl"),
    "Event": ("endDate", "description", "image", "offers", "organizer"),
    "Person": ("sameAs", "image", "jobTitle", "description"),
    "LocalBusiness": ("url", "telephone", "openingHours", "geo", "priceRange", "image"),
    "JobPosting": ("jobLocation", "validThrough", "employmentType", "baseSalary"),
    "Course": ("provider", "offers", "hasCourseInstance"),
    "SoftwareApplication": (
        "applicationCategory",
        "operatingSystem",
        "aggregateRating",
        "description",
    ),
}


@dataclass(slots=True)
class ValidationResult:
    """Outcome of validating one JSON-LD node.

    Args:
        node_type: The ``@type`` that was validated (``"unknown"`` if
            missing).
        errors: Blocking problems that make the node ineligible for the
            rich result.
        warnings: Non-blocking gaps, typically missing recommended
            properties.
    """

    node_type: str
    errors: list[str]
    warnings: list[str]

    @property
    def is_valid(self) -> bool:
        """Return ``True`` when there are no blocking errors."""
        return not self.errors


def _selector_list_ok(value: object) -> bool:
    """True for a non-empty string or non-empty list of strings."""
    if isinstance(value, str):
        return bool(value)
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(entry, str) and entry for entry in value)
    )


def _check_speakable(value: object) -> list[str]:
    """Structural errors for a node's ``speakable`` property.

    Args:
        value: The ``speakable`` payload - one SpeakableSpecification
            object or a list of them.

    Returns:
        Blocking problems; empty when the specification is well-formed.
    """
    specs = value if isinstance(value, list) else [value]
    errors: list[str] = []
    for spec in specs:
        if not isinstance(spec, dict):
            errors.append("speakable: entry is not an object")
            continue
        if spec.get("@type") != "SpeakableSpecification":
            errors.append('speakable: @type must be "SpeakableSpecification"')
        if not _selector_list_ok(spec.get("cssSelector")) and not _selector_list_ok(
            spec.get("xpath")
        ):
            errors.append("speakable: needs a non-empty cssSelector or xpath")
    return errors


def validate_node(node: dict[str, object]) -> ValidationResult:
    """Validate a single JSON-LD node.

    Args:
        node: A parsed JSON-LD object.

    Returns:
        A :class:`ValidationResult` describing errors and warnings.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if node.get("@context") != "https://schema.org":
        warnings.append('@context should be "https://schema.org"')

    raw_type = node.get("@type")
    if not isinstance(raw_type, str) or not raw_type:
        errors.append("@type is missing")
        return ValidationResult("unknown", errors, warnings)

    if "speakable" in node:
        errors.extend(_check_speakable(node["speakable"]))

    if raw_type not in _REQUIRED:
        warnings.append(f"@type {raw_type!r} has no rich-result rule set; skipping")
        return ValidationResult(raw_type, errors, warnings)

    for prop in _REQUIRED[raw_type]:
        value = node.get(prop)
        if value is None or value == "" or value == [] or value == {}:
            errors.append(f"{raw_type}: required property {prop!r} is missing or empty")

    for prop in _RECOMMENDED.get(raw_type, ()):
        value = node.get(prop)
        if value is None or value == "" or value == [] or value == {}:
            warnings.append(f"{raw_type}: recommended property {prop!r} is missing")

    return ValidationResult(raw_type, errors, warnings)


def validate(
    data: dict[str, object] | list[dict[str, object]],
) -> list[ValidationResult]:
    """Validate one JSON-LD node or a list of nodes.

    Args:
        data: A single JSON-LD object or a list of them.

    Returns:
        One :class:`ValidationResult` per node, in input order.
    """
    nodes = data if isinstance(data, list) else [data]
    return [validate_node(node) for node in nodes]
