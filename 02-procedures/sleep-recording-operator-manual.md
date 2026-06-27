---
tags:
  - procedure
  - operator-manual
  - radiens
  - allego
  - headstage
  - eeg
  - emg
  - sleep
  - onboarding
created: 2026-06-27
status: complete
---

# Sleep-Recording Operator Manual (Intan RHD2216 + NeuroNexus Allego)

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The **start-here hub** for running the mouse sleep EEG/EMG rig end to end — from plugging the hardware together to reading the data. It does not repeat the detail; it puts every guide in the **right order** and tells you what "done" looks like at each step.
> **Why it exists.** The knowledge is spread across a dozen focused docs. New operators (and future-you at 2 a.m.) need one ordered path, not a folder to guess through.
> **How to read this page.** Follow the numbered phases top to bottom the first few times. Each phase links the deep-dive doc and states the **pass criterion** before you move on. Bookmark this page.

> [!important] The two rules that prevent 90% of lost days
> 1. **Ground the animal before you judge anything.** A floating animal rails every channel and hides all other problems ([[grounding-reference-noise-concepts]], [[signal-quality-and-grounding]]).
> 2. **Stream, don't Record, while setting up.** `Record` starts a real session + video. Use `Stream` for all checks.

---

## The rig in one line
mouse 4-pin dura electrode → tether → slip ring → **C3410** adapter → **RHD2216** headstage → **C3026** SPI cable → **SAdpt-XDAQ-OM12** bridge → **XDAQ Core G1** → USB3 → **Allego**. Chip details: [[intan-rhd2216-reference]].

---

## Phase 0 — Understand before you touch (recommended once)
- **Read:** [[intan-rhd2216-reference]] (why bipolar, ±5 mV rail, no reference electrode), [[grounding-reference-noise-concepts]] (ground vs reference vs noise), [[eeg-emg-data-guide]] Part 1 (what EEG/EMG look like by eye).
- **Pass criterion:** you can say in one sentence each what *ground*, *reference*, *tissue noise*, *environmental noise* are, and why our `REF` pad stays empty.

## Phase 1 — Assemble the hardware
- **Do:** [[rig-assembly-guide]] — connect the chain in order, mind keying/"don't force", attach the animal-ground busbar, leave `REF` empty.
- **Pass criterion:** chain fully seated; animal ground wired to the bus; nothing forced.

## Phase 2 — Multimeter pre-power checks
- **Do:** [[multimeter-guide]] — ground-chain continuity (dura pin → bus → `GND` → chip GND must beep), no VDD↔GND short, (after power) VDD↔GND ≈ 3.2–3.6 V.
- **Watch for:** the slip-ring **green↔orange** defect ([[grounding-reference-noise-concepts]] §3) — if the ground beep fails end-to-end, suspect it.
- **Pass criterion:** ground beeps end-to-end; power reads ~3.3–3.6 V; no shorts.

## Phase 3 — Launch Allego, set the mode
- **Do:** open Allego → set Mode = **"XDAQ One (G1) with XR Headstage"** (`XDAQ_ONE_REC`). Reference: [[radiens-software-reference]]; troubleshooting: [[intan-headstage-troubleshooting]].
- **Pass criterion:** the port shows a channel count > 0 (e.g. 32), **not** 0. If 0 → wrong mode or detection fault ([[intan-headstage-troubleshooting]], socket-swap test).

## Phase 4 — Set the sample rate
- **Do:** [[allego-sampling-rate]] — set acquisition rate. **128–256 Hz is not possible** (minimum is 1,000 S/s); acquire at 1 kHz for sleep and **decimate offline**.
- **Gotcha:** switching Mode resets the rate to 1000 — re-check after any mode change.
- **Pass criterion:** rate set deliberately (1 kHz for sleep), confirmed after the last mode change.

## Phase 5 — Load the sensor map + select channels
- **Do:** [[signal-mapping-guide]] — load your custom sensor (csv2sensor) or passthrough; select **only** the wired channels (mind the sites-vs-`D/n` trap).
- **Pass criterion:** Signal Map shows your used channels mapped (no `−23`/no-site); correct channel count selected.

## Phase 6 — Ground/signal check on screen
- **Do:** `Stream`. Open the Monitor ([[allego-monitor-guide]]). Judge quality with [[signal-quality-and-grounding]] (§3 cheat-sheet) and Signal Metrics.
- **Pass criterion:** noise floor present (a few µV on quiet/unconnected channels), **no global railing** (floating animal), real EEG/EMG on wired channels, hum manageable. If everything rails together → ground problem, go back to Phase 2.

## Phase 7 — Save your setup
- **Do:** [[allego-presets-workspace]] — Save Workspace. **Note:** selected sites are **NOT** retained — you must reselect channels each session (manual p30).
- **Pass criterion:** workspace saved; you know what Restore does and doesn't bring back.

## Phase 8 — Record
- **Do:** set file name/location (Settings), then `Record`. (Project session/video automation: [[session-recording-workflow]] if applicable.)
- **Pass criterion:** recording running; data + video landing where expected.

## Phase 9 — Analyze EEG/EMG
- **Do:** [[eeg-emg-data-guide]] — read by eye first (sleep-stage signatures), then Python: decimate to 128–256 Hz, bandpass (EEG 0.5–30 / EMG 10–300), 50 Hz notch, paired-reference, band power / EMG RMS, simple hypnogram.
- **Pass criterion:** you can identify Wake / NREM / REM from your own traces and reproduce it in code.

---

## Quick-reference: which doc for which question

| I need to… | Doc |
|---|---|
| Understand the chip / why bipolar / ±5 mV | [[intan-rhd2216-reference]] |
| Plug the rig together | [[rig-assembly-guide]] |
| Use the multimeter | [[multimeter-guide]] |
| Understand ground vs reference vs noise | [[grounding-reference-noise-concepts]] |
| Map channels to electrodes | [[signal-mapping-guide]] |
| Judge if signal/grounding is OK | [[signal-quality-and-grounding]] |
| Use the Monitor tab | [[allego-monitor-guide]] |
| Set sample rate | [[allego-sampling-rate]] |
| Save/restore my setup | [[allego-presets-workspace]] |
| Fix a headstage problem | [[intan-headstage-troubleshooting]] |
| Analyze EEG/EMG data | [[eeg-emg-data-guide]] |
| Look up Allego features by page | [[radiens-software-reference]] |
| See the original bring-up story | [[first-headstage-connection]] |

---

## Related
- [[radiens-software-reference]] — primary Allego/Radiens reference (page index)
- [[first-headstage-connection]] — first-light bring-up log
- [[_INDEX]] — vault home
