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
- 2026-10-28: Allego 4.1.2 with `radiens-core` records per port, so "start and stop is global" is no longer true for the XDAQ on Allego: see [[_allego-hub]] and [[2026-10-28-per-port-recording-bench-test]]
- 2026-10-28: **Meeting with the professor on Pinnacle**: one PC, start 8 to 12 units; no more TTL/video questions; no video licence; Sleep Pro value unclear; still ask high-pass 1.0 Hz, gain per channel or global, pin orientation, COMMON vs AGND. [[2026-10-28-pinnacle-reply-draft-range-highpass-sync]]
- 2026-10-28: **Reply to Pinnacle drafted, not sent**: their 2026-10-27 answers agree with the installer, Morelia and firmware reads. Draft answers their four questions (Ch3 stays standard ±465 µV, Andrea 2026-10-28: pontine waves mainly under 0.2 mV; high-pass and camera count left as brackets) and asks the Model Number string, connector drawing and battery. [[2026-10-28-pinnacle-reply-draft-range-highpass-sync]]
- 2026-10-27: **Pinnacle answered in writing** (Sam Kaplan, COO): TTL Plus to wireless alignment no better than about ±78 ms at 512 Hz (PC timestamps); Ch3 range can be widened but needs a Sirenia and Morelia gain change; they propose a 1.0 Hz high-pass; official 4 systems per PC, more than 16 run on one PC; USB bandwidth is not a limit. Four questions back to us; connector drawing still missing. [[2026-10-27-pinnacle-reply-software-ttl-headunit-pc]]
- 2026-10-27: **Morelia API and 8274/8274D firmware read**: Pinnacle's own Python API accepts only exact 8474 names like `8474HR-SE4`, so the custom unit's Model Number is the top question; an unused head-unit clock tick in every packet could give drift correction in our own decoder; `pypvfs` should read `.pvfs` on Linux. [[2026-10-26-sirenia-3-3-5-installer-static-analysis]] [[2026-10-27]]
- 2026-10-26: **Sirenia 3.3.5 installer read statically** (partial download, main EXEs missing): wireless timestamps come from the PC clock, so TTL Plus pulses meet 8474 samples only through PC arrival time; the 8474 has no TTL; cameras are Windows cameras or HTTP MJPEG only (no H.264); the custom unit's reported model string decides whether Sirenia applies the 14-bit ±465 µV scaling, with no user override: ask Pinnacle. Recording, TTL input and export need no licence; video is licensed per camera (max 8). [[2026-10-26-sirenia-3-3-5-installer-static-analysis]]
- 2026-10-26: **Questions sent to Pinnacle** (Andrea; shortened from the 2026-10-25 draft): software modules, what is strictly needed to record our own cameras' TTL pulses (free Sirenia, TTL Plus 9085-N, or a paid licence), Sleep Pro, the 8474-HR-SE4-C pin map, range and connector drawing, and the one-PC plan for 16 dongles. Answered 2026-10-27 (bullet above). [[2026-10-25-pinnacle-software-video-pc-questions-email]] [[2026-10-26]]
- 2026-10-23: Andrea: head-unit model code 8474-HR-SE4-C confirmed; 6 mm headmount limit confirmed (average B6 skull and surgical area), so the 6.4 x 7.8 mm drawing must shrink; Pinnacle runs on a separate Windows PC (Sirenia is Windows-only). The one-or-two-PC and "proven on our bench" questions are parked. [[2026-10-23]]
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
- **No Allego licence for the 32-mouse comparison**: all three ecosystems are priced on the free Open Ephys GUI (Andrea, 2026-07-28). Per-mouse start and stop is global on every option; the radiens per-port API is absent in 4.0.0 (2026-09-11; retracted for Allego 4.1.2 on 2026-10-28, see [[2026-10-28-per-port-recording-bench-test]]). [[2026-07-24-daq-32-mouse-final-comparison]] [[multi-user-independent-recording-schedules]]
- **Pinnacle: get answers in writing before the purchase order**, and do not trust the handover brief's part numbers or ranges. [[2026-10-16-pinnacle-wireless-16-mice-evaluation]]
- **Pinnacle: label every via hole and test it before cement** [[2026-10-16-pinnacle-wireless-16-mice-evaluation]]. The 512 Hz and +/-465 uV figures are for the 3-channel 8274-HR; confirm range and battery life of the 4-channel 8474-HR in writing before choosing a rate.

## Open items
- XDAQ route: outcome of the 2026-07-29 call, a written Kontex quote, commutator inventory (swings the budget by about €70k), headstage count, sample rate. [[2026-07-24-daq-32-mouse-final-comparison]]
- Pinnacle runs on its own Windows PC, because Sirenia does not support Linux (Andrea, 2026-10-23); the XDAQ route is not replaced. A Linux interface of our own is an option, depending on whether the premium software package (sleep scoring, video sync) is bought. [[2026-10-23]]
- Ask Pinnacle: does the premium software alone make the head units expose a TTL pulse, or is Pinnacle's TTL pulse generator needed, or can we use our own? Not clear on their website. [[2026-10-23]]
- The headmount board is drawn at 6.4 x 7.8 mm, over the 6 mm limit Andrea confirmed on 2026-10-23 (based on the average B6 skull and surgical area). [[2026-10-23]]
- Pinnacle: connector drawing and written answers from Pinnacle, electrode sites and the board layout, the video-sync decision (the wireless unit has no TTL input). [[pinnacle-wireless-plan-status]]
- Pinnacle: December 72 h test of 12 units on one PC, then the last 4 in January 2027. [[2026-10-20]]
- Contradictions found in this folder, settled and open: [[contradictions-rig-expansion|contradictions log]]

## Everything here
![[area.base]]
