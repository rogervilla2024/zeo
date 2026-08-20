"""Render every layout variant as a static preview gallery.

Forty variants are too many to pick from a text catalog: this module
renders one self-contained HTML preview per variant (light and dark)
from a canned sample homepage that exercises the shipped hooks -
header/nav, hero with stats and search, campaign banner, feature
card, post cards with category chips, entity cards, FAQ, newsletter,
footer - plus an index page that shows the whole fleet side by side.
The builder picks a variant by looking, not by reading.
"""

from __future__ import annotations

import html
from dataclasses import dataclass, field
from pathlib import Path

from seo_content_forge.theme_css import (
    VARIANTS,
    ThemeTokens,
    compose_css,
)

_THUMB = (
    "data:image/svg+xml;utf8,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 640 360'%3E"
    "%3Crect width='640' height='360' fill='%23{bg}'/%3E"
    "%3Ccircle cx='320' cy='180' r='90' fill='%23{fg}' opacity='0.55'/%3E"
    "%3C/svg%3E"
)


def _thumb(bg: str, fg: str) -> str:
    return _THUMB.format(bg=bg, fg=fg)


def _post_card(title: str, chip: str, bg: str, fg: str) -> str:
    return f"""<li>
  <img src="{_thumb(bg, fg)}" alt="" width="640" height="360">
  <span class="post-category">{chip}</span>
  <a href="#">{title}</a>
  <p>Sample summary line so the card shows body rhythm.</p>
</li>"""


def sample_body(variant: str) -> str:
    """The canned homepage markup every preview renders.

    Args:
        variant: Variant name, shown in the masthead.

    Returns:
        HTML body markup using the golden template's class hooks.
    """
    cards = "\n".join(
        (
            _post_card("The complete starter guide", "Guides", "b8c7d1", "51606e"),
            _post_card("Seven honest comparisons", "Reviews", "d1c4b0", "6e5c44"),
            _post_card("What changed this season", "News", "bcd1b8", "4e6b52"),
        )
    )
    return f"""<header class="container">
  <a class="site-brand" href="#">{html.escape(variant)} sample</a>
  <nav class="site-nav" aria-label="Primary">
    <a href="#" aria-current="page">Guides</a>
    <a href="#">Reviews</a>
    <a href="#">About</a>
  </nav>
</header>
<main class="container">
  <section class="site-hero">
    <h1>Field guide to the sample niche</h1>
    <p>Evidence-based guides, honest comparisons, and practical
    answers - the same content in every preview, so only the design
    changes.</p>
    <p class="hero-stats">128 entries &#183; 6 areas &#183; 42 guides</p>
    <form class="hero-search" action="#" method="get">
      <input type="search" name="q" placeholder="Search the guide">
      <button type="submit">Search</button>
    </form>
  </section>
  <aside class="cta-banner">
    <p>Season guide is out: twelve options compared on evidence.</p>
    <a href="#">Read the guide</a>
  </aside>
  <div class="with-aside">
    <section class="home-main">
      <a class="feature-card" href="#">
        <img src="{_thumb("8ea3b5", "2f4356")}" alt="" width="1600"
          height="900">
        <div class="feature-body">
          <h2>The one comparison readers start with</h2>
          <p>Why the obvious pick is not the best pick this year.</p>
        </div>
      </a>
      <h2 class="section-title">Latest articles</h2>
      <ul class="post-list">
{cards}
      </ul>
      <h2 class="section-title"><a href="#">Browse the catalog</a>
        <a class="view-all" href="#">View all</a></h2>
      <ul class="entity-grid">
        <li class="entity-card">
          <img src="{_thumb("a8bfae", "3d5c49")}" alt="" width="640"
            height="360">
          <span class="entity-badge">Editor's pick</span>
          <a href="#">Harbor View House</a>
          <p>Quiet rooms over the marina with a generous breakfast.</p>
          <p class="entity-score"><span>Editor's score</span> 9.1</p>
          <p class="entity-price">from 120 EUR</p>
          <ul class="entity-attrs">
            <li><span>Area</span> Old town</li>
            <li><span>Rooms</span> 24</li>
          </ul>
          <a class="entity-cta" href="#"
            rel="sponsored nofollow noopener">See prices</a>
        </li>
        <li class="entity-card">
          <img src="{_thumb("c9b6a8", "6b4f3a")}" alt="" width="640"
            height="360">
          <a href="#">Cedar Ridge Lodge</a>
          <p>Hillside cabins with a long view and short trails.</p>
          <p class="entity-score"><span>Editor's score</span> 8.4</p>
          <p class="entity-price">from 95 EUR</p>
          <ul class="entity-attrs">
            <li><span>Area</span> Ridge</li>
            <li><span>Rooms</span> 12</li>
          </ul>
          <a class="entity-cta" href="#"
            rel="sponsored nofollow noopener">See prices</a>
        </li>
      </ul>
      <section class="faq" aria-label="FAQ">
        <h2>Frequently asked questions</h2>
        <details><summary>Who writes the guides?</summary>
          <p>An editorial team, with sources cited in every piece.</p>
        </details>
        <details><summary>How are picks chosen?</summary>
          <p>Evidence first; sponsors never influence rankings.</p>
        </details>
      </section>
      <div class="newsletter-cta">
        <h2>Get new articles by email</h2>
        <p>One email when we publish. No spam.</p>
        <form action="#" method="post">
          <input type="email" name="email" placeholder="you@example.com">
          <button type="submit">Subscribe</button>
        </form>
      </div>
    </section>
    <aside class="site-aside">
      <h2>Popular</h2>
      <ul>
        <li><a href="#">The complete starter guide</a></li>
        <li><a href="#">Seven honest comparisons</a></li>
        <li><a href="#">What changed this season</a></li>
      </ul>
    </aside>
  </div>
</main>
<footer class="site-footer">
  <div class="container">
    <p>Sample site. All rights reserved.</p>
    <a href="#">About</a> <a href="#">Contact</a> <a href="#">Privacy</a>
  </div>
</footer>"""


