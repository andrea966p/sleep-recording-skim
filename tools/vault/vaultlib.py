"""Shared vault model: file listing, link parsing and link resolution that match Obsidian.

Obsidian is the referee: `obsidian_dump.sh` writes Obsidian's own resolvedLinks /
unresolvedLinks, and `check_parser.py` requires this module to agree with it before
any script here is allowed to rewrite a link.

Parsing rules (what Obsidian does, verified against the dump):
- links inside fenced / indented code blocks and inline code spans are not links;
- frontmatter values may hold wikilinks ("[[note]]"), which Obsidian tracks;
- `[[target#heading|alias]]`, `![[embed]]`, and `\\|` as the alias separator in tables;
- `./` and `../` link paths resolve relative to the source note, with no fallback;
- otherwise: exact vault path, then any file whose path ends with the link path.
"""
from __future__ import annotations

import os
import re
import posixpath
from dataclasses import dataclass, field
from urllib.parse import unquote

from markdown_it import MarkdownIt

HIDDEN_DIRS = {".obsidian", ".git", ".trash", ".claude"}

_md = MarkdownIt("commonmark").enable("table")
WIKI_RE = re.compile(r"(!?)\[\[([^\[\]\n]+?)\]\]")
# [text](target "title") — local targets only; external schemes are filtered later
MDLINK_RE = re.compile(r"(!?)\[((?:[^\[\]\n]|\[[^\[\]\n]*\])*)\]\((<[^>\n]+>|[^)\s\n]+)(\s+\"[^\"\n]*\")?\)")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


# --------------------------------------------------------------------------- files

def list_files(root: str) -> list[str]:
    """All vault files Obsidian indexes, as vault-relative posix paths."""
    out = []
    for dp, dns, fns in os.walk(root):
        dns[:] = sorted(d for d in dns if not d.startswith("."))
        for fn in sorted(fns):
            if fn.startswith("."):
                continue
            out.append(posixpath.relpath(os.path.join(dp, fn), root).replace(os.sep, "/"))
    return out


def link_name(path: str) -> str:
    """The lookup key Obsidian uses for a file: md files without extension."""
    base = posixpath.basename(path)
    return base[:-3] if base.lower().endswith(".md") else base


class FileIndex:
    def __init__(self, files: list[str]):
        self.files = list(files)
        self.by_lower = {f.lower(): f for f in files}
        self.by_name: dict[str, list[str]] = {}
        for f in files:
            self.by_name.setdefault(link_name(f).lower(), []).append(f)

    def exact(self, path: str) -> str | None:
        p = path.lower()
        if p in self.by_lower:
            return self.by_lower[p]
        if not posixpath.splitext(p)[1] or not self._has_known_ext(p):
            return self.by_lower.get(p + ".md")
        return None

    @staticmethod
    def _has_known_ext(p: str) -> bool:
        ext = posixpath.splitext(p)[1]
        return bool(ext) and len(ext) <= 6 and ext[1:].isalnum()

    def resolve(self, linkpath: str, src: str) -> str | None:
        lp = linkpath.strip()
        if not lp:
            return src
        if lp.startswith("/"):
            lp = lp.lstrip("/")
        if lp.startswith("./") or lp.startswith("../"):
            joined = posixpath.normpath(posixpath.join(posixpath.dirname(src), lp))
            if joined.startswith(".."):
                return None
            return self.exact(joined)
        hit = self.exact(lp)
        if hit:
            return hit
        name = link_name(lp).lower()
        if not lp.lower().endswith(".md") and self._has_known_ext(lp.lower()):
            name = posixpath.basename(lp).lower()
        cands = self.by_name.get(name, [])
        want = lp.lower()
        if not want.endswith(".md") and (not self._has_known_ext(want)):
            want_md = want + ".md"
        else:
            want_md = want
        cands = [c for c in cands if c.lower() == want_md or c.lower().endswith("/" + want_md)]
        if not cands:
            return None
        if len(cands) == 1:
            return cands[0]
        srcdir = posixpath.dirname(src)
        same = [c for c in cands if posixpath.dirname(c) == srcdir]
        if same:
            return same[0]
        return sorted(cands, key=lambda c: (c.count("/"), c))[0]

    def shortest(self, target: str) -> str:
        """Shortest link path that uniquely names `target` among the indexed files."""
        name = link_name(target)
        if len(self.by_name.get(name.lower(), [])) == 1:
            return name
        parts = target[:-3].split("/") if target.lower().endswith(".md") else target.split("/")
        for k in range(2, len(parts) + 1):
            cand = "/".join(parts[-k:])
            hits = [f for f in self.by_name.get(name.lower(), [])
                    if (f[:-3] if f.lower().endswith(".md") else f).lower().endswith(cand.lower())]
            if len(hits) == 1:
                return cand
        return "/".join(parts)


