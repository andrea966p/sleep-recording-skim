#!/usr/bin/env python3
"""Normalise note frontmatter to the vault schema (rehaul P5). Bodies are never touched.

    frontmatter.py VAULT --map MAP [--journal-summaries TSV] [--apply]

Sets `type`, `area`, `status` and, when the map says so, `canonical: true` and
`superseded-by`. Every other existing key is kept as written. An old status that does
not mean the same as the new one is kept as `status-note`; an old `type` that is not a
schema type is kept as `type-note`; `date` becomes `created` when there is no `created`.
Journal notes get `type: journal` and a `summary` (from their own H1 headline, else from
the summaries TSV: path<TAB>summary).
"""
import argparse
import csv
import json
import os
import re
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import movemap  # noqa: E402
import vaultlib as V  # noqa: E402

TYPES = {"hub", "procedure", "reference", "experiment", "decision", "incident", "meeting", "journal"}
SAME = {
    "done": {"done", "complete", "completed", "closed", "finished"},
    "active": {"active", "current", "live", "production", "canonical", "in-progress", "open"},
    "planned": {"planned", "draft", "todo"},
    "superseded": {"superseded", "retracted", "archived"},
}
SKIP_PREFIX = ("_templates/", "_meta/", "_bases/", "90-archive/", "_attachments/")
JOURNAL_RE = re.compile(r"^04-journal/\d{4}-\d{2}/(\d{4}-\d{2}-\d{2})\.md$")
H1_RE = re.compile(r"^#\s+(\d{4}-\d{2}-\d{2})\s*[:—–-]+\s*(.+?)\s*$", re.M)


def q(s):
    return json.dumps(str(s), ensure_ascii=False)


def top_keys_spans(lines):
    """Map top-level key -> (start, end) line indices in the YAML lines (end exclusive)."""
    spans, cur, start = {}, None, 0
    for i, ln in enumerate(lines):
        m = re.match(r"^([A-Za-z0-9_-]+)\s*:", ln)
        if m:
            if cur is not None:
                spans[cur] = (start, i)
            cur, start = m.group(1), i
    if cur is not None:
        spans[cur] = (start, len(lines))
    return spans


def build(text, sets, renames):
    s, e = V.split_frontmatter(text)
    if e:
        head = text[s:e]
        first_nl = head.index("\n") + 1
        close = head.rstrip().rfind("\n") + 1
        yml = head[first_nl:close]
        tail = head[close:]
        body = text[e:]
    else:
        yml, tail, body = "", "---\n", text
    lines = yml.splitlines(keepends=True)
    spans = top_keys_spans(lines)
    for old, new in renames.items():
        if old in spans and new not in spans:
            a, _ = spans[old]
            lines[a] = re.sub(rf"^{re.escape(old)}(\s*:)", new + r"\1", lines[a])
    spans = top_keys_spans(lines)
    drop = set()
    for k in sets:
        if k in spans:
            a, b = spans[k]
            drop.update(range(a, b))
    kept = [ln for i, ln in enumerate(lines) if i not in drop]
    new_head = "".join(f"{k}: {v}\n" for k, v in sets.items())
    if kept and not kept[-1].endswith("\n"):
        kept[-1] += "\n"
    return "---\n" + new_head + "".join(kept) + tail + body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vault")
    ap.add_argument("--map", required=True)
    ap.add_argument("--journal-summaries")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    root = a.vault
    rows = movemap.load(a.map)
    by_final = {r.new: r for r in rows.values() if r.stays_in_vault}
    jsum = {}
    if a.journal_summaries and os.path.exists(a.journal_summaries):
        for rec in csv.reader(open(a.journal_summaries, encoding="utf-8"), delimiter="\t"):
            if rec and not rec[0].startswith("#"):
                jsum[rec[0]] = rec[1]
    changed, problems, nosum = 0, [], []
    for f in V.list_files(root):
        if not f.endswith(".md") or f.startswith(SKIP_PREFIX) or "/" not in f:
            continue
        if f == "04-journal/_JOURNAL-INDEX.md":
            continue
        text = V.read(root, f)
        s, e = V.split_frontmatter(text)
        fm = {}
        if e:
            try:
                fm = yaml.safe_load(text[s:e].split("\n", 1)[1].rsplit("---", 1)[0]) or {}
            except Exception:
                problems.append(f"INVALID YAML, fix by hand first: {f}")
                continue
            if not isinstance(fm, dict):
                problems.append(f"frontmatter not a mapping: {f}")
                continue
        elif text.startswith("---"):
            problems.append(f"starts with --- but no closing fence: {f}")
            continue
        sets, renames = {}, {}
        mj = JOURNAL_RE.match(f)
        if mj:
            sets["type"] = "journal"
            if not fm.get("summary"):
                h = H1_RE.search(text[e:])
                summ = h.group(2) if h else jsum.get(f)
                if summ:
                    sets["summary"] = q(summ.strip())
                else:
                    nosum.append(f)
            if "date" not in fm and "created" not in fm:
                sets["date"] = mj.group(1)
        else:
            r = by_final.get(f)
            if r is None:
                problems.append(f"not in move map: {f}")
                continue
            parts = f.split("/")
            area = parts[1] if parts[0] in ("10-projects", "20-areas") else r.area
            old_t = fm.get("type")
            sets["type"] = r.type
            if area and area != "-":
                sets["area"] = area
            sets["status"] = r.status
            old_s = fm.get("status")
            if old_s is not None and str(old_s).strip().lower() not in SAME.get(r.status, set()) \
                    and str(old_s).strip().lower() != r.status and "status-note" not in fm:
                sets["status-note"] = q(old_s)
            if old_t is not None and str(old_t) not in TYPES and "type-note" not in fm:
                sets["type-note"] = q(old_t)
            if r.canonical.lower() == "true":
                sets["canonical"] = "true"
            if r.superseded_by not in ("-", "") and "superseded-by" not in fm:
                sets["superseded-by"] = q("[[" + V.link_name(r.superseded_by) + "]]")
            if "created" not in fm and "date" in fm:
                renames["date"] = "created"
        new = build(text, sets, renames)
        if new != text:
            changed += 1
            if a.apply:
                V.write(root, f, new)
    print(f"{'APPLIED' if a.apply else 'DRY RUN'}: {changed} notes changed")
    for p in problems:
        print("PROBLEM", p)
    if nosum:
        print(f"journal notes with no summary source: {len(nosum)}")
        for x in nosum:
            print("  NOSUM", x)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
