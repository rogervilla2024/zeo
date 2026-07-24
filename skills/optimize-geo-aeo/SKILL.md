---
name: optimize-geo-aeo
description: Restructures content to be cited by AI answer engines and to win featured snippets and AI Overviews through extractable answers, Q&A blocks, entity clarity, citations, and an llms.txt file. Use when the user wants generative engine optimization (GEO), answer engine optimization (AEO), to get content cited by ChatGPT, Perplexity, or Google AI Overviews, to win featured snippets, or to make a page more quotable by LLMs.
---

Reworks a page so that AI answer engines and generative search can easily extract, trust, and cite it, while also targeting classic featured snippets.

## Inputs

- The page content or URL and its target query set (including natural-language questions).
- Domain, niche, and audience.
- The primary entity/topic the page should be recognized for.
- Available authoritative sources for citation.
- Whether the site can publish an llms.txt file and add schema.

You may delegate to the `geo-aeo-optimizer` subagent for the restructure, `schema-engineer` for structured data, and `fact-checker` for source verification via the Task/Agent mechanism.

## Instructions

1. Map the questions. List the exact natural-language questions the page should answer, including who/what/why/how and comparison and "best for" phrasings.
2. Lead with extractable answers. For each key question, place a direct 40-60 word answer immediately under a question-style heading, before elaboration. Answer first, explain second.
3. Build Q&A blocks. Structure sections as clear question headings (H2/H3) followed by self-contained answers that make sense when quoted out of context.
4. Make answers self-contained. Avoid "as mentioned above" and pronoun-only references; restate the subject so any extracted passage stands alone.
5. Establish entity clarity. Define the primary entity explicitly, use consistent naming, and connect it to related entities so engines understand what the page is about. Add an author/expertise signal where relevant.
6. Add extractable formats. Use concise definition sentences, ordered steps for processes, comparison tables for "X vs Y", and short bulleted lists for enumerable answers.
7. Cite sources. Support claims with links to authoritative primary sources; verified, well-sourced content is more likely to be cited. Coordinate with the fact-check skill.
8. Add structured data. Implement FAQPage, HowTo, QAPage, or Article schema matching the visible Q&A and steps.
9. Publish llms.txt. Draft or update a root-level llms.txt that lists the site's key pages, a short site description, and priority content for AI crawlers, in the plain llms.txt markdown format.
10. Reinforce E-E-A-T. Surface author credentials, publish/update dates, and first-hand experience signals that increase trust and citation likelihood.

## Output

- The restructured content with question headings and lead-in extractable answers.
- A Q&A block set ready to paste.
- JSON-LD schema (FAQPage/HowTo/QAPage/Article) matching the content.
- A drafted or updated llms.txt file.
- A citation list mapping claims to authoritative sources.

## Quality checklist

- [ ] Each key question has a direct 40-60 word answer placed first.
- [ ] Answers are self-contained and quotable out of context.
- [ ] Primary entity is defined and consistently named.
- [ ] Comparison, definition, and step formats used where they fit the query.
- [ ] Claims are cited to authoritative primary sources.
- [ ] Valid schema matches the visible Q&A and steps.
- [ ] llms.txt is present, well-formed, and lists priority pages.
- [ ] E-E-A-T signals (author, dates, experience) are present.
- [ ] Content stays site-agnostic to brand beyond the provided inputs.
