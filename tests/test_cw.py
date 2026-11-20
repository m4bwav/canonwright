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
        self.assertEqual(len([x for x in w if "paraphrase" in x]), 1)

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

    def test_motif_states_need_ref(self):
        good = entry(kind="motif", states=[{"state": "whole", "ref": "ch. 2"}, {"state": "cracked", "ref": "ch. 9"}])
        self.assertEqual(self.errs(good), [])
        self.assertTrue(self.errs(entry(kind="motif", states=[{"state": "cracked"}])))
        self.assertTrue(self.errs(entry(kind="motif", states=["cracked"])))

    def test_place_role_needs_ref(self):
        self.assertEqual(self.errs(entry(kind="place", role={"text": "hems him in", "ref": "ch. 3"})), [])
        self.assertTrue(self.errs(entry(kind="place", role={"text": "hems him in"})))
        self.assertTrue(self.errs(entry(kind="place", role="hems him in")))

    def test_motif_and_role_render(self):
        md = cw.render_md({"entries": [entry(kind="motif", states=[{"state": "cracked", "ref": "ch. 9"}],
                                             role={"text": "frees her", "ref": "ch. 4"})]})
        self.assertIn("State at ch. 9: cracked", md)
        self.assertIn("Role for the hero: frees her (ch. 4)", md)

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

    def test_out_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "sub", "brief.json")
            rc = cw.main(["export", EXAMPLE, "--to", "artwright", "--out", path])
            self.assertEqual(rc, 0)
            with open(path, encoding="utf-8") as f:
                self.assertIn("brief_checks", json.load(f))


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


class JsonAndHash(unittest.TestCase):
    def run_cw(self, *args):
        return subprocess.run([sys.executable, os.path.join(SKILL, "scripts", "cw.py")] + list(args),
                              capture_output=True, text=True, encoding="utf-8")

    def copy_example(self, d):
        p = os.path.join(d, "b")
        os.makedirs(p)
        with open(os.path.join(EXAMPLE, "bible.json"), encoding="utf-8") as f:
            text = f.read()
        with open(os.path.join(p, "bible.json"), "w", encoding="utf-8", newline="") as f:
            f.write(text)
        return p

    def test_lint_json_clean_is_empty_list(self):
        r = self.run_cw("lint", "--json", EXAMPLE)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(json.loads(r.stdout), [])

    def test_lint_json_issue_fields(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.copy_example(d)
            bp = os.path.join(p, "bible.json")
            b = cw.load(p)
            b["entries"][1]["canon"][0].pop("ref")
            b["canon_hash"] = cw.canon_hash(b)
            with open(bp, "w", encoding="utf-8") as f:
                json.dump(b, f, indent=2)
            r = self.run_cw("lint", "--json", p)
            self.assertEqual(r.returncode, 1)
            issues = json.loads(r.stdout)
            self.assertEqual([i["code"] for i in issues], ["no-ref"])
            i = issues[0]
            self.assertTrue(i["file"].endswith("bible.json") and i["hint"])
            with open(bp, encoding="utf-8") as f:
                self.assertIn(b["entries"][1]["id"], f.read().splitlines()[i["line"] - 1])

    def test_hash_ignores_formatting_and_stamp(self):
        b = cw.load(EXAMPLE)
        c = json.loads(json.dumps(b))
        c["canon_hash"] = "sha256:other"
        self.assertEqual(cw.canon_hash(b), cw.canon_hash(c))
        self.assertEqual(b["canon_hash"], cw.canon_hash(b))

    def test_stale_until_restamp(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.copy_example(d)
            bp = os.path.join(p, "bible.json")
            out = os.path.join(d, "checks.json")
            self.assertEqual(self.run_cw("export", p, "--to", "artwright", "--out", out).returncode, 0)
            self.assertEqual(self.run_cw("verify", p, out).returncode, 0)
            with open(bp, encoding="utf-8") as f:
                text = f.read()
            with open(bp, "w", encoding="utf-8") as f:
                f.write(text.replace("yellow skin", "green skin", 1))
            r = self.run_cw("lint", "--json", p)
            self.assertEqual([i["code"] for i in json.loads(r.stdout)], ["stale-hash"])
            self.assertEqual(self.run_cw("export", p, "--to", "artwright").returncode, 1)
            self.assertEqual(self.run_cw("lint", "--json", p).returncode, 1)
            self.assertEqual(self.run_cw("stamp", p).returncode, 0)
            self.assertEqual(json.loads(self.run_cw("lint", "--json", p).stdout), [])
            r = self.run_cw("verify", "--json", p, out)
            self.assertEqual(r.returncode, 1)
            self.assertEqual([x["code"] for x in json.loads(r.stdout)], ["stale-output"])

    def test_stamp_keeps_formatting(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.copy_example(d)
            bp = os.path.join(p, "bible.json")
            with open(bp, encoding="utf-8") as f:
                before = f.read()
            self.run_cw("stamp", p)
            with open(bp, encoding="utf-8") as f:
                self.assertEqual(f.read(), before)


if __name__ == "__main__":
    unittest.main()
