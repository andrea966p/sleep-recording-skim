---
tags: [troubleshooting, symptom, eeg, grounding, qc]
created: 2026-08-29
---

# "No EEG" is at least four different faults, and the chip's own floor tells them apart

> [!abstract] TL;DR
> A position that produces no usable EEG can be an **open electrode**, a **damaged tether
> conductor**, a **fully floating chip**, or a **chip whose ground is merely WEAK**. The last one
> is the newest and it was missed for a whole 20 h endpoint recording on 2026-08-27.
>
> **Two numbers separate all four, and both come from the same file:**
> 1. the **chip's wire-free floor**, the median 60 Hz across the 14 unwired inputs on that chip;
> 2. the **EEG channel's own 60 Hz as a fraction of that floor**.
>
> 🔑 **A working EEG channel sits at about 0.03 of its chip's floor. An open input sits at 1.0 or
> above, because it is riding the rail.** That ratio is the same for a good channel whether the
> chip's ground is strong or weak — which is exactly why a weak ground hides.
>
> 🔴 **Empirically, on this rig, a chip floor below about 2000 µV means no EEG, full stop.** Across
> 32 chip-recordings in four runs, six chips sat below 2000 µV and **not one produced EEG**; the
> lowest floor that ever produced EEG was 2186 µV. The code's current gate is **800 µV**, which is
> too low and lets a dead chip be scored as a failed animal.

## The four signatures

| what is wrong | chip floor 60 Hz | EEG channel 60 Hz ÷ floor | EEG rms | slope | railing | what to do |
|---|---|---|---|---|---|---|
| **nothing — working channel** | normal, 2200-5400 µV | **≈ 0.03** | 80-150 µV | −1.3 to −1.9 | ~0% | — |
| **open electrode** | normal | **≥ 1.0** | 3000-4500 µV | ≈ 0 | 50-100% | animal side; tether change under isoflurane |
| **damaged / partial tether conductor** | normal | **0.1 to 0.5** | intermediate | flat | **~0%** | replace the tether |
| **chip fully floating, no ground** | **< 800 µV** | meaningless | small | flat | ~0% | the code refuses a verdict already |
| 🔴 **chip ground WEAK** | **800-2000 µV** | **≈ 0.03, i.e. it looks fine** | small, 50-70 µV | **flat** | ~0% | **re-mate the connector; no anaesthesia needed** |

The trap is the last row. The channel's proportion to its own chip is *normal*, so every per-channel
statistic says the electrode is fine. What has changed is the **whole chip's reference**, which
scales everything on it down by a factor of three or four, so the EEG arrives too small and too
flat to beat any spectral test. **The verdict engine then calls the animal a FAIL.**

## The worked example: A1 and A2, 2026-08-27

Twenty hours of recovery sleep, cohort W-SD. See
[[2026-08-27-W-SD-recovery-sleep|the run report]].

| | A1 (HLBWSD01) | A2 (HLBWSD02) | D2 (HLBWSD08), working |
|---|---|---|---|
| chip floor 60 Hz, the day before | 4314 µV | 4606 µV | 3175 µV |
| chip floor 60 Hz, this run | **1347** | **1575** | 4761 |
| EEG 60 Hz ÷ chip floor | **0.032** | **0.045** | **0.032** |
| EEG rms | 55 µV | 67 µV | 139 µV |
| EEG slope, every hourly bin | −0.03 to −0.17 | +0.09 to −0.30 | −1.45 |
| epochs beating the chip floor's lf/hf p99 | **4 / 7,243** | **2 / 7,243** | **7,239 / 7,243** |
| EMG through the same tether | **98.4% usable** | **99.2% usable** | 98.5% |

**A1's ratio is identical to D2's.** Nothing about A1's electrode was wrong. Its chip had lost three
quarters of its ground reference, and it stayed that way for the entire twenty hours without ever
recovering on its own — which also rules out settling after handling.

✅ **The fix was a connection, not surgery.** An 80 s check taken 21 minutes after the run ended
(`allego_3__uid0828-09-26-12`) shows A1's floor back at **5026 µV** and A2's at **4490 µV**, with
EEG at 91 and 134 µV, slope −1.43 and −1.53, and lf/hf 13.75 and 10.73 against floor 99th
percentiles of 1.88 and 3.48.

