---
name: generate-llms-txt
description: Generate an llms.txt file (llmstxt.org standard) that tells AI agents and answer engines what a site is about and which pages matter. Use when the user wants an llms.txt, wants the site readable by LLMs or AI agents, mentions GEO/AEO discoverability, or an agent-readiness test flagged a missing llms.txt.
---

# Generate llms.txt

Produce a valid ``llms.txt`` for the site root, backed by a helper script
so the format always matches the llmstxt.org proposal.

## Inputs

- Site name and a one-or-two sentence summary of what the site offers.
- The site's most important pages grouped into sections (docs, guides,
  key content hubs), each with title, absolute URL, and an optional
  one-line note. Prefer linking markdown (``.md``) mirrors where they
  exist; otherwise link the canonical HTML pages.
- Secondary pages that agents may skip go into an ``Optional`` section.

If you have the site's codebase or sitemap, derive the page list from it
instead of asking the user to enumerate URLs by hand: take the highest-
value pages (home, pillar pages, docs roots), not every URL.

## Instructions

1. Build the site config JSON:

   ```json
   {
     "site_name": "Example",
     "summary": "What the site is, in one or two sentences.",
     "details": "Optional extra context paragraphs.",
     "sections": {
       "Guides": [
         {"title": "Getting started", "url": "https://example.com/start",
          "note": "Setup in five minutes"}
       ],
       "Optional": [
         {"title": "Changelog", "url": "https://example.com/changelog"}
       ]
     }
   }
   ```

2. Generate the file with the helper script from the toolkit's
   `scripts/` directory:

   ```bash
   python generate_llmstxt.py --input site.json --output llms.txt
   ```

3. Place ``llms.txt`` at the site root so it is served at
   ``https://example.com/llms.txt`` (static assets directory in most
   frameworks: ``public/``, ``static/``, or the web root).
4. Keep it maintained: when major sections are added to the site, update
   the file. Do not list every URL; llms.txt is a curated map, not a
   sitemap replacement.

## Output

- The generated ``llms.txt`` content and where it was placed (or should
  be placed) in the codebase.

## Quality checklist

- Starts with a single H1 (site name) then a blockquote summary.
- Every listed URL is absolute and returns 200.
- Sections are curated: the highest-value pages, not an exhaustive dump.
- The file is plain markdown with no HTML.
