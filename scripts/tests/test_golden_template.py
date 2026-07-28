"""Tests keeping templates/golden in sync with its template sources."""

from __future__ import annotations

import json
from pathlib import Path

from seo_content_forge.theme_css import compose_css, from_config

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = ROOT / "templates" / "golden"
THEME = ROOT / "templates" / "theme"

# Golden file -> source of truth it must stay byte-identical to.
SYNCED: dict[str, Path] = {
    "src/layouts/BaseLayout.astro": THEME / "BaseLayout.astro",
    "public/robots.txt": ROOT / "templates" / "robots.txt",
    "public/_headers": ROOT / "templates" / "deploy" / "_headers",
    "public/_redirects": ROOT / "templates" / "deploy" / "_redirects",
    "site.config.json": ROOT / "templates" / "site.config.example.json",
}


def test_component_copies_match_theme_sources() -> None:
    components = sorted((GOLDEN / "src" / "components").glob("*.astro"))
    assert components, "golden template has no components"
    for copy in components:
        source = THEME / copy.name
        assert source.is_file(), f"{copy.name} has no source in templates/theme"
        assert copy.read_bytes() == source.read_bytes(), (
            f"{copy.name} drifted from templates/theme; re-copy the original"
        )


def test_synced_files_match_sources() -> None:
    for relative, source in SYNCED.items():
        copy = GOLDEN / relative
        assert copy.is_file(), f"golden template is missing {relative}"
        assert copy.read_bytes() == source.read_bytes(), (
            f"{relative} drifted from {source.relative_to(ROOT)}"
        )


def test_tokens_css_regenerates_from_golden_config() -> None:
    config = json.loads((GOLDEN / "site.config.json").read_text())
    expected = compose_css(from_config(config))
    actual = (GOLDEN / "src" / "styles" / "tokens.css").read_text()
    assert actual == expected, (
        "tokens.css is stale; regenerate with generate_theme_css.py "
        "--config templates/golden/site.config.json"
    )


def test_required_skeleton_files_exist() -> None:
    required = [
        "README.md",
        "CLAUDE.md",
        "package.json",
        "astro.config.mjs",
        "tsconfig.json",
        ".gitignore",
        "src/content.config.ts",
        "src/lib/slugify.ts",
        "src/styles/site.css",
        "src/pages/index.astro",
        "src/pages/blog/index.astro",
        "src/pages/[...slug].astro",
        "src/pages/[category_base]/[slug].astro",
        "src/pages/authors/[slug].astro",
        "src/pages/search.astro",
        "src/pages/rss.xml.js",
        "src/pages/sitemap.xml.js",
        "src/pages/llms.txt.js",
        "src/pages/api/articles.json.js",
        "public/.well-known/api-catalog",
        "src/pages/[directory_base]/[facet]/[value].astro",
        "src/pages/about.astro",
        "src/pages/contact.astro",
        "src/pages/privacy-policy.astro",
        "src/pages/terms-of-service.astro",
        "src/pages/disclaimer.astro",
    ]
    for relative in required:
        assert (GOLDEN / relative).is_file(), f"missing {relative}"


