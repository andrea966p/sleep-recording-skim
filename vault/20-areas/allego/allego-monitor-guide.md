---
type: procedure
area: allego
status: active
status-note: "complete"
tags:
  - procedure
  - radiens
  - allego
  - monitor
  - signal-quality
  - onboarding
created: 2026-06-27
---

# Allego Monitor Tab — Reading the Live Signal

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A walkthrough of the **Monitor** tab in NeuroNexus Allego — the screen that draws the live EEG/EMG waveforms (and an optional heatmap) while the rig is streaming. It explains the controls you actually touch: how tall the traces are, how many microvolts fit on screen, how to measure a bump, and the three "View Modes."
>
> **Why it exists.** Operators need to glance at the Monitor and tell *good signal* from *railed/floating junk* before committing to a recording. This page covers the **knobs**; the *interpretation* cheat-sheet (what clean vs. railed vs. floating looks like) lives in [[signal-quality-and-grounding]] — don't duplicate it, link it.
>
> **How to read this page.** Skim the "What Monitor shows" section, then the View Modes warning (the one that surprises people), then keep the controls table handy at the rig. Big picture: [[nvr-system-overview]].

> [!important] The single most important fact on this page
> **The Monitor plot is downsampled for DISPLAY ONLY. The recorded/saved data is not affected.** The manual is explicit: "While the real-time signals are displayed in the Monitor tab, it is downsampled data that gets used to plot the waveforms at the resolution shown" (manual p85). What you see on screen is a decimated preview; the file on disk keeps every sample at the configured sample rate. See [[allego-sampling-rate]].

---

## What the Monitor tab shows

The Monitor tab "is used to view electrical signals for connected probes, in addition to any peripheral device activity on the recording system's digital and analog inputs" (manual p73). Most of the window is the trace area; controls sit in a **Top Bar** and a **Bottom Bar** (manual p73, p76).

- **Voltage traces** — the default view. Each trace is labelled on the left with its **port letter + probe site number** (e.g. `A/5`); to relate site numbers to amplifier channels, see the read-only **Signal Map** in the System tab (manual p75). For our rig the `D/n` labelling and the site/amplifier mapping are covered in [[radiens-software-reference]] and [[signal-mapping-guide]].
- **Heatmap** — an alternative `Plot type (X-Y) Plot` setting that "replaces the voltage traces with a heatmap display which may make it easier to identify more active channels. This uses a 150 µV amplitude as a default maximum value" (manual p76). Useful for spotting one hot/dead channel across many; less useful for reading EEG/EMG morphology.

> [!note] Peripheral / GPIO channels
> Digital and analog I/O (e.g. our `DI`/`DO` sync lines) appear below the neural channels by default. The **Send GPIO channels to top** toggle pins them above the neural traces so they stay in view (manual p74). Relevant when validating the hardware video-sync path.

## Preset views — pick `Fields` for EEG/EMG

The Bottom Bar has two preset buttons (manual p77):

- **`Units`** — configures Monitor for single- and multi-unit (spike) recordings.
- **`Fields`** — "intended for use with LFP, ECoG, and EEG streaming."

> [!tip] Our montage is EEG + EMG, not spikes
> Start from the **`Fields`** preset (manual p77). Spike-oriented features — `Show Thresholds`, `Configure Spike Threshold`, the `Spike Plot` pop-out, `Disable Volume` audio — are "only relevant when online spike sorting is turned on" (manual p74, p79) and can be ignored for sleep EEG/EMG.

## View Modes — Raw / Spikes / Anti-Alias

The View Modes button (default label shows the active mode, e.g. `Spikes`) sets **how the on-screen trace is decimated**. The manual is blunt: "The Monitor does not plot every sample collected. There are three view mode options that impact how signals are shown" (manual p77):

| View Mode | What it does (manual p77) | When to use |
|---|---|---|
| **Raw** | "Signal is down sampled through simple decimation. For example, if the system is set to a sample frequency of 30 kS/s and the Monitor is set to a 5 s window which has a 1 kS/s plotted sample frequency, every 30th sample is plotted while the rest are not displayed." | Fastest, but can *miss* short high-amplitude events between plotted samples. |
| **Spikes** | "Signal is down sampled in a way that preserves high amplitude events that may be lost by decimation in Raw mode." | Default-ish; good for catching transient artifact/saturation. |
| **Anti-Alias** | "Applies a lowpass filter with the upper bound defined as the Nyquist frequency (plot sample freq/2) prior to downsampling for Monitor. The signal is then resampled at the current plot sample frequency." | Cleanest cosmetic display; avoids aliasing artifacts in the *preview*. |

> [!warning] None of the three changes your saved data
> All three View Modes operate on the **display only**. The "plotted sample frequency" (shown in the `Frequency scale` readout, e.g. `fs=20(1)` = acquisition fs vs. plotted fs, manual p77) is a function of the `Window (s)` setting and the screen width — it is **not** your recording sample rate. To see the *true* recorded waveform with all samples, use the **HD Snapshot** module (see below), not the Monitor.

## Key controls (Bottom Bar)

| Control | Label | What it does (manual p78) |
|---|---|---|
| **Amplitude Range (µV)** | `AMP Range (µV)` | "The voltage span covered by the channel… (e.g., ±100 µV)… the minimum and maximum voltage values displayed on the y-axis." This is your vertical zoom. If a trace looks flat, *shrink* the range; if it's clipping, *grow* it. |
| **Channel Height** | `Chan height (px)` | Vertical size of each trace in pixels — fit more channels on screen vs. see one in detail. |
| **Window Duration** | `Window (s)` | Seconds of signal shown across the screen. Also drives the plotted sample frequency (and thus decimation density) — see View Modes. |
| **Signal Clipping** | `Clip` | If the signal exceeds the amplitude range, portions of the waveform are "cut off or truncated" on screen. A *clipped display* ≠ clipped data, but it hides true amplitude — widen `AMP Range` to confirm. |
| **Analog IN Range (mV)** | `AIN range (V)` | Min/max for analog-in channels; leave at default unless reading an external analog sensor. |

