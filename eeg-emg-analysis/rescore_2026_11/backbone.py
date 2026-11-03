"""Stage D of the 2026-11 HLB re-score: the data backbone every figure is built from.

Reads EPOCHS/<batch>/<B|R>/<mouse>/{features.parquet, hypnogram.parquet, score.json, psd_eeg.npy}
and writes OUT/ (one row per thing, long format, no wide pivots):

  recordings.csv        one row per mouse-window: identity, arm, tier, every screen metric
  epochs.parquet        one row per 4-s epoch of every recording: stages from every scorer,
                        artifact / usable flags, rule marks, the features the stages rest on
  hourly.csv            one row per mouse-window-ZT hour: minutes of W / NR / R, usable minutes
  bouts.csv             one row per bout (run of one stage, usable epochs only, `stage` = the rule on the chosen EMG)
  spectra.csv           one row per mouse-window-state-phase-frequency (1..50 Hz): mean EEG power
  nrem_delta_hourly.csv one row per mouse-window-ZT hour: mean NREM delta power, raw and as % of
                        that mouse's baseline 24-h NREM mean (the SWA time course; empty when the
                        baseline has < 1 h of usable NREM)

Stage letters: W, NR, R; X = artifact; U = unstaged. Usage: backbone.py EPOCHS OUT [FINAL_TIERS_JSON]
With FINAL_TIERS_JSON ({"<MOUSE>_<B|R>": {"tier", "why"}}), `tier` is the reviewed tier and `tier_screen`
the automatic one; every downstream script reads `tier`.
"""
import json, sys
from pathlib import Path

import numpy as np
import pandas as pd

ARM = {"HLBWSD": ("water", "SD"), "HLBSSD": ("SOD1", "SD"), "HLBWSL": ("water", "SL"), "HLBSSL": ("SOD1", "SL")}
KEEP = ["delta_power", "theta_power", "sigma_power", "beta_power", "low_gamma_power", "theta_delta", "gamma_frac",
        "emg_rms_gap", "emg_tone_gap", "emg_rms_ss60", "emg_tone_ss60", "eeg_line60_uv", "emg_line60_uv"]


def main(epochs: Path, out: Path, final: Path | None = None):
    out.mkdir(parents=True, exist_ok=True)
    recs, eps, hourly, bouts, spectra, swa = [], [], [], [], [], []
    for d in sorted(p.parent for p in epochs.glob("*/*/*/score.json")):
        s = json.loads((d / "score.json").read_text())
        liquid, protocol = ARM[s["batch"]]
        tp = "B" if s["tp"] == "Baseline" else "R"
        key = dict(batch=s["batch"], liquid=liquid, protocol=protocol, mouse=s["mouse"], tp=tp)
        recs.append({**{k: v for k, v in s.items() if not isinstance(v, dict)}, **key})
        h = pd.read_parquet(d / "hypnogram.parquet")
        f = pd.read_parquet(d / "features.parquet", columns=KEEP)
        e = pd.concat([pd.DataFrame(key, index=h.index), h, f], axis=1)
        e["usable"] = e.hour_ok & ~e.artifact & e.stage.isin(["W", "NR", "R"])
        eps.append(e)

        e["zt_hour"] = np.floor(e.zt_h).astype(int)
        u = e[e.usable]
        hh = (u.groupby(["zt_hour", "stage"]).size().unstack(fill_value=0).reindex(columns=["W", "NR", "R"], fill_value=0)
              * 4 / 60).add_suffix("_min")
        hh["usable_min"] = e.groupby("zt_hour").usable.sum() * 4 / 60
        hourly.append(hh.reindex(range(24)).reset_index().assign(**key))

        st = e.stage.where(e.usable, "-").to_numpy()
        cut = np.flatnonzero(st[1:] != st[:-1]) + 1
        starts = np.r_[0, cut]; ends = np.r_[cut, len(st)]
        b = pd.DataFrame({"stage": st[starts], "start_epoch": starts + 1, "n_epochs": ends - starts})
        b = b[b.stage != "-"]
        b["duration_s"] = b.n_epochs * 4
        b["zt_h"] = e.zt_h.to_numpy()[b.start_epoch - 1]
        bouts.append(b.assign(**key))

        psd = np.load(d / "psd_eeg.npy")
        light = (e.zt_h < 12).to_numpy()
        for stg in ("W", "NR", "R"):
            for ph, pm in (("light", light), ("dark", ~light), ("24h", np.ones(len(e), bool))):
                m = e.usable.to_numpy() & (e.stage == stg).to_numpy() & pm
                if m.sum() < 30:
                    continue
                spectra.append(pd.DataFrame({**key, "stage": stg, "phase": ph, "n_epochs": int(m.sum()),
                                             "hz": np.arange(1, 51), "power_uv2": psd[m].mean(0)}))
        nr = e[e.usable & (e.stage == "NR")]
        sw = nr.groupby("zt_hour").agg(nrem_delta=("delta_power", "mean"), n_nrem_epochs=("delta_power", "size"))
        swa.append(sw.reindex(range(24)).reset_index().assign(**key, nrem_delta_24h_mean=nr.delta_power.mean(), n_nrem_24h=len(nr)))

    R = pd.DataFrame(recs)
    if final:
        F = json.loads(final.read_text())
        R["tier_screen"] = R.tier
        R["tier"] = [F[f"{m}_{tp}"]["tier"] for m, tp in zip(R.mouse, R.tp)]
        R["tier_why"] = [F[f"{m}_{tp}"]["why"] for m, tp in zip(R.mouse, R.tp)]
    R.to_csv(out / "recordings.csv", index=False)
    E = pd.concat(eps, ignore_index=True)
    E.to_parquet(out / "epochs.parquet", index=False)
    pd.concat(hourly, ignore_index=True).to_csv(out / "hourly.csv", index=False)
    pd.concat(bouts, ignore_index=True).to_csv(out / "bouts.csv", index=False)
    pd.concat(spectra, ignore_index=True).to_csv(out / "spectra.csv", index=False)
    S = pd.concat(swa, ignore_index=True)
    bl = S[(S.tp == "B") & (S.n_nrem_24h >= 900)]                         # a baseline with >= 1 h usable NREM
    base = bl.groupby("mouse").nrem_delta_24h_mean.first()                 # % of the mouse's own baseline
    S["nrem_delta_pct_baseline"] = 100 * S.nrem_delta / S.mouse.map(base)
    S.to_csv(out / "nrem_delta_hourly.csv", index=False)
    print(f"{len(R)} recordings, {len(E):,} epochs -> {out}")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]) if len(sys.argv) > 3 else None)
