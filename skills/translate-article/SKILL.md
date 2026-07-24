---
name: translate-article
description: Localize a published article into another language as a full SEO citizen: localized keywords and examples, translated meta and slug, per-language schema, hreflang alternates, and sitemap entries. Use when the user wants an article translated, a multilingual site, localized content, hreflang setup for a piece, or to publish existing content in additional languages.
---

# Translate and localize an article

A translated article is a new article in a new market, not a word swap.
This skill produces a localized version that can rank in its own
language and wires the cross-language plumbing that makes both versions
index correctly.

## Inputs

- The source article (markdown plus its metadata block) and its URL.
- Target language(s), from site.config.json `languages` or the request.
- The site's URL pattern for languages (subdirectory `/de/` is the
  toolkit default).

## Instructions

1. Localize keywords first. Do not translate the primary keyword
   literally: delegate to `keyword-researcher` for how the target
   audience actually searches this topic in the target language, and
   pick the primary/secondary keywords from that. If intent differs
   materially, adjust the angle.
2. Translate for meaning, then localize: examples, idioms, units,
   currencies, regulations, and cultural references adapt to the target
   market. The FAQ section is re-derived from target-language People
   Also Ask questions where they differ.
3. Rewrite the metadata for the target language: title tag, meta
   description, and a translated slug (never reuse the source slug).
4. Run the same quality gates as an original article: the
   humanize-content pass plus `check_ai_patterns.py`, and internal
   linking with `suggest_internal_links.py` against the target
   language's inventory (link to same-language pages only).
5. Wire the cross-language plumbing:
   - hreflang alternates on both versions (each lists all versions plus
     x-default), via the theme's SeoHead/metadata component
   - JSON-LD regenerated with `inLanguage` and the translated headline,
     description, and author wiring
   - sitemap entries with the full alternate set for every version
     (`generate_sitemap.py` alternates field)
6. Verify: `check_rich_results.py --file` on the built translated page;
   confirm reciprocal hreflang between versions.

## Output

- The localized article with its metadata block, per-language JSON-LD,
  the hreflang set for all versions, and the sitemap entry updates.

## Quality checklist

- Primary keyword comes from target-language research, not literal
  translation.
- Examples, units, and references are localized; nothing reads as
  machine-translated (gates passed).
- Slug, title, and meta description are written in the target language.
- hreflang is reciprocal across every version and includes x-default.
- Internal links point only to same-language pages.
