#!/usr/bin/env python3
"""canonwright: canon bibles for adapting a book with AI image and video models.

Commands (stdlib only, deterministic):
  new <work> [--dir D] [--title T] [--author A] [--edition E] [--public-domain]
  lint [bible ...] [--json]   check bibles (default: examples/ and $CANONWRIGHT_HOME/bibles);
                              --json prints [] when clean, else file, line, code, hint per issue
  stamp <bible>               record the canon hash (the explicit re-stamp after canon changes)
  verify <bible> [out.json ...] [--json]  report a stale bible or outputs built from older canon
  md <bible>                  regenerate bible.md from bible.json
  check <bible> <prompt.txt>  flag never_say words, list checks for entities named
  export <bible> --to cinewright|artwright [--out FILE]

A <bible> is a folder holding bible.json, or the bible.json path itself.
Exit codes: 0 ok, 1 findings, 2 usage or file error.
"""
import argparse
import hashlib
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
    b["canon_hash"] = canon_hash(b)
    write_text(bible_path(d), json.dumps(b, indent=2, ensure_ascii=False) + "\n")
    write_text(os.path.join(d, "bible.md"), render_md(b))
    print(d)
    return 0


HINTS = {
    "duplicate-id": "give each entry its own id",
    "bad-kind": "set kind to one of: " + ", ".join(sorted(KINDS)),
    "no-canon": "add at least one canon line with a quote and its chapter ref",
    "no-ref": "add the chapter ref the quote comes from",
    "quote-too-long": "cut the quote to %d words or fewer, or paraphrase the rest" % MAX_QUOTE_WORDS,
    "paraphrase-verified": "mark the paraphrase verified false, or replace it with a quote",
    "unverified-paraphrase": "quote the passage once the book text is on disk",
    "no-quote": "add a quote (or a paraphrase marked verified false)",
    "ruling-incomplete": "a ruling needs text and why",
    "miss-incomplete": "a model miss needs miss and fix",
    "check-incomplete": "a check needs code, claim and ref",
    "duplicate-check-code": "give each check of an entry its own code",
    "correction-incomplete": "a correction needs id and text",
    "stale-hash": "canon changed since the last stamp: review outputs built from it, then run cw.py stamp",
    "unstamped": "run cw.py stamp to record the canon hash",
    "cannot-read": "fix the JSON syntax or the path",
}


def lint_issues(b):
    """Return issue dicts: entity, code, message, hint, severity (error or warning)."""
    out = []

    def add(eid, code, msg, sev="error"):
        out.append({"entity": eid, "code": code, "message": msg, "hint": HINTS[code], "severity": sev})

    pd = bool(b.get("public_domain"))
    ids = set()
    for e in b.get("entries", []):
        eid = e.get("id") or "?"
        if eid in ids:
            add(eid, "duplicate-id", "%s: duplicate id" % eid)
        ids.add(eid)
        if e.get("kind") not in KINDS:
            add(eid, "bad-kind", "%s: kind must be one of %s" % (eid, ", ".join(sorted(KINDS))))
        if not e.get("canon"):
            add(eid, "no-canon", "%s: no canon lines" % eid)
        for i, c in enumerate(e.get("canon", [])):
            where = "%s canon[%d]" % (eid, i)
            if not c.get("ref"):
                add(eid, "no-ref", "%s: no chapter ref" % where)
            if c.get("quote"):
                n = len(c["quote"].split())
                if not pd and n > MAX_QUOTE_WORDS:
                    add(eid, "quote-too-long", "%s: quote of %d words from a work under copyright (max %d)"
                        % (where, n, MAX_QUOTE_WORDS))
            elif c.get("paraphrase"):
                if c.get("verified", True):
                    add(eid, "paraphrase-verified", "%s: paraphrase without a quote must be marked verified false" % where)
                else:
                    add(eid, "unverified-paraphrase",
                        "%s: unverified paraphrase; quote it when the book text is on disk" % where, "warning")
            else:
                add(eid, "no-quote", "%s: no quote" % where)
        for i, r in enumerate(e.get("ruling", [])):
            if not r.get("text") or not r.get("why"):
                add(eid, "ruling-incomplete", "%s ruling[%d]: needs text and why" % (eid, i))
        for i, m in enumerate(e.get("misses", [])):
            if not m.get("miss") or not m.get("fix"):
                add(eid, "miss-incomplete", "%s misses[%d]: needs miss and fix" % (eid, i))
        codes = set()
        for i, k in enumerate(e.get("checks", [])):
            if not isinstance(k, dict) or not k.get("code") or not k.get("claim") or not k.get("ref"):
                add(eid, "check-incomplete", "%s checks[%d]: needs code, claim and ref" % (eid, i))
            elif k["code"] in codes:
                add(eid, "duplicate-check-code", "%s checks[%d]: duplicate code %s" % (eid, i, k["code"]))
            else:
                codes.add(k["code"])
        for i, c in enumerate(e.get("corrections", [])):
            if not c.get("id") or not c.get("text"):
                add(eid, "correction-incomplete", "%s corrections[%d]: needs id and text" % (eid, i))
    stamp = b.get("canon_hash")
    if not stamp:
        add(None, "unstamped", "no canon_hash recorded", "warning")
    elif stamp != canon_hash(b):
        add(None, "stale-hash", "canon_hash %s does not match the canon (%s)" % (stamp, canon_hash(b)))
    return out


