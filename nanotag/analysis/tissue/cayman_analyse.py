"""Independent reanalysis of SOD (Cayman 706002) and MDA (Abcam ab118970) tissue assays. 2x2: drink (S/W) x sleep (SD/SL)."""
import itertools, warnings, sys
import numpy as np, pandas as pd, statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
from scipy import stats, optimize
import pingouin as pg
warnings.filterwarnings("ignore")
D = sys.argv[1]
S = pd.read_csv(f"{D}/samples.csv"); ST = pd.read_csv(f"{D}/standards.csv"); T = pd.read_csv(f"{D}/tissue.csv")
S["drink"] = S.group.str[0]; S["sleep"] = S.group.str[2:]
S["odm"] = S[["od1", "od2"]].mean(1)
rng = np.random.default_rng(20261102)
CAY = 0.23 / 0.01  # Cayman 706002 well-volume factor (manual p.20)
DIL = 50

def fit_lin(x, y):
    b, a = np.polyfit(x, y, 1); return b, a

def fourpl(x, A, B, C, Dd): return Dd + (A - Dd) / (1 + (x / C) ** B)

def sod_values(df, std, method):
    out = pd.Series(index=df.index, dtype=float)
    for plate, sub in df.groupby("plate"):
        s = std[std.plate == plate].copy(); s["m"] = s[["od1", "od2"]].mean(1)
        blank = sub.bg.mean()  # no blank wells recorded: sample-background wells (no XO) used as blank proxy
        if method == "sheet":  # linear OD vs U/mL on raw standards; samples BG-subtracted; no x23
            b, a = fit_lin(s.conc, s.m)
            out[sub.index] = (((sub.od1 - sub.bg) - a) / b * DIL + ((sub.od2 - sub.bg) - a) / b * DIL) / 2
        elif method == "sheet_noBG":  # same line, samples raw (consistent with raw standards)
            b, a = fit_lin(s.conc, s.m); out[sub.index] = (sub.odm - a) / b * DIL
        elif method in ("cayman", "cayman_noblank"):
            bl = blank if method == "cayman" else 0.0
            csv = s.m - bl; A0 = csv[s.conc == 0].iloc[0]
            b, a = fit_lin(s.conc, A0 / csv)
            lr = A0 / (sub.odm - sub.bg) if method == "cayman" else A0 / (sub.odm)
            out[sub.index] = (lr - a) / b * CAY * DIL
        elif method == "4pl":  # 4PL on blank-corrected standards, samples background-corrected
            csv = s.m - blank
            p, _ = optimize.curve_fit(fourpl, s.conc + 1e-6, csv, p0=[csv.max(), 1, 0.02, 0.0], maxfev=20000)
            A, B, C, Dd = p; y = sub.odm - sub.bg
            out[sub.index] = C * ((A - Dd) / (y - Dd) - 1) ** (1 / B) * CAY * DIL
    return out

def mda_values(df, std, method):
    s = std.copy(); s["m"] = s[["od1", "od2"]].mean(1)
    if method == "sheet":
        b, a = fit_lin(s.conc, s.m); return (df.odm - a) / b
    if method == "drop5":  # top standard flattens; refit without 5 nmol
        s = s[s.conc < 5]; b, a = fit_lin(s.conc, s.m); return (df.odm - a) / b
    if method == "quad":
        c = np.polyfit(s.conc, s.m, 2)
        return df.odm.apply(lambda y: min(r.real for r in np.roots([c[0], c[1], c[2] - y]) if abs(r.imag) < 1e-9 and r.real > -1))
    if method == "interp":
        return pd.Series(np.interp(df.odm, s.m, s.conc), index=df.index)

