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

Figure: vault `_attachments/2026-10-07-noise-figQ-grounding-fix-before-after.png` (`qc/electrician_before_after_2026_10_07.py`).
Related: [[noise-hunt-verdict-2026-10-06]] · [[emg-mains-corrupts-sleep-staging]] · [[weak-chip-ground-hides-as-electrode-failure]] · [[recording-2026-10-01-noise-4mice-overnight]]

**Confirmation run (started 2026-10-07 15:28:38 by Claude, Andrea's request):** console `ee0263bffeaa`, `allego_0__uid1007-15-28-38`,
stop **2026-10-08 21:02** (~29.5 h: rest of light, full dark, full light; both lights-OFF + lights-ON inside). Same settings as the 10-01/02
runs (batch `noise-tests`, POS-<slot>, A+B, 8 labels). Watchdog armed by hand at 15:29. Expect official QC UNJUDGEABLE on all chips (gate).
After DONE: compare hour by hour with the 10-01/02 24 h (`analysis-24h/hourly.csv`), and stage it diagnostically, with and without the notch.
Vault: noise series Entry 11 + Fig Q, journal 10-07, verdict-page update, audit C1 "now blocking" callout.

**RESULT of the 29.5 h run (analysed 2026-10-09; outputs `~/radix/noise-tests/2026-10-09/`):**
- Hourly hum, QC bundle (`qc/hourly_hum_bundle.py`):
  - floors max 239 µV (bar 300; before 664-2965);
  - A2 EMG 60 Hz 0.5-2.3 µV (bar 3; before 14-27); B1 0.6-2.7 µV (before 4.2-4.7);
  - EEG 60 Hz 2-3 µV on all four. PASS.
- Light switching NOT smaller (`qc/light_switch_peaks.py`): lights-ON floors 1.7-5.2 mV vs 1.3-5.5 mV before. Lights-OFF small both times. FAIL.
- System-wide events, same voting chips A2+B1: 1 unexplained (10-08 01:08:09, small) in 29.5 h vs 6 in 24 h before.
  10-08 17:31:24 falls inside a lab member's visit (markers `MARKERS_visit_2026-10-08.tsv`).
- Staging, diagnostic (`--all-verdicts` + `qc/emg_mains_staging_test.py`):
  - A2 SCOREABLE r@1min 0.615 as published (before REJECT 0.19/0.29); B1 0.587;
  - the notch changes nothing (0.630/0.589); shuffled r ≈ 0;
  - wake dark/light: A2 55.6/26.9, B1 61.1/20.6 (before as published 17.8/11.3 and 30.1/17.6).
- ✅ RESOLVED 2026-10-09 (Andrea: nothing wired to the GPIO; option A): manual strip `--gpio-never-connected`, bit-exact; run DB backed up, FAILED_STRIP→STRIPPING→STRIPPED via RunStore, `POST /postprocess` → DONE, 4 CSVs sha256-verified on the NAS. Was: the console run was `FAILED_STRIP`: GATE B saw din_1 with 6 single-ms glitches at random times (floating input).
  - The raw data are safe.
  - To finish: `strip_channels --gpio-never-connected` (needs Andrea's assertion that nothing is wired to the GPIO header) or keep the GPIO channels.
  - The console's retry can do neither.

**Gate review 2026-10-14 (read-only, e10 `/tmp/qcgate/`, journal 10-14):** no automatic ground detector is supportable
post-fix (no post-fix known-ungrounded chip; every absolute feature overlaps floating-Aug 81-246 µV vs grounded-post-fix
34-222 µV). Fixing the hum gate unblocks ONLY uid1007 B1; the slope-validity gate keeps A1, A2, B2 UNJUDGEABLE (floor
slopes unchanged by the fix; old "empty floor ≥ −1.73" was mains masking) ⇒ recovering A2 = criterion redesign.
Recommended (c) era-dated gate: 800 before 2026-10-07 14:34, none after with "ground unverified". 🛑 Andrea's decision, pending.