def lint_bible(b):
    """Return (errors, warnings) as lists of strings."""
    issues = lint_issues(b)
    return ([i["message"] for i in issues if i["severity"] == "error"],
            [i["message"] for i in issues if i["severity"] == "warning"])


def canon_hash(b):
    """sha256 over the bible's canon (everything but the stamp), independent of JSON formatting."""
    body = {k: v for k, v in b.items() if k != "canon_hash"}
    raw = json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def stale(b):
    """True when the bible records a stamp that no longer matches its canon."""
    return bool(b.get("canon_hash")) and b["canon_hash"] != canon_hash(b)


def find_line(path, eid):
    """1-based line of the entry's id in bible.json (1 when not found)."""
    if not eid:
        return 1
    pat = re.compile(r'"id"\s*:\s*' + re.escape(json.dumps(eid)))
    try:
        with open(path, "r", encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                if pat.search(line):
                    return n
    except OSError:
        pass
    return 1


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
    report = []
    for p in paths:
        bp = bible_path(p)
        try:
            issues = lint_issues(load(p))
        except (OSError, ValueError) as ex:
            issues = [{"entity": None, "code": "cannot-read", "message": "cannot read: %s" % ex,
                       "hint": HINTS["cannot-read"], "severity": "error"}]
        for i in issues:
            if a.json:
                report.append({"file": bp, "line": find_line(bp, i["entity"]), "code": i["code"],
                               "severity": i["severity"], "message": i["message"], "hint": i["hint"]})
            elif i["severity"] == "warning":
                print("%s: warning: %s" % (p, i["message"]))
            else:
                print("%s: %s" % (p, i["message"]))
        errs = [i for i in issues if i["severity"] == "error"]
        bad += len(errs)
        if not errs and not a.json:
            print("%s: ok" % p)
    if a.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if bad else 0


def cmd_stamp(a):
    """Record the canon hash in bible.json, keeping the file's own formatting."""
    p = bible_path(a.bible)
    with open(p, "r", encoding="utf-8") as f:
        text = f.read()
    h = canon_hash(json.loads(text))
    line = '"canon_hash": "%s"' % h
    if re.search(r'"canon_hash"\s*:\s*"[^"]*"', text):
        text = re.sub(r'"canon_hash"\s*:\s*"[^"]*"', line, text, count=1)
    else:
        text = re.sub(r"^\{\s*\n", "{\n  %s,\n" % line, text, count=1)
    if json.loads(text).get("canon_hash") != h:
        raise ValueError("could not stamp %s" % p)
    write_text(p, text)
    print("%s %s" % (h, p))
    return 0


def cmd_verify(a):
    """Report a stale bible and outputs built from an older canon than the bible's current one."""
    b = load(a.bible)
    now = canon_hash(b)
    report = []
    if stale(b):
        report.append({"file": bible_path(a.bible), "code": "stale-hash", "hint": HINTS["stale-hash"]})
    for o in a.outputs:
        with open(o, "r", encoding="utf-8") as f:
            got = json.load(f).get("canon_hash")
        if got != now:
            report.append({"file": o, "code": "stale-output", "built_from": got, "canon": now,
                           "hint": "rebuild this output from the current bible (cw.py export)"})
    if a.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        for r in report:
            print("STALE  %s (%s): %s" % (r["file"], r["code"], r["hint"]))
        if not report:
            print("current: %s" % now)
    return 1 if report else 0


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
        return {"characters": chars, "canon_hash": canon_hash(b)}
    checks = []
    for e in b.get("entries", []):
        for k in e.get("checks", []):
            checks.append({"id": "%s-%s" % (e.get("id"), k.get("code")), "question": k.get("claim"),
                           "answer": "yes", "ref": k.get("ref")})
    return {"brief_checks": checks, "source": b.get("work"), "canon_hash": canon_hash(b)}


def cmd_export(a):
    b = load(a.bible)
    if stale(b):
        print("stale: canon changed since the last stamp; review it, then run cw.py stamp", file=sys.stderr)
        return 1
    text = json.dumps(export(b, a.to), indent=2, ensure_ascii=False)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, "w", encoding="utf-8", newline="\n") as f:
            f.write(text + "\n")
        print("wrote %s" % a.out)
    else:
        print(text)
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
    li.add_argument("--json", action="store_true", help="print issues as JSON; [] when clean")
    li.set_defaults(fn=cmd_lint)
    m = sub.add_parser("md")
    m.add_argument("bible")
    m.set_defaults(fn=cmd_md)
    c = sub.add_parser("check")
    c.add_argument("bible")
    c.add_argument("prompt")
    c.add_argument("--json", action="store_true")
    c.set_defaults(fn=cmd_check)
    st = sub.add_parser("stamp")
    st.add_argument("bible")
    st.set_defaults(fn=cmd_stamp)
    v = sub.add_parser("verify")
    v.add_argument("bible")
    v.add_argument("outputs", nargs="*")
    v.add_argument("--json", action="store_true")
    v.set_defaults(fn=cmd_verify)
    x = sub.add_parser("export")
    x.add_argument("bible")
    x.add_argument("--to", choices=["cinewright", "artwright"], required=True)
    x.add_argument("--out", help="write the JSON to this file instead of stdout")
    x.set_defaults(fn=cmd_export)
    a = ap.parse_args(argv)
    try:
        return a.fn(a)
    except (OSError, ValueError) as ex:
        print("error: %s" % ex, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
