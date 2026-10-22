#!/usr/bin/env python3
"""Compare two Obsidian link-graph dumps across a migration step.

    compare_dumps.py BEFORE.json AFTER.json --map vault/_meta/move-map.tsv --stage {rename,final}
                     [--allow allowed-changes.tsv]

Every path in BEFORE is first mapped to where it should be in AFTER (`rename`: P3 state,
basename changes only; `final`: after the moves). Then, per source note, the resolved
targets with counts and the unresolved link texts must be identical. Allowed changes
(source<TAB>kind<TAB>target<TAB>delta, kind = resolved|unresolved) are subtracted first.
"""
import argparse
import collections
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import movemap  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("--map", required=True)
    ap.add_argument("--stage", choices=["rename", "final"], required=True)
    ap.add_argument("--allow")
    ap.add_argument("--show", type=int, default=40)
    a = ap.parse_args()
    rows = movemap.load(a.map)
    f = movemap.renamed_in_place if a.stage == "rename" else movemap.final_path
    B, A = json.load(open(a.before)), json.load(open(a.after))

    def mp(p):
        return f(rows, p)

    exp_files = sorted(x for x in (mp(p) for p in B["files"]) if x)
    problems = []
    if exp_files != sorted(A["files"]):
        problems.append("FILES missing " + str(sorted(set(exp_files) - set(A["files"]))[:10])
                        + " unexpected " + str(sorted(set(A["files"]) - set(exp_files))[:10]))
    exp_r = collections.defaultdict(collections.Counter)
    exp_u = collections.defaultdict(collections.Counter)
    for s, tg in B["resolved"].items():
        ms = mp(s)
        if not ms:
            continue
        for t, n in tg.items():
            mt = mp(t)
            if mt:
                exp_r[ms][mt] += n
            else:
                exp_u[ms]["<left vault> " + t] += n
    for s, tg in B["unresolved"].items():
        ms = mp(s)
        if ms:
            for t, n in tg.items():
                exp_u[ms][t] += n
    if a.allow:
        with open(a.allow) as fh:
            for rec in csv.reader(fh, delimiter="\t"):
                if not rec or rec[0].startswith("#"):
                    continue
                s, kind, t, d = rec[0], rec[1], rec[2], int(rec[3])
                (exp_r if kind == "resolved" else exp_u)[s][t] += d
    for s in sorted(set(exp_r) | set(A["resolved"]) | set(exp_u) | set(A["unresolved"])):
        er = +exp_r.get(s, collections.Counter())
        ar = +collections.Counter(A["resolved"].get(s, {}))
        if er != ar:
            problems.append(f"RESOLVED {s}: missing {dict(er - ar)} extra {dict(ar - er)}")
        eu = +exp_u.get(s, collections.Counter())
        au = +collections.Counter(A["unresolved"].get(s, {}))
        if eu != au:
            problems.append(f"UNRESOLVED {s}: missing {dict(eu - au)} extra {dict(au - eu)}")
    print(f"{len(problems)} differences")
    for p in problems[:a.show]:
        print(" ", p[:500])
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
