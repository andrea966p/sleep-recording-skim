---
name: fleet-duty-cycle-census-and-new-mouse
description: "2026-08-06 — 20-sweep census of all 8 mice: only 1.8 of 8 animals usable per sweep; a 16-day-recovery mouse on the soldered tether hit 40/40 with zero flips; duty cycle proved reproducible across days"
metadata: 
  node_type: memory
  type: project
  originSessionId: 3430655c-999e-4bb1-abaa-9187f41c99d5
  modified: 2026-08-06T08:08:59.201Z
---

**The 2026-08-06 morning session.** Write-up: vault
`10-projects/rig-bringup/2026-08-06-fleet-duty-cycle-census.md`.
Files `~/Downloads/impedance measurments/2026-08-06/fleet-census/`.
Scripts: scratchpad `fleet_census.py`, `census_stats.py`, `probe8.py`.

⭐⭐⭐ **A NEW MOUSE READS 40/40 WITH ZERO FLIPS.** Implanted 21 Jul with the cohort but left
**untethered in its home cage until 6 Aug (16 d post-op)**, then put on the **19.5 cm short
soldered + resin tether** from arm B. EEG **20/20 = 100%**, EMG **20/20 = 100%**, **0 flips**,
EEG median 0.813 MΩ, max 1.531. It occupies the **B1 slot** (original B1 SACRIFICED 08-05, detached skull electrode).
Nearly identical to arm B on the old B1 (20/20, 0 flips, median 0.903, max 1.341).
⚠️ **TWO VARIABLES AT ONCE: 16 d recovery AND the soldered tether.** The other seven were
tethered at **day 8-10**, i.e. **4-6 d earlier than our own ≥14 d SOP** — this is the first
animal ever tethered SOP-compliant. **n=1. Do not claim either cause.**

🔑 **RIG ANSWER: capacity YES, yield NO.** 4 ports + C3442 splitters = **256 ch, 8 animals,
all enumerated clean** = the hard XDAQ Core ceiling, and capacity is NOT the constraint.
But **mean 1.80 of 8 animals had both EEG+EMG connected per sweep**. A 256-ch sweep takes
**31.4 s** (vs ~30 s for 64 ch).

