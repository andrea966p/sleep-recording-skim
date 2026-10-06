#!/usr/bin/env python3
"""Rescue borderline EMGs: muscle power measured only BETWEEN the 60 Hz harmonics, from the raw 1000 Hz file. 2026-10-06.

WHY. Every S-SD mouse fails rung 3 on its EMG. Stage 3 reads EMG as rms over 10-124 Hz of the 250 Hz stage-2 copy,
which holds 60 and 120 Hz. A lead carrying 400-1400 uV of mains, or a connected lead whose muscle signal is small
next to its mains (HLBSSD18), shows no wake/sleep contrast there. Muscle power runs up to the 475 Hz hardware
corner, and between the harmonics there is no mains by construction.

  extract (e10)  per 4 s epoch of every mouse-window: Blackman-Harris Welch PSD (1 Hz) of the RAW 1000 Hz EMG, power
                 in the eight gaps between harmonics (7 Hz clear of every 60 Hz multiple) and at the harmonics;
                 rung 2's own EEG mask and the EMG-not-railed mask (10 s QC epochs mapped onto the 4 s grid).
  stage   (e10)  stage 3 UNCHANGED on every stage-2 window file, two inputs swapped in memory: emg_rms := sqrt(power
                 in the gaps 67-470 Hz) ['gap67', primary; 'gap10' = 10-470 Hz, sensitivity] and epoch_ok/blocks :=
                 the gate (see usage). 'shuffle' = gap67 permuted within blocks, the negative control. Outputs land
                 beside symlinks in OUT/staged-<gate>/<variant>/<day>/; nothing official is written.
  analyse        agreement with the official and notched staging where the EMG already worked, then the 2x2 over
                 every mouse with an EEG connection (longest EEG block >= 15 min, rung 2's EEG mask) that is gap67
                 SCOREABLE and whose shuffle control is not.

usage: python3 qc/emg_rescue_2026_10_06.py extract OUT
       python3 qc/emg_rescue_2026_10_06.py stage|analyse|measures OUT [stage1|eegmask]
  stage1 (default): stage 1's own 4 s gate minus its EMG-mains clause. eegmask: rung 2's EEG mask (first run;
  it fragments windows whose EEG fails the slope test in scattered epochs, which depresses r@1min).
       python3 qc/emg_rescue_2026_10_06.py extract-sd|stage-max|analyse-max OUT
  MAXIMUM RESCUE of W-SD and S-SD: every position, gates {stage1, norail (no mains clause at all)} x EMG
  filters {gap67, gap10, gaplow 10-113 Hz, gaphigh 127-470 Hz, floor67 = minus the chip's wire-free inputs},
  each with its own shuffle control; a filter is used only if it reproduces the notched staging (kappa >= 0.8);
  per window the first passing filter in that fixed order is taken. Only railing or flat epochs are excluded.
"""
import glob, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
CARDS = os.path.join(HERE, "..", "cards", "out-windows")
OFFICIAL_WIN = os.path.expanduser(os.environ.get("OFFICIAL_WIN", "~/eeg-processed-windows"))  # copies elsewhere
NOTCH_WIN = os.path.expanduser(os.environ.get("NOTCH_WIN", "~/eeg-notch-windows-2026-10-06/notch"))
NEW_BASES = ("allego_0__uid0825-09-00-00", "allego_2__uid0902-13-00-28",  # stage 2 --all-verdicts in OUT/whole
             "allego_0__uid0910-09-00-00", "allego_0__uid0912-08-55-18", "allego_2__uid0827-12-58-32")
GAPS = [(10, 53), (67, 113), (127, 173), (187, 233), (247, 293), (307, 353), (367, 413), (427, 470)]
HARM = [60 * k for k in range(1, 8)]
VARIANTS = {"gap67": slice(1, None), "gap10": slice(0, None), "shuffle": slice(1, None)}
# max-rescue: every validated filter, tried in this fixed order, each with its own shuffle control
MAX_VARIANTS = {"gap67": slice(1, None), "gap10": slice(0, None), "gaplow": slice(0, 2), "gaphigh": slice(2, None),
                "floor67": slice(1, None)}
MAX_GATES = ("stage1", "norail")


def cards():
    out = []
    for f in sorted(glob.glob(os.path.join(CARDS, "*", "*_card.json"))):
        c = json.load(open(f)); out.append((c, {x["number"]: x for x in c["rungs"]}))
    first = {}
    for c, _ in out:
        first[c["cohort_id"]] = min(first.get(c["cohort_id"], "9"), c["window"]["start_kst"])
    for c, _ in out:  # the earlier window of each batch is its baseline
        c["tp"] = "B" if c["window"]["start_kst"] == first[c["cohort_id"]] else "R"
    return out


def window_files(out):
    """{(recording, position): stage-2 window npz}; the all-verdicts split wins where both exist."""
    files = {}
    for root in (OFFICIAL_WIN, os.path.join(out, "windows")):
        for f in sorted(glob.glob(os.path.join(root, "20*", "port*.npz"))):
            m = json.loads(str(np.load(f, allow_pickle=True)["meta"]))
            files[(m["recording"], f"{m['port']}{m['slot']}")] = f
    return files


