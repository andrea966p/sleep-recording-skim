#!/usr/bin/env python3
"""Contract for naming.py -- what a run is called on the NAS.

These names are what people will look for in a year, and a folder name is the
hardest thing in this pipeline to change after the fact: once a run is on the
NAS, renaming it breaks every note and script that points at it. So the rule gets
the same treatment as the state machine -- half the cases are refusals.

    python3 test_naming.py
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import naming
import presets as P

PASS, FAIL = [], []
CFG = P.load()


def check(name, fn):
    try:
        fn()
    except Exception:
        FAIL.append((name, traceback.format_exc()))
        print(f"  FAIL  {name}")
    else:
        PASS.append(name)
        print(f"  ok    {name}")


def expect(name, fn, exc=Exception, want=""):
    def run():
        try:
            fn()
        except exc as e:
            if want and want.lower() not in str(e).lower():
                raise AssertionError(f"wrong reason: {e}\nwanted {want!r}")
            return
        raise AssertionError("NOT REFUSED")
    check(name, run)


class FakeRun:
    """Just the fields naming.run_names reads."""
    def __init__(self, *, slots, batch_name=None,
                 base_name="allego_0__uid0925-09-00-01",
                 actual_start="2026-09-25T00:00:01Z"):
        self.slots = slots
        self.batch_name = batch_name
        self.base_name = base_name
        self.actual_start = actual_start


def mice(n, rtype="recovery"):
    slots = ["A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2"][:n]
    return {s: {"mouse_id": f"HLBSSL{i}", "recording_type": rtype}
            for i, s in enumerate(slots, start=31)}


# --------------------------------------------------------------------------- #
def t_the_example_from_the_request():
    """andrea, batch HLBSSL, 8 recovery mice, 25 Sep 2026 -> 20260925_HLBSSL_RSR."""
    n = naming.run_names(FakeRun(slots=mice(8), batch_name="HLBSSL"), CFG)
    assert n["folder"] == "20260925_HLBSSL_RSR", n
    assert n["file_base"] == "20260925_HLBSSL_RSR_8mice", n
    assert n["renamed"] is True


def t_each_code():
    for rtype, code in (("basal", "BSR"), ("recovery", "RSR"), ("sd", "SDR")):
        n = naming.run_names(FakeRun(slots=mice(4, rtype), batch_name="B1"), CFG)
        assert n["folder"] == f"20260925_B1_{code}", (rtype, n)
        assert n["file_base"].endswith("_4mice"), n


def t_count_follows_the_occupied_slots():
    for k in (1, 3, 5, 8):
        n = naming.run_names(FakeRun(slots=mice(k), batch_name="X"), CFG)
        assert n["file_base"] == f"20260925_X_RSR_{k}mice", (k, n)


def t_mixed_conditions_name_all_of_them():
    """A run may hold mice of different types. Both codes appear, in config order.

    The rig records all four ports at once, so nothing stops a basal animal and a
    recovery animal sharing a run. Picking one code would file half the animals
    under a condition they were not in -- silently, in the folder name, which is
    the thing people trust most.
    """
    slots = mice(4, "basal")
    slots["D1"] = {"mouse_id": "HLBSSL99", "recording_type": "sd"}
    n = naming.run_names(FakeRun(slots=slots, batch_name="MIX"), CFG)
    assert n["folder"] == "20260925_MIX_BSR-SDR", n
    assert n["file_base"] == "20260925_MIX_BSR-SDR_5mice", n


def t_empty_slots_are_not_counted():
    slots = mice(3)
    slots["D2"] = {"mouse_id": "", "recording_type": "basal"}   # left blank
    n = naming.run_names(FakeRun(slots=slots, batch_name="P"), CFG)
    assert n["file_base"] == "20260925_P_RSR_3mice", n
    assert "BSR" not in n["folder"], "an empty slot's type reached the folder name"


def t_no_batch_name_keeps_the_old_layout():
    """A blank field is not a failure. Nothing in the pipeline requires a name."""
    n = naming.run_names(FakeRun(slots=mice(8)), CFG)
    assert n["folder"] == "2026-09-25_allego_0__uid0925-09-00-01", n
    assert n["file_base"] == "allego_0__uid0925-09-00-01", n
    assert n["renamed"] is False


def t_date_is_local_and_from_the_uid():
    """A 08:55 KST start is 23:55 UTC the PREVIOUS day. The uid is already local.

    This exact case filed the first real 24 h run a day early before it was fixed.
    """
    r = FakeRun(slots=mice(8), batch_name="HLBSSL",
                base_name="allego_0__uid0912-08-55-18",
                actual_start="2026-09-11T23:55:18Z")     # UTC, previous day
    assert naming.run_names(r, CFG)["folder"] == "20260912_HLBSSL_RSR"


def t_collision_suffix_reaches_both_names():
    """Folder and file base must pick up the same suffix.

    Two runs of one batch on one day are distinguishable in their folders anyway;
    it is the moment someone downloads both into a single directory that a shared
    file name loses one of them.
    """
    n = naming.run_names(FakeRun(slots=mice(8), batch_name="HLBSSL"), CFG, suffix=3)
    assert n["folder"] == "20260925_HLBSSL_RSR-3", n
    assert n["file_base"] == "20260925_HLBSSL_RSR-3_8mice", n


def t_preview_matches_the_real_thing():
    """The UI must not be able to promise a name the uploader would not produce."""
    slots = mice(6, "sd")
    live = naming.run_names(FakeRun(slots=slots, batch_name="ABC"), CFG)
    shown = naming.preview(batch_name="ABC", slots=slots, cfg=CFG,
                           date_yyyymmdd="20260925")
    assert shown["folder"] == live["folder"], (shown, live)
    assert shown["file_base"] == live["file_base"], (shown, live)


def refusals():
    bad = {
        "a slash escapes the user's folder": "../../11_Protocols",
        "a space is not a folder name here": "HLB SSL",
        "a dot-dot segment": "..",
        "an absolute path": "/etc",
        "a quote": "HLB'SSL",
        "too long": "H" * 33,
    }
    for why, name in bad.items():
        expect(f"refuse batch name: {why}",
               lambda n=name: naming.clean_batch(n), naming.NamingError, "letters")

    expect("refuse: a run with no occupied slot has no condition to name",
           lambda: naming.run_names(
               FakeRun(slots={"A1": {"mouse_id": "", "recording_type": "basal"}},
                       batch_name="X"), CFG),
           naming.NamingError, "no occupied slot")

    expect("refuse: a recording type with no code",
           lambda: naming.run_names(
               FakeRun(slots={"A1": {"mouse_id": "M", "recording_type": "nonsense"}},
                       batch_name="X"), CFG),
           P.PresetError, "no code")

    # blank is allowed and means "keep Allego's name" -- the opposite of a refusal
    check("blank batch name is accepted, not refused",
          lambda: (naming.clean_batch("") is None) or (_ for _ in ()).throw(
              AssertionError("blank should be None")))


def t_upload_lands_renamed(tmp: Path):
    """The uploader must actually write the new names, not merely compute them.

    Runs the real `upload_recording` against a temporary directory standing in
    for the mount, because the interesting part is the local-name -> remote-name
    mapping and the folder layout, neither of which needs a network.
    """
    import nas_upload as NU

    src = tmp / "stripped"
    src.mkdir(parents=True)
    base = "allego_0__uid0925-09-00-01"
    for suf in ("_data.xdat", "_timestamp.xdat", ".xdat.json", ".strip-report.json"):
        (src / f"{base}{suf}").write_bytes(b"x" * 4096)
    (src / f"{base}.xdat.json").write_text('{"status": {"start_time": "2026-09-25T00:00:01Z"}}')
    qc = tmp / f"{base}.npz"
    qc.write_bytes(b"q" * 512)

    fake_nas = tmp / "nas" / "andrea"
    fake_nas.mkdir(parents=True)
    real = (NU.require_nas, NU.user_dir, NU.MANIFEST)
    try:
        NU.require_nas = lambda: {"ok": True}
        NU.user_dir = lambda u: fake_nas
        NU.MANIFEST = tmp / "uploads.jsonl"     # NEVER the real one: a fake
                                                # VERIFIED row makes the uploader
                                                # skip a real file later
        summary = NU.upload_recording(
            src / base, "andrea", qc_bundle=[qc],
            run_json={"run_id": "test", "owner": "andrea"},
            dest_name="20260925_HLBSSL_RSR",
            file_base="20260925_HLBSSL_RSR_8mice",
            progress=lambda _m: None)
    finally:
        NU.require_nas, NU.user_dir, NU.MANIFEST = real

    dest = fake_nas / "20260925_HLBSSL_RSR"
    got = sorted(p.relative_to(dest).as_posix() for p in dest.rglob("*") if p.is_file())
    want = sorted([
        "20260925_HLBSSL_RSR_8mice_data.xdat",
        "20260925_HLBSSL_RSR_8mice_timestamp.xdat",
        "20260925_HLBSSL_RSR_8mice.xdat.json",
        "20260925_HLBSSL_RSR_8mice.strip-report.json",
        "run.json", "UPLOAD.json",
        f"qc/{base}.npz",          # QC keeps ITS name: it describes the ORIGINAL
    ])
    assert got == want, f"\n got: {got}\nwant: {want}"
    assert summary["status"] == "VERIFIED", summary
    assert summary["allego_base"] == base and summary["file_base"].endswith("_8mice")
    assert not any(base in n for n in got if not n.startswith("qc/")), \
        "an Allego-named file reached the NAS alongside the renamed ones"


def t_a_verified_row_is_not_believed_over_the_share(tmp: Path):
    """A manifest row must never stop an upload of a file that is not there.

    THE HAZARD. A VERIFIED row means "do not upload this again". If someone has
    since deleted the file from the share -- ordinary housekeeping -- that row
    makes the uploader ship nothing and report success, and the data is gone.

    Found 2026-09-15: four folders of test data were tidied off the NAS and the
    manifest still swore every file was verified. The manifest is a CLAIM about
    the share, so it is checked against the share before it is believed.
    """
    import nas_upload as NU

    src = tmp / "stripped"
    src.mkdir(parents=True)
    base = "allego_0__uid0925-09-00-01"
    for suf in ("_data.xdat", "_timestamp.xdat", ".xdat.json", ".strip-report.json"):
        (src / f"{base}{suf}").write_bytes(b"x" * 4096)
    (src / f"{base}.xdat.json").write_text('{"status": {"start_time": "2026-09-25T00:00:01Z"}}')

    fake_nas = tmp / "nas" / "andrea"
    fake_nas.mkdir(parents=True)
    real = (NU.require_nas, NU.user_dir, NU.MANIFEST)
    try:
        NU.require_nas = lambda: {"ok": True}
        NU.user_dir = lambda u: fake_nas
        NU.MANIFEST = tmp / "uploads.jsonl"

        first = NU.upload_recording(src / base, "andrea", dest_name="D",
                                    file_base="F", progress=lambda _m: None)
        assert first["status"] == "VERIFIED"
        landed = fake_nas / "D" / "F_data.xdat"
        assert landed.exists()

        # someone tidies the share, exactly as happened
        landed.unlink()

        second = NU.upload_recording(src / base, "andrea", dest_name="D",
                                     file_base="F", progress=lambda _m: None)
        assert second["status"] == "VERIFIED", second
        assert landed.exists(), "the deleted file was NOT re-uploaded"
        assert landed.stat().st_size == 4096

        # and an untouched file is still skipped, so this costs nothing normally
        ts = fake_nas / "D" / "F_timestamp.xdat"
        before = ts.stat().st_mtime_ns
        NU.upload_recording(src / base, "andrea", dest_name="D", file_base="F",
                            progress=lambda _m: None)
        assert ts.stat().st_mtime_ns == before, "an intact file was re-sent"
    finally:
        NU.require_nas, NU.user_dir, NU.MANIFEST = real


def main() -> int:
    print("NAMING")
    for fn in (t_the_example_from_the_request, t_each_code,
               t_count_follows_the_occupied_slots, t_mixed_conditions_name_all_of_them,
               t_empty_slots_are_not_counted, t_no_batch_name_keeps_the_old_layout,
               t_date_is_local_and_from_the_uid, t_collision_suffix_reaches_both_names,
               t_preview_matches_the_real_thing):
        check(fn.__name__, fn)
    import tempfile
    check("a VERIFIED row is not believed over the share",
          lambda: t_a_verified_row_is_not_believed_over_the_share(
              Path(tempfile.mkdtemp(prefix="naming-"))))
    check("t_upload_lands_renamed",
          lambda: t_upload_lands_renamed(Path(tempfile.mkdtemp(prefix="naming-"))))
    print("\nMUST REFUSE")
    refusals()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    for n, tb in FAIL:
        print(f"\n--- {n} ---\n{tb}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
