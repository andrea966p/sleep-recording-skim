---
name: a2-control-48h-reference-profile
description: "A2 control mouse gave 47.09 of 48.19 h usable EEG over two complete ZT0-to-ZT0 circadian cycles, with a working EMG and a day-to-day replication"
metadata: 
  node_type: memory
  type: project
  originSessionId: ad1ca725-35bc-44d8-b02a-ed707ae385f9
  modified: 2026-08-11T00:49:42.389Z
---

⭐⭐⭐ **THE BEST DATA THIS PROJECT HAS EVER TAKEN. `allego_0__uid0809-09-00-00`, 2026-08-09 09:00 to 2026-08-11 09:11, 48.19 h, 181.8 GB, INTACT** (173,496,576 samples both files, remainders 0). A2 = the old B1 mouse, port A slot 2, short soldered resin tether. Sites **`A/33` EEG, `A/34` EMG**.

⭐⭐ **STARTED AND ENDED AT ZT0** (lights on 09:00) ⇒ **two complete circadian cycles, 24.2 h light and 24.0 h dark, equal**. 📌 **Make a ZT0 start the default for any run over a day** — costs nothing, removes a correction from every circadian number. Helper `eeg-emg-analysis/qc/start_recording_at.py HH:MM:SS`.

**Quality:** **47.09 of 48.19 h usable = 97.7%** (light 99.1, dark 96.3), longest unbroken block 96 min, ⭐⭐⭐ **ZERO railed epochs in 17,349**. Median slope **−1.52** vs floor p1 **−1.11**; median 60 Hz **36 µV** vs floor median **2754 µV**. ✅ Floor scores 0.00% usable.

⭐ **THE EMG IS REAL — still the only working one on the rig.** State dependence r(delta, EMG rms) = **−0.645** over 2836 min, **negative in BOTH phases separately** (−0.514 light, −0.492 dark) so it is not the cycle driving both. ⭐ **Raw amplitude alone separates the phases with NO scoring: ~31 µV light vs ~73 µV dark.** ⚠️ **Sign convention: I correlate delta vs EMG amplitude so NEGATIVE is correct** — the vault's older `r@1min +0.603` uses the opposite convention; comparable magnitude, **not the same metric, do not table together**.

⭐⭐ **CIRCADIAN: the ORDERING is threshold-independent even though the VALUE is not.** ±25% Otsu sweep (Otsu 0.386): light/dark = 85.5/51.8, 72.3/29.6, **61.6/19.8**, 50.5/13.6, 32.9/7.4. **Light beats dark at EVERY threshold by 25.5-42.7 points.** 🔴 **The absolute % is STILL threshold-dependent and must NOT be quoted as fact** — the council finding stands. 🛑 **The 0.90× row lands on 72.3% = the literature ~70%; that threshold was NOT chosen because picking the one that matches the answer is circular** (banned in `02-procedures/blind-scoring-and-kappa.md`).

⭐⭐⭐ **IT REPLICATES ON ITSELF** (same whole-file Otsu applied unchanged to each cycle): cycle 1 vs 2 = usable 98/98%, **asleep-in-light 62.5% vs 61.1% (1.4 points apart)**, **median light EMG 31.0 vs 31.1 µV (0.1 µV apart)**, r −0.673 vs −0.618. ⚠️ Dark phase looser (17.6 vs 22.1) and it is **n=2 days on n=1 animal**.

**Physiology visible and all correct:** sleep pressure decays across light (76% asleep at ZT1 → 49% at ZT10), sharp lights-off transition (ZT12 45% → ZT13 14%, EMG 47→77 µV), and ⭐ a **mid-dark rest bout at ZT19-20** showing on **both channels at once** (delta up, EMG down) = a behavioural state, not a scoring artefact.

⭐ **Script `eeg-emg-analysis/qc/animal_signal_report.py`** does all of the above for one animal and saves per-epoch arrays (`..._A33_report.npz`) so nobody re-reads 182 GB.

⚠️ **THIS IS THE CONTROL, NOT THE FLEET.** The six re-pinned mice gave 57-72% usable EEG at best, **no EMG state dependence**, **no heartbeat on 7 of 7 ECG**. See [[ground-fix-worked-2026-08-08]]. 🔴 Still no **kappa** and no **positive control**; every "asleep" number is gated behind them. 🔴 Dark phase of `uid0808-16-17-36` still unscored.
