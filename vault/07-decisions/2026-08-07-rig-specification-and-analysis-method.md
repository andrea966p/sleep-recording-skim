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

> [!danger] 🔴 SCOPE — the cohort changed on the evening of 2026-08-07, AFTER the results below
> The 8 mouse EEG+EMG cohort described in Part 1 **no longer exists**. It was replaced the same
> evening by **7 new mice carrying EEG, EMG and ECG**, with the old B1 kept in port A slot 2 as a
> positive control. See [[2026-08-07-ecg-cohort-baseline]].
>
> **What still holds:** Part 1's established claims, and Part 3's *principles*. Those were earned
> on data and do not expire with the animals.
>
> **What is cohort-specific and has already changed:** the channel map (§2.2), the floor-control
> channel list (§3.1), and the usefulness of the 0.5 MΩ line and of hum as a contact proxy (§3.2).
> Each is flagged inline. **Read those flags before quoting a number.**

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
| channel selection, **EEG+EMG cohort** | `/1`, `/2`, `/33`, `/34` per port | [[CANONICAL-allego-channel-selection]]. `/1` = EEG, `/2` = EMG for mouse 1; `/33`, `/34` for mouse 2 |
| channel selection, **ECG cohort from 2026-08-07** | `/1`, `/2`, `/3`, `/33`, `/34`, `/35` | **`/1` EEG, `/2` EMG, `/3` ECG**; mouse 2 on `/33`, `/34`, `/35`. The port map itself is unchanged |
| sample rate | **1 kHz** | sufficient for sleep; 89 GB for 24 h at 256 channels |
| channels saved | **all 256** | non-negotiable, see 2.3 |
| filters | **Hardware stage untouched. Data and Visualization stages are display-only** | verified 2026-07-31: the `.xdat` is raw wideband with the hardware bandpass only |

## 2.3 ⭐ Keep an empty cable permanently plugged in

**This is the single most valuable change to come out of the last three days, and it is free.**

A sweep reads every port at once and a recording saves every channel, so a tether with **no animal
on it**, wired through its slip ring, headstage and splitter, costs nothing and gives a live
negative control in every measurement.

It was an accident that the A2 position held one. It should now be deliberate.

🔴 **It was lost on 2026-08-07** when all 8 slots were filled by the new cohort. `A/35` is a partial
substitute because the control animal has no ECG implanted. **Restore a real one** — a dedicated
empty chain is worth more than an eighth animal, given that six of eight animals produced nothing
for the whole of the last cohort.

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

A mouse uses only a few of its chip's 16 amplifier inputs, so the rest are **real amplifier inputs
with no wire attached**. They are the null distribution, and **the exact list depends on how many
channels the cohort wires**:

| cohort | wired per mouse | **floor-control channels** |
| --- | --- | --- |
| EEG+EMG, to 2026-08-07 | `/1`,`/2` | `/3`-`/16` and `/35`-`/48` — **112 per sweep** |
| **ECG cohort, from 2026-08-07** | `/1`,`/2`,`/3` | **`/4`-`/16` and `/36`-`/48` — 104 per sweep** |

⚠️ **Recompute this list whenever the montage changes.** Using the old list on the ECG cohort would
put two live ECG channels into the control group.

❌ **Never include `/17`-`/32` or `/49`-`/64`, in any cohort.** Those are inactive slots, internally
tied, and read low almost always. Including them would flatter the control and condemn every real
animal.

🔴 **The dedicated empty-cable control was lost** when all 8 slots were filled by the new cohort.
`A/35` is a free substitute, because the control mouse has no ECG implanted. **Restore a deliberate
empty cable at the next opportunity** — §2.3.

## 3.2 Impedance

**Criterion: `|Z| < 0.5 MΩ`. Not 2 MΩ.**

| threshold | fraction of *bare wires* that pass |
| --- | --- |
| 2 MΩ, the old rule | **21.4%** |
| **0.5 MΩ** | **3.1%** |

The floor reached **0.051 MΩ**, the same value as the best electrode reading ever recorded here.
⇒ **A single low impedance reading is never evidence of contact.** Re-score any historical block
before quoting it. [[2026-08-06-fleet-duty-cycle-census]]

> [!warning] 🔴 0.5 MΩ beats an unwired floor. It is NOT an absolute measure of contact.
> On the ECG cohort the criterion **calls our best-ever channel open**: the control animal scored
> 0.0% duty on all three sites, and B1's EEG median was already 0.813 MΩ when B1 was the only
> working animal on the rig.
>
> **Use it as a comparison against the floor in the same block, never as a pass mark quoted on its
> own.** [[2026-08-07-ecg-cohort-baseline]]

> [!important] ⭐ Zero flips is a wiring signature, not a good electrode
> Every genuine contact failure this rig has produced was **intermittent**. When 7 channels come
> back at **100% duty with zero flips**, that is not how electrodes behave, it is how **wiring
> errors** behave. On 2026-08-07 that tell was correct: the cerebellum ground had been mated to the
> wrong pin and all seven animals were recording with **no ground at all**.
>
> Treat a suspiciously perfect, perfectly stable result as a **red flag to check the wiring**, not
> as a success.

