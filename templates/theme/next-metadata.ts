// SEO metadata helpers for Next.js (App Router) sites scaffolded by
// seo-content-forge. Copy into lib/seo.ts and place site.config.json at
// the project root.
//
// Per page:
//
//   import { buildMetadata } from "@/lib/seo";
//   export const metadata = buildMetadata({
//     title: "Page title",
//     description: "Page description",
//     path: "/guides/example",
//   });
//
// JSON-LD in the page body:
//
//   <JsonLd nodes={[articleNode, breadcrumbNode]} />

import type { Metadata } from "next";
import config from "../site.config.json";

interface PageSeo {
  title: string;
  description: string;
  path: string;
  ogImage?: string;
  ogType?: "website" | "article";
  hreflang?: Record<string, string>;
  noindex?: boolean;
}

export function buildMetadata(page: PageSeo): Metadata {
  const fullTitle = `${page.title}${config.seo.title_suffix}`;
  const canonical = new URL(page.path, config.domain).href;
  const ogImage = page.ogImage ?? config.seo.og_image;
  const absoluteOgImage = ogImage.startsWith("http")
    ? ogImage
    : new URL(ogImage, config.domain).href;

  return {
    title: fullTitle,
    description: page.description,
    alternates: {
      canonical,
      languages: page.hreflang,
    },
    robots: page.noindex ? { index: false, follow: false } : undefined,
    openGraph: {
      type: page.ogType ?? "website",
      title: fullTitle,
      description: page.description,
      url: canonical,
      siteName: config.site_name,
      images: [{ url: absoluteOgImage, width: 1200, height: 630 }],
    },
    twitter: {
      card: "summary_large_image",
      title: fullTitle,
      description: page.description,
      images: [absoluteOgImage],
    },
  };
}

export function JsonLd({ nodes }: { nodes: object[] }) {
  return (
    <>
      {nodes.map((node, index) => (
        <script
          key={index}
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(node) }}
        />
      ))}
    </>
  );
}
