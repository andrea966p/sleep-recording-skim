#!/usr/bin/env python3
"""Build a BLIND scoring pack so a human can be compared against stage 3.

Why this exists
---------------
The pipeline's accuracy has never been measured. Every architecture number, and
the placement of the WAKE threshold that the 2026-08-08 Otsu sweep showed the
circadian result depends on, is unvalidated without a human reference.

Design decisions, and why
-------------------------
* **20 s per item, the centre epoch is the one you score.** The lab convention is
  4 s epochs viewed 5 at a time. Each item therefore shows the target epoch plus
  two either side, with the target shaded.
* **Items are in RANDOM order.** Scoring contiguous data lets a human follow bout
  structure and inflates agreement for the wrong reason. Randomising forces each
  epoch to be judged on its own evidence, which is what we want to compare
  against a per-epoch classifier.
* **Stratified by the automatic label, equal n per state.** REM is only 4-7% of
  epochs, so a purely random draw would give too few to say anything about it.
  ⚠️ This means the pack's prevalence is BY DESIGN and does not match the
  recording. Cohen's kappa is prevalence-sensitive, so this is reported as a
  stratified kappa. Use --random for an unstratified draw as well.
* **The automatic label is never shown and never encoded in the filename.**
  Truth lives in `_TRUTH_do_not_open.csv`.
* **Fixed y-axis on every item.** Auto-scaling would leak state information: a
  quiet epoch autoscaled looks as large as a loud one.

Usage
    python3 make_scoring_set.py <npz> [--n 300] [--out DIR] [--random] [--seed 1]
"""
import argparse
import csv
import json
import os
import random

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

EPOCH_S = 4
CONTEXT = 2                      # epochs either side -> 5 epochs, 20 s
STATES = ["WAKE", "NREM", "REM"]


