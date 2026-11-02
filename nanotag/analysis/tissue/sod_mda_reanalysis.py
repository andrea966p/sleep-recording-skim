"""Re-derive SOD and MDA values from the raw ODs in raw/SOD1-biochem_raw_data.xlsx and test them.
Usage: python sod_mda_reanalysis.py raw/SOD1-biochem_raw_data.xlsx  (needs openpyxl scipy pandas statsmodels)"""
import sys, itertools, numpy as np, pandas as pd, openpyxl
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm

wb = openpyxl.load_workbook(sys.argv[1], data_only=True)
def rows(ws): return [list(r) for r in ws.iter_rows(values_only=True) if any(c is not None for c in r)]

# ---------- standard-curve helpers ----------
def fit_lin(x, y):
    b, a = np.polyfit(x, y, 1); return a, b
def cayman_lr(std_conc, std_od, od):
    """Cayman 706002: linearized rate LR = A0/A, linear in SOD (U/mL)."""
    a0 = std_od[np.argmin(std_conc)]
    a, b = fit_lin(std_conc, a0 / np.asarray(std_od))
    return (a0 / np.asarray(od) - a) / b

# ---------- hippocampus SOD (two plates) ----------
H = rows(wb['0922 Hippocampus'])
def block(r0):  # ids row index, OD1, OD2, BG
    ids = [v for v in H[r0][2:] if v is not None]
    n = len(ids)
    return ids, np.array(H[r0+1][2:2+n], float), np.array(H[r0+2][2:2+n], float), np.array(H[r0+3][2:2+n], float), np.array(H[r0+8][2:2+n], float)
conc = np.array(H[1][2:9], float)
plate = {1: np.array(H[4][2:9], float), 2: np.array(H[26][2:9], float)}
recs = []
for r0, grp, pl in [(5, 'W-SD', 1), (14, 'S-SD', 1), (27, 'W-SL', 2), (36, 'S-SL', 2)]:
    ids, o1, o2, bg, theirs = block(r0)
    od = (o1 + o2) / 2
    std = plate[pl]
    a, b = fit_lin(conc, std)
    lin_bg = ((od - bg) - a) / b * 50          # reproduce sheet: linear on OD, BG subtracted
    lr_raw = cayman_lr(conc, std, od) * 50     # Cayman method, no BG subtraction
    lr_bg = cayman_lr(conc, std, od - bg) * 50
    for i, m in enumerate(ids):
        recs.append(dict(tissue='hippo_SOD', group=grp, mouse=int(m), plate=pl, sheet=theirs[i],
                         lin_bg=lin_bg[i], lr_raw=lr_raw[i], lr_bg=lr_bg[i], dup_cv=abs(o1[i]-o2[i])/od[i]))
hip = pd.DataFrame(recs)
print('hippo: max |sheet - reproduced linear| =', (hip.sheet - hip.lin_bg).abs().max().round(4))
for pl in (1, 2):
    a, b = fit_lin(conc, plate[pl]); r = np.corrcoef(conc, plate[pl])[0, 1]
    a0 = plate[pl][-1]; rl = np.corrcoef(conc, a0/plate[pl])[0, 1]
    print(f'  plate {pl}: linear-OD r2={r*r:.4f}  LR r2={rl*rl:.4f}')

# ---------- heart SOD (one plate) ----------
Hh = rows(wb['SOD1-Heart'])
meta = {}
for r0 in (1, 5):
    ids = [v for v in Hh[r0][2:] if v is not None]
    for i, m in enumerate(ids):
        meta[int(m)] = dict(mg=Hh[r0+1][2+i], buf=Hh[r0+2][2+i])
hconc = np.array(Hh[8][2:9], float); hstd = np.array(Hh[11][2:9], float)
recs = []
for r0, groups in [(13, ('W-SD', 'S-SD')), (26, ('W-SL', 'S-SL'))]:
    idrow = Hh[r0]; o1row, o2row, bgrow = Hh[r0+1], Hh[r0+2], Hh[r0+3]; avgrow = Hh[r0+10]
    for c in range(2, len(idrow)):
        if idrow[c] is None: continue
        g = groups[0] if c < 9 else groups[1]
        od = (o1row[c] + o2row[c]) / 2; bg = bgrow[c]
        a, b = fit_lin(hconc, hstd)
        m = int(idrow[c])
        recs.append(dict(tissue='heart_SOD', group=g, mouse=m, sheet=avgrow[c],
                         lin_bg=((od-bg)-a)/b*50, lr_raw=cayman_lr(hconc, hstd, od)*50,
                         lr_bg=cayman_lr(hconc, hstd, od-bg)*50, dup_cv=abs(o1row[c]-o2row[c])/od,
                         mg=meta[m]['mg'], buf=meta[m]['buf']))
