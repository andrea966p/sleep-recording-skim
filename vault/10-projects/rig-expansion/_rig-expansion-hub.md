---
type: hub
area: rig-expansion
status: active
created: 2026-07-28
summary: "Scaling the EEG/EMG rig from 8 to 16 or 32 mice: the XDAQ 32-mouse comparison (open, no purchase recorded) and the Pinnacle wireless 16-mouse plan (settled 2026-10-19, PC decided 2026-10-20)."
tags: [hub, scale-up, 32-mice, xdaq, kontex, pinnacle, acquisition, procurement]
---
# Rig expansion hub: 8 to 16 / 32 mice

## What this is
Getting the sleep EEG/EMG rig from 8 mice to 16 or 32 recorded at once. Two routes are written up: the **XDAQ / Open Ephys / Intan**
tethered comparison for 32 mice (July 2026), and the **Pinnacle wireless** plan for 16 mice with EEG, pons LFP and EMG (October 2026).
This page is the map. The detail lives in the linked notes; if a note and this page disagree, the note wins and this page is wrong.

## Current state
- 2026-10-22: No note says whether the Pinnacle plan replaces the XDAQ route or runs beside it; neither is marked closed. [[2026-07-24-daq-32-mouse-final-comparison]] [[pinnacle-wireless-plan-status]]
- 2026-10-20: **Pinnacle acquisition PC decided**: 16 head units in total (12 before the end of 2026, 4 in January 2027), one custom PC (ASUS PRIME B550-PLUS) with USB cards for the dongles, a second identical PC if it proves unstable. A 72 h test of the first 12 is planned for December. [[2026-10-20]] [[pinnacle-wireless-plan-status]]
- 2026-10-19: **Pinnacle plan settled with the professor**: custom 4-channel head unit (quote model 8474-HR-SE4-C, from Andrea's recollection, to be checked against the quote), our own headmount board, all 16 mice on one PC as the target. It replaces the 3-channel 8200-K9-SL purchase plan on the evaluation page. [[2026-10-16-pinnacle-wireless-16-mice-evaluation]] [[2026-10-19]]
- 2026-10-16: Pinnacle wireless evaluation written (±465 µV fixed range, no TTL input, Windows only, 512 Hz for 72 h runs; the handover brief's part numbers were wrong). [[2026-10-16-pinnacle-wireless-16-mice-evaluation]]
- 2026-07-29: **XDAQ 32-mouse route, last dated entry**: the call sheet for the Kontex finalization call. The vault records no call outcome, no written quote for 2 x ONE-R1024 with 8 Port Expanders, and no purchase. Posture on 2026-07-28: XDAQ in the lead pending that quote, Intan the benchmark, Open Ephys hardware out on isolation. [[2026-07-29-kontex-kc-call-prep-rig-finalization]] [[2026-07-24-daq-32-mouse-final-comparison]]

## Start here
- [[pinnacle-wireless-plan-status]]: settled facts and open items of the Pinnacle plan.
- [[2026-10-16-pinnacle-wireless-16-mice-evaluation]]: Pinnacle spec, literature, the 14 questions, prices.
- [[2026-07-24-daq-32-mouse-final-comparison]]: XDAQ vs Open Ephys vs Intan, priced bills of materials.
- [[xdaq-32-mouse-wiring-and-channel-law]]: the channel law and the wiring, wall socket to mouse.
- [[2026-07-29-rig-expansion-xdaq-route-map]]: the old hub, frozen at 2026-07-29, with the full document and vendor map.

## Rules that must not be broken
- **Animals = recording channels / 64.** Never reason from channel counts. A 1024-channel box records 16 mice; 32 mice always means two boxes; order the ONE+ as **R1024**, because R512 records only 8. [[xdaq-32-mouse-wiring-and-channel-law]]
- **Do not revive the killed ideas** (DDR doubling on the Core, 4 sockets per port, a splitter past the slot ceiling): the XDAQ Core is capped at 8 headstages by wire count. [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]] [[intan-rhd-spi-wiring-and-headstage-limits]]
- **Pricing stays inside the vault.** Kontex quote 262024 carries a do-not-disclose clause: never publish a page or Artifact with these numbers. [[2026-07-24-daq-32-mouse-final-comparison]]
- **No Allego licence for the 32-mouse comparison**: all three ecosystems are priced on the free Open Ephys GUI (Andrea, 2026-07-28). Per-mouse start and stop is global on every option; the radiens per-port API is absent in 4.0.0 (2026-09-11). [[2026-07-24-daq-32-mouse-final-comparison]] [[multi-user-independent-recording-schedules]]
- **Pinnacle: get answers in writing before the purchase order**, and do not trust the handover brief's part numbers or ranges. [[2026-10-16-pinnacle-wireless-16-mice-evaluation]]
- **Pinnacle: label every via hole and test it before cement** [[2026-10-16-pinnacle-wireless-16-mice-evaluation]]. The 512 Hz and +/-465 uV figures are for the 3-channel 8274-HR; confirm range and battery life of the 4-channel 8474-HR in writing before choosing a rate.

## Open items
- XDAQ route: outcome of the 2026-07-29 call, a written Kontex quote, commutator inventory (swings the budget by about €70k), headstage count, sample rate. [[2026-07-24-daq-32-mouse-final-comparison]]
- Relation between the two routes (replace, or run side by side): not recorded. Ask Andrea.
- Pinnacle: connector drawing and written answers from Pinnacle, electrode sites and the board layout, whether the 6 mm headmount limit holds, the video-sync decision (the wireless unit has no TTL input). [[pinnacle-wireless-plan-status]]
- Pinnacle: December 72 h test of 12 units on one PC, then the last 4 in January 2027. [[2026-10-20]]
- Contradictions found in this folder, settled and open: [[contradictions-rig-expansion|contradictions log]]

## Everything here
![[area.base]]
