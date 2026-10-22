#!/usr/bin/env python3
"""Repoint broken links (e.g. to Claude memory slugs) at the vault notes that now hold
their content, keeping what the reader sees.

    retarget.py VAULT MAP.tsv [--apply]

MAP.tsv: old link name <TAB> vault note name (or `TEXT` to turn the link into plain
`code` text, for links to agent rules that have no vault page). Only links that are
broken today and whose last path component equals the old name are touched. A link
without an alias gets the old visible text as alias, so the page reads the same.
"""
import argparse
import os
import posixpath
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vaultlib as V  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vault")
    ap.add_argument("map")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    m = {}
    for line in open(a.map, encoding="utf-8"):
        if line.strip() and not line.startswith("#"):
            k, v = line.rstrip("\n").split("\t")[:2]
            m[k.strip().lower()] = v.strip()
    files = V.list_files(a.vault)
    idx = V.FileIndex(files)
    for k, v in m.items():
        if v != "TEXT" and len(idx.by_name.get(v.lower(), [])) != 1:
            sys.exit(f"target note not found or ambiguous: {v}")
    changed, n = 0, 0
    for f in files:
        if not f.endswith(".md") or f.startswith("90-archive/"):
            continue  # the archive is frozen, verbatim
        t = V.read(a.vault, f)
        edits = []
        for lk in V.parse_links(t, f):
            if lk.kind != "wiki" or lk.table_split or not lk.linkpath.strip():
                continue
            if idx.resolve(lk.linkpath, f) is not None:
                continue
            key = posixpath.basename(lk.linkpath.rstrip("\\").strip()).lower()
            if key.endswith(".md"):
                key = key[:-3]
            if key not in m:
                continue
            if m[key] == "TEXT":
                shown = lk.alias if lk.alias is not None else lk.linkpath
                new = f"`{shown}` (Claude memory rule)"
            else:
                if lk.alias is None:
                    lk.alias = lk.linkpath
                    line_start = t.rfind("\n", 0, lk.start) + 1
                    if line_start in V.table_lines(t, V.split_frontmatter(t)[1]):
                        lk.sep = "\\|"  # a bare | would split the table cell
                new = lk.render(m[key])
            edits.append((lk, new))
            n += 1
            print(f"{f}: {lk.raw} -> {new}")
        if edits:
            changed += 1
            if a.apply:
                V.write(a.vault, f, V.apply_rewrites(t, edits))
    print(f"{'APPLIED' if a.apply else 'DRY RUN'}: {n} links in {changed} files")


if __name__ == "__main__":
    main()
