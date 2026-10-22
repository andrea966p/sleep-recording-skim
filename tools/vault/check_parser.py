#!/usr/bin/env python3
"""Compare vaultlib's link graph against Obsidian's own (obsidian_dump.sh output).

    python3 tools/vault/check_parser.py VAULT_DIR DUMP.json [--show N]

Exit 0 only when every source file has the same resolved targets (with counts) and
the same unresolved link paths as Obsidian. This is the gate before any rewrite.
"""
import argparse
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vaultlib as V  # noqa: E402


def our_graph(root):
    files = V.list_files(root)
    idx = V.FileIndex(files)
    res = collections.defaultdict(collections.Counter)
    unres = collections.defaultdict(collections.Counter)
    for f in files:
        if not f.lower().endswith(".md"):
            continue
        for lk in V.parse_links(V.read(root, f), f):
            if lk.table_split:
                continue
            tgt = idx.resolve(lk.linkpath, f)
            if tgt:
                res[f][tgt] += 1
            elif lk.kind == "wiki":
                unres[f][lk.linkpath] += 1
    return files, res, unres


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vault")
    ap.add_argument("dump")
    ap.add_argument("--show", type=int, default=40)
    a = ap.parse_args()
    d = json.load(open(a.dump))
    files, res, unres = our_graph(a.vault)
    problems = []
    if sorted(files) != sorted(d["files"]):
        only_us = sorted(set(files) - set(d["files"]))
        only_ob = sorted(set(d["files"]) - set(files))
        problems.append(f"file list differs: only ours {only_us[:5]} only obsidian {only_ob[:5]}")
    srcs = set(res) | set(d["resolved"]) | set(unres) | set(d["unresolved"])
    nres = nunres = 0
    for s in sorted(srcs):
        ob_r = collections.Counter(d["resolved"].get(s, {}))
        ob_u = collections.Counter(d["unresolved"].get(s, {}))
        if res.get(s, collections.Counter()) != ob_r:
            nres += 1
            a_ = res.get(s, collections.Counter())
            problems.append(f"RESOLVED {s}: ours-only {dict(a_ - ob_r)} obsidian-only {dict(ob_r - a_)}")
        if unres.get(s, collections.Counter()) != ob_u:
            nunres += 1
            a_ = unres.get(s, collections.Counter())
            problems.append(f"UNRESOLVED {s}: ours-only {dict(a_ - ob_u)} obsidian-only {dict(ob_u - a_)}")
    tot_r = sum(sum(c.values()) for c in res.values())
    tot_u = sum(sum(c.values()) for c in unres.values())
    print(f"ours: {tot_r} resolved, {tot_u} unresolved | obsidian: "
          f"{sum(sum(v.values()) for v in d['resolved'].values())} resolved, "
          f"{sum(sum(v.values()) for v in d['unresolved'].values())} unresolved")
    print(f"sources disagreeing: resolved {nres}, unresolved {nunres}")
    for p in problems[:a.show]:
        print(" ", p[:400])
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
