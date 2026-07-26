// Content collections for the golden template. Every field the article
// template needs to satisfy the toolkit's gates is declared here, so a
// post missing SEO-critical frontmatter fails the build, not the audit.
import { glob } from "astro/loaders";
import { defineCollection, z } from "astro:content";

const blog = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/blog" }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    author: z.string(),
    authorUrl: z.string(),
    image: z.string().optional(),
    takeaways: z.array(z.string()).default([]),
    faq: z
      .array(z.object({ question: z.string(), answer: z.string() }))
      .default([]),
  }),
});

export const collections = { blog };