def test_ui_strings_config_and_wiring() -> None:
    config = json.loads((GOLDEN / "site.config.json").read_text())
    ui = config["ui"]
    required = {
        "latest_articles", "key_takeaways", "on_this_page", "faq_title",
        "read_next", "by", "published", "updated", "min_read",
        "footer_explore", "footer_trust", "rights", "search",
        "search_placeholder", "home", "skip_to_content", "theme_toggle",
        "about", "contact", "privacy_policy", "terms_of_service", "disclaimer",
        "blog", "popular", "category_description", "author_articles",
        "about_the_author", "blog_description",
        "quick_facts", "how_to_title", "directory_title", "comparison_title",
        "facet_description", "entity_cta", "thread_replies",
        "answers_count", "view_all",
    }
    assert required <= set(ui), f"missing ui keys: {required - set(ui)}"
    # The category page substitutes the category name into the text.
    assert "{category}" in ui["category_description"]
    assert "{author}" in ui["author_articles"]
    assert "{site}" in ui["blog_description"]
    blog = (GOLDEN / "src" / "pages" / "blog" / "index.astro").read_text()
    assert "ui.blog_description" in blog and 'title={ui.blog' in blog
    assert all(isinstance(v, str) and v for v in ui.values())
    # The visible component labels must be driven by config.ui, so a
    # Turkish site never leaks English chrome.
    pages = GOLDEN / "src" / "pages"
    assert "ui.latest_articles" in (pages / "index.astro").read_text()
    article = (pages / "[...slug].astro").read_text()
    for key in ("ui.key_takeaways", "ui.faq_title", "ui.read_next", "ui.by"):
        assert key in article, f"article template misses {key}"
    assert "ui.search" in (pages / "search.astro").read_text()
    footer = (GOLDEN / "src" / "components" / "Footer.astro").read_text()
    assert "ui.footer_explore" in footer and "ui.rights" in footer
    layout = (GOLDEN / "src" / "layouts" / "BaseLayout.astro").read_text()
    assert "ui.skip_to_content" in layout


def test_homepage_portal_composition() -> None:
    index = (GOLDEN / "src" / "pages" / "index.astro").read_text()
    for hook in ("feature-card", "category-strip", "PostCard", "Sidebar"):
        assert hook in index, f"homepage misses {hook}"
    # Strip titles must link to the category archives.
    assert '<a href={strip.url}>' in index
    assert "slugify" in index
    schema = (GOLDEN / "src" / "content.config.ts").read_text()
    assert "category" in schema, "content schema misses the category field"


def test_category_archive_pages() -> None:
    config = json.loads((GOLDEN / "site.config.json").read_text())
    # The URL segment is config-driven so non-English sites get a
    # native path (e.g. /kategori/...).
    base = config["seo"]["category_base"]
    assert isinstance(base, str) and base and "/" not in base

    route = (GOLDEN / "src" / "pages" / "[category_base]" / "[slug].astro")
    text = route.read_text()
    for hook in (
        "getStaticPaths", "BreadcrumbList", "PostCard", "category_base",
        "slugify", "ui.category_description", "canonical",
    ):
        assert hook in text, f"category route misses {hook}"

    # The slug helper must fold Turkish dotless i explicitly - NFD
    # normalization alone cannot, so its absence breaks Turkish sites.
    helper = (GOLDEN / "src" / "lib" / "slugify.ts").read_text()
    assert "\\u0131" in helper and "\\u0130" in helper
    assert 'normalize("NFD")' in helper

    # Article breadcrumbs climb to the category archive when set.
    article = (GOLDEN / "src" / "pages" / "[...slug].astro").read_text()
    assert "parentCrumb" in article
    assert "post.data.category" in article


def test_author_profile_pages() -> None:
    config = json.loads((GOLDEN / "site.config.json").read_text())
    # Config authors must resolve to the shipped route, so bylines and
    # article JSON-LD never point at a 404.
    for author in config["authors"]:
        assert author["url"].startswith("/authors/")
        assert author["bio"], "example author needs a bio placeholder"

    route = (GOLDEN / "src" / "pages" / "authors" / "[slug].astro")
    text = route.read_text()
    for hook in (
        "getStaticPaths", '"Person"', "BreadcrumbList", "PostCard",
        "ui.author_articles", "canonical", "sameAs", "jobTitle",
        "authorUrl",
    ):
        assert hook in text, f"author route misses {hook}"
    # Only authors published under /authors/ get a page; a config
    # author pointing elsewhere (e.g. an external profile) must not
    # break the build.
    assert 'startsWith("/authors/")' in text

    # Articles end with a visible author box that mirrors the Article
    # JSON-LD's author node and links to the profile page.
    article = (GOLDEN / "src" / "pages" / "[...slug].astro").read_text()
    for hook in ("AuthorBox", "authorEntity", "ui.about_the_author"):
        assert hook in article, f"article template misses {hook}"