hea = pd.DataFrame(recs)
hea['uL_per_mg'] = hea.buf * 1000 / hea.mg
hea['U_per_mg'] = hea.sheet * hea.buf / hea.mg          # with recorded buffer
print('heart: max |sheet - reproduced linear| =', (hea.sheet - hea.lin_bg).abs().max().round(4))
a0 = hstd[-1]; print(f'  heart plate: linear-OD r2={np.corrcoef(hconc,hstd)[0,1]**2:.4f}  LR r2={np.corrcoef(hconc,a0/hstd)[0,1]**2:.4f}')
print(hea.loc[(hea.uL_per_mg-20).abs() > 1, ['group','mouse','mg','buf','uL_per_mg','sheet','U_per_mg']])

# ---------- hippocampus MDA ----------
M = rows(wb['MDA-Hippo'])
mmeta = {}
for r0, gs in [(1, ('W-SD', 'S-SD')), (5, ('W-SL', 'S-SL'))]:
    ids = M[r0][2:]
    for i, m in enumerate(ids):
        if m is None: continue
        mmeta[(gs[0] if i < 6 else gs[1], int(m))] = M[r0+1][2+i]
mconc = np.array(M[8][2:8], float); mstd = np.array(M[11][2:8], float)
ma, mb = fit_lin(mconc, mstd)
print(f'MDA std r2={np.corrcoef(mconc,mstd)[0,1]**2:.4f}')
recs = []
for r0, gs in [(13, ('W-SD', 'S-SD')), (21, ('W-SL', 'S-SL'))]:
    idrow, o1, o2, avg = M[r0], M[r0+1], M[r0+2], M[r0+5]
    for c in range(len(idrow)):
        if not isinstance(idrow[c], (int, float)) or c == 0: continue
        g = gs[0] if c < 8 else gs[1]
        od = (o1[c] + o2[c]) / 2
        recs.append(dict(tissue='hippo_MDA', group=g, mouse=int(idrow[c]), sheet=avg[c],
                         lin_bg=(od - ma) / mb, dup_cv=abs(o1[c]-o2[c])/od,
                         mg_table=mmeta.get((g, int(idrow[c])))))
mda = pd.DataFrame(recs)
print('MDA: max |sheet - (OD-intercept)/slope| =', (mda.sheet - mda.lin_bg).abs().max().round(4))
print('MDA ids in data rows without a tissue weight:', mda.loc[mda.mg_table.isna(), ['group','mouse']].values.tolist())

# ---------- statistics ----------
def two_way(df, col):
    d = df.assign(sod=df.group.str[0].map({'W': 'water', 'S': 'SOD1'}), sleep=df.group.str[2:].map({'SD': 'CSD', 'SL': 'NSL'}))
    fit = smf.ols(f'{col} ~ C(sod, Sum) * C(sleep, Sum)', d).fit()
    tab = anova_lm(fit, typ=3).iloc[1:4]
    resid = fit.resid
    out = {k.replace('C(sod, Sum)', 'SOD').replace('C(sleep, Sum)', 'sleep'): (round(v.F, 2), round(v['PR(>F)'], 4)) for k, v in tab.iterrows()}
    # permutation of the interaction / main effects via cell-label shuffling (approximate, 20000)
    rng = np.random.default_rng(0); y = d[col].values; lab = d.group.values
    def stats_of(lbl):
        m = {g: y[lbl == g].mean() for g in ('W-SD', 'S-SD', 'W-SL', 'S-SL')}
        return np.array([(m['S-SD']+m['S-SL'])-(m['W-SD']+m['W-SL']), (m['W-SD']+m['S-SD'])-(m['W-SL']+m['S-SL']), (m['S-SD']-m['S-SL'])-(m['W-SD']-m['W-SL'])]) / 2
    obs = stats_of(lab); null = np.array([stats_of(rng.permutation(lab)) for _ in range(20000)])
    perm = ((np.abs(null) >= np.abs(obs) - 1e-12).sum(0) + 1) / 20001
    sw = stats.shapiro(resid).pvalue; lev = stats.levene(*[y[lab == g] for g in ('W-SD','S-SD','W-SL','S-SL')]).pvalue
    return out, dict(zip(['SOD', 'sleep', 'SODxsleep'], perm.round(4))), round(sw, 3), round(lev, 3), d

