---
name: mine-questions
description: Mine real user questions (People Also Ask style) for a niche or keyword from live search autocomplete, in the site's language, and feed them into launch topics, article outlines, and FAQ blocks. Use at site bootstrap, before writing any article, when planning clusters, or when the user mentions PAA, user questions, or "what do people search".
---

# Mine real user questions

Answer what people actually ask. Autocomplete data is live search
demand; every article and FAQ block should be built on it.

## Instructions

1. Run the miner with the site's content language:

   ```bash
   python scripts/mine_questions.py --seed "topic keyword" \
       --lang en --json questions.json
   ```

   Run once per pillar topic at bootstrap and once per target keyword
   before writing an article.
2. Use the output in three places:
   - build-topic-clusters: recurring question themes become launch-pack
     article topics
   - write-article outline: each major question the article targets
     becomes an H2/H3 with a direct answer in the first sentence
   - the FAQ block: pick 3-5 mined questions NOT already covered by the
     headings; mirror them exactly in FAQPage schema (the rich-results
     consistency gate verifies visible text matches the schema)
3. Questions come back in the query language; never translate them for
   the FAQ - rank for the phrasing people actually type.
4. If the endpoint is unreachable, fall back to WebSearch for the PAA
   box of the target keyword and note the source.

## Quality checklist

- FAQ questions trace to mined data, not invention.
- No duplicate intent between headings and FAQ entries.
