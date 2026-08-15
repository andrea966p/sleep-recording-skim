---
name: ecg-cohort-2026-08-07
description: "2026-08-07 evening — 7 new EEG+EMG+ECG mice replaced the whole cohort; impedance is the best ever recorded while the live stream shows no biology at all, and the unsoldered 8co tether may be shorting the bipolar pairs"
metadata: 
  node_type: memory
  type: project
  originSessionId: a13e9044-6cc6-4f21-b8d5-7413872da116
  modified: 2026-08-07T10:17:39.667Z
---

**Section:** vault `05-experiments/active/2026-08-07-ecg-cohort-baseline.md`.
Journal `04-journal/2026-08/2026-08-07.md` (evening half). Sweeps
`~/Downloads/impedance measurments/2026-08-07/01-ecg-cohort-baseline-30sweeps/`,
config string `8slots-ECG-Actrl-4ports-64ch`.

⭐⭐ **NEW COHORT: 7 new mice, THREE bipolar channels each — EEG `/1`, EMG `/2`, ECG `/3`;
second mouse per port = `/33`,`/34`,`/35`.** 1000 Hz, 4 ports, 256 ch, map UNCHANGED.
**Port A slot 2 = the old B1new mouse kept as a positive control** (short soldered + resin
tether). Tether on the new mice = **22 cm, 8 conductor, thicker, wires NOT soldered, thin
heatshrink**. **Ground tissue wire now from CEREBELLUM, not right parietal.**

🔑⭐⭐ **FLOOR CONTROL CHANNELS CHANGED: now `/4`-`/16` and `/36`-`/48` (104 ch), because `/3`
and `/35` are wired now.** ⚠️ still NEVER `/17`-`/32` or `/49`-`/64`. 🔴 **The dedicated empty
A2 cut-tether control is GONE** (all 8 slots filled); A/35 is a free substitute since the
control mouse has no ECG implanted.

🔴🔴 **THE CENTRAL CONTRADICTION.** 30-sweep block (17.4 min, floor 3.4% — calibrated):
**19 of 21 new-mouse channels beat the floor, 7 at 100% duty with ZERO flips — BY IMPEDANCE THE
BEST THE RIG HAS EVER LOOKED** (08-06 was 4 of 14). **But 120 s of live stream shows 22 of 24
channels at 2-6 µV median = amplifier noise.** Three checks agree: slope inside bare-wire range;
residual cross-correlation < 0.5; ⭐⭐ **NOT ONE ECG CHANNEL HAS A HEARTBEAT** (interval CV
0.31-0.46; a real mouse heart gives < 0.1). **Only the control A/33 is real** (slope −1.93,
85 µV) ⇒ rig/amps/analysis exonerated, fault is animal-side of the connector.

⚠️⭐⭐ **THE 0.5 MΩ CRITERION CALLS OUR BEST-EVER CHANNEL OPEN.** Control A2 = 0.0% duty on all
three sites; B1's EEG median was already 0.813 MΩ. The threshold beats an unwired floor, it is
**NOT an absolute measure of contact**. Never quote it as one.

⭐⭐ **LEADING HYPOTHESIS (not a result): THE BIPOLAR PAIRS ARE SHORTED IN THE UNSOLDERED 8co
TETHER.** A short explains all three at once — very low |Z| (several sites 4-20 kΩ, at/below the
published 10-50 kΩ epidural range), **fleet-wide 60 Hz hum collapse** (800-5500 µV → 20-210 µV,
a real and new change), and **zero differential signal by construction**. Both chains that ever
worked here were **soldered + resin encapsulated**. 📌 **Test = the overnight recording; if flat,
next step is a BENCH pin-to-pin continuity check on a SPARE 8co tether, no animals.**
⚠️⭐ **LOW HUM IS NO LONGER A CONTACT PROXY ON THIS COHORT** — hum was cleanly bimodal before;
now you can have 20 µV hum over 3 µV of nothing. Re-derive every hum threshold from this
cohort's own floor.

🗂️ **RECORDING `allego_0__uid0807-19-14-58`** started 2026-08-07 19:14:58 KST in
`~/radix/data/`, 1000 Hz, 262 ch, verified growing. andrea stops it 08-08.

🛠️ **TOOLING:** ⭐ `qc/sweep_block_all_ports.py` generalised — `--roles eeg,emg,ecg` (or
`eeg,emg` for the old cohort), date/config from args, console criterion moved 2 MΩ → **0.5 MΩ**.
⭐ NEW `qc/block_duty_cycle.py BLOCKDIR --roles ... --thresh 0.5` = duty cycle + flips +
binomial test vs the in-file floor. ⚠️ `radiens` lives in **`/opt/neurosurveillance/venv`**;
scipy analysis needs **`~/eeg-analysis-venv`**; neither has both.
🔑 **Live stream: `client.get_signals()` returns ONLY the GUI-selected channels** (24 here), in
the order of `get_channel_metadata().table[selected == True]`.

🔴⭐ **RADIENS LIBRARY BUG: `AllegoClient.set_recording_config()` IS BROKEN** —
`StatusCode.INTERNAL "Exception serializing request!"` because `ConfigRecording` has a
**required `recordingType` enum** that `api_allego.py` never sets. Build the protobuf yourself
with `recordingType=ap.continuous`. ⚠️ **A failed config silently leaves the old path**, and
**`get_status().recording.path` is USELESS — it reports the calling process's cwd.** Only proof
is `ls` the destination and watch `_data.xdat` grow.

See also [[overnight-two-animals-tether-is-the-fix]], [[recording-usable-fraction-analysis]],
[[fleet-duty-cycle-census-and-new-mouse]].
