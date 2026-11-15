# AGENTS.md: canonwright

Claude Code plugin (one skill): canon bibles for adapting published books with AI image and video models.

- Layout: `.claude-plugin/plugin.json`; `skills/canonwright/` (SKILL.md, references/, scripts/cw.py, examples/ with one public-domain bible, evals/, evergreen files); `tests/`.
- Before committing: `python -m unittest discover -s tests` with `CANONWRIGHT_HOME` pointing at the private sidecar. The leak test FAILS when no term list is found (sidecar `leak-terms.txt`, or the fallback `~/.canonwright/leak-terms.txt`).
- No copyrighted text in this repository. Public examples come from public-domain works only. Bibles for works under copyright, owner rulings and owner lessons live in `CANONWRIGHT_HOME` (`bibles/`, `LEARNINGS-private.md`).
- Never put the owner's paths, project names or the names of the books he adapts in a tracked file, ai-docs/ included.
- After editing an example bible.json, run `cw.py md` on it (a test checks bible.md is current).
- Python edits keep LF line endings; write Python with a file tool, not a Bash heredoc.
- State and handoff: [ai-docs/HANDOFF.md](ai-docs/HANDOFF.md), log [ai-docs/log.md](ai-docs/log.md), index [ai-docs/INDEX.md](ai-docs/INDEX.md).
