#!/usr/bin/env python3
"""THE EMG GATE: does muscle tone actually fall when the animal sleeps?

WHY THIS IS THE GATE, AND WHY IT COMES BEFORE THE KAPPA
-------------------------------------------------------
Sleep staging on this rig begins with an EMG threshold: high muscle tone is WAKE,
and everything downstream -- the NREM/REM split, the bout structure, the
persistence statistic, the circadian check -- is computed inside whatever the EMG
cut leaves behind. If EMG does not track state in the animals we intend to
publish, there is no scorer, and a blind-scoring kappa would spend a human's
hours certifying agreement about noise.

As of 2026-08-09 EMG state dependence had been demonstrated on exactly ONE animal
(A2, r = -0.651), which is the OLD cohort's control and is not in the publishable
set. The best re-pinned mouse reached -0.175 and one was +0.053, the wrong sign
entirely. The 2026-08-08 dark phase -- where a nocturnal animal does most of its
waking, and therefore where the EMG contrast should be largest -- had never been
analysed at all.

So this script asks the question on the full recording, per animal, split by
light and dark phase.

THE MEASUREMENT
---------------
r = Pearson correlation, over 1-minute bins, between
      EMG amplitude   (rms, uV)
      EEG delta ratio (1-4 Hz share of 1-40 Hz)
computed ONLY over minutes where that animal's OWN EEG passes the slope criterion
against the wire-free floor in the same file.

A working pair gives a NEGATIVE r: when the EEG goes delta-rich the animal is
asleep, and the neck muscle goes quiet. Noise gives ~0. A POSITIVE r means the
"EMG" channel is following the EEG rather than opposing it, which is what a
shared artefact path does.

⚠️ RESTRICTING TO USABLE EEG MINUTES IS NOT OPTIONAL AND IT IS NOT NEUTRAL. If
the EEG channel is open, its delta ratio is a property of the amplifier, and
correlating anything against it measures nothing. It does mean the test is only
as good as the EEG, so an animal with no usable EEG returns "cannot ask" rather
than a number -- INSUFFICIENT, not FAIL.

⚠️ THIS TEST CANNOT PROVE THE EMG IS GOOD, ONLY THAT IT IS COUPLED TO STATE. A
strong negative r on a channel that is actually picking up EEG bleed would look
identical. It is a necessary condition, not a sufficient one.

Usage
    python qc/emg_state_dependence.py <recording> [--hours N] [--cohort-roles 3]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys

import numpy as np

from core import criteria as C
from core import paths as PATHS
from core import qc_thresholds as T

EPOCHS_PER_MIN = 60 // T.EPOCH_S_QC        # 10 s QC epochs -> 6 per minute
MIN_MINUTES = 20                            # below this, r is not reportable
USABLE_MIN_FRACTION = 0.8                   # of the epochs in a minute

# --- test 2: burstiness -- DIAGNOSTIC ONLY, NOT A VERDICT ----------------- #
BURST_BAND = (30.0, 300.0)   # muscle band, above the EEG and below the anti-alias
BURST_WINDOW_EPOCHS = 30     # 5 min of 10 s epochs
BURST_CV_MARGIN = 1.5        # x the floor's own burst_cv, measured in the same file
#
# The idea: real muscle FIRES IN BURSTS, so a working EMG channel has a highly
# variable 1 s amplitude envelope, while stationary amplifier noise does not. It
# needs no EEG, which is attractive because three of seven animals on 2026-08-08
# had no usable EEG and the state-dependence test cannot even be asked of them.
#
# 🔴 IT DOES NOT WORK ON THIS RIG, AND THE ANIMAL THAT BREAKS IT IS A1.
# MEASURED 2026-08-10 on allego_0__uid0808-16-17-36, floor burst_cv 0.213, bar
# 0.319:
#     A1  0.769  "bursty"     <- A1 HAS NO GROUND AT ALL. It is the floating
#                                control. It cannot be recording muscle.
#     C1  1.394  "bursty"     <- C1 has ZERO usable EEG across three days
#     A2  0.878  "bursty"     <- the working control, correct
#     D2  0.316  "flat"       <- yet D2 gave 63.7% usable EEG
#
# So the ranking is uncorrelated with every other line of evidence, and the
# known-floating channel scores near the top. THIS IS THE HUM CRITERION'S
# FAILURE REPEATED IN A NEW COSTUME: a floating input is high impedance and
# picks up variable interference, so its envelope is variable, so a test that
# rewards variability rewards having no electrode.
#
# The numbers are still printed, because "A1 scores bursty" is exactly the kind
# of evidence that kills a criterion and it should stay visible. But this test
# EMITS NO PASS, and nothing downstream may gate on it. Judge EMG on state
# dependence against the EEG, which A1 cannot fake because it has no EEG either.


def verdict_for(r: float, n: int) -> str:
    if n < MIN_MINUTES:
        return "INSUFFICIENT (too few usable EEG minutes)"
    if np.isnan(r):
        return "INSUFFICIENT (no variance)"
    if r <= -0.30:
        return "STATE-DEPENDENT"
    if r <= -0.15:
        return "weak, right direction"
    if r >= 0.15:
        return "WRONG DIRECTION"
    return "no state dependence"


def local_start(base: str) -> dt.datetime:
    meta = json.loads(open(base + ".xdat.json").read())
    # astimezone, not "+9 h": Allego 4 (2026-10-28) writes start_time in local
    # time with +09:00, Allego 3 wrote UTC with Z. Converting handles both.
    t = dt.datetime.fromisoformat(meta["status"]["start_time"].replace("Z", "+00:00"))
    if t.tzinfo is None:
        t = t.replace(tzinfo=dt.timezone.utc)
    return t.astimezone(dt.timezone(dt.timedelta(hours=T.TZ_OFFSET_HOURS))).replace(tzinfo=None)


def bin_to_minutes(a: np.ndarray, nmin: int) -> np.ndarray:
    return a[:nmin * EPOCHS_PER_MIN].reshape(nmin, EPOCHS_PER_MIN).mean(1)


# --------------------------------------------------------------------------- #
# TEST 2 -- burstiness, which needs no EEG
# --------------------------------------------------------------------------- #

def quiet_window(feat: C.EpochFeatures, site: str) -> int | None:
    """First epoch of the quietest railing-free window for this site."""
    c = feat.col(site)
    n = feat.n_epochs - BURST_WINDOW_EPOCHS
    if n <= 0:
        return None
    rail = feat.rail[:, c]
    rms = feat.rms[:, c]
    best, best_k = None, None
    for k in range(0, n, BURST_WINDOW_EPOCHS // 2):
        w = slice(k, k + BURST_WINDOW_EPOCHS)
        if rail[w].max() > 0:
            continue
        score = float(np.median(rms[w]))
        if best is None or score < best:
            best, best_k = score, k
    return best_k


def burstiness(x, fs: int, col: int, k0: int, epoch_s: int) -> dict:
    """Envelope CV and mains-free 30-300 Hz amplitude on one window."""
    from scipy.signal import butter, filtfilt, hilbert, iirnotch, welch

    n0 = k0 * epoch_s * fs
    v = np.asarray(x[n0:n0 + BURST_WINDOW_EPOCHS * epoch_s * fs, col],
                   dtype=np.float64)
    v -= v.mean()
    for h in range(60, int(fs / 2) - 1, 60):     # mains comb, zero-phase
        b, a_ = iirnotch(h, 30.0, fs)
        v = filtfilt(b, a_, v)

    f, P = welch(v, fs=fs, nperseg=4096)
    m = (f >= BURST_BAND[0]) & (f <= min(BURST_BAND[1], fs / 2 - 1))
    for h in range(60, int(fs / 2), 60):          # exclude residual mains bins
        m &= ~((f >= h - 2.5) & (f <= h + 2.5))
    amp = float(np.sqrt(np.trapezoid(P[m], f[m])))

    hi = min(BURST_BAND[1], fs / 2 - 1)
    b, a_ = butter(3, [BURST_BAND[0], hi], btype="band", fs=fs)
    env = np.abs(hilbert(filtfilt(b, a_, v)))
    nsec = len(env) // fs
    e1 = env[:nsec * fs].reshape(nsec, fs).mean(1)
    cv = float(e1.std() / e1.mean()) if e1.mean() > 0 else float("nan")
    return {"amp_uv": amp, "burst_cv": cv, "window_start_epoch": k0}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("recording")
    ap.add_argument("--hours", type=float, default=None,
                    help="analyse only the first N hours (default: all)")
    ap.add_argument("--roles", type=int, default=3, choices=(2, 3),
                    help="2 = eeg,emg cohort; 3 = eeg,emg,ecg cohort")
    ap.add_argument("--json", default=None, help="write results here")
    ap.add_argument("--control", default="", help=(
        "comma-separated positions that are CONTROLS and must not count towards "
        "the gate, e.g. --control A1,A2. A control passing this test says the "
        "measurement works; it says nothing about the animals being published."))
    a = ap.parse_args()
    controls = {p.strip() for p in a.control.split(",") if p.strip()}

    base = PATHS.recording(a.recording)
    roles = ("eeg", "emg", "ecg")[:a.roles]
    spec = C.CohortSpec(roles=roles)

    integ = C.file_integrity(base)
    print(f"recording : {integ['base']}")
    print(f"rung 0    : {integ['verdict']} -- {integ['reason']}")
    if integ["verdict"] == "MALFORMED":
        return 1

    print("features  : single pass, this takes a while on a full night")
    feat = C.compute_features(base, spec, max_hours=a.hours)
    floor = C.floor_stats(feat)
    print(f"            {feat.n_epochs} epochs of {feat.epoch_s}s = {feat.hours:.2f} h")
    print(f"floor     : slope p1 {floor.slope_p1:+.3f} from {floor.n_sites} "
          f"wire-free sites")

    # zeitgeber time per epoch, so light and dark can be split
    start = local_start(base)
    offs = np.arange(feat.n_epochs) * feat.epoch_s
    start_h = start.hour + start.minute / 60 + start.second / 3600
    zt = (start_h - T.LIGHTS_ON_HOUR + offs / 3600.0) % 24.0
    light_ep = zt < 12.0
    print(f"clock     : starts {start:%Y-%m-%d %H:%M} KST = ZT{(start_h - T.LIGHTS_ON_HOUR) % 24:.2f}; "
          f"{100 * light_ep.mean():.0f}% of epochs in the light phase")

    nmin = feat.n_epochs // EPOCHS_PER_MIN
    print(f"\n{'animal':7}{'EEG':7}{'EMG':7}{'phase':7}{'n_min':>7}{'r':>9}   verdict")
    print("-" * 78)
    out: dict[str, dict] = {}
    for pos in spec.positions():
        eeg_site, emg_site = spec.site_of(pos, "eeg"), spec.site_of(pos, "emg")
        ce, cg = feat.col(eeg_site), feat.col(emg_site)

        # the EEG must be connected for its delta ratio to mean anything, and
        # neither channel may be railed in the minutes we use
        try:
            ok_eeg = C.usable(feat, eeg_site, floor, "slope", role="eeg")
        except C.CriterionRefused as e:
            print(f"{pos:7}{eeg_site:7}{emg_site:7}{'-':7}{'-':>7}{'-':>9}   REFUSED: {e}")
            out[pos] = {"refused": str(e)}
            continue
        ok = ok_eeg & (feat.rail[:, cg] == 0)

        delta_m = bin_to_minutes(feat.delta[:, ce], nmin)
        emg_m = bin_to_minutes(feat.rms[:, cg], nmin)
        ok_m = bin_to_minutes(ok.astype(float), nmin) > USABLE_MIN_FRACTION
        light_m = bin_to_minutes(light_ep.astype(float), nmin) > 0.5

        row = {"eeg_site": eeg_site, "emg_site": emg_site}
        for phase, sel in (("all", ok_m),
                           ("light", ok_m & light_m),
                           ("dark", ok_m & ~light_m)):
            n = int(sel.sum())
            r = float("nan")
            if n >= MIN_MINUTES and delta_m[sel].std() > 0 and emg_m[sel].std() > 0:
                r = float(np.corrcoef(delta_m[sel], emg_m[sel])[0, 1])
            v = verdict_for(r, n)
            row[phase] = {"n_min": n, "r": None if np.isnan(r) else round(r, 3),
                          "verdict": v,
            "is_verdict": False,
            "caveat": ("diagnostic only: A1, a channel with no ground, scores "
                       "above this bar, so envelope variability does not "
                       "distinguish muscle from a floating input on this rig")}
            rtxt = "     nan" if np.isnan(r) else f"{r:9.3f}"
            print(f"{pos if phase == 'all' else '':7}"
                  f"{eeg_site if phase == 'all' else '':7}"
                  f"{emg_site if phase == 'all' else '':7}"
                  f"{phase:7}{n:7d}{rtxt}   {v}")
        out[pos] = row
        print()

    # ------------------------------------------------- test 2: burstiness
    # This one needs NO EEG, so it reaches the animals the test above cannot ask.
    print("=" * 78)
    print("TEST 2 -- EMG BURSTINESS: DIAGNOSTIC ONLY, THIS TEST EMITS NO PASS")
    print("Real muscle fires in bursts, so its envelope should be variable while")
    print("stationary amplifier noise is not. On this rig that reasoning FAILS:")
    print("A1, which has NO GROUND AT ALL, scores near the top, because a floating")
    print("input picks up variable interference. Numbers are printed as evidence")
    print("against the test, not as a verdict. Nothing may gate on this column.")
    print()
    x, labels, fs_raw, _ = C.open_xdat(base)

    floor_cv, floor_amp = [], []
    for site in feat.spec.floor_sites()[::4]:
        k = quiet_window(feat, site)
        if k is None:
            continue
        b = burstiness(x, fs_raw, labels.index(site), k, feat.epoch_s)
        if np.isfinite(b["burst_cv"]):
            floor_cv.append(b["burst_cv"])
            floor_amp.append(b["amp_uv"])
    if not floor_cv:
        print("  no railing-free window on any floor site; burstiness not computed")
        floor_cv_med = floor_amp_med = float("nan")
    else:
        floor_cv_med = float(np.median(floor_cv))
        floor_amp_med = float(np.median(floor_amp))
        print(f"  floor: burst_cv {floor_cv_med:.3f}, 30-300 Hz amplitude "
              f"{floor_amp_med:.1f} uV, from {len(floor_cv)} unwired inputs")
    bar = floor_cv_med * BURST_CV_MARGIN
    print(f"\n{'animal':7}{'EMG':7}{'burst_cv':>10}{'bar':>8}{'amp30_300':>11}"
          f"{'floor_x':>9}   verdict")
    print("-" * 78)
    for pos in spec.positions():
        emg_site = spec.site_of(pos, "emg")
        k = quiet_window(feat, emg_site)
        if k is None or not np.isfinite(bar):
            print(f"{pos:7}{emg_site:7}{'-':>10}{'-':>8}{'-':>11}{'-':>9}   "
                  "INSUFFICIENT (no railing-free window)")
            continue
        b = burstiness(x, fs_raw, labels.index(emg_site), k, feat.epoch_s)
        fx = b["amp_uv"] / floor_amp_med if floor_amp_med > 0 else float("nan")
        v = ("high envelope variability" if b["burst_cv"] >= bar
             else "low envelope variability")
        print(f"{pos:7}{emg_site:7}{b['burst_cv']:10.3f}{bar:8.3f}"
              f"{b['amp_uv']:11.1f}{fx:9.2f}   {v}")
        out.setdefault(pos, {})["burst"] = {
            "burst_cv": round(b["burst_cv"], 3), "bar": round(bar, 3),
            "amp30_300_uv": round(b["amp_uv"], 1),
            "floor_x": round(fx, 2) if np.isfinite(fx) else None,
            "verdict": v}
    print()

    # ------------------------------------------------------------------ gate
    def band(lo, hi):
        return [p for p, r in out.items()
                if isinstance(r.get("all"), dict) and r["all"]["r"] is not None
                and lo < r["all"]["r"] <= hi]

    strong = band(-2.0, -0.30)
    weak = band(-0.30, -0.15)
    wrong = [p for p, r in out.items()
             if isinstance(r.get("all"), dict) and r["all"]["r"] is not None
             and r["all"]["r"] >= 0.15]

    def mark(ps):
        return ", ".join(f"{p}{' [CONTROL]' if p in controls else ''}"
                         for p in ps) or "NONE"

    print("=" * 78)
    print(f"STATE-DEPENDENT (r <= -0.30) : {mark(strong)}")
    print(f"weak, right direction        : {mark(weak)}")
    print(f"WRONG DIRECTION (r >= +0.15) : {mark(wrong)}")
    if controls:
        print(f"declared controls            : {', '.join(sorted(controls))}")
    print()

    # 🔑 A CONTROL PASSING THIS TEST IS NOT THE GATE PASSING. It shows the
    # MEASUREMENT works -- the sites, the binning, the correlation, the sign
    # convention -- which is worth knowing and is exactly why a control is run.
    # It says nothing about whether the animals destined for the paper have a
    # usable staging input. Counting it would let a cohort with no working EMG
    # at all report a green gate, which is how this project has been misled
    # before.
    experimental = [p for p in strong if p not in controls]
    if experimental:
        print(f"✅ GATE PASSED for {len(experimental)} EXPERIMENTAL animal(s): "
              f"{', '.join(experimental)}.")
        print("   Their staging input is coupled to state. That is a NECESSARY")
        print("   condition, not a sufficient one: it does not rule out EEG bleed")
        print("   into the EMG channel. Build kappa packs from these animals.")
    else:
        print("🔴 GATE NOT PASSED BY ANY EXPERIMENTAL ANIMAL.")
        if strong:
            print(f"   The only animal(s) reaching r <= -0.30 are declared CONTROLS "
                  f"({', '.join(strong)}).")
            print("   That is a working measurement on an animal that is not the")
            print("   experiment. It does not license a hypnogram for anybody else.")
        print("   The EMG threshold is the FIRST step of staging, so a hypnogram")
        print("   from these animals is not a weak result, it is not a result.")
        print("   DO NOT BUILD KAPPA PACKS FROM THIS RECORDING: a human would be")
        print("   scoring epochs whose staging input is unvalidated, and the")
        print("   resulting kappa would measure agreement about noise at the cost")
        print("   of hours that cannot be reused.")

    if a.json:
        with open(a.json, "w") as fh:
            json.dump({"recording": integ["base"], "hours": feat.hours,
                       "roles": list(roles), "floor": floor.as_dict(),
                       "thresholds_hash": C.thresholds_hash(),
                       "controls": sorted(controls),
                       "gate_passed_experimental": experimental,
                       "animals": out}, fh, indent=1)
        print(f"\nwrote {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
