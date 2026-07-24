"""Site-agnostic SEO helpers for the seo-content-forge toolkit.

This package provides small, dependency-light building blocks that the
Claude Code agents and skills call from the command line:

- ``sitemap``: build standards-compliant XML sitemaps and sitemap indexes
  from a list of URL entries, including hreflang alternates and automatic
  splitting at the 50,000-URL limit.
- ``jsonld``: assemble schema.org JSON-LD for the rich-result types Google
  supports (Article, FAQPage, HowTo, BreadcrumbList, Organization,
  WebSite+SearchAction, Product).
- ``validate``: check a JSON-LD block for the required and recommended
  properties of its ``@type`` before publishing.

Nothing here is specific to any single website; every function takes the
site's data as input so the same toolkit serves any number of sites.
"""

from __future__ import annotations

__all__ = ["jsonld", "sitemap", "validate"]

__version__ = "0.1.0"
