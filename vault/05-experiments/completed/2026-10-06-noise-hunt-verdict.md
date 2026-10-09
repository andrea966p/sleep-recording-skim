---
tags: [experiment, conclusion, noise, emg, notch, grounding, series]
created: 2026-10-06
status: completed
---

# Is the noise hunt chasing a ghost? The verdict (2026-10-06)

> [!success] Update 2026-10-07: the cheap electrician work removed the EMG mains at the source
> The isolated-earth socket and the XDAQ bonded to the earthed rack cut the mains on every channel:
> - A2's EMG 60 Hz went from 26-33 to 1 µV, and B1's from 4-5 to 0.5 µV;
> - the chip floors dropped 12-60x.
>
> Details: [[2026-09-30-xdaq-noise-series#Entry 11: the electrician's work, and the first block after it (2026-10-07)|noise series Entry 11]].
> - **For new recordings the hardware now does what the notch did.** The notch decision below matters only for the archive
>   (recordings made before 2026-10-07).
> - **The prediction in Entry 10 ("a small effect at most") was wrong.** The effect was large.
> - **New first open item: the 800 µV ground gate now calls every chip UNJUDGEABLE.** It must be replaced before the next real recording.
> - The rest of this page stands as written on 2026-10-06.
>
> **Confirmed over 24 h (2026-10-09,** [[2026-09-30-xdaq-noise-series#Entry 12: the 29.5 h confirmation run after the grounding fix (2026-10-07 15:28 → 10-08 21:02)|Entry 12]]**):**
> - A2 is SCOREABLE without the notch (r@1min 0.615), and B1 at 0.587;
> - wake is 2-3x higher in the dark than in the light;
> - the hum stays down in every hour.
>
> The light-switch spikes were not changed by the fix.

> [!abstract] TL;DR
> **The question (Andrea, after the electrician's visit):** take away the per-mouse faults. Is the electrical noise that is
> left worth hunting, or can post-processing remove it? The per-mouse faults are:
> - an electrode not touching the dura;
> - cement on the electrode's metal pin;
> - misplaced EMG wires;
> - a failing tether;
> - a wrong ground connection.
>
> **The answer: what is left is mostly a ghost.**
> - **EEG:** the room's mains hum does not reach the sleep scoring.
> - **EMG:** there is ONE real problem, the 60 Hz mains, and a validated notch filter removes it in post-processing.
> - **Building-wide spikes:** rare, and epoch rejection already handles them.
>
> **The hunt was not wasted.** It found the one noise that matters and showed it can be removed.
> Drafted by Claude Code from the noise series and the archive. The recommendations are Claude's; the decisions are Andrea's.

## What is left once the per-mouse faults are out

| noise | size on a good mouse | does it hurt the data? | removable in post-processing? |
|---|---|---|---|
| EEG 60 Hz mains | 2–9 µV peak (A1 about 20) | **No.** Staging reads the EEG at 0.5–30 Hz (`FILT_EEG`, `BAND_TOTAL`), so 60 Hz is outside it | not needed |
| **EMG 60 Hz mains** | A2 13–33 µV, B1 3.6–5.7 µV | **Yes, the only real one.** On A2 it is the size of the quiet muscle tone, and across the archive it is a median 68 % of the EMG measure that stage 3 uses to call WAKE (10–124 Hz rms, no mains removal). Sleep then looks like wake | **yes**, a 60 + 120 Hz notch, validated below |
| building-wide spikes | the light timer at 09:00 and 21:00 (09-22 lights-ON: EEG up to 1056 µV, EMG 3.2–4.2 mV), plus about 6 unexplained ones in 24 h on the wire-free inputs (10-01/02) | barely, a few 4 s epochs a day | yes, epoch rejection ([[eeg-artefact-and-railing-rejection-policy]]: reject the epoch, never repair it) |
| people, hands, the wireless receiver, the air showers | nothing on the connected EEG/EMG (noise series Entries 8-9) | no | not needed |

## The EMG notch is validated (whole archive, 2026-10-02)
- **Setup:** 100 animal-recordings in `~/eeg-processed`. Without the notch, the test reproduces 99/99 official verdicts.
- **Result:** with 60 + 120 Hz notched (Q 30), SCOREABLE goes from **44 to 69**: 27 up, 2 down (07-31 C2 and 08-19 C1 fail the
  physiology checks after the notch).
- **Negative control:** the notched EMG with its 4 s epochs shuffled in time passes **0/100**. The notch does not invent sleep/wake structure.
- **Dose-response:** the gain tracks how much of the EMG measure is mains. Where mains is under 20 % of it, no verdict flips.
- **Biology gets more plausible:** more wake in the dark than in the light in **47/49** recordings that have both phases (41/49 as published).
- **Sources:** [[2026-10-02-noise-series-4mice-24h-analysis]] section 7 (Fig P); audit C3 in [[2026-10-02-noise-series-method-audit]];
  `eeg-emg-analysis/qc/emg_notch_validation_2026_10_02.py`.

## What has actually limited the data: the per-mouse faults
- The hum collapsed when the ground was moved to the right pin, on 2026-08-08 ([[2026-08-08-ground-fix-post-repin-night]]).
  It was a cerebellum ground on the wrong pin, not the building earth.
- The electricians' July earth wire changed nothing measurable ([[2026-07-31-contact-intermittency-no-wire-control]]).

## Recommendations (Claude's, for Andrea to decide)
1. **Adopt the EMG notch** (60 + 120 Hz). It is the real fix for the only noise that hurts.
   ⚠️ **DECISION OPEN:** it re-scores numbers already published (wake %, r@1min). Pre-register it, run the falsification suite, then re-score.
2. **Do the cheap electrician work, then stop the noise hunt.** That means the isolated-earth socket (we pay for the part only) and
   the foil earth busbar ([[2026-09-30-xdaq-noise-series#Entry 10: building electrician's inspection, and what he will change (2026-10-06)|Entry 10]]).
   Both are cheap, and the foils can be taken off again.
3. **Skip the expensive steps.** From the electrician: parallel earths, the 3rd-floor earth, a new earth rod. From the plan: Phase 2
   (aluminium boxes, Faraday cage) and T3 (tether shield). The lab is moving to E7 anyway.
4. **Put the effort into per-mouse reliability:** surgery (dura contact, no cement on the pins, EMG placement), the ground pin and the tethers.
   Phase 3 of [[2026-10-02-noise-troubleshooting-plan]] (counterbalance arm, slip ring) belongs here, judged on long runs.
5. **Keep judging every recording with the QC ladder.** NEVER WRITE "ALL OUR EEG IS CLEAN".

## Limits of this answer
- **Few mice behind the detailed numbers.** The noise measurements come from 2 clean mice on today's wiring, A2 and B1 (A1 and B2 have open EMGs).
  The notch validation covers 100 recordings.
- **Not every EEG recording is clean.**
  - Before 2026-08-08 the hum on some channels was 2.3–7.8 mV (07-15).
  - Light switching still puts spikes on the EEG.

  Those are the per-mouse ground fault and the rare spikes, not a reason to keep hunting.
- **A notch cannot rescue an EMG sitting on the rail** (open electrode, mV of hum). That is a per-mouse fault.
- **The notch also removes the muscle's own power at 60 and 120 Hz.** At Q 30 that is about 2 + 4 Hz out of the 114 Hz-wide EMG band.
  The validation above says the trade is a gain.

## Still open
- 🔴 **(added 2026-10-07)** Replace the 800 µV ground gate (audit C1). It now calls every chip UNJUDGEABLE after the grounding fix.
- Andrea's decision on the notch, now only for the recordings made before 2026-10-07.
- The 6 unexplained building events: ask facilities for the air handler (AHU) and chiller on/off log for 10-01 and 10-02.
- After the socket is replaced: one 10 min block before and one after, judged against the untouched spread in the plan.

Related: [[2026-09-30-xdaq-noise-series]] · [[2026-10-02-noise-troubleshooting-plan]] · [[2026-10-02-noise-series-4mice-24h-analysis]] ·
[[2026-10-02-noise-series-method-audit]] · [[2026-10-06]]
