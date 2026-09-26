---
tags: [troubleshooting, symptom, eeg, emg, qc, verdict-ladder, open]
created: 2026-09-26
first_observed: 2026-09-01
status: open
affects: [S-SD]
---

# An EMG with no muscle-band activity passes rung 2

> [!abstract] TL;DR
> 🔴 **Rung 2 CONNECTION can PASS an animal whose EMG carries no state-dependent
> activity in the muscle band.** EMG is judged on 60 Hz hum and rms only, and a quiet
> input satisfies both, so rung 2 cannot tell an EMG that can stage sleep from one
> that cannot.
>
> ⚠️ **"Dead" is too strong.** See "What the raw
> channel shows" below: the broadband channel is not flat.
>
> ✅ **Rung 3 catches it.** Stage 3 splits wake from sleep on EMG amplitude, finds
> almost no wake, and rejects the animal. So no false result has been published
> from this. But until stage 3 runs, a rung 2 PASS on such an animal looks like a
> usable animal. That is what happened to S-SD for three weeks.
>
> 🛑 **NOT FIXED.** Logged 2026-09-26. No code change made.

## The case: S-SD D2 / HLBSSD18

The only S-SD animal to pass rung 2 at every timepoint (08-25, 08-26, 09-02).
Stage 3, run for the first time on 2026-09-26, rejects it on all three days:
wake 1.6%, 0.9%, 0.2%; `r@1min` 0.029, 0.025, −0.023.

| | EMG rms p5 | p95 / p5 | EMG light → dark |
|---|---|---|---|
| S-SD D2, all three days | 27–33 µV | **1.41–1.75** | 30.9 → 32.3 µV, flat |
| working EMGs (W-SD D2 twice, S-SD A1) | 7–9 µV | 4.1–6.0 | roughly doubles |

Measured on the stage 3 hypnograms: 4 s epochs, inside unbroken contact blocks,
EMG band-passed 10–300 Hz (`FILT_EMG`). Re-derived independently on 2026-09-26:
1.75, 1.66 and 1.41 for S-SD D2, against 5.53 and 4.09 for W-SD D2.

### What the raw channel shows, and why it limits the claim

On the raw 10 s feature cache (broadband, unfiltered), **the groups do NOT
separate.** p95/p5 is 14.4, 11.6 and 123 (railing on 09-02) for S-SD D2, against
13.2 and 9.0 for W-SD D2. S-SD D2's raw rms also rises at night, from about 33 to
75 µV. The site `D/34` has a steep, EEG-like spectral slope (−1.27 on 08-25, −1.38
on 08-26), so the raw channel is dominated by low-frequency content.

So the supported statement is: **no state-dependent activity in the muscle band.**
Whether the nightly broadband rise is volume-conducted brain signal, movement
artefact or residual muscle is not established. Any rung 2 test built on this
must say which band it measures.

🔑 **It was seen and misread.** The 2026-09-01 pre-flight screen logged D2's EMG as
"locked at 50 µV" and counted it as a pass. A live neck EMG is never locked: it
falls toward atonia in NREM and REM and rises at night.

Consequence: **S-SD recovery sleep is n = 0**, and the endpoint cannot be repeated.
See [[05-experiments/completed/2026-09-02-S-SD-recovery-sleep]].

## A second, weaker case

S-SD B1 / HLBSSD17 on `allego_1__uid0826-12-50-16`: EMG p95/p5 1.7, and the
stage 3 wake split is unstable (94% wake at a 0.75× Otsu threshold). Stage 3 calls
it SCOREABLE (0.386); rung 2 FAILs it on block length, so the ladder never reached
the question.

## Candidate fixes, not chosen

Any of these could be a rung 2 EMG validity test. None has been measured against
the full card set, and none should be adopted without that.

- **Dynamic range, in the muscle band:** p95/p5 of per-epoch EMG rms after the 10–300 Hz
  band-pass. S-SD D2 1.41–1.75 against working
  4–6. The gap looks wide but was seen on six animal-recordings, and it VANISHES on raw
  broadband rms, so the band is part of the test.
- **Circadian modulation:** dark/light median EMG ratio. Flat on D2, ~2× on working
  EMGs. Needs a recording that covers both phases.
- **Spectral shape:** EMG is broadband and flat; D2's EMG slope is EEG-like. Beware:
  `core/criteria.py` (`usable()`) refuses slope on EMG: it is a category error for EMG
  as a CONNECTION criterion. As a *validity* flag it has not been tested.

⚠️ The rung 4 EMG state-dependence check (the one that withdrew W-SD C1) asks a
related question later in the ladder. A rung 2 test would duplicate part of it,
so decide which rung owns the question before writing anything.

## Related

[[05-experiments/completed/2026-09-02-S-SD-recovery-sleep]] ·
[[03-troubleshooting/symptoms/contaminated-floor-rejects-good-eeg]] ·
[[02-procedures/eeg-data-analysis/animal-card-and-verdict-ladder]]
