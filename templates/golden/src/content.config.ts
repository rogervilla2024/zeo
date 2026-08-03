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
    // Pillar/cluster name from the topic map; feeds the homepage
    // category strips. Empty means the article joins no strip.
    category: z.string().default(""),
    takeaways: z.array(z.string()).default([]),
    faq: z
      .array(z.object({ question: z.string(), answer: z.string() }))
      .default([]),
    // Forum-archetype threads: editorial answers rendered as a
    // discussion under the article, mirrored in QAPage JSON-LD.
    // Attribute answers to real authors or cited sources - never
    // fabricate community members.
    replies: z
      .array(
        z.object({
          author: z.string(),
          text: z.string(),
          highlight: z.boolean().default(false),
        }),
      )
      .default([]),
  }),
});

// Directory-archetype catalog (site_type: "directory"): one entry
// per entity (hotel, tool, venue) with typed attributes. Cards and
// the comparison table on the homepage render from this data; the
// deep dive stays an article, linked via `article`. Portal and
// product sites simply leave the folder empty.
const entities = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/entities" }),
  schema: z.object({
    title: z.string(),
    description: z.string().default(""),
    image: z.string().optional(),
    // Additional photos for the gallery on the entity's article page.
    images: z.array(z.string()).default([]),
    // Root-relative path to the entity's review article.
    article: z.string().default(""),
    badge: z.string().default(""),
    // Display price ("from 120 EUR" / "$$$") and the outbound offer
    // link (affiliate URL; rendered rel="sponsored nofollow").
    price: z.string().default(""),
    cta_url: z.string().default(""),
    // EDITORIAL score (e.g. "8.7") - shown as the editor's rating,
    // never dressed up as user votes the site does not have.
    rating: z.string().default(""),
    order: z.number().default(999),
    attributes: z
      .array(z.object({ label: z.string(), value: z.string() }))
      .default([]),
  }),
});

export const collections = { blog, entities };
