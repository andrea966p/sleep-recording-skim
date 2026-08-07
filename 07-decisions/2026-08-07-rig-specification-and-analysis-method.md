---
tags: [decision, eeg, rig, specification, analysis-method, synthesis]
created: 2026-08-07
status: current
---

# The rig specification and the analysis method, as established by evidence

> [!abstract] TL;DR
> This is the page to argue from. It states **what we now know, how the rig should be built, how
> the data must be analysed, and what may not be claimed** — each with the evidence behind it and
> an honest strength rating.
>
> The short version: **the bottleneck was never the surgery, the animals or the acquisition
> system. It was the tether chain.** Replacing it took one animal from producing nothing to
> producing 23.66 hours of scoreable sleep. The analysis method changed just as much, because we
> finally got a negative control and it showed that both of our old judgements — a 2 MΩ impedance
> threshold, and looking at filtered traces — accept a cable attached to nothing.

Supersedes nothing outright; it consolidates. Sources are linked per claim rather than restated.

---

# Part 1 — What is established

Strength ratings: 🟢 solid, multiple independent lines · 🟡 single strong result, n = 1 ·
🔴 suggestive only.

| # | Claim | Strength | Evidence |
| --- | --- | --- | --- |
| 1 | **Electrical contact is the bottleneck. Nothing else is close.** | 🟢 | Open electrode in 36 of 41 animal-recordings; hum is bimodal at ~100× between connected and open; the rig itself produced a flawless 4.55 h recording. |
| 2 | **The electrodes and implants are good. No surgery is warranted.** | 🟢 | B1 measured **0.052 MΩ**, inside the published 10-50 kΩ band and the best ever on this rig; D2 recovered completely from fully open. A degraded electrode cannot do either. [[2026-08-04-movement-dependent-contact]] |
| 3 | **Contact is intermittent and reversible, on a timescale of minutes to tens of minutes.** | 🟢 | 6.236 → 0.052 → 8.649 → 0.177 MΩ in 23 min; and a 21 min block of 40 sweeps sat in **one** state throughout. |
| 4 | **The tether chain is the fix.** | 🟡 | **D2: 0.0% → 87.9% usable EEG**, hum 916.9 → 133.2 µV, railing 29.7% → 0.0%, spectral slope −0.38 → −2.05, after a tether swap and nothing else. [[2026-08-07-overnight-recording-two-animals-work]] |
| 5 | **Long post-op recovery is NOT required.** | 🟡 | D2 was tethered at **day 8**, well short of our 14 day protocol, and now records cleanly. This was the pre-registered disambiguation of the B1 confound. |
| 6 | **Soldered + resin-encapsulated joints are the common factor in both successes.** | 🔴 | Arm B improved B1 **with** the slip ring; arm C improved D2 **without** it. Construction is what they share. Confounded by animal and tether length. |
| 7 | **Capacity for 8 mice is proven and is not the constraint.** | 🟢 | 4 ports × splitter × 2 mice = 256 channels, all enumerated and returning data. That is the hard XDAQ Core ceiling. |
| 8 | **The analysis pipeline works end to end and agrees with external biology.** | 🟢 | Two animals, 5/5 physiology checks each, REM-from-NREM 73.9% and 79.5%, and **D2 asleep 70.3% of the light phase against a literature value of ~70%** — a check nothing in the pipeline was tuned against. [[2026-08-07-staging-preregistration]] |

## What is dead — never re-propose

Electrodes degraded or failing · cold solder joint on pads 0/1 · board leakage or bridging · the
slip ring as a *statically* broken conductor · per-pad rather than per-channel-type faults · the
port, splitter or XDAQ · "we need new mice" · the negative electrode being permanently open ·
movement as the *cause* of contact loss (proposed and disproved the same day).

Added 2026-08-06: **the tether, slip ring and splitter are not leaking.** The teardown ladder was
flat — a bare headstage with nothing attached still produced 0.107 MΩ, so the spurious readings are
the amplifier's own floating-input behaviour.

---

# Part 2 — The rig specification

## 2.1 Tether

**Build: soldered joints, encapsulated in resin.** This is the only construction that has ever
produced a working animal on this rig, and it has now done so twice.

⚠️ **Slip ring: undecided, and it does not currently matter.** Both successful arms disagree — B1
improved with it, D2 improved without it. The user's ruling stands: **rotation and binding are not
relevant at this stage**, because the current phase is rig validation, signal quality and
troubleshooting, not long-term husbandry. Revisit before any unattended multi-day run.

