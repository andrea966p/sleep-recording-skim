"""Stages B + C of the 2026-11 HLB re-score: usability screen and staging of every recording.

Pre-specified 2026-11-03, before any recording was screened with it (thresholds are written here
and not tuned on the HLB results):

Staging (C): SleepStager's adopted rule, unchanged (rule.apply_rule, physio passes, 4-s epochs,
  cuts fitted on this recording's clean epochs), fed the mains-free EMG (`gap`: 70-470 Hz with
  notches at every 60 Hz multiple). Sensitivity: the same rule on `ss60` (SleepStager's 20-90 Hz
  RMS, notch at 60 Hz). An independent second scorer, a 3-state Gaussian HMM on log EMG, log delta,
  log theta/delta, log sigma, gamma fraction (fitted per recording, no labels), gives the
  rule-vs-HMM kappa and marks the epochs where two methods disagree.

Usability (B), label-free, per recording and per 1-h block:
  artifact epoch  rail contact (EEG or EMG), flat EEG (< 2 uV sd), or log total power / log EMG
                  more than 6 robust SD above the recording median.
  EMG             eta = Otsu separability of log EMG (SleepStager notes 5.8): >= 0.70 usable
                  (professor's operating point; < 0.70 flagged 2 of 112 reference recordings, both
                  failures). Block test: p10 of log EMG above the log cut = EMG failed in that
                  block (professor 2026-10-22: 7 of 7 flagged blocks were failures, 0 false alarms),
                  unless the EEG-only HMM finds < 10 % NREM in that hour (an all-wake hour; the
                  professor's test was only defined on blocks with 10-90 % wake).
  EEG             the EEG must see the state the EMG sees: AUC of log delta for the rule's NR vs
                  W epochs (split by the EMG alone) >= 0.75 (block and recording).
  Calibration     the two "unless/NR vs W" refinements above were made 2026-11-03 on the positive
                  control HLBSSL33 R (the hand-scored mouse) BEFORE any other recording was screened:
                  the first draft (AUC on EMG-sleep incl. REM; floor test on every hour) failed 6 of
                  its 24 hours, all in single-state hours. With a dead EMG, EEG alone:
                  2-state HMM on EEG features must separate (d' >= 1.5 on log delta) and put more
                  of its high-delta state in the light than in the dark phase.
  Tier            A  EMG + EEG usable in >= 20 of 24 h (or >= 17 of 20 h for SD recoveries)
                  B  both usable in >= 6 h of the light AND >= 6 h of the dark phase (scored on
                     those hours only, outcome as a share of usable time)
                  C  EEG usable, EMG not: EEG-only NREM vs not-NREM
                  D  EMG usable, EEG not: wake vs sleep from the EMG only
                  X  neither
Review fixes, 2026-11-03 (after the agent review of all 64 windows, before any outcome was read;
  see the method note): (1) EEG level gate: median log10 delta of clean epochs within 2-4 (log10 uV^2;
  dead or disconnected channels sat at 0.3-0.9, cortical EEG at 2.3-3.3, a railed one at 4.6), required for
  tier A/B/C and per hour; (2) the EEG-only HMM must alternate (>= 5 NR/not-NR changes per hour; a split
  at a technical step gave 0.1-0.4, every other window >= 9); (3) the per-hour delta AUC is judged only
  in mixed hours (10-90 % EMG wake), the same domain as the professor's floor test, so near all-sleep
  hours are no longer dropped (that had enriched the kept hours for wake).
Writes hypnogram.parquet + score.json beside features.parquet.  Usage: score.py EPOCHS [--only ...]
"""
import argparse, json, sys, warnings
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "SleepStager"))
from sleepstager import rule as R  # noqa: E402
sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parents[1] / "pipeline")]
import pipeline_common as P  # noqa: E402  (the project's r@1min)

EP_H = 900
ETA_MIN, AUC_MIN, DPRIME_MIN = 0.70, 0.75, 1.5
DELTA_LOG10 = (2.0, 4.0)          # review fix (1): cortical EEG level, log10 uV^2
EO_SWITCH_PER_H = 5               # review fix (2)
ZT0_HOUR = 9


