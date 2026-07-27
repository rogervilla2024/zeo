---
name: build-author-entity
description: Create E-E-A-T author entities for a site: author profile pages with Person schema, sameAs links to real profiles, author boxes on articles, and Article schema wired to the author's profile URL. Use when the user wants author pages, author bios, E-E-A-T improvements, byline credibility, or when articles publish without a linked author entity.
---

# Build author entities (E-E-A-T)

Give every byline a verifiable identity: a profile page search engines
and AI systems can resolve, connected from each article. Author identity
is a load-bearing trust signal for content quality assessment.

## Inputs

- The author(s): name, role, credentials, short bio, photo, and real
  external profiles (LinkedIn, X, ORCID, personal site) for sameAs.
- The site's codebase and site.config.json (authors are registered
  there so write-article can reference them).

Never invent credentials, degrees, or experience. If an author has no
external profiles, use what exists; a thin real profile beats a
fabricated impressive one, which is a policy risk.

## Instructions

1. Register authors in site.config.json under an `authors` array:
   name, role, profile path (e.g. `/authors/jane-doe`), bio, optional
   image, and sameAs URLs.
2. Create the author profile page per author: bio focused on
   experience and credentials relevant to the site's niche, photo,
   role, and a list of their articles. Sites built from
   templates/golden already ship this page
   (`src/pages/authors/[slug].astro`): it renders every config author
   whose `url` starts with `/authors/` - profile, Person +
   BreadcrumbList JSON-LD, and the author's article list - so on
   those sites this step is just filling the config fields.
3. Generate the Person schema for each profile page and validate it:

   ```bash
   python scripts/build_jsonld.py --type person --input author.json --output person.jsonld
   python scripts/validate_schema.py --input person.jsonld
   ```

   Embed it on the profile page.
4. Wire articles to the entity: article JSON-LD uses the `author_url`
   parameter of the article builder so the byline Person carries a
   `url` pointing at the profile page. Update the article template so
   this happens automatically for future articles.
5. Add a visible author box to the article template: photo, name, role,
   one-line bio, link to the profile. Schema must mirror visible
   content. Golden-template sites ship this too (AuthorBox.astro,
   rendered at the end of every article from the matching config
   author), so there it works as soon as the config entry is filled.
6. Verify with the offline checker on a built article page and the
   profile page:

   ```bash
   python scripts/check_rich_results.py --file dist/articles/example/index.html
   ```

## Output

- Author entries in site.config.json, profile page(s) with validated
  Person schema, the author-box template change, and the article
  template change wiring `author_url`.

## Quality checklist

- Every sameAs URL resolves to a real profile of this actual person.
- Bio states experience relevant to the niche, without invented
  credentials.
- Article schema author now carries the profile URL; new articles get
  it automatically from the template.
- Person schema validates with no errors and mirrors visible content.