def emg_bands(x, fs):
    """x: (n_epochs, samples) raw EMG -> (gap power, harmonic power), uV^2, per epoch."""
    import scipy.signal as sg
    fr, p = sg.welch(x, fs, window="blackmanharris", nperseg=fs, noverlap=fs // 2, axis=1)
    band = lambda lo, hi: p[:, (fr >= lo) & (fr <= hi)].sum(1) * (fr[1] - fr[0])
    return (np.stack([band(lo, hi) for lo, hi in GAPS], 1).astype(np.float32),
            np.stack([band(h - 2, h + 2) for h in HARM], 1).astype(np.float32))


def extract(out, only=None, floor=False, dest="emg"):
    os.environ["EEG_PROCESSED_ROOT"] = os.path.join(out, "whole")
    os.environ["EEG_WINDOW_PROCESSED_ROOT"] = os.path.join(out, "windows")
    from core import criteria as C, paths as PATHS
    from cards import window_recheck as W
    from cohorts.load import load_cohort
    import pipeline.pipeline_common as P

    cc = cards()
    wins = sorted({(c["recording"], c["window"]["start_kst"], c["window"]["end_kst"], c["cohort_id"]) for c, _ in cc
                   if not only or c["cohort_id"] in only})
    for base, s, e, _ in wins:
        if base in NEW_BASES and not glob.glob(os.path.join(out, "windows", s[:10], "port*.npz")):
            W.slice_stage2(base, W._kst(s), W._kst(e))
    files = window_files(out)
    os.makedirs(os.path.join(out, dest), exist_ok=True)
    from core import qc_thresholds as T
    for base, s, e, cohort in wins:
        meta = P.load_meta(base); info = P.recording_info(base, meta)
        labels, _, emg_cols = P.derive_layout(meta)
        spec = load_cohort(cohort, None, verbose=False).to_spec()
        site_col = {lab: k for k, lab in enumerate(C.open_xdat(os.path.join(P.DATA_DIR, base))[1])}
        fl = {f"{l['port']}{l['slot']}": [site_col[x] for x in C.floor_sites_of(spec, f"{l['port']}{l['slot']}")]
              for l in labels} if floor else {}
        fcols = sorted({c for v in fl.values() for c in v})
        fs, N, NC = info["fs"], info["n_samp"], info["n_chan"]
        assert fs == 1000, fs
        any_f = next(f for (b, _), f in files.items() if b == base and s[:10] in f)
        a4, b4 = json.loads(str(np.load(any_f, allow_pickle=True)["meta"]))["window"]["epochs"]
        ep = 4 * fs
        gaps = np.zeros((len(labels), b4 - a4, len(GAPS)), np.float32)
        harm = np.zeros((len(labels), b4 - a4, len(HARM)), np.float32)
        rail = np.zeros((len(labels), b4 - a4), np.float32)
        fgaps = np.zeros((len(fcols), b4 - a4, len(GAPS)), np.float32)
        mm = np.memmap(os.path.join(P.DATA_DIR, base + "_data.xdat"), dtype="<f4", mode="r", shape=(N, NC))
        step = 150  # epochs = 10 min per read; columns indexed directly, as stage 2 does
        for k in range(a4, b4, step):
            k1 = min(k + step, b4)
            chunk = np.asarray(mm[k * ep:k1 * ep, list(emg_cols) + fcols], dtype=np.float64).T
            for i in range(len(labels)):
                x = chunk[i].reshape(k1 - k, ep)
                gaps[i, k - a4:k1 - a4], harm[i, k - a4:k1 - a4] = emg_bands(x, fs)
                rail[i, k - a4:k1 - a4] = (np.abs(x) >= T.RAIL_UV_EFF).mean(1)
            for i in range(len(fcols)):
                fgaps[i, k - a4:k1 - a4] = emg_bands(chunk[len(labels) + i].reshape(k1 - k, ep), fs)[0]
            print(f"  {base} {100 * (k1 - a4) / (b4 - a4):5.1f}%", end="\r", flush=True)
        del mm
        ws, we = W._kst(s), W._kst(e)
        q = np.load(PATHS.CACHE_ROOT / "windows" / f"{base}__{ws:%Y%m%dT%H%M}-{we:%Y%m%dT%H%M}.npz", allow_pickle=True)
        feat = C.EpochFeatures(base=base, fs=int(q["fs"]), epoch_s=int(q["epoch_s"]), n_epochs=int(q["n_epochs"]),
                               n_samples=int(q["n_samples"]), sites=list(q["sites"]), spec=spec, hum=q["hum"],
                               rms=q["rms"], rail=q["rail"], slope=q["slope"], delta=q["delta"], lfhf=q["lfhf"])
        for i, lab in enumerate(labels):
            pos = f"{lab['port']}{lab['slot']}"
            c, r = next((c, r) for c, r in cc if c["recording"] == base and c["window"]["start_kst"] == s
                        and c["position"] == pos)
            if r[2]["verdict"] == "UNJUDGEABLE":  # no valid wire-free control on this chip: no EEG mask
                m10 = np.zeros(feat.n_epochs, bool)
            else:  # rung 2's own EEG mask; must reproduce the card's EEG fraction exactly
                m10 = C.usable(feat, spec.animal_sites()[pos]["eeg"], C.floor_stats(feat, pos), "slope",
                               role="eeg", allow_refused=True)
                assert abs(m10.mean() - r[2]["detail"]["per_role"]["eeg"]["usable_fraction"]) < 1e-9, (base, pos)
            rail10 = feat.rail[:, feat.col(spec.animal_sites()[pos]["emg"])] > 0
            j = ((a4 + np.arange(b4 - a4)) * 4 + 2) // 10 - c["window"]["qc_epochs"][0]
            inside = (j >= 0) & (j < feat.n_epochs); j = np.clip(j, 0, feat.n_epochs - 1)
            fg = (np.median(fgaps[[fcols.index(x) for x in fl[pos]]], 0) if fl.get(pos)
                  else np.full_like(gaps[i], np.nan))  # the chip's own wire-free inputs, median per epoch and gap
            np.savez_compressed(os.path.join(out, dest, f"{cohort}_{c['tp']}_{pos}_{c['animal_id']}.npz"),
                                cohort=cohort, tp=c["tp"], pos=pos, animal=c["animal_id"], recording=base,
                                gaps=gaps[i], harm=harm[i], eeg_ok=inside & m10[j], emg_ok=inside & ~rail10[j],
                                emg_rail=rail[i], floor_gaps=fg, npz=files.get((base, pos), ""))
        print(f"  {base}: {len(labels)} mice, {b4 - a4} epochs" + " " * 20)


def stage1_gate(base, pos, a4, n):
    """Stage 1's own QC gate (pipeline/stage1_qc.gate) on the same 4 s grid, WITHOUT its EMG-mains clause:
    the gap measure excludes mains by construction, and that clause is what drops every mains-dominated lead."""
    import pipeline.stage1_qc as S1
    from core import qc_thresholds as T
    d = S1.extract_features(base)  # cached in ~/eeg-qc-cache
    i = next(k for k, lab in enumerate(d["labels"]) if f"{lab['port']}{lab['slot']}" == pos)
    ok = ((d["eeg_mains"][:, i] < T.OPEN_UV) & (d["eeg_rms"][:, i] >= T.FLAT_UV) & (d["eeg_clip"][:, i] <= T.CLIP_FRAC)
          & (d["delta"][:, i] > 0) & (d["theta"][:, i] > 0))
    return ok[a4:a4 + n]


class _NpzDict(dict):
    files = property(lambda self: list(self.keys()))


def run_stage3(npz, gate, blocks, emg, od):
    """stage 3, unchanged, on a symlink of `npz` in `od`, with epoch_ok/blocks and emg_rms swapped in memory."""
    import pipeline.stage3_features as S3
    real_load, real_feat = np.load, S3.epoch_features
    os.makedirs(od, exist_ok=True)
    link = os.path.join(od, os.path.basename(npz))
    if not os.path.lexists(link):
        os.symlink(os.path.realpath(npz), link)

    def load(path, allow_pickle=True, **kw):
        z = real_load(path, allow_pickle=allow_pickle, **kw)
        d = _NpzDict({k: z[k] for k in z.files}); d["epoch_ok"], d["blocks"] = gate, blocks
        return d

    def feats(eeg, emg_sig, fs):
        fe = real_feat(eeg, emg_sig, fs)
        assert fe["n"] == len(emg), (npz, fe["n"], len(emg))
        return {**fe, "emg_rms": emg}

    S3.np.load, S3.epoch_features = load, feats  # S3.np IS numpy: restored in finally
    try:
        return S3.analyse(link), link
    finally:
        S3.np.load, S3.epoch_features = real_load, real_feat


def shuffled(x, blocks, seed=0):
    rng, x = np.random.default_rng(seed), x.copy()
    for a, b in blocks:
        x[a:b] = rng.permutation(x[a:b])
    return x


def stage(out, gate_kind="stage1"):
    import pipeline.pipeline_common as P
    from core import qc_thresholds as T
    root = os.path.join(out, f"staged-{gate_kind}")
    rows = []
    for f in sorted(glob.glob(os.path.join(out, "emg", "*.npz"))):
        e = {k: v[()] if v.shape == () else v for k, v in np.load(f, allow_pickle=True).items()}
        if not e["npz"]:
            continue
        if gate_kind == "eegmask":  # rung 2's EEG mask: stricter per epoch, fragments some windows
            gate = e["eeg_ok"] & e["emg_ok"]
        else:
            a4 = json.loads(str(np.load(str(e["npz"]), allow_pickle=True)["meta"]))["window"]["epochs"][0]
            gate = stage1_gate(str(e["recording"]), str(e["pos"]), a4, len(e["gaps"])) & e["emg_ok"]
        blocks = np.array([b for b in P.blocks_of(gate) if b[1] - b[0] >= T.MIN_BLOCK], np.int64).reshape(-1, 2)
        for var, sl in VARIANTS.items():
            emg = np.sqrt(e["gaps"][:, sl].sum(1))
            if var == "shuffle":
                emg = shuffled(emg, blocks)
            day = os.path.basename(os.path.dirname(str(e["npz"])))
            res, link = run_stage3(str(e["npz"]), gate, blocks, emg, os.path.join(root, var, day))
            rows.append((str(e["cohort"]), str(e["tp"]), str(e["animal"]), var, res["verdict"].split(":")[0],
                         res["persistence"]["1min"]["r"], res["wake_pct"], res["hours_in_blocks"],
                         res.get("physiology_informative_pass"), os.path.join(var, day, os.path.basename(link))))
    json.dump(rows, open(os.path.join(root, "summary.json"), "w"), indent=0)
    print(f"{'batch':<5} tp {'mouse':<9} {'variant':<8} {'verdict':<10} r@1min  wake%  h-in-blocks  informative-physiology")
    for r in rows:
        print(f"{r[0]:<5} {r[1]}  {r[2]:<9} {r[3]:<8} {r[4]:<10} {r[5] if r[5] is None else round(r[5], 3)!s:>6} "
              f"{r[6]:6.1f} {r[7]:8.2f}     {r[8]}")


def gate_of(kind, e):
    """stage1: stage 1's gate minus its EMG-mains clause. norail: EEG not clipped, not flat; nothing about mains."""
    import pipeline.stage1_qc as S1
    from core import qc_thresholds as T
    a4 = json.loads(str(np.load(str(e["npz"]), allow_pickle=True)["meta"]))["window"]["epochs"][0]
    n, base, pos = len(e["gaps"]), str(e["recording"]), str(e["pos"])
    if kind == "stage1":
        g = stage1_gate(base, pos, a4, n)
    else:
        d = S1.extract_features(base)
        i = next(k for k, lab in enumerate(d["labels"]) if f"{lab['port']}{lab['slot']}" == pos)
        g = ((d["eeg_rms"][:, i] >= T.FLAT_UV) & (d["eeg_clip"][:, i] <= T.CLIP_FRAC)
             & (d["delta"][:, i] > 0) & (d["theta"][:, i] > 0))[a4:a4 + n]
    return g & (e["emg_rail"] == 0)


def emg_of(var, e):
    sl = MAX_VARIANTS[var]
    if var == "floor67":  # what the chip's wire-free inputs also see is not muscle: subtract it, per epoch and gap
        x = np.clip(e["gaps"][:, sl] - e["floor_gaps"][:, sl], 0, None).sum(1)
        return np.sqrt(x + 0.01 * np.median(x[x > 0]) if np.any(x > 0) else x + 1e-6)
    return np.sqrt(e["gaps"][:, sl].sum(1))


def stage_max(out, src="emg-sd", validate_src="emg"):
    """Every SD mouse-window x MAX_GATES x MAX_VARIANTS, each with its own shuffle control; plus the validation runs
    of each variant on windows whose EMG already worked (stage1 gate, all batches; floor67 only where floors exist)."""
    import pipeline.pipeline_common as P
    from core import qc_thresholds as T
    root, rows = os.path.join(out, "staged-max"), []

    def one(e, kind, var, ctrl):
        gate = gate_of(kind, e)
        blocks = np.array([b for b in P.blocks_of(gate) if b[1] - b[0] >= T.MIN_BLOCK], np.int64).reshape(-1, 2)
        emg = emg_of(var, e)
        if ctrl:
            emg = shuffled(emg, blocks)
        day = os.path.basename(os.path.dirname(str(e["npz"])))
        tag = f"{kind}/{var}{'-shuffle' if ctrl else ''}"
        res, link = run_stage3(str(e["npz"]), gate, blocks, emg, os.path.join(root, tag, day))
        rows.append((str(e["cohort"]), str(e["tp"]), str(e["animal"]), kind, var, ctrl, res["verdict"].split(":")[0],
                     res["persistence"]["1min"]["r"], res["wake_pct"], res["hours_in_blocks"],
                     os.path.join(tag, day, os.path.basename(link))))

    load = lambda f: {k: v[()] if v.shape == () else v for k, v in np.load(f, allow_pickle=True).items()}
    for f in sorted(glob.glob(os.path.join(out, src, "*.npz"))):
        e = load(f)
        if e["npz"]:
            for kind in MAX_GATES:
                for var in MAX_VARIANTS:
                    one(e, kind, var, False); one(e, kind, var, True)
        print(f"  {os.path.basename(f)} done", flush=True)
    for f in sorted(glob.glob(os.path.join(out, validate_src, "*.npz"))):  # validation of the floor-free variants
        e = load(f)
        if e["npz"] and str(e["cohort"]) in ("W-SL", "S-SL"):
            e["emg_rail"] = np.where(e["emg_ok"], 0, 1)  # first extract had the 10 s QC rail mask only
            for var in ("gaplow", "gaphigh"):
                one(e, "stage1", var, False)
    json.dump(rows, open(os.path.join(root, "summary.json"), "w"), indent=0)


def analyse(out, gate_kind="stage1"):
    """OUT holds staged-<gate>/summary.json and the staged hypnograms (rsync from e10)."""
    import sod_sleep_2x2_2026_10_06 as M  # sleep_pct, compare, SEGS, ARM
    root = os.path.join(out, f"staged-{gate_kind}")
    rows = json.load(open(os.path.join(root, "summary.json")))
    st = {(r[0], r[1], r[2], r[3]): r for r in rows}
    hyp = lambda r: os.path.join(root, r[9][:-4] + "_hypnogram.csv")

    def labels(path):
        import csv
        with open(path) as fh:
            x = [(row["state"], row["in_block"] == "1") for row in csv.DictReader(fh)]
        return np.array([s for s, _ in x]), np.array([b for _, b in x])

    print("=== 1. does the new EMG measure agree with the staging where the EMG already worked? (sleep vs wake kappa)")
    for ref, ref_root in (("official", OFFICIAL_WIN), ("notched", NOTCH_WIN)):
        ks = []
        for r in rows:
            if r[3] != "gap67":
                continue
            rp = os.path.join(ref_root, os.path.basename(os.path.dirname(r[9])), os.path.basename(r[9])[:-4])
            if not os.path.exists(rp + "_features.json") or \
                    json.load(open(rp + "_features.json"))["verdict"].split(":")[0] != "SCOREABLE":
                continue
            a, ia = labels(hyp(r)); b, ib = labels(rp + "_hypnogram.csv")
            m = ia & ib & (a != "EXCLUDED") & (b != "EXCLUDED")
            x, y = a[m] != "WAKE", b[m] != "WAKE"
            pe = x.mean() * y.mean() + (1 - x.mean()) * (1 - y.mean())
            ks.append(((np.mean(x == y) - pe) / (1 - pe), r[2], r[1], 100 * (1 - x.mean()), 100 * (1 - y.mean())))
        ks.sort()
        print(f"  vs {ref:<8} n={len(ks):2d} windows, kappa median {np.median([k[0] for k in ks]):.2f} "
              f"(min {ks[0][0]:.2f} {ks[0][1]} {ks[0][2]}); wake % new - {ref}: median "
              f"{np.median([k[3] - k[4] for k in ks]):+.1f} pts")

    eeg_conn = eeg_connected()

    print("\n=== 2. per mouse-window: gap67 (primary) | gap10 | shuffle control   (EEG = rung-2 EEG connection)")
    use, tsv = {}, []
    for key in sorted({k[:3] for k in st}):
        g, g10, sh = (st.get(key + (v,)) for v in ("gap67", "gap10", "shuffle"))
        fmt = lambda r: "-" if r is None else f"{r[4][:6]:<6} r {r[5] if r[5] is None else round(r[5], 2)!s:>5} wake {r[6]:5.1f}"
        ok = eeg_conn.get(key, False) and g is not None and g[4] == "SCOREABLE" and (sh is None or sh[4] != "SCOREABLE")
        print(f"  {key[0]} {key[1]} {key[2]:<9} EEG {'ok ' if eeg_conn.get(key) else 'NO '} {fmt(g)} | {fmt(g10)} | "
              f"{fmt(sh)}{'   <- in' if ok else ''}")
        if ok:
            use[key] = M.sleep_pct(hyp(g))[0]
        if g is not None:
            tsv.append([*key, int(eeg_conn.get(key, False)), g[4], g[5], round(g[6], 1),
                        sh[4] if sh else "", int(ok), *(f"{v[0]:.2f}" for v in M.sleep_pct(hyp(g))[0].values())])
    with open(os.path.join(out, f"emg_rescue_{gate_kind}_per_mouse.tsv"), "w") as fh:
        fh.write("batch\ttimepoint\tanimal\teeg_connected\tgap67_verdict\tr1min\twake_pct\tshuffle_verdict\tincluded\t"
                 + "\t".join(f"sleep_{k}" for k in M.SEGS) + "\n")
        fh.writelines("\t".join(map(str, row)) + "\n" for row in tsv)

    def val(batch, tp, k):
        return {a: s[k][0] for (b, t, a), s in use.items() if b == batch and t == tp and not np.isnan(s[k][0])}

    def delta(batch, k):
        b, r = val(batch, "B", k), val(batch, "R", k)
        return {a: r[a] - b[a] for a in b if a in r}

    print("\n=== 3. 2x2 on sleep % (NREM + REM), every mouse staged with the same EMG measure")
    for b in M.ARM:
        print(f"  {b} {M.ARM[b][0]:>5} {M.ARM[b][1]:<6} B={len(val(b, 'B', '24h'))} R={len(val(b, 'R', 'ZT4-24'))} "
              f"paired={sorted(delta(b, 'ZT4-24'))}")
    for k in ("ZT4-24", "L4-12", "D12-24"):
        print(f"  change {k}: " + "   ".join(f"{b} " + ", ".join(f"{a} {v:+.1f}" for a, v in sorted(delta(b, k).items()))
                                          for b in M.ARM if delta(b, k)))
        M.compare(f"SOD1 effect under CSD {k}", delta("S-SD", k), delta("W-SD", k), "S-SD", "W-SD")
        M.compare(f"CSD effect, SOD1 {k}", delta("S-SD", k), delta("S-SL", k), "S-SD", "S-SL")
        M.compare(f"CSD effect, water {k}", delta("W-SD", k), delta("W-SL", k), "W-SD", "W-SL")
        M.compare(f"SOD1 effect, ad lib {k}", delta("S-SL", k), delta("W-SL", k), "S-SL", "W-SL")
        dd = [np.mean(list(delta(b, k).values())) if delta(b, k) else np.nan for b in ("S-SD", "S-SL", "W-SD", "W-SL")]
        print(f"  {'interaction (S-SD - S-SL) - (W-SD - W-SL)':<44} {(dd[0] - dd[1]) - (dd[2] - dd[3]):+.1f} pts")
    M.compare("recovery level ZT4-24", val("S-SD", "R", "ZT4-24"), val("W-SD", "R", "ZT4-24"), "S-SD", "W-SD")
    for k in ("24h", "L0-12", "D12-24"):
        M.compare(f"baseline SOD1 vs water {k}", {**val("S-SL", "B", k), **val("S-SD", "B", k)},
                  {**val("W-SL", "B", k), **val("W-SD", "B", k)}, "SOD1", "water")


def eeg_connected():
    """rung 2's EEG connection test on its own: longest unbroken EEG block >= 15 min."""
    from core import qc_thresholds as T
    out = {}
    for c, r in cards():
        pr = (r[2].get("detail") or {}).get("per_role", {}).get("eeg") or {}
        out[(c["cohort_id"], c["tp"], c["animal_id"])] = pr.get("longest_block_minutes", 0) >= T.MIN_BLOCK_MINUTES
    return out


def measures(out, gate_kind="stage1"):
    """Descriptive, no tests: sleep, NREM, bouts and NREM delta for every included mouse-window, then the change after
    CSD against the change after ad lib sleep. NREM delta is RELATIVE (1-4 Hz power / 0.5-30 Hz power), so electrode
    gain drift between recordings cancels. REM's share of sleep is fixed by the staging rule: shown to prove it."""
    res = {key: window_metrics(path) for key, path in primary_included(out, gate_kind).items()}
    measures_report(res)


def primary_included(out, gate_kind="stage1"):
    """{(batch, tp, animal): hypnogram} of the primary rescue: EEG connected, gap67 SCOREABLE, shuffle not."""
    root = os.path.join(out, f"staged-{gate_kind}")
    rows = json.load(open(os.path.join(root, "summary.json")))
    st = {(r[0], r[1], r[2], r[3]): r for r in rows}
    conn, inc = eeg_connected(), {}
    for key in sorted({k[:3] for k in st}):
        g, sh = st.get(key + ("gap67",)), st.get(key + ("shuffle",))
        if conn.get(key) and g and g[4] == "SCOREABLE" and (sh is None or sh[4] != "SCOREABLE"):
            inc[key] = os.path.join(root, g[9][:-4] + "_hypnogram.csv")
    return inc


def window_metrics(path):
    """sleep, NREM, REM share (constructed), bouts and NREM relative delta per segment of one hypnogram."""
    import csv
    if True:
        with open(path) as fh:
            h = list(csv.DictReader(fh))
        zt = np.array([float(x["zt_h"]) for x in h]); lab = np.array([x["state"] for x in h])
        ok = np.array([x["in_block"] == "1" for x in h]) & np.isin(lab, ["WAKE", "NREM", "REM"])
        rel = np.array([float(x["delta"]) / max(float(x["eeg_rms_uv"]) ** 2, 1e-9) for x in h])
        m = {}
        for seg, (a, b) in (("24h", (0, 24)), ("ZT4-24", (4, 24)), ("ZT4-8", (4, 8))):
            w = ok & (zt >= a) & (zt < b)
            if w.sum() < 450:  # under 30 min scored: no number
                continue
            idx = np.flatnonzero(w); runs = []
            for part in np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1):  # bouts never span a gap
                e = np.flatnonzero(lab[part][1:] != lab[part][:-1]) + 1
                runs += [(lab[part][i], (j - i) * 4 / 60) for i, j in zip(np.r_[0, e], np.r_[e, len(part)])]
            hrs, s = w.sum() * 4 / 3600, lab[w]
            nb = [d for x, d in runs if x == "NREM"]; wb = [d for x, d in runs if x == "WAKE"]
            m[seg] = dict(sleep=100 * np.mean(s != "WAKE"), nrem=100 * np.mean(s == "NREM"),
                          rem_of_sleep=100 * np.sum(s == "REM") / max(np.sum(s != "WAKE"), 1),
                          nrem_bout=np.mean(nb) if nb else np.nan, nrem_bouts_h=len(nb) / hrs,
                          wake_bout=np.mean(wb) if wb else np.nan,
                          swa=np.median(rel[w & (lab == "NREM")]) if np.any(w & (lab == "NREM")) else np.nan, h=hrs)
    return m


