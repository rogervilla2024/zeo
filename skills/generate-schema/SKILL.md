---
name: generate-schema
description: Generate and validate schema.org JSON-LD structured data for rich results (Article, BlogPosting, FAQPage, HowTo, BreadcrumbList, Organization, WebSite SearchAction, Product, Recipe, VideoObject, Event, Person, LocalBusiness, JobPosting, Course, SoftwareApplication, Speakable). Use when the user wants structured data, rich snippets, rich results, JSON-LD, schema markup, speakable/voice markup, or to make a page eligible for enhanced Google listings.
---

# Generate schema.org JSON-LD for rich results

Produce valid, publish-ready JSON-LD and confirm it before shipping. This
skill is backed by helper scripts so output is deterministic and
schema-correct rather than hand-written.

## Inputs

Gather from the user or the page being marked up:

- Page type and the rich result targeted: `article`, `faq`, `howto`,
  `breadcrumb`, `organization`, `website`, `product`, `recipe`, `video`,
  `event`, `person`, `localbusiness` (subtype via `business_type`),
  `jobposting`, `course`, `softwareapp`, or `speakable` (voice/AEO
  sections; 2-3 quotable selectors, never the whole article).
- The concrete field values for that type (headline, URL, author,
  publisher name and logo URL, publish/modified dates, images, Q/A pairs,
  steps, breadcrumb trail, price and currency, etc.).
- Site context: canonical domain and brand name.

If required values are missing, ask for them before generating. Never
invent prices, ratings, dates, or authorship: fabricated structured data
violates Google guidelines and risks manual action.

## Instructions

1. Decide the type(s). A single page often needs more than one node
   (for example `BlogPosting` plus `BreadcrumbList` plus `FAQPage`).
2. Assemble a parameters JSON file matching the builder signature. For
   `faq`, `howto`, and `breadcrumb`, pass arrays of two-element arrays
   (`questions`, `steps`, `items` respectively).
3. Build the JSON-LD by calling the helper script from the toolkit's
   `scripts/` directory:

   ```bash
   python scripts/build_jsonld.py --type article --input params.json --output out.json
   ```

4. Validate the result against rich-result requirements:

   ```bash
   python scripts/validate_schema.py --input out.json
   ```

   Resolve every reported error and review each warning. A non-zero exit
   means a required property is missing.
5. For deeper design decisions (which type fits, eligibility nuances,
   multiple linked nodes), delegate to the `schema-engineer` subagent.
6. Present the final JSON-LD wrapped in a
   `<script type="application/ld+json">` tag and tell the user to confirm
   it in Google's Rich Results Test before publishing.

## Output

- One or more validated JSON-LD blocks, each in a script tag.
- A short note on which rich result each block targets and any recommended
  (non-blocking) properties still missing.

## Quality checklist

- `@context` is `https://schema.org` and every node has a valid `@type`.
- All required properties for the type are present and truthful.
- Structured data reflects content visible on the page.
- `validate_schema.py` exits zero.
- Dates are ISO 8601; image and logo URLs are absolute.