def test_homepage_archetypes() -> None:
    index = (GOLDEN / "src" / "pages" / "index.astro").read_text()
    # The homepage must compose itself from site_type: product blocks
    # (quick facts, how-to) and directory blocks (entity cards,
    # comparison table) alongside the portal default.
    for hook in (
        "site_type", "QuickFacts", "HowToSteps", "EntityCard",
        "comparison", 'getCollection("entities")', "product.facts",
        "product.steps",
    ):
        assert hook in index, f"homepage misses {hook}"

    config = json.loads((GOLDEN / "site.config.json").read_text())
    assert config["site_type"] == "portal"
    product = config["product"]
    assert product["facts"] == [] and product["steps"] == []
    for key in ("name", "cta_label", "demo_path"):
        assert key in product

    schema = (GOLDEN / "src" / "content.config.ts").read_text()
    assert "entities" in schema and "attributes" in schema
    assert (GOLDEN / "src" / "content" / "entities").is_dir()

    # Directory facet archives: config declares the facets, the
    # 3-segment route pre-renders one page per attribute value, and
    # the homepage links them as chips.
    directory = config["directory"]
    assert directory["base"] and directory["facets"] == []
    assert "facet-nav" in index and "facetLinks" in index
    facet_route = (
        GOLDEN / "src" / "pages" / "[directory_base]" / "[facet]"
        / "[value].astro"
    ).read_text()
    for hook in (
        "getStaticPaths", "EntityCard", "BreadcrumbList", "slugify",
        "ui.facet_description", "canonical",
    ):
        assert hook in facet_route, f"facet route misses {hook}"
    assert "{label}" in config["ui"]["facet_description"]
    assert "{value}" in config["ui"]["facet_description"]


def test_dynamic_sitemap_and_llms_endpoints() -> None:
    # A hand-written public/sitemap.xml lists the launch pack forever;
    # the endpoints regenerate from the article list on every build.
    sitemap = (GOLDEN / "src" / "pages" / "sitemap.xml.js").read_text()
    for hook in (
        'getCollection("blog")', "lastmod", "category_base",
        "/authors/", 'getCollection("entities")', "urlset",
    ):
        assert hook in sitemap, f"sitemap endpoint misses {hook}"
    assert not (GOLDEN / "public" / "sitemap.xml").exists(), (
        "golden must not ship a static sitemap next to the endpoint"
    )
    llms = (GOLDEN / "src" / "pages" / "llms.txt.js").read_text()
    assert 'getCollection("blog")' in llms and "config.niche" in llms
    assert "/api/articles.json" in llms
    assert not (GOLDEN / "public" / "llms.txt").exists()
    # robots.txt keeps pointing at the endpoint's path.
    robots = (GOLDEN / "public" / "robots.txt").read_text()
    assert "/sitemap.xml" in robots


def test_agent_discovery_surface() -> None:
    # The read API renders the full article catalog from the content
    # collection - agents get the site in one request.
    api = (GOLDEN / "src" / "pages" / "api" / "articles.json.js").read_text()
    for hook in (
        'getCollection("blog")', "description", "published", "updated",
        "category", "application/json",
    ):
        assert hook in api, f"articles.json endpoint misses {hook}"

    # RFC 9727 catalog: valid linkset JSON once the placeholder is
    # substituted, anchoring the read API and llms.txt.
    catalog_text = (
        GOLDEN / "public" / ".well-known" / "api-catalog"
    ).read_text()
    assert "{{SITE_URL}}" in catalog_text
    catalog = json.loads(
        catalog_text.replace("{{SITE_URL}}", "https://example.com")
    )
    entry = catalog["linkset"][0]
    assert entry["anchor"].endswith("/api/articles.json")
    assert entry["service-doc"][0]["href"].endswith("/llms.txt")

    # Link headers advertise the machine endpoints on the homepage,
    # and the extensionless catalog gets its media type pinned.
    headers = (GOLDEN / "public" / "_headers").read_text()
    assert 'rel="api-catalog"' in headers
    assert 'rel="describedby"' in headers
    assert "application/linkset+json" in headers

    # The archetype decision is wired into the design workflow.
    design = (ROOT / "skills" / "design-theme" / "SKILL.md").read_text()
    assert "site_type" in design and "ARCHETYPE" in design
    assert "`forum`" in design
    review = (ROOT / "skills" / "visual-review" / "SKILL.md").read_text()
    assert "Archetype match" in review