COLS = [("sleep", "sleep %", "{:+.1f}"), ("nrem", "NREM %", "{:+.1f}"), ("rem_of_sleep", "REM % of sleep*", "{:+.1f}"),
            ("nrem_bout", "NREM bout min", "{:+.2f}"), ("nrem_bouts_h", "NREM bouts/h", "{:+.1f}"),
        ("wake_bout", "wake bout min", "{:+.2f}"), ("swa", "NREM rel. delta", "x{:.2f}")]


def change_rows(res, seg, batches=("S-SD", "W-SD", "S-SL", "W-SL"), tag=lambda key: ""):
    print(f"  {'mouse':<20}" + "".join(f"{n:>17}" for _, n, _ in COLS) + "   h scored B/R")
    for batch in batches:
        for (b, t, a), mb in sorted(res.items()):
            mr = res.get((b, "R", a))
            if b != batch or t != "B" or not mr or seg not in mb or seg not in mr:
                continue
            cells = [(f.format(mr[seg][k] / mb[seg][k]) if k == "swa" else f.format(mr[seg][k] - mb[seg][k]))
                     for k, _, f in COLS]
            print(f"  {b} {a:<14}" + "".join(f"{c:>17}" for c in cells) + f"   {mb[seg]['h']:.1f}/{mr[seg]['h']:.1f}"
                  + tag((b, "R", a)))


