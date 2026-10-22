#!/usr/bin/env python3
"""Apply the reviewed move map to the vault with git (rehaul P3 file ops and P4).

    migrate.py REPO --map MAP --stage rename [--apply]   # basename renames, DELETE, OUT
    migrate.py REPO --map MAP --stage move   [--apply]   # directory moves + .obsidian paths

`rename` keeps every file in its folder and only changes basenames, deletes, or moves code
out of the vault, so links rewritten by relink.py keep resolving. `move` then relocates
files without touching their content, so git records 100% renames. Run with Obsidian
closed: plugins rewrite their settings and react to file-create events.
"""
import argparse
import json
import os
import posixpath
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import movemap  # noqa: E402
import vaultlib as V  # noqa: E402


def git(repo, *args, check=True):
    return subprocess.run(["git", "-C", repo, *args], check=check, capture_output=True, text=True)


def tracked(repo, rel):
    return git(repo, "ls-files", "--error-unmatch", rel, check=False).returncode == 0


def mv(repo, src, dst, apply, log):
    log.append(f"mv {src} -> {dst}")
    if not apply:
        return
    os.makedirs(os.path.dirname(os.path.join(repo, dst)), exist_ok=True)
    if tracked(repo, src):
        git(repo, "mv", src, dst)
    else:
        os.rename(os.path.join(repo, src), os.path.join(repo, dst))


def rm(repo, rel, apply, log):
    log.append(f"rm {rel}")
    if not apply:
        return
    if tracked(repo, rel):
        git(repo, "rm", "-q", rel)
    else:
        os.remove(os.path.join(repo, rel))


def prune_empty_dirs(vault):
    for dp, dns, fns in os.walk(vault, topdown=False):
        if "/." in dp.replace(vault, "") or dp == vault:
            continue
        if not os.listdir(dp):
            os.rmdir(dp)


def patch_obsidian(vault, pathmap, apply, log):
    """Rewrite vault paths stored in .obsidian JSON (shortcuts, bookmarks, per-file keys)."""
    targets = ["bookmarks.json", "app.json", "plugins/notebook-navigator/data.json"]

    def fix(o):
        if isinstance(o, dict):
            return {pathmap.get(k, k): fix(v) for k, v in o.items()}
        if isinstance(o, list):
            return [fix(v) for v in o]
        if isinstance(o, str):
            return pathmap.get(o, o)
        return o

    for t in targets:
        p = os.path.join(vault, ".obsidian", t)
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding="utf-8"))
        nd = fix(d)
        if t == "app.json":
            nd["attachmentFolderPath"] = "_attachments"
        if nd != d:
            log.append(f"patch .obsidian/{t}")
            if apply:
                with open(p, "w", encoding="utf-8") as fh:
                    json.dump(nd, fh, indent=2, ensure_ascii=False)
                    fh.write("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--map", required=True)
    ap.add_argument("--stage", choices=["rename", "move"], required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    repo = os.path.abspath(a.repo)
    vault = os.path.join(repo, "vault")
    rows = movemap.load(a.map)
    files = set(V.list_files(vault))
    log = []
    for old, r in sorted(rows.items()):
        if a.stage == "rename":
            if old not in files:
                continue
            if r.delete:
                rm(repo, "vault/" + old, a.apply, log)
            elif r.out:
                mv(repo, "vault/" + old, r.out, a.apply, log)
            elif r.renamed:
                mv(repo, "vault/" + old, "vault/" + movemap.renamed_in_place(rows, old), a.apply, log)
        else:
            if not r.stays_in_vault:
                continue
            cur = movemap.renamed_in_place(rows, old)
            if r.new in files:
                continue  # already in place
            src = cur if cur in files else (old if not a.apply and old in files else None)
            if src is None:
                log.append(f"MISSING {cur}")
                continue
            mv(repo, "vault/" + src, "vault/" + r.new, a.apply, log)
    if a.stage == "move":
        pathmap = {movemap.renamed_in_place(rows, o): r.new for o, r in rows.items() if r.stays_in_vault}
        pathmap.update({o: r.new for o, r in rows.items() if r.stays_in_vault})
        patch_obsidian(vault, pathmap, a.apply, log)
        if a.apply:
            prune_empty_dirs(vault)
    for line in log:
        print(line)
    kinds = {}
    for line in log:
        kinds[line.split()[0]] = kinds.get(line.split()[0], 0) + 1
    print(("APPLIED " if a.apply else "DRY RUN ") + str(kinds))
    sys.exit(1 if kinds.get("MISSING") else 0)


if __name__ == "__main__":
    main()
