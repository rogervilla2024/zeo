// RSS feed at /rss.xml, advertised by BaseLayout's alternate link.
import rss from "@astrojs/rss";
import { getCollection } from "astro:content";
import config from "../../site.config.json";

export async function GET(context) {
  const posts = (await getCollection("blog")).sort(
    (a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf(),
  );
  return rss({
    title: config.site_name,
    description: config.niche,
    site: context.site ?? config.domain,
    items: posts.map((post) => ({
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.pubDate,
      link: `/${post.id}/`,
    })),
  });
}