def eta(x):
    v = np.log(np.clip(np.asarray(x, float), 1e-9, None)); v = v[np.isfinite(v)]
    hist, edges = np.histogram(v, bins=256); p = hist / hist.sum(); c = np.cumsum(p)
    mids = (edges[:-1] + edges[1:]) / 2; mu = np.cumsum(p * mids)
    with np.errstate(invalid="ignore", divide="ignore"):
        vb = (mu[-1] * c - mu) ** 2 / (c * (1 - c))
    return float(np.nanmax(vb) / v.var())


def auc(score, y):
    score, y = np.asarray(score, float), np.asarray(y, bool)
    ok = np.isfinite(score); score, y = score[ok], y[ok]
    n1, n0 = int(y.sum()), int((~y).sum())
    if n1 < 20 or n0 < 20:
        return np.nan
    r = pd.Series(score).rank().to_numpy()
    return float((r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def kappa(a, b):
    labs = ("W", "NR", "R"); ok = np.isin(a, labs) & np.isin(b, labs); a, b = a[ok], b[ok]
    M = np.array([[((a == x) & (b == y)).sum() for y in labs] for x in labs], float)
    n = M.sum(); po = np.trace(M) / n; pe = (M.sum(0) * M.sum(1)).sum() / n ** 2
    return float((po - pe) / (1 - pe)) if n and pe < 1 else np.nan


def robust_hi(v, k=6.0):
    lv = np.log(np.clip(v, 1e-9, None)); med = np.nanmedian(lv)
    mad = np.nanmedian(np.abs(lv - med)) * 1.4826
    return lv > med + k * mad


def hmm_stage(X, n_states, seeds=(0, 1, 2)):
    """Per-recording Gaussian HMM (no labels). Robust z (median / MAD, clipped at +-5) so a few
    artifact epochs cannot own a state; sticky start (p_stay 0.95); best log-likelihood of 3 seeds."""
    from hmmlearn.hmm import GaussianHMM
    from sklearn.cluster import KMeans
    med = np.median(X, 0); mad = np.median(np.abs(X - med), 0) * 1.4826 + 1e-9
    Z = np.clip((X - med) / mad, -5, 5)
    best = None
    for seed in seeds:
        m = GaussianHMM(n_components=n_states, covariance_type="diag", n_iter=100, random_state=seed,
                        init_params="c", params="stmc")
        m.startprob_ = np.full(n_states, 1 / n_states)
        m.transmat_ = np.full((n_states, n_states), 0.05 / (n_states - 1)); np.fill_diagonal(m.transmat_, 0.95)
        m.means_ = KMeans(n_states, n_init=5, random_state=seed).fit(Z).cluster_centers_
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            m.fit(Z)
            ll = m.score(Z)
        if best is None or ll > best[0]:
            best = (ll, m)
    m = best[1]
    return m.predict(Z), m.means_ * mad + med


MIN_CLEAN = 1800                     # 2 h of clean epochs before anything is fitted


def score(rec: Path) -> dict:
    t = pd.read_parquet(rec / "features.parquet")
    meta = json.loads((rec / "meta.json").read_text())
    n = len(t)
    zt = ((t.t_kst.dt.hour - ZT0_HOUR) % 24 + t.t_kst.dt.minute / 60 + t.t_kst.dt.second / 3600).to_numpy()
    light = zt < 12
    eeg_art = (t.eeg_rail | t.eeg_flat).to_numpy() | robust_hi(t.total_power)
    emg_art = t.emg_rail.to_numpy() | robust_hi(t.emg_rms_gap)
    art = eeg_art | emg_art
    out = dict(mouse=meta["mouseID"], batch=meta["batch"], tp=meta["condition"], position=meta["position"],
               n_epochs=n, hours=n * 4 / 3600, artifact_pct=round(100 * art.mean(), 2),
               eeg_artifact_pct=round(100 * eeg_art.mean(), 2), emg_artifact_pct=round(100 * emg_art.mean(), 2),
               old_qc=meta.get("old_qc_verdict"), old_qc_why=meta.get("old_qc_why"),
               eeg_line60_med_uv=round(float(t.eeg_line60_uv.median()), 1),
               emg_line60_med_uv=round(float(t.emg_line60_uv.median()), 1))
    hyp = pd.DataFrame({"epoch": t.epoch, "t_kst": t.t_kst, "zt_h": zt, "artifact": art,
                        "eeg_artifact": eeg_art, "emg_artifact": emg_art})
    ld = np.log(t.delta_power.to_numpy())
    emg = t.emg_rms_gap.to_numpy(); le = np.log(emg)
    emg_fit = (~emg_art).sum() >= MIN_CLEAN
    eeg_fit = (~eeg_art).sum() >= MIN_CLEAN
    joint = (~art).sum() >= MIN_CLEAN

    # EMG alone: wake vs sleep by the rule's own Otsu midpoint (for an EEG that cannot be read)
    for name in ("gap", "ss60"):
        out[f"eta_{name}"] = round(eta(t[f"emg_rms_{name}"].to_numpy()[~emg_art]), 3) if emg_fit else None
    cut_emg_only = R.otsu_midpoint(emg[~emg_art]) if emg_fit else np.nan
    hyp["stage_emg_only"] = np.where(emg_art | ~emg_fit, "X", np.where(emg > cut_emg_only, "W", "S"))

    # EEG alone: 2-state HMM, NREM vs not-NREM (for an EMG that cannot be read)
    Xe = np.column_stack([ld, np.log(t.theta_delta.clip(1e-6)), np.log(t.sigma_power),
                          np.log(t.gamma_frac.clip(1e-4) / (1 - t.gamma_frac.clip(1e-4, 0.999)))])
    oke = ~eeg_art & np.isfinite(Xe).all(1)
    eeg_only = np.full(n, "X", dtype="<U2")
    out["eeg_only_dprime"] = out["eeg_only_nrem_light_minus_dark"] = None
    if oke.sum() >= MIN_CLEAN:
        se, me = hmm_stage(Xe[oke], 2)
        hi = int(np.argmax(me[:, 0]))
        eeg_only[oke] = np.where(se == hi, "NR", "WR")
        a_, b_ = ld[oke][se == hi], ld[oke][se != hi]
        out["eeg_only_dprime"] = round(float((a_.mean() - b_.mean()) / np.sqrt(0.5 * (a_.var() + b_.var()))), 2)
        nrl, nrd = (eeg_only[light & oke] == "NR").mean(), (eeg_only[~light & oke] == "NR").mean()
        out["eeg_only_nrem_light_minus_dark"] = round(100 * float(nrl - nrd), 1)
    hyp["stage_eeg_only"] = eeg_only

    # EEG + EMG: the professor's rule (gap EMG, then ss60 as sensitivity) and the HMM second scorer
    for name in ("gap", "ss60"):
        hyp[f"stage_{name}"] = "X"; hyp[f"flag_{name}"] = ""
        out[f"emg_cut_{name}"] = None
        if not joint:
            continue
        lab_, info = R.apply_rule(t[f"emg_rms_{name}"].to_numpy(), t.theta_delta.to_numpy(), t.delta_power.to_numpy(),
                                  epoch_s=4.0, emg_tone_med=t[f"emg_tone_{name}"].to_numpy(), exclude=art)
        hyp[f"stage_{name}"] = np.asarray(lab_).astype("<U2")
        flags = np.full(n, "", dtype=object)
        for e, f in (info.get("flags") or {}).items():
            flags[int(e) - 1] = f
        hyp[f"flag_{name}"] = flags
        out[f"emg_cut_{name}"] = round(float(info.get("emg_cut", np.nan)), 2)
        out[f"rule_{name}"] = {k: info.get(k) for k in ("td_cut", "veto_cut", "n_tone_islands", "n_quiet_wake_islands",
                                                        "n_rem_onset_R")}
    lvl = lambda m: float(np.median(ld[m]) / np.log(10)) if m.sum() else np.nan
    out["eeg_median_log10_delta"] = round(lvl(oke), 2) if oke.sum() else None
    eeg_level_ok = bool(oke.sum() and DELTA_LOG10[0] <= lvl(oke) <= DELTA_LOG10[1])
    s_eo = eeg_only[np.isin(eeg_only, ("NR", "WR"))]
    out["eeg_only_switches_per_h"] = round(float((s_eo[1:] != s_eo[:-1]).sum() / (len(s_eo) * 4 / 3600)), 1) if len(s_eo) > 1 else None
    eeg_alone_ok = bool(out["eeg_only_dprime"] is not None and out["eeg_only_dprime"] >= DPRIME_MIN
                        and out["eeg_only_nrem_light_minus_dark"] > 0 and eeg_level_ok
                        and out["eeg_only_switches_per_h"] is not None and out["eeg_only_switches_per_h"] >= EO_SWITCH_PER_H)
    eo = hyp.stage_emg_only.to_numpy()
    wl = (eo[light & (eo != "X")] == "W").mean() if (light & (eo != "X")).sum() > 900 else np.nan
    wd = (eo[~light & (eo != "X")] == "W").mean() if (~light & (eo != "X")).sum() > 900 else np.nan
    out["emg_only_wake_dark_minus_light"] = round(100 * float(wd - wl), 1) if np.isfinite(wd - wl) else None
    emg_nocturnal = bool(np.isfinite(wd - wl) and wd - wl >= 0.10)
    hour = np.arange(n) // EP_H
    need = 17 if n * 4 / 3600 < 22 else 20

    def screen(name):
        """Second scorer, hour tests and tier with the rule staged on EMG measure `name`."""
        o = {}
        lab = hyp[f"stage_{name}"].to_numpy().astype("<U2")
        em = t[f"emg_rms_{name}"].to_numpy(); lem = np.log(em)
        hmm = np.full(n, "X", dtype="<U2")
        o["kappa_rule_hmm"] = o["kappa_nrem_rule_vs_eeg_only"] = None
        if joint:
            X = np.column_stack([lem, ld, np.log(t.theta_delta.clip(1e-6))])
            ok = ~art & np.isfinite(X).all(1)
            st, means = hmm_stage(X[ok], 3)
            w = int(np.argmax(means[:, 0])); rest = [k for k in range(3) if k != w]
            r = rest[int(np.argmax(means[rest, 2]))]; nr = [k for k in rest if k != r][0]
            hmm[ok] = np.select([st == w, st == r, st == nr], ["W", "R", "NR"], default="X")
            o["kappa_rule_hmm"] = round(kappa(lab, hmm), 3)
            # rule NREM vs the EEG-alone NREM call: two routes to NREM that share no EMG
            m2 = np.isin(lab, ("W", "NR", "R")) & np.isin(eeg_only, ("NR", "WR"))
            a2, b2 = np.where(lab[m2] == "NR", "NR", "W"), np.where(eeg_only[m2] == "NR", "NR", "W")
            o["kappa_nrem_rule_vs_eeg_only"] = round(kappa(a2, b2), 3)
        emg_rec_ok = bool(emg_fit and out[f"eta_{name}"] >= ETA_MIN)
        cut = out[f"emg_cut_{name}"] if joint else (cut_emg_only if name == "gap" else np.nan)
        lc = np.log(cut) if cut is not None and np.isfinite(cut) else np.nan
        wake_emg = em > cut if np.isfinite(lc) else np.zeros(n, bool)
        blocks = []
        for h in np.unique(hour):
            inh = hour == h
            me, mE, mb = inh & ~emg_art, inh & ~eeg_art, inh & ~art
            row = dict(hour=int(h), zt_h=float(zt[inh][0]), n_clean=int(mb.sum()), n_emg_clean=int(me.sum()),
                       n_eeg_clean=int(mE.sum()))
            emg_ok = eeg_ok = False
            if emg_fit and np.isfinite(lc) and me.sum() >= EP_H // 2:
                floor_rel = float(np.percentile(lem[me], 10) - lc)
                bw = float(wake_emg[me].mean())
                nrem_eeg = float((eeg_only[mE] == "NR").mean()) if (eeg_alone_ok and mE.sum() >= EP_H // 2) else None
                # the floor test is only defined for mixed-state hours (professor: blocks with 10-90 % wake);
                # an hour whose EMG floor sits above the cut is a failed EMG only if the EEG says it slept
                # (no readable EEG: only if the EMG itself does not call >= 90 % of the hour wake)
                all_wake = (nrem_eeg < 0.10) if nrem_eeg is not None else (bw >= 0.90)
                emg_ok = floor_rel <= 0 or all_wake
                row.update(floor_rel=round(floor_rel, 2), wake_frac_emg=round(bw, 3),
                           nrem_eeg=round(nrem_eeg, 3) if nrem_eeg is not None else None)
            hl = lvl(inh & oke)
            row["eeg_log10_delta"] = round(hl, 2) if np.isfinite(hl) else None
            hour_level = bool(np.isfinite(hl) and DELTA_LOG10[0] <= hl <= DELTA_LOG10[1])
            eeg_alone_hour = bool(eeg_alone_ok and mE.sum() >= EP_H // 2 and hour_level)
            if mE.sum() >= EP_H // 2 and oke.sum() >= MIN_CLEAN and eeg_level_ok and hour_level:
                eeg_ok = True
                if joint and emg_rec_ok:
                    wn = mb & np.isin(lab, ("W", "NR"))                    # W vs NR is split by the EMG alone
                    a_d = auc(ld[wn], lab[wn] == "NR")                     # NREM should carry HIGHER delta
                    row["auc_delta"] = round(a_d, 3) if np.isfinite(a_d) else None
                    bwh = float(wake_emg[me].mean()) if me.sum() else np.nan
                    mixed = np.isfinite(bwh) and 0.10 <= bwh <= 0.90       # review fix (3): mixed hours only
                    eeg_ok = (a_d >= AUC_MIN) if (np.isfinite(a_d) and mixed) else True
            row.update(eeg_alone_ok=eeg_alone_hour, emg_ok=bool(emg_ok), eeg_ok=bool(eeg_ok), both_ok=bool(emg_ok and eeg_ok and joint and mb.sum() >= EP_H // 2))
            blocks.append(row)
        B = pd.DataFrame(blocks)
        o["auc_delta_recording"] = None
        if joint:
            wn = ~art & np.isin(lab, ("W", "NR"))
            o["auc_delta_recording"] = round(auc(ld[wn], lab[wn] == "NR"), 3)
        zt_b = B.zt_h.to_numpy()
        def hrs(col, ph=None):
            m = B[col].to_numpy()
            if ph == "L": m = m & (zt_b < 12)
            if ph == "D": m = m & (zt_b >= 12)
            return int(m.sum())
        o.update(hours_both_ok=hrs("both_ok"), hours_both_ok_light=hrs("both_ok", "L"), hours_both_ok_dark=hrs("both_ok", "D"),
                 hours_emg_ok=hrs("emg_ok"), hours_emg_ok_light=hrs("emg_ok", "L"), hours_emg_ok_dark=hrs("emg_ok", "D"),
                 hours_eeg_ok=hrs("eeg_ok"), hours_eeg_ok_light=hrs("eeg_ok", "L"), hours_eeg_ok_dark=hrs("eeg_ok", "D"),
                 hours_eeg_alone_ok=hrs("eeg_alone_ok"), hours_eeg_alone_ok_light=hrs("eeg_alone_ok", "L"),
                 hours_eeg_alone_ok_dark=hrs("eeg_alone_ok", "D"))
        eeg_rec_ok = (bool(o["auc_delta_recording"] >= AUC_MIN) and eeg_level_ok) if (emg_rec_ok and joint) else eeg_alone_ok
        lb, db = o["hours_both_ok_light"], o["hours_both_ok_dark"]
        if emg_rec_ok and eeg_rec_ok and o["hours_both_ok"] >= need:
            tier = "A"
        elif emg_rec_ok and eeg_rec_ok and lb >= 6 and db >= 6:
            tier = "B"
        elif eeg_alone_ok and o["hours_eeg_alone_ok_light"] >= 6 and o["hours_eeg_alone_ok_dark"] >= 6:
            tier = "C"
        elif name == "gap" and emg_rec_ok and o["hours_emg_ok_light"] >= 6 and o["hours_emg_ok_dark"] >= 6 and emg_nocturnal:
            tier = "D"
        else:
            tier = "X"
        o.update(emg_recording_ok=emg_rec_ok, eeg_recording_ok=eeg_rec_ok, tier=tier)
        return o, B, lab, hmm

    # primary = gap EMG; SleepStager's own 20-90 Hz EMG (60 Hz notch) is used instead only when it
    # reaches tier A/B and the gap EMG does not (added 2026-11-03 after the S-SD batch, see the method note)
    og, Bg, labg, hmmg = screen("gap")
    os_, Bs, labs, hmms = screen("ss60")
    out["tier_gap"], out["tier_ss60"] = og["tier"], os_["tier"]
    rank = "ABCDX"
    use_ss60 = os_["tier"] in "AB" and rank.index(os_["tier"]) < rank.index(og["tier"])
    o, B, lab, hmm = (os_, Bs, labs, hmms) if use_ss60 else (og, Bg, labg, hmmg)
    src = "ss60" if use_ss60 else "gap"
    out.update(o, emg_source=src, eeg_alone_ok=eeg_alone_ok, emg_cut=out[f"emg_cut_{src}"], eta=out[f"eta_{src}"])
    out["kappa_gap_ss60"] = round(kappa(labg, labs), 3) if joint else None
    hyp["stage"] = lab; hyp["flag"] = hyp[f"flag_{src}"]; hyp["stage_hmm"] = hmm
    for col in ("both_ok", "emg_ok", "eeg_ok", "eeg_alone_ok"):
        hyp[f"hour_{col}"] = B[col].to_numpy()[hour]
    hyp["hour_ok"] = hyp.hour_both_ok

    # read-outs on usable epochs: W/NR/R from the rule (A/B); NREM from the EEG alone; sleep from the EMG alone
    use = hyp.hour_ok.to_numpy() & ~art & np.isin(lab, ("W", "NR", "R"))
    def pct(arr, stg, m):
        return round(100 * float((arr[m] == stg).mean()), 1) if m.sum() > 100 else None
    for ph, pm in (("", np.ones(n, bool)), ("_light", light), ("_dark", ~light)):
        out[f"wake_pct{ph}"] = pct(lab, "W", use & pm)
        out[f"nrem_pct{ph}"] = pct(lab, "NR", use & pm)
        out[f"rem_pct{ph}_provisional"] = pct(lab, "R", use & pm)
        out[f"nrem_pct{ph}_eeg_only"] = pct(eeg_only, "NR", hyp.hour_eeg_alone_ok.to_numpy() & oke & pm)
        out[f"sleep_pct{ph}_emg_only"] = pct(hyp.stage_emg_only.to_numpy(), "S", hyp.hour_emg_ok.to_numpy() & ~emg_art & pm)
    for stg in ("W", "NR", "R"):
        m = use & (lab == stg)
        out[f"med_logdelta_{stg}"] = round(float(np.median(ld[m])), 2) if m.sum() > 50 else None
    out["r_1min"] = out["rem_entries_from_nrem_pct"] = None
    if use.sum() > 900:
        sl = np.isin(lab, ("NR", "R")).astype(float)
        edges = np.flatnonzero(np.diff(np.r_[0, use.astype(int), 0]))
        r1, _, _, r1s = P.within_block_persistence(sl, list(zip(edges[::2], edges[1::2])), lag=15)
        out["r_1min"], out["r_1min_shuffled"] = round(float(r1), 3), round(float(r1s), 3)
        R_ = np.flatnonzero((lab == "R") & use); R_ = R_[R_ > 0]; prev = lab[R_ - 1]
        out["rem_entries_from_nrem_pct"] = round(100 * float((prev[prev != "R"] == "NR").mean()), 1) if (prev != "R").sum() else None

    hyp.to_parquet(rec / "hypnogram.parquet", index=False)
    B.to_csv(rec / "blocks_1h.csv", index=False)
    (rec / "score.json").write_text(json.dumps(out, indent=1, default=str))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("epochs", type=Path)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    recs = sorted(p.parent for p in a.epochs.glob("*/*/*/features.parquet"))
    if a.only:
        recs = [r for r in recs if any(o in str(r) for o in a.only)]
    rows = []
    for r in recs:
        try:
            o = score(r)
        except Exception as ex:                       # one bad recording must not stop the cohort
            print(f"ERROR {r}: {ex!r}", flush=True); continue
        rows.append(o)
        print(f"{o['mouse']} {o['tp'][0]} tier {o['tier']} tier_gap {o['tier_gap']} ss60 {o['tier_ss60']} src {o['emg_source']} eta {o['eta_gap']}/{o['eta_ss60']} auc {o['auc_delta_recording']} "
              f"hours {o['hours_both_ok']} ({o['hours_both_ok_light']}L/{o['hours_both_ok_dark']}D) k_hmm {o['kappa_rule_hmm']} k_nrem {o['kappa_nrem_rule_vs_eeg_only']} "
              f"W {o['wake_pct_light']}/{o['wake_pct_dark']} eegonly NR {o['nrem_pct_light_eeg_only']}/{o['nrem_pct_dark_eeg_only']} "
              f"emgonly S {o['sleep_pct_light_emg_only']}/{o['sleep_pct_dark_emg_only']} old {o['old_qc']}", flush=True)
    pd.DataFrame([{k: v for k, v in o.items() if not isinstance(v, dict)} for o in rows]).to_csv(
        a.epochs / "screen_summary.csv", index=False)


if __name__ == "__main__":
    main()
