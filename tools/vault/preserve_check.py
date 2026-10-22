#!/usr/bin/env python3
"""Prove a migration step changed no note bodies (rehaul gates).

    preserve_check.py REPO OLD_REV NEW_REV --map MAP [--mode {body,links}]

For every note present in OLD_REV, find it in NEW_REV through the move map and compare:
  body  — text after the frontmatter must be byte-identical (frontmatter step, move step);
  links — text with every link span replaced by a placeholder must be identical, and the
          number of links equal (relink step).
Also reports word counts that differ. Exit 1 on any difference.
"""
import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import movemap  # noqa: E402
import vaultlib as V  # noqa: E402


def show(repo, rev, path):
    r = subprocess.run(["git", "-C", repo, "show", f"{rev}:vault/{path}"], capture_output=True)
    return None if r.returncode else r.stdout.decode("utf-8", "surrogateescape")


def ls(repo, rev):
    out = subprocess.run(["git", "-C", repo, "ls-tree", "-r", "--name-only", rev, "vault/"],
                         capture_output=True, text=True, check=True).stdout.split("\n")
    return [p[len("vault/"):] for p in out if p.startswith("vault/") and p.endswith(".md")]


def body(t):
    return t[V.split_frontmatter(t)[1]:]


def skeleton(t, src):
    links = V.parse_links(t, src)
    out, pos = [], 0
    for lk in links:
        out.append(t[pos:lk.start])
        out.append("\0LINK\0")
        pos = lk.end
    out.append(t[pos:])
    return "".join(out), len(links)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--map", required=True)
    ap.add_argument("--mode", choices=["body", "links"], default="body")
    ap.add_argument("--stage", choices=["same", "rename", "final"], default="final",
                    help="where OLD paths live in NEW: same | renamed in place | final")
    a = ap.parse_args()
    rows = movemap.load(a.map)
    newfiles = set(ls(a.repo, a.new))
    bad, checked, gone = [], 0, 0
    for p in ls(a.repo, a.old):
        np_ = {"same": lambda x: x, "rename": lambda x: movemap.renamed_in_place(rows, x),
               "final": lambda x: movemap.final_path(rows, x)}[a.stage](p)
        if np_ is None:
            gone += 1
            continue
        if np_ not in newfiles:
            bad.append(f"MISSING {p} -> {np_}")
            continue
        o, n = show(a.repo, a.old, p), show(a.repo, a.new, np_)
        checked += 1
        if a.mode == "body":
            if body(o) != body(n):
                bad.append(f"BODY CHANGED {p} -> {np_}")
        else:
            so, co = skeleton(o, p)
            sn, cn = skeleton(n, np_)
            if so != sn or co != cn:
                bad.append(f"TEXT OUTSIDE LINKS CHANGED {p} -> {np_} (links {co}->{cn})")
        if len(body(o).split()) != len(body(n).split()) and a.mode == "body":
            bad.append(f"WORDCOUNT {p}")
    print(f"checked {checked} notes, {gone} left the vault by design, {len(bad)} problems")
    for b in bad[:50]:
        print(" ", b)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
