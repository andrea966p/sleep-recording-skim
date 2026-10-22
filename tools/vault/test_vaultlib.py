"""Fixture tests pinning vaultlib's Obsidian-compatible link parsing and resolution."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vaultlib import (FileIndex, apply_rewrites, frontmatter_valid, link_name,  # noqa: E402
                      parse_links, split_frontmatter)

SRC = "02-procedures/note.md"


def links(text, src=SRC):
    return parse_links(text, src)


# ---------------------------------------------------------------- 1. escaped pipe
ESC = ("| a | [[../00-config/production-values#Mosquitto MQTT Authentication "
       "(since 2026-05-22)\\|production-values]] |\n")


def test_escaped_pipe_fields():
    (lk,) = links("| h | h |\n|---|---|\n" + ESC)
    assert lk.kind == "wiki" and not lk.embed
    assert lk.linkpath == "../00-config/production-values"
    assert lk.fragment == "Mosquitto MQTT Authentication (since 2026-05-22)"
    assert lk.alias == "production-values"
    assert lk.sep == "\\|"
    assert not lk.table_split


def test_escaped_pipe_resolves_relative_to_source_folder():
    (lk,) = links("| h | h |\n|---|---|\n" + ESC)
    idx = FileIndex([SRC, "00-config/production-values.md", "x/production-values.md"])
    assert idx.resolve(lk.linkpath, SRC) == "00-config/production-values.md"


def test_escaped_pipe_render():
    (lk,) = links("| h | h |\n|---|---|\n" + ESC)
    assert lk.render(lk.linkpath) == lk.raw
    new = lk.render("production-values")
    assert new.startswith("[[production-values#Mosquitto") and "\\|production-values]]" in new


# ---------------------------------------------------------------- 2. table_split
def test_unescaped_pipe_table_split():
    tbl = "| h | h |\n|---|---|\n| a | [[n#H|x]] |\n"
    (lk,) = links(tbl)
    assert lk.table_split is True and lk.sep == "|" and lk.alias == "x"
    (lk2,) = links("Some paragraph with [[n#H|x]] here.\n")
    assert lk2.table_split is False


# ---------------------------------------------------------------- 3. code exclusion
def test_fenced_code_ignored():
    assert links("```\n[[a]]\n```\n") == []
    assert links("~~~\n[[a]]\n~~~\n") == []


def test_fence_in_callout_ignored_but_after_is_link():
    t = "> [!note]\n> ```bash\n> echo [[a]]\n> ```\n\n[[b]]\n"
    assert [l.linkpath for l in links(t)] == ["b"]


def test_indented_code_ignored():
    assert links("para\n\n    [[a]]\n\n[[b]]\n") and \
        [l.linkpath for l in links("para\n\n    [[a]]\n\n[[b]]\n")] == ["b"]


def test_inline_code_spans_ignored():
    assert links("x `[[a]]` y\n") == []
    assert links("x ``[[a]] ` [[b]]`` y [[c]]\n")[0].linkpath == "c"
    # span wrapping onto a second line of the same paragraph
    t = "start `code [[a]]\nstill [[b]] code` then [[c]]\n"
    assert [l.linkpath for l in links(t)] == ["c"]


def test_ascii_art_tildes_inside_backtick_fence():
    t = "```\n~~~~-~~~~\n[[a]]\n~~~~-~~~~\n```\n[[b]]\n"
    assert [l.linkpath for l in links(t)] == ["b"]


# ---------------------------------------------------------------- 4. frontmatter
def test_frontmatter_quoted_link_is_link():
    t = '---\nrelated: "[[a]]"\n---\nbody [[b]]\n'
    ls = links(t)
    assert [(l.linkpath, l.in_frontmatter) for l in ls] == [("a", True), ("b", False)]


def test_frontmatter_invalid_yaml_yields_no_links():
    t = "---\nrelated: [[a]], [[b]]\n---\nbody\n"
    assert not frontmatter_valid(t)
    assert links(t) == []


def test_unterminated_or_non_yaml_frontmatter():
    t = "---\nthis: is: not: yaml: [\n[[a]]\n---\nbody\n"
    assert not frontmatter_valid(t)
    assert [l for l in links(t) if l.in_frontmatter] == []
    assert split_frontmatter("---\nno end\n") == (0, 0)
    assert split_frontmatter("no fm\n") == (0, 0)


# ---------------------------------------------------------------- 5. kinds
def test_embeds():
    a, b = links("![[fig.png]] and ![[note#Heading|alias]]\n")
    assert a.embed and a.linkpath == "fig.png" and a.alias is None
    assert b.embed and (b.linkpath, b.fragment, b.alias) == ("note", "Heading", "alias")


def test_self_link():
    (lk,) = links("[[#Heading|x]]\n")
    assert (lk.linkpath, lk.fragment, lk.alias) == ("", "Heading", "x")
    assert FileIndex([SRC]).resolve("", SRC) == SRC


def test_markdown_links():
    ls = links("[x](#anchor) [y](other%20note.md) [z](https://e.com) [m](mailto:a@b.c)\n")
    assert [(l.kind, l.linkpath, l.fragment) for l in ls] == [
        ("md", "", "anchor"), ("md", "other note.md", "")]
    assert ls[1].render("my note.md") == "[y](my%20note.md)"


# ---------------------------------------------------------------- 6. resolve
FILES = ["README.md", "pipeline/README.md", "docs/README.md", "pipeline/Run.md",
         "02-procedures/note.md", "02-procedures/dup.md", "other/dup.md",
         "data/x.tsv", "img/fig.png", "00-config/Prod.md"]
IDX = FileIndex(FILES)


def test_resolve_basic():
    r = IDX.resolve
    assert r("pipeline/README.md", SRC) == "pipeline/README.md"       # exact
    assert r("Run", SRC) == "pipeline/Run.md"                          # bare name
    assert r("pipeline/README", SRC) == "pipeline/README.md"           # partial path
    assert r("docs/README", SRC) == "docs/README.md"
    assert r("run", SRC) == "pipeline/Run.md"                          # case-insensitive
    assert r("PIPELINE/readme", SRC) == "pipeline/README.md"
    assert r("nope", SRC) is None


def test_resolve_non_md():
    assert IDX.resolve("x.tsv", SRC) == "data/x.tsv"
    assert IDX.resolve("fig.png", SRC) == "img/fig.png"
    assert IDX.resolve("img/fig.png", SRC) == "img/fig.png"
    assert IDX.resolve("fig", SRC) is None


def test_resolve_relative_no_fallback():
    assert IDX.resolve("./dup", SRC) == "02-procedures/dup.md"
    assert IDX.resolve("../00-config/Prod", SRC) == "00-config/Prod.md"
    assert IDX.resolve("./Run", SRC) is None          # exists elsewhere: no fallback
    assert IDX.resolve("../Prod", SRC) is None
    assert IDX.resolve("../../../Run", SRC) is None   # escapes the vault


def test_resolve_ambiguity_prefers_source_folder():
    assert IDX.resolve("dup", "02-procedures/note.md") == "02-procedures/dup.md"
    assert IDX.resolve("dup", "other/zzz.md") == "other/dup.md"
    # no same-folder candidate: shallowest path wins
    assert IDX.resolve("README", "elsewhere/n.md") == "README.md"


# ---------------------------------------------------------------- 7. shortest
def test_shortest():
    assert IDX.shortest("pipeline/Run.md") == "Run"
    assert IDX.shortest("data/x.tsv") == "x.tsv"
    assert IDX.shortest("pipeline/README.md") == "pipeline/README"
    assert IDX.shortest("README.md") == "README"  # only one top-level; still ambiguous by name
    assert IDX.shortest("other/dup.md") == "other/dup"
    deep = FileIndex(["a/x/n.md", "b/x/n.md", "c/n.md"])
    assert deep.shortest("a/x/n.md") == "a/x/n"
    assert deep.shortest("c/n.md") == "c/n"
    assert link_name("a/b.md") == "b" and link_name("a/b.png") == "b.png"


# ---------------------------------------------------------------- 8. round trip
FIXTURE = (
    '---\nrelated: "[[a]]"\ntags: [x]\n---\n'
    "Intro [[a#H|alias]] ![[fig.png]] ![[note#Heading|al]] [[#Self|x]]\n"
    "md [x](#anchor) [y](other%20note.md \"t\") [e](https://e.com)\n\n"
    "| h | h |\n|---|---|\n" + ESC +
    "| a | [[n#H|x]] |\n\n"
    "```\n~~~~-~~~~\n[[code]]\n```\n\n"
    "> [!n]\n> ```bash\n> [[code2]]\n> ```\n\n"
    "    [[indented]]\n\n"
    "inline `[[c]]` and ``[[d]] ` x`` and `wrap [[e]]\nmore` end [[z|zz]]\n"
)


def test_round_trip_is_byte_identical():
    ls = links(FIXTURE)
    names = [l.linkpath for l in ls]
    assert "code" not in names and "code2" not in names and "indented" not in names
    assert len(ls) >= 10
    out = apply_rewrites(FIXTURE, [(l, l.render(l.linkpath)) for l in ls])
    assert out == FIXTURE


def test_rewrite_changes_only_target():
    t = "A [[old#H|al]] B ![[old]] C\n"
    ls = links(t)
    out = apply_rewrites(t, [(l, l.render("new/old")) for l in ls])
    assert out == "A [[new/old#H|al]] B ![[new/old]] C\n"


if __name__ == "__main__":
    bad = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS", name)
            except Exception as e:  # noqa: BLE001
                bad += 1
                print("FAIL", name, repr(e))
    sys.exit(1 if bad else 0)
