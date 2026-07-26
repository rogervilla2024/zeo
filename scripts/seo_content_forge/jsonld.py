"""Assemble schema.org JSON-LD blocks for Google rich results.

Each builder returns a plain ``dict`` ready to be serialized and embedded
in a ``<script type="application/ld+json">`` tag. Builders include only
the properties they are given so callers stay in control of what ships,
while :mod:`seo_content_forge.validate` checks required coverage.

The builders are site-agnostic: pass the site's own values for every
argument.
"""

from __future__ import annotations

from collections.abc import Callable

SCHEMA_CONTEXT: str = "https://schema.org"


def _clean(mapping: dict[str, object]) -> dict[str, object]:
    """Drop keys whose value is ``None`` or an empty string/list/dict."""
    return {
        key: value
        for key, value in mapping.items()
        if value is not None and value != "" and value != [] and value != {}
    }


def article(
    headline: str,
    url: str,
    author_name: str,
    publisher_name: str,
    publisher_logo: str,
    date_published: str,
    date_modified: str | None = None,
    description: str | None = None,
    image: list[str] | None = None,
    article_type: str = "BlogPosting",
    author_url: str | None = None,
) -> dict[str, object]:
    """Build an Article/BlogPosting node.

    Args:
        headline: Article title (Google truncates past ~110 characters).
        url: Canonical URL of the article.
        author_name: Name of the person or organization that wrote it.
        publisher_name: Publishing organization name.
        publisher_logo: Absolute URL of the publisher logo image.
        date_published: ISO 8601 publish datetime.
        date_modified: ISO 8601 last-modified datetime; defaults to
            ``date_published``.
        description: Short summary of the article.
        image: One or more absolute image URLs (16:9, 4:3, 1:1 preferred).
        article_type: ``Article``, ``BlogPosting`` or ``NewsArticle``.
        author_url: URL of the author's profile page, linking the byline
            to the site's author entity (E-E-A-T signal).

    Returns:
        The JSON-LD node as a dict.
    """
    author: dict[str, object] = {"@type": "Person", "name": author_name}
    if author_url:
        author["url"] = author_url
    node: dict[str, object] = {
        "@context": SCHEMA_CONTEXT,
        "@type": article_type,
        "headline": headline,
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "url": url,
        "description": description,
        "image": image,
        "author": author,
        "publisher": {
            "@type": "Organization",
            "name": publisher_name,
            "logo": {"@type": "ImageObject", "url": publisher_logo},
        },
        "datePublished": date_published,
        "dateModified": date_modified or date_published,
    }
    return _clean(node)


def faq_page(questions: list[tuple[str, str]]) -> dict[str, object]:
    """Build an FAQPage node from question/answer pairs.

    Args:
        questions: List of ``(question, answer_html)`` tuples. Answers may
            contain limited HTML as allowed by the FAQ rich result.

    Returns:
        The JSON-LD node as a dict.

    Raises:
        ValueError: If ``questions`` is empty.
    """
    if not questions:
        raise ValueError("faq_page requires at least one question")
    return {
        "@context": SCHEMA_CONTEXT,
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {"@type": "Answer", "text": answer},
            }
            for question, answer in questions
        ],
    }


def how_to(
    name: str,
    steps: list[tuple[str, str]],
    description: str | None = None,
    total_time: str | None = None,
) -> dict[str, object]:
    """Build a HowTo node.

    Args:
        name: Title of the how-to.
        steps: List of ``(step_name, step_text)`` tuples in order.
        description: Optional summary of the overall task.
        total_time: Optional ISO 8601 duration, e.g. ``PT30M``.

    Returns:
        The JSON-LD node as a dict.

    Raises:
        ValueError: If ``steps`` is empty.
    """
    if not steps:
        raise ValueError("how_to requires at least one step")
    node: dict[str, object] = {
        "@context": SCHEMA_CONTEXT,
        "@type": "HowTo",
        "name": name,
        "description": description,
        "totalTime": total_time,
        "step": [
            {"@type": "HowToStep", "position": index, "name": step_name, "text": text}
            for index, (step_name, text) in enumerate(steps, start=1)
        ],
    }
    return _clean(node)


def breadcrumb(items: list[tuple[str, str]]) -> dict[str, object]:
    """Build a BreadcrumbList node.

    Args:
        items: Ordered list of ``(name, url)`` tuples from root to page.

    Returns:
        The JSON-LD node as a dict.

    Raises:
        ValueError: If ``items`` is empty.
    """
    if not items:
        raise ValueError("breadcrumb requires at least one item")
    return {
        "@context": SCHEMA_CONTEXT,
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": index, "name": name, "item": url}
            for index, (name, url) in enumerate(items, start=1)
        ],
    }


