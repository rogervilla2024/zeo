// Dynamic llms.txt at /llms.txt - the AI-readability index. Built
// from the config and the live article list on every build, so it
// never goes stale as content grows. The generate-llms-txt skill can
// still replace this with a hand-curated file for finer control; the
// default just always stays complete.
import { getCollection } from "astro:content";
import config from "../../site.config.json";

export async function GET() {
  const posts = (await getCollection("blog")).sort(
    (a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf(),
  );
  const absolute = (path) => new URL(path, config.domain).href;

  const lines = [
    `# ${config.site_name}`,
    "",
    `> ${config.niche}`,
    "",
    "## Key pages",
    "",
    `- [Articles](${absolute("/blog/")})`,
    `- [Article index, JSON](${absolute("/api/articles.json")})`,
    `- [About](${absolute("/about/")})`,
    `- [Contact](${absolute("/contact/")})`,
    "",
    "## Articles",
    "",
  ];
  for (const post of posts) {
    lines.push(
      `- [${post.data.title}](${absolute(`/${post.id}/`)}): ` +
        post.data.description,
    );
  }
  return new Response(lines.join("\n") + "\n", {
    headers: { "Content-Type": "text/plain; charset=utf-8" },
  });
}
