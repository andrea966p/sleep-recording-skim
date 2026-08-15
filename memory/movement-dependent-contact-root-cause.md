---
name: movement-dependent-contact-root-cause
description: "2026-08-04 — the electrodes and implants are PROVEN GOOD (0.052 MOhm, D2 fully recovered) and the real problem is fast reversible contact intermittency; the movement hypothesis was proposed and DISPROVED the same day"
metadata: 
  node_type: memory
  type: project
  originSessionId: 1c8ce7c5-ec36-4595-9a71-7100cbae80c1
  modified: 2026-08-04T09:58:13.418Z
---

**The 2026-08-04 session. Seven sweeps in 23 minutes.** Full write-up: vault `05-experiments/completed/2026-08-04-movement-dependent-contact.md`. Timeline + file names: `06-references/impedance-sweep-register.md`. Files: `~/Downloads/impedance measurments/2026-08-04/`, all named `imp_2026-08-04_HHMM_<config>_<context>.csv`.

✅✅ **THE ELECTRODES AND IMPLANTS ARE GOOD. This is the solid part.**
- **B1 EEG = 0.052 MΩ @ 179.7°** (16:47, alone port B, mouse still). Best ever on this rig, EEG or EMG, and inside the published 10-50 kΩ band. A degraded/failed/badly-implanted electrode CANNOT produce that.
- **D2 recovered completely** from 9.200 MΩ (fully open after Run 2) and was connected on BOTH channels in EVERY sweep today: 0.352/0.233 · 0.459/0.270 · 0.400/0.088. Only animal to manage that. **Open channels recover.** Damage is not cumulative.
- ⇒ 🛑 **NO SURGERY, and now for a POSITIVE reason.** Don't use the [[electrode-failure-literature]] 82% figure to explain our numbers.

⭐ **THE REAL PROBLEM = FAST REVERSIBLE INTERMITTENCY.** B1 EEG across 23 min: **6.236 → 0.052 → 8.649 → 0.177 MΩ**. D1 EMG: 8.203 at 16:33, **0.688 at 16:42**. Consequences: **a single sweep cannot rank/screen/classify a channel** · comparing sweeps across days compares two *moments*, not two conditions (this kills the "EEG worse on 8/8 across Run 2" trend) · **a sweep takes ~20 s**.

⚠️ **THE MOVEMENT HYPOTHESIS WAS PROPOSED AND DISPROVED THE SAME DAY. Do NOT state that movement causes contact loss.** Evidence for: B1 alone, 16:47 still **0.052** vs 16:48 moving **8.649** (166×, both channels together, phase tracking). Evidence against: 16:56 pre-registered 8-mouse test (B1/B2/C1 moving, five still) gave **MOVED 3/6 vs STILL 5/10 connected — 50% vs 50%**. **The killer is B1 contradicting ITSELF**: 8.649 moving at 16:48, **0.177 CONNECTED while moving** at 16:56. Animals definitely still went open (A2 both, D1 both). ⚖️ Be fair in both directions: the 8-mouse test is **unpaired, n=8, ~50% base rate ⇒ very little power**, so its null is weak; the paired design was the better one and deserves a proper run (alternate still/moving on one animal several times).

☠️ **DEAD — never re-propose:** electrodes degraded/failing · cold solder joint pad 0/1 · board leakage or bridging · slip ring as a *statically* broken conductor · per-pad not per-channel-type · **port, splitter or XDAQ** (B1 works in port B AND port D, 16:44) · "we need new mice" · negative electrode permanently open.

❓ **STILL OPEN:** what triggers the flip · **slip ring under load** (never tested) · tether construction · **implantation depth** (⚠️ only the "pin marginally on the dura" version is consistent — plain "too shallow" can't give 0.052 MΩ — and it CANNOT help the current cohort, it's a future-batch protocol change).

📌 **NEXT = THE SWEEP LOOP (2026-08-05):** repeated sweeps every ~30 s for ~20 min, timestamped, via the radiens Python API, to measure **flip rate not state**. Required because at a ~50% base rate one sweep reading "good" proves nothing — every later comparison (slip-ring vs direct, old vs rebuilt tether) must be **duty cycle vs duty cycle**. Then: bypass slip ring with a direct tether (⚠️ changes 2 variables at once — prefer bypassing with the EXISTING tether), then rebuild tethers soldered+resin (⚠️ leave a flexible length before the headcap or the break point just moves).

🧹 **Room stripped 2026-08-04:** rack = wifi router + ASUS PC + XDAQ + white-noise generator only. ⚠️ **Pis and ALL CAMERAS REMOVED ⇒ NO VIDEO RECORDING** until restored, so behaviour can't be scored against the sweep loop yet.

⚠️ **Limits:** still/moving pair is n=1 and failed its one replication · "still"/"moving" judged **by eye**, not video (the labels in those two filenames are the experimenter's note, not an instrument reading) · **no board photographs taken, by choice** · only the positive input of each bipolar pair is ever measured · 8-mouse sweeps use splitters, single-animal ones don't.