def organization(
    name: str,
    url: str,
    logo: str,
    same_as: list[str] | None = None,
) -> dict[str, object]:
    """Build an Organization node for brand knowledge-panel signals.

    Args:
        name: Organization name.
        url: Organization home page URL.
        logo: Absolute URL of the organization logo.
        same_as: Authoritative profile URLs (social, Wikipedia, etc.).

    Returns:
        The JSON-LD node as a dict.
    """
    node: dict[str, object] = {
        "@context": SCHEMA_CONTEXT,
        "@type": "Organization",
        "name": name,
        "url": url,
        "logo": logo,
        "sameAs": same_as,
    }
    return _clean(node)


def person(
    name: str,
    url: str,
    description: str | None = None,
    image: str | None = None,
    job_title: str | None = None,
    same_as: list[str] | None = None,
    works_for: str | None = None,
) -> dict[str, object]:
    """Build a Person node for an author profile page (E-E-A-T).

    Args:
        name: Author's name.
        url: Author profile page URL; Article nodes should reference it
            in their author field.
        description: Short credentials-focused bio.
        image: Absolute URL of the author's photo.
        job_title: Role or title, e.g. "Senior Editor".
        same_as: Authoritative profile URLs (LinkedIn, X, ORCID, etc.)
            that establish the author is a real person.
        works_for: Employer or publisher organization name.

    Returns:
        The JSON-LD node as a dict.
    """
    node: dict[str, object] = {
        "@context": SCHEMA_CONTEXT,
        "@type": "Person",
        "name": name,
        "url": url,
        "description": description,
        "image": image,
        "jobTitle": job_title,
        "sameAs": same_as,
        "worksFor": (
            {"@type": "Organization", "name": works_for} if works_for else None
        ),
    }
    return _clean(node)


def website_search(name: str, url: str, search_url_template: str) -> dict[str, object]:
    """Build a WebSite node with a SearchAction (sitelinks search box).

    Args:
        name: Site name.
        url: Site home page URL.
        search_url_template: Search URL with a ``{search_term_string}``
            placeholder, e.g. ``https://example.com/s?q={search_term_string}``.

    Returns:
        The JSON-LD node as a dict.
    """
    return {
        "@context": SCHEMA_CONTEXT,
        "@type": "WebSite",
        "name": name,
        "url": url,
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": search_url_template,
            },
            "query-input": "required name=search_term_string",
        },
    }


def product(
    name: str,
    description: str,
    image: list[str],
    price: str,
    currency: str,
    availability: str = "https://schema.org/InStock",
    rating_value: str | None = None,
    review_count: int | None = None,
) -> dict[str, object]:
    """Build a Product node with Offer and optional AggregateRating.

    Args:
        name: Product name.
        description: Product description.
        image: One or more absolute image URLs.
        price: Price as a string, e.g. ``"29.99"``.
        currency: ISO 4217 currency code, e.g. ``"USD"``.
        availability: schema.org availability URL.
        rating_value: Average rating, e.g. ``"4.6"``.
        review_count: Number of reviews backing the rating.

    Returns:
        The JSON-LD node as a dict.
    """
    node: dict[str, object] = {
        "@context": SCHEMA_CONTEXT,
        "@type": "Product",
        "name": name,
        "description": description,
        "image": image,
        "offers": {
            "@type": "Offer",
            "price": price,
            "priceCurrency": currency,
            "availability": availability,
        },
    }
    if rating_value is not None and review_count is not None:
        node["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": rating_value,
            "reviewCount": review_count,
        }
    return node


