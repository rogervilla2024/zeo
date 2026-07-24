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
}
