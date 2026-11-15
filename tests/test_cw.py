import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "canonwright")
sys.path.insert(0, os.path.join(SKILL, "scripts"))
import cw  # noqa: E402

EXAMPLE = os.path.join(SKILL, "examples", "frankenstein-1818")


def entry(**kw):
    e = {"id": "x", "kind": "character", "name": "X",
         "canon": [{"quote": "a tall man", "ref": "ch. 1"}]}
    e.update(kw)
    return e


class Lint(unittest.TestCase):
    def errs(self, e, pd=False):
        return cw.lint_bible({"public_domain": pd, "entries": [e]})[0]

    def test_example_clean(self):
        self.assertEqual(cw.lint_bible(cw.load(EXAMPLE)), ([], []))

    def test_missing_ref(self):
        self.assertTrue(self.errs(entry(canon=[{"quote": "a tall man"}])))

    def test_missing_quote(self):
        self.assertTrue(self.errs(entry(canon=[{"ref": "ch. 1"}])))

    def test_paraphrase_needs_unverified(self):
        self.assertTrue(self.errs(entry(canon=[{"paraphrase": "tall", "ref": "ch. 1"}])))
        e, w = cw.lint_bible({"entries": [entry(canon=[{"paraphrase": "tall", "ref": "ch. 1", "verified": False}])]})
        self.assertEqual(e, [])
        self.assertEqual(len(w), 1)

    def test_long_quote_only_public_domain(self):
        q = " ".join(["word"] * 30)
        e = entry(canon=[{"quote": q, "ref": "ch. 1"}])
        self.assertTrue(self.errs(e))
        self.assertEqual(self.errs(e, pd=True), [])

    def test_ruling_needs_why(self):
        self.assertTrue(self.errs(entry(ruling=[{"text": "short hair"}])))

    def test_miss_needs_fix(self):
        self.assertTrue(self.errs(entry(misses=[{"miss": "green skin"}])))

    def test_check_needs_code_and_ref(self):
        self.assertTrue(self.errs(entry(checks=["yellow skin"])))
        self.assertTrue(self.errs(entry(checks=[{"code": "a", "claim": "b"}])))
        dup = [{"code": "a", "claim": "b", "ref": "c"}] * 2
        self.assertTrue(self.errs(entry(checks=dup)))

    def test_bad_kind_and_dup_id(self):
        self.assertTrue(self.errs(entry(kind="robot")))
        b = {"entries": [entry(), entry()]}
        self.assertTrue(cw.lint_bible(b)[0])


class Check(unittest.TestCase):
    def test_never_say_and_checks(self):
        b = cw.load(EXAMPLE)
        r = cw.check_prompt(b, "Frankenstein's monster stands in the laboratory, green skin glowing.")
        words = {h["word"] for h in r["never_say"]}
        self.assertIn("green skin", words)
        self.assertIn("laboratory", words)
        codes = {k["code"] for k in r["checks"]}
        self.assertIn("yellow-skin", codes)

    def test_word_boundary(self):
        b = {"entries": [entry(never_say=["heron"])]}
        self.assertEqual(cw.check_prompt(b, "the herons fly")["never_say"], [])
        self.assertEqual(len(cw.check_prompt(b, "a Heron spear")["never_say"]), 1)

    def test_clean_prompt(self):
        r = cw.check_prompt(cw.load(EXAMPLE), "A ship locked in Arctic ice at dawn.")
        self.assertEqual(r, {"never_say": [], "checks": []})


class Export(unittest.TestCase):
    def test_cinewright(self):
        out = cw.export(cw.load(EXAMPLE), "cinewright")
        self.assertIn("creature", out["characters"])
        self.assertNotIn("workshop", out["characters"])
        self.assertIn("yellow skin", out["characters"]["creature"]["identity"])

    def test_artwright(self):
        out = cw.export(cw.load(EXAMPLE), "artwright")
        ids = {c["id"] for c in out["brief_checks"]}
        self.assertIn("creature-black-lips", ids)
        self.assertTrue(all(c["ref"] for c in out["brief_checks"]))


class Cli(unittest.TestCase):
    def run_cw(self, *args):
        return subprocess.run([sys.executable, os.path.join(SKILL, "scripts", "cw.py")] + list(args),
                              capture_output=True, text=True)

    def test_new_lint_md(self):
        with tempfile.TemporaryDirectory() as d:
            r = self.run_cw("new", "Moby Dick", "--dir", d, "--public-domain")
            self.assertEqual(r.returncode, 0, r.stderr)
            p = os.path.join(d, "moby-dick")
            with open(os.path.join(p, "bible.json"), encoding="utf-8") as f:
                b = json.load(f)
            self.assertTrue(b["public_domain"])
            self.assertTrue(os.path.isfile(os.path.join(p, "bible.md")))
            self.assertEqual(self.run_cw("lint", p).returncode, 0)
            self.assertEqual(self.run_cw("new", "Moby Dick", "--dir", d).returncode, 2)

    def test_check_exit_code(self):
        with tempfile.TemporaryDirectory() as d:
            pf = os.path.join(d, "p.txt")
            with open(pf, "w", encoding="utf-8") as f:
                f.write("the monster in a laboratory")
            self.assertEqual(self.run_cw("check", EXAMPLE, pf).returncode, 1)

    def test_example_md_current(self):
        with open(os.path.join(EXAMPLE, "bible.md"), encoding="utf-8") as f:
            self.assertEqual(f.read(), cw.render_md(cw.load(EXAMPLE)))

    def test_lint_sidecar_bibles(self):
        if not os.environ.get(cw.HOME_ENV):
            self.skipTest("CANONWRIGHT_HOME unset")
        self.assertEqual(self.run_cw("lint").returncode, 0, self.run_cw("lint").stdout)


if __name__ == "__main__":
    unittest.main()
