# canonwright

A Claude Code plugin for adapting a published book with AI image and video models. It keeps a canon bible per book: what the text says each character, creature, place and object looks like (quoted, with chapter refs), what you ruled where the book is silent, what the models keep getting wrong and what fixed it, and yes/no checks you can score takes against.

## Install

```
claude plugin marketplace add m4bwav/canonwright
claude plugin install canonwright@canonwright
```

## Quick start

Ask "make a canon bible for the Morlocks from The Time Machine" or "canon check this prompt against the bible". The skill reads the book a section at a time (with readwright, if installed) and uses `cw.py`:

```
python skills/canonwright/scripts/cw.py new "The Time Machine" --dir bibles --public-domain
python skills/canonwright/scripts/cw.py lint bibles/the-time-machine
python skills/canonwright/scripts/cw.py check bibles/the-time-machine prompt.txt
python skills/canonwright/scripts/cw.py export bibles/the-time-machine --to artwright
```

Python 3.8+, standard library only. Worked example: [Frankenstein (1818)](skills/canonwright/examples/frankenstein-1818/bible.md), where the book's creature (yellow skin, flowing black hair, black lips) is not the film's.

## Private bibles

Books under copyright should not have their text in a public repository. Set `CANONWRIGHT_HOME` to a private folder; the skill reads `bibles/` and `LEARNINGS-private.md` from there, and `cw.py lint` keeps quotes from such works to 25 words.

## Tests

```
python -m unittest discover -s tests
```

The leak test needs a term list (`$CANONWRIGHT_HOME/leak-terms.txt` or `~/.canonwright/leak-terms.txt`) and fails without one.

## Licence

MIT
