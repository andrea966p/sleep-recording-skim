---
name: weak-chip-ground-hides-as-electrode-failure
description: "A WEAK (not absent) chip ground is a distinct EEG fault that reads as a dead electrode; the EEG channel's 60 Hz as a fraction of its own chip floor exposes it, and the 800 uV grounded gate is too low"
metadata:
  node_type: memory
  type: project
---

🔴⭐⭐⭐ **"NO EEG" IS AT LEAST FIVE FAULTS. The newest, and the one that HIDES, is a chip ground
that is WEAK rather than absent.** Vault:
`03-troubleshooting/symptoms/weak-chip-ground-vs-open-electrode.md`.

## 🔑 THE DISCRIMINATOR: EEG channel 60 Hz ÷ ITS OWN CHIP FLOOR
| ratio | meaning |
|---|---|
| **≈ 0.03** | channel proportionally NORMAL (a working channel AND a weak-ground channel look identical here) |
| 0.1 - 0.5, ~0% railing | damaged / partially conducting conductor |
| **≥ 1.0** | OPEN input riding the rail |
Then read the **chip floor 60 Hz** itself. **Below ~2000 µV ⇒ nothing on that chip means anything.**
A weak ground scales the WHOLE chip down 3-4x, so real EEG arrives at 50-70 µV and spectrally flat
and every per-channel statistic still says the electrode is fine.

## 🔴 `FLOOR_MIN_HUM_UV = 800` IS TOO LOW — evidence, 32 chip-recordings, 4 runs
**Six chips below 2000 µV: 246, 593, 1347, 1491, 1575, 1814. NONE produced EEG.**
**Lowest floor that EVER produced EEG: 2186 µV.** No overlap.
Proposed **2000 µV**. Moves A1/A2/D1 (08-27) and B1 (08-24) FAIL → **UNJUDGEABLE**; **no PASS is
affected**. 🛑 **NOT APPLIED — awaiting the user's decision**, it rewrites verdicts in three
published reports.
🔑 Why it matters: **FAIL** reads "the electrode is bad" ⇒ tether change under isoflurane.
**UNJUDGEABLE** reads "the rig could not answer" ⇒ **connector re-mate at the bench**, which is what
actually fixed A1 and A2.

## ⭐ THE EMG CROSS-CHECK — cheapest way to exonerate an implant
Both roles share the tether. **EMG working while EEG is flat ⇒ implant and cable are fine.**
A1/A2 on 2026-08-27: 98.4% / 99.2% EMG all night, A1 dark/light 2.73x = real state dependence.
🛑 Converse is INVALID: a quiet EMG passing the hum criterion may itself be floating. Only amplitude
that tracks behaviour proves an EMG channel.

## WORKED CASE (see [[w-sd-recovery-sleep-run-2026-08-27]])
A1 floor 4976 → 1347 µV, EEG 84 → 55 µV, slope −1.56 → −0.10, **4 of 7243 epochs beat its floor**.
Ratio stayed **0.032**, identical to working D2. 80 s check 21 min after the run: floor **5026 µV**,
EEG back. Nothing was done to the electrode.

## CHECK ORDER
1. chip floor 60 Hz (<2000 ⇒ stop, re-mate, re-record) → 2. channel ÷ floor ratio → 3. EMG on the
same position → 4. |r| between the position's own two channels (0.06-0.09 working, 0.5-0.75 shared
path) → 5. only THEN talk about the electrode.

Related: [[w-sd-recovery-sleep-run-2026-08-27]] · [[w-sd-batch-closeout-2026-08-28]] ·
[[floor-threshold-fixed-per-chip]] · [[ecg-cohort-ground-miswired]] ·
[[movement-dependent-contact-root-cause]]

## 🔴 2026-10-01/02 UPDATE: the floor scale is CONFIGURATION-DEPENDENT. The 2000 proposal is FALSIFIED here
After the noise-series changes (slip-ring free wires taped 09-30, adapter boards off/on 10-01, 8-core tethers), two
chips under 2000 µV ON THE GATE'S PEAK SCALE carried working EEG in the first overnight: **B2 1820 and B1 742 (632-808)**. A2 was 2057.
B1 also has an EMG that tracks behaviour (p95/p5 6.5). (First written as 'three chips: A2 1520, B2 1350, B1 455-599', which were band-RMS
numbers, √2 small; corrected 01:45.) The old "lowest floor that ever produced EEG = 2186" no longer holds. **Do NOT
apply 2000.** The 800 gate is suspect in this configuration too, in BOTH directions: empty headstages with NO animal
read ~1750-4300 µV peak (the gate would call them grounded), while B1 with a working animal reads ~740 (gate calls it
ungrounded). Open-input 60 Hz pickup measures antenna geometry as much as ground. Proposed fix (NOT applied): re-derive
the populations with dummy loads (GND on vs lifted, same geometry), plus a pre-registered EMG-behaviour route.
See [[recording-2026-10-01-noise-4mice-overnight]].
