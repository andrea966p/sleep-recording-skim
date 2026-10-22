#!/usr/bin/env python3
"""Rewrite vault links so they survive the move map (rehaul P3).

    relink.py VAULT --map MAP [--apply] [--report OUT.tsv]           # P3a: no meaning change
    relink.py VAULT --map MAP --repairs [--apply] [--report OUT.tsv] [--allow OUT.tsv]   # P3b

P3a: every link is resolved the way Obsidian resolves it TODAY. If its current text would
not reach the same file both in the renamed-in-place layout (P3) and in the final layout
(after the moves), it is rewritten to the shortest unique link path for the final layout.
Both resolutions are re-checked before writing. Links that are broken today, table-split
links, self links and links into code are left alone. Links whose target leaves the vault
are reported and left alone.

P3b (--repairs): links broken TODAY that have one obvious target:
  - an unescaped `|` inside a wikilink in a table row  -> `\\|` (Obsidian splits the cell);
  - a broken link whose file name matches exactly one vault file -> that file.
Each repair is reported, and --allow writes the expected link-graph changes for
compare_dumps.py.
"""
import argparse
import os
import posixpath
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import movemap  # noqa: E402
import vaultlib as V  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vault")
    ap.add_argument("--map", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--repairs", action="store_true")
    ap.add_argument("--report")
    ap.add_argument("--allow")
    a = ap.parse_args()
    root = a.vault
    rows = movemap.load(a.map)
    files = V.list_files(root)
    now = V.FileIndex(files)
    p3_files = [x for x in (movemap.renamed_in_place(rows, f) for f in files) if x]
    fin_files = [x for x in (movemap.final_path(rows, f) for f in files) if x]
    p3 = V.FileIndex(p3_files)
    fin = V.FileIndex(fin_files)
    report, allow = [], []
    changed_files = 0
    for f in files:
        if not f.lower().endswith(".md"):
            continue
        src_p3 = movemap.renamed_in_place(rows, f)
        src_fin = movemap.final_path(rows, f)
        if not src_fin:
            continue  # note leaves the vault; its links do not matter
        text = V.read(root, f)
        edits = []
        for lk in V.parse_links(text, f):
            if lk.kind == "wiki" and not lk.linkpath.strip():
                continue
            if lk.kind == "md" and not lk.linkpath.strip():
                continue
            if lk.table_split:
                if a.repairs:
                    new = lk.raw.replace("|", "\\|", 1) if lk.raw.count("|") >= 1 else lk.raw
                    # only the alias separator: the first unescaped | in the wikilink
                    inner = lk.raw[lk.raw.index("[[") + 2:-2]
                    i = inner.index("|")
                    new = lk.raw[:lk.raw.index("[[") + 2] + inner[:i] + "\\|" + inner[i + 1:] + "]]"
                    tgt = now.resolve(lk.linkpath, f)
                    if tgt and movemap.final_path(rows, tgt):
                        tf = movemap.final_path(rows, tgt)
                        lp = lk.linkpath
                        if fin.resolve(lp, src_fin) != tf or p3.resolve(lp, src_p3) != movemap.renamed_in_place(rows, tgt):
                            lp = fin.shortest(tf)
                        lk2 = V.Link(**{**lk.__dict__})
                        lk2._had_hash = lk._had_hash
                        lk2.sep = "\\|"
                        new = lk2.render(lp)
                        edits.append((lk, new))
                        report.append((f, "table-pipe", lk.raw, new))
                        allow.append((src_p3, "resolved", movemap.renamed_in_place(rows, tgt), 1))
                    else:
                        report.append((f, "table-pipe-UNRESOLVED-left", lk.raw, ""))
                continue
            tgt = now.resolve(lk.linkpath, f)
            if tgt is None:
                if a.repairs and lk.kind == "wiki":
                    name = V.link_name(lk.linkpath.rstrip("/")).lower()
                    cands = now.by_name.get(name, [])
                    if len(cands) == 1 and movemap.final_path(rows, cands[0]):
                        c = cands[0]
                        new = lk.render(fin.shortest(movemap.final_path(rows, c)))
                        edits.append((lk, new))
                        report.append((f, "broken-to-unique-name", lk.raw, new))
                        allow.append((src_p3, "resolved", movemap.renamed_in_place(rows, c), 1))
                        allow.append((src_p3, "unresolved", lk.linkpath, -1))
                continue
            if a.repairs:
                continue
            tgt_p3 = movemap.renamed_in_place(rows, tgt)
            tgt_fin = movemap.final_path(rows, tgt)
            if not tgt_fin:
                report.append((f, "TARGET-LEAVES-VAULT", lk.raw, rows[tgt].new))
                continue
            if p3.resolve(lk.linkpath, src_p3) == tgt_p3 and fin.resolve(lk.linkpath, src_fin) == tgt_fin:
                continue
            lp = fin.shortest(tgt_fin)
            if p3.resolve(lp, src_p3) != tgt_p3 or fin.resolve(lp, src_fin) != tgt_fin:
                report.append((f, "NO-SAFE-FORM", lk.raw, lp))
                continue
            new = lk.render(lp)
            edits.append((lk, new))
            report.append((f, "rewrite", lk.raw, new))
        if edits:
            changed_files += 1
            new_text = V.apply_rewrites(text, edits)
            if a.apply:
                V.write(root, f, new_text)
    kinds = {}
    for r in report:
        kinds[r[1]] = kinds.get(r[1], 0) + 1
    print(f"{'APPLIED' if a.apply else 'DRY RUN'}: {changed_files} files changed; {kinds}")
    if a.report:
        with open(a.report, "w", encoding="utf-8") as fh:
            fh.write("source\tkind\told\tnew\n")
            for r in report:
                fh.write("\t".join(str(x).replace("\t", " ") for x in r) + "\n")
    if a.allow:
        with open(a.allow, "w", encoding="utf-8") as fh:
            for s, k, t, d in allow:
                fh.write(f"{s}\t{k}\t{t}\t{d}\n")
    bad = kinds.get("NO-SAFE-FORM", 0) + kinds.get("TARGET-LEAVES-VAULT", 0)
    sys.exit(2 if bad else 0)


if __name__ == "__main__":
    main()
