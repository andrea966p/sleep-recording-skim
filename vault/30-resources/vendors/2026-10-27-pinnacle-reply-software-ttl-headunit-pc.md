---
type: reference
area: rig-expansion
status: active
created: 2026-10-27
summary: "Pinnacle's written answers (Sam Kaplan, COO, 2026-10-27) to our 2026-10-26 questions: TTL alignment no better than about ±78 ms, Ch3 range can be widened with a software change, 1.0 Hz high-pass proposed, 4 systems per PC official but more than 16 done, Morelia on Linux needs gain changes."
tags: [pinnacle, wireless, vendor, email, video-sync, ttl, pc]
---
# Pinnacle reply: software, TTL, head unit and PC (2026-10-27)

> [!abstract] TL;DR
> - Sam Kaplan (Chief Operating Officer, Pinnacle) answered our 2026-10-26 email ([[2026-10-25-pinnacle-software-video-pc-questions-email]])
>   on 2026-10-27 01:12 KST, to Staci Kim, cc ahyeon, VIVO Solutions Korea, me and Shaheen Latif. PDF: `~/.claude/uploads/.../Gmail_-_Re__Inquiry_about_wireless_system_for_mice.PDF`
>   (not copied into the vault).
> - **TTL to EEG alignment: assume no better than about ±40 samples, ±78 ms at 512 Hz** ("general engineering guideline,
>   not a guaranteed tolerance"). The PC timestamps the data, so drift is not their concern, packet jitter is. This matches
>   what the Sirenia installer showed ([[2026-10-26-sirenia-3-3-5-installer-static-analysis]]).
> - **Ch3 can get a wider range**, but a per-channel gain needs a Sirenia software change, and a Morelia change too. They
>   ask what range we want. They also propose a **1.0 Hz high-pass** instead of 0.1 Hz and ask if 0.1 Hz is necessary.
> - **PC:** official limit 4 systems per PC (conservative, video is the bottleneck); they have run **more than 16 wireless
>   units on one PC**. USB bandwidth is not a concern, so PCIe USB cards are not needed for bandwidth. Extensions up to 3 m.
> - Four questions back to us, below. They offer a 30-day Sleep Pro trial and a free Synchronized Video trial licence.

## Answers, by section

| Our question | Pinnacle's answer | Against the installer read |
|---|---|---|
| A. Video licence: per PC, camera or instance? K30 key? | Per camera, does not expire. Each 9000-K30 kit includes its video licence | Agrees (per-camera count, up to 8) |
| A. Sleep Pro at 512 Hz, separate PC, trial | 512 Hz "more than sufficient" for mouse scoring (no validation study named). Cluster and threshold scoring. Separate analysis PC allowed under normal licensing. 30-day trial offered | Not testable statically |
| B. Is TTL Plus always needed? | Yes, TTL Plus is required to capture external TTL alongside wireless recordings | Agrees: 8474 has no TTL |
| B. Alignment: sample counter or PC arrival? Accuracy, drift | PC timestamps incoming data, so clock drift "is not expected to be an issue". Packets give timing uncertainty: assume **≥ ±40 samples (±78 ms at 512 Hz)** | Agrees: PC clock with PLL. The head-unit tick in each packet stays unused |
| B. TTL Plus per PC, 30 pulses/s for 72 h | Samples up to 2000 Hz, so 30 Hz "should be feasible". 4 inputs per TTL Plus, **one Sirenia experiment per TTL Plus at a time**. Count depends on cameras and how recordings are organised | Installer: each edge is one annotation, no rate limit. 72 h not answered |
| B. Third-party USB / RTSP cameras, 4 per PC | Third-party USB cameras work for customers, not tested or guaranteed. **RTSP needs software modifications.** Pulses must also be tied to specific video frames to correct video latency | Agrees: no RTSP. HTTP MJPEG not mentioned by them (our question 4, not yet asked) |
| C. Channel layout | Ch1 EEG1 vs EEG COMMON, Ch2 EEG2 vs EEG COMMON, Ch3 EEG3A vs EEG3B, Ch4 EEG4A vs EEG4B, 8th pin AGND. Headmount **longitudinal, EEG COMMON and AGND toward the anterior end** | Matches our map (Ch3 = pons LFP, Ch4 = EMG) |
| C. Range | Standard ±465 µV, catalog "mV" is a typo. **Wider range on Ch3 possible**, they ask what range. Per-channel gain needs a software adjustment | Agrees: scaling is chosen by model string, no user override, so a different Ch3 gain means a Sirenia change |
| C. Connector drawing | **Not sent** | |
| C. Battery with 16 units, 8276 battery | About 5 days at 512 Hz nominal; many systems in one area may shorten it; not validated for 16. 8276 not answered | |
| D. 16 units on one PC | Official max **4 per PC** (conservative, video). They have run **more than 16 wireless units on one PC**. Ryzen 5 fine for EEG; no guarantee for 16 with video without testing | Installer: no dongle cap |
| D. One dongle per head unit? | Not answered | Installer: one unit per dongle in Sirenia |
| D. PCIe cards vs hubs, full or high speed | USB bandwidth not a significant limit: dedicated PCIe controllers or special hubs not needed for bandwidth. Space receivers apart, close to their transmitters, extensions ≤ 3 m | |
| D. Morelia on Linux for the 8474 | Open source, usable on Linux. The custom unit may need changes for channel-specific gain; they think it is straightforward but want to confirm first | Agrees: 8474HR support only on `develop`, exact-name allow-list |

## What this changes
- **Video sync through TTL Plus is ±78 ms at best**, about ±2 frames at 30 fps. Good enough to find a behaviour epoch
  (4 s or 10 s scoring epochs), not good enough for frame-level events. Frame-level sync would need our own decoder using
  the head-unit clock tick (a hypothesis, see [[2026-10-26-sirenia-3-3-5-installer-static-analysis]]).
- **A wider Ch3 range makes the unit non-standard in software.** Every future Sirenia update, and Morelia, must keep our
  per-channel gain. Ask for it in writing as part of the order, with the exact Model Number the unit reports.
- **The PCIe USB cards are optional**, not required. Keeping them still spreads the dongles over controllers; the reason
  is now isolation, not bandwidth.
- **1.0 Hz high-pass**: our plan asked 0.5 Hz, possibly 0.1 Hz ([[pinnacle-wireless-plan-status]]). Delta is 0.5 to 4 Hz,
  so a 1.0 Hz corner attenuates the slow end of delta. Decision for Andrea and the professor.

## Pinnacle's questions to us (to answer)
1. What EEG to video synchronization accuracy do we need?
2. How many cameras, and does each camera send its own TTL signal?
3. What input range would be ideal on Ch3 (pons LFP)? Our only data: ahyeon's 10 min awake test peaked at 522 and 921 µV,
   mouse P-waves are about 0.3 to 0.5 mV ([[2026-10-16-pinnacle-wireless-16-mice-evaluation]] §4).
4. Is the 0.1 Hz high-pass necessary, or is 1.0 Hz acceptable?

## Not answered yet
- Connector drawing (part, pitch, outline, pin 1) for our own headmount board.
- Whether one dongle serves one head unit; full or high speed USB; the 9005 hub.
- 8276 supplemental battery for 72 h runs.
- Questions 1 to 11 from the installer read (exact Model Number bytes, Master Clock pod, HTTP MJPEG Pi cameras, the head-unit
  clock tick, battery reporting, Morelia release): not recorded as sent.

Related: [[pinnacle-wireless-plan-status]] · [[_rig-expansion-hub]] · [[2026-10-27]]