def test_directory_pro_and_forum_archetype() -> None:
    index = (GOLDEN / "src" / "pages" / "index.astro").read_text()
    # Booking-style directory: zero-JS search hero, facet grouping
    # past a dozen entities, price on cards.
    for hook in ("hero-search", "entity-group", "GROUP_LIMIT", "view_all",
                 "price={entity.data.price}"):
        assert hook in index, f"homepage misses {hook}"
    # Forum board: thread rows with answer counts.
    for hook in ("thread-list", "isForum", "answers_count", "thread-tag"):
        assert hook in index, f"homepage misses {hook}"

    schema = (GOLDEN / "src" / "content.config.ts").read_text()
    for field in ("images", "price", "cta_url", "replies", "highlight"):
        assert field in schema, f"content schema misses {field}"

    article = (GOLDEN / "src" / "pages" / "[...slug].astro").read_text()
    for hook in ("EntityPanel", "ThreadReplies", "QAPage", "acceptedAnswer",
                 "entityEntry"):
        assert hook in article, f"article template misses {hook}"
    # The offer CTA is an affiliate link and must say so.
    panel = (GOLDEN / "src" / "components" / "EntityPanel.astro").read_text()
    assert 'rel="sponsored nofollow noopener"' in panel


def test_composition_recipes() -> None:
    recipes = (ROOT / "skills" / "design-theme" / "recipes.md").read_text()
    # One recipe per group is mandatory; the catalog must actually
    # contain the advertised recipes and stay on shipped hooks.
    for recipe_id in (
        "H1", "H2", "H3", "H4", "N1", "N2", "N3",
        "L1", "L2", "L3", "F1", "F2", "F3",
    ):
        assert f"### {recipe_id} -" in recipes, f"recipes.md misses {recipe_id}"
    for hook in (".site-hero", "header.container", ".post-list", ".site-footer"):
        assert hook in recipes
    skill = (ROOT / "skills" / "design-theme" / "SKILL.md").read_text()
    assert "recipes.md" in skill and "H2+N1+L2+F3" in skill


def test_claude_md_encodes_the_workflow() -> None:
    # CLAUDE.md is what keeps builder sessions on the toolkit path -
    # it must name the load-bearing skills and the gate rule.
    text = (GOLDEN / "CLAUDE.md").read_text()
    for hook in (
        "write-article", "generate-article-images", "design-theme",
        "seo_report.py", "article-images", "site.config.json",
        "visual-check.mjs", "check_toolkit_version.py",
    ):
        assert hook in text, f"CLAUDE.md misses {hook}"


def test_package_json_is_zero_js_static_build() -> None:
    package = json.loads((GOLDEN / "package.json").read_text())
    assert package["scripts"]["build"] == "astro build"
    assert "astro" in package["dependencies"]


_BINARY_SUFFIXES = {".png", ".ico", ".jpg", ".jpeg", ".webp", ".svg", ".woff2"}


def test_golden_files_are_ascii() -> None:
    checked = 0
    for path in GOLDEN.rglob("*"):
        if path.is_file() and path.suffix not in _BINARY_SUFFIXES:
            content = path.read_bytes()
            assert content.isascii(), f"{path} contains non-ASCII bytes"
            checked += 1
    assert checked > 20, "ASCII sweep unexpectedly skipped most files"
