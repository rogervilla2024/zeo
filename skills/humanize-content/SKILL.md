---
name: humanize-content
description: Rewrites an AI-sounding draft into natural, human-sounding prose while preserving meaning, facts, and target keywords. It removes the tell-tale patterns of machine writing and matches a specific brand voice. Use when the user wants to humanize content, make text sound less like AI, remove robotic or generic phrasing, fix a draft that "sounds like ChatGPT", or match a brand's natural voice.
---

Takes a draft that reads as machine-generated and rewrites it to sound like a knowledgeable human writer, without changing the substance or hurting SEO.

## Inputs

- The draft text to humanize.
- Brand voice and tone (formal, conversational, expert, witty, plain).
- Target audience and reading level.
- Primary and secondary keywords that must be preserved.
- Any phrases, claims, or section structure that must not change.

You may delegate the rewrite to the `content-humanizer` subagent via the Task/Agent mechanism and then verify the output against the checklist below.

## Instructions

1. Read the full draft and note the meaning, facts, keywords, and structure that must survive the rewrite.
2. Remove these concrete AI-tell patterns:
   - Uniform paragraph and sentence lengths. Vary rhythm: mix short punchy sentences with longer ones.
   - Formulaic transitions ("Furthermore", "Moreover", "Additionally", "In today's fast-paced world"). Replace with natural connective tissue or none.
   - Hedging and filler ("It is important to note", "It is worth mentioning", "arguably", "generally speaking").
   - Wrap-up cliches ("In conclusion", "In summary", "At the end of the day"). Cut or replace with a real closing thought.
   - Empty introductions that restate the title before delivering value. Open with a specific hook, fact, or tension.
   - Overuse of em-dashes as a default connector. Prefer commas, periods, or parentheses; keep an em-dash only where it earns its place, and do not let it become a signature tic.
   - Listy, parallel "rule of three" phrasing on every point; break the pattern.
   - Over-explaining the obvious and repeating the keyword unnaturally.
   - Generic examples; swap in concrete, specific, plausible detail appropriate to the niche.
3. Inject human signals: a clear point of view, natural contractions where the voice allows, varied openers, occasional rhetorical questions, and confident direct statements instead of hedges.
4. Preserve every fact and every required keyword. Keep keyword density natural; do not strip keywords to sound human.
5. Match the specified brand voice and reading level throughout.
6. Read the result aloud mentally. If any sentence sounds like a template, rewrite it.

## Output

- The rewritten draft, same structure and meaning, natural human voice.
- A short change note summarizing the main AI-tells removed and any keywords retained.

## Quality checklist

- [ ] Meaning and all facts are unchanged.
- [ ] All required keywords are still present and read naturally.
- [ ] No formulaic transitions or "In conclusion" style wrap-ups remain.
- [ ] Sentence and paragraph lengths vary.
- [ ] No hedging filler or empty restatement intro.
- [ ] Em-dashes are not overused; punctuation is varied.
- [ ] Voice matches the brand and audience.
- [ ] Text no longer pattern-matches as AI-generated.