def recipe(
    name: str,
    image: list[str],
    ingredients: list[str],
    instructions: list[str],
    author_name: str | None = None,
    description: str | None = None,
    prep_time: str | None = None,
    cook_time: str | None = None,
) -> dict[str, object]:
    """Build a Recipe node.

    Args:
        name: Recipe title.
        image: One or more absolute image URLs.
        ingredients: Ingredient lines, one string each.
        instructions: Ordered instruction steps, one string each.
        author_name: Recipe author.
        description: Short recipe summary.
        prep_time: ISO 8601 duration, e.g. ``PT20M``.
        cook_time: ISO 8601 duration, e.g. ``PT30M``.

    Returns:
        The JSON-LD node as a dict.

    Raises:
        ValueError: If ``ingredients`` or ``instructions`` is empty.
    """
    if not ingredients or not instructions:
        raise ValueError("recipe requires ingredients and instructions")
    node: dict[str, object] = {
        "@context": SCHEMA_CONTEXT,
        "@type": "Recipe",
        "name": name,
        "image": image,
        "description": description,
        "author": {"@type": "Person", "name": author_name} if author_name else None,
        "prepTime": prep_time,
        "cookTime": cook_time,
        "recipeIngredient": ingredients,
        "recipeInstructions": [
            {"@type": "HowToStep", "position": index, "text": text}
            for index, text in enumerate(instructions, start=1)
        ],
    }
    return _clean(node)


def video(
    name: str,
    thumbnail_url: list[str],
    upload_date: str,
    description: str | None = None,
    duration: str | None = None,
    content_url: str | None = None,
    embed_url: str | None = None,
) -> dict[str, object]:
    """Build a VideoObject node.

    Args:
        name: Video title.
        thumbnail_url: One or more absolute thumbnail image URLs.
        upload_date: ISO 8601 date or datetime the video was published.
        description: Video summary.
        duration: ISO 8601 duration, e.g. ``PT8M32S``.
        content_url: Direct URL of the video file.
        embed_url: URL of the embeddable player.

    Returns:
        The JSON-LD node as a dict.
    """
    node: dict[str, object] = {
        "@context": SCHEMA_CONTEXT,
        "@type": "VideoObject",
        "name": name,
        "description": description,
        "thumbnailUrl": thumbnail_url,
        "uploadDate": upload_date,
        "duration": duration,
        "contentUrl": content_url,
        "embedUrl": embed_url,
    }
    return _clean(node)


def event(
    name: str,
    start_date: str,
    location_name: str,
    location_address: str,
    end_date: str | None = None,
    description: str | None = None,
    image: list[str] | None = None,
    organizer_name: str | None = None,
    is_online: bool = False,
    url: str | None = None,
) -> dict[str, object]:
    """Build an Event node.

    Args:
        name: Event title.
        start_date: ISO 8601 start datetime with timezone offset.
        location_name: Venue name, or the online event page name.
        location_address: Postal address, or the attendance URL for
            online events.
        end_date: ISO 8601 end datetime.
        description: Event summary.
        image: One or more absolute image URLs.
        organizer_name: Organizing person or organization name.
        is_online: Set ``True`` for online-only events, which switches the
            location to a ``VirtualLocation``.
        url: Canonical event page URL.

    Returns:
        The JSON-LD node as a dict.
    """
    location: dict[str, object]
    if is_online:
        location = {"@type": "VirtualLocation", "url": location_address}
    else:
        location = {
            "@type": "Place",
            "name": location_name,
            "address": location_address,
        }
    node: dict[str, object] = {
        "@context": SCHEMA_CONTEXT,
        "@type": "Event",
        "name": name,
        "startDate": start_date,
        "endDate": end_date,
        "eventAttendanceMode": (
            "https://schema.org/OnlineEventAttendanceMode"
            if is_online
            else "https://schema.org/OfflineEventAttendanceMode"
        ),
        "location": location,
        "description": description,
        "image": image,
        "url": url,
        "organizer": (
            {"@type": "Organization", "name": organizer_name}
            if organizer_name
            else None
        ),
    }
    return _clean(node)


