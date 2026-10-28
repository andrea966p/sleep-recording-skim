---
type: reference
area: rig-expansion
status: active
created: 2026-10-22
summary: "What is settled, what is open and what the old evaluation page no longer says, for the Pinnacle wireless 16-mouse plan (EEG + pons LFP + EMG), as of 2026-10-20."
tags: [pinnacle, wireless, headmount, purchase, pc]
---
# Pinnacle wireless 16-mouse plan: settled facts and open items

> [!info] 2026-10-23: Andrea confirmed the head-unit model code **8474-HR-SE4-C** and the 6 mm headmount limit (average B6 skull and surgical area). [[2026-10-23]]

> [!abstract] What this is
> One page for the Pinnacle wireless plan, because its facts are spread over the evaluation page and two journal days.
> The evaluation page ([[2026-10-16-pinnacle-wireless-16-mice-evaluation]]) is still the source for the spec, the
> literature and the 14 questions to Pinnacle. Its body (K9-SL kits, 4-mouse pilot, 4 PCs of 4 mice) pre-dates the
> decisions below. Written 2026-10-22 from those notes and the Claude memory file of the same name; nothing here is new data.

## Scope, as Andrea gave it on 2026-10-16
- LFP target: **pons, DV 4.5 mm**. Up to **16 mice** at once. Runs of **48 to 72 h**.
- **Pinnacle only**, no other vendors considered. (This line is not on the evaluation page; it comes from the memory file
  written on 2026-10-16.)
- Source: the handover brief `wireless_mouse_sleep_eeg_emg_lfp_handover.md` (Downloads), checked in [[2026-10-16-pinnacle-wireless-16-mice-evaluation]].

## Settled with the professor, 2026-10-19 ([[2026-10-19]])
- **Head unit:** custom 4-channel **8474-HR**. The model code **8474-HR-SE4-C** is Andrea's recollection of the quote, not read from
  the quote itself: check it. 2 EEG + 2 fully independent channels. The professor asks Pinnacle for an EEG high-pass of
  **0.5 Hz, possibly 0.1 Hz** (stock seizure setting 1.0 Hz).
- **Pin map:** Pinnacle's 4-channel standard configuration (catalog p.10): CH1 = EEG1 minus COMMON, CH2 = EEG2 minus COMMON,
  CH3 = pons LFP target minus LFP reference, CH4 = EMG A minus EMG B, plus one COMMON and one GROUND. 8 pins, no spare. The
  "second GND" idea was retracted on 2026-10-19.
- **Headmount:** a printed circuit board designed by us, Pinnacle connector, electrodes soldered by us.
- **All 16 mice on one PC** is the target, to be confirmed by Pinnacle and by a test.
- The meeting brief (`2026-10-19-pinnacle-electrode-setup-meeting-brief.pdf` in `30-resources/meetings/`) still describes the 8400-K40 3-EEG/1-EMG option;
  the settled unit above replaces it.

## Headmount design state, 2026-10-19 ([[2026-10-19]])
![[2026-10-19-custom-headmount-concept.png]]
- Redrawn in skull coordinates following [[tsukuba-sleep-recording-method]]: pins at the stereotaxic EEG sites, a separate LFP
  target pin and LFP reference pin (pons entry AP -5.4, ML 0.9, tips 1 mm apart, DV about 4.5), EMG pads at the back edge.
  Two-layer board, automatic clearance check PASS (trace 0.15 mm, clearance at least 0.15 mm).
- Size **6.4 mm ML x 7.8 mm AP**. The first brief said "must fit within 6 mm"; Andrea noted that number may be wrong (see
  [[2026-10-19]]). Not settled.
- Bregma to lambda taken as 4.2 mm, a reference value: scale AP to the measured distance.
- Not known: pitch, gender and outline of the 8474-HR connector. Parts already on our shelf (8-position 1.27 mm sockets) are
  not confirmed to match.
- Files: `_attachments/2026-10-19-custom-headmount-concept.png` and `.svg`, made by `_attachments/headmount_drawing.py`
  (the evaluation page still names `attachments/...`, an old path).

