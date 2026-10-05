"""Refresh the `qc` block inside the 8 noise-series info.json files on the NAS, now that stage 3 has run.

The console wrote each info.json at upload time (21:11 / 09:14), BEFORE stage 3 existed for these runs, so:
  * B1 light phase reads "NOT SCOREABLE: rung 3 INSUFFICIENT, no stage 3 output" although its card now passes rung 3;
  * the NO VERDICT mice lack the `stage3` block that qc_info.HOW_TO_READ tells the reader to look at.
This rebuilds the block with the console's OWN function (eeg-recorder/backend/qc_info.qc_block) from cards made by the
unchanged cards/ladder.py with stage 3 outputs (official code, stage-1 gate) under
~/radix/noise-tests/2026-10-02/official-noise-tests/. Every other field of info.json is left byte-for-byte as it was;
the previous verdict is kept in `qc_refreshed.previous`. The original files are saved first under BACKUP.
Dry run unless --apply. Writes go to a temp file in the same NAS folder, then os.replace; every file is read back
from the share with the page cache dropped and compared.
usage: python3 qc/refresh_nas_qc_2026_10_02.py BACKUP_DIR [--apply]
"""
import datetime as dt, glob, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "eeg-recorder", "backend"))
import qc_info  # noqa: E402

backup, apply = sys.argv[1], "--apply" in sys.argv
OFF = os.path.expanduser("~/radix/noise-tests/2026-10-02/official-noise-tests")
NAS = "/mnt/skimnas/02_Data_Sleep/andrea/noise-tests/Baseline"
RUNS = {"cfdf8ebde0c6": ("allego_0__uid1001-21-00-07", "20261001", "2026-10-01"),
        "8f84e3e62af6": ("allego_0__uid1002-09-16-58", "20261002", "2026-10-02")}
POS = {"A1": "portA-slot1", "A2": "portA-slot2", "B1": "portB-slot1", "B2": "portB-slot2"}
rev = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


def read_back(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)
        data = b""
        while True:
            b = os.read(fd, 1 << 20)
            if not b:
                break
            data += b
        return data
    finally:
        os.close(fd)


os.makedirs(backup, exist_ok=True); changed = 0
for run, (base, ymd, day) in RUNS.items():
    for pos, stem in POS.items():
        card_p = os.path.join(OFF, "cards", f"auto-{run}", f"{base}__{pos}_card.json")
        card = qc_info.load_card(card_p)
        if card is None:
            sys.exit(f"missing card {card_p}")
        s3 = sorted(glob.glob(os.path.join(OFF, "processed", day, f"{stem}_*_features.json")))
        s3 = json.load(open(s3[0])) if len(s3) == 1 else None
        qc = qc_info.qc_block(card, card_path=card_p, judged_on="whole recording")
        if qc["verdict"] != "SCOREABLE" and s3 is not None:          # the block HOW_TO_READ points NO VERDICT readers to
            qc = qc_info.qc_block(card, card_path=card_p, judged_on="whole recording", stage3=s3)
        folder = f"{ymd}_POS-{pos}_B"; info_p = os.path.join(NAS, folder, folder + ".info.json")
        raw = read_back(info_p); info = json.loads(raw)
        bk = os.path.join(backup, folder + ".info.json.as-uploaded")
        if not os.path.exists(bk):
            open(bk, "wb").write(raw)
        old = info.get("qc") or {}
        new = dict(info)
        new["qc"] = qc
        new["qc_refreshed"] = dict(
            utc=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), tool="eeg-emg-analysis/qc/refresh_nas_qc_2026_10_02.py",
            git_rev=rev, why="stage 3 run after the console's upload; card rebuilt by cards/ladder.py with stage 3 outputs "
                              "(official code, stage-1 gate) in ~/radix/noise-tests/2026-10-02/official-noise-tests on e10",
            previous=dict(verdict=old.get("verdict"), why=old.get("why"), card=(old.get("card") or {}).get("path")))
        s3txt = f"  stage3 {qc['stage3']['verdict'][:40]} r {qc['stage3']['r_1min']}" if "stage3" in qc else ""
        print(f"{folder}: {old.get('verdict')} -> {qc['verdict']}  ({qc['why'][:90]}){s3txt}")
        if not apply:
            continue
        tmp = info_p + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(new, fh, indent=1); fh.flush(); os.fsync(fh.fileno())
        os.replace(tmp, info_p)
        got = json.loads(read_back(info_p))
        assert got == json.loads(json.dumps(new)), f"read-back mismatch {info_p}"
        assert {k: v for k, v in got.items() if k not in ("qc", "qc_refreshed")} == \
               {k: v for k, v in info.items() if k not in ("qc", "qc_refreshed")}, f"other fields changed {info_p}"
        changed += 1
print(("APPLIED, read back and verified: " if apply else "DRY RUN, nothing written: ") + f"{changed} file(s)")
