// Machine-readable article index at /api/articles.json - the static
// site's read API. Agents that should not scrape HTML get the whole
// catalog in one request; /.well-known/api-catalog (RFC 9727)
// advertises this endpoint and the homepage's Link headers point at
// the catalog. Regenerated from the content collection on every
// build, so it can never go stale.
import { getCollection } from "astro:content";
import config from "../../../site.config.json";

export async function GET() {
  const posts = (await getCollection("blog")).sort(
    (a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf(),
  );
  const articles = posts.map((post) => ({
    title: post.data.title,
    url: new URL(`/${post.id}/`, config.domain).href,
    description: post.data.description,
    published: post.data.pubDate.toISOString().slice(0, 10),
    updated: (post.data.updatedDate ?? post.data.pubDate)
      .toISOString()
      .slice(0, 10),
    category: post.data.category || null,
    author: post.data.author,
  }));
  const payload = {
    site: config.site_name,
    domain: config.domain,
    language: config.default_language,
    count: articles.length,
    articles,
  };
  return new Response(JSON.stringify(payload, null, 2) + "\n", {
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
}
