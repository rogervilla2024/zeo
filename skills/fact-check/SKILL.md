---
name: fact-check
description: Verifies factual claims in a draft, adds citations, flags unsupported statements, and corrects wrong statistics, dates, names, and quotes. Use when the user wants to fact-check content, verify claims, add sources or citations, check accuracy of stats and dates, validate an article before publishing, or find and fix unsupported assertions.
---

Audits a draft for factual accuracy and returns a corrected, cited version plus a claim-by-claim report.

## Inputs

- The draft text to verify.
- Domain and niche (to calibrate what counts as an authoritative source).
- Citation style or format the site uses (inline links, footnotes, reference list).
- Any facts already known to be correct or off-limits.
- Locale and recency requirements (how current stats must be).

You may delegate verification to the `fact-checker` subagent via the Task/Agent mechanism and then review its report against the checklist.

## Instructions

1. Extract every checkable claim: statistics, dates, names, quotes, product specs, historical facts, cause-effect assertions, and superlatives ("the largest", "the first", "the only").
2. Classify each claim: verifiable and material, verifiable but minor, opinion, or vague/unfalsifiable.
3. Verify each material claim against authoritative, primary sources (official data, standards bodies, original publishers, reputable outlets). Use current web sources where recency matters. Prefer primary over secondary sources.
4. For each claim, record a status: Supported, Corrected, Unsupported, or Outdated.
   - Supported: add a citation to the source.
   - Corrected: fix the number, date, name, or quote and cite the correct source.
   - Unsupported: flag it. Either remove it, soften it to an attributed opinion, or request a source.
   - Outdated: replace with the current figure and cite.
5. Check internal consistency: numbers that should sum, dates in sequence, names spelled consistently.
6. Insert citations in the site's required format. Never fabricate a source, URL, or quote. If a claim cannot be verified, say so explicitly rather than inventing support.
7. Preserve wording and keywords except where a correction is required.

## Output

- The corrected draft with citations added inline or as references per site style.
- A claim ledger: each claim, its status (Supported/Corrected/Unsupported/Outdated), the source, and the change made.
- A flag list of any claims that still need human sourcing or a decision to cut.

## Quality checklist

- [ ] Every statistic, date, name, and quote was checked.
- [ ] All corrections are backed by a cited authoritative source.
- [ ] No fabricated sources, URLs, or quotes.
- [ ] Unsupported claims are flagged, softened, or removed, never left as bare assertions.
- [ ] Outdated figures replaced with current data.
- [ ] Internal numeric and naming consistency holds.
- [ ] Citations follow the site's format.
- [ ] Meaning and keywords preserved outside of necessary corrections.