def measures_report(res):
    cols = COLS

    def grp(batch, tp, seg, k):
        return [m[seg][k] for (b, t, a), m in res.items() if b == batch and t == tp and seg in m]

    print("=== 1. baseline, about a week on treatment, no CSD (24 h): SOD1 (S-SL + S-SD) vs water (W-SL + W-SD)")
    for k, name, _ in cols:
        sod, wat = grp("S-SL", "B", "24h", k) + grp("S-SD", "B", "24h", k), grp("W-SL", "B", "24h", k) + grp("W-SD", "B", "24h", k)
        print(f"  {name:<17} SOD1 {np.nanmean(sod):7.3f} (n={len(sod)})   water {np.nanmean(wat):7.3f} (n={len(wat)})"
              f"   SOD1-water {np.nanmean(sod) - np.nanmean(wat):+.3f}")
    print("\n=== 2. change after CSD vs change after ad lib sleep, same mouse, recovery - baseline (relative delta: ratio)")
    for seg in ("ZT4-24", "ZT4-8"):
        print(f"  -- {seg} ({'13:00-09:00' if seg == 'ZT4-24' else 'first 4 h after the deprivation ends, 13:00-17:00'})")
        change_rows(res, seg)
    print("  * REM is the top fraction of sleep by theta/delta BY CONSTRUCTION in stage 3: its share cannot carry an effect.")


