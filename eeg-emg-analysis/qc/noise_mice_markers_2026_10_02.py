"""Canonical event markers for the two 4-mouse noise-series runs of 2026-10-01/02, in EACH FILE'S OWN TIME BASE.

One list, used by every figure and table and copied to the NAS beside the per-mouse CSVs. Supersedes the
light-phase `trials/MARKERS.tsv` written by qc/rig_session_2026_10_02.py (same events, plus the overnight, the
full-scan detections and the air showers, and the exact time base).

Time base. The clock origin is each file's status.start_time (UTC, ms) converted to KST, NOT the uid in the
file name (overnight 21:00:06.832, name says 21:00:07; light phase 09:16:58.153, name says 09:16:58). For each
event the table gives
    file_s         seconds from the file's first sample  == the per-mouse CSV's `timestamp_sec`
    sample         0-based sample index (file_s * fs)    == the CSV row number after the header
    timestamp_raw  Allego's device counter               == the CSV's `timestamp_raw` (every step is 1 in both files)
Clock sources differ in accuracy, and the column `clock_basis` says which applies:
    data      found in the recording itself (all-chip scan, A2-B1 floor coincidence, probe-contact steps), +-0.1 s
    andrea    Andrea's own clock, which ran >= 8 s AHEAD of e10 on 2026-10-02 17:35 (so the true time is earlier)
    allego    read off Allego's screen; ambiguous between stream time and file time (both given)
    console   the recording console's own log (e10 clock, NTP-synced)
usage: python3 qc/noise_mice_markers_2026_10_02.py OUTDIR      -> MARKERS_<run>_<base>.tsv for both runs
"""
import datetime as dt
import json
import os
import sys

RAW = os.environ.get("EEG_RAW_ROOT", "/home/skimlab/radix/data")
KST = dt.timezone(dt.timedelta(hours=9))
RUNS = {"overnight": "allego_0__uid1001-21-00-07", "lightphase": "allego_0__uid1002-09-16-58"}

# (run, start clock KST, end clock or None, kind, event, clock_basis)
# kind: lights | system | disturbance | test | console. "system" = detected on the wire-free floors of several chips.
# A start or end written "@<seconds>" is a position in the FILE (from the scans' t_s, or a file-seconds reading);
# its clock time is computed from the file's own origin; "@end" is the last sample. Plain clock strings are KST.
EVENTS = [
    ("overnight", "@0", None, "console", "overnight run cfdf8ebde0c6 starts (lights went OFF just before)", "console"),
    ("overnight", "@17989.7", None, "system", "small 3-chip floor event (A1 A2 B1 x3-13; below the all-chip bar), cause unknown", "data"),
    ("overnight", "@37655.7", None, "system", "small 3-chip floor event (A1 A2 B1 x5-10), cause unknown", "data"),
    ("overnight", "@42067.0", None, "system", "3-chip floor event (A1 A2 B1 x9-29), cause unknown", "data"),
    ("overnight", "@43184.2", None, "lights", "lights ON (timer); all-chip event, floors x83-86 on port A", "data"),
    ("overnight", "@end", None, "console", "last sample; the console logged the stop (R_ON -> R_OFF) at 09:02:04", "console"),
    ("lightphase", "@0", None, "console", "light-phase run 8f84e3e62af6 starts", "console"),
    ("lightphase", "@21755.5", "@21762.8", "disturbance", "first disturbance of Andrea's visit (4 all-chip events in 8 s); Andrea's message said ~15:35", "data"),
    ("lightphase", "@23619.2", "@23677.7", "test", "multimeter V~200 probe: black on XDAQ chassis GND lug, red on A2's foil; hands at the headstages", "data"),
    ("lightphase", "2026-10-02 16:00:00", "2026-10-02 16:03:00", "test", "presence test: absent (control)", "andrea"),
    ("lightphase", "2026-10-02 16:03:00", "2026-10-02 16:04:00", "test", "presence test: standing 50 cm in front, hand brought close to each headstage (no touch)", "andrea"),
    ("lightphase", "2026-10-02 16:04:00", "2026-10-02 16:05:00", "test", "presence test: absent (control)", "andrea"),
    ("lightphase", "2026-10-02 16:05:00", "2026-10-02 16:06:00", "test", "presence test: in front, waving hands", "andrea"),
    ("lightphase", "2026-10-02 16:06:00", "2026-10-02 16:07:00", "test", "presence test: waving the powered custom wireless EEG/EMG receiver near the headstages", "andrea"),
    ("lightphase", "@25506.4", "@25575", "test", "meter ON: red tip hover/touch on A2's foil, black on chassis lug (4 touches below)", "data"),
    ("lightphase", "@25517", "@25525", "test", "  touch 1 (meter ON)", "data"),
    ("lightphase", "@25536", "@25542", "test", "  touch 2 (meter ON)", "data"),
    ("lightphase", "@25551", "@25558", "test", "  touch 3 (meter ON)", "data"),
    ("lightphase", "@25567", "@25574", "test", "  touch 4 (meter ON)", "data"),
    ("lightphase", "@25803.0", "@25813", "test", "meter OFF: floating red lead touching A2's foil", "data"),
    ("lightphase", "@26192.2", None, "disturbance", "last all-chip event of the visit (end of the visit not logged)", "data"),
    ("lightphase", "@28390.0", None, "system", "all-chip event, all 4 chips x61-133 (strongest of the day), cause unknown", "data"),
    ("lightphase", "2026-10-02 17:22:14", None, "disturbance", "facility air shower ON (Andrea's clock; true time <= 17:22:06)", "andrea"),
    ("lightphase", "2026-10-02 17:23:00", "2026-10-02 17:24:00", "disturbance", "air shower ON again '1 or 2 minutes later' (second not logged)", "andrea"),
    ("lightphase", "@29834.36", None, "disturbance", "air shower ON read off Allego as 29937.4 s, IF Allego shows stream time (file starts at stream 103.04 s)", "allego"),
    ("lightphase", "2026-10-02 17:35:50", None, "disturbance", "air shower ON (Andrea's clock; message reached e10 at <= 17:35:42)", "andrea"),
    ("lightphase", "@29937.4", None, "disturbance", "the same Allego 29937.4 s reading IF Allego shows time since the file started", "allego"),
    ("lightphase", "@32112.3", "@32113.2", "system", "all-chip event (B2 x113, A2 x34), cause unknown", "data"),
    ("lightphase", "@41978.4", None, "system", "3-chip floor event (A1 A2 B1 x6-14), cause unknown", "data"),
    ("lightphase", "@42253.35", None, "lights", "lights OFF (timer); floors A1 x3.8 A2 x4.4 B2 x5.1, B1 x1.2: below the all-chip bar", "data"),
    ("lightphase", "@end", None, "console", "last sample; the console logged the stop (R_ON -> R_OFF) at 21:02:04", "console"),
]
# Disturbed windows for staging sensitivity (DISTURBED = a person or the facility acting on the room).
DISTURBED = [("lightphase", "2026-10-02 15:19:00", "2026-10-02 16:40:00", "Andrea's visit (end not logged; last event 16:33:30)"),
             ("lightphase", "2026-10-02 17:21:30", "2026-10-02 17:27:00", "air showers, first pair"),
             ("lightphase", "2026-10-02 17:34:00", "2026-10-02 17:37:00", "air showers, second pair")]