## ⭐ The EMG cross-check: the cheapest way to exonerate an implant

Both roles run through the same tether. **If the EMG on a position is working while its EEG is
flat, the implant and the tether are both carrying signal, and the fault is specific to the EEG
path or to the chip's reference.** On 2026-08-27 A1 and A2 gave 98.4% and 99.2% usable EMG all
night, and A1's muscle amplitude was 2.73× higher in the dark, which is genuine behavioural state
dependence and cannot come from a floating input.

🛑 The converse is not true. A quiet EMG channel that passes the hum criterion may simply be a
floating input, because "quiet and quieter than the floor" describes both. Only amplitude that
tracks behaviour proves an EMG channel.

## 🔴 The 800 µV gate is too low — the evidence, and the proposed change

`core/qc_thresholds.py` sets `FLOOR_MIN_HUM_UV = 800`. Below that, `criteria.floor_stats()` marks
the chip ungrounded and the ladder returns **UNJUDGEABLE** instead of a verdict, which is correct
behaviour. The bar itself is wrong.

Every chip-recording available on 2026-08-29, sorted by floor, four runs and 32 rows. "EEG?" is the
lf/hf separation test: the animal's median against its own chip floor's 99th percentile.

| floor 60 Hz | run | pos | EEG rms | EEG present? |
|---|---|---|---|---|
| 246 | 08-25 | B1 | 486 | no |
| 593 | 08-27 | B1 | 215 | no |
| **1347** | 08-27 | **A1** | 55 | **no** |
| 1491 | 08-24 | B1 | 3137 | no |
| **1575** | 08-27 | **A2** | 67 | **no** |
| **1814** | 08-27 | **D1** | 2087 | **no** |
| **2186** | 08-26 | **B1** | 93 | ✅ **YES** ← the lowest floor that ever worked |
| 2807 | 08-24 | D2 | 79 | ✅ |
| 2890 | 08-24 | D1 | 99 | ✅ |
| 3076 | 08-25 | D2 | 86 | ✅ |
| 3175 | 08-26 | D2 | 92 | ✅ |
| 3189 – 5398 | various | | | mixed — above this level, failures are **open electrodes**, not grounds |

**Six chips below 2000 µV. Zero produced EEG. The lowest floor that ever produced EEG is 2186 µV.
There is no overlap.**

> [!tip] Proposed change, NOT YET APPLIED
> Raise `FLOOR_MIN_HUM_UV` from **800** to **2000 µV**, and say in the refusal text that the chip is
> *inadequately grounded* rather than *ungrounded*.
> **What it changes:** A1, A2 and D1 on 2026-08-27 and B1 on 2026-08-24 move from **FAIL** to
> **UNJUDGEABLE**. No position moves from FAIL to PASS, and no PASS is affected — the lowest
> passing floor, 2186 µV, is above the proposed bar.
> **Why it matters beyond bookkeeping:** a FAIL reads as "this animal's electrode is bad" and sends
> you towards a tether change under anaesthesia. UNJUDGEABLE reads as "the rig could not answer",
> and the fix is a connector re-mate at the bench.
> ⚠️ Awaiting approval before the constant is touched, because it rewrites verdicts already
> published in three experiment reports.

## The order to check things in

1. **Chip floor 60 Hz first.** Below ~2000 µV, stop — no channel statistic on that chip means
   anything. Re-mate the headstage and tether connector and re-record for an hour.
2. **Then the EEG channel's ratio to that floor.** At or above 1.0 the input is open and riding the
   rail; around 0.03 the channel is proportionally normal; between 0.1 and 0.5 with almost no
   railing, suspect a damaged conductor.
3. **Then the EMG on the same position.** Working muscle through the same tether exonerates the
   implant and the cable.
4. **Then the inter-channel correlation.** |r| between a position's own two channels sits at
   0.06-0.09 on working animals and 0.5-0.75 when one damaged cable feeds both.
5. **Only then** talk about the electrode.

## Related

[[per-animal-failure-signatures]] · [[2026-08-27-W-SD-recovery-sleep]] ·
[[2026-08-25-S-SD-24h-ZT0-run]] · [[02-procedures/signal-quality-and-grounding|signal quality and grounding]] ·
[[02-procedures/grounding-reference-noise-concepts|grounding and reference concepts]] ·
[[eeg-analysis-problems]]
