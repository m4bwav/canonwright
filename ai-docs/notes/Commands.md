All commands: `python skills/canonwright/scripts/cw.py <command>`. A `<bible>` is a folder holding `bible.json`, or the `bible.json` path itself. Exit codes: 0 ok, 1 findings, 2 usage or file error.

## new

`new <work> [--dir D] [--title T] [--author A] [--edition E] [--public-domain]` starts a bible folder named after the work's slug.

## lint

`lint [bible ...]` checks bibles; with no argument it checks `examples/` and `$CANONWRIGHT_HOME/bibles`.

```sh
python skills/canonwright/scripts/cw.py lint skills/canonwright/examples/frankenstein-1818
```

```text
skills/canonwright/examples/frankenstein-1818: ok
```

## md

`md <bible>` regenerates `bible.md` from `bible.json`. Run it after every edit to the JSON.

## check

`check <bible> <prompt.txt> [--json]` flags `never_say` words in the prompt and lists the checks for the entities it names. See [Getting started](Getting-Started#a-first-check).

## export

`export <bible> --to cinewright|artwright [--out FILE]` writes JSON for the cinewright plugin (identity strings per character) or artwright-judge (yes/no brief checks with refs). Without `--out` it prints to stdout; `--out` (new in 0.1.0) writes the file, creating folders, and prints `wrote FILE`.

```sh
python skills/canonwright/scripts/cw.py export skills/canonwright/examples/frankenstein-1818 --to artwright --out brief.json
```

```text
wrote brief.json
```

The file starts:

```json
{
  "brief_checks": [
    {
      "id": "creature-yellow-skin",
      "question": "skin reads yellowish, thin over muscle, not green or grey",
      "answer": "yes",
      "ref": "Vol. I, ch. IV"
    },
```
