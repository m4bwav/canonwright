# Changelog: canonwright

Every change to [SKILL.md](SKILL.md) and its companions, newest first, each with the reason. Reasons cite findings in [RESEARCH.md](RESEARCH.md) (`R-`), lessons in [LEARNINGS.md](LEARNINGS.md) (`L-`), and test runs in [TESTS.md](TESTS.md) (`T-`). State in `evergreen.json`. Protocol: MAINTENANCE.md.

Entry shape: `### C-YYYYMMDD-n · date · one-line summary`, then `because:` (IDs or "user request"), `files:` (file and section), and a sentence on what changed. Cite section headings, not line numbers.

### C-20261115-2 · 2026-11-15 · cw.py export --out
- because: user request
- files: scripts/cw.py (export), tests/test_cw.py (Export)
- `export` can write its JSON to a file with `--out` instead of stdout.

### C-20261115-1 · 2026-11-15 · Created as an evergreen unit
- because: user request
- files: SKILL.md, RESEARCH.md, LEARNINGS.md, evergreen.json (skills: also TESTS.md and evals/evals.json)
- Initial version. Tier `slow`, interval 120d. See R-20261115-1 for the research basis; the first test run, for a skill, is logged in TESTS.md.