def two_way(d, y="y"):
    m = smf.ols(f"{y} ~ C(drink, Sum) * C(sleep, Sum)", d).fit()
    a3 = anova_lm(m, typ=3); a2 = anova_lm(smf.ols(f"{y} ~ C(drink, Sum) + C(sleep, Sum)", d).fit(), typ=2)
    mse, dfe = m.mse_resid, m.df_resid
    res = {"F_int": a3.iloc[3, 2], "p_int": a3.iloc[3, 3], "p_drink3": a3.iloc[1, 3], "p_sleep3": a3.iloc[2, 3],
           "p_drink2": a2.iloc[0, 3], "p_sleep2": a2.iloc[1, 3], "dfe": dfe}
    ss_e = a3.loc["Residual", "sum_sq"]
    for k, lab in [(1, "drink"), (2, "sleep"), (3, "int")]:
        res[f"np2_{lab}"] = a3.iloc[k, 0] / (a3.iloc[k, 0] + ss_e)
    g = d.groupby("group")[y]; mu, n = g.mean(), g.size()
    for sl in ["SD", "SL"]:  # Prism "compare within rows": S vs W within each sleep level, Sidak k=2
        diff = mu[f"S-{sl}"] - mu[f"W-{sl}"]; se = np.sqrt(mse * (1 / n[f"S-{sl}"] + 1 / n[f"W-{sl}"]))
        t = diff / se; p = 2 * stats.t.sf(abs(t), dfe); tc = stats.t.ppf(1 - (1 - (1 - 0.05) ** (1 / 2)) / 2, dfe)
        res[f"diff_{sl}"] = diff; res[f"p_{sl}_unadj"] = p; res[f"p_{sl}_sidak2"] = 1 - (1 - p) ** 2
        res[f"p_{sl}_sidak4"] = 1 - (1 - p) ** 4; res[f"ci_{sl}"] = (diff - tc * se, diff + tc * se)
        res[f"ci95_{sl}"] = (diff - stats.t.ppf(.975, dfe) * se, diff + stats.t.ppf(.975, dfe) * se)
        a_, b_ = d[d.group == f"S-{sl}"][y], d[d.group == f"W-{sl}"][y]
        gg = pg.compute_effsize(a_, b_, eftype="hedges"); res[f"g_{sl}"] = gg
        res[f"gci_{sl}"] = tuple(pg.compute_esci(stat=gg, nx=len(a_), ny=len(b_), eftype="hedges"))
    ic = (mu["S-SD"] - mu["W-SD"]) - (mu["S-SL"] - mu["W-SL"]); se = np.sqrt(mse * sum(1 / n))
    res["int_contrast"] = ic; res["int_ci95"] = (ic - stats.t.ppf(.975, dfe) * se, ic + stats.t.ppf(.975, dfe) * se)
    return res

def exact_perm(a, b):
    """Exact two-sided permutation test, difference in means, full enumeration."""
    x = np.r_[a, b]; na = len(a); obs = abs(np.mean(a) - np.mean(b)); tot = x.sum(); N = len(x)
    cnt = tot_n = 0
    for idx in itertools.combinations(range(N), na):
        sa = x[list(idx)].sum(); d = abs(sa / na - (tot - sa) / (N - na))
        cnt += d >= obs - 1e-12; tot_n += 1
    return cnt / tot_n

def freedman_lane(d, y="y", B=20000):
    """Permutation p for type-III interaction and main effects: permute residuals of reduced model."""
    full = "C(drink, Sum) * C(sleep, Sum)"; out = {}
    terms = {"int": ("C(drink, Sum) + C(sleep, Sum)", 3), "drink": ("C(sleep, Sum) + C(drink, Sum):C(sleep, Sum)", 1),
             "sleep": ("C(drink, Sum) + C(drink, Sum):C(sleep, Sum)", 2)}
    Fobs = anova_lm(smf.ols(f"{y} ~ {full}", d).fit(), typ=3)
    for k, (red, row) in terms.items():
        # reduced-model fit with Sum-coded interaction column built by hand to keep type-III meaning
        dd = d.copy(); dd["dc"] = np.where(dd.drink == "S", 1, -1); dd["sc"] = np.where(dd.sleep == "SD", 1, -1); dd["ic"] = dd.dc * dd.sc
        X = {"int": ["dc", "sc"], "drink": ["sc", "ic"], "sleep": ["dc", "ic"]}[k]
        Xr = np.c_[np.ones(len(dd)), dd[X].values]; Xf = np.c_[np.ones(len(dd)), dd[["dc", "sc", "ic"]].values]
        yv = dd[y].values; br = np.linalg.lstsq(Xr, yv, rcond=None)[0]; fit = Xr @ br; r = yv - fit
        col = {"int": 3, "drink": 1, "sleep": 2}[k]
        def Fstat(yy):
            bf, ssf = np.linalg.lstsq(Xf, yy, rcond=None)[:2]; ssf = ((yy - Xf @ bf) ** 2).sum()
            ssr = ((yy - Xr @ np.linalg.lstsq(Xr, yy, rcond=None)[0]) ** 2).sum()
            return (ssr - ssf) / (ssf / (len(yy) - 4))
        f0 = Fstat(yv); cnt = sum(Fstat(fit + rng.permutation(r)) >= f0 - 1e-12 for _ in range(B))
        out[k] = (cnt + 1) / (B + 1)
    return out

def describe(d, y="y"):
    g = d.groupby("group")[y]
    return pd.DataFrame({"n": g.size(), "mean": g.mean(), "sd": g.std(), "median": g.median()}).loc[["W-SD", "S-SD", "W-SL", "S-SL"]]