# --------------------------------------------------------------------------- parsing

@dataclass
class Link:
    src: str
    start: int            # offset of the whole link in the file text
    end: int
    kind: str             # "wiki" or "md"
    embed: bool
    linkpath: str         # target path text, unescaped, no fragment
    fragment: str         # text after '#', without the '#'
    alias: str | None
    sep: str = "|"        # "|" or "\\|" (escaped in a table)
    in_frontmatter: bool = False
    table_split: bool = False   # unescaped | inside a table cell: Obsidian sees no link
    raw: str = ""
    md_title: str = ""

    def render(self, linkpath: str) -> str:
        frag = ("#" + self.fragment) if self.fragment or self._had_hash else ""
        if self.kind == "wiki":
            inner = linkpath + frag
            if self.alias is not None:
                inner += self.sep + self.alias
            return ("!" if self.embed else "") + "[[" + inner + "]]"
        target = linkpath.replace(" ", "%20") + frag
        return ("!" if self.embed else "") + "[" + (self.alias or "") + "](" + target + self.md_title + ")"

    _had_hash: bool = False


def split_frontmatter(text: str) -> tuple[int, int]:
    """(start, end) character span of the YAML frontmatter including fences, or (0, 0)."""
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return (0, 0)
    m = re.search(r"\n---[ \t]*(\r?\n|$)", text[3:])
    if not m:
        return (0, 0)
    return (0, 3 + m.end())


def _code_mask(text: str, body_start: int) -> list[bool]:
    """Per-character True where text is code (fences, indented blocks, inline spans)."""
    mask = [False] * len(text)
    body = text[body_start:]
    lines = body.split("\n")
    line_off = [0]
    for ln in lines:
        line_off.append(line_off[-1] + len(ln) + 1)

    def mark_lines(a: int, b: int) -> None:
        s = body_start + line_off[a]
        e = body_start + min(line_off[b], len(body))
        for i in range(s, min(e, len(text))):
            mask[i] = True

    tokens = _md.parse(body)
    for t in tokens:
        if t.type in ("fence", "code_block") and t.map:
            mark_lines(t.map[0], t.map[1])
    # inline code spans: a span never crosses a blank line (also inside callouts)
    n = len(text)
    pos = body_start
    while pos < n:
        if mask[pos]:
            pos += 1
            continue
        if text[pos] == "`":
            run_end = pos
            while run_end < n and text[run_end] == "`":
                run_end += 1
            run = run_end - pos
            # find closing run of exactly the same length, not crossing a blank line
            j = run_end
            close = -1
            while j < n:
                if text[j] == "\n" and _blank_follows(text, j):
                    break
                if mask[j]:
                    break
                if text[j] == "`":
                    k = j
                    while k < n and text[k] == "`":
                        k += 1
                    if k - j == run:
                        close = j
                        break
                    j = k
                    continue
                j += 1
            if close >= 0:
                for q in range(pos, close + run):
                    mask[q] = True
                pos = close + run
                continue
            pos = run_end
            continue
        pos += 1
    return mask


def _blank_follows(text: str, j: int) -> bool:
    """True if the line after the newline at j is blank (or only '>' quote markers)."""
    e = text.find("\n", j + 1)
    line = text[j + 1:] if e < 0 else text[j + 1:e]
    return line.replace(">", "").strip() == ""


