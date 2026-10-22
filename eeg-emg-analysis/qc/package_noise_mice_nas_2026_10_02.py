"""Assemble the NAS analysis folder for the four noise-series mice (2026-10-01/02) in a local staging directory.

Layout (README.txt is written by hand next to this and copied in; everything else is generated or copied here):
  INDEX.csv                 one row per mouse x run: where its CSV is, what is valid, the official and diagnostic verdicts
  markers/                  canonical event markers per file, in that file's own time base (CSV timestamp_sec / row)
  qc/cards/                 the verdict-ladder cards behind each info.json `qc` block
  qc/info-json-as-uploaded/ each info.json as the console uploaded it, before the 2026-10-02 refresh
  staging/official/         stage 3 (pipeline unchanged, stage-1 gate): A2, B1
  staging/diagnostic/       stage 3 on all four, QC bypassed: as_published/ and emg_notched/
  analysis/                 24 h tables, the archive-wide notch validation, logs of every analysis
  scans/                    full-resolution system-wide event scans, A2-B1 coincidences, splitter, positive control
  figures/                  every figure, as embedded in the vault
  scripts/                  the code that produced all of it, with sha256 and the git state
usage: python3 qc/package_noise_mice_nas_2026_10_02.py STAGE_DIR README.txt
"""
import csv, glob, hashlib, json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import noise_mice_markers_2026_10_02 as MK

ST, README = sys.argv[1], sys.argv[2]
D = os.path.expanduser("~/radix/noise-tests/2026-10-02"); OFF = os.path.join(D, "official-noise-tests"); A24 = os.path.join(D, "analysis-24h")
VAULT_ATT = os.path.join(REPO, "vault", "_attachments"); NAS = "/mnt/skimnas/02_Data_Sleep/andrea/noise-tests/Baseline"
RUNS = {"overnight": ("cfdf8ebde0c6", "2026-10-01", "20261001", "diag-emgtest-overnight"),
        "lightphase": ("8f84e3e62af6", "2026-10-02", "20261002", "diag-emgtest-lightphase")}
POS = {"A1": "portA-slot1", "A2": "portA-slot2", "B1": "portB-slot1", "B2": "portB-slot2"}
ANIMAL = {"A1": "B6/J BomTac female, DOB 2026-04-12, no ID", "A2": "HLBWSL30 (W-SL)", "B1": "HLBSSD20 (S-SD)",
          "B2": "B6/J BomTac female, DOB 2026-04-12, no ID"}
EMG_OK = {"A1": False, "A2": True, "B1": True, "B2": False}
SCRIPTS = ["noise_mice_markers_2026_10_02.py", "noise_mice_24h_2026_10_02.py", "emg_notch_validation_2026_10_02.py",
           "emg_mains_staging_test.py", "allchip_scan_file.py", "allchip_events.py", "night_spikes.py", "splitter_coincidence.py",
           "air_shower_2026_10_02.py", "presence_test_2026_10_02.py", "rig_session_2026_10_02.py", "fullscan_figures_2026_10_02.py",
           "noise_figures_2026_10_02.py", "refresh_nas_qc_2026_10_02.py", "nas_copy_verified.py", "package_noise_mice_nas_2026_10_02.py"]


def cp(src, dst_dir, name=None):
    os.makedirs(dst_dir, exist_ok=True); shutil.copy2(src, os.path.join(dst_dir, name or os.path.basename(src)))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


if os.path.exists(ST):
    shutil.rmtree(ST)
os.makedirs(ST)
cp(README, ST, "README.txt")
# markers
for run, base in MK.RUNS.items():
    p = os.path.join(ST, "markers", f"MARKERS_{run}_{base}.tsv"); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as fh:
        fh.write("\t".join(MK.COLS) + "\n")
        for r in MK.rows(run):
            fh.write("\t".join(str(r[c]) for c in MK.COLS) + "\n")
        for a, b, lab in MK.disturbed(run):
            fh.write("\t".join(str(x) for x in (run, base, "", "", round(a, 3), round(b, 3), "", "", "", "", "disturbed_window", "", lab)) + "\n")
# qc
for run, (rid, day, ymd, diag) in RUNS.items():
    for f in glob.glob(os.path.join(OFF, "cards", f"auto-{rid}", "*.json")):
        cp(f, os.path.join(ST, "qc", "cards", f"auto-{rid}"))
for f in glob.glob(os.path.join(A24, "info-json-as-uploaded", "*")):
    cp(f, os.path.join(ST, "qc", "info-json-as-uploaded"))
# staging outputs
for run, (rid, day, ymd, diag) in RUNS.items():
    for f in glob.glob(os.path.join(OFF, "processed", day, "port*_*")):
        if f.endswith((".csv", ".json", ".txt")):
            cp(f, os.path.join(ST, "staging", "official", run))
    for cond, name in (("orig", "as_published"), ("notch", "emg_notched")):
        for f in glob.glob(os.path.join(D, diag, cond, day, "port*_*")):
            if f.endswith((".csv", ".json", ".txt")):
                cp(f, os.path.join(ST, "staging", "diagnostic", run, name))
