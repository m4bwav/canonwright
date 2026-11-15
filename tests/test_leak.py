"""Fails if a private term appears in a public file.

Terms come from $CANONWRIGHT_HOME/leak-terms.txt, else from the fixed fallback
~/.canonwright/leak-terms.txt (one term per line, # comments). If neither file
exists the test FAILS: a leak check that silently skips proves nothing.
A term matches case-insensitively and not inside a longer word. Every tracked
and untracked-but-not-ignored file is checked, ai-docs/ included.
"""
import os
import re
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOW_FILES = {"tests/test_leak.py"}
FALLBACK = os.path.join(os.path.expanduser("~"), ".canonwright", "leak-terms.txt")


def terms_file():
    home = os.environ.get("CANONWRIGHT_HOME")
    if home:
        p = os.path.join(os.path.expanduser(home), "leak-terms.txt")
        if os.path.isfile(p):
            return p
    return FALLBACK if os.path.isfile(FALLBACK) else None


def load_terms(path):
    with open(path, "r", encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip() and not ln.lstrip().startswith("#")]


def public_files():
    try:
        r = subprocess.run(["git", "-C", ROOT, "ls-files", "--cached", "--others", "--exclude-standard"],
                           capture_output=True, text=True, check=True)
        files = r.stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        files = []
        for d, _, fs in os.walk(ROOT):
            for f in fs:
                files.append(os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, "/"))
    return [f for f in files if not f.startswith(".git/") and f not in ALLOW_FILES
            and "__pycache__/" not in f and not f.endswith(".pyc")]


def pattern(term):
    left = r"(?<![A-Za-z0-9])" if term[0].isalnum() else ""
    right = r"(?![A-Za-z0-9])" if term[-1].isalnum() else ""
    return re.compile(left + re.escape(term) + right, re.I)


class LeakTest(unittest.TestCase):
    def test_terms_file_found(self):
        self.assertIsNotNone(terms_file(), "no leak-terms.txt: set CANONWRIGHT_HOME or create %s" % FALLBACK)

    def test_no_private_terms(self):
        p = terms_file()
        self.assertIsNotNone(p, "no leak-terms.txt: set CANONWRIGHT_HOME or create %s" % FALLBACK)
        terms = load_terms(p)
        self.assertTrue(terms, "leak-terms.txt is empty")
        pats = [(t, pattern(t)) for t in terms]
        hits = []
        for rel in public_files():
            hits += ["%s (file name): %s" % (rel, t) for t, pt in pats if pt.search(rel)]
            try:
                with open(os.path.join(ROOT, rel), "r", encoding="utf-8", errors="replace") as f:
                    text = f.read()
            except OSError:
                continue
            hits += ["%s: %s" % (rel, t) for t, pt in pats if pt.search(text)]
        self.assertEqual(hits, [], "private terms in public files")


if __name__ == "__main__":
    unittest.main()
