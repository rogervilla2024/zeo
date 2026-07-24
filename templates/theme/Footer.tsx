// Site footer for Next.js sites scaffolded by seo-content-forge.
// Links every page to the trust pages (About, Contact, Privacy, Terms,
// Disclaimer) - a sitewide trust signal for users and quality raters.
// Copy into components/Footer.tsx and include in the root layout.

import Link from "next/link";
import config from "../site.config.json";

const LINKS = [
  { name: "About", href: "/about" },
  { name: "Contact", href: "/contact" },
  { name: "Privacy Policy", href: "/privacy-policy" },
  { name: "Terms of Service", href: "/terms-of-service" },
  { name: "Disclaimer", href: "/disclaimer" },
];

export function Footer() {
  const year = new Date().getFullYear();
  return (
    <footer
      style={{
        marginTop: "4rem",
        padding: "2rem 1rem",
        borderTop: "1px solid rgba(128,128,128,0.25)",
        fontSize: "0.875rem",
        textAlign: "center",
      }}
    >
      <nav aria-label="Footer">
        <ul
          style={{
            display: "flex",
            flexWrap: "wrap",
            justifyContent: "center",
            gap: "0.5rem 1.5rem",
            listStyle: "none",
            margin: "0 0 1rem",
            padding: 0,
          }}
        >
          {LINKS.map((link) => (
            <li key={link.href}>
              <Link href={link.href}>{link.name}</Link>
            </li>
          ))}
        </ul>
      </nav>
      <p style={{ margin: 0, opacity: 0.7 }}>
        &copy; {year} {config.site_name}. All rights reserved.
      </p>
    </footer>
  );
}
