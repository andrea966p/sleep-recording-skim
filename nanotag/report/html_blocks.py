#!/usr/bin/env python3
"""Flatten one of the analysis HTML pages (report.html, methods.html) into a
list of blocks that build_docx.js / build_pptx.js lay out, so the Word and
PowerPoint versions are rebuilt from the HTML and never drift from it.

    python3 html_blocks.py report.html > report.json

Block types: h1 h2 h3 p (style: lede | eyebrow | note | callout) li ref kv
table (rows of cells, head flag, colspan) img caption. Text is a list of runs
{text, b, i, code, color}. Scripts and styles are dropped; an inline <svg> is
replaced by an img block for 'bout_diagram.png' (the only svg in these pages).
ponytail: handles the tags these two pages use, not general HTML.
"""
import json, re, sys
from html.parser import HTMLParser

COLORS = {"sod1": "C2410C", "water": "1D4ED8"}
BLOCK_P = {"lede": "lede", "eyebrow": "eyebrow", "caption-note": "note"}

class Flatten(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks, self.runs, self.fmt = [], None, []
        self.skip = 0           # inside script/style/svg
        self.kind = None        # current text block type
        self.style = None
        self.table = None       # rows while inside a table
        self.cell = None
        self.step = None        # methods: number of the step whose h3 comes next
        self.in_n = False
        self.divs = []          # class of every open div
        self.refs = False       # inside <ol class="refs">
        self.ol = 0
        self.title, self.in_title = "", False

    @property
    def callout(self):
        return any("callout" in c.split() for c in self.divs)

    # --- helpers
    def start_block(self, kind, style=None):
        self.flush()
        self.kind, self.style, self.runs = kind, style, []

    def flush(self):
        if self.runs is None or self.kind is None:
            return
        runs = [r for r in self.runs if r["text"]]
        if runs:
            runs[0]["text"] = runs[0]["text"].lstrip()
            runs[-1]["text"] = runs[-1]["text"].rstrip()
        if any(r["text"].strip() for r in runs):
            b = {"t": self.kind, "runs": runs}
            if self.style:
                b["style"] = self.style
            if self.kind == "ref":
                b["n"] = self.ol
            self.blocks.append(b)
        self.kind, self.style, self.runs = None, None, None

    def cur_fmt(self):
        f = {}
        for x in self.fmt:
            f.update(x)
        return f

    # --- parser callbacks
    def handle_starttag(self, tag, a):
        a = dict(a)
        cls = a.get("class", "") or ""
        if tag == "title":
            self.flush(); self.skip += 1; self.in_title = True; return
        if tag in ("script", "style", "svg") or self.skip:
            if tag == "svg" and not self.skip:
                self.flush()
                self.blocks.append({"t": "img", "src": "bout_diagram.png", "alt": "bout diagram"})
            if tag in ("script", "style", "svg"):
                self.skip += 1
            return
        if tag == "table":
            self.flush(); self.table = []
        elif tag == "tr" and self.table is not None:
            self.table.append({"head": False, "cells": []})
        elif tag in ("td", "th") and self.table is not None:
            self.cell = {"runs": [], "colspan": int(a.get("colspan", 1)), "head": tag == "th"}
            self.runs = self.cell["runs"]
            if tag == "th":
                self.table[-1]["head"] = True
        elif tag in ("h1", "h2", "h3"):
            self.start_block(tag)
            if tag == "h3" and self.step:
                self.runs.append({"text": f"{self.step}. "}); self.step = None
        elif tag == "p" and self.table is None:
            self.start_block("p", "callout" if self.callout else next(
                (v for k, v in BLOCK_P.items() if k in cls.split()), None))
        elif tag == "div":
            self.divs.append(cls)
            if "eyebrow" in cls.split():
                self.start_block("p", "eyebrow")
            elif cls == "n":
                self.in_n = True; self.step = ""
        elif tag == "ol":
            self.ol, self.refs = 0, "refs" in cls.split()
        elif tag == "li":
            self.ol += 1
            self.start_block("ref" if self.refs else "li", "callout" if self.callout else None)
        elif tag == "dt":
            self.start_block("kv"); self.fmt.append({"b": True})
        elif tag == "dd":
            self.fmt.append({})          # value continues the kv block opened by dt
        elif tag == "img":
            self.flush()
            self.blocks.append({"t": "img", "src": a.get("src"), "alt": a.get("alt", "")})
        elif tag == "figcaption":
            self.start_block("caption")
        elif tag == "br" and self.runs is not None:
            self.runs.append({"text": " "})
        elif tag in ("b", "strong"):
            self.fmt.append({"b": True})
        elif tag in ("i", "em"):
            self.fmt.append({"i": True})
        elif tag == "code":
            self.fmt.append({"code": True})
        elif tag == "span":
            col = next((COLORS[c] for c in cls.split() if c in COLORS), None)
            self.fmt.append({"color": col, "b": True} if col else {})

    def handle_endtag(self, tag):
        if self.skip:
            if tag in ("script", "style", "svg", "title"):
                self.skip -= 1
                self.in_title = False
            return
        if tag in ("b", "strong", "i", "em", "code", "span", "dd") and self.fmt:
            self.fmt.pop()
        elif tag == "dt":
            self.fmt.pop(); self.runs.append({"text": ": "})
        elif tag in ("td", "th") and self.cell is not None:
            self.table[-1]["cells"].append(self.cell); self.cell = None; self.runs = None
        elif tag == "table" and self.table is not None:
            self.blocks.append({"t": "table", "rows": [r for r in self.table if r["cells"]]})
            self.table = None
        elif tag in ("h1", "h2", "h3", "p", "li", "figcaption", "dd"):
            self.flush()
        elif tag == "div":
            if self.divs and "eyebrow" in self.divs[-1].split():
                self.flush()
            self.in_n = False
            if self.divs:
                self.divs.pop()
        elif tag == "ol":
            self.refs = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.skip:
            return
        if self.in_n:
            self.step += data.strip(); return
        text = re.sub(r"\s+", " ", data)
        if self.runs is None:
            if not text.strip():
                return
            self.start_block("p")       # loose text, e.g. the footer
        self.runs.append({"text": text, **{k: v for k, v in self.cur_fmt().items() if v}})

def parse(path):
    f = Flatten()
    f.feed(open(path, encoding="utf-8").read())
    f.flush()
    return [{"t": "title", "text": f.title.strip()}] + f.blocks

if __name__ == "__main__":
    json.dump(parse(sys.argv[1]), sys.stdout, ensure_ascii=False, indent=1)