def table_lines(text: str, body_start: int) -> set[int]:
    """Character offsets of line starts that belong to markdown tables (header, rows)."""
    body = text[body_start:]
    offs = [0]
    for ln in body.split("\n"):
        offs.append(offs[-1] + len(ln) + 1)
    starts = set()
    for tok in _md.parse(body):
        if tok.type == "table_open" and tok.map:
            for i in range(tok.map[0], tok.map[1]):
                starts.add(body_start + offs[i])
    return starts


def _parse_wiki_inner(inner: str) -> tuple[str, str, str | None, str, bool]:
    sep = "|"
    alias = None
    m = re.search(r"\\\||\|", inner)
    if m:
        sep = m.group(0)
        target, alias = inner[:m.start()], inner[m.end():]
    else:
        target = inner
    had_hash = "#" in target
    if had_hash:
        linkpath, frag = target.split("#", 1)
    else:
        linkpath, frag = target, ""
    return linkpath, frag, alias, sep, had_hash


def frontmatter_valid(text: str) -> bool:
    import yaml
    s, e = split_frontmatter(text)
    if not e:
        return False
    body = text[s:e].split("\n", 1)[1].rsplit("---", 1)[0]
    try:
        data = yaml.safe_load(body)
    except Exception:
        return False
    return data is None or isinstance(data, dict)


def _fm_link_ok(text: str, start: int, end: int) -> bool:
    """Obsidian only links a frontmatter value that is a quoted string holding the link."""
    ls = text.rfind("\n", 0, start) + 1
    le = text.find("\n", end)
    line = text[ls:le if le >= 0 else len(text)]
    return bool(re.search(r"""(["'])\s*!?\[\[[^\]]+\]\]\s*\1""", line))


def parse_links(text: str, src: str) -> list[Link]:
    fm_s, fm_e = split_frontmatter(text)
    fm_ok = frontmatter_valid(text) if fm_e else False
    mask = _code_mask(text, fm_e)
    tables = table_lines(text, fm_e)
    links: list[Link] = []
    for m in WIKI_RE.finditer(text):
        if mask[m.start()]:
            continue
        in_fm = fm_s <= m.start() < fm_e and fm_e > 0
        if in_fm and not (fm_ok and _fm_link_ok(text, m.start(), m.end())):
            continue
        linkpath, frag, alias, sep, had_hash = _parse_wiki_inner(m.group(2))
        lk = Link(src, m.start(), m.end(), "wiki", bool(m.group(1)), linkpath, frag, alias, sep,
                  in_frontmatter=in_fm, raw=m.group(0))
        lk._had_hash = had_hash
        line_start = text.rfind("\n", 0, m.start()) + 1
        if sep == "|" and alias is not None and line_start in tables:
            lk.table_split = True   # Obsidian splits the cell here: not a link today
        links.append(lk)
    for m in MDLINK_RE.finditer(text):
        if mask[m.start()] or (fm_e and m.start() < fm_e):
            continue
        tgt = m.group(3)
        if tgt.startswith("<") and tgt.endswith(">"):
            tgt = tgt[1:-1]
        if SCHEME_RE.match(tgt):
            continue
        if any(m.start() < l.end and l.start < m.end() for l in links):
            continue
        had_hash = "#" in tgt
        lp, frag = (tgt.split("#", 1) if had_hash else (tgt, ""))
        lk = Link(src, m.start(), m.end(), "md", bool(m.group(1)), unquote(lp), frag, m.group(2),
                  raw=m.group(0), md_title=m.group(4) or "")
        lk._had_hash = had_hash
        links.append(lk)
    links.sort(key=lambda l: l.start)
    return links


def read(root: str, rel: str) -> str:
    with open(os.path.join(root, rel), encoding="utf-8", errors="surrogateescape") as fh:
        return fh.read()


def write(root: str, rel: str, text: str) -> None:
    with open(os.path.join(root, rel), "w", encoding="utf-8", errors="surrogateescape") as fh:
        fh.write(text)


def apply_rewrites(text: str, repl: list[tuple[Link, str]]) -> str:
    """Replace each link span with its new rendering, right to left."""
    for lk, new in sorted(repl, key=lambda x: x[0].start, reverse=True):
        text = text[:lk.start] + new + text[lk.end:]
    return text
