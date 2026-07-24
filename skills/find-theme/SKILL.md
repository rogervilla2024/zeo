---
name: find-theme
description: Sweep the open-source Astro theme ecosystem on GitHub and shortlist the best themes for a niche: hard-filter hundreds of candidates by license, activity, and traction, rank by niche fit, then deep-evaluate finalists with builds and screenshots. Use when the user wants a ready-made theme, asks which theme fits their topic, or wants to evaluate the theme catalog instead of a custom design.
---

# Find the best theme for a niche

Evaluate the whole ecosystem by metadata; clone only finalists.

## Inputs

- Niche description and site type words (blog, magazine, docs, review).
- Optional GITHUB_TOKEN in the environment for a higher API rate limit.

## Instructions

1. Broad sweep and ranking (seconds, no cloning):

   ```bash
   python scripts/find_theme.py --niche "the niche" \
       --keywords blog,magazine --top 6 --json finalists.json
   ```

   This pulls hundreds of astro-theme/astro-template repositories,
   drops non-permissive licenses, repos idle for 18+ months, and low
   traction, then ranks by niche keyword match, stars, freshness.
2. Deep-evaluate the finalists (only these get cloned):
   - clone each finalist shallow, `npm install && npm run build`
   - run `check_js_budget.py --dist dist` (a theme over ~60 KB before
     our content is a red flag)
   - screenshot the built homepage with Playwright at 390/768/1440 px
   - note schema/SEO gaps (most themes need our SEO spine anyway)
3. Report to the user: for each finalist, the screenshots, stars,
   license, JS weight, what fits the niche, what needs surgery, and
   your single recommendation with reasons.
4. On the user's pick, hand off to the adopt-theme skill.

## Output

- Ranked finalist report with screenshots and one recommendation.

## Quality checklist

- Only permissive-license themes are ever recommended.
- Every recommendation was actually built, budget-checked, and
  screenshotted; no judging by README alone.
- Rate limits respected: one sweep, finalists capped.
