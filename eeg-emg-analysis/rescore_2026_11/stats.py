"""Stage E of the 2026-11 HLB re-score: did SOD1 change sleep? The 2x2 on the re-scored windows.

Reads the backbone (backbone.py) and prints / writes:
  per_mouse_segments.csv  one row per mouse-window-segment-source: sleep share and NREM share of usable time
  stats.txt               the comparisons below, each with exact permutation p, Welch 95 % CI, Hedges g, MDE

Who is in: tier A or B (rule, W/NR/R). Sensitivity: EEG-alone NREM share over tiers A, B and C (one
method for everyone, so a tier C mouse is never mixed with rule-scored mice).
Segments: 24h, light (ZT0-12), dark (ZT12-24), ZT4-24 and its light / dark parts (the SD recoveries
exist only 13:00 -> 09:00, so every recovery-vs-baseline change uses ZT4-24 in both windows).
A segment counts only with >= 3 usable hours in it.
Comparisons:
  1. SOD1 vs water at baseline (no deprivation yet, about a week on treatment): all batches, SL only
  2. recovery - baseline, per paired mouse, ZT4-24: by arm; SOD1 vs water within SD and within SL;
     the SOD1 x SD interaction as (S-SD - S-SL) - (W-SD - W-SL) of arm means
  3. NREM delta in the first 4 h of recovery (ZT4-8), % of the same mouse's baseline ZT4-8 NREM delta
Usage: stats.py BACKBONE OUT
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "qc"))
from sod_sleep_2x2_2026_10_06 import perm, hedges_g, mde_d  # noqa: E402
from scipy import stats as st  # noqa: E402

SEGS = {"24h": (0, 24), "light": (0, 12), "dark": (12, 24), "ZT4-24": (4, 24), "L4-12": (4, 12), "D12-24": (12, 24)}
MIN_H = 3


def seg_table(B: Path) -> pd.DataFrame:
    rec = pd.read_csv(B / "recordings.csv")
    h = pd.read_csv(B / "hourly.csv")
    e = pd.read_parquet(B / "epochs.parquet", columns=["mouse", "tp", "zt_h", "stage_eeg_only", "hour_eeg_alone_ok", "eeg_artifact"])
    e["zt_hour"] = np.floor(e.zt_h).astype(int)
    ok = e[e.hour_eeg_alone_ok & ~e.eeg_artifact & e.stage_eeg_only.isin(["NR", "WR"])]
    eo = ok.groupby(["mouse", "tp", "zt_hour"]).agg(eo_nr=("stage_eeg_only", lambda s: (s == "NR").sum()),
                                                    eo_n=("stage_eeg_only", "size")).reset_index()
    rows = []
    for _, r in rec.iterrows():
        hm = h[(h.mouse == r.mouse) & (h.tp == r.tp)]
        em = eo[(eo.mouse == r.mouse) & (eo.tp == r.tp)]
        for name, (a, b) in SEGS.items():
            x = hm[(hm.zt_hour >= a) & (hm.zt_hour < b)]
            y = em[(em.zt_hour >= a) & (em.zt_hour < b)]
            base = dict(mouse=r.mouse, tp=r.tp, batch=r.batch, liquid=r.liquid, protocol=r.protocol, tier=r.tier, segment=name)
            if r.tier in ("A", "B") and (x.usable_min >= 30).sum() >= MIN_H:
                u = x.usable_min.sum()
                rows.append({**base, "source": "rule", "usable_h": u / 60,
                             "sleep_pct": 100 * (x.NR_min.sum() + x.R_min.sum()) / u, "nrem_pct": 100 * x.NR_min.sum() / u})
            if r.tier in ("A", "B", "C") and (y.eo_n >= 450).sum() >= MIN_H:
                rows.append({**base, "source": "eeg_only", "usable_h": y.eo_n.sum() * 4 / 3600,
                             "sleep_pct": np.nan, "nrem_pct": 100 * y.eo_nr.sum() / y.eo_n.sum()})
    return pd.DataFrame(rows)


def cmp(label, a: dict, b: dict, la, lb, out):
    va, vb = list(a.values()), list(b.values())
    s = f"{label:<44} {la} n={len(va)} {np.mean(va) if va else np.nan:5.1f} vs {lb} n={len(vb)} {np.mean(vb) if vb else np.nan:5.1f}"
    if len(va) + len(vb) > 2 and va and vb:
        obs, p, pmin = perm(va, vb)
        s += f"  diff {obs:+5.1f}  p={p:.3f} (min {pmin:.2g})"
        if len(va) > 1 and len(vb) > 1:
            g = hedges_g(va, vb)
            ci = st.ttest_ind(va, vb, equal_var=False).confidence_interval()
            sp = np.sqrt(((len(va) - 1) * np.var(va, ddof=1) + (len(vb) - 1) * np.var(vb, ddof=1)) / (len(va) + len(vb) - 2))
            md = mde_d(len(va), len(vb))
            s += f"  CI [{ci.low:+.1f}, {ci.high:+.1f}]  g={g:+.2f}  MDE {md * sp:.0f} pts"
    elif va and vb:
        s += f"  diff {np.mean(va) - np.mean(vb):+5.1f}  (1 vs 1: a case, no test)"
    else:
        s += "  NOT ESTIMABLE"
    s += "\n      " + ", ".join(f"{k} {v:.1f}" for k, v in {**a, **b}.items())
    out.append(s)


def main(B: Path, OUT: Path):
    OUT.mkdir(parents=True, exist_ok=True)
    T = seg_table(B)
    T.to_csv(OUT / "per_mouse_segments.csv", index=False)
    out = [f"HLB EEG re-score 2026-11: SOD1 x deprivation on sleep. Shares are % of usable time. "
           f"Rule = tiers A/B; EEG-only = tiers A/B/C, NREM vs not."]

    def vals(src, tp, seg, metric, **kw):
        q = T[(T.source == src) & (T.tp == tp) & (T.segment == seg)]
        for k, v in kw.items():
            q = q[q[k] == v]
        return dict(zip(q.mouse, q[metric]))

    out.append("\n1. SOD1 vs water at baseline (on treatment, before any deprivation)")
    for src, metric in (("rule", "sleep_pct"), ("rule", "nrem_pct"), ("eeg_only", "nrem_pct")):
        for seg in ("24h", "light", "dark"):
            cmp(f"[{src} {metric}] all batches, {seg}", vals(src, "B", seg, metric, liquid="SOD1"),
                vals(src, "B", seg, metric, liquid="water"), "SOD1", "water", out)
        cmp(f"[{src} {metric}] SL batches only, 24h", vals(src, "B", "24h", metric, liquid="SOD1", protocol="SL"),
            vals(src, "B", "24h", metric, liquid="water", protocol="SL"), "SOD1", "water", out)

    out.append("\n2. Recovery - baseline, same mouse, ZT4-24 (and its light / dark parts)")
    deltas = {}
    for src, metric in (("rule", "sleep_pct"), ("rule", "nrem_pct"), ("eeg_only", "nrem_pct")):
        for seg in ("ZT4-24", "L4-12", "D12-24"):
            d = {}
            for arm in ("HLBWSD", "HLBSSD", "HLBWSL", "HLBSSL"):
                b, r = vals(src, "B", seg, metric, batch=arm), vals(src, "R", seg, metric, batch=arm)
                d[arm] = {m: r[m] - b[m] for m in b if m in r}
            deltas[(src, metric, seg)] = d
            out.append(f"  [{src} {metric} {seg}] paired n: " + ", ".join(f"{k} {len(v)}" for k, v in d.items()))
            cmp(f"  SD: SOD1 vs water change", d["HLBSSD"], d["HLBWSD"], "S-SD", "W-SD", out)
            cmp(f"  SL: SOD1 vs water change", d["HLBSSL"], d["HLBWSL"], "S-SL", "W-SL", out)
            cmp(f"  water: SD vs SL change", d["HLBWSD"], d["HLBWSL"], "W-SD", "W-SL", out)
            cmp(f"  SOD1: SD vs SL change", d["HLBSSD"], d["HLBSSL"], "S-SD", "S-SL", out)
            m = {k: np.mean(list(v.values())) if v else np.nan for k, v in d.items()}
            out.append(f"      interaction (S-SD - S-SL) - (W-SD - W-SL) = {(m['HLBSSD'] - m['HLBSSL']) - (m['HLBWSD'] - m['HLBWSL']):+.1f} pts")

    out.append("\n3. NREM delta, first 4 h of recovery (ZT4-8), % of the same mouse's baseline ZT4-8")
    sw = pd.read_csv(B / "nrem_delta_hourly.csv")
    rec = pd.read_csv(B / "recordings.csv")
    sw = sw.merge(rec[rec.tier.isin(["A", "B"])][["mouse", "tp"]])
    sw = sw[sw.zt_hour.between(4, 7) & (sw.n_nrem_epochs >= 30)]
    g = sw.groupby(["batch", "mouse", "tp"]).apply(lambda x: np.average(x.nrem_delta, weights=x.n_nrem_epochs)).unstack("tp")
    g = g.reindex(columns=["B", "R"]).dropna()
    rel = (100 * g.R / g.B).reset_index()
    d = {b: dict(zip(rel[rel.batch == b].mouse, rel[rel.batch == b][0])) for b in ("HLBWSD", "HLBSSD", "HLBWSL", "HLBSSL")}
    cmp("NREM delta % baseline: SD vs SL, water", d["HLBWSD"], d["HLBWSL"], "W-SD", "W-SL", out)
    cmp("NREM delta % baseline: SD vs SL, SOD1", d["HLBSSD"], d["HLBSSL"], "S-SD", "S-SL", out)
    cmp("NREM delta % baseline: SOD1 vs water, SD", d["HLBSSD"], d["HLBWSD"], "S-SD", "W-SD", out)
    rel.to_csv(OUT / "nrem_delta_zt4_8_pct_baseline.csv", index=False)

    txt = "\n".join(out)
    (OUT / "stats.txt").write_text(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
