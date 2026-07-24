---
description: Generate validated JSON-LD structured data for a given page and schema type
argument-hint: [page URL or content] [schema type]
---

You are generating structured data (JSON-LD) for a page.

Parse $ARGUMENTS for the target page (URL or pasted content) and the desired schema
type (e.g. Article, BlogPosting, Product, FAQPage, HowTo, Organization, LocalBusiness,
BreadcrumbList). If the page or content is missing, ask for the URL or the content to
mark up. If the schema type is unclear, infer the best fit from the content and state
your assumption, or ask when genuinely ambiguous. Do NOT assume any brand, domain, or
niche; use only details present in the provided input or ask for them.

Orchestrate the following:

1. Invoke the generate-schema skill (or delegate to the schema-engineer subagent) to
   build the JSON-LD for the identified type(s). Populate only fields supported by the
   provided content; never fabricate values such as ratings, prices, or authors.
2. Validate the output against schema.org requirements and Google's rich-result
   eligibility. Distinguish required vs. recommended properties.
3. Add complementary schema where clearly warranted (e.g. BreadcrumbList, FAQPage).

Deliver:
- The final JSON-LD in a fenced code block, ready to paste into the page head.
- A short field map noting which properties were populated and their source.
- A list of any missing required or recommended fields and the input needed to fill
  them.
- Validation notes: rich-result types the markup is eligible for and any warnings.
