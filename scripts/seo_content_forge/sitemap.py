"""Build standards-compliant XML sitemaps and sitemap indexes.

The sitemap protocol caps a single sitemap file at 50,000 URLs and 50 MB
uncompressed. :func:`build_sitemaps` transparently splits larger inputs
into multiple files and emits a sitemap index that references them.

All inputs are plain data structures, so this module is fully
site-agnostic: callers supply the URL entries and a public base path for
the generated files.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from xml.sax.saxutils import escape

MAX_URLS_PER_FILE: int = 50_000

_URLSET_OPEN: str = (
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
    'xmlns:xhtml="http://www.w3.org/1999/xhtml" '
    'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">'
)
_SITEMAPINDEX_OPEN: str = (
    '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
)
_ALLOWED_CHANGEFREQ: frozenset[str] = frozenset(
    {"always", "hourly", "daily", "weekly", "monthly", "yearly", "never"}
)


@dataclass(slots=True)
class Alternate:
    """An hreflang alternate for a URL.

    Args:
        hreflang: BCP-47 language (or ``x-default``) code.
        href: Absolute URL of the alternate version.
    """

    hreflang: str
    href: str


@dataclass(slots=True)
class ImageRef:
    """A content image on a page, for Google image sitemaps.

    Args:
        loc: Absolute URL of the image file.
    """

    loc: str

    def __post_init__(self) -> None:
        if not self.loc:
            raise ValueError("ImageRef.loc must be a non-empty URL")


@dataclass(slots=True)
class UrlEntry:
    """A single ``<url>`` entry in a sitemap.

    Args:
        loc: Absolute URL of the page.
        lastmod: Last modification date (``YYYY-MM-DD`` or ISO 8601).
        changefreq: One of the sitemap protocol change frequencies.
        priority: Relative priority between 0.0 and 1.0.
        alternates: hreflang alternates for internationalized pages.
        images: Content images on the page, emitted as image-sitemap
            entries (max 1000 per page per the Google spec).
    """

    loc: str
    lastmod: str | None = None
    changefreq: str | None = None
    priority: float | None = None
    alternates: list[Alternate] = field(default_factory=list)
    images: list[ImageRef] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.loc:
            raise ValueError("UrlEntry.loc must be a non-empty URL")
        if self.changefreq is not None and self.changefreq not in _ALLOWED_CHANGEFREQ:
            raise ValueError(
                f"changefreq {self.changefreq!r} is not one of "
                f"{sorted(_ALLOWED_CHANGEFREQ)}"
            )
        if self.priority is not None and not 0.0 <= self.priority <= 1.0:
            raise ValueError("priority must be between 0.0 and 1.0")
        if len(self.images) > 1000:
            raise ValueError("at most 1000 images per URL (Google image sitemap limit)")


def _render_url(entry: UrlEntry) -> str:
    """Render one ``<url>`` element as an XML string."""
    parts: list[str] = [f"    <loc>{escape(entry.loc)}</loc>"]
    if entry.lastmod:
        parts.append(f"    <lastmod>{escape(entry.lastmod)}</lastmod>")
    if entry.changefreq:
        parts.append(f"    <changefreq>{entry.changefreq}</changefreq>")
    if entry.priority is not None:
        parts.append(f"    <priority>{entry.priority:.1f}</priority>")
    for alt in entry.alternates:
        parts.append(
            '    <xhtml:link rel="alternate" '
            f'hreflang="{escape(alt.hreflang, {chr(34): "&quot;"})}" '
            f'href="{escape(alt.href, {chr(34): "&quot;"})}"/>'
        )
    for image in entry.images:
        parts.append(
            "    <image:image>\n"
            f"      <image:loc>{escape(image.loc)}</image:loc>\n"
            "    </image:image>"
        )
    body = "\n".join(parts)
    return f"  <url>\n{body}\n  </url>"


def render_urlset(entries: list[UrlEntry]) -> str:
    """Render a list of URL entries as a complete ``<urlset>`` document.

    Args:
        entries: URL entries to include. Must not exceed
            :data:`MAX_URLS_PER_FILE`.

    Returns:
        The full XML document as a string.

    Raises:
        ValueError: If ``entries`` exceeds the per-file URL limit.
    """
    if len(entries) > MAX_URLS_PER_FILE:
        raise ValueError(
            f"{len(entries)} URLs exceed the {MAX_URLS_PER_FILE} per-file limit; "
            "use build_sitemaps() to split automatically"
        )
    urls = "\n".join(_render_url(entry) for entry in entries)
    header = '<?xml version="1.0" encoding="UTF-8"?>'
    return f"{header}\n{_URLSET_OPEN}\n{urls}\n</urlset>\n"


def render_index(sitemap_locs: list[str], lastmod: str | None = None) -> str:
    """Render a ``<sitemapindex>`` referencing child sitemap files.

    Args:
        sitemap_locs: Absolute URLs of the child sitemap files.
        lastmod: Optional last modification date applied to every child.

    Returns:
        The full sitemap-index XML document as a string.
    """
    items: list[str] = []
    for loc in sitemap_locs:
        line = f"  <sitemap>\n    <loc>{escape(loc)}</loc>"
        if lastmod:
            line += f"\n    <lastmod>{escape(lastmod)}</lastmod>"
        line += "\n  </sitemap>"
        items.append(line)
    body = "\n".join(items)
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n{_SITEMAPINDEX_OPEN}\n{body}\n'
        "</sitemapindex>\n"
    )


def build_sitemaps(
    entries: list[UrlEntry],
    index_base_url: str,
    file_prefix: str = "sitemap",
    lastmod: str | None = None,
) -> dict[str, str]:
    """Build one or more sitemap files, splitting past the URL limit.

    When ``entries`` fits in a single file, the result contains just
    ``{"sitemap.xml": <urlset>}``. Otherwise the URLs are chunked into
    ``sitemap-1.xml``, ``sitemap-2.xml``, ... and a ``sitemap-index.xml``
    that references each chunk at ``index_base_url``.

    Args:
        entries: All URL entries for the site.
        index_base_url: Public base URL where the files will be hosted,
            used to build absolute ``<loc>`` values in the index
            (e.g. ``https://example.com``).
        file_prefix: Base filename for split sitemap chunks.
        lastmod: Optional last modification date for the index entries.

    Returns:
        Mapping of output filename to XML content.

    Raises:
        ValueError: If ``entries`` is empty.
    """
    if not entries:
        raise ValueError("entries must contain at least one URL")

    if len(entries) <= MAX_URLS_PER_FILE:
        return {f"{file_prefix}.xml": render_urlset(entries)}

    base = index_base_url.rstrip("/")
    files: dict[str, str] = {}
    child_locs: list[str] = []
    for chunk_index in range(0, len(entries), MAX_URLS_PER_FILE):
        chunk = entries[chunk_index : chunk_index + MAX_URLS_PER_FILE]
        number = chunk_index // MAX_URLS_PER_FILE + 1
        filename = f"{file_prefix}-{number}.xml"
        files[filename] = render_urlset(chunk)
        child_locs.append(f"{base}/{filename}")

    files[f"{file_prefix}-index.xml"] = render_index(child_locs, lastmod=lastmod)
    return files
