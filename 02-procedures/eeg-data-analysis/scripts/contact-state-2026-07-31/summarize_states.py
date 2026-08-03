"""
Per-leg connection-state summary + state timelines from longrun_coarse.npz.

Produces the duty-cycle table and the OPEN/CONNECTED segment lists reported in
05-experiments/completed/2026-08-01-28h-contact-duty-cycle-and-c1-negative.md

Usage:  python3 summarize_states.py [path/to/longrun_coarse.npz]
"""
import sys
import numpy as np

NPZ = sys.argv[1] if len(sys.argv) > 1 else 'longrun_coarse.npz'

# --- THE ONE FREE PARAMETER -------------------------------------------------
# OPEN threshold on 55-65 Hz band RMS, in microvolts.
# Chosen from the 2026-07-31 bimodality: legs land either <150 uV or >500 uV,
# with a single value in between (525). 300 sits in that empty gap, so the
# classification is insensitive to the exact number. See the sensitivity check
# at the bottom of this script.
OPEN_UV = 300
# Biology threshold on 0.5-45 Hz band RMS. A leg can be quiet AND dead (shorted
# to ground), so "not open" is NOT the same as "usable".
BIO_UV = 25
# ----------------------------------------------------------------------------

d = np.load(NPZ, allow_pickle=True)
m, b, c = d['mains'], d['bio'], d['clip']
names = list(map(str, d['names']))
nlegs = int(d['nlegs'])
starts = d['starts']
hours = starts / 3600.0

print(f'windows {m.shape}   span {hours[-1]:.2f} h')

# --- control pins: amplifier floor + animal grounds --------------------------
ctrl = m[:, nlegs:]
print(f'\nCONTROL tied-floor pins: median {np.median(ctrl):.1f} uV  '
      f'p99 {np.percentile(ctrl, 99):.1f}  max {ctrl.max():.1f}')
print('  per-control medians:', np.round(np.median(ctrl, 0), 1))

# --- per-leg duty cycle ------------------------------------------------------
print(f'\n{"leg":12s} {"med":>7s} {"p10":>7s} {"p90":>7s} '
      f'{"%OPEN":>6s} {"%bio":>6s} {"flips":>6s} {"clip%":>6s}')
for i in range(nlegs):
    mm, bb = m[:, i], b[:, i]
    op = mm > OPEN_UV
    flips = int(np.sum(op[1:] != op[:-1]))
    usable = (~op) & (bb > BIO_UV)
    print(f'{names[i]:12s} {np.median(mm):7.0f} {np.percentile(mm, 10):7.0f} '
          f'{np.percentile(mm, 90):7.0f} {100*op.mean():6.1f} '
          f'{100*usable.mean():6.1f} {flips:6d} {100*c[:, i].mean():6.2f}')

# --- state timelines ---------------------------------------------------------
def timeline(name, min_minutes=3.0):
    i = names.index(name)
    op = m[:, i] > OPEN_UV
    segs, cur, s0 = [], op[0], 0
    for j in range(1, len(op)):
        if op[j] != cur:
            segs.append((cur, hours[s0], hours[j]))
            cur, s0 = op[j], j
    segs.append((cur, hours[s0], hours[-1]))
    print(f'\n{name}: segments longer than {min_minutes:g} min')
    for o, a, z in segs:
        if (z - a) * 60 >= min_minutes:
            print(f'   {"OPEN " if o else "CONN "} {a:6.2f}h -> {z:6.2f}h  '
                  f'({(z-a)*60:6.1f} min)')

for n in ['C1/front', 'C1/pariet', 'B1/front', 'C2/front', 'D2/front', 'B2/EMG+']:
    timeline(n)

# --- sensitivity: does the verdict depend on OPEN_UV? ------------------------
print('\nSENSITIVITY of %OPEN to the threshold (should be nearly flat):')
for thr in [150, 200, 300, 400, 600]:
    frac = np.mean(m[:, :nlegs] > thr)
    print(f'   OPEN_UV={thr:4d} -> {100*frac:.1f}% of all leg-windows OPEN')
