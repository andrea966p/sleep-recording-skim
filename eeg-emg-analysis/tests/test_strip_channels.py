#!/usr/bin/env python3
"""Contract for convert/strip_channels.py.

HALF OF THIS FILE IS REFUSALS, on purpose. The repo's own rule is that "a test
that can only pass is not evidence": a stripper that happily wrote something for
every input would pass any suite made only of success cases, and the failure it
would eventually produce -- a file whose sidecar misdescribes its own columns --
is silent. So every guard gets a case that makes it fire, including the
bit-exactness gate itself, which is given a deliberately corrupted output and
must reject it.

Run as a script, not under pytest (this repo's convention):
    PYTHONPATH=. python3 tests/test_strip_channels.py
Needs numpy and scipy (scipy only because tests/synth.py uses it for the noise
shapes; strip_channels itself is numpy + stdlib).
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile
import traceback
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from convert import strip_channels as SC
from core import criteria as C
from tests import synth

FS = synth.FS
PASS, FAIL = [], []


def check(name: str, fn):
    try:
        fn()
    except Exception:
        FAIL.append((name, traceback.format_exc()))
        print(f"  FAIL  {name}")
    else:
        PASS.append(name)
        print(f"  ok    {name}")


def expect_refused(name: str, fn, *, want: str = "", exc=SC.StripRefused):
    """The case must RAISE. A case that silently succeeds is the bug."""
    def run():
        try:
            fn()
        except exc as e:
            if want and want.lower() not in str(e).lower():
                raise AssertionError(
                    f"refused for the wrong reason: {e}\nwanted mention of {want!r}")
            return
        raise AssertionError("NOT REFUSED -- the guard did not fire")
    check(name, run)


# --------------------------------------------------------------------------- #
# fixtures
# --------------------------------------------------------------------------- #

def make_recording(tmp: Path, *, seconds: int = 12, name: str = "rec",
                   n_pri_per_port: int = 8, ports=("A", "B"),
                   with_gpio: bool = True, extra_array=None,
                   biointerface_spec=None, din_live: bool = False,
                   seed: int = 7) -> tuple[str, list[str]]:
    """A small but structurally real recording. Returns (base, labels)."""
    rng = np.random.default_rng(seed)
    n = seconds * FS
    items, types, sel = [], [], []
    for p in ports:
        for s in range(1, n_pri_per_port + 1):
            items.append((f"{p}/{s}", synth.scale_to_epoch_rms(
                synth.pink(n, rng, 1.8), 50.0)))
            types.append(synth._PRI)
            sel.append(s in (1, 2))          # the two-role selection
    if with_gpio:
        for i, (lab, t) in enumerate(synth.gpio_labels()):
            if t == synth._DIN:
                v = (np.arange(n) % 500 < 5).astype(np.float32) if din_live \
                    else np.zeros(n, dtype=np.float32)
            elif t == synth._AUX:
                v = np.full(n, 10.24, dtype=np.float32) + (
                    rng.normal(0, 0.01, n) if i == 0 else 0.0)
            else:
                v = np.ones(n, dtype=np.float32)
            items.append((lab, v)); types.append(t); sel.append(False)
    base = synth.write_full_sidecar(
        tmp / name, items, chan_types=types, selected=sel,
        extra_array=extra_array, biointerface_spec=biointerface_spec)
    return base, [lab for lab, _ in items]


def strip_ok(base: str, out: Path, keep, **kw) -> dict:
    dst = str(out / os.path.basename(base))
    return SC.strip(base, dst, keep, progress=None, min_free_gb=0.0, **kw)


# --------------------------------------------------------------------------- #
# MUST PASS
# --------------------------------------------------------------------------- #

def test_happy_path(tmp: Path):
    base, _ = make_recording(tmp, name="happy")
    meta = SC.read_meta(base)
    keep = SC.resolve_keep(meta, selected=True)
    out = tmp / "o"; out.mkdir()
    rep = strip_ok(base, out, keep)
    dst = str(out / "happy")
    k = len(keep)

    assert rep["status"] == "verified"
    assert rep["verify"]["exact"] is True

    dm = json.load(open(dst + ".xdat.json"))
    bm = dm["sapiens_base"]["biointerface_map"]

    # every per-channel array subset to k; the scalar left alone
    for key, val in bm.items():
        if isinstance(val, list):
            assert len(val) == k, f"{key} has {len(val)}, want {k}"
    assert bm["samp_freq"] is None

    # the two row-addressing fields renumbered, identity preserved
    assert bm["sys_chan_idx"] == list(range(k))
    assert bm["absolute_idx"] == list(range(k))
    sm = json.load(open(base + ".xdat.json"))["sapiens_base"]["biointerface_map"]
    for key in ("ntv_chan_idx", "ntv_chan_name", "chan_name", "port", "site_num",
                "headstage_id", "probe_id", "is_selected"):
        assert bm[key] == [sm[key][i] for i in keep], f"{key} was not preserved"

    # status
    assert dm["status"]["shape"] == [12 * FS, k]
    assert dm["status"]["num_smpl"] == 12 * FS
    sig = dm["status"]["signals"]
    assert sig["total"] == k == sig["pri"] + sig["aux"] + sig["din"] + sig["dout"]
    assert dm["status"]["dataset_uid"] != sm and dm["status"]["dataset_uid"]


def test_checksum_matches_independent_recompute(tmp: Path):
    """dataset_checksum must equal sha256(data || timestamp), computed here."""
    base, _ = make_recording(tmp, name="ck")
    keep = SC.resolve_keep(SC.read_meta(base), selected=True)
    out = tmp / "o"; out.mkdir()
    strip_ok(base, out, keep)
    dst = str(out / "ck")
    h = hashlib.sha256()
    for suffix in ("_data.xdat", "_timestamp.xdat"):
        h.update(Path(dst + suffix).read_bytes())
    assert json.load(open(dst + ".xdat.json"))["status"]["dataset_checksum"] \
        == h.hexdigest()


def test_timestamp_copied_verbatim(tmp: Path):
    base, _ = make_recording(tmp, name="ts")
    keep = SC.resolve_keep(SC.read_meta(base), selected=True)
    out = tmp / "o"; out.mkdir()
    strip_ok(base, out, keep)
    assert Path(base + "_timestamp.xdat").read_bytes() == \
        Path(str(out / "ts") + "_timestamp.xdat").read_bytes()


def test_roundtrip_through_open_xdat(tmp: Path):
    base, labels = make_recording(tmp, name="rt")
    meta = SC.read_meta(base)
    keep = SC.resolve_keep(meta, labels=["A/1", "A/2", "B/1", "B/2"])
    out = tmp / "o"; out.mkdir()
    strip_ok(base, out, keep)
    dst = str(out / "rt")
    assert C.file_integrity(dst)["verdict"] == "INTACT"
    x, got, fs, n = C.open_xdat(dst)
    assert got == ["A/1", "A/2", "B/1", "B/2"], got
    assert fs == FS and n == 12 * FS and x.shape == (12 * FS, 4)
    del x


def test_bit_exact_against_source(tmp: Path):
    base, _ = make_recording(tmp, name="be")
    meta = SC.read_meta(base)
    keep = SC.resolve_keep(meta, labels=["A/1", "B/2"])
    out = tmp / "o"; out.mkdir()
    strip_ok(base, out, keep)
    n_in = len(meta["sapiens_base"]["biointerface_map"]["port"])
    src = SC._read_block(base + "_data.xdat", 0, 12 * FS, n_in)
    dst = SC._read_block(str(out / "be") + "_data.xdat", 0, 12 * FS, 2)
    assert np.array_equal(src[:, keep].view(np.uint32), dst.view(np.uint32))


def test_site_hood_pruned_and_friends_filtered(tmp: Path):
    base, _ = make_recording(tmp, name="hood")
    meta = SC.read_meta(base)
    keep = SC.resolve_keep(meta, labels=["A/1", "A/2"])
    out = tmp / "o"; out.mkdir()
    strip_ok(base, out, keep)
    dm = json.load(open(str(out / "hood") + ".xdat.json"))
    hood = dm["sapiens_base"]["neighborhoods"]["site_hood"]
    bm = dm["sapiens_base"]["biointerface_map"]
    kept_ntv = {bm["ntv_chan_idx"][i] for i in range(len(bm["port"]))
                if bm["chan_type"][i] == "ai0"}
    assert set(int(k) for k in hood) == kept_ntv, "hood keys not pruned to kept"
    for entry in hood.values():
        for f in entry["friends"]:
            assert f["ntv_chan_idx"] in kept_ntv, "a dropped friend survived"


def test_unknown_extra_array_is_carried_not_dropped(tmp: Path):
    """A 36th per-channel array must be subset, not silently discarded."""
    base, _ = make_recording(tmp, name="extra", extra_array="future_field_v2")
    keep = SC.resolve_keep(SC.read_meta(base), selected=True)
    out = tmp / "o"; out.mkdir()
    strip_ok(base, out, keep)
    bm = json.load(open(str(out / "extra") + ".xdat.json"))["sapiens_base"]["biointerface_map"]
    assert "future_field_v2" in bm, "an unknown array was dropped"
    assert len(bm["future_field_v2"]) == len(keep)


def test_with_gpio_keeps_all_six(tmp: Path):
    base, _ = make_recording(tmp, name="gpio")
    meta = SC.read_meta(base)
    keep = SC.resolve_keep(meta, selected=True, with_gpio=True)
    out = tmp / "o"; out.mkdir()
    rep = strip_ok(base, out, keep)
    sig = json.load(open(str(out / "gpio") + ".xdat.json"))["status"]["signals"]
    assert (sig["aux"], sig["din"], sig["dout"]) == (2, 2, 2), sig
    assert rep["dropped_gpio"] == []


def test_provenance_makes_renumbering_reversible(tmp: Path):
    base, _ = make_recording(tmp, name="prov")
    meta = SC.read_meta(base)
    keep = SC.resolve_keep(meta, labels=["A/2", "B/1"])
    out = tmp / "o"; out.mkdir()
    strip_ok(base, out, keep)
    prov = json.load(open(str(out / "prov") + ".xdat.json"))["status"]["dataset_provenance"][-1]
    assert prov["kept_orig_file_index"] == list(keep)
    assert prov["renumbered_fields"] == ["sys_chan_idx", "absolute_idx"]
    assert prov["source_n_channels"] == len(meta["sapiens_base"]["biointerface_map"]["port"])
    assert prov["kept_labels"] == ["A/2", "B/1"]


def test_resume_from_torn_partial_is_identical(tmp: Path):
    base, _ = make_recording(tmp, name="res", seconds=20)
    meta = SC.read_meta(base)
    keep = SC.resolve_keep(meta, labels=["A/1", "A/2"])
    out = tmp / "o"; out.mkdir()
    dst = str(out / "res")
    strip_ok(base, out, keep)
    ref = Path(dst + "_data.xdat").read_bytes()

    row = 2 * 4
    rows = (len(ref) // row) * 60 // 100
    os.replace(dst + "_data.xdat", dst + "_data.xdat.part")
    with open(dst + "_data.xdat.part", "r+b") as fh:
        fh.truncate(rows * row)
        # truncate() does NOT move the file position, so seek to the end or the
        # three bytes land on row 0 and corrupt real data instead of appending a
        # torn tail. (Gate A caught exactly that mistake when this test was
        # first written, which is the gate doing its job.)
        fh.seek(0, os.SEEK_END)
        fh.write(b"\x01\x02\x03")                 # a torn partial row
    os.remove(dst + ".xdat.json")
    os.remove(dst + "_timestamp.xdat")
    strip_ok(base, out, keep)
    assert Path(dst + "_data.xdat").read_bytes() == ref, "resume diverged"


def test_already_done_is_a_noop(tmp: Path):
    base, _ = make_recording(tmp, name="idem")
    keep = SC.resolve_keep(SC.read_meta(base), selected=True)
    out = tmp / "o"; out.mkdir()
    strip_ok(base, out, keep)
    again = strip_ok(base, out, keep)
    assert again["status"] == "already_done", again["status"]


def test_stale_live_flag_is_not_read_as_busy(tmp: Path):
    """The 2026-09-11 correction: a crashed recording keeps is_live_recording
    true forever, so it must not be treated as liveness."""
    base, _ = make_recording(tmp, name="stale")
    meta = json.load(open(base + ".xdat.json"))
    meta["status"]["is_live_recording"] = True
    Path(base + ".xdat.json").write_text(json.dumps(meta, separators=(",", ":")))
    old = os.path.getmtime(base + "_data.xdat")
    os.utime(base + "_data.xdat", (old - 10_000, old - 10_000))
    assert SC.rig_is_busy(tmp) is None, "a stale flag was read as a live recording"
    assert "stale.xdat.json" in SC.stale_live_flags(tmp), "crash marker not reported"


# --------------------------------------------------------------------------- #
# MUST REFUSE
# --------------------------------------------------------------------------- #

def refusals(tmp: Path):
    base, _ = make_recording(tmp, name="ref")
    meta = SC.read_meta(base)
    n_in = len(meta["sapiens_base"]["biointerface_map"]["port"])
    out = tmp / "or"; out.mkdir()

    expect_refused("refuse: no selection mode",
                   lambda: SC.resolve_keep(meta), want="exactly one")
    expect_refused("refuse: two selection modes",
                   lambda: SC.resolve_keep(meta, selected=True, labels=["A/1"]),
                   want="exactly one")
    expect_refused("refuse: index out of range (the 134-channel trap)",
                   lambda: SC.resolve_keep(meta, indices=[0, n_in]),
                   want="outside range")
    expect_refused("refuse: duplicate index",
                   lambda: SC.resolve_keep(meta, indices=[3, 3]),
                   want="more than once")
    expect_refused("refuse: unknown label",
                   lambda: SC.resolve_keep(meta, labels=["A/999"]),
                   want="not in this file")
    expect_refused("refuse: AMBIGUOUS gpio label",
                   lambda: SC.resolve_keep(meta, labels=["GPIO-AIN/0"]),
                   want="ambiguous")
    expect_refused("refuse: empty keep set",
                   lambda: SC.resolve_keep(meta, labels=[]), want="empty")

    # a keep set that puts a din before a pri
    bad = json.loads(Path(base + ".xdat.json").read_text())
    bm = bad["sapiens_base"]["biointerface_map"]
    bm["chan_type"][0] = "din0"
    p = tmp / "order"; shutil.copy(base + "_data.xdat", str(p) + "_data.xdat")
    shutil.copy(base + "_timestamp.xdat", str(p) + "_timestamp.xdat")
    Path(str(p) + ".xdat.json").write_text(json.dumps(bad, separators=(",", ":")))
    expect_refused("refuse: chan_type sections out of order",
                   lambda: SC.resolve_keep(SC.read_meta(str(p)), indices=[0, 1]),
                   want="out of")

    # unknown chan_type
    bad2 = json.loads(Path(base + ".xdat.json").read_text())
    bad2["sapiens_base"]["biointerface_map"]["chan_type"][0] = "quantum7"
    p2 = tmp / "utype"
    for s in ("_data.xdat", "_timestamp.xdat"):
        shutil.copy(base + s, str(p2) + s)
    Path(str(p2) + ".xdat.json").write_text(json.dumps(bad2, separators=(",", ":")))
    expect_refused("refuse: unknown chan_type",
                   lambda: SC.resolve_keep(SC.read_meta(str(p2)), indices=[0]),
                   want="unknown chan_type")

    # biointerface_spec populated
    b3, _ = make_recording(tmp, name="spec", biointerface_spec={"anything": 1})
    expect_refused("refuse: biointerface_spec populated",
                   lambda: SC.plan_strip(b3, str(out / "spec"), [0, 1]),
                   want="second")

    # a file with no selection at all
    b4, _ = make_recording(tmp, name="nosel")
    m4 = json.loads(Path(b4 + ".xdat.json").read_text())
    m4["sapiens_base"]["biointerface_map"]["is_selected"] = \
        [False] * len(m4["sapiens_base"]["biointerface_map"]["port"])
    Path(b4 + ".xdat.json").write_text(json.dumps(m4, separators=(",", ":")))
    expect_refused("refuse: --keep-selected with nothing selected",
                   lambda: SC.resolve_keep(SC.read_meta(b4), selected=True),
                   want="is_selected")

    # truncated source
    b5, _ = make_recording(tmp, name="trunc")
    with open(b5 + "_data.xdat", "r+b") as fh:
        fh.truncate(os.path.getsize(b5 + "_data.xdat") - 4)
    expect_refused("refuse: truncated source without --allow-truncated",
                   lambda: SC.plan_strip(b5, str(out / "trunc"), [0, 1]),
                   want="truncated")

    # a LIVE din being dropped
    b6, _ = make_recording(tmp, name="livedin", din_live=True)
    m6 = SC.read_meta(b6)
    keep6 = SC.resolve_keep(m6, selected=True)      # drops the din
    expect_refused("refuse: dropping a LIVE digital input (gate B)",
                   lambda: SC.strip(b6, str(out / "livedin"), keep6,
                                    progress=None, min_free_gb=0.0),
                   want="live digital input", exc=SC.StripFailed)

    # free-space reserve
    b7, _ = make_recording(tmp, name="space")
    k7 = SC.resolve_keep(SC.read_meta(b7), selected=True)
    expect_refused("refuse: would breach the free-space reserve",
                   lambda: SC.strip(b7, str(out / "space"), k7, progress=None,
                                    min_free_gb=10 ** 9),
                   want="reserve")

    # THE GATE'S OWN NEGATIVE CONTROL
    b8, _ = make_recording(tmp, name="corrupt")
    m8 = SC.read_meta(b8)
    k8 = SC.resolve_keep(m8, labels=["A/1", "A/2"])
    o8 = tmp / "oc"; o8.mkdir()
    SC.strip(b8, str(o8 / "corrupt"), k8, progress=None, min_free_gb=0.0)
    dp = str(o8 / "corrupt") + "_data.xdat"
    with open(dp, "r+b") as fh:                    # flip one bit
        fh.seek(4096); b = fh.read(1); fh.seek(4096); fh.write(bytes([b[0] ^ 1]))
    n8 = len(m8["sapiens_base"]["biointerface_map"]["port"])
    expect_refused(
        "refuse: verify_bit_exact detects a one-bit corruption (gate A control)",
        lambda: SC.verify_bit_exact(b8, dp, k8, n_channels_in=n8,
                                    n_channels_out=2, n_samples=12 * FS,
                                    mode="full"),
        want="bit mismatch", exc=SC.StripFailed)


# --------------------------------------------------------------------------- #

def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="strip-test-"))
    try:
        print("MUST PASS")
        for fn in (test_happy_path, test_checksum_matches_independent_recompute,
                   test_timestamp_copied_verbatim, test_roundtrip_through_open_xdat,
                   test_bit_exact_against_source,
                   test_site_hood_pruned_and_friends_filtered,
                   test_unknown_extra_array_is_carried_not_dropped,
                   test_with_gpio_keeps_all_six,
                   test_provenance_makes_renumbering_reversible,
                   test_resume_from_torn_partial_is_identical,
                   test_already_done_is_a_noop,
                   test_stale_live_flag_is_not_read_as_busy):
            d = Path(tempfile.mkdtemp(dir=tmp))
            check(fn.__name__, lambda fn=fn, d=d: fn(d))
        print("\nMUST REFUSE")
        refusals(Path(tempfile.mkdtemp(dir=tmp)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    for name, tb in FAIL:
        print(f"\n--- {name} ---\n{tb}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
