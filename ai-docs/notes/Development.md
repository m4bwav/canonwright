```sh
git clone https://github.com/m4bwav/canonwright
cd canonwright
python -m unittest discover -s tests
```

The leak test needs a term list at `$CANONWRIGHT_HOME/leak-terms.txt` or `~/.canonwright/leak-terms.txt` and fails without one, so a missing list cannot pass silently. Public examples come from public-domain works only. Python files keep LF line endings. Project rules are in [AGENTS.md](https://github.com/m4bwav/canonwright/blob/main/AGENTS.md).
