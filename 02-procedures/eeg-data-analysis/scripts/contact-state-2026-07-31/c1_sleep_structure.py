"""
Does the C1 bipolar EEG window contain SLEEP STRUCTURE? (2026-08-01: answer = NO)

Runs four independent tests on the epoch table from c1_window.py. Each test is
written so that a NEGATIVE result is visible, because the 2026-07-15 retraction
happened by reporting a positive without checking the failure modes.

Usage:  python3 c1_sleep_structure.py [path/to/c1_window.npz]
"""
import sys
import numpy as np

NPZ = sys.argv[1] if len(sys.argv) > 1 else 'c1_window.npz'
d = np.load(NPZ)
delta, theta, tot = d['delta'], d['theta'], d['tot']
rms, clip, mains = d['rms'], d['clip'], d['mains']
EP = int(d['ep'])
n = len(delta)
hours = np.arange(n) * EP / 3600.0

# --- GATE 0: clipped epochs are excluded BEFORE anything is computed ---------
# This is the 2026-07-15 lesson. A railed amplifier is non-linear and its
# spectrum is meaningless, so every downstream number must be conditioned on
# clean epochs, and the CLEAN FRACTION must be reported alongside the result.
clean = clip < 0.001
print(f'epochs {n} = {n*EP/3600:.2f} h')
print(f'CLEAN epochs (0% clipped): {clean.sum()} / {n} = {100*clean.mean():.1f}%')
if clean.sum() < 60:
    sys.exit('UNSCOREABLE: too few clean epochs')

print(f'mains on bipolar: median {np.median(mains):.1f} uV  '
      f'p90 {np.percentile(mains, 90):.1f}')
print(f'rms 0.5-45Hz: median {np.median(rms):.1f} uV  '
      f'p10 {np.percentile(rms[clean], 10):.1f}  p90 {np.percentile(rms[clean], 90):.1f}')

dt = delta[clean] / theta[clean]
lg = np.log10(dt)
print(f'\ndelta/theta: median {np.median(dt):.2f}  '
      f'p10 {np.percentile(dt, 10):.2f}  p90 {np.percentile(dt, 90):.2f}')
print(f'delta as % of 0.5-45 total: median {100*np.median(delta[clean]/tot[clean]):.1f}%')

# --- TEST 1: BIMODALITY -----------------------------------------------------
# Sleep/wake should split log(delta/theta) into two modes. One smooth peak = no
# state separation.
print('\nTEST 1 — bimodality of log10(delta/theta):')
hist, edges = np.histogram(lg, bins=20)
for i in range(20):
    print(f'  {edges[i]:6.2f}..{edges[i+1]:6.2f} '
          f'{"#" * int(60*hist[i]/hist.max())} {hist[i]}')

# --- TEST 2: TEMPORAL PERSISTENCE -------------------------------------------
# Mouse NREM bouts last MINUTES. Compare against a shuffle control so that
# "structure exists" cannot be confused with "structure is on the right scale".
x = lg - lg.mean()
ac = np.correlate(x, x, 'full')[len(x)-1:]
ac /= ac[0]
print('\nTEST 2 — autocorrelation of log(delta/theta):')
for k in [1, 3, 6, 12, 30, 60, 120, 360]:
    if k < len(ac):
        print(f'   lag {k*EP:5d}s ({k*EP/60:5.1f} min): r = {ac[k]:+.3f}')
rng = np.random.default_rng(0)
xs = rng.permutation(x)
acs = np.correlate(xs, xs, 'full')[len(xs)-1:]
acs /= acs[0]
print(f'   SHUFFLE CONTROL lag {EP}s: r = {acs[1]:+.3f}')

# --- TEST 3: BOUT LENGTH ----------------------------------------------------
# Random epoch-to-epoch switching gives a median run of 2 epochs. Real states
# give much longer runs. This is the decisive test.
hi = lg > np.median(lg)
runs, cur, L = [], hi[0], 1
for v in hi[1:]:
    if v == cur:
        L += 1
    else:
        runs.append((cur, L)); cur, L = v, 1
runs.append((cur, L))
hl = [L for v, L in runs if v]
ll = [L for v, L in runs if not v]
print('\nTEST 3 — bout lengths around the median:')
print(f'   high-delta runs: n={len(hl)} median {np.median(hl)*EP:.0f}s  max {max(hl)*EP:.0f}s')
print(f'   low-delta  runs: n={len(ll)} median {np.median(ll)*EP:.0f}s  max {max(ll)*EP:.0f}s')
print(f'   RANDOM EXPECTATION: median run = {2*EP}s')

# --- TEST 4: AMPLITUDE / DELTA COVARIATION ----------------------------------
# Physiological positive control. Real synchronised cortical activity is both
# SLOWER and BIGGER, so rms must rise with the delta ratio. Noise does not.
print('\nTEST 4 — amplitude vs delta ratio (real NREM = bigger AND more delta):')
q = np.quantile(lg, [0, .25, .5, .75, 1.])
for i in range(4):
    msk = (lg >= q[i]) & (lg <= q[i+1])
    print(f'   d/t quartile {i+1}: rms {np.median(rms[clean][msk]):6.1f} uV   '
          f'delta% {100*np.median((delta[clean]/tot[clean])[msk]):5.1f}')

# --- hourly profile: circadian / homeostatic trend --------------------------
print('\nHourly profile (clean epochs only):')
print(f'{"hour":>5s} {"n":>5s} {"rms":>7s} {"delta%":>7s} {"theta%":>7s} {"d/t":>6s} {"mains":>7s}')
for k in range(int(np.ceil(hours[-1]))):
    msk = (hours >= k) & (hours < k+1) & clean
    if msk.sum() < 10:
        print(f'{k:5d} {msk.sum():5d}   (too few clean epochs)')
        continue
    print(f'{k:5d} {msk.sum():5d} {np.median(rms[msk]):7.1f} '
          f'{100*np.median(delta[msk]/tot[msk]):7.1f} '
          f'{100*np.median(theta[msk]/tot[msk]):7.1f} '
          f'{np.median(delta[msk]/theta[msk]):6.2f} {np.median(mains[msk]):7.1f}')
