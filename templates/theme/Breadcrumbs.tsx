// Visible breadcrumb trail for Next.js sites scaffolded by
// seo-content-forge. Pair it with the BreadcrumbList JSON-LD (rendered
// via the JsonLd helper in next-metadata.ts) - Google shows the
// breadcrumb rich result when the visible trail and the schema agree.
// Copy into components/Breadcrumbs.tsx.
//
//   <Breadcrumbs
//     items={[
//       { name: "Home", url: "/" },
//       { name: "Guides", url: "/guides/" },
//       { name: article.title }, // current page: no url
//     ]}
//   />

import Link from "next/link";

interface Crumb {
  name: string;
  url?: string;
}

export function Breadcrumbs({ items }: { items: Crumb[] }) {
  return (
    <nav aria-label="Breadcrumb">
      <ol
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "0.25rem",
          listStyle: "none",
          margin: 0,
          padding: 0,
          fontSize: "0.875rem",
        }}
      >
        {items.map((item, index) => {
          const isCurrent = index === items.length - 1 || !item.url;
          return (
            <li key={`${item.name}-${index}`}>
              {index > 0 && (
                <span aria-hidden="true" style={{ opacity: 0.5 }}>
                  {" / "}
                </span>
              )}
              {isCurrent ? (
                <span aria-current="page" style={{ opacity: 0.75 }}>
                  {item.name}
                </span>
              ) : (
                <Link href={item.url as string}>{item.name}</Link>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
