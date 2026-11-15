# Handoff: canonwright

State (2026-11-15): 0.1.0 built (step E), private repo, not released or tagged. One skill, cw.py (new, lint, md, check, export), Frankenstein 1818 example bible, unit tests and a leak test that fails without a term list. Bibles for works under copyright, owner lessons and the term list live in the private sidecar (`CANONWRIGHT_HOME`).

Next (step F):
1. Web creation pass on all four tracks (RESEARCH.md search plan); next_due is set to the build day.
2. Run the eval suite with the skill (evals/evals.json: 12 cases, 1 action case, 3 decoys) and compare to the bare baseline (7/12); evergreen-worth verdict.
3. Read the books on disk through readwright and turn the sidecar stubs' unverified paraphrases into quotes with refs.
4. README banner, wiki, CI; decide public release with the owner.