def analyse_max(out):
    """Validation per variant, the first passing filter per SD window in a fixed order, then every measure."""
    import csv
    root = os.path.join(out, "staged-max")
    rows = json.load(open(os.path.join(root, "summary.json")))
    R = {tuple(r[:6]): r for r in rows}
    hyp = lambda r: os.path.join(root, r[10][:-4] + "_hypnogram.csv")

    def labels(path):
        with open(path) as fh:
            x = [(row["state"], row["in_block"] == "1") for row in csv.DictReader(fh)]
        return np.array([a for a, _ in x]), np.array([b for _, b in x])

    print("=== 1. validation: sleep vs wake kappa against the notched staging, windows where it is SCOREABLE")
    accepted = []
    for var in MAX_VARIANTS:
        ks = []
        for r in rows:
            if r[3] != "stage1" or r[4] != var or r[5]:
                continue
            rp = os.path.join(NOTCH_WIN, os.path.basename(os.path.dirname(r[10])), os.path.basename(r[10])[:-4])
            if not os.path.exists(rp + "_features.json") or \
                    json.load(open(rp + "_features.json"))["verdict"].split(":")[0] != "SCOREABLE":
                continue
            a, ia = labels(hyp(r)); b, ib = labels(rp + "_hypnogram.csv")
            m = ia & ib & (a != "EXCLUDED") & (b != "EXCLUDED")
            x, y = a[m] != "WAKE", b[m] != "WAKE"
            pe = x.mean() * y.mean() + (1 - x.mean()) * (1 - y.mean())
            ks.append((np.mean(x == y) - pe) / (1 - pe))
        ok = len(ks) >= 3 and np.median(ks) >= 0.8
        accepted += [var] if ok else []
        print(f"  {var:<8} n={len(ks):2d}  kappa median {np.median(ks) if ks else np.nan:.2f}  min "
              f"{min(ks) if ks else np.nan:.2f}  -> {'ACCEPTED' if ok else 'not used'}")

    print("\n=== 2. per SD window: first filter that passes stage 3 AND fails its own shuffle control, fixed order "
          f"{list(MAX_GATES)} x {accepted}")
    conn, res, how = eeg_connected(), {}, {}
    for key in sorted({tuple(r[:3]) for r in rows if r[0] in ("W-SD", "S-SD")}):
        pick, best = None, None
        for kind in MAX_GATES:
            for var in accepted:
                g, sh = R.get(key + (kind, var, False)), R.get(key + (kind, var, True))
                if not g:
                    continue
                best = g if best is None or (g[7] or -9) > (best[7] or -9) else best
                if pick is None and g[6] == "SCOREABLE" and sh and sh[6] != "SCOREABLE":
                    pick = g
        flag = "EEG-conn" if conn.get(key) else "EEG-NOT-conn"
        if pick:
            res[key], how[key] = window_metrics(hyp(pick)), f"{pick[3]}/{pick[4]}"
            print(f"  {' '.join(key):<22} SCOREABLE via {pick[3]}/{pick[4]:<8} r {pick[7]:.2f} wake {pick[8]:5.1f} "
                  f"h {pick[9]:5.1f}  {flag}")
        else:
            print(f"  {' '.join(key):<22} not scoreable; best r {best[7] if best and best[7] is not None else float('nan'):.2f} "
                  f"({best[3]}/{best[4]}, h {best[9]:.1f})  {flag}" if best else f"  {' '.join(key)}: no stage-2 file")

    sl = {k: window_metrics(p) for k, p in primary_included(out).items() if k[0] in ("W-SL", "S-SL")}
    allm = {**res, **sl}
    print("\n=== 3. change after CSD (max rescue) vs after ad lib sleep (primary rescue), recovery - baseline")
    for seg in ("ZT4-24", "ZT4-8"):
        print(f"  -- {seg}")
        change_rows(allm, seg, tag=lambda k: f"   [{how.get(k, 'primary')}]")
    for seg in ("ZT4-24", "ZT4-8"):
        print(f"  -- group mean change, {seg}")
        for b in ("S-SD", "W-SD", "S-SL", "W-SL"):
            d = [(allm[(b, 'R', a)][seg], m[seg]) for (bb, t, a), m in allm.items()
                 if bb == b and t == "B" and (b, "R", a) in allm and seg in m and seg in allm[(b, "R", a)]]
            if d:
                print(f"     {b} n={len(d)}  sleep {np.mean([r['sleep'] - x['sleep'] for r, x in d]):+5.1f}  NREM "
                      f"{np.mean([r['nrem'] - x['nrem'] for r, x in d]):+5.1f}  NREM bout "
                      f"{np.mean([r['nrem_bout'] - x['nrem_bout'] for r, x in d]):+.2f} min  rel delta "
                      f"x{np.mean([r['swa'] / x['swa'] for r, x in d]):.2f}")
    print("\n=== 4. baseline levels of the SD mice (24 h)")
    for (b, t, a), m in sorted(res.items()):
        if t == "B" and "24h" in m:
            print(f"  {b} {a:<10} sleep {m['24h']['sleep']:5.1f}  NREM {m['24h']['nrem']:5.1f}  "
                  f"NREM bout {m['24h']['nrem_bout']:.2f} min  rel delta {m['24h']['swa']:.3f}  [{how[(b, t, a)]}]")