def local_business(
    name: str,
    url: str,
    street_address: str,
    address_locality: str,
    postal_code: str,
    address_country: str,
    business_type: str = "LocalBusiness",
    address_region: str | None = None,
    telephone: str | None = None,
    price_range: str | None = None,
    image: list[str] | None = None,
    latitude: str | None = None,
    longitude: str | None = None,
    opening_hours: list[str] | None = None,
    same_as: list[str] | None = None,
) -> dict[str, object]:
    """Build a LocalBusiness node (Google local business rich result).

    Args:
        name: Business name, exactly as shown on the site.
        url: Business page URL.
        street_address: Street and number.
        address_locality: City or town.
        postal_code: Postal code.
        address_country: ISO 3166-1 alpha-2 country code, e.g. ``"DE"``.
        business_type: ``LocalBusiness`` or a schema.org subtype such as
            ``Restaurant``, ``Dentist``, or ``Store``.
        address_region: State, province, or region.
        telephone: Phone number with country code.
        price_range: Relative price band, e.g. ``"$$"``.
        image: One or more absolute image URLs.
        latitude: Decimal latitude as a string, paired with
            ``longitude``.
        longitude: Decimal longitude as a string.
        opening_hours: Hour ranges like ``"Mo-Fr 09:00-17:00"``.
        same_as: Authoritative profile URLs (maps listing, socials).

    Returns:
        The JSON-LD node as a dict.
    """
    geo: dict[str, object] | None = None
    if latitude is not None and longitude is not None:
        geo = {"@type": "GeoCoordinates", "latitude": latitude, "longitude": longitude}
    node: dict[str, object] = {
        "@context": SCHEMA_CONTEXT,
        "@type": business_type,
        "name": name,
        "url": url,
        "address": _clean(
            {
                "@type": "PostalAddress",
                "streetAddress": street_address,
                "addressLocality": address_locality,
                "addressRegion": address_region,
                "postalCode": postal_code,
                "addressCountry": address_country,
            }
        ),
        "telephone": telephone,
        "priceRange": price_range,
        "image": image,
        "geo": geo,
        "openingHours": opening_hours,
        "sameAs": same_as,
    }
    return _clean(node)


def job_posting(
    title: str,
    description: str,
    date_posted: str,
    organization_name: str,
    organization_url: str | None = None,
    address_locality: str | None = None,
    address_region: str | None = None,
    address_country: str | None = None,
    is_remote: bool = False,
    employment_type: str | None = None,
    valid_through: str | None = None,
    salary_value: str | None = None,
    salary_currency: str | None = None,
    salary_unit: str = "YEAR",
) -> dict[str, object]:
    """Build a JobPosting node (Google job posting rich result).

    Args:
        title: Job title only (no company name or location).
        description: Full description in HTML.
        date_posted: ISO 8601 date the posting went live.
        organization_name: Hiring organization.
        organization_url: Hiring organization's site URL.
        address_locality: City of the job location.
        address_region: State, province, or region of the job location.
        address_country: Country of the job location (required by
            Google for on-site jobs).
        is_remote: ``True`` marks the job 100 percent remote
            (``jobLocationType: TELECOMMUTE``); pass the applicant
            country via ``address_country``.
        employment_type: ``FULL_TIME``, ``PART_TIME``, ``CONTRACTOR``,
            etc.
        valid_through: ISO 8601 expiry datetime of the posting.
        salary_value: Base salary amount, e.g. ``"85000"``.
        salary_currency: ISO 4217 code backing ``salary_value``.
        salary_unit: ``HOUR``, ``DAY``, ``WEEK``, ``MONTH``, or
            ``YEAR``.

    Returns:
        The JSON-LD node as a dict.
    """
    organization: dict[str, object] = {
        "@type": "Organization",
        "name": organization_name,
    }
    if organization_url:
        organization["sameAs"] = organization_url
    location: dict[str, object] | None = None
    if address_locality or address_region or address_country:
        location = {
            "@type": "Place",
            "address": _clean(
                {
                    "@type": "PostalAddress",
                    "addressLocality": address_locality,
                    "addressRegion": address_region,
                    "addressCountry": address_country,
                }
            ),
        }
    salary: dict[str, object] | None = None
    if salary_value is not None and salary_currency is not None:
        salary = {
            "@type": "MonetaryAmount",
            "currency": salary_currency,
            "value": {
                "@type": "QuantitativeValue",
                "value": salary_value,
                "unitText": salary_unit,
            },
        }
    node: dict[str, object] = {
        "@context": SCHEMA_CONTEXT,
        "@type": "JobPosting",
        "title": title,
        "description": description,
        "datePosted": date_posted,
        "validThrough": valid_through,
        "hiringOrganization": organization,
        "jobLocation": location,
        "jobLocationType": "TELECOMMUTE" if is_remote else None,
        "applicantLocationRequirements": (
            {"@type": "Country", "name": address_country}
            if is_remote and address_country
            else None
        ),
        "employmentType": employment_type,
        "baseSalary": salary,
    }
    return _clean(node)


