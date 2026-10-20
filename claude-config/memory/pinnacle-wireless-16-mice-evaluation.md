---
name: pinnacle-wireless-16-mice-evaluation
description: "2026-10-16: verified Pinnacle wireless (8274-HR) for up to 16 mice, EEG + pons LFP (DV 4.5) + EMG, 48-72 h. The handover brief had the part numbers wrong; ±465 µV fixed; no TTL; Windows only. Andrea chose Pinnacle only."
metadata:
  node_type: memory
  type: project
  originSessionId: b8226054-9323-4c7a-bf19-bc04204404e3
  modified: 2026-10-16T01:16:52.126Z
---

Andrea's handover `wireless_mouse_sleep_eeg_emg_lfp_handover.md` (Downloads) was checked against Pinnacle primary sources on 2026-10-16.
Andrea's answers: LFP target = **pons, DV 4.5 mm**; up to **16 mice** at once; **48-72 h**; **Pinnacle only** (no other vendors).

- 🔴 Handover WRONG: **8200-K9-SL** ($4,237) is the wireless system, ONE head unit + dongle per kit, mouse AND rat.
  **8200-K10-SL/SE** ($884.25) is only the mouse accessory kit. Store says K9 ships 8274-SL, 2026 catalog says 8274-HR-SL: unresolved.
- 8274-HR: 2600 V/V fixed, 14-bit, **±465 µV** (website/catalog print "mV", typo), EEG HP 0.5 Hz, EMG HP 10 Hz,
  battery 512 Hz 6 d / 1024 Hz 3 d / 2000 Hz 2 d ⇒ **512 Hz for 72 h**. **No TTL** ⇒ our Pi-pulse video sync cannot work.
  Sirenia = **Windows 10/11 only**. Pinnacle states no per-PC limit; Morrone 2023 tested 4, Kolling 2026 ran 10 for 72 h.
- 8201-SS pins: EEG1, EEG2, EEG COMMON, AGND, EMG A, EMG B ⇒ pons wire on EEG2 = pons − COMMON screw; 3 skull screws.
- Our 10-min unipolar data: EMG would flat-top in 18-46 % of awake seconds at ±465 µV; LFP_TGT ≤ 1.5 %. No REM tested yet.
- Recommendation given: 4-mouse pilot before 16; 14 questions + email draft (to VIVO Solutions, Korean distributor) in the vault page.

**Why:** a ~$71k purchase rests on these; the handover's numbers would have bought the wrong item.
**How to apply:** before any Pinnacle order or answer, read `vault/06-references/2026-10-16-pinnacle-wireless-16-mice-evaluation.md`
and check whether Pinnacle's written answers have been filed there. Script: `eeg-emg-analysis/qc/wireless_range_clip_check.py`.
Related: [[unipolar-run-2026-10-15-ahyeon]] · [[project_hardware_sync_neuronexus_reply]]

**SETTLED 2026-10-19 with the professor (supersedes K9-SL):** custom 4-ch **8474-HR-SE4-C** (Andrea's recollection of the quote):
2 EEG + 2 fully independent channels; professor requests EEG high-pass 0.5 Hz, maybe 0.1 Hz. We design our OWN headmount PCB
(redesigned 10-19 in skull coordinates: pins at Tsukuba EEG sites + separate pons LFP target/reference pins, 6.4 ML x 7.8 AP mm, routed 2-layer, clearance check PASS). Target: all 16 mice on one PC.
Pin map verified (catalog p.10): 4-ch standard = CH1/CH2 vs COMMON, CH3/CH4 differential, 1 COMMON + 1 GND, 8 pins, NO spare
(my "2nd GND" was wrong). Headmount socket female, openings up. Drawing + script: `vault/06-references/attachments/`. Journal [[2026-10-19]].
