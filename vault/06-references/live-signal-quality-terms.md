---
tags: [reference, eeg, allego, glossary, signal-quality, onboarding]
created: 2026-09-16
status: active
---

# Reading the rig live — signal quality terms

> [!abstract] TL;DR
> **What this is.** A dictionary for the numbers Allego shows you *while the rig
> is running*: the Signal Metrics tab, the Monitor bottom bar, the filter
> stages. Sister page to [[eeg-analysis-glossary]], which covers the numbers
> that appear *after* a file exists.
>
> **Why it is separate.** The live numbers and the analysis numbers look alike
> and are not the same thing. Allego's `RMS` is broadband over a lookback
> window. `eeg_rms` in the pipeline is the standard deviation of a 0.5-30 Hz
> band-passed 4 s epoch. Comparing them directly is how a channel gets called
> good when it is not.
>
> **How to read it.** Do not read top to bottom. Search it when a control or a
> column blocks you.

---

## 1. What live checking is for

**Pre-flight screen**
: Looking at signal quality *before* pressing record, while you can still do
  something about it. It answers one question — *is something grossly wrong
  that I can still fix?* — and no others. It is not a verdict, not a
  measurement for a paper, and not a substitute for the QC ladder in
  [[animal-card-verdict-ladder]].

**Why it is not a verdict**
: Contact state flips within minutes ([[movement-dependent-contact-root-cause]]),
  so a clean screen does not promise a clean 20 h recording, and a channel that
  screens badly may recover on its own. A few minutes of stream cannot rank
  channels and cannot classify a fault.

**Monitor vs Signal Metrics**
: Monitor shows **shape** — you look at waveforms, one at a time. Signal Metrics
  collapses each channel to **one number**, so 256 channels can be compared
  without eyeballing 256 traces. Different jobs, both live.

---

## 2. The Signal Metrics tab

**Port dropdown**
: Picks which port's wireframe and table are displayed. That is *all* it does.
  It does not change acquisition, does not restrict anything, is not saved into
  the recording. Cycle A → B → C → D to see everything.

**Lookback window (ms)**
: How far back in time each metric is computed over. **This is the averaging.**
: 🔴 The default of **100 ms is a spike-sorting default and is wrong for us.**
  At 1000 Hz that is 100 samples. One delta cycle is 250-2000 ms, so a 100 ms
  window never contains a whole slow wave: the number jitters violently and
  systematically under-reads delta. **Set it to 5000 ms.**

**Live Update**
: Repaints the wireframe and table every 2 seconds. Leave on, then let it run
  about a minute before writing anything down, so the value settles.

**Custom scale**
: Fixes the heat-map colour range instead of autoscaling. **Turn it on and set
  0-150 µV.** On autoscale a single 400 µV channel compresses everything else
  into one colour and a genuinely bad channel looks ordinary.

**Show Table**
: Lists every channel's value below the wireframe, sortable by column
  (three-bar button), exportable to CSV or PDF (export button).
: ⚠️ Read **only** the channels that carry an animal — `/1 /2 /33 /34` per port.
  The other 60 per port are wire-free floor. They are the control, not data,
  and grading them is the mistake recorded in
  [[partial-rig-qc-and-unjudgeable-presets]].

**Refresh (⟳)**
: Recomputes all values for the current metric. Press it after any filter
  change, before reading numbers.

---

## 3. The metric dropdown, entry by entry

The manual's list on p87 (*Absolute, Max, Min, Mean, Std Dev, Variance, S/N*) is
**stale** and does not match Allego 3.11.3. The real list is below.

### Use these

**RMS**
: Root mean square — the square root of the mean squared voltage over the
  lookback window. The everyday "how big is this signal" number, in µV.
: **RMS equals standard deviation for our data.** Measured on all 16 live
  channels 2026-09-16: every channel's mean is under 3.6 µV and SD/RMS = 1.0000
  to four decimals. The input is AC-coupled, so the mean is zero and the two
  definitions coincide. There is no Std Dev entry in the dropdown and none is
  needed.

**Abs(max-min)**
: Peak-to-peak: largest sample minus smallest, in the window. Catches large
  excursions and railing that an RMS average hides.

**Cumulative Abs(max-min)**
: The same thing accumulated over the whole stream rather than one window. The
  only long-window stable metric the tab offers — **there is no Cumulative RMS**,
  in the interface or in the API. Asking the API for `RMS` in `AVG` or `STREAM`
  mode returns `BASE` unchanged (verified 2026-09-16).

