"""Prism-style Sidak after two-way ANOVA: pooled residual MS, df = N - 4, families of 2 and 4 comparisons."""
import numpy as np
from scipy import stats
D = {
 'hippo_SOD': {'W-SD':[1.875,2.159,1.674,2.081,1.930,1.889,1.802,1.834,2.186],'S-SD':[1.811,1.853,2.058,2.058,2.109,1.953,1.926,2.090,1.985],
               'W-SL':[1.802,1.869,1.802,1.949,1.785,1.842,2.212,1.865,1.851],'S-SL':[1.740,1.767,1.736,1.834,1.949,1.847,1.838,1.758]},
 'heart_SOD': {'W-SD':[2.180,2.008,1.785,2.113,2.225,2.102],'S-SD':[1.957,1.879,1.879,1.684,1.807,1.606],
               'W-SL':[1.774,1.712,1.930,1.640,1.729,1.991],'S-SL':[1.913,1.918,1.874,2.108,1.952,2.197]},
 'hippo_MDA': {'W-SD':[1.988,1.685,1.920,1.348,1.416,1.753],'S-SD':[1.671,1.569,1.552,2.360,1.845],
               'W-SL':[1.583,1.358,1.521,1.119,1.620,1.613],'S-SL':[1.123,1.559,1.300,1.429,1.443,1.576]}}
for k, d in D.items():
    g = {a: np.array(v) for a, v in d.items()}
    N = sum(len(v) for v in g.values()); dfe = N - 4
    mse = sum(((v - v.mean())**2).sum() for v in g.values()) / dfe
    print(f'== {k}  pooled SD {np.sqrt(mse):.3f}, df {dfe}')
    for a, b in [('W-SD','W-SL'),('S-SD','S-SL'),('S-SL','W-SL'),('S-SD','W-SD')]:
        t = (g[a].mean()-g[b].mean())/np.sqrt(mse*(1/len(g[a])+1/len(g[b]))); p = 2*stats.t.sf(abs(t), dfe)
        print(f'  {a} vs {b}: diff {g[a].mean()-g[b].mean():+.3f}  p {p:.4f}  Sidak k=2 {1-(1-p)**2:.4f}  k=4 {1-(1-p)**4:.4f}')
    # robustness: drop the single most extreme point per group and the S-SD MDA high value
    if k == 'hippo_MDA':
        h = dict(g); h['S-SD'] = h['S-SD'][h['S-SD'] < 2.3]
        allv = np.concatenate(list(h.values())); 
        import itertools
        print('  without HLBSSD15 (2.36): S-SD mean', h['S-SD'].mean().round(3), 'S-SD vs S-SL Welch p', stats.ttest_ind(h['S-SD'], h['S-SL'], equal_var=False).pvalue.round(4),
              ' sleep main (OLS):', end=' ')
        import pandas as pd, statsmodels.formula.api as smf
        from statsmodels.stats.anova import anova_lm
        df = pd.DataFrame([(a, x) for a, v in h.items() for x in v], columns=['grp','y']); df['sod']=df.grp.str[0]; df['sl']=df.grp.str[2:]
        print(anova_lm(smf.ols('y ~ C(sod,Sum)*C(sl,Sum)', df).fit(), typ=3).iloc[1:4]['PR(>F)'].round(4).to_dict())
