## Install

```sh
claude plugin marketplace add m4bwav/canonwright
claude plugin install canonwright@canonwright
```

Python 3.8 or later, standard library only. The skill reads books a section at a time with the readwright plugin when it is installed.

## A first bible

Ask Claude "make a canon bible for the Morlocks from The Time Machine". The skill starts the bible with `cw.py new`, fills it from the book, and lints it. By hand:

```sh
python skills/canonwright/scripts/cw.py new "The Time Machine" --dir bibles --public-domain
```

This writes `bibles/the-time-machine/bible.json` and `bible.md`.

## A first check

Write a prompt to a file and check it against the worked example:

```sh
echo "a tall pale creature with green skin and bolts in his neck" > prompt.txt
python skills/canonwright/scripts/cw.py check skills/canonwright/examples/frankenstein-1818 prompt.txt
```

```text
NEVER SAY  creature: 'bolts'
NEVER SAY  creature: 'green skin'
```

The exit code is 1 because there were findings.

## Private bibles

Do not put the text of a book under copyright in a public repository. Set `CANONWRIGHT_HOME` to a private folder; the skill reads `bibles/` and `LEARNINGS-private.md` from there, and `lint` keeps quotes from works that are not public domain to 25 words.