def welch(a, b):
    t = stats.ttest_ind(a, b, equal_var=False); d = a.mean() - b.mean()
    se = np.sqrt(a.var(ddof=1)/len(a) + b.var(ddof=1)/len(b))
    df_ = se**4 / ((a.var(ddof=1)/len(a))**2/(len(a)-1) + (b.var(ddof=1)/len(b))**2/(len(b)-1))
    q = stats.t.ppf(.975, df_)
    sp = np.sqrt(((len(a)-1)*a.var(ddof=1)+(len(b)-1)*b.var(ddof=1))/(len(a)+len(b)-2))
    g = d/sp*(1-3/(4*(len(a)+len(b))-9))
    # exact permutation of the difference in means
    pool = np.r_[a, b]; n = len(a); cnt = tot = 0
    for idx in itertools.combinations(range(len(pool)), n):
        m = np.zeros(len(pool), bool); m[list(idx)] = True
        tot += 1; cnt += abs(pool[m].mean()-pool[~m].mean()) >= abs(d) - 1e-12
    return dict(diff=round(d, 3), ci=(round(d-q*se, 3), round(d+q*se, 3)), pct=round(100*d/b.mean(), 1), g=round(g, 2), p_welch=round(t.pvalue, 4), p_perm=round(cnt/tot, 4))

def sidak(p, k=4): return min(1, 1-(1-p)**k)

for name, df, cols in [('HIPPOCAMPUS SOD (U/mL lysate; plate 1 = SD groups, plate 2 = SL groups)', hip, ['sheet', 'lr_raw']),
                       ('HEART SOD', hea, ['sheet', 'lr_raw', 'U_per_mg']),
                       ('HIPPOCAMPUS MDA (nmol per well)', mda, ['sheet'])]:
    print('\n=====', name)
    print(df.groupby('group')[cols].agg(['mean', 'std', 'count']).round(3).reindex(['W-SL','S-SL','W-SD','S-SD']))
    for col in cols:
        anv, perm, sw, lev, d = two_way(df, col)
        print(f'  [{col}] typeIII ANOVA (F,p): {anv}\n      permutation p: {perm}  Shapiro resid p={sw}  Levene p={lev}')
        for a_, b_ in [('W-SD','W-SL'), ('S-SD','S-SL'), ('S-SL','W-SL'), ('S-SD','W-SD')]:
            r = welch(df.loc[df.group == a_, col].values, df.loc[df.group == b_, col].values)
            print(f'      {a_} vs {b_}: {r}  Sidak(4) Welch p={sidak(r["p_welch"]):.4f}')
    # leave-one-out on the key contrast for the first column
    col = cols[-1] if name.startswith('HEART') else cols[0]
    print('  LOO interaction p range:', end=' ')
    ps = []
    for i in df.index:
        ps.append(two_way(df.drop(i), col)[0]['SOD:sleep'][1] if 'SOD:sleep' in two_way(df.drop(i), col)[0] else None)
    print(min(ps), max(ps))
    print('  max duplicate CV %:', round(100*df.dup_cv.max(), 1), ' median', round(100*df.dup_cv.median(), 1))
    print(df.sort_values(['group','mouse'])[['group','mouse']+cols].round(3).to_string(index=False))

# cross-tissue
x = hip.set_index(['group','mouse']).sheet; y = mda.set_index(['group','mouse']).sheet; z = hea.set_index(['group','mouse']).sheet
j = pd.concat([x.rename('hipSOD'), y.rename('MDA'), z.rename('heartSOD')], axis=1)
print('\nmice with all three:', j.dropna().shape[0])
for a_, b_ in [('hipSOD','MDA'), ('hipSOD','heartSOD'), ('MDA','heartSOD')]:
    jj = j[[a_, b_]].dropna(); r = stats.spearmanr(jj[a_], jj[b_])
    print(f'  {a_} vs {b_}: n={len(jj)} spearman rho={r.statistic:.2f} p={r.pvalue:.3f}')
# MDA vs tissue mass
mm = mda.dropna(subset=['mg_table'])
print('MDA tissue mg by group:', mda.groupby('group').mg_table.mean().round(1).to_dict())
print('MDA vs mg (spearman, all):', stats.spearmanr(mm.mg_table, mm.sheet))
print('heart mg by group:', hea.groupby('group').mg.mean().round(0).to_dict())