def build_variant_preview(
    variant: str, tokens: ThemeTokens, dark: bool = False
) -> str:
    """One variant's full self-contained preview document.

    Args:
        variant: Variant name to compose.
        tokens: Base tokens; the variant field is overridden.
        dark: Render with the dark palette forced via data-theme.

    Returns:
        A complete HTML document string.
    """
    tokens = ThemeTokens(
        palette=tokens.palette,
        dark_palette=tokens.dark_palette,
        heading_font=tokens.heading_font,
        body_font=tokens.body_font,
        radius=tokens.radius,
        max_width=tokens.max_width,
        site_width=tokens.site_width,
        variant=variant,
        motion=tokens.motion,
        finish=tokens.finish,
    )
    theme_attr = ' data-theme="dark"' if dark else ' data-theme="light"'
    scheme = "dark" if dark else "light"
    return f"""<!doctype html>
<html lang="en"{theme_attr}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<meta name="color-scheme" content="{scheme}">
<title>{html.escape(variant)} preview ({scheme})</title>
<style>
{compose_css(tokens)}
</style>
</head>
<body>
{sample_body(variant)}
</body>
</html>
"""


def build_index(variants: tuple[str, ...] = VARIANTS) -> str:
    """The gallery page: every variant, light and dark, side by side.

    Args:
        variants: Variant names to include.

    Returns:
        A complete HTML document string with lazy iframes.
    """
    cells = "\n".join(
        f"""<section class="cell">
  <h2>{html.escape(variant)}</h2>
  <div class="pair">
    <iframe src="{variant}.html" loading="lazy" title="{variant} light"></iframe>
    <iframe src="{variant}-dark.html" loading="lazy" title="{variant} dark"></iframe>
  </div>
  <p><a href="{variant}.html">light</a> &#183;
    <a href="{variant}-dark.html">dark</a></p>
</section>"""
        for variant in variants
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Variant gallery ({len(variants)})</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem;
  background: #f3f4f6; color: #111827; }}
h1 {{ font-size: 1.4rem; }}
.grid {{ display: grid; gap: 2rem;
  grid-template-columns: repeat(auto-fill, minmax(30rem, 1fr)); }}
.cell {{ background: #fff; border: 1px solid #d1d5db; border-radius: 8px;
  padding: 1rem; }}
.cell h2 {{ margin: 0 0 0.6rem; font-size: 1.05rem; }}
.pair {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; }}
.pair iframe {{ width: 100%; aspect-ratio: 9 / 14; border: 1px solid
  #e5e7eb; border-radius: 6px; background: #fff; }}
.cell p {{ margin: 0.6rem 0 0; font-size: 0.9rem; }}
</style>
</head>
<body>
<h1>Variant gallery: {len(variants)} baselines, light + dark</h1>
<p>Same sample content in every frame - only the character layer
changes. Pick by mood, then art-direct on top (design-theme).</p>
<div class="grid">
{cells}
</div>
</body>
</html>
"""


def write_gallery(output: Path, tokens: ThemeTokens) -> int:
    """Write the full gallery: index plus light/dark previews.

    Args:
        output: Directory to write into (created if missing).
        tokens: Base tokens (palette/fonts) shared by every preview.

    Returns:
        Number of files written.
    """
    output.mkdir(parents=True, exist_ok=True)
    count = 0
    for variant in VARIANTS:
        for dark in (False, True):
            suffix = "-dark" if dark else ""
            path = output / f"{variant}{suffix}.html"
            path.write_text(
                build_variant_preview(variant, tokens, dark=dark),
                encoding="utf-8",
            )
            count += 1
    (output / "index.html").write_text(build_index(), encoding="utf-8")
    return count + 1


# --- Anatomy gallery -------------------------------------------------
# The variant gallery answers "which THEME?"; this one answers "which
# FIRST SCREEN?". One page per A recipe (recipes.md, "Page
# anatomies"), all on the SAME variant, so only the structure changes
# between frames: hero mode, rail side and content, and the block
# stack. Picking homepage.hero/aside/rail becomes a visual decision
# too.

@dataclass
class Anatomy:
    """One A recipe: the knobs that shape the first screen."""

    label: str
    hero: str = "standard"
    aside: str = "none"
    rail: str = "popular"
    lead: list[str] = field(default_factory=list)
    main: list[str] = field(default_factory=list)
    search: bool = False


ANATOMIES: dict[str, Anatomy] = {
    "A1": Anatomy("Story lead", hero="standard", aside="right",
                  main=["feature", "latest"]),
    "A2": Anatomy("Booking funnel", hero="search",
                  lead=["directory:list", "comparison"], main=["latest"]),
    "A3": Anatomy("Marketplace", hero="none",
                  lead=["directory:shelves", "comparison"],
                  main=["latest:rows"], search=True),
    "A4": Anatomy("Feed board", hero="compact", aside="right",
                  main=["feed"], search=True),
    "A5": Anatomy("Dense portal", hero="compact", aside="right",
                  main=["latest:rows", "strips", "newsletter"]),
    "A6": Anatomy("Reading room", hero="standard",
                  main=["feature", "latest"]),
    "A7": Anatomy("Cover story", hero="cover", aside="right",
                  main=["feature:overlay", "latest"]),
    "A8": Anatomy("Signup first", hero="signup", main=["latest:rows"]),
    "A9": Anatomy("Wire", hero="compact", aside="right", lead=["ticker"],
                  main=["feed:compact"], search=True),
    "A10": Anatomy("Filter rail", hero="compact", aside="left",
                   rail="facets", lead=["directory:list", "comparison"]),
    "A11": Anatomy("A-Z index", hero="compact",
                   lead=["directory:index"], main=["latest:rows"]),
    "A12": Anatomy("Tile wall", hero="none", main=["latest:tiles"]),
}

_COVER = _thumb("31435a", "7d95ad")


def _anatomy_hero(mode: str) -> str:
    stats = '<p class="hero-stats">128 entries &#183; 6 areas</p>'
    search = (
        '<form class="hero-search" action="#" method="get">'
        '<input type="search" name="q" placeholder="Search">'
        "<button type=\"submit\">Search</button></form>"
    )
    signup = (
        '<div class="newsletter-cta"><h2>Get the briefing</h2>'
        "<p>One email when we publish.</p>"
        '<form action="#" method="post">'
        '<input type="email" name="email" placeholder="you@example.com">'
        "<button type=\"submit\">Subscribe</button></form></div>"
    )
    title = "<h1>Field guide to the sample niche</h1>"
    tagline = "<p>The same content in every frame - only the anatomy changes.</p>"
    if mode == "none":
        return '<h1 class="visually-hidden">Sample site</h1>'
    if mode == "cover":
        img = (
            f'<img class="site-hero-cover" src="{_COVER}" alt="" '
            'width="1600" height="900">'
        )
        return (
            f'<section class="site-hero hero--cover">{img}{title}'
            f"{tagline}</section>"
        )
    if mode == "signup":
        return (
            f'<section class="site-hero hero--signup">{title}{tagline}'
            f"{signup}</section>"
        )
    if mode == "search":
        return (
            f'<section class="site-hero hero--search">{title}{tagline}'
            f"{stats}{search}</section>"
        )
    if mode == "compact":
        return (
            f'<section class="site-hero hero--compact">{title}{tagline}'
            "</section>"
        )
    return f'<section class="site-hero">{title}{tagline}{stats}</section>'


def _anatomy_entity(title: str, bg: str, fg: str) -> str:
    return f"""<li class="entity-card">
  <img src="{_thumb(bg, fg)}" alt="" width="640" height="360">
  <a href="#">{title}</a>
  <p>Short summary so the card shows rhythm.</p>
  <p class="entity-score"><span>Editor's score</span> 8.9</p>
  <p class="entity-price">from 110 EUR</p>
  <a class="entity-cta" href="#" rel="sponsored nofollow noopener">See
  prices</a>
</li>"""


def _anatomy_block(block: str) -> str:
    base, _, style = block.partition(":")
    if base == "ticker":
        items = "".join(
            f'<li><a href="#">Wire headline number {i}</a></li>'
            for i in range(1, 5)
        )
        return (
            '<div class="ticker"><span class="ticker-label">Latest</span>'
            f"<ul>{items}</ul></div>"
        )
    if base == "directory":
        cls = f" entity-grid--{style}" if style else ""
        cards = "\n".join(
            (
                _anatomy_entity("Harbor View House", "a8bfae", "3d5c49"),
                _anatomy_entity("Cedar Ridge Lodge", "c9b6a8", "6b4f3a"),
                _anatomy_entity("Old Town Rooms", "b8c7d1", "51606e"),
            )
        )
        return (
            '<section class="directory"><h2 class="section-title">Browse'
            f' the catalog</h2><ul class="entity-grid{cls}">{cards}</ul>'
            "</section>"
        )
    if base == "comparison":
        rows = "".join(
            f'<tr><td><a href="#">{name}</a></td><td>{area}</td>'
            f"<td>{rooms}</td></tr>"
            for name, area, rooms in (
                ("Harbor View House", "Old town", "24"),
                ("Cedar Ridge Lodge", "Ridge", "12"),
            )
        )
        return (
            '<div class="comparison"><table><thead><tr><th>Compare</th>'
            "<th>Area</th><th>Rooms</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></div>"
        )
    if base == "feature":
        cls = f" feature-card--{style}" if style else ""
        return (
            f'<a class="feature-card{cls}" href="#">'
            f'<img src="{_thumb("8ea3b5", "2f4356")}" alt="" width="1600" '
            'height="900"><div class="feature-body">'
            "<h2>The one comparison readers start with</h2>"
            "<p>Why the obvious pick is not the best pick.</p></div></a>"
        )
    if base == "latest":
        cls = f" post-list--{style}" if style else ""
        cards = "\n".join(
            (
                _post_card("The complete starter guide", "Guides",
                           "b8c7d1", "51606e"),
                _post_card("Seven honest comparisons", "Reviews",
                           "d1c4b0", "6e5c44"),
                _post_card("What changed this season", "News",
                           "bcd1b8", "4e6b52"),
            )
        )
        return (
            '<h2 class="section-title">Latest articles</h2>'
            f'<ul class="post-list{cls}">{cards}</ul>'
        )
    if base == "feed":
        cls = " feed--compact" if style == "compact" else ""
        items = "".join(
            '<li class="feed-item">'
            f'<img src="{_thumb("b8c7d1", "51606e")}" alt="" width="640" '
            'height="360"><div class="feed-body">'
            '<span class="post-category">Guides</span>'
            f'<a href="#">Feed story number {i}</a>'
            "<p>One-line summary for the stream.</p>"
            '<p class="feed-meta"><time datetime="2026-01-01">2026-01-01'
            "</time></p></div></li>"
            for i in range(1, 6)
        )
        return f'<ol class="feed{cls}">{items}</ol>'
    if base == "strips":
        cards = "\n".join(
            (
                _post_card("Strip story one", "Guides", "b8c7d1", "51606e"),
                _post_card("Strip story two", "Guides", "d1c4b0", "6e5c44"),
            )
        )
        return (
            '<section class="category-strip"><h2 class="section-title">'
            f'<a href="#">Guides</a></h2><ul class="post-list">{cards}</ul>'
            "</section>"
        )
    if base == "newsletter":
        return (
            '<div class="newsletter-cta"><h2>Get new articles by email</h2>'
            "<p>One email when we publish. No spam.</p>"
            '<form action="#" method="post">'
            '<input type="email" name="email" placeholder="you@example.com">'
            "<button type=\"submit\">Subscribe</button></form></div>"
        )
    return ""


def _anatomy_rail(mode: str) -> str:
    if mode == "facets":
        items = "".join(
            f'<li><a href="#">{value}</a></li>'
            for value in ("Old town", "Ridge", "Coast", "Breakfast",
                          "All inclusive")
        )
        return (
            '<aside class="site-aside"><h2>Filters</h2>'
            f"<ul>{items}</ul></aside>"
        )
    if mode == "categories":
        items = "".join(
            f'<li><a href="#">{name}</a> <span class="rail-count">{n}</span>'
            "</li>"
            for name, n in (("Guides", 18), ("Reviews", 11), ("News", 7))
        )
        return (
            '<aside class="site-aside"><h2>Topics</h2>'
            f"<ul>{items}</ul></aside>"
        )
    if mode == "newsletter":
        return (
            '<aside class="site-aside"><div class="newsletter-cta">'
            "<h2>Get the briefing</h2>"
            '<form action="#" method="post">'
            '<input type="email" name="email" placeholder="you@example.com">'
            "<button type=\"submit\">Subscribe</button></form></div></aside>"
        )
    items = "".join(
        f'<li><a href="#">{title}</a></li>'
        for title in ("The complete starter guide", "Seven honest "
                      "comparisons", "What changed this season")
    )
    return f'<aside class="site-aside"><h2>Popular</h2><ul>{items}</ul></aside>'


def anatomy_body(variant: str, code: str) -> str:
    """The canned homepage markup for one A recipe.

    Args:
        variant: Variant name, shown in the masthead.
        code: Anatomy code (A1-A12).

    Returns:
        HTML body markup mirroring the golden homepage's anatomy
        composition: hero mode, lead zone, main zone beside the rail,
        and the rail-beside fallback when only lead blocks are active.
    """
    spec = ANATOMIES[code]
    lead = spec.lead
    main = spec.main
    aside = spec.aside
    rail = spec.rail
    header_search = (
        '<form class="header-search" action="#" method="get">'
        '<input type="search" name="q" placeholder="Search">'
        "<button type=\"submit\">Search</button></form>"
        if spec.search
        else ""
    )
    header = (
        '<header class="container">'
        f'<a class="site-brand" href="#">{html.escape(variant)} '
        f"&#183; {code}</a>{header_search}"
        '<nav class="site-nav" aria-label="Primary">'
        '<a href="#" aria-current="page">Guides</a>'
        '<a href="#">Reviews</a><a href="#">About</a></nav></header>'
    )
    lead_html = "\n".join(_anatomy_block(block) for block in lead)
    main_html = "\n".join(_anatomy_block(block) for block in main)
    rail_html = _anatomy_rail(rail) if aside != "none" else ""
    left = " left" if aside == "left" else ""
    if main:
        columns = (
            f'<div class="with-aside{left}">'
            f'<section class="home-main">{main_html}</section>'
            f"{rail_html}</div>"
            if rail_html
            else f'<section class="home-main">{main_html}</section>'
        )
        content = f"{lead_html}\n{columns}"
    elif rail_html:
        # Lead-only anatomies dock the rail BESIDE the lead content
        # (the booking results-page shape) instead of dangling it
        # under an empty main column. Mirrors the golden homepage's
        # DOM: the rail stays inside its .with-aside wrapper (whose
        # empty main column the rail-beside grid hides).
        content = (
            f'<div class="rail-beside{left}">{lead_html}'
            f'<div class="with-aside{left}">'
            f'<section class="home-main"></section>{rail_html}</div></div>'
        )
    else:
        content = lead_html
    hero = _anatomy_hero(spec.hero)
    return (
        f"{header}\n<main class=\"container\">\n{hero}\n{content}\n</main>\n"
        '<footer class="site-footer"><div class="container">'
        "<p>Sample site. All rights reserved.</p>"
        '<a href="#">About</a> <a href="#">Privacy</a></div></footer>'
    )


def build_anatomy_preview(
    variant: str, code: str, tokens: ThemeTokens
) -> str:
    """One anatomy's full self-contained preview document."""
    tokens = ThemeTokens(
        palette=tokens.palette,
        dark_palette=tokens.dark_palette,
        heading_font=tokens.heading_font,
        body_font=tokens.body_font,
        radius=tokens.radius,
        max_width=tokens.max_width,
        site_width=tokens.site_width,
        variant=variant,
        motion=tokens.motion,
        finish=tokens.finish,
    )
    spec = ANATOMIES[code]
    return f"""<!doctype html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<meta name="color-scheme" content="light">
<title>{code} {html.escape(spec.label)} ({html.escape(variant)})</title>
<style>
{compose_css(tokens)}
</style>
</head>
<body>
{anatomy_body(variant, code)}
</body>
</html>
"""


def build_anatomy_index(variant: str) -> str:
    """The anatomy gallery page: all twelve A recipes side by side."""
    cells = "\n".join(
        f"""<section class="cell">
  <h2>{code} - {html.escape(spec.label)}</h2>
  <p class="knobs">hero: {spec.hero} &#183; aside: {spec.aside}
    &#183; rail: {spec.rail}</p>
  <iframe src="{code}.html" loading="lazy"
    title="{code} {html.escape(spec.label)}"></iframe>
  <p><a href="{code}.html">open</a></p>
</section>"""
        for code, spec in ANATOMIES.items()
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Anatomy gallery ({html.escape(variant)})</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem;
  background: #f3f4f6; color: #111827; }}
h1 {{ font-size: 1.4rem; }}
.grid {{ display: grid; gap: 2rem;
  grid-template-columns: repeat(auto-fill, minmax(24rem, 1fr)); }}
.cell {{ background: #fff; border: 1px solid #d1d5db; border-radius: 8px;
  padding: 1rem; }}
.cell h2 {{ margin: 0 0 0.2rem; font-size: 1.05rem; }}
.cell .knobs {{ margin: 0 0 0.6rem; font-size: 0.8rem; color: #6b7280; }}
.cell iframe {{ width: 100%; aspect-ratio: 9 / 14; border: 1px solid
  #e5e7eb; border-radius: 6px; background: #fff; }}
.cell p {{ margin: 0.6rem 0 0; font-size: 0.9rem; }}
</style>
</head>
<body>
<h1>Anatomy gallery: 12 first screens, one variant ({html.escape(variant)})</h1>
<p>Same content and same theme in every frame - only the ANATOMY
changes: hero mode, rail side and content, block stack. Pick the A
recipe by what the visitor comes to DO (recipes.md), then set
homepage.hero / aside / rail and the blocks.</p>
<div class="grid">
{cells}
</div>
</body>
</html>
"""


def write_anatomy_gallery(
    output: Path, tokens: ThemeTokens, variant: str
) -> int:
    """Write the anatomy gallery: index plus one page per A recipe.

    Args:
        output: Directory to write into (created if missing).
        tokens: Base tokens (palette/fonts) shared by every preview.
        variant: The single variant every frame renders with.

    Returns:
        Number of files written.
    """
    output.mkdir(parents=True, exist_ok=True)
    for code in ANATOMIES:
        (output / f"{code}.html").write_text(
            build_anatomy_preview(variant, code, tokens), encoding="utf-8"
        )
    (output / "index.html").write_text(
        build_anatomy_index(variant), encoding="utf-8"
    )
    return len(ANATOMIES) + 1
