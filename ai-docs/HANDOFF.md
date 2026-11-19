# Handoff: canonwright

State (2026-11-18): 0.2.0 released (lint --json, canon hash stamp; sidecar bibles not yet stamped). Earlier: 0.1.0 released PUBLIC (https://github.com/m4bwav/canonwright/releases/tag/v0.1.0). History passed the leak check (0 of 25 terms in `git log -p --all`, PR text), so the repo was switched to public in place, no fresh repo. Installed as canonwright@mark-local. Banner in .github/images (FLUX.3 seed 61101, recipe beside it). Bibles for works under copyright, owner lessons and the term list live in the private sidecar (`CANONWRIGHT_HOME`).

Next:
1. Wiki: m4bwav/canonwright.wiki.git does not exist. Mark saves a first page at https://github.com/m4bwav/canonwright/wiki/_new; then clone the wiki, copy ai-docs/notes/wiki-pages/*.md in, push, run `wikiwright.py live`.
2. Read the books on disk through readwright and turn the sidecar stubs' unverified paraphrases into quotes with refs.
3. CI (self-hosted runner or none; public repo can use GitHub Actions).
