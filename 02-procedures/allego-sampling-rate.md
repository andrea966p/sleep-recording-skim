---
tags:
  - procedure
  - radiens
  - allego
  - sampling-rate
  - eeg
  - emg
  - onboarding
created: 2026-06-27
status: complete
---

# Allego Sample Rate — Why 128–256 Hz Is Not Possible (and What To Do)

> [!abstract] TL;DR — for non-technical readers
> **What this is.** How to set the acquisition **sample rate** in Allego, and a direct answer to a real request: *"can we sample EEG/EMG at 128–256 Hz to keep files small?"*
>
> **Why it exists.** The answer is **no — Allego cannot acquire below 1,000 samples/sec.** 128–256 Hz is impossible in hardware/software. The only sub-1 kHz number anywhere in Allego is a *cosmetic display* setting on the Monitor screen that does **not** change the saved file. This page prevents a wasted session built on a wrong assumption.
>
> **How to read this page.** Read the "Verified facts" box, then the "128–256 Hz" box, then the resolution (acquire at 1 kHz, decimate offline). Big picture: [[01-infrastructure/system-overview]].

> [!important] Verified facts (manual p34-36, FAQ p176)
> - Sample rate is set in the **System tab**, in the section below the **Mode** selector (manual p34-35).
> - The **default is 30,000 S/s (30 kHz)**, pre-selected "to ensure high-quality data acquisition" (manual p35).
> - Allego offers **17 sample rates ranging between 1,000 and 30,000 samples/sec** — "This range is sufficient for nearly all electrophysiological applications" (FAQ, manual **p176**).
> - **The minimum is 1,000 S/s.** There is no native 128 Hz or 256 Hz option.

---

## How to set the sample rate

1. Open the **System** tab.
2. Find the **Sample Rate** dropdown, immediately to the right of / below the **Mode** selector (manual p34-35).
3. Pick a rate from the list. The 17 documented values span **1,000 → 30,000 S/s** (FAQ p176); the dropdown lists them in ascending order ending at `30000` (manual p36).

> [!warning] Switching Mode resets the rate to its default
> Changing the **Mode** (e.g. re-selecting `XDAQ One (G1) with XR Headstage` after a revert) **resets the sample rate** — set the rate *after* you've locked in the Mode, and re-confirm it every session. Sample Rate *is* retained by Restore Workspace (manual p30), but a Mode change overrides that. See [[allego-presets-workspace]] and [[radiens-software-reference]].

## The 128–256 Hz request — not possible

> [!important] Direct answer
> **You cannot acquire/save at 128–256 Hz in Allego. The minimum acquisition rate is 1,000 S/s** (FAQ p176). Setting "128 Hz" or "256 Hz" is simply not an option in the Sample Rate dropdown.

Where the confusion comes from: the **Monitor** tab has a *"plotted sample frequency"* that can be **below** 1 kHz. That is **display decimation only** — Allego "does not plot every sample collected" and downsamples for the screen (manual p77), while the saved data keeps every sample at the configured acquisition rate. The manual states it plainly for HD Snapshot: the Monitor shows "downsampled data… used to plot the waveforms at the resolution shown," whereas HD Snapshot draws "all collected data points from recorded data" (manual p85). So a low number on the Monitor is **cosmetic**, not a recording rate. See [[allego-monitor-guide]].

> [!note] VERIFY — a `625` entry appears in the dropdown image
> The Sample Rate dropdown screenshot (manual p36) shows a **`625`** value listed *above* `1000`, which would be below the FAQ's stated 1,000 S/s minimum (manual p176). The two sources disagree by one entry. Either way, **`625` is still far above 128–256 Hz, so the conclusion is unchanged.** Treat **1,000 S/s as the practical/documented minimum** for our work. If a sub-1 kHz acquisition is ever genuinely needed, confirm on the live unit whether `625` is selectable and whether it is supported for the XDAQ/XR mode before relying on it.

## Resolution — acquire at 1 kHz, decimate offline

> [!tip] Recommended setting for sleep EEG/EMG
> **Acquire and save at 1,000 S/s** (the documented minimum, and ample for sleep-band EEG/EMG), **then decimate to 128–256 Hz offline** in analysis (Python/MATLAB) if smaller files or a specific downstream rate are required.

Why this is the right call:
- 1 kHz comfortably captures sleep EEG (delta/theta, < ~30 Hz of interest) and EMG envelope content — Nyquist at 1 kHz is 500 Hz, well above the bands that matter.
- Decimating **offline** lets you apply a proper anti-alias lowpass before downsampling, which is the correct way to reach 128–256 Hz without aliasing — cleaner than any acquisition-time shortcut.
- File-size math: at 1 kHz the recordings are already small relative to the 30 kHz default; offline decimation to 128–256 Hz shrinks them a further ~4–8×.

For the offline decimation workflow, naming, and analysis conventions, see [[eeg-emg-data-guide]].

## Reference — the dropdown values (manual p36)

The Sample Rate dropdown (manual p36 image) lists, in order:
`625` · `1000` · `1250` · `1500` · `2000` · `2500` · `3000` · `3333` · `4000` · `5000` · `6250` · `8000` · `10000` · `12500` · `15000` · `20000` · `25000` · `30000`.

Counting from `1000` to `30000` gives exactly the **17 rates** the FAQ documents (manual p176); `625` is the extra entry flagged above. (Mode dropdown list confirmed on manual p35; our mode = `XDAQ One (G1) with XR Headstage`.)

## Related
- [[allego-monitor-guide]] — the Monitor "plotted sample frequency" is display-only, not a recording rate
- [[allego-presets-workspace]] — sample rate is retained, but a Mode change resets it
- [[eeg-emg-data-guide]] — offline decimation to 128–256 Hz + analysis conventions
- [[radiens-software-reference]] — PRIMARY Radiens/Allego reference (Mode, file formats, Videre)
- [[01-infrastructure/system-overview]]