**Noise**
: Allego's own noise-floor estimate, µV. Useful as a cross-check on RMS; on our
  field-potential channels the two track each other closely, because there is no
  spike-versus-background separation for it to exploit.

### Do not use these

**Signal To Noise / Average Signal To Noise**
: Defined against **spike** activity versus background. The manual says the
  value "depends strongly on the specific spatiotemporal characteristics of
  neural activity". We record field potentials and have no spikes, so this is
  noise ÷ noise. Measured 0.7-2.1 across all 16 of our channels — a flat,
  meaningless spread.

**Number of Events · Cumulative Number of Events · Event Rate · Average Event Rate · Event Average Max / Min / Max(Abs)**
: All count **threshold crossings**, i.e. detected spikes. On our channels they
  read 85-240 events per second: that is the detector firing on slow waves.
  Meaningless here.

**Max (abs) · Cumulative Max (abs)**
: A single worst sample. One artefact ruins the number. `Abs(max-min)` answers
  the same question more robustly.

**Abs(max-min) Amplified · Cumulative Abs(max-min) Amplified**
: Undocumented scaling. Do not put a number in a run log when you cannot say
  what produced it.

---

## 4. Filter stages — the irreversible one

Allego applies filters at three stages, and only one of them is safe to
experiment with. Full detail in [[radiens-software-reference]].

| stage | where | reaches the saved file? | undoable? |
|---|---|---|---|
| **Hardware** | on the Intan chip, before the ADC | **YES** | **never** |
| **Data** (Software Stage 1) | in Allego, after acquisition | **YES** | no |
| **Visualization** (Software Stage 2) | Monitor display only | no | n/a |

**Viz Bandpass**
: The Monitor's own display filter. Visualization stage, so cosmetic. Must stay
  under the Nyquist limit — at `fs` 1000 Hz that means below 500 Hz.

**Show Monitor DSPs**
: Monitor → ☰. Temporarily disables Visualization-stage filters without deleting
  them. **This is the correct way to A/B a filter**: the difference appears and
  disappears within the same second, on the same animal state. Comparing two
  measurements taken minutes apart cannot separate a filter's effect from the
  animal simply moving.

**Notch**
: Attenuates one frequency, 50-60 Hz allowed, default bandwidth 2 (so 60 Hz
  notches 59-61 Hz).
: 🛑 **NEVER ADD ONE, AT ANY STAGE.** Our connection test *measures* 60 Hz
  amplitude — hum is the readout of contact quality, not a nuisance — and a
  per-chip collapse in 60 Hz is how a floating ground is detected at all. A
  notch erases that evidence permanently and silently. Same for any bandstop
  covering mains. See [[radiens-software-reference]] and
  [[weak-chip-ground-hides-as-electrode-failure]].

**Restore Workspace, what it does not keep**
: Selected/deselected sites and site reordering are **not** retained, while
  system mode, sample rate, gain, highpass, headstage, probe and filters are.
  This is why the montage has to be re-selected after a mode change.

---

## 5. Reading the numbers

**Mains amplitude / 60 Hz (`eeg_mains`, `emg_mains`)**
: Amplitude in the 55-65 Hz band, measured as the standard deviation of the
  mains-band-passed signal. Physically `differential_60Hz ≈ common_mode ×
  electrode_Z_imbalance`, so it is a direct readout of contact quality.
  `OPEN_UV` = 150 µV is the open-circuit cut; connected channels sit far lower.

**cv% (coefficient of variation)**
: Standard deviation of a metric across repeated readings, as a percentage of
  its mean. How much the channel *moved* over the sampling period.
: ⚠️ **Only interpretable on EEG.** Real EMG is bursty — an awake mouse produces
  60-200% variability because muscle genuinely does that. High cv on EMG is
  physiology, not a fault.
: ⭐ **The reverse is the useful signal.** A channel that is *large and steady*
  is an artefact: 2026-09-16, A/2 read 465 µV with cv 3%, five times any other
  EMG channel and the steadiest thing on the rig. Muscle does not do that. A
  constant large amplitude is hum or a loose ground.

**Chip ground floor**
: The 55-65 Hz amplitude of a chip's **wire-free** inputs — the amplifier channels
  with no electrode attached. They sit in mains hum, and how much they pick up is
  set by the ground/reference return, so the floor reads the **ground screw's
  contact**, not any electrode's.
