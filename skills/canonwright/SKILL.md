---
name: canonwright
description: "Canon bibles for adapting a published book with AI image and video models: characters, creatures, places and objects quoted with chapter refs, rulings where the book is silent, the model misses and their fixes, and yes/no canon checks for prompts and takes. Use on 'make a canon bible for', 'is this book-accurate', 'canon check this prompt', 'what does the book say he looks like', 'the model keeps drawing the film version', 'checklist to score takes against the book', 'how is this name pronounced'. Not for matching shots inside one film (cinewright-continuity), real history (historywright), ranking renders (artwright-judge) or the user's own invented worlds."
---

# Canonwright

The book is the canon. A bible records what it says, where, and what models get wrong.

## Step 0

1. Read `evergreen.json` (freshness, see Maintenance).
2. If `CANONWRIGHT_HOME` is set, read `$CANONWRIGHT_HOME/LEARNINGS-private.md` and list `$CANONWRIGHT_HOME/bibles/`: owner rulings and bibles for works under copyright live there, never in this repository.

`CW` below means `python "<this folder>/scripts/cw.py"` (Python 3.8+, stdlib).

## Build a bible

1. `CW new <work> --dir <bibles folder> [--public-domain]`. Works under copyright go in `$CANONWRIGHT_HOME/bibles/`, quotes of 25 words or fewer.
2. Read the book a section at a time with readwright (`rw.py outline`, then the chapters, then grep); never describe from memory or from film and fan images.
3. Fill entries in [bible format](references/bible-format.md) (worked example: [Frankenstein 1818](examples/frankenstein-1818/bible.json)). Every canon line carries a quote and its chapter ref. A trait the book leaves out (hair length, clothes, colour) still gets a value, written as a ruling with its reason, so the model does not drift between shots. Without the book on disk, write a paraphrase marked `"verified": false`.
4. `CW lint --json <bible>` and fix each issue by its `hint`, looping until it prints `[]`; then `CW stamp <bible>` and `CW md <bible>`.
5. When canon changes later, lint reports `stale-hash`: rebuild or recheck what was built from the bible (`CW verify <bible> <export.json ...>` lists outputs from older canon), then `CW stamp` again. `CW export` refuses a stale bible.

## Rules (each failed without this skill)

- **Book first.** Where the book, the popular image (films, fan art), a reference picture or the film's own bible disagree, the book wins unless the owner has ruled otherwise and the ruling is recorded with its reason. When canon changes a state (open chest, empty scabbard), change the bible text and the refs together; the words name the state.
- **Cite or rule.** A prompt or entry built from the book cites chapters for what the book says and labels each filled gap a ruling.
- **Wear in text, per beat.** Blood, dirt and damage that canon places at a moment go in each card's prompt text, after checking the passage for when they appear; never paint them into a reference picture that later shots reuse.
- **Checks are claims.** A checklist for scoring takes is discrete yes/no claims, each with a short code (`yellow-skin`) and a chapter ref, so misses can be counted claim by claim. `CW export --to artwright` hands them to artwright-judge; `--to cinewright` hands identity strings to cinewright-continuity.
- **Names said from the audiobook.** Take the pronunciation of an invented name from the audiobook narrator; never guess, and never use speech-to-text to judge it (it cannot spell invented words).

## Check a prompt or a take

`CW check <bible> <prompt.txt>` flags `never_say` words and lists the checks for each entity the prompt names. Then answer each check yes or no against the take or prompt, citing its ref. Model misses and the fixes that worked: [model misses](references/model-misses.md).

## Maintenance

Evergreen unit: follows the Evergreen Protocol in the installed evergreen plugin; see [MAINTENANCE.md](MAINTENANCE.md). Files: [RESEARCH.md](RESEARCH.md), [CHANGELOG.md](CHANGELOG.md), [LEARNINGS.md](LEARNINGS.md), [TESTS.md](TESTS.md), `evals/evals.json`, `evergreen.json`, `harvest.json`.
