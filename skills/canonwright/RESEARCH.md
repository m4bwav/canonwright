# Research: canonwright

Findings that back [SKILL.md](SKILL.md). Changes they caused are in [CHANGELOG.md](CHANGELOG.md); lessons in [LEARNINGS.md](LEARNINGS.md); runs in [TESTS.md](TESTS.md); state in `evergreen.json`. Protocol: [MAINTENANCE.md](MAINTENANCE.md).

Topic: canon bibles for adapting books with AI image and video models. Tier `slow`. The web creation pass is owed (next_due is set to the build day so the first use runs it).

## Current understanding

- The method rests on one owner's practice across several novel adaptations (harvest of 62 lessons, 2026-11-15) and a bare-model baseline: 7 of 12 canon cases passed without the skill. The five that failed became the skill's rules (cite or rule, book first, wear in text, coded checks, audiobook pronunciation); the rest sit in references/model-misses.md as a lookup.
- Prior art (private notes): story-bible tools for writers and continuity tools for AI video exist; none found that ties a published book's quoted text to model misses and yes/no checks. To be confirmed by the creation pass.
- Quotes from works under copyright stay short (25 words) and out of public files; public examples use public-domain texts.

## Open questions

- Do current video models (2026) still draw film looks for public-domain monsters when the description is explicit?
- Is there a maintained story-bible or lorebook format (for example SillyTavern lorebooks, Sudowrite story bible) worth exporting to?

## Search plan

Subject: `"story bible" AI video consistency <year>`; `book adaptation AI film character consistency <year>`; `"character bible" prompt video model`.
Tooling: `path:SKILL.md "story bible"` and `path:SKILL.md canon` on GitHub; `registry.modelcontextprotocol.io/v0/servers?search=lore`; `"lorebook" OR "story bible" mcp server`.
Practice: `r/aivideo book adaptation consistency`; `"AI film" novel adaptation workflow <year>`.
Testing: `vision language model checklist evaluation image prompt adherence <year>` (TIFA, DSG, VQAScore style yes/no checks).

## Findings log

### R-20261115-1 · 2026-11-15 · Build from harvest and baseline (no web pass yet)
- Summary: rules taken from the owner harvest and the bare baseline; web creation pass on all four tracks is owed. Cost: no searches.
- Track: practice
- Sources: private harvest and baseline (sidecar)
- Magnitude: n/a (initial)
- Applied: C-20261115-1