def report(name, d, y="y", perm=True):
    print(f"\n######## {name}")
    print(describe(d, y).round(4).to_string())
    r = two_way(d, y)
    print(f"TypeIII p: drink {r['p_drink3']:.4f} sleep {r['p_sleep3']:.4f} int {r['p_int']:.4f} (F={r['F_int']:.2f}, dfe={r['dfe']:.0f}); "
          f"np2 drink {r['np2_drink']:.3f} sleep {r['np2_sleep']:.3f} int {r['np2_int']:.3f}")
    print(f"TypeII additive p: drink {r['p_drink2']:.4f} sleep {r['p_sleep2']:.4f}")
    for sl in ["SD", "SL"]:
        print(f"  S-W within {sl}: diff {r[f'diff_{sl}']:.4f} 95%CI {np.round(r[f'ci95_{sl}'],4)} Sidak-CI {np.round(r[f'ci_{sl}'],4)} "
              f"p unadj {r[f'p_{sl}_unadj']:.4f} Sidak(k=2) {r[f'p_{sl}_sidak2']:.4f} (k=4) {r[f'p_{sl}_sidak4']:.4f}  "
              f"g {r[f'g_{sl}']:.2f} [{r[f'gci_{sl}'][0]:.2f}, {r[f'gci_{sl}'][1]:.2f}]")
    print(f"  interaction contrast {r['int_contrast']:.4f} 95%CI {np.round(r['int_ci95'],4)}")
    if perm:
        for sl in ["SD", "SL"]:
            a_, b_ = d[d.group == f"S-{sl}"][y].values, d[d.group == f"W-{sl}"][y].values
            print(f"  exact perm S vs W within {sl}: p={exact_perm(a_, b_):.4f}; MWU p={stats.mannwhitneyu(a_, b_, method='exact').pvalue:.4f}")
        fl = freedman_lane(d, y, 20000); print(f"  Freedman-Lane perm p: drink {fl['drink']:.4f} sleep {fl['sleep']:.4f} int {fl['int']:.4f}")
        sw = {gname: stats.shapiro(gd[y]).pvalue for gname, gd in d.groupby("group")}
        lev = stats.levene(*[gd[y] for _, gd in d.groupby("group")], center="median").pvalue
        m = smf.ols(f"{y} ~ C(drink, Sum) * C(sleep, Sum)", d).fit(); sr = m.get_influence().resid_studentized_external
        print(f"  Shapiro per group p: {dict((k, round(v,3)) for k,v in sw.items())}; Brown-Forsythe p={lev:.3f}; "
              f"max |ext. stud. resid| {np.abs(sr).max():.2f} at mouse {d.mouse.values[np.abs(sr).argmax()]}")
    return r

def loo(name, d, y="y"):
    rows = []
    for i in d.index:
        r = two_way(d.drop(i), y); rows.append(dict(mouse=d.loc[i, "mouse"], p_int=r["p_int"], p_drink=r["p_drink3"], p_sleep=r["p_sleep3"],
                                                    pSD=r["p_SD_sidak2"], pSL=r["p_SL_sidak2"]))
    L = pd.DataFrame(rows)
    print(f"  LOO {name}: ranges " + "; ".join(f"{c} [{L[c].min():.4f}, {L[c].max():.4f}]" for c in ["p_int", "p_drink", "p_sleep", "pSD", "pSL"]))
    base = two_way(d, y)
    for c, bk in [("p_int", "p_int"), ("p_drink", "p_drink3"), ("p_sleep", "p_sleep3"), ("pSD", "p_SD_sidak2"), ("pSL", "p_SL_sidak2")]:
        flips = L[(L[c] < .05) != (base[bk] < .05)].mouse.tolist()
        if flips: print(f"    {c} crosses 0.05 when dropping mice {flips}")

# ---------- curve checks
for assay in ["hippoSOD", "heartSOD"]:
    for plate, s in ST[ST.assay == assay].groupby("plate"):
        m = s[["od1", "od2"]].mean(1); b, a = fit_lin(s.conc, m); r2 = np.corrcoef(s.conc, m)[0, 1] ** 2
        bl = S[(S.assay == assay) & (S.plate.astype(str) == str(plate))].bg.mean()
        csv = m - bl; A0 = csv[s.conc == 0].iloc[0]; lr = A0 / csv; b2, a2 = fit_lin(s.conc, lr); r2b = np.corrcoef(s.conc, lr)[0, 1] ** 2
        lr0 = m.iloc[-1] / m; r2c = np.corrcoef(s.conc, lr0)[0, 1] ** 2
        print(f"{assay} plate {plate}: OD-linear slope {b:.4f} int {a:.4f} R2 {r2:.4f} | LR(blank={bl:.4f}) slope {b2:.2f} int {a2:.3f} R2 {r2b:.4f} | LR no blank R2 {r2c:.4f}")
s = ST[ST.assay == "MDA"]; m = s[["od1", "od2"]].mean(1); b, a = fit_lin(s.conc, m)
print(f"MDA: linear slope {b:.4f} int {a:.4f} R2 {np.corrcoef(s.conc, m)[0,1]**2:.4f}; residuals {np.round(m - (a + b * s.conc), 3).tolist()}")

