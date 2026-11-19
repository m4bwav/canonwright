# Changelog

## [0.2.0] - 2026-11-18

- `cw.py lint --json`: prints `[]` when clean, else one object per issue with file, line, a stable code and a hint; the skill loops on it until `[]`.
- Canon hash: `cw.py stamp` records a hash of the bible's canon in `canon_hash`; `export` outputs carry it; lint reports `stale-hash` after canon changes and `export` refuses until an explicit re-stamp; `cw.py verify` lists outputs built from older canon.
- Ideas credited to legend-of-alan/spookery (its author-pack checker loop and `pack_rev` content hash); written fresh, no code copied.

## [0.1.0] - 2026-11-15

First public release.

- canonwright skill: canon bibles with quoted descriptions and chapter refs, rulings where the book is silent, model misses and fixes, yes/no canon checks.
- `cw.py` (standard-library Python): `new`, `lint`, `md`, `check`, `export --to cinewright|artwright [--out FILE]`.
- Public-domain example bible (Frankenstein, 1818 text), unit tests, a leak test that fails without a term list, eval suite.
