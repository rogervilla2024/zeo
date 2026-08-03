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
