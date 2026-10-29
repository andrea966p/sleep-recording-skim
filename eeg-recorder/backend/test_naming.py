#!/usr/bin/env python3
"""Contract for naming.py and the per-mouse uploader -- where each mouse lands.

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
    """Just the fields naming.mouse_folders reads."""
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
    """andrea, batch HLBSSL, 8 recovery mice, 25 Sep 2026."""
    n = naming.mouse_folders(FakeRun(slots=mice(8), batch_name="HLBSSL"), CFG)
    assert n["A1"]["rel"] == "HLBSSL/Recovery/20260925_HLBSSL31_R", n["A1"]
    assert n["A1"]["file_base"] == n["A1"]["folder"] == "20260925_HLBSSL31_R"
    assert [n[s]["mouse_id"] for s in sorted(n)] == [f"HLBSSL{i}" for i in range(31, 39)]


def t_each_code_and_folder():
    want = {"basal": ("B", "Baseline"), "recovery": ("R", "Recovery")}
    assert set(CFG.recording_types) == set(want), CFG.recording_types
    for rtype, (code, folder) in want.items():
        n = naming.mouse_folders(FakeRun(slots=mice(1, rtype), batch_name="X"), CFG)
        assert n["A1"]["folder"].endswith(f"_{code}") and n["A1"]["condition_dir"] == folder, n


def t_there_is_no_sd_type():
    """SD is carried by the batch id (HLBWSD...), so it is not a condition folder."""
    assert "sd" not in CFG.recording_types
    expect_fn = lambda: CFG.type_folder("sd")
    try:
        expect_fn()
    except P.PresetError:
        return
    raise AssertionError("an `sd` folder still resolves")


def t_mixed_conditions_file_each_mouse_by_its_own_type():
    slots = {"A1": {"mouse_id": "M1", "recording_type": "basal"},
             "A2": {"mouse_id": "M2", "recording_type": "recovery"}}
    n = naming.mouse_folders(FakeRun(slots=slots, batch_name="MIX"), CFG)
    assert n["A1"]["rel"] == "MIX/Baseline/20260925_M1_B", n
    assert n["A2"]["rel"] == "MIX/Recovery/20260925_M2_R", n


def t_empty_slots_are_skipped():
    slots = {"A1": {"mouse_id": "M1", "recording_type": "basal"},
             "A2": {"mouse_id": "", "recording_type": "basal"}}
    assert list(naming.mouse_folders(FakeRun(slots=slots, batch_name="P"), CFG)) == ["A1"]


def t_date_is_local_and_from_the_uid():
    """08:55 KST is 23:55 UTC the day before; the folder takes the LOCAL date."""
    r = FakeRun(slots=mice(1), batch_name="HLBSSL",
                base_name="allego_0__uid0912-08-55-18", actual_start="2026-09-11T23:55:18Z")
    assert naming.mouse_folders(r, CFG)["A1"]["folder"] == "20260912_HLBSSL31_R"


def t_suffix_reaches_folder_file_and_path():
    e = naming.mouse_entry(date_yyyymmdd="20260925", batch="HLBSSL", mouse_id="HLBSSL31",
                           rtype="recovery", cfg=CFG, suffix=2)
    assert e == {"batch": "HLBSSL", "condition_dir": "Recovery",
                 "folder": "20260925_HLBSSL31_R-2", "file_base": "20260925_HLBSSL31_R-2",
                 "rel": "HLBSSL/Recovery/20260925_HLBSSL31_R-2"}, e


def t_preview_matches_the_real_thing():
    slots = mice(3)
    live = naming.mouse_folders(FakeRun(slots=slots, batch_name="ABC"), CFG)
    pv = naming.preview(batch_name="ABC", slots=slots, cfg=CFG, date_yyyymmdd="20260925")
    assert [m["rel"] for m in pv["mice"]] == [live[s]["rel"] for s in sorted(live)], pv
    assert naming.preview(batch_name="", slots=slots, cfg=CFG,
                          date_yyyymmdd="20260925")["mice"] == []


def t_config_refuses_a_type_without_a_folder(tmp: Path):
    head = """
nas: {share: S, root: R}
recording_types: [basal]
recording_type_codes: {basal: B}
users: {}
headstages:
  hs: {label: H, slots_per_chip: 32, real_channels: 16}
recording_settings:
  s: {label: S, headstage: hs, roles: {eeg: 1, emg: 2}}