> [!tip] ⭐ Use the phase column. It was ignored for months.
> | phase | means |
> | --- | --- |
> | ~0° or ~180° | **resistive** — a real conduction path, or a short |
> | −20° to −60° | an **electrode/tissue interface**, which is what a good electrode looks like |
> | ~−90° | **pure capacitance**, e.g. coupling through a cable rather than a connection |
>
> A prediction was tested and failed on 2026-08-07: capacitive coupling through the tether would
> have given ~−90° and the measurement came back purely resistive, killing that explanation.

**Measure duty cycle over repeated sweeps, never a single reading.** A sweep of 256 channels takes
31.4 s and the process is automated: `eeg-emg-analysis/qc/sweep_block_all_ports.py`, with
`remap_channels.py` run first after any port change, because `ntvChanIdx` is global and a port
change silently relabels everything.

> [!danger] 🔑 Impedance blocks SCREEN. Only a multi-hour recording is an OUTCOME.
> A 40 sweep block spans about 21 minutes, and contact states persist **longer than that**. On
> 2026-08-06 a block gave **p = 1.0e-07** for a conclusion the overnight recording reversed
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

## 3.3b ⚠️ Hum is a contact proxy only while it is bimodal — check per cohort

On the EEG+EMG cohort, 60 Hz hum separated connected from open by about 100× and was cleanly
bimodal, which is what made it the primary discriminator.

🔴 **That relationship broke on the ECG cohort.** Fleet-wide hum collapsed from 800-5500 µV to
20-210 µV **while the channels carried no biology at all** — you can now have 20 µV of hum sitting
over 3 µV of nothing.

The reason is instructive: **losing the ground raises hum only in single-ended recording. In a
bipolar pair, an ungrounded animal is driven by mains as common mode, and the pair rejects it.**
Low hum and absent signal had the same cause.

⇒ **Re-derive every hum threshold from the current cohort's own floor, and never assume low hum
means good contact.**

## 3.3c Diagnosing WHICH failure an animal has

Stage 1 says `OPEN` and stops. That word hides at least four faults needing different fixes:
**floating conductor** (huge hum, railing), **shared path** (both channels rail, and the animal's
**own two channels correlate > 0.5**), **damaged/partially conducting** (intermediate hum, *quieter
than the floor*, no railing, e.g. a chewed tether), and **one good channel of two**.

⭐ The discriminator that turned out to matter is the **correlation between an animal's own EEG and
EMG** after filtering: working animals sit at **0.07-0.08**, a shared fault drives it to **0.74**.

🛑 **Spectral slope judges EEG, not EMG** — real EMG is broadband, so a flat spectrum is expected
for a working muscle channel.

Full lookup table and the worked example on all 8 positions:
[[per-animal-failure-signatures]].

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

**Sweep tooling:** `qc/sweep_block_all_ports.py` takes `--roles eeg,emg,ecg` (or `eeg,emg`) and its
console criterion is now 0.5 MΩ; `qc/block_duty_cycle.py BLOCKDIR --roles ... --thresh 0.5` gives
duty cycle, flips and a binomial test against the in-file floor. Run `remap_channels.py` first after
any port change.

🔴 **`AllegoClient.set_recording_config()` is broken** — `ConfigRecording` has a required
`recordingType` enum the library never sets, so it fails with `Exception serializing request!`, and
**a failed config silently leaves the old path**. `get_status().recording.path` is useless, it
reports the calling process's cwd. **The only proof is to `ls` the destination and watch
`_data.xdat` grow.** Workaround: `qc/set_recording_config_fixed.py`.

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

## 🔴 The immediate situation, 2026-08-07 22:00

The new ECG cohort produced **the best impedance the rig has ever shown** — 19 of 21 channels
beating the floor, 7 at 100% duty with zero flips — **and no biology whatsoever**: 22 of 24 stream
channels at 2-6 µV amplifier noise, and **not one ECG channel with a heartbeat**. Only the control
animal is real, which exonerates the rig, the amplifiers and the analysis.

**Root cause identified: the cerebellum ground was mated to the wrong pin.** The dura pin went to
the orange wire, floating at the far end, while the brown wire sitting in the headstage GND pad
touches nothing on the animal. **All seven new mice recorded with no ground.**

✅ **The fix is a connector re-mate and needs no anaesthesia**, so the standing "never reseat an
electrode" rule does not apply. Scheduled for 2026-08-08.

> [!important] ⭐ The prediction that decides it
> With the ground correctly connected, **the impedances should get worse or change character**,
> because the return path moves from the paired electrode to the ground electrode. **If they come
> back identical, at 100% duty with zero flips, the ground is still not connected.**

Pre-fix baseline to keep: `allego_0__uid0807-19-14-58`, 2.768 h, 10.44 GB, verified intact.

## Still open, ranked

0. **Re-pin the seven animals and prove the ground.** Watch the live stream *before* committing to a
   night; EEG should appear within seconds. Then a fresh impedance block, then an overnight
   recording, scored against floor `/4`-`/16`, `/36`-`/48`, **with the heartbeat as the primary
   yes/no** — a heartbeat is unfakeable in a way a wandering EEG trace is not.
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

---

> [!note] Provenance of this page
> Written 2026-08-07 from the 4 to 7 August work. Corrected the same evening once the ECG cohort
> replaced the animals: the scope banner, the channel map in §2.2, the floor-control list in §3.1,
> the 0.5 MΩ and hum caveats in §3.2 and §3.3b, the zero-flips and phase diagnostics, and the
> immediate-situation section were all added after the fact. **Parts 1 and 3's principles predate
> that change and are unaffected by it.**
