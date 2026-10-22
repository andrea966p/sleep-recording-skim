---
name: overnight-two-animals-tether-is-the-fix
description: "2026-08-07 — a 23.66 h recording gave TWO working animals, retracted the arm C harm claim, and proved the tether chain (not long recovery) is what fixes signal quality"
metadata: 
  node_type: memory
  type: project
  originSessionId: 3430655c-999e-4bb1-abaa-9187f41c99d5
  modified: 2026-08-07T07:55:39.252Z
---

**Write-up:** vault `05-experiments/completed/2026-08-07-overnight-recording-two-animals-work.md`.
Journal `04-journal/2026-08/2026-08-07.md`. Retraction logged in
`05-experiments/active/2026-08-05-tether-comparison.md` §14.
Recording **`allego_1__uid0806-16-57-38`**, 2026-08-06 16:57:38 → 2026-08-07 16:37,
**23.66 h, 89.3 GB, 8517 epochs**, full light/dark cycle.

⭐⭐⭐ **TWO ANIMALS WORK NOW.** Threshold from 953,904 floor epochs = 60 Hz < **415.0 µV**.
✅ falsification passed (floor 0.00%, no-mouse A2 0.0%).
**B1: EEG 100%, EMG 99.6%, both 99.6%, longest unbroken block 215.8 min = 3.6 h.**
**D2: EEG 87.9%, EMG 98.6%, both 86.5%, longest block 87.3 min.**
Everything else 0.0% both. C1 EMG 37.8%, C2 EMG 15.2%, A1 EMG 7.6% (EMG only, unusable alone).
Spectral check agrees: **D2 slope −2.05 / delta 0.47 (steepest on the rig), B1 −1.81 / 0.32**,
floor range [−1.29, −0.07]. **Neither railed at all.**

🔴🔴 **RETRACTED: "arm C harmed D2" (2026-08-06) IS WRONG. THE SWAP FIXED D2.**
D2 EEG **0.0% → 87.9% usable**, median 60 Hz **916.9 → 133.2 µV**, slope **−0.38 → −2.05**,
railed epochs **29.7% → 0.0%**, EMG 86.1% → 98.6%.
**The 40-sweep block spanned only 21 min and caught ONE LONG OPEN STATE.** Drift and anaesthesia
were correctly excluded; **state persistence was not, and could not be, from a 21-min window.**

🔑⭐⭐ **THE RULE THIS PRODUCES: IMPEDANCE BLOCKS SCREEN, ONLY A MULTI-HOUR RECORDING IS AN
OUTCOME.** Always state a block's **duration** next to its duty cycle. **Never conclude harm or
benefit from a block alone** — a 40-sweep block gave p = 8.4e-08 for a conclusion that was exactly
backwards. This supersedes nothing about duty cycles being better than single sweeps; it says the
fix was **necessary but not sufficient**.

⭐⭐ **THE 16-DAY-RECOVERY CONFOUND IS RESOLVED: IT IS THE TETHER, NOT THE RECOVERY TIME.**
D2 was tethered **30 Jul, day 8 post-op** (short of our ≥14 d SOP) and had 0.0% usable EEG; a new
tether chain took it to 87.9%. This was the **pre-registered** disambiguation.
⇒ **The existing cohort is recoverable WITHOUT new surgery. The fix is an engineering change
applicable to every animal.** 🛑 Still no surgeries.

⚠️ **Four things changed together** in the swap: tether construction · slip ring removed ·
connector re-seated · one isoflurane episode. **"Does the new chain help" = YES. "Is it the slip
ring" remains unanswerable** without one anaesthesia per animal.
⭐ **But arm B improved B1 WITH the slip ring and arm C improved D2 WITHOUT it ⇒ what the two
successful chains share is SOLDERED + RESIN-ENCAPSULATED CONSTRUCTION.** Leading candidate,
circumstantial.

📌 **NEXT:** (1) ⭐ **circadian validation is finally possible** — 2 animals + a full light/dark
cycle; light-phase sleep should approach the literature ~70%, a threshold-independent check on the
whole pipeline; (2) **fit the new chain to the remaining animals**; (3) export B1 + D2 to EDF+ for
manual scoring; (4) C1's EMG still needs video.

📊 Figures `05-experiments/attachments/2026-08-07-figD-D2-before-after.png` (D2 spectrum before =
flat plateau, after = falls steeply and tracks B1) and `...-figE-usable-timeline.png` (usable epochs
across 23.66 h with light/dark shading).

🗂️ **PROCESSED DATA: `/home/skimlab/eeg-processed/2026-08-06/`** (both recordings start 08-06 so
they share the day folder). `INDEX.md` + **`by-mouse/A1..D2/`** with a README and symlinks each;
`impedance/` mirrors the six source blocks; `qc/` holds stage-1 JSON. Built with the canonical
`stage1_qc.py` + `stage2_split.py --all-verdicts`.
⚠️ **`stage2_split.py` copies the WRONG impedance files** — it flattened all four sweep blocks and
pulled in 44 sweeps from 2026-08-05 plus an unrelated file. Fixed by hand; sources verified intact
first. **Check `impedance/` after every stage2 run.**
✅⭐ **THIRD INDEPENDENT CONFIRMATION: the pipeline's own stage 1** (fixed 150 µV mains limit,
inherited, nothing to do with the floor control) gives **B1 CLEAN 100.00%, D2 CLEAN 98.68%, the
other six OPEN**.
⭐⭐ **B1's ENTIRE 23.66 h is ONE UNBROKEN BLOCK (1419.5 min, n_blocks = 1); D2's longest is
576.4 min = 9.6 h.** Both beat the previous project best (C1's 8.1 h on 31 July).
⚠️ **Block lengths differ between analyses and both are right**: pipeline = 4 s epochs + inherited
gate; my §1 analysis = 10 s epochs + floor-derived 415 µV + rms window + **both channels at once**,
which fragments blocks. **Quote the PIPELINE numbers for scoreability.**
🔴 **The final impedance sweep taken before disconnecting was NOT saved and is NOT recoverable** —
`zcheck_spec` is null in the recording JSON, the workspace CSV holds only the channel map, and the
gRPC call fires a NEW measurement. ✅ **Never sweep from the GUI: use
`eeg-emg-analysis/qc/sweep_block_all_ports.py`, which writes a CSV per sweep** (run
`remap_channels.py` first after any port change).

See also [[recording-usable-fraction-analysis]], [[fleet-duty-cycle-census-and-new-mouse]],
[[tether-soldered-duty-cycle-result]].


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- ⭐⭐⭐ **[TWO ANIMALS WORK; THE TETHER IS THE FIX](overnight-two-animals-tether-is-the-fix.md).** Impedance SCREENS; only a multi-hour recording is an OUTCOME.
