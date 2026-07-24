---
name: generate-trust-pages
description: Generate a site's trust and legal pages from templates: About, Contact, Privacy Policy, Terms of Service, and Disclaimer, plus the footer that links them sitewide. Use when the user wants an about page, privacy policy, terms, disclaimer, contact page, footer links, legal pages, or when a new site is missing its trust pages.
---

# Generate trust pages

Ship the five pages users and search quality raters look for before
trusting a site, filled with the site's real details, plus the footer
that links them from every page.

## Inputs

- site.config.json (site name, domain, niche) and the `legal` section
  (contact email, what the site actually uses: analytics provider, ad
  network, newsletter). Ask for anything missing - especially the
  contact email, which must be real and monitored.
- The site's niche, to choose the right disclaimer block (health,
  finance, legal, or general). YMYL niches must not skip the
  disclaimer.

## Instructions

1. Copy the five templates from the toolkit's `templates/pages/`
   directory into the site's content/pages location: `about.md`,
   `contact.md`, `privacy-policy.md`, `terms-of-service.md`,
   `disclaimer.md`.
2. Fill every `{{PLACEHOLDER}}` from site.config.json and the gathered
   answers. Expand the prose sections (mission, niche description,
   author section) with real site-specific content - these pages carry
   E-E-A-T weight and must not read as unfilled boilerplate.
3. Prune honestly: delete the analytics/ads/newsletter/cookies sections
   that do not apply to this site. A policy describing tools the site
   does not run is a trust liability, not a shortcut.
4. Pick exactly one niche disclaimer block (health, finance, legal, or
   the general one) and delete the rest. Set `Last updated` to the real
   date.
5. Install the footer from `templates/theme/` (`Footer.astro` or
   `Footer.tsx`) into the base layout so every page links the five
   pages.
6. Finish the wiring: add the pages to the sitemap, mark them as
   `Optional` entries in llms.txt, and give each a proper title and
   meta description via the theme's SEO head component. Trust pages are
   indexable - do not noindex them.
7. Remind the user: the privacy policy and terms are starting
   templates, not legal advice - they should be reviewed for the
   jurisdictions the site serves (GDPR, CCPA, and similar).

## Output

- The five filled pages in place, the footer wired into the layout, and
  sitemap/llms.txt/meta updates.
- A note listing which sections were pruned and the legal-review
  reminder.

## Quality checklist

- No `{{PLACEHOLDER}}` or template comment remains in any published
  page.
- Policy sections match what the site actually runs; nothing claimed
  that is not in use.
- The contact email is real; the disclaimer matches the niche.
- Footer links resolve on every page; the five pages are in the
  sitemap.
