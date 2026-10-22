#!/usr/bin/env python3
"""Vault health check. Read-only. Run as `./skim lint` (or `./skim lint -v` for details).

Errors (exit 1): broken links, duplicate link names, notes outside the skeleton,
frontmatter that breaks the schema in vault/CLAUDE.md.
Warnings: path-style links, unreferenced attachments, superseded notes without
superseded-by, journal notes without a summary, areas without a hub.
"""
import argparse
import collections
import os
import posixpath
import re
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vaultlib as V  # noqa: E402

TYPES = {"hub", "procedure", "reference", "experiment", "decision", "incident", "meeting", "journal"}
STATUSES = {"planned", "active", "done", "superseded"}
ROOT_FILES = {"HOME.md", "CLAUDE.md", "TASKS.md", "TASKS-WEEK.md"}
RESOURCE_SUBS = {"literature", "vendors", "meetings", "datasheets"}
FREE_DIRS = ("_templates/", "_bases/", "_attachments/", "_meta/", "90-archive/", "00-inbox/")
JOURNAL_RE = re.compile(r"^04-journal/\d{4}-\d{2}/\d{4}-\d{2}-\d{2}\.md$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def frontmatter(text):
    s, e = V.split_frontmatter(text)
    if not e:
        return None
    body = text[s:e].split("\n", 1)[1].rsplit("---", 1)[0]
    try:
        d = yaml.safe_load(body)
    except Exception:
        return "INVALID"
    return d if isinstance(d, dict) else ({} if d is None else "INVALID")


def area_key(path):
    parts = path.split("/")
    if parts[0] in ("10-projects", "20-areas") and len(parts) >= 3:
        return parts[1]
    return None


def load_allow(root):
    p = os.path.join(root, "_meta", "lint-allow.tsv")
    allow = set()
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            if line.strip() and not line.startswith("#"):
                src, lp = (line.rstrip("\n").split("\t") + [""])[:2]
                allow.add((src, lp))
    return allow


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vault", nargs="?", default=os.path.join(os.path.dirname(__file__), "..", "..", "vault"))
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("-q", "--quiet", action="store_true", help="one summary line")
    ap.add_argument("--no-schema", action="store_true", help="skip layout + frontmatter checks")
    a = ap.parse_args()
    root = os.path.abspath(a.vault)
    files = V.list_files(root)
    idx = V.FileIndex(files)
    allow = load_allow(root)
    err = collections.defaultdict(list)
    warn = collections.defaultdict(list)
    inbound = collections.Counter()

    names = collections.defaultdict(list)
    for f in files:
        names[V.link_name(f).lower()].append(f)
    for n, fs in names.items():
        if len(fs) > 1:
            err["duplicate link name"].append(f"{n}: {fs}")

    for f in files:
        if not f.endswith(".md"):
            continue
        text = V.read(root, f)
        for lk in V.parse_links(text, f):
            if lk.kind == "wiki" and not lk.linkpath.strip():
                continue
            if lk.table_split:
                (warn["broken link in the archive (frozen)"] if f.startswith("90-archive/") else err["broken link"]
                 ).append(f"{f}: {lk.raw} (unescaped | in a table row)")
                continue
            tgt = idx.resolve(lk.linkpath, f)
            if tgt is None:
                if lk.kind == "wiki" and (f, lk.linkpath) not in allow:
                    if f.startswith("90-archive/"):
                        warn["broken link in the archive (frozen)"].append(f"{f}: {lk.raw}")
                    else:
                        err["broken link"].append(f"{f}: {lk.raw}")
                continue
            inbound[tgt] += 1
            if lk.kind == "wiki" and "/" in lk.linkpath and not f.startswith("90-archive/"):
                warn["path-style link"].append(f"{f}: {lk.raw}")

        if a.no_schema:
            continue
        top = f.split("/")[0]
        ok_place = (f in ROOT_FILES or f.startswith(FREE_DIRS) or JOURNAL_RE.match(f)
                    or f == "04-journal/_JOURNAL-INDEX.md"
                    or (top in ("10-projects", "20-areas") and area_key(f))
                    or (top == "30-resources" and f.split("/")[1] in RESOURCE_SUBS))
        if not ok_place:
            err["note outside the skeleton"].append(f)
        if f.startswith(("_templates/", "_meta/", "_bases/", "90-archive/")) or f in ROOT_FILES \
                or f == "04-journal/_JOURNAL-INDEX.md":
            continue
        fm = frontmatter(text)
        if fm is None or fm == "INVALID":
            err["frontmatter missing or invalid"].append(f)
            continue
        t, s = fm.get("type"), fm.get("status")
        if t not in TYPES:
            err["bad type"].append(f"{f}: {t!r}")
        if JOURNAL_RE.match(f):
            if not fm.get("summary"):
                warn["journal without summary"].append(f)
            continue
        if s not in STATUSES:
            err["bad status"].append(f"{f}: {s!r}")
        c = fm.get("created")
        if c is not None and not DATE_RE.match(str(c)):
            err["bad created date"].append(f"{f}: {c!r}")
        k = area_key(f)
        if k and fm.get("area") != k:
            err["area does not match folder"].append(f"{f}: area={fm.get('area')!r}")
        if s == "superseded" and not fm.get("superseded-by"):
            warn["superseded without superseded-by"].append(f)

    if not a.no_schema:
        for top in ("10-projects", "20-areas"):
            d = os.path.join(root, top)
            if os.path.isdir(d):
                for k in sorted(os.listdir(d)):
                    if os.path.isdir(os.path.join(d, k)) and not any(
                            x.startswith(f"{top}/{k}/") and posixpath.basename(x).startswith("_") and x.endswith("-hub.md")
                            for x in files):
                        warn["area without a hub"].append(f"{top}/{k}")
    for f in files:
        if f.startswith("_attachments/") and inbound[f] == 0:
            warn["unreferenced attachment"].append(f)

    ne = sum(len(v) for v in err.values())
    nw = sum(len(v) for v in warn.values())
    summary = (f"vault lint: {ne} error(s), {nw} warning(s)"
               + ("" if not ne else " — " + ", ".join(f"{k} {len(v)}" for k, v in err.items())))
    if a.quiet:
        print(summary)
        sys.exit(1 if ne else 0)
    for label, d in (("ERROR", err), ("WARN", warn)):
        for k, v in d.items():
            print(f"{label} {k}: {len(v)}")
            for x in v[: (len(v) if a.verbose else 8)]:
                print("   ", x[:300])
    print(summary)
    sys.exit(1 if ne else 0)


if __name__ == "__main__":
    main()
