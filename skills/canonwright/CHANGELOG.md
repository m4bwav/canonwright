# Changelog: canonwright

Every change to [SKILL.md](SKILL.md) and its companions, newest first, each with the reason. Reasons cite findings in [RESEARCH.md](RESEARCH.md) (`R-`), lessons in [LEARNINGS.md](LEARNINGS.md) (`L-`), and test runs in [TESTS.md](TESTS.md) (`T-`). State in `evergreen.json`. Protocol: MAINTENANCE.md.

Entry shape: `### C-YYYYMMDD-n · date · one-line summary`, then `because:` (IDs or "user request"), `files:` (file and section), and a sentence on what changed. Cite section headings, not line numbers.

### C-20261119-2 · 2026-11-19 · Release 0.3.0
- because: C-20261119-1
- files: .claude-plugin/plugin.json, .claude-plugin/marketplace.json, evergreen.json (version)
- Version 0.2.0 to 0.3.0, tag v0.3.0.

### C-20261119-1 · 2026-11-19 · motif kind with states; place role
- because: book learnings round 6 (Truby, The Anatomy of Story, ch. 6-7)
- files: references/bible-format.md, scripts/cw.py (KINDS, lint, md), tests/test_cw.py (Lint)
- Optional `motif` kind with `states` `{state, ref}` per appearance and optional `role` `{text, ref}` on places; lint requires the ref (`state-incomplete`, `role-incomplete`). Existing bibles lint unchanged.

### C-20261118-1 · 2026-11-18 · lint --json loop and canon hash stamp
- because: technique harvest from legend-of-alan/spookery (checker that prints [] when clean; pack_rev content hash), ideas only
- files: SKILL.md (Build a bible), references/bible-format.md, scripts/cw.py (lint, stamp, verify, export), tests/test_cw.py (JsonAndHash), examples/frankenstein-1818/bible.json (stamped)
- The agent loops on `lint --json` until `[]`; a stale canon hash blocks export until `stamp`, and `verify` names outputs built from older canon.

### C-20261115-2 · 2026-11-15 · cw.py export --out
- because: user request
- files: scripts/cw.py (export), tests/test_cw.py (Export)
- `export` can write its JSON to a file with `--out` instead of stdout.

### C-20261115-1 · 2026-11-15 · Created as an evergreen unit
- because: user request
- files: SKILL.md, RESEARCH.md, LEARNINGS.md, evergreen.json (skills: also TESTS.md and evals/evals.json)
- Initial version. Tier `slow`, interval 120d. See R-20261115-1 for the research basis; the first test run, for a skill, is logged in TESTS.md.