# ---------- duplicates
S["cv"] = S[["od1", "od2"]].std(1, ddof=1) / S.odm * 100
S["cv_net"] = np.where(S.bg.notna(), (S.od1 - S.od2).abs() / np.sqrt(2) / (S.odm - S.bg.fillna(0)) * 100, S.cv)
print("\nDuplicate CV% (net of background) by assay/group: median, max, mice >10%")
for (a_, g_), d in S.groupby(["assay", "group"]):
    t = stats.ttest_rel(d.od1, d.od2)
    print(f"  {a_:8s} {g_}: median {d.cv_net.median():.1f} max {d.cv_net.max():.1f}  >10%: {d[d.cv_net > 10].mouse.tolist()}  "
          f"mean(od1-od2) {np.mean(d.od1 - d.od2):+.4f} paired p {t.pvalue:.3f}")

# ---------- SOD analyses
RES = {}
for assay in ["hippoSOD", "heartSOD"]:
    base = S[S.assay == assay].copy(); stds = ST[ST.assay == assay].copy()
    base["plate"] = base.plate.astype(str); stds["plate"] = stds.plate.astype(str)
    for meth in ["sheet", "sheet_noBG", "cayman", "cayman_noblank", "4pl"]:
        d = base.copy(); d["y"] = sod_values(d, stds, meth)
        if meth == "sheet":
            print(f"\n{assay} sheet-method per-mouse values:\n" + d[["group", "mouse", "y"]].round(4).to_string(index=False))
        RES[(assay, meth)] = report(f"{assay} [{meth}] U/mL homogenate", d, perm=(meth in ("sheet", "cayman")))
        if meth == "cayman": loo(f"{assay} cayman", d); d.to_csv(f"{D}/{assay}_cayman.csv", index=False)
        if meth == "cayman": print("  ratio cayman/sheet per mouse: ", np.round((d.y / sod_values(base, stds, 'sheet')).describe()[["min", "mean", "max"]].values, 2))
    if assay == "hippoSOD":
        for lab, drop in [("drop W-SL 27", [27])]:
            d = base.copy(); d["y"] = sod_values(d, stds, "cayman"); report(f"{assay} cayman, {lab}", d[~d.mouse.isin(drop)], perm=False)
    if assay == "heartSOD":
        d = base.copy(); d["y"] = sod_values(d, stds, "cayman"); d = d.merge(T[T.assay == "heartSOD"][["mouse", "tissue_mg", "buffer"]], on="mouse")
        d["ratio_uL_mg"] = d.buffer * 1000 / d.tissue_mg
        print("\nheart buffer:tissue ratio (uL/mg), off-protocol (|r-20|>0.2):\n" + d[(d.ratio_uL_mg - 20).abs() > 0.2][["group", "mouse", "tissue_mg", "buffer", "ratio_uL_mg", "y"]].round(3).to_string(index=False))
        d["y_mg"] = d.y * d.buffer / d.tissue_mg  # U per mg wet tissue
        report("heartSOD cayman, U/mg wet tissue (uses recorded buffer)", d, "y_mg", perm=True); loo("heart U/mg", d, "y_mg")
        report("heartSOD cayman U/mL, excluding off-ratio mice 6 and 24", d[~d.mouse.isin([6, 24])], perm=False)
        report("heartSOD cayman U/mg, excluding mice 6 and 24", d[~d.mouse.isin([6, 24])], "y_mg", perm=False)

# ---------- MDA
base = S[S.assay == "MDA"].copy(); stds = ST[ST.assay == "MDA"]
for meth in ["sheet", "drop5", "quad", "interp"]:
    d = base.copy(); d["y"] = mda_values(d, stds, meth)
    report(f"MDA [{meth}] nmol/well (fixed 30 uL/mg lysis, so proportional to nmol/mg)", d, perm=(meth == "sheet"))
    if meth == "sheet": loo("MDA sheet", d)
d = base.copy(); d["y"] = mda_values(d, stds, "sheet"); report("MDA sheet, drop S-SD 15", d[d.mouse != 15], perm=False)

# ---------- sensitivity: minimum detectable difference (80% power, alpha .05 two-sided) per simple contrast, in pooled SD units
from statsmodels.stats.power import tt_ind_solve_power
for n1, n2 in [(9, 9), (9, 8), (6, 6), (6, 5), (4, 5), (5, 5)]:
    print(f"MDE d (80% power, two-sided .05) n={n1} vs {n2}: {tt_ind_solve_power(None, n1, .05, .8, n2 / n1):.2f}; at alpha .025 (Sidak k=2): {tt_ind_solve_power(None, n1, .0253, .8, n2 / n1):.2f}")