"""
    bad = tmp / "bad.yaml"
    bad.write_text(head)
    try:
        P.load(bad)
    except P.PresetError as e:
        assert "recording_type_folders" in str(e), e
    else:
        raise AssertionError("a type with no condition folder was accepted")
    bad.write_text(head + "recording_type_folders: {basal: '../x'}\n")
    try:
        P.load(bad)
    except P.PresetError as e:
        assert "safe" in str(e), e
    else:
        raise AssertionError("an unsafe condition folder was accepted")


# --------------------------------------------------------------------------- #
# the uploader, against a temporary directory standing in for the share
# --------------------------------------------------------------------------- #

class _FakeShare:
    def __init__(self, tmp: Path):
        import nas_upload as NU
        self.NU, self.tmp = NU, tmp
        self.root = tmp / "nas" / "02_Data_Sleep"

    def __enter__(self):
        NU = self.NU
        self.real = (NU.require_nas, NU.user_dir, NU.MANIFEST)
        NU.require_nas = lambda: {"ok": True}
        NU.user_dir = lambda u: self.root / u
        NU.MANIFEST = self.tmp / "uploads.jsonl"    # NEVER the real one: a fake
                                                    # VERIFIED row makes the uploader
                                                    # skip a real file later
        return NU

    def __exit__(self, *a):
        self.NU.require_nas, self.NU.user_dir, self.NU.MANIFEST = self.real


def _csv(tmp: Path, name="20260921_HLBSSL31_R.csv") -> Path:
    p = tmp / "local" / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("timestamp_raw,timestamp_sec,datetime_kst,EEG,EMG\n1,0.000,x,1.000,2.000\n")
    return p


def t_upload_lands_in_the_per_mouse_tree(tmp: Path):
    import hashlib, json
    src = _csv(tmp)
    e = naming.mouse_entry(date_yyyymmdd="20260921", batch="HLBSSL", mouse_id="HLBSSL31",
                           rtype="recovery", cfg=CFG)
    with _FakeShare(tmp) as NU:
        out = NU.upload_mouse(src, "andrea", e, {"mouseID": "HLBSSL31"},
                              expect_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
                              progress=None)
        root = tmp / "nas" / "02_Data_Sleep"
    got = sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())
    assert got == ["andrea/HLBSSL/Recovery/20260921_HLBSSL31_R/20260921_HLBSSL31_R.csv",
                   "andrea/HLBSSL/Recovery/20260921_HLBSSL31_R/20260921_HLBSSL31_R.info.json"], got
    info = json.loads((root / "andrea/HLBSSL/Recovery/20260921_HLBSSL31_R/"
                       "20260921_HLBSSL31_R.info.json").read_text())
    assert info["mouseID"] == "HLBSSL31" and info["upload"]["status"] == "VERIFIED", info
    assert info["upload"]["sha256_remote"] == info["upload"]["sha256_local"]
    assert out["upload"]["status"] == "VERIFIED"


def t_a_changed_csv_is_refused_by_hash(tmp: Path):
    src = _csv(tmp)
    e = naming.mouse_entry(date_yyyymmdd="20260921", batch="HLBSSL", mouse_id="HLBSSL31",
                           rtype="recovery", cfg=CFG)
    with _FakeShare(tmp) as NU:
        try:
            NU.upload_mouse(src, "andrea", e, {}, expect_sha256="0" * 64, progress=None)
        except NU.UploadFailed:
            pass
        else:
            raise AssertionError("a CSV whose hash differs from the exporter's was accepted")
        dest = tmp / "nas/02_Data_Sleep/andrea/HLBSSL/Recovery/20260921_HLBSSL31_R"
        assert not (dest / "20260921_HLBSSL31_R.info.json").exists(), \
            "info.json was written for an unverified CSV"


def t_second_folder_for_a_mouse_gets_a_suffix(tmp: Path):
    e = naming.mouse_entry(date_yyyymmdd="20260921", batch="HLBSSL", mouse_id="HLBSSL31",
                           rtype="recovery", cfg=CFG)
    with _FakeShare(tmp) as NU:
        assert NU.free_mouse_folder("andrea", e)["folder"] == "20260921_HLBSSL31_R"
        NU.mouse_dir("andrea", e).mkdir(parents=True)
        f2 = NU.free_mouse_folder("andrea", e)
    assert f2["folder"] == f2["file_base"] == "20260921_HLBSSL31_R-2", f2
    assert f2["rel"] == "HLBSSL/Recovery/20260921_HLBSSL31_R-2" and f2.get("suffix_reason")


def t_a_verified_row_is_not_believed_over_the_share(tmp: Path):
    """A manifest row must never stop an upload of a file that is not there.

    Found 2026-09-15: four folders of test data were tidied off the NAS and the
    manifest still swore every file was verified. The manifest is a CLAIM about
    the share, so it is checked against the share before it is believed.
    """
    src = _csv(tmp)
    e = naming.mouse_entry(date_yyyymmdd="20260921", batch="HLBSSL", mouse_id="HLBSSL31",
                           rtype="recovery", cfg=CFG)
    with _FakeShare(tmp) as NU:
        NU.upload_mouse(src, "andrea", e, {}, progress=None)
        landed = NU.mouse_dir("andrea", e) / "20260921_HLBSSL31_R.csv"
        assert landed.exists()
        landed.unlink()                       # someone tidies the share
        NU.upload_mouse(src, "andrea", e, {}, progress=None)
        assert landed.exists(), "the deleted file was NOT re-uploaded"
        before = landed.stat().st_mtime_ns
        NU.upload_mouse(src, "andrea", e, {}, progress=None)
        assert landed.stat().st_mtime_ns == before, "an intact file was re-sent"


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

    expect("refuse: a blank batch name, now that the batch is a folder level",
           lambda: naming.mouse_folders(FakeRun(slots=mice(1)), CFG),
           naming.NamingError, "required")
    expect("refuse: require_batch on whitespace",
           lambda: naming.require_batch("   "), naming.NamingError, "required")
    expect("refuse: a run with no occupied slot has no mouse to name",
           lambda: naming.mouse_folders(
               FakeRun(slots={"A1": {"mouse_id": "", "recording_type": "basal"}},
                       batch_name="X"), CFG),
           naming.NamingError, "no occupied slot")
    expect("refuse: a recording type with no code",
           lambda: naming.mouse_folders(
               FakeRun(slots={"A1": {"mouse_id": "M", "recording_type": "nonsense"}},
                       batch_name="X"), CFG),
           P.PresetError, "no code")
    expect("refuse: a name that is not an Allego base",
           lambda: naming.parse_allego_base("allego_portZ_0__uid1028"),
           naming.NamingError, "not an allego base")

    import nas_upload as NU
    for comp in ("..", "a/b", "", "x y"):
        expect(f"refuse: unsafe path component {comp!r}",
               lambda c=comp: NU.mouse_dir("andrea", {"batch": "B", "condition_dir": "Recovery",
                                                      "folder": c}),
               NU.UploadRefused, "unsafe")


def t_allego_base_per_port_and_old():
    """Since 2026-10-28 each port has its own file; old combined names still parse."""
    assert naming.allego_base("b", 0, "1028-18-36-51") == "allego_portB_0__uid1028-18-36-51"
    new = naming.parse_allego_base("allego_portB_0__uid1028-18-36-51_data.xdat")
    assert new == {"base": "allego", "port": "B", "n": 0, "uid": "1028-18-36-51"}, new
    old = naming.parse_allego_base("allego_0__uid0912-08-55-18")
    assert old == {"base": "allego", "port": None, "n": 0, "uid": "0912-08-55-18"}, old
    # the date still comes from the uid, for the per-port name too
    f = naming.mouse_folders(FakeRun(slots={"B1": {"mouse_id": "M1", "recording_type": "basal"}},
                                     batch_name="X",
                                     base_name="allego_portB_3__uid1029-08-55-18",
                                     actual_start="2026-10-28T23:55:18Z"), CFG)
    assert f["B1"]["folder"].startswith("20261029_"), f


def main() -> int:
    import tempfile
    print("NAMING")
    for fn in (t_the_example_from_the_request, t_each_code_and_folder, t_there_is_no_sd_type,
               t_mixed_conditions_file_each_mouse_by_its_own_type, t_empty_slots_are_skipped,
               t_date_is_local_and_from_the_uid, t_suffix_reaches_folder_file_and_path,
               t_preview_matches_the_real_thing, t_allego_base_per_port_and_old):
        check(fn.__name__, fn)
    for fn in (t_config_refuses_a_type_without_a_folder, t_upload_lands_in_the_per_mouse_tree,
               t_a_changed_csv_is_refused_by_hash, t_second_folder_for_a_mouse_gets_a_suffix,
               t_a_verified_row_is_not_believed_over_the_share):
        check(fn.__name__, lambda fn=fn: fn(Path(tempfile.mkdtemp(prefix="naming-"))))
    print("\nMUST REFUSE")
    refusals()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    for n, tb in FAIL:
        print(f"\n--- {n} ---\n{tb}")
    return 1 if FAIL or not PASS else 0


if __name__ == "__main__":
    raise SystemExit(main())