def course(
    name: str,
    description: str,
    provider_name: str,
    provider_url: str | None = None,
    url: str | None = None,
    course_mode: str | None = None,
    price: str | None = None,
    currency: str | None = None,
) -> dict[str, object]:
    """Build a Course node (Google course list rich result).

    Args:
        name: Course title.
        description: Concise course summary (Google shows ~60 chars).
        provider_name: Organization offering the course.
        provider_url: Provider's site URL.
        url: Course page URL.
        course_mode: ``online``, ``onsite``, or ``blended``; emitted on
            a ``hasCourseInstance``.
        price: Course price (``"0"`` for free), paired with
            ``currency``.
        currency: ISO 4217 code backing ``price``.

    Returns:
        The JSON-LD node as a dict.
    """
    provider: dict[str, object] = {"@type": "Organization", "name": provider_name}
    if provider_url:
        provider["sameAs"] = provider_url
    offers: dict[str, object] | None = None
    if price is not None and currency is not None:
        offers = {"@type": "Offer", "price": price, "priceCurrency": currency}
    node: dict[str, object] = {
        "@context": SCHEMA_CONTEXT,
        "@type": "Course",
        "name": name,
        "description": description,
        "url": url,
        "provider": provider,
        "offers": offers,
        "hasCourseInstance": (
            {"@type": "CourseInstance", "courseMode": course_mode}
            if course_mode
            else None
        ),
    }
    return _clean(node)


def software_application(
    name: str,
    operating_system: str,
    application_category: str,
    price: str = "0",
    currency: str = "USD",
    rating_value: str | None = None,
    rating_count: int | None = None,
    description: str | None = None,
    url: str | None = None,
    image: list[str] | None = None,
) -> dict[str, object]:
    """Build a SoftwareApplication node (Google software app result).

    Args:
        name: Application name.
        operating_system: e.g. ``"Windows, macOS"`` or ``"ANDROID"``.
        application_category: schema.org category, e.g.
            ``"DeveloperApplication"``.
        price: Price as a string; ``"0"`` for free apps.
        currency: ISO 4217 currency code.
        rating_value: Average rating, e.g. ``"4.6"`` - Google requires
            a rating or review for the rich result, so pass one when
            real ratings exist.
        rating_count: Number of ratings backing ``rating_value``.
        description: Short application summary.
        url: Application or download page URL.
        image: One or more absolute image URLs.

    Returns:
        The JSON-LD node as a dict.
    """
    node: dict[str, object] = {
        "@context": SCHEMA_CONTEXT,
        "@type": "SoftwareApplication",
        "name": name,
        "operatingSystem": operating_system,
        "applicationCategory": application_category,
        "description": description,
        "url": url,
        "image": image,
        "offers": {"@type": "Offer", "price": price, "priceCurrency": currency},
    }
    if rating_value is not None and rating_count is not None:
        node["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": rating_value,
            "ratingCount": rating_count,
        }
    return _clean(node)


def speakable(
    name: str,
    url: str,
    css_selectors: list[str] | None = None,
    xpaths: list[str] | None = None,
    page_type: str = "WebPage",
) -> dict[str, object]:
    """Build a page node with a SpeakableSpecification (voice/AEO).

    Marks the sections of a page best suited for text-to-speech
    playback by assistants. Point the selectors at the 2-3 most
    quotable, self-contained sections (headline, summary, key answer),
    around 20-30 seconds of speech - never the whole article.

    Args:
        name: Page or article title.
        url: Canonical page URL.
        css_selectors: CSS selectors of the speakable sections, e.g.
            ``[".article-summary", ".key-takeaways"]``. Prefer these
            over xpaths.
        xpaths: XPath expressions as an alternative to CSS selectors.
        page_type: ``WebPage``, ``Article``, ``BlogPosting``, or
            ``NewsArticle`` - must match the page's main node type.

    Returns:
        The JSON-LD node as a dict.

    Raises:
        ValueError: If neither ``css_selectors`` nor ``xpaths`` is
            given.
    """
    if not css_selectors and not xpaths:
        raise ValueError("speakable requires css_selectors or xpaths")
    return {
        "@context": SCHEMA_CONTEXT,
        "@type": page_type,
        "name": name,
        "url": url,
        "speakable": _clean(
            {
                "@type": "SpeakableSpecification",
                "cssSelector": css_selectors,
                "xpath": xpaths,
            }
        ),
    }


BUILDERS: dict[str, Callable[..., dict[str, object]]] = {
    "article": article,
    "faq": faq_page,
    "howto": how_to,
    "breadcrumb": breadcrumb,
    "organization": organization,
    "website": website_search,
    "product": product,
    "recipe": recipe,
    "video": video,
    "event": event,
    "person": person,
    "localbusiness": local_business,
    "jobposting": job_posting,
    "course": course,
    "softwareapp": software_application,
    "speakable": speakable,
}
