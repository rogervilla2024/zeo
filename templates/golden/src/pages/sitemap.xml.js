// Dynamic sitemap at /sitemap.xml (robots.txt points here). Built
// from the same sources as the pages themselves - static routes, every
// article (with lastmod), category archives, author profiles, and
// directory facet archives - so it can NEVER go stale: a hand-written
// public/sitemap.xml rots the moment article 11 ships; this one is
// regenerated on every build.
import { getCollection } from "astro:content";
import config from "../../site.config.json";
import { slugify } from "../lib/slugify";

const STATIC_PATHS = [
  "",
  "blog/",
  "about/",
  "contact/",
  "privacy-policy/",
  "terms-of-service/",
  "disclaimer/",
];

function escapeXml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function entry(path, lastmod) {
  const loc = escapeXml(new URL(path, config.domain).href);
  const dated = lastmod ? `<lastmod>${lastmod}</lastmod>` : "";
  return `<url><loc>${loc}</loc>${dated}</url>`;
}

export async function GET() {
  const posts = await getCollection("blog");
  const urls = STATIC_PATHS.map((path) => entry(path));

  for (const post of posts) {
    const lastmod = (post.data.updatedDate ?? post.data.pubDate)
      .toISOString()
      .slice(0, 10);
    urls.push(entry(`${post.id}/`, lastmod));
  }

  const categoryBase = config.seo.category_base ?? "category";
  const categories = new Set();
  for (const post of posts) {
    if (post.data.category) categories.add(slugify(post.data.category));
  }
  for (const slug of [...categories].sort()) {
    if (slug) urls.push(entry(`${categoryBase}/${slug}/`));
  }

  const authors = config.authors ?? [];
  for (const author of authors) {
    if (author.url && author.url.startsWith("/authors/")) {
      urls.push(entry(`${author.url.replace(/\/+$/, "")}/`));
    }
  }

  if ((config.site_type ?? "portal") === "directory") {
    const directory = config.directory ?? {};
    const base = directory.base || "directory";
    const facets = directory.facets ?? [];
    const entities = await getCollection("entities");
    const seen = new Set();
    for (const label of facets) {
      const facetSlug = slugify(label);
      for (const entity of entities) {
        const match = entity.data.attributes.find(
          (attr) => attr.label === label,
        );
        if (!match) continue;
        const valueSlug = slugify(match.value);
        const path = `${base}/${facetSlug}/${valueSlug}/`;
        if (facetSlug && valueSlug && !seen.has(path)) {
          seen.add(path);
          urls.push(entry(path));
        }
      }
    }
  }

  const xml =
    '<?xml version="1.0" encoding="UTF-8"?>\n' +
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    urls.join("\n") +
    "\n</urlset>\n";
  return new Response(xml, {
    headers: { "Content-Type": "application/xml; charset=utf-8" },
  });
}