def file_origin(base):
    """(t0 as an aware KST datetime, fs, n_samples, timestamp_raw_first) from the file's own metadata."""
    st = json.load(open(os.path.join(RAW, base + ".xdat.json")))["status"]
    t0 = dt.datetime.fromisoformat(st["start_time"].replace("Z", "+00:00")).astimezone(KST)
    return t0, float(st["samp_freq"]), int(st["num_smpl"]), int(st["timestamp_range"][0])


def clock(s):
    return dt.datetime.fromisoformat(s).replace(tzinfo=KST)


def rows(run):
    """Marker rows for one run, in that file's time base; refuses events outside the file."""
    base = RUNS[run]; t0, fs, n, raw0 = file_origin(base); out = []
    fsec = lambda c: ((n - 1) / fs if c == "@end" else float(c[1:])) if c.startswith("@") else (clock(c) - t0).total_seconds()
    ck = lambda v: (t0 + dt.timedelta(seconds=v)).strftime("%Y-%m-%d %H:%M:%S.%f")[:-5]
    smp = lambda v: None if v is None else min(max(int(round(v * fs)), 0), n - 1)
    for r, s, e, kind, what, basis in EVENTS:
        if r != run:
            continue
        a = fsec(s); b = fsec(e) if e else None
        for v in (a, b):
            if v is not None and not (-1.0 <= v <= n / fs + 1.0):
                raise ValueError(f"{run}: {s} is outside the file ({v:.1f} s of {n / fs:.1f})")
        out.append(dict(run=run, base=base, clock_kst=ck(a), clock_end_kst="" if b is None else ck(b), kind=kind,
                        event=what, clock_basis=basis, file_s=round(a, 3), file_s_end="" if b is None else round(b, 3),
                        sample=smp(a), sample_end="" if b is None else smp(b),
                        timestamp_raw=raw0 + smp(a), timestamp_raw_end="" if b is None else raw0 + smp(b)))
    return out


def disturbed(run):
    """[(file_s start, file_s end, label)] for one run."""
    t0, _, _, _ = file_origin(RUNS[run])
    return [((clock(a) - t0).total_seconds(), (clock(b) - t0).total_seconds(), lab) for r, a, b, lab in DISTURBED if r == run]


COLS = ["run", "base", "clock_kst", "clock_end_kst", "file_s", "file_s_end", "sample", "sample_end",
        "timestamp_raw", "timestamp_raw_end", "kind", "clock_basis", "event"]

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for run, base in RUNS.items():
        p = os.path.join(out, f"MARKERS_{run}_{base}.tsv")
        with open(p, "w") as fh:
            fh.write("\t".join(COLS) + "\n")
            for r in rows(run):
                fh.write("\t".join(str(r[c]) for c in COLS) + "\n")
            for a, b, lab in disturbed(run):
                fh.write("\t".join(str(x) for x in (run, base, "", "", round(a, 3), round(b, 3), "", "", "", "",
                                                    "disturbed_window", "", lab)) + "\n")
        print(p)
