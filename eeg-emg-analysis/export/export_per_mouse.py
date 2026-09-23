#!/usr/bin/env python3
"""Split one .xdat recording into a well-organised per-mouse folder tree.

Deliberately NOT EDF. Produces, per rig position:

    <POS>/<POS>_raw_1000Hz.mat    MATLAB v5. eeg, emg (float32 uV), fs, t0_*.
                                  NO time vector is stored: at 1000 Hz it would
                                  double the file and push it past MATLAB v5's
                                  2 GB limit. Rebuild it in one line:
                                      t = (0:numel(eeg)-1)'/fs;
    <POS>/<POS>_raw_1000Hz.txt    time_s,eeg_uV,emg_uV -- OPT IN, pass --txt.
                                  ~3.7 GB per position, and a LOSSY copy of the
                                  .mat beside it: it rounds to 2 decimals, so
                                  61.815 uV is written 61.81. Three times the
                                  size of the .mat for less precision. It exists
                                  only for tools that cannot read MATLAB v5.
    <POS>/<POS>_hypnogram_4s.csv  per-epoch stage + features (stageable only)
    <POS>/<POS>_summary.txt       the staging verdict and its caveats
    <POS>/<POS>_info.json         provenance: channels, QC, verdict, timing

⚠️ The signals are ALREADY the bipolar difference the RHD2216 produces.
   Do not subtract anything from them.
"""
import argparse, json, os, shutil, sys, glob
import datetime as dt
import numpy as np
from scipy.io import savemat

sys.path.insert(0, '/home/skimlab/Monitoring_project/eeg-emg-analysis')
from core import criteria as C

CHUNK = 2_000_000          # rows per text-write chunk


def export(base, outroot, positions, roles, hypno_dir, want_text=False):
    x, labels, fs, n = C.open_xdat(base)
    spec = C.CohortSpec(roles=tuple(roles))
    meta_path = base + '.xdat.json'
    meta = json.load(open(meta_path))
    t0_utc = meta.get('status', {}).get('t0_datetime_utc') or meta.get('t0_datetime_utc')

    name = os.path.basename(base)
    root = os.path.join(outroot, name)
    os.makedirs(root, exist_ok=True)
    manifest = []

    for pos in positions:
        sites = spec.animal_sites()[pos]
        eeg_s, emg_s = sites['eeg'], sites['emg']
        ce, cg = labels.index(eeg_s), labels.index(emg_s)
        d = os.path.join(root, pos)
        os.makedirs(d, exist_ok=True)
        print(f'[{pos}] {eeg_s} + {emg_s} -> {d}', flush=True)

        eeg = np.asarray(x[:, ce], dtype=np.float32)
        emg = np.asarray(x[:, cg], dtype=np.float32)

        # ---- MATLAB ---------------------------------------------------------
        mat = os.path.join(d, f'{pos}_raw_1000Hz.mat')
        savemat(mat, {
            'eeg': eeg, 'emg': emg, 'fs': np.int32(fs),
            'position': pos, 'eeg_channel': eeg_s, 'emg_channel': emg_s,
            'units': 'microvolts', 'recording': name,
            't0_local_iso': meta.get('status', {}).get('t0_datetime_local', '') or '',
            't0_utc_iso': t0_utc or '',
            'note': ('signals are already bipolar; do not subtract. '
                     'time vector: t = (0:numel(eeg)-1)./double(fs)'),
        }, do_compression=False, format='5')
        print(f'   mat  {os.path.getsize(mat)/1e9:.2f} GB', flush=True)

        # ---- text -----------------------------------------------------------
        txt = os.path.join(d, f'{pos}_raw_1000Hz.txt')
        if want_text:
            with open(txt, 'w', buffering=1 << 22) as fh:
                fh.write('time_s,eeg_uV,emg_uV\n')
                for i in range(0, n, CHUNK):
                    j = min(i + CHUNK, n)
                    t = (np.arange(i, j, dtype=np.float64) / fs)
                    blk = np.column_stack([t, eeg[i:j], emg[i:j]])
                    np.savetxt(fh, blk, fmt='%.3f,%.2f,%.2f')
                    if (i // CHUNK) % 20 == 0:
                        print(f'   txt  {100*j/n:5.1f}%', end='\r', flush=True)
            print(f'   txt  {os.path.getsize(txt)/1e9:.2f} GB', flush=True)

        # ---- hypnogram + summary, if this position was staged ---------------
        port, slot = pos[0], pos[1]
        stem = f'port{port}-slot{slot}_'
        hyp = glob.glob(os.path.join(hypno_dir, stem + '*_hypnogram.csv'))
        summ = glob.glob(os.path.join(hypno_dir, stem + '*_summary.txt'))
        feat = glob.glob(os.path.join(hypno_dir, stem + '*_features.json'))
        staged = bool(hyp)
        if hyp:  shutil.copy(hyp[0],  os.path.join(d, f'{pos}_hypnogram_4s.csv'))
        if summ: shutil.copy(summ[0], os.path.join(d, f'{pos}_summary.txt'))
        if feat: shutil.copy(feat[0], os.path.join(d, f'{pos}_features.json'))

        info = {'position': pos, 'recording': name,
                'eeg_channel': eeg_s, 'emg_channel': emg_s,
                'fs_hz': int(fs), 'n_samples': int(n),
                'duration_h': round(n / fs / 3600, 4),
                't0_utc': t0_utc, 'units': 'microvolts',
                'bipolar': True, 'subtract_anything': False,
                'hypnogram_present': staged,
                'files': sorted(os.listdir(d))}
        json.dump(info, open(os.path.join(d, f'{pos}_info.json'), 'w'), indent=2)
        manifest.append(info)

    json.dump({'recording': name, 'exported': dt.datetime.now().isoformat(),
               'positions': manifest},
              open(os.path.join(root, 'manifest.json'), 'w'), indent=2)
    print(f'\n-> {root}')
    return root


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('base')
    ap.add_argument('--out', default='/home/skimlab/eeg-processed/per-mouse')
    ap.add_argument('--positions', default='A1,A2,B1,B2,C1,C2,D1,D2')
    ap.add_argument('--roles', default='eeg,emg')
    ap.add_argument('--hypno-dir', default='/home/skimlab/eeg-processed/2026-08-19')
    # OPT IN since 2026-09-23. It used to be written every time, which put 27.6 GB
    # of rounded text on the rig for ONE recording - three times the size of the
    # .mat holding the same signal at full precision. Anything that can read
    # MATLAB v5 should read the .mat.
    ap.add_argument('--txt', action='store_true',
                    help='also write <POS>_raw_1000Hz.txt, ~3.7 GB per position, '
                         'rounded to 2 decimals. The .mat is smaller and exact.')
    # Accepted and ignored: callers that still pass it get the new default rather
    # than an argparse error.
    ap.add_argument('--skip-text', action='store_true',
                    help=argparse.SUPPRESS)
    a = ap.parse_args()
    export(a.base, a.out, a.positions.split(','), a.roles.split(','),
           a.hypno_dir, a.txt and not a.skip_text)
