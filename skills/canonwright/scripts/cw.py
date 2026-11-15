#!/usr/bin/env python3
"""canonwright: canon bibles for adapting a book with AI image and video models.

Commands (stdlib only, deterministic):
  new <work> [--dir D] [--title T] [--author A] [--edition E] [--public-domain]
  lint [bible ...]            check bibles (default: examples/ and $CANONWRIGHT_HOME/bibles)
  md <bible>                  regenerate bible.md from bible.json
  check <bible> <prompt.txt>  flag never_say words, list checks for entities named
  export <bible> --to cinewright|artwright

A <bible> is a folder holding bible.json, or the bible.json path itself.
Exit codes: 0 ok, 1 findings, 2 usage or file error.
"""
import argparse
import json
import os
import re
import sys

HOME_ENV = "CANONWRIGHT_HOME"
MAX_QUOTE_WORDS = 25
KINDS = {"character", "creature", "place", "object", "magic", "tech", "event"}
HERE = os.path.dirname(os.path.abspath(__file__))
EXAMPLES = os.path.join(os.path.dirname(HERE), "examples")


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "work"


def bible_path(p):
    return p if p.endswith(".json") else os.path.join(p, "bible.json")


def load(p):
    with open(bible_path(p), "r", encoding="utf-8") as f:
        return json.load(f)


def write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def render_md(b):
    out = ["# Canon bible: %s" % b.get("title", b.get("work", "")), ""]
    meta = "%s; edition: %s; public domain: %s" % (
        b.get("author", "?"), b.get("edition", "?"), "yes" if b.get("public_domain") else "no")
    out += [meta, "", "Generated from bible.json by `cw.py md`; edit the JSON, not this file.", ""]
    for e in b.get("entries", []):
        out += ["## %s (%s)" % (e.get("name", e.get("id")), e.get("kind", "?")), ""]
        for c in e.get("canon", []):
            body = c.get("quote") and '"%s"' % c["quote"] or "(paraphrase) %s" % c.get("paraphrase", "")
            flag = "" if c.get("verified", True) else " [unverified]"
            out.append("- %s (%s)%s" % (body, c.get("ref", "no ref"), flag))
        for r in e.get("ruling", []):
            out.append("- Ruling: %s (why: %s; by %s, %s)" % (r.get("text"), r.get("why"), r.get("by", "?"), r.get("date", "?")))
        if e.get("prefer"):
            out.append("- Prefer: %s" % e["prefer"])
        for m in e.get("misses", []):
            out.append("- Model miss (%s): %s. Fix: %s%s" % (m.get("model", "any"), m.get("miss"), m.get("fix"),
                                                         "" if m.get("verified") else " [fix unverified]"))
        if e.get("never_say"):
            out.append("- Never say: %s" % ", ".join(e["never_say"]))
        for k in e.get("checks", []):
            out.append("- Check `%s`: %s (%s)" % (k.get("code"), k.get("claim"), k.get("ref")))
        for c in e.get("corrections", []):
            out.append("- Correction %s%s: %s" % (c.get("id"), " (locked)" if c.get("locked") else "", c.get("text")))
        out.append("")
    return "\n".join(out)


def cmd_new(a):
    work = slug(a.work)
    d = os.path.join(a.dir or ".", work)
    if os.path.exists(bible_path(d)):
        print("exists: %s" % bible_path(d), file=sys.stderr)
        return 2
    os.makedirs(d, exist_ok=True)
    b = {"work": work, "title": a.title or a.work, "author": a.author or "", "edition": a.edition or "",
         "public_domain": bool(a.public_domain), "entries": []}
    write_text(bible_path(d), json.dumps(b, indent=2, ensure_ascii=False) + "\n")
    write_text(os.path.join(d, "bible.md"), render_md(b))
    print(d)
    return 0


def lint_bible(b):
    """Return (errors, warnings) as lists of strings."""
    errs, warns = [], []
    pd = bool(b.get("public_domain"))
    ids = set()
    for e in b.get("entries", []):
        eid = e.get("id") or "?"
        if eid in ids:
            errs.append("%s: duplicate id" % eid)
        ids.add(eid)
        if e.get("kind") not in KINDS:
            errs.append("%s: kind must be one of %s" % (eid, ", ".join(sorted(KINDS))))
        if not e.get("canon"):
            errs.append("%s: no canon lines" % eid)
        for i, c in enumerate(e.get("canon", [])):
            where = "%s canon[%d]" % (eid, i)
            if not c.get("ref"):
                errs.append("%s: no chapter ref" % where)
            if c.get("quote"):
                n = len(c["quote"].split())
                if not pd and n > MAX_QUOTE_WORDS:
                    errs.append("%s: quote of %d words from a work under copyright (max %d)" % (where, n, MAX_QUOTE_WORDS))
            elif c.get("paraphrase"):
                if c.get("verified", True):
                    errs.append("%s: paraphrase without a quote must be marked verified false" % where)
                else:
                    warns.append("%s: unverified paraphrase; quote it when the book text is on disk" % where)
            else:
                errs.append("%s: no quote" % where)
        for i, r in enumerate(e.get("ruling", [])):
            if not r.get("text") or not r.get("why"):
                errs.append("%s ruling[%d]: needs text and why" % (eid, i))
        for i, m in enumerate(e.get("misses", [])):
            if not m.get("miss") or not m.get("fix"):
                errs.append("%s misses[%d]: needs miss and fix" % (eid, i))
        codes = set()
        for i, k in enumerate(e.get("checks", [])):
            if not isinstance(k, dict) or not k.get("code") or not k.get("claim") or not k.get("ref"):
                errs.append("%s checks[%d]: needs code, claim and ref" % (eid, i))
            elif k["code"] in codes:
                errs.append("%s checks[%d]: duplicate code %s" % (eid, i, k["code"]))
            else:
                codes.add(k["code"])
        for i, c in enumerate(e.get("corrections", [])):
            if not c.get("id") or not c.get("text"):
                errs.append("%s corrections[%d]: needs id and text" % (eid, i))
    return errs, warns