> [!note] The bench-only restriction on the long tether is lifted for this phase
> `2026-08-05-tether-comparison` §5 said the long, non-rotating tether "must never be proposed for
> an overnight run". **D2 then ran 23.66 h on it flawlessly**, in one 9.6 h block. The restriction
> was a reasonable precaution, it was not borne out, and it is set aside while the goal is rig
> validation.

## 2.2 Acquisition

| setting | value | why |
| --- | --- | --- |
| channel selection | `/1`, `/2`, `/33`, `/34` per port | [[CANONICAL-allego-channel-selection]]. `/1` = EEG, `/2` = EMG for mouse 1; `/33`, `/34` for mouse 2. **If any other page disagrees, that page is stale.** |
| sample rate | **1 kHz** | sufficient for sleep; 89 GB for 24 h at 256 channels |
| channels saved | **all 256** | non-negotiable, see 2.3 |
| filters | **Hardware stage untouched. Data and Visualization stages are display-only** | verified 2026-07-31: the `.xdat` is raw wideband with the hardware bandpass only |

## 2.3 ⭐ Keep an empty cable permanently plugged in

**This is the single most valuable change to come out of the last three days, and it is free.**

A sweep reads every port at once and a recording saves every channel, so a tether with **no animal
on it**, wired through its slip ring, headstage and splitter, costs nothing and gives a live
negative control in every measurement.

It was an accident that the A2 position held one. It should now be deliberate.

## 2.4 🟡 Open decision: the 1.10 Hz hardware high-pass

The hardware bandpass is currently **1.10 to 475.17 Hz** and, unlike the display filters, it
**reaches the saved file and cannot be undone**. Delta is 0.5 to 4 Hz, so the bottom of the band we
depend on is attenuated before saving.

- It is identical on all four ports and every threshold we use was derived from data carrying it,
  so **our internal comparisons are unaffected**.
- It matters when comparing our delta power to published values.

**Decide before the next long run.** No action taken yet, deliberately, because changing it now
would break comparability with everything recorded to date.

---

# Part 3 — The analysis method

## 3.1 The principle: controls go inside the file

Every threshold this project used before 6 August was inherited from an earlier session or from the
literature. They are now derived from **channels recorded at the same instant, on the same chips,
in the same room**.

Each mouse uses only 2 of its chip's 16 amplifier inputs, so **`/3`-`/16` and `/35`-`/48` are real
amplifier inputs with no wire attached** — 112 per sweep, 953,904 epochs in a 24 h recording.

❌ **Never include `/17`-`/32` or `/49`-`/64`.** Those are inactive slots, internally tied, and read
low almost always. Including them would flatter the control and condemn every real animal.

## 3.2 Impedance

**Criterion: `|Z| < 0.5 MΩ`. Not 2 MΩ.**

| threshold | fraction of *bare wires* that pass |
| --- | --- |
| 2 MΩ, the old rule | **21.4%** |
| **0.5 MΩ** | **3.1%** |

The floor reached **0.051 MΩ**, the same value as the best electrode reading ever recorded here.
⇒ **A single low impedance reading is never evidence of contact.** Re-score any historical block
before quoting it. [[2026-08-06-fleet-duty-cycle-census]]

**Measure duty cycle over repeated sweeps, never a single reading.** A sweep of 256 channels takes
31.4 s and the process is automated: `eeg-emg-analysis/qc/sweep_block_all_ports.py`, with
`remap_channels.py` run first after any port change, because `ntvChanIdx` is global and a port
change silently relabels everything.

> [!danger] 🔑 Impedance blocks SCREEN. Only a multi-hour recording is an OUTCOME.
> A 40 sweep block spans about 21 minutes, and contact states persist **longer than that**. On
> 2026-08-06 a block gave **p = 8.4e-08** for a conclusion the overnight recording reversed
> completely.
>
> **Always state a block's duration next to its duty cycle, and never conclude harm or benefit
> from a block alone.** [[2026-08-05-tether-comparison]] §13 and §14.

## 3.3 Recorded data

**Judge by spectral shape against the in-file floor. Never by how the trace looks.**

> [!danger] Filtering manufactures a convincing EEG from nothing
> Put a channel with **no wire attached** through a 60/120/180 Hz notch and a 0.5-30 Hz band-pass
> and it emerges as a median **69 µV of smooth, plausible, EEG-looking signal**.
>
> Trace morphology is therefore **not evidence of connection**, and neither is amplitude.

What survives filtering is **shape**. Real neural activity falls steeply with frequency; noise is
flat.