Duty cycles, 20 sweeps 11:30-11:41 (EEG / EMG / both): **B1new 100/100/100** · A1 20/95/20 ·
A2 25/20/5 · B2 15/15/5 · C1 30/20/5 · C2 35/40/15 · D1 35/15/**0** · D2 30/100/30.
**13 of 16 channels flip**, up to 12 flips in 20 sweeps.

⭐⭐ **DUTY CYCLE REPRODUCES ACROSS DAYS — method validated.** D2 `D/1` 27.5% (08-05, 40
sweeps, no splitter) → **30%** (08-06, 20 sweeps, with splitter); `D/2` 97.5% → **100%**.
It is a **stable per-channel property**, which is what makes the 45%→100% arm-B result hard
to explain away.

🔴⭐⭐⭐ **THE A2 SLOT HAS NO MOUSE — IT IS AN UNWIRED NEGATIVE CONTROL, THE FIRST EVER.**
Cut tether attached to nothing, still through its slip ring + headstage + port A splitter.
It read **<2 MΩ in 9 of 40 channel-sweeps = 22%** (min **0.248 MΩ @ 1.3°**).
⇒ **THE 2 MΩ "CONNECTED" CRITERION HAS A 22% FALSE-POSITIVE RATE. Every duty cycle in the
15-35% band is indistinguishable from nothing attached.**
✅ **FIX: use |Z| < 0.5 MΩ** — control drops to **1/40 = 2.5%** while real channels still
score 30-70%. **Re-score old blocks before quoting them.**
✅ **LEAVE A2 IN PLACE** — a sweep reads all ports at once, so the control is free forever.
⭐ **Re-scored, only 4 of 14 channels in 7 animals beat the empty tether**: A1 EMG (70%,
p=2.9e-8), B1new EEG (30%, p=0.0042) + EMG (65%, p=1.8e-7), D2 EMG (70%, p=2.9e-8).
**B2, C1, D1, C2, A1 EEG and D2 EEG are ALL n.s. vs a cable attached to nothing.**
⇒ **the rig is really recording 1 animal of 8**, not 1.8.
⚠️ Does NOT overturn 08-05: arm B was 20/20 vs a 22% control. It does mean arm A's "45%
baseline" was partly false positives ⇒ **the true A→B effect is LARGER**.
⚠️ Removing the A2 mouse did **not** unload the port A splitter (headstage still plugged),
so A1's good EMG cannot be credited to splitter load.
⚠️ **C1 is NOT good** despite looking fine in a single sweep: 0/20 below 0.5 MΩ on both channels.

✅⭐⭐⭐ **TEARDOWN LADDER DONE 2026-08-06 — THE FALSE POSITIVES ARE THE AMPLIFIER, NOT OUR
CABLING.** Protocol + results: vault `10-projects/rig-bringup/2026-08-06-unloaded-chain-interference.md`.
Rungs on the empty A2 slot: full chain 9/40 = 22.5% · minus tether 8/30 = 26.7% · **headstage
alone 7/30 = 23.3%, best 0.107 MΩ**. **FLAT ⇒ tether, slip ring and splitter are all
INNOCENT.** ⚠️ **Rung A0 (unplug headstage) is DEGENERATE — it REMOVES the channels**: port A
went 64→32 ch, total 256→224, `A/33`,`A/34` ceased to exist. **Always remap after unplugging
a headstage.**
⭐⭐ **THE REAL FLOOR CONTROL IS FREE AND ALREADY IN EVERY SWEEP: `/3`-`/16` and `/35`-`/48` are
REAL amp inputs with NO WIRE** (mouse uses only 2 of 16). n=2240 → **21.4% <2 MΩ, 3.1% <0.5 MΩ,
min 0.051 MΩ**. Matches the cut-tether control to 1%. ⚠️ **EXCLUDE `/17`-`/32` and `/49`-`/64`**
— inactive slots, internally tied, 96% below 0.5 MΩ, they would destroy the control.
🔴 **The unwired floor reached 0.051 MΩ = the best electrode value ever recorded here ⇒ a
single low impedance reading is NOT evidence of contact, ever.**
⭐ **RECORDABLE ANIMALS (vs the 2240-sample floor, 0.5 MΩ): B1new ONLY** (EEG p=3e-05, EMG
p=5e-15). **A1 and D2 = EMG only** (p=1e-16), EEG n.s. ⇒ **cannot stage sleep**. **B2, C1, C2,
D1 = NOT recordable**, neither channel beats an unwired input. ⇒ **1 of 8 scoreable, 3 of 8 any
signal.** Status page for the professor: `30-resources/meetings/2026-08-06-rig-status-for-professor.md`.

📌 **NEXT — D2 + long custom tether this afternoon** (see [[tether-soldered-duty-cycle-result]]
for protocol: stay on port D, first sweep ~4 min after swap, 40 sweeps, re-run `remap.py`).
⭐ It now **disambiguates the new mouse for free**: D2 is day-8-tethered with a twice-measured
30% baseline ⇒ **near-100% after the swap = construction is sufficient**; **partial
improvement = recovery time matters** and the fix for the next batch is the ≥14 d SOP.
`D/2` at 100% is the **harm detector**. Still cannot say "it is the slip ring" — the long
tether changes construction and slip ring together.

🗂️ **FILES REORGANISED 2026-08-06 EVENING.** `~/Downloads/impedance measurments/2026-08-06/` is now
numbered chronologically: `01-fleet-census-20sweeps` · `02-teardown-rungA2-ring+headstage-15sweeps` ·
`03-teardown-rungA1-headstage-only-15sweeps` · `04-preswap-D2-baseline-15sweeps` ·
`05-armC-D2-longtether-noslipring-40sweeps` · `06-single-sweeps` · `README.md`.
Config string standardised to **`7mice-A2empty-4ports-64ch`** (seven mice — A2 is a cable).
Every move logged in `../RENAME-MANIFEST.csv`. ⚠️ **Single sweeps must NEVER be pooled into a block
folder** — that is why the arm C block was scoring 41 instead of 40.
📄 **Professor handout = `30-resources/meetings/2026-08-06-rig-status-for-professor.md`; its
PART 0 is a paste-ready short version (no dashes, per [[feedback_no_dashes_in_emails]]).**
Day log `04-journal/2026-08/2026-08-06.md`. Figures in `05-experiments/attachments/2026-08-06-*`:
**figA** threshold histogram · **figB** duty cycle per animal vs floor · **figC** D2 arm C timeline ·
**traces-filtered** · **psd**.

See also [[movement-dependent-contact-root-cause]], [[eeg-rig-current-state]],
[[recording-usable-fraction-analysis]].


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- ⭐⭐⭐ **[THE 0.5 MΩ CRITERION](fleet-duty-cycle-census-and-new-mouse.md).** Empty tether read "connected" 22% at 2 MΩ ⇒ use |Z| < 0.5 MΩ.
