---
type: reference
area: rig-expansion
status: active
created: 2026-10-28
summary: "Draft reply to Pinnacle's 2026-10-27 answers: our answers to their four questions (sync accuracy, cameras and TTL, Ch3 range, high-pass) and the questions still open after the Sirenia installer, Morelia and firmware reads, with a settled vs open table for Andrea."
tags: [pinnacle, wireless, vendor, email, video-sync, ttl]
---
# Pinnacle reply draft: range, high-pass, sync, model string (2026-10-28)

> [!abstract] TL;DR
> - From Claude Code, 2026-10-28. Pinnacle's 2026-10-27 answers ([[2026-10-27-pinnacle-reply-software-ttl-headunit-pc]])
>   checked against the installer, Morelia and firmware reads ([[2026-10-26-sirenia-3-3-5-installer-static-analysis]]).
>   **No contradiction found.** Everything they said that the files can test agrees with the files.
> - The reply below answers their four questions and asks what is still missing. Values in `[brackets]` are Andrea's
>   or the professor's to fill: the high-pass choice, the camera count.
> - The single most important new question: **what Model Number string the custom unit reports.** Both Sirenia and
>   Morelia pick the 14-bit ±465 µV scaling and the 4th channel from that string.
> > - 2026-10-28: **Andrea decided Ch3 stays at the standard ±465 µV**: the detected pontine waves sit mainly under
>   0.2 mV (Andrea's note on [[2026-10-27-pinnacle-reply-software-ttl-headunit-pc]], written on the ThinkPad). So no
>   custom gain, no Sirenia or Morelia change, and question 3 of the draft answers "standard range".
> - Not sent. No dashes in the body except inside part numbers and model strings.

## Their answers against what we read in the files

| Topic | Pinnacle 2026-10-27 | Installer / Morelia / firmware | Verdict |
|---|---|---|---|
| Video licence | per camera, no expiry, one with each 9000-K30 | "Video Recording 1" to "8", counted per camera | agrees, settled |
| TTL Plus required | yes | 8474 class has no TTL members or command | agrees, settled |
| TTL to EEG timing | PC timestamps, assume ≥ ±40 samples (±78 ms at 512 Hz) | samples placed by PC arrival with a ±2 % PLL; snaps only when > max(8 samples, 1 s) off; up to ~1 s early after uncounted losses | agrees; the files add a worse case (~1 s after a dropout) they did not mention |
| 30 pulses/s | "should be feasible", TTL Plus samples to 2000 Hz | no rate limit; one annotation row per edge (~7.8 M rows in 72 h) | agrees; database load over 72 h untested |
| One experiment per TTL Plus | stated | not checked in the files | new fact; see open item on 16 units in one experiment |
| RTSP cameras | need software changes | no RTSP, ONVIF or H.264; HTTP MJPEG and Windows cameras only | agrees; HTTP MJPEG not discussed by them |
| Channel layout, headmount orientation | Ch1/Ch2 vs EEG COMMON, Ch3 3A/3B, Ch4 4A/4B, AGND; COMMON and AGND anterior | not in the files | settled by them, matches our map |
| Range ±465 µV | standard; Ch3 can be wider with a software change | 14-bit, ±465.4 µV, chosen from the model string, no override | agrees; adds the model-string dependency |
| High-pass | propose 1.0 Hz, ask if 0.1 Hz is needed | no hardware high-pass corner in the software | new from them |
| 16 units per PC | official 4 (video), > 16 done | no dongle or device cap | agrees |
| USB bandwidth | not a limit, no PCIe cards needed | FTDI "BT5 Dongle", 921600 baud, probably full speed | agrees |
| Morelia on Linux | yes; may need changes for per-channel gain | 8474HR only on unreleased `develop`, exact-name allow-list; timing code assumes 40 samples/packet where 4-channel HR has 30 | agrees; they did not mention it is unreleased |
| Dongle per unit | not answered | one head unit per dongle in Sirenia (dongle has 4 slots, Sirenia uses one) | settled from the files, confirm |
| Battery 16 units | ~5 d at 512 Hz, may shorten, not validated | no battery reporting in 0.4.1 firmware | partly open |

## Settled vs still open (for Andrea)

**Settled**
- Software: free Sirenia records all units, TTL Plus and exports; video is per camera; Sleep Pro is the analysis unlock.
- TTL Plus is the only way to get our pulses into Sirenia. Sync through it is PC-clock alignment, ±78 ms at best.
- Pin map and headmount orientation (COMMON and AGND anterior).
- Standard range ±465 µV on all four channels; "mV" in the catalog is a typo.
- One PC for 16 units is realistic for EEG only; video on that PC is the risk.
- PCIe USB cards are optional (isolation, not bandwidth). Extensions ≤ 3 m.
- Morelia works on Linux in principle.

**Decisions on our side (needed to reply)**
- ~~Ch3 range~~ **Decided 2026-10-28 (Andrea): standard ±465 µV**, detected pontine waves mainly under 0.2 mV. Data
  considered before the decision: mouse P-waves 0.2 to 0.5 mV, motor artefacts > 0.5 mV (Schott 2023), ahyeon's awake
  LFP_TGT peaks 522 and 921 µV (10 min, no REM). Headroom at ±465 µV is about 1x. ±2 mV would give 4x over the
  largest P-wave and still resolve 0.24 µV per bit at 14 bits. Caveat kept for the record: ahyeon's awake peaks (522, 921 µV) would flat-top
  in 0.2 to 1.5 % of 1 s windows; wake artefacts, not P-waves.
- High-pass: 0.5 Hz (our ask) vs 1.0 Hz (theirs). Delta is 0.5 to 4 Hz and the scoring band starts at 0.5 Hz, so a
  1.0 Hz corner attenuates slow delta. Decision for Andrea and the professor.
- Sync accuracy needed. ±78 ms is under one 4 s scoring epoch by a factor of 50: fine for scoring and behaviour bouts,
  not for frame-level events. If frame-level matters, the route is our own decoder on the head-unit clock tick.
- Camera count for 16 cages: not decided anywhere in the vault.

**Still open with Pinnacle**
- Model Number string of the 8474-HR-SE4-C; whether Sirenia 3.3.5 and Morelia accept it.
- ~~Whether the wider Ch3 range is analog gain~~ not needed (standard range chosen); still ask range and resolution of each channel on the final unit.
- Connector drawing (asked twice).
- 8276 battery for 72 h; battery voltage reporting.
- High-pass: filter order, why 1.0 Hz, settling time; anti-alias corner.
- Can 16 units and one TTL Plus share one Sirenia experiment, or does each experiment need its own TTL Plus?
- 9085 TTL Plus status (changelog lists "9085 I/O Monitor" as deprecated); Master Clock pod.
- HTTP MJPEG IP cameras (our Pi nodes) as Sirenia cameras.
- Head-unit clock tick in each packet; 8474 firmware; Morelia release with 8474HR.
- Dropout behaviour (firmware read says no buffering): confirm.

## Email draft

**To:** Sam Kaplan · **cc:** Staci Kim, ahyeon, VIVO Solutions Korea, Shaheen Latif (same list as their reply)

**Subject:** Re: Inquiry about wireless system for mice

> Dear Sam,
>
> Thank you very much for the detailed answers, they helped a lot. Below are our answers to your four questions, then a
> few points we still need before we place the order.
>
> **Your questions**
>
> 1. Synchronization accuracy. Our sleep scoring uses 4 second epochs, so the ±40 samples (about ±78 ms) you describe is
>    acceptable for scoring and for matching behaviour to sleep states. We do not need frame level accuracy for this
>    study. We would still like to know if the Master Clock pod improves the alignment between TTL events and the
>    wireless samples, or if it only stamps the TTL edges.
> 2. Cameras. We plan [N] cameras for the 16 cages, and each camera sends its own TTL pulse ([one per frame / one per
>    second]). Since one TTL Plus has 4 inputs and serves one Sirenia experiment, can all 16 head units and one TTL Plus
>    be in the same experiment? If not, how would you organise 16 units with [N] camera pulses?
> 3. Ch3 range. Thank you for offering a wider range. The pontine waves we detect sit mainly under 0.2 mV, so the
>    standard ±465 µV is sufficient and we would keep the standard gain on all four channels, with no software change.
>    Could you confirm the final unit is ±465 µV at 14 bits on every channel, Ch4 (EMG) included?
> 4. High pass filter. We would prefer [0.5 Hz]. Our delta band starts at 0.5 Hz, so a 1.0 Hz corner would reduce the
>    slow end of it. Could you tell us why you recommend 1.0 Hz (settling time, drift, noise), the filter order, and
>    whether 0.5 Hz is possible? What is the anti aliasing corner at 512 Hz?
>
> **Model number reported by the custom unit**
>
> 5. Which exact Model Number string will the 8474-HR-SE4-C report over Bluetooth? Could you confirm that Sirenia 3.3.5
>    and the Morelia release we would use both recognise it as a four channel 14 bit unit? We would like this written
>    into the order.
>
> **Still open from our earlier email**
>
> 6. Could you send the mechanical drawing of the head unit connector (part number, pitch, outline, pin 1)? We need it to
>    design our headmount board.
> 7. Do you recommend the 8276 supplemental battery for 72 hour runs at 512 Hz? Does the head unit report its battery
>    voltage anywhere in Sirenia?
> 8. We understand each BT5 dongle serves one head unit in Sirenia, so 16 units need 16 dongles. Is that right?
> 9. During a radio dropout, is the missing data lost (shown as a gap) or buffered and resent?
>
> **A few technical questions on timing and cameras**
>
> 10. Is the 9085 TTL Plus fully supported in Sirenia 3.3.5? We ask because the changelog lists the "9085 I/O Monitor" as
>     legacy.
> 11. Our cameras run on Raspberry Pi computers. Would Sirenia accept them as HTTP MJPEG IP cameras, each using one video
>     licence?
> 12. Each data packet seems to carry a counter from the head unit's own clock. What drives that clock and how stable is
>     it? If we write our own Linux recorder with Morelia, could we use it to correct drift between units?
> 13. When do you expect a Morelia release with 8474HR support, and could we have the 8474 firmware version our units
>     will ship with?
>
> We would be glad to take the 30 day Sleep Pro trial and the Synchronized Video trial licence. Could we start them when
> the first head units arrive, so we can test them on our own recordings?
>
> Best regards,
> Andrea
> SKIM sleep lab, KAIST

## Before sending (Andrea)
- [x] Ch3 range: standard ±465 µV (Andrea, 2026-10-28).
- [ ] Fill `[0.5 Hz]` (high-pass), `[N]` cameras and pulse rate, with the professor.
- [ ] Decide whether to keep question 12 and 13 (only matter if we build a Linux recorder).
- [ ] Question 1 says frame level sync is not needed: confirm that is true for this study.
- [ ] Questions 10 to 12 reveal we read the installer; drop them if that is unwelcome.

Related: [[pinnacle-wireless-plan-status]] · [[_rig-expansion-hub]] · [[2026-10-28]]
