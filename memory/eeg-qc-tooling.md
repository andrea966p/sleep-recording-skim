---
name: eeg-qc-tooling
description: "multimouse_scan.py metric caveats and verified bugs — don't trust 60Hz%raw or the hardcoded layouts"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 01d67996-fc6d-445a-b14a-bb600afc0cf8
---

QC tooling for XDAT recordings. Scripts in vault `02-procedures/eeg-data-analysis/scripts/` (hub `_eeg-analysis-hub.md`). Venv `/home/skimlab/eeg-analysis-venv`. Not yet under git.

⭐ **USE `state_scan.py` (2026-07-15), not multimouse_scan.py, to judge whether a recording contains SLEEP.** Layout derived from `sensors_by_port`; scorer-style filtering (bipolar → 60Hz comb → bandpass 0.5-30 EEG / **10-150 EMG** per 4s epoch); samples 1 epoch per N seconds so 272GB files are tractable.
- 🔴 **SINGLE-ENDED 60Hz IS NOT A CONTACT FAULT** (2026-07-18, Andrea's challenge). REF pin is empty by design → every leg floats up on the FULL common-mode mains hum, which **cancels in the bipolar difference** (EEG_F−EEG_P, EMG_L−EMG_R). A leg at 4mV single-ended can still give a clean differential. **The real per-leg fault is CLIPPING (`rail%`)** — a saturated amp is non-linear and does NOT subtract out. Contact model: an OPEN/high-Z leg floats to the full common-mode swing and RAILS; a well-seated leg is clamped near tissue and stays inside ±6390. So `rail%` per leg = the contact readout (consistent with `differential_60Hz ≈ common_mode × Z_imbalance`).
- **EMG band = 10-150 Hz + 60Hz notch** (Rayan 2024 EJN; Sensors 2025), NOT 10-100. `state_scan.py` runs EMG at **full fs (1000), not decimated** — decimated Nyquist (fsd/2=125 at DEC=4) is below the 150Hz edge, so EMG gets its own full-rate notch comb + bandpass while EEG stays decimated. `EMGrl%` column = median EMG-leg clipping (verdict previously ignored EMG rail entirely).
- **EMG contact is NOT our blocker** (2026-07-18 re-analysis of all troubleshooting runs): C2/D1/D2 show clean live bimodal EMG (`EMGrl%`<9%, 700-1300µV) every run. **A2 is the chronic EMG offender** (17-23% clip every run) yet has our cleanest EEG pair — contact is per-electrode not per-animal. **Frontal EEG remains the entire wall**; still zero sleep biology anywhere.
- **numpy 1.26 on this box** → use `np.trapz` not `np.trapezoid` (2.0 name); the latter crashes.
- **THE GATE = `td_sep`** = Cliff's delta of θ/δ between LOW-EMG and HIGH-EMG epochs. Real sleep: low EMG = NREM = delta-rich = LOW θ/δ → **strongly NEGATIVE** (<-0.25). Noise has no reason to produce this. Dead archives = -0.2…+0.2. **NO channel has ever legitimately passed** (the -0.65 of 2026-07-15 was retracted as a clipping artifact).
- 🛑 **REJECT CLIPPED EPOCHS BEFORE ANY METRIC — this invalidated our biggest claim** (2026-07-16). A railed amp is non-linear ⇒ its spectrum is meaningless, and clipping COVARIES WITH EMG, which manufactures a fake td_sep. Real case: A1 `uid0715-18-58-54` gave td_sep −0.65 on all epochs but **+0.63 once epochs ≥10% clipped were dropped — the effect FLIPS SIGN.** Rail = ±6390µV (RHD2216); real mouse bipolar EEG is <300µV, so a std of ~4050µV means hard saturation.
- **ALWAYS report `keep%` (fraction of epochs with ~0 clipped samples), NOT just median rail%.** "rail 19.3%" sounds like 1 epoch in 5 is bad; it actually meant the MEDIAN epoch was 19.3% clipped and only 1 of 493 epochs was clean. Two different quantities, catastrophically confusable.
- `state_scan.py` now prints `UNSCOREABLE (only N clean epochs)` when clean epochs ≤60 and **never falls back to dirty data** (the fallback silently printed "SLEEP-LIKE" from 3 railed epochs).
- `--start-h` / `--end-h` trim the analysis window (lights-on cutoff, chewed tether, etc).
- **`persist` and `bimod` alone are FALSE-POSITIVE GENERATORS** — the dead 72h run scores persist +0.93 (slow drift) and bimod 0.80 (bimodal noise) and LOOKS structured. Never verdict on variance; any noisy signal varies.
- `circ` = fraction of log-EMG power at 20-28h period. **A real mouse over ≥24h MUST show a circadian rhythm**; the 72h run scored 0.0% on all 8 slots = decisive negative.
- **Two flaws to never repeat** (found by Andrea's challenge): (1) never use a `phys%`-style metric whose denominator runs to Nyquist — HF junk above 40Hz tanks the score even when the EEG band is clean; a scorer bandpasses it away. (2) Never concatenate windows then Welch — it smears non-stationary hum. Filter like a scorer, metric PER EPOCH.
- Delta and EMG do NOT anti-correlate even in real sleep — **motion artifact during wake dumps low-frequency power into delta**, flipping the raw correlation positive. Use the θ/δ RATIO + EMG time course, not the correlation sign.
- "Delta-dominant at the right amplitude" is NECESSARY NOT SUFFICIENT — a quiet/dead high-Z input bandpassed to 0.5-30Hz also looks delta-dominant (1/f). Only **structure over time** separates brain from a shielded noise floor.

**`multimouse_scan.py` — verified defects (council 2026-07-15). Do not trust blindly:**
- **`60Hz%raw` is a power FRACTION → denominator-confounded.** A clean channel reads LOW because real signal fills the denominator; a dead-quiet input reads ~100% while being harmless. NOT a valid primary metric. Use **absolute µV** instead: single-ended 60Hz per leg + leg-imbalance ratio + notch-residual µV + delta-dominance (θ/δ<1).
- **Hardcoded `eight`/`four` LAYOUTS assume a fixed 64ch/port → MIS-MAP every slot when port channel counts vary.** Real example (2026-07-15): port B enumerated as 32ch, which shifted C/D by one slot — the scan mislabeled C1 as "B2" and ran off the end into aux channels, reporting a false DEAD. **Always derive base rows from the JSON `sensors_by_port` (`connection_ntv_idx` + `num_channels`), never hardcoded.**
- **`scan()` concatenates 40 overlapping windows before Welch** → understates variance ~20×. Sub-minute clips have n_eff ≈ 2-4, not 40 → those are SPOT READINGS, not validated states (this is how the 07-14 "clean" 42s clip fooled us).
- **`USABLE` threshold `eeg_rms_n<800µV` is too loose** (real mouse bipolar EEG is <300µV) and **never gates EMG** → a USABLE verdict certifies Wake/NREM only, never REM.
- **Floating/open slots are NOT an earth-state control** — open inputs antenna 60Hz regardless of system earth. Only CONNECTED channels are diagnostic.

**XDAT format:** float32 µV, 3-file set — `_data.xdat` (num_smpl × n_sig × 4) + `_timestamp.xdat` (int64) + `.xdat.json` (metadata under `status`). Files too big for RAM → memmap.

**Allego gotchas:** min 1000 S/s (decimate offline). **Forgets mode/rate/channel-select on EVERY re-enumeration** → re-set `XDAQ_ONE_REC` + 1000 S/s + reselect channels. **NEVER call SDK `GetIntanImpedance` while streaming** (crashes allegoserver → port 50051 refused); impedance ONLY via GUI paused (0.1-1MΩ good, ≫5MΩ open). Backend crashes under fast sensor-reload/channel churn → restart + re-set.

See also [[eeg-60hz-saga]].