# analysis tables and logs
for f in ("staging_summary.csv", "hourly.csv", "light_dark_summary.json", "disturbance.csv"):
    cp(os.path.join(A24, f), os.path.join(ST, "analysis", "24h"))
for f in glob.glob(os.path.join(A24, "logs", "*.log")):
    cp(f, os.path.join(ST, "analysis", "logs"))
MT = os.path.join(D, "emg-mains-test-all")
for f in ("notch_validation.csv", "notch_validation_summary.json"):
    cp(os.path.join(MT, f), os.path.join(ST, "analysis", "emg-notch-validation-whole-archive"))
cp(os.path.join(D, "fullscans", "emg_mains_all_days.log"), os.path.join(ST, "analysis", "emg-notch-validation-whole-archive"))
# scans
for f in glob.glob(os.path.join(D, "fullscans-v2", "*")):
    if f.endswith((".csv", ".log")):
        cp(f, os.path.join(ST, "scans"))
# figures
for f in sorted(glob.glob(os.path.join(VAULT_ATT, "2026-10-02-noise-fig*.png"))):
    cp(f, os.path.join(ST, "figures"))
# scripts + git state
for s in SCRIPTS:
    cp(os.path.join(HERE, s), os.path.join(ST, "scripts"))
cp(os.path.join(REPO, "eeg-emg-analysis", "pipeline", "stage1_qc.py"), os.path.join(ST, "scripts", "pipeline"))
git = lambda *a: subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True).stdout.strip()
with open(os.path.join(ST, "scripts", "GIT_STATE.txt"), "w") as fh:
    fh.write(f"repository sleep-recording-skim, HEAD {git('rev-parse', 'HEAD')} ({git('log', '-1', '--format=%cd %s')})\n")
    fh.write("These scripts are NOT committed yet (2026-10-02); the copies here are the exact versions that produced this folder.\n")
    fh.write("core/ and cards/ are unchanged on HEAD. pipeline/stage1_qc.py carries one fix (cache path, see README).\n\n")
    fh.write("git status of the files used:\n" + git("status", "--short", "--", "eeg-emg-analysis/qc", "eeg-emg-analysis/pipeline",
                                                    "eeg-emg-analysis/tests") + "\n\nsha256:\n")
    for f in sorted(glob.glob(os.path.join(ST, "scripts", "**", "*.py"), recursive=True)):
        fh.write(f"{sha(f)}  {os.path.relpath(f, ST)}\n")
# INDEX.csv
s24 = {(r["mouse"], r["run"], r["condition"]): r for r in csv.DictReader(open(os.path.join(A24, "staging_summary.csv")))}
hr = list(csv.DictReader(open(os.path.join(A24, "hourly.csv"))))
med = lambda m, key, lit: (lambda v: round(sorted(v)[len(v) // 2], 3) if v else "")(
    [float(r[key]) for r in hr if r["mouse"] == m and r["light"] == str(lit) and r.get(key, "") != ""])
rows = []
for run, (rid, day, ymd, diag) in RUNS.items():
    for m, pos in POS.items():
        folder = f"{ymd}_POS-{m}_B"; info = json.load(open(os.path.join(NAS, folder, folder + ".info.json"))); q = info["qc"]
        lit = 1 if run == "lightphase" else 0
        g = lambda cond, k: (s24.get((m, run, cond)) or {}).get(k, "")
        fl, e60 = med(m, "floor60_uv", lit), med(m, "eeg60_uv", lit)
        rows.append(dict(slot=m, animal=ANIMAL[m], run=run, console_run=rid, nas_folder=f"Baseline/{folder}", csv=folder + ".csv",
                         start_kst=info["startTime_kst"], hours=info["duration_h"], eeg=info["channels"]["eeg"], emg=info["channels"]["emg"],
                         emg_status="ok" if EMG_OK[m] else "OPEN (implant side): EEG only",
                         official_verdict=q["verdict"], official_why=q["why"], stage3_official_r_1min=g("official", "r_1min"),
                         diag_r_1min_as_published=g("orig", "r_1min"), diag_r_1min_emg_notched=g("notch", "r_1min"),
                         diag_wake_pct_as_published=g("orig", "wake_pct"), diag_wake_pct_emg_notched=g("notch", "wake_pct"),
                         chip_floor60_uv_hourly_median=fl, eeg60_uv_hourly_median=e60,
                         eeg60_over_own_floor=round(e60 / fl, 4) if fl and e60 else "",
                         markers=f"markers/MARKERS_{run}_{MK.RUNS[run]}.tsv"))
with open(os.path.join(ST, "INDEX.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
n = sum(len(fs) for _, _, fs in os.walk(ST)); size = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(ST) for f in fs)
print(f"staged {n} files, {size / 1e6:.1f} MB in {ST}")