: An RHD2216 presents **16 real inputs per chip**; the animal uses the first two and
  the other 14 are the control. ⚠️ The remaining 16 slots of each 32-slot block have
  no amplifier behind them and read 3-8 µV — counting those as floor sites drags a
  grounded chip down ~20× and calls everything ungrounded.
: `FLOOR_MIN_HUM_UV` is **800**; **2000 has been proposed and NOT applied**. Under
  2000, nothing measured on that chip means anything, so the animal is
  **UNJUDGEABLE, never FAIL**.

**Flat / dead (`FLAT_UV`, `DEAD_CHANNEL_UV`)**
: Below about 20 µV median, a channel never carried EEG — open or shorted. Dead
  is a property of the **channel** (tested on its median across the recording);
  flat is a property of one **epoch** (a momentary dropout).

**Rail (`RAIL_UV_EFF` = 6377 µV)**
: The amplifier ran out of range. `0.195 µV/LSB × 32767 counts × 0.998`. Note
  that ordinary EMG excursions of 1500-2900 µV peak-to-peak are **nowhere near**
  the rail — do not call them railing.

---

## 6. The two live tools

They answer different questions and are meant to be run in that order.

### `qc/preflight_screen.py` — is it connected?

Runs the stage 1 QC measurement against a few minutes of live stream and prints a
per-animal verdict. Every threshold is imported from `core/qc_thresholds.py`;
nothing is redefined locally, so it can never pass a channel the real gate would
later reject.

```bash
cd ~/sleep-recording-skim/eeg-emg-analysis && /usr/bin/python3 -m qc.preflight_screen --secs 300
```

🛑 **Under the normal 16-channel montage it CANNOT check grounding, and says so.**
The per-chip floor lives on the 14 wire-free inputs of each chip. `get_signals()`
returns only SELECTED channels, `get_metrics()` computes only those too (verified:
exactly 16 of 256 non-zero), and radiens 4.0.0 has **no setter for the selection**.
So the screen reports `NO FLOOR` instead of `CLEAN`.

This matters because a floating chip looks perfect on its animal channels. On
2026-09-17 an earlier version of this tool passed **A2, C1 and D1 as CLEAN while
their floors were 454, 7 and 5 µV** — all three were ungrounded and unjudgeable.

To get the grounding check: select **all** channels in Allego (System → Signals),
run the screen, then re-select the montage. **Never during a recording.** Otherwise
rely on stage 1 after the file exists.

### `qc/biology_probe.py` — is it neural?

A connected electrode sitting in saline passes the screen above. This one asks
whether the signal has the *shape* of neural tissue, using the spectral-slope
measurement from `core/criteria.py`: real EEG is steep 1/f (working animals
**-1.5 to -2.1**), a wire-free input is flat (**-1.29 to -0.07**). It also reports
the band-limit guard, delta fraction, and the EEG↔EMG correlation that catches a
shared-path fault.

```bash
cd ~/sleep-recording-skim/eeg-emg-analysis && /usr/bin/python3 -m qc.biology_probe --secs 300
```

🛑 **Slope tracks vigilance state as well as electrode quality.** The reference
range comes from full recordings dominated by sleep; awake EEG is legitimately
flatter because there is less delta in it. A flat reading in the dark phase means
*inconclusive, look again in the light phase* — not *bad electrode*. The tool
prints the circadian time and warns for exactly this reason.

Both are split across two interpreters on purpose: `radiens` lives only in
`/opt/neurosurveillance/venv`, whose scipy is broken, so `preflight_grab.py`
captures under the venv and the measuring half runs under `/usr/bin/python3`.
Pass `--keep` to retain the capture, then `--npz FILE` to run the other tool on
the same data rather than capturing twice.

Verdict names are stage 1's: `CLEAN`, `DIRTY`, `OPEN`, `DEAD`, `CLIPPED`.
`INSUFFICIENT` is not a negative result — it means the test could not be run.

⚠️ **Neither tool can tell you whether an animal is scorable.** That needs an
unbroken usable block of at least 15 minutes (`MIN_BLOCK_MINUTES`) and the state
variation that only a multi-hour recording contains. Passing both tools means the
rig is worth pressing record on, nothing more.

---

## Related

- [[eeg-analysis-glossary]] — the same job for the offline analysis
- [[radiens-software-reference]] — the Allego interface itself, page by page
- [[animal-card-verdict-ladder]] — where a real verdict comes from
- `02-procedures/CANONICAL-allego-channel-selection.md` — the montage
- [[allego-blank-monitor-canvas-texture-limit]] — when the Monitor draws nothing
