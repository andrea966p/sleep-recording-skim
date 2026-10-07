---
name: grounding-fix-2026-10-07-mains-collapsed
description: "2026-10-07: the electrician's isolated-earth socket + XDAQ bonded to the earthed rack collapsed the mains on every channel (floors x12-60, A2 EMG 60 Hz 26-33 -> 1.0-1.4 µV). Side effect: the 800 µV hum ground gate now calls EVERY chip UNJUDGEABLE. Open EMGs A1/B2 no longer rail but are still not EMG."
metadata:
  type: project
---

**What changed (2026-10-07, before 13:43; e10 shut down cleanly, rebooted 14:34 on 7.0.0-28):**
- The rig wall socket was replaced with an isolated-earth socket. Its earth pin no longer touches the sandwich panel through the mounting screws.
  BUT its earth terminal is still the same shared building earth wire, so the isolation is only partial (Andrea's answer, and my reading, which she confirmed).
- The XDAQ now sits on the TOP rack shelf, screwed to it, with a short wire from the chassis GND to the shelf. The rack is earthed by a short, thick
  wire soldered to the shelf. That wire is one of 3 earth wires coming out of a hole in the wall beside the socket, from the building main line,
  not from the socket.
- The PC sits on ANOTHER, unearthed rack. One double wall socket feeds two multitaps: multitap 1 = the XDAQ brick only (2-prong);
  multitap 2 = the ASUS PC and everything else. The USB loop is: XDAQ chassis → rack → wall-hole earth ~ building ~ socket earth → PC → USB shield.
- The socket and the rack bond changed TOGETHER, so the effect cannot be split between them.

**Measured, block `~/radix/noise-tests/2026-10-07/E1-after-socket-rack_0__uid1007-15-04-18` (15:04-15:14, ZT6), same 4 mice:**
- Compared with 10-01 20:36/20:42 and 10-02 14:55/15:05 (same ZT), using `qc/noise_scan.py` + `qc/baseline_compare.py`.
- Two windows of the new block agree within 1-6 %. Outputs are in `out/`.
- Chip floors at 60 Hz: A1 2758-2943 → 232-235; A2 2057-2133 → 36; B1 712-1106 → 41-43; B2 1809-2008 → 41-42 µV.
  The 120 Hz floors fell x20-120. Broadband floors are unchanged, and no recorded notch or filter is involved (metadata checked).
- EEG 60 Hz is now ~2 µV on all four (A1 was 20). The EEG spectra are otherwise unchanged.
- EMG 60 Hz: A2 26-33 → 1.0-1.4 µV; B1 4.0-4.7 → 0.4-0.5 µV.
  - A2's mains share of the stager's EMG measure: 93-97 % → 12 % (`qc/emg_mains_share_windows.py`).
  - A2's raw quiet EMG (p10): 19-23 → 2.6 µV.
  - **For new recordings the hardware now does what the notch did.** The notch decision still matters for the ARCHIVE.
- Open EMGs:
  - A1: 4.65-4.85 → 3.22 mV, rail 13.5 % → ≤ 0.8 %.
  - B2: 4.7-5.0 → 0.57 mV, rail 14 % → ≤ 0.08 %.
  - Both now show a 3.0-3.8 Hz slow wave (430-890 µV rms) that does not follow their EEG or each other. Most likely the broken leads moving with
    breathing. No muscle band, so they are STILL NOT EMG (EEG-only mice).
- The A1 position still sees ~6x the field of the others (floor 232 vs 36-43).
- **I predicted "a small effect at most". It was large.** The July bond probably never made good contact (the electrician blamed the generic ring lug).

🔴 **The ground gate (`FLOOR_MIN_HUM_UV = 800`, `core/criteria.py`) now calls ALL 4 chips UNJUDGEABLE** (they were "grounded" on 10-02).
Any new official QC will reject every mouse at rung 2 until the gate is replaced (audit C1). This is Andrea's decision. Raise it before the next real run.

Figure: vault `05-experiments/attachments/2026-10-07-noise-figQ-grounding-fix-before-after.png` (`qc/electrician_before_after_2026_10_07.py`).
Related: [[noise-hunt-verdict-2026-10-06]] · [[emg-mains-corrupts-sleep-staging]] · [[weak-chip-ground-hides-as-electrode-failure]] · [[recording-2026-10-01-noise-4mice-overnight]]

**Confirmation run (started 2026-10-07 15:28:38 by Claude, Andrea's request):** console `ee0263bffeaa`, `allego_0__uid1007-15-28-38`,
stop **2026-10-08 21:02** (~29.5 h: rest of light, full dark, full light; both lights-OFF + lights-ON inside). Same settings as the 10-01/02
runs (batch `noise-tests`, POS-<slot>, A+B, 8 labels). Watchdog armed by hand at 15:29. Expect official QC UNJUDGEABLE on all chips (gate).
After DONE: compare hour by hour with the 10-01/02 24 h (`analysis-24h/hourly.csv`), and stage it diagnostically, with and without the notch.
Vault: noise series Entry 11 + Fig Q, journal 10-07, verdict-page update, audit C1 "now blocking" callout.