def default_bibles():
    roots = [EXAMPLES]
    home = os.environ.get(HOME_ENV)
    if home:
        roots.append(os.path.join(os.path.expanduser(home), "bibles"))
    found = []
    for r in roots:
        if os.path.isdir(r):
            for d in sorted(os.listdir(r)):
                if os.path.isfile(os.path.join(r, d, "bible.json")):
                    found.append(os.path.join(r, d))
    return found


def cmd_lint(a):
    paths = a.bibles or default_bibles()
    bad = 0
    for p in paths:
        try:
            errs, warns = lint_bible(load(p))
        except (OSError, ValueError) as ex:
            print("%s: cannot read: %s" % (p, ex))
            bad += 1
            continue
        for w in warns:
            print("%s: warning: %s" % (p, w))
        for e in errs:
            print("%s: %s" % (p, e))
        bad += len(errs)
        if not errs:
            print("%s: ok" % p)
    return 1 if bad else 0


def cmd_md(a):
    p = bible_path(a.bible)
    write_text(os.path.join(os.path.dirname(p), "bible.md"), render_md(load(p)))
    return 0


def word_re(term):
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(term) + r"(?![A-Za-z0-9])", re.I)


def check_prompt(b, text):
    hits, applies = [], []
    for e in b.get("entries", []):
        for w in e.get("never_say", []):
            if word_re(w).search(text):
                hits.append({"entity": e.get("id"), "word": w})
        names = [e.get("name", "")] + e.get("aliases", [])
        if any(n and word_re(n).search(text) for n in names):
            for k in e.get("checks", []):
                applies.append({"entity": e.get("id"), "code": k.get("code"), "claim": k.get("claim"), "ref": k.get("ref")})
    return {"never_say": hits, "checks": applies}


def cmd_check(a):
    with open(a.prompt, "r", encoding="utf-8") as f:
        text = f.read()
    r = check_prompt(load(a.bible), text)
    if a.json:
        print(json.dumps(r, indent=2, ensure_ascii=False))
    else:
        for h in r["never_say"]:
            print("NEVER SAY  %s: %r" % (h["entity"], h["word"]))
        for k in r["checks"]:
            print("CHECK  %s  %s (%s)" % (k["code"], k["claim"], k["ref"]))
        if not r["never_say"] and not r["checks"]:
            print("no bible entity named and no never_say word")
    return 1 if r["never_say"] else 0


def export(b, to):
    if to == "cinewright":
        chars = {}
        for e in b.get("entries", []):
            if e.get("kind") not in ("character", "creature"):
                continue
            parts = [c.get("quote") or c.get("paraphrase", "") for c in e.get("canon", [])]
            parts += [r["text"] for r in e.get("ruling", []) if r.get("text")]
            chars[e["id"]] = {"name": e.get("name"), "identity": "; ".join(p for p in parts if p),
                              "avoid": e.get("never_say", []), "source": b.get("work")}
        return {"characters": chars}
    checks = []
    for e in b.get("entries", []):
        for k in e.get("checks", []):
            checks.append({"id": "%s-%s" % (e.get("id"), k.get("code")), "question": k.get("claim"),
                           "answer": "yes", "ref": k.get("ref")})
    return {"brief_checks": checks, "source": b.get("work")}


def cmd_export(a):
    print(json.dumps(export(load(a.bible), a.to), indent=2, ensure_ascii=False))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="cw.py", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new")
    n.add_argument("work")
    n.add_argument("--dir")
    n.add_argument("--title")
    n.add_argument("--author")
    n.add_argument("--edition")
    n.add_argument("--public-domain", action="store_true")
    n.set_defaults(fn=cmd_new)
    li = sub.add_parser("lint")
    li.add_argument("bibles", nargs="*")
    li.set_defaults(fn=cmd_lint)
    m = sub.add_parser("md")
    m.add_argument("bible")
    m.set_defaults(fn=cmd_md)
    c = sub.add_parser("check")
    c.add_argument("bible")
    c.add_argument("prompt")
    c.add_argument("--json", action="store_true")
    c.set_defaults(fn=cmd_check)
    x = sub.add_parser("export")
    x.add_argument("bible")
    x.add_argument("--to", choices=["cinewright", "artwright"], required=True)
    x.set_defaults(fn=cmd_export)
    a = ap.parse_args(argv)
    try:
        return a.fn(a)
    except (OSError, ValueError) as ex:
        print("error: %s" % ex, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