| measure | wire-free floor | B1 | D2 |
| --- | --- | --- | --- |
| spectral slope (1-30 Hz) | −1.29 to −0.07 | **−1.81** | **−2.05** |
| delta fraction | ~0.17 | 0.32 | **0.47** |

## 3.4 Artefact and railing

Full rules: [[eeg-artefact-and-railing-rejection-policy]].

- **Reject at the epoch level, never the animal level** — but only after checking that the
  surviving clean epochs still differ from the floor in spectral shape.
- 🔴 **On this rig, railing is the open-electrode signature, not movement artefact.** The A2
  position, which contains **no mouse**, railed 100% of the time. Railing is **missing data**, not
  noisy data: clipping is nonlinear and irreversible.
- ⚠️ **Always state samples versus epochs.** "7% railed" as a fraction of samples was **77.6% of
  epochs** for the same channel. They lead to opposite decisions.

## 3.5 The pipeline is canonical for scoreability

`stage1_qc.py` → `stage2_split.py --all-verdicts` → `stage3_features.py` → `stage4_export_edf.py`.
Use the **system `python3`**; scripts needing scipy use `~/eeg-analysis-venv/bin/python`.

Stage 1 uses a fixed 150 µV mains limit that predates all of the above and reaches the **same
verdicts**, which is a useful independent check. **Quote pipeline block lengths for scoreability**;
quote the floor-control analysis when the point is separation from an unconnected amplifier.

⚠️ **`stage2_split.py` copies the wrong impedance files** — it flattens sweep blocks together and
pulls in other days. Check `impedance/` after every run.

Persistence is computed **within unbroken blocks only**. Computing it across gaps produced both the
project's largest false positive and a false negative on 2026-08-03.

---

# Part 4 — What may not be claimed

| 🛑 | Why |
| --- | --- |
| **No REM share, ever** | Fixed by construction. The percentile rule gives 7-11%; an independent Otsu cut gives **41.6% and 41.3% of sleep**; literature is <10%. Neither is a measurement. Report **WAKE vs NREM** and REM's **order** (entered from NREM, >70%). |
| **Never subtract EEG from EMG** | The RHD2216 is bipolar and already subtracted before the ADC. |
| **Never "reseat" an electrode** | Impossible after implantation. The only animal-side option is a tether change, which costs an isoflurane episode. |
| **Do not schedule surgeries** | Claim 2. The implants are good. |
| **Do not quote "~6% yield"** | Both early runs were commissioning tests, 2-6 days early against our own protocol. |
| **B1's 82.1% light-phase sleep is not "normal architecture"** | It is *above* the literature mean; consistent with recent tethering. D2's 70.3% is the cleaner figure. |

## Still open, ranked

1. **Which part of the tether chain does the work?** Every swap changes four things at once:
   construction, slip ring, connector re-seating, anaesthesia. Separating them costs one anaesthesia
   episode per animal. n = 1 per condition today.
2. **Only the positive input of each electrode pair is ever measured.** The chip can test the other
   side but neither Radiens nor the Open Ephys plugin exposes the control. With the vendor.
3. **No video.** Cameras were removed on 2026-08-04. This blocks resolving C1's ambiguous EMG
   (rms 1834 µV against only 506 µV of hum, so large non-hum content) and blocks the video-EEG sync
   work entirely.
4. **The 1.10 Hz hardware high-pass**, §2.4.
5. **Part B of the interference test** — whether a dangling cable disturbs a working neighbour — is
   designed and unrun. [[2026-08-06-unloaded-chain-interference]]

---

# The claim this page supports

> [!quote] Paper-ready
> Signal quality in chronic tethered mouse EEG was found to be limited by intermittent electrical
> contact rather than by electrode or implant failure, with individual electrodes measuring as low
> as 0.052 MOhm and recovering spontaneously from an open state. Because repeated impedance sweeps
> revealed contact states persisting for tens of minutes, and because amplifier inputs with no
> electrode attached passed a conventional 2 MOhm criterion in 21.4% of measurements and yielded a
> median 69 microvolts of spectrally flat but morphologically plausible signal after standard
> notch and band-pass filtering, channel viability was assessed against simultaneously acquired
> unconnected inputs and classified by spectral slope. Replacement of the tether chain in a single
> animal raised its usable EEG fraction from 0.0% to 87.9% and yielded 23.3 h of scoreable data,
> of which 70.3% of the light phase was scored as sleep, against a literature value of
> approximately 70%.