## Acquisition PC, decided 2026-10-20 ([[2026-10-20]])
- **16 head units in total: 12 before the end of 2026, 4 more in January 2027.**
- **One custom PC**, DDR4, ASUS PRIME B550-PLUS (5 slots: x16, x16 at x4, three x1), single-slot graphics card, dongles on
  extensions. Later the same day: 4 dongles on the rear USB ports plus 3 PCIe x1 cards of 4 dongles each = 16.
- If unstable: a second identical PC and move 2 cards (8 + 8). Sirenia Acquisition is free on any number of PCs (catalog).
- Rejected: Lenovo/HP/Dell business towers and Pinnacle's 9001-K1-AW workstation.
- Plan: run all 12 for 72 h in December on this PC and look for gaps, then add the 4 in January.
- Not verified: Korean part prices; whether 16 dongles run cleanly on one PC (nobody has published it: Morrone 2023 tested 4,
  Kolling 2026 ran 10, neither gives PC specs).

## What the evaluation page no longer says
| Evaluation page, section | Now |
|---|---|
| Title block and section 8: 4 x 8200-K9-SL pilot, then 16 | Superseded by the custom 4-channel unit; 12 + 4 units instead of a 4-mouse pilot (2026-10-19, 2026-10-20) |
| Section 6: start with 4 PCs x 4 mice | Superseded by one PC with USB cards (2026-10-20) |
| Section 3: 3-channel pin map (CH3 = EMG) | Replaced by the 4-channel map above |
| Section 7: no TTL, so Pi-pulse video sync cannot work | Still true; no decision on video sync is recorded |

## Still open
- [ ] Pinnacle: connector drawing for the custom unit, written answers to the 14 questions in section 9 of the evaluation page. Whether the email draft was sent is not recorded.
  2026-10-26: a new question set (software, TTL, connector drawing, PC) was sent; answers pending. [[2026-10-25-pinnacle-software-video-pc-questions-email]]
  2026-10-27: Pinnacle answered most of it; the connector drawing, dongle count per unit and the 8276 battery are still unanswered. [[2026-10-27-pinnacle-reply-software-ttl-headunit-pc]]
- [ ] Answer Pinnacle's four questions (2026-10-27): sync accuracy needed, camera count and TTL per camera, ideal Ch3 range, 0.1 Hz vs their proposed 1.0 Hz high-pass. [[2026-10-27-pinnacle-reply-software-ttl-headunit-pc]]
  2026-10-28: reply drafted; Ch3 stays standard ±465 µV (Andrea: pontine waves mainly under 0.2 mV); high-pass and camera count still brackets; not sent. [[2026-10-28-pinnacle-reply-draft-range-highpass-sync]]
- [ ] Update the meeting brief and the evaluation page body to the 4-channel unit (listed open on 2026-10-19).
- [ ] Electrode sites, then the KiCad board and Gerbers.
- [ ] Decide on video sync (no TTL input on the wireless unit). 2026-10-25: routes and questions in [[2026-10-25-pinnacle-software-video-pc-questions-email]].
  2026-10-26: the Sirenia 3.3.5 installer shows TTL pods and wireless units share only the PC clock; five new questions for Pinnacle, top one the model string of the custom unit.
  2026-10-27: Morelia and firmware read: the model-string risk holds in Pinnacle's Python API too; four more questions (8 to 11). [[2026-10-26-sirenia-3-3-5-installer-static-analysis]]
  2026-10-27: Pinnacle: TTL Plus is required, alignment no better than about ±78 ms at 512 Hz, RTSP cameras need software changes. [[2026-10-27-pinnacle-reply-software-ttl-headunit-pc]]
- [ ] Head mass 3.8 to 3.9 g plus cement and a depth wire on a 20 to 30 g mouse: check against the animal protocol.
- [ ] Is ahyeon's LFP target the same pons site? Her next run with REM would give a direct clipping test (`eeg-emg-analysis/qc/wireless_range_clip_check.py`).