def selfcheck():
    """1 mV of off-nominal mains and its harmonics must not leak into the gaps: they must read the noise alone."""
    fs, rng = 1000, np.random.default_rng(1)
    t = np.arange(40 * 4 * fs) / fs
    noise = 10 * rng.standard_normal(t.size)                       # white, 10 uV rms -> 0.2 uV^2/Hz
    mains = sum(a * np.sin(2 * np.pi * 60.3 * k * t) for k, a in ((1, 1000), (2, 400), (3, 300), (5, 100)))
    g0, _ = emg_bands(noise.reshape(40, -1), fs)
    g1, h1 = emg_bands((noise + mains).reshape(40, -1), fs)
    expect = np.array([hi - lo for lo, hi in GAPS]) * 100 / (fs / 2)
    assert np.all(np.abs(g0.mean(0) / expect - 1) < 0.15), g0.mean(0) / expect
    assert np.all(np.abs(g1.mean(0) / g0.mean(0) - 1) < 0.05), g1.mean(0) / g0.mean(0)
    assert h1[:, 0].mean() > 1e5                                   # and the mains is where it should be


if __name__ == "__main__":
    selfcheck()
    if len(sys.argv) not in (3, 4) or sys.argv[1] not in ("extract", "stage", "analyse", "measures", "extract-sd",
                                                           "stage-max", "analyse-max"):
        sys.exit(__doc__)
    {"extract": extract, "stage": stage, "analyse": analyse, "measures": measures,
     "extract-sd": lambda o: extract(o, only=("W-SD", "S-SD"), floor=True, dest="emg-sd"),
     "stage-max": stage_max, "analyse-max": analyse_max}[sys.argv[1]](os.path.expanduser(sys.argv[2]), *sys.argv[3:])