> [!tip] Measure tool — approximate µV by drag
> The **`Measure`** button gives "a method to quickly approximate the amplitude of a given signal in Monitor. After clicking Measure, click and drag over a signal of interest and an approximate value in µV will be shown in the adjacent box" (manual p78). Use it for a fast "is this 50 µV or 5 mV?" sanity check — it is approximate, not a measurement of record.

## Site selection and trace detail

- **Which channels are drawn:** "In the signals area of the System tab, some or all channels can be selected or deselected. All voltage traces will be enabled and displayed by default… Also, in the Electrodes tab, the Select tool can be used to achieve the same result" (manual p76). (Reminder: channel *selection* is **not** retained between sessions — see [[allego-presets-workspace]].)
- **Detailed single-channel view:** "Individual voltage traces can be opened up for a more detailed view by double clicking on them. Thresholds and scales for that specific channel can be changed here as well" (manual p76). A `Scope` pop-out opens with its own `Sec/Window` and `Range (± µV)` controls (manual p81).
- **Grid / cursor helpers:** `Grid On/Off` splits the display into 10 vertical sections; `Disable Cursor` shows/hides the green vertical "current plot position" line (manual p74).

## Related modules for closer inspection

- **HD Snapshot** (manual p85) — draws waveforms using **all collected data points** from recorded data (and recently-streamed data), with a `Start Time` + `Duration` (max 15 s available window), `Condensed`/`Show Grid` toggles, hover-for-exact-value, and zoom/pan tools. This is the place to verify true signal detail because the Monitor is decimated.
- **Signal Metrics** (manual p87-88) — a probe-wireframe **heatmap** of per-site metrics (`Abs(max-min)`, Max, Min, Mean, Std Dev, variance, signal-to-noise ratio), with `Live Update` (every 2 s), `Show Table`, CSV/PDF export. Good for an at-a-glance "which sites are quiet vs. saturated" before recording.

> [!note] Reading the signal — go to the interpretation guide
> This page is the *controls* reference. For **what clean vs. railed vs. floating EEG/EMG actually looks like**, the grounding-first decision order, and the bipolar **Paired Reference** setup (RHD2216 → no `ref_elec`, Common Average Reference OFF), use [[signal-quality-and-grounding]]. Reference Types are set in the Signal Processing tab (manual p70), not in Monitor.

## Practical notes from the rig (2026-10-14, first unipolar mice)

- **Visualization (Software Stage 2) filters are set per PORT, so they hit every trace on it.** A 10-300 Hz band-pass
  added for EMG also strips delta (0.5-4 Hz) and theta (6-9 Hz) from the EEG and LFP traces ON SCREEN. Turn it on only
  to look at EMG bursts. The saved file is untouched (checked from the data spectrum of `allego_0__uid1014-21-08-06`).
  🔴 The radiens API's `get_signals()` live feed carries these filters too: analyse the recorded file, not a live grab,
  whenever a display filter is on.
- **`fs=1(0.5)` in the bottom bar** = recorded 1 kHz, plotted 0.5 kHz (every 2nd sample). The plotted rate falls as the
  Window grows. At a 10 s window this is invisible (more points than pixels) and the screen is honest up to half the
  plotted rate (250 Hz). Shorten the Window until it reads `fs=1(1)` to see every sample.
- **HD Snapshot, as it behaves here:** the Duration choices follow the Monitor's Window (a 1 s window offers at most
  1-2 s; set Window 10 s for up to ~10 s). **Start Time is STREAM seconds**, not clock time, and must lie inside the green
  **Avail. Window** (e.g. `342.63, 351.74`): a value outside it turns the box red and draws stale flat lines. The draw
  button is **Refresh**. The window moves with the stream, so press Refresh, type the first number + 0.5, Refresh again.
- **Measure** gives the vertical span of a drag in µV, in effect a peak-to-peak, on the DISPLAYED (filtered,
  decimated) trace. Clear display filters before measuring EMG; peak-to-peak is ~3-6x the rms numbers in analysis.
- **Frequency:** Allego has no spectrum tool (the manual has none). Count cycles over a known time: f = cycles ÷ seconds,
  over several cycles, on a broad display band. A narrow band-pass makes noise look rhythmic at its centre frequency.
  For a number to report, compute a spectrum offline from the recorded file.
- **Unipolar mice:** every channel is measured against one reference, so neighbouring electrodes correlate in the slow
  band (EMG L/R, LFP target/reference). That is expected, not mirroring; mirroring is r ≈ 1.00 in every band with a
  near-zero difference. The SAME big event on all six channels of one mouse points at the reference path.

## Related
- [[signal-quality-and-grounding]] — ⭐ what good/bad signal looks like + grounding + referencing (the interpretation half of this page)
- [[allego-sampling-rate]] — why the on-screen "plotted sample frequency" is not your recording rate
- [[allego-presets-workspace]] — channel selection is NOT saved between sessions
- [[radiens-software-reference]] — PRIMARY Radiens/Allego reference (Signal Map, modes, channel labelling)
- [[signal-mapping-guide]] — real-world ↔ Allego site/channel mapping
- [[nvr-system-overview]]