def build(npz_path, n_items, outdir, stratified, seed):
    rng = random.Random(seed)
    z = np.load(npz_path, allow_pickle=True)
    meta = json.loads(str(z["meta"]))
    fs = int(z["fs"])
    eeg, emg = z["eeg"], z["emg"]
    name = f"{meta.get('port','?')}{meta.get('slot','?')}"

    hyp = npz_path[:-4] + "_hypnogram.csv"
    if not os.path.exists(hyp):
        raise SystemExit(f"need stage 3 output first: {hyp}")
    rows = list(csv.DictReader(open(hyp)))
    usable = [r for r in rows if r["in_block"] == "1" and r["state"] in STATES]
    if not usable:
        raise SystemExit("no scored epochs in this recording")

    by_state = {s: [r for r in usable if r["state"] == s] for s in STATES}
    picked = []
    if stratified:
        per = max(1, n_items // len(STATES))
        for s in STATES:
            pool = by_state[s]
            if not pool:
                continue
            picked += rng.sample(pool, min(per, len(pool)))
    else:
        picked = rng.sample(usable, min(n_items, len(usable)))
    rng.shuffle(picked)

    os.makedirs(outdir, exist_ok=True)
    # fixed scales, from the recording as a whole, so no item leaks its state
    e_lim = float(np.percentile(np.abs(eeg), 99.5))
    m_lim = float(np.percentile(np.abs(emg), 99.5))

    truth, sheet = [], []
    spe = fs * EPOCH_S
    for i, r in enumerate(picked, 1):
        ep = int(r["epoch"])
        a, b = ep - CONTEXT, ep + CONTEXT + 1
        if a < 0 or b * spe > len(eeg):
            continue
        E = eeg[a * spe:b * spe]
        M = emg[a * spe:b * spe]
        t = np.arange(len(E)) / fs

        fig, ax = plt.subplots(2, 1, figsize=(10, 4.2), sharex=True)
        for k, (sig, lim, lbl) in enumerate(((E, e_lim, "EEG µV"), (M, m_lim, "EMG µV"))):
            ax[k].plot(t, sig, lw=0.6, color="k")
            ax[k].set_ylim(-lim, lim)
            ax[k].set_ylabel(lbl)
            ax[k].axvspan(CONTEXT * EPOCH_S, (CONTEXT + 1) * EPOCH_S,
                          color="tab:blue", alpha=0.10, lw=0)
            for x in range(0, (2 * CONTEXT + 2) * EPOCH_S, EPOCH_S):
                ax[k].axvline(x, color="0.8", lw=0.6)
            ax[k].grid(alpha=.2)
        ax[0].set_title(f"item {i:04d}   score the SHADED 4 s epoch   "
                        f"(20 s shown, fixed scale)", fontsize=10)
        ax[1].set_xlabel("seconds")
        fig.tight_layout()
        fig.savefig(os.path.join(outdir, f"{i:04d}.png"), dpi=95)
        plt.close(fig)

        truth.append(dict(item=i, epoch=ep, auto_state=r["state"],
                          zt_h=r["zt_h"], light=r["light"]))
        sheet.append(dict(item=i, your_stage=""))

    with open(os.path.join(outdir, "_TRUTH_do_not_open.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["item", "epoch", "auto_state", "zt_h", "light"])
        w.writeheader(); w.writerows(truth)
    with open(os.path.join(outdir, "scoresheet.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["item", "your_stage"])
        w.writeheader(); w.writerows(sheet)

    open(os.path.join(outdir, "README.txt"), "w").write(f"""BLIND SCORING PACK -- {name}
source: {os.path.basename(npz_path)}
items:  {len(truth)}   ({'stratified equal-n per auto state' if stratified else 'unstratified random'})
seed:   {seed}

HOW TO SCORE
  Open score.html in a browser, or flip through the PNGs and fill scoresheet.csv.
  Each image shows 20 s. Score ONLY the shaded 4 s epoch in the middle.
  Allowed answers: WAKE, NREM, REM   (or UNSURE, which is excluded from kappa)

DO NOT OPEN _TRUTH_do_not_open.csv until you have finished.
Items are in random order on purpose, so bout structure cannot be followed.

WHEN DONE
  python3 score_kappa.py {outdir}
""")

    html = """<!doctype html><meta charset=utf-8><title>Blind scoring</title>
<style>body{font-family:system-ui;margin:0;background:#111;color:#eee}
#top{position:sticky;top:0;background:#000;padding:8px 12px;display:flex;gap:12px;align-items:center}
img{max-width:100%;display:block;margin:0 auto;background:#fff}
button{font-size:16px;padding:8px 14px;border:0;border-radius:6px;cursor:pointer}
.w{background:#e07b39}.n{background:#4a8fe7}.r{background:#57b85a}.u{background:#777}
#prog{margin-left:auto;font-variant-numeric:tabular-nums}</style>
<div id=top>
 <button class=w onclick=pick('WAKE')>1 WAKE</button>
 <button class=n onclick=pick('NREM')>2 NREM</button>
 <button class=r onclick=pick('REM')>3 REM</button>
 <button class=u onclick=pick('UNSURE')>4 unsure</button>
 <button onclick=back()>&larr; back</button>
 <button onclick=save()>save CSV</button>
 <span id=prog></span>
</div>
<img id=im>
<script>
const N=NITEMS; let i=+(localStorage.getItem('i')||1);
let ans=JSON.parse(localStorage.getItem('ans')||'{}');
function show(){if(i>N){document.getElementById('im').src='';
 document.getElementById('prog').textContent='DONE -- press save CSV';return}
 document.getElementById('im').src=String(i).padStart(4,'0')+'.png';
 document.getElementById('prog').textContent=i+' / '+N+'   scored '+Object.keys(ans).length;}
function pick(s){ans[i]=s;localStorage.setItem('ans',JSON.stringify(ans));
 i++;localStorage.setItem('i',i);show();}
function back(){if(i>1){i--;localStorage.setItem('i',i);show();}}
function save(){let t='item,your_stage\\n';for(let k=1;k<=N;k++)t+=k+','+(ans[k]||'')+'\\n';
 const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([t],{type:'text/csv'}));
 a.download='scoresheet.csv';a.click();}
document.onkeydown=e=>{if(e.key=='1')pick('WAKE');if(e.key=='2')pick('NREM');
 if(e.key=='3')pick('REM');if(e.key=='4')pick('UNSURE');if(e.key=='Backspace')back();};
show();
</script>"""
    open(os.path.join(outdir, "score.html"), "w").write(html.replace("NITEMS", str(len(truth))))
    print(f"{name}: {len(truth)} items -> {outdir}")
    print(f"  open {os.path.join(outdir,'score.html')} in a browser, or fill scoresheet.csv")
    return len(truth)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("npz")
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--out", default=None)
    ap.add_argument("--random", action="store_true",
                    help="unstratified draw (prevalence matches the recording)")
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    out = a.out or (a.npz[:-4] + "_SCORING")
    build(a.npz, a.n, out, not a.random, a.seed)


if __name__ == "__main__":
    main()
