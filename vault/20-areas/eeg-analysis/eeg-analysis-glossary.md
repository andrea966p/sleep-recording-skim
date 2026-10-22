---
type: reference
area: eeg-analysis
status: active
tags: [reference, eeg, analysis, glossary, onboarding]
created: 2026-08-03
---

# EEG analysis glossary — every term and parameter, in plain words

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A dictionary. Every piece of jargon, every parameter name
> and every abbreviation that appears in the analysis code, the QC tables and
> the reports, explained once in ordinary language, with the value we use and
> why.
>
> **Why it exists.** The pipeline prints things like `nperseg`, `r@1min`,
> `DIRTY`, `ZT`, `Otsu`, `rms`. None of those are guessable. Not knowing what
> one means is how a wrong number gets believed.
>
> **How to read this page.** Do not read it top to bottom. Search it when a
> word blocks you. Entries are grouped by where you meet them: the recording,
> the maths, the quality gate, the sleep scoring, the files.
>
> Big picture: [[nvr-system-overview]].
> The procedure itself: [[_eeg-analysis-hub]].

---

## 1. Words about the recording itself

**Sample / sampling rate (`fs`, `FS_RAW`)**
: How many times per second the amplifier measures the voltage. Ours is
  **1000 hertz** during acquisition, meaning one measurement every millisecond.
  After filtering we **decimate** to 250 hertz for storage, because nothing in
  sleep EEG lives above 30 hertz and keeping 1000 would waste four times the
  space.

**Nyquist frequency**
: Half the sampling rate. The hard ceiling on what a recording can possibly
  see. At 1000 hertz the ceiling is 500 hertz; at 250 hertz it is 125 hertz.
  You cannot filter, plot or claim anything above it. Asking for a filter above
  the Nyquist is what produces the Allego error in
  [[allego-iir-filter-design-errors]].

**`Wn` (normalised frequency)**
: How filter software actually takes a frequency: as a fraction of the Nyquist,
  not in hertz. A legal filter needs `0 < Wn < 1`. `Wn = cutoff_hz / (fs / 2)`.
  A 30 hertz cutoff at 1000 hertz gives `Wn = 0.06`, fine. A 6000 hertz cutoff
  at 1000 hertz gives `Wn = 12`, impossible.

**LSB (`LSB_UV`)**
: Least significant bit. The smallest voltage step the analogue to digital
  converter can represent, **0.195 microvolts** for the Intan RHD2216. Every
  stored value is a whole number of LSBs. Nothing finer than this exists in the
  data, no matter what a plot suggests.

**Rail / railed / clipped (`RAIL_UV` = 6389.6 µV)**
: The amplifier ran out of range and the trace flattened against its ceiling.
  `0.195 µV/LSB × 32767 counts = 6389.6 µV`. A railed epoch has undefined band
  power, so we throw the whole epoch away rather than measure nonsense. This is
  not a judgement call: a clipped sine wave has energy at frequencies that were
  never in the signal.

**Bipolar**
: Two electrodes, one amplifier, and the amplifier reports the **difference**
  between them. Our chip is bipolar, so what lands in the file is already a
  difference. This is the single most dangerous term on this page, see the
  warning in section 6.

**Wideband / raw**
: Unfiltered, as acquired. Our saved `.xdat` file is wideband. Everything we do
  to the picture in Allego is display only and never reaches it.

**Mains / line noise (`FILT_MAINS` = 55 to 65 Hz)**
: The 60 hertz hum radiated by building wiring (Korea is 60 hertz; Europe is
  50). We do not merely tolerate it, we **use** it: hum amplitude is a direct
  readout of electrode contact. Connected electrodes sit at 9 to 90 microvolts,
  open ones at 1000 to 4700. That hundredfold gap is the most reliable number
  in this project.

---

## 2. Words about the maths

**rms (root mean square)**
: One number summarising how big a wiggly signal is. Square every sample,
  average, take the square root. It is the honest version of "amplitude" for a
  signal that swings both ways, because a plain average of an EEG trace is
  about zero regardless of how large it is.

**Epoch (`EPOCH_S` = 4 s)**
: The chunk of time everything is measured over. All scoring, all band powers,
  all QC decisions are per epoch. Four seconds is the short end of the accepted
  rodent range, chosen because mouse sleep bouts are frequently under 30
  seconds and longer epochs smear the transitions. Epoch `i` covers samples
  `i × 1000` to `(i+1) × 1000` at 250 hertz.

**Power spectral density (PSD) / spectrum**
: How much of the signal's energy sits at each frequency. The tool that turns
  "a wiggly line" into "mostly slow waves" or "mostly fast waves".

**Welch's method**
: The standard way to compute a PSD: cut the epoch into overlapping windows,
  compute a spectrum for each, average them. Averaging trades frequency detail
  for a less noisy estimate. `scipy.signal.welch` is what the pipeline calls.

**`nperseg`** ⭐
: **The single parameter people ask about most.** It is the length, **in
  samples**, of each window Welch cuts the data into. It sets your frequency
  resolution:
  ```
  df = fs / nperseg
  ```
  Ours is **`nperseg = 2048`**, so `df = 1000 / 2048 = 0.49 hertz`. That means
  the spectrum has one value roughly every half hertz.
  > [!danger] Do not lower `nperseg`
  > At `nperseg = 512` the resolution becomes `df = 1.95 Hz`, and the theta band
  > (6 to 9 hertz) then spans a **single** frequency bin. Integrating over one
  > point returns **exactly zero**, with no error raised. Every REM measurement
  > silently becomes 0. A parameter that quietly zeroes a result is worse than
  > one that crashes.
  >
  > Bigger is not free either: `nperseg` cannot exceed the number of samples in
  > an epoch, and larger windows mean fewer of them to average, so the estimate
  > gets noisier.

**Bin**
: One entry in the spectrum, `df` hertz wide. "The 60 hertz bin" means the
  value covering roughly 59.75 to 60.25 hertz.

**Band / band power**
: The total energy in a frequency range. Ours: **delta 0.5 to 4 hertz** (slow
  waves, the signature of non REM sleep), **theta 6 to 9 hertz** (the signature
  of REM and of active wake), **total 0.5 to 30 hertz**.

**theta/delta ratio**
: Theta power divided by delta power. The conventional rodent discriminator:
  high ratio with low muscle tone means REM, low ratio with low muscle tone
  means non REM.

**Band-pass filter (`FILT_EEG` 0.5 to 30 Hz, `FILT_EMG` 10 to 300 Hz)**
: Keeps frequencies between two limits and removes the rest. Ours are 4th order
  Butterworth, applied **zero phase** (forwards then backwards), so no feature
  gets shifted in time. Filtering is irreversible, which is why we record
  wideband and filter offline.

**Notch filter**
: A narrow band-pass in reverse: removes one frequency, ours would be 60 hertz.
  In Allego it is display only. Proven on 2026-07-31 by parking it at 50 hertz
  and finding the saved spectrum perfectly flat there.

**Decimate / downsample**
: Reduce the sample rate, after low-pass filtering so nothing above the new
  Nyquist folds back and masquerades as a low frequency (that folding is called
  **aliasing**). We go 1000 to 250 hertz.

**Otsu's method**
: An automatic way to split one cluster of numbers into two, by picking the cut
  that makes the two groups internally tightest. We use it on the logarithm of
  EMG rms to separate "muscle active" from "muscle quiet", i.e. wake from
  sleep.
  > [!warning] Otsu is computed **per animal**, never shared
  > Muscle tone amplitude depends on where the wires ended up in that
  > individual's neck. Reusing one animal's threshold on another is what wrongly
  > passed D2 on 2026-08-01.

**Autocorrelation**
: How much a signal resembles a time-shifted copy of itself. We use it to ask
  whether sleep and wake come in **runs** rather than flickering randomly.

**`r@1min`** ⭐
: Our **persistence statistic**. The autocorrelation of the state sequence at a
  one minute lag. Real sleep is consolidated, noise is not, so a high value says
  the states are physiologically plausible.
  - Threshold: `r > 0.30` = SCOREABLE. Calibrated against synthetic bouts
    through the identical code path: noise −0.035, 30 s bouts +0.112,
    2 min +0.214, 4 min +0.510, 10 min +0.703. So `r > 0.30` means consolidated
    bouts of roughly **3 minutes or longer**.
  - **This is our own addition, not a standard criterion.** It is a validity
    check, not a scoring method: it never assigns any epoch to a stage. Describe
    it that way in any methods section.
  > [!danger] It must be computed WITHIN unbroken blocks
  > See **block** below. Computing it across contact gaps produced both the
  > project's largest false positive and a false negative.

---

## 3. Words about the quality gate

**QC**
: Quality control. Stage 1 of the pipeline. It answers one question per animal:
  *can this recording be scored at all?*

**Gate / gated**
: The per-epoch pass or fail test. An epoch must pass **all** of OPEN, FLAT,
  CLIPPED and FINITE to count. `epoch_ok` in the output files is the result.

**`OPEN_UV` = 150 µV**
: Above this much 55 to 65 hertz hum, the electrode is **not electrically
  connected**. Measured, not chosen: the pooled hum distribution is cleanly
  bimodal in log space, connected mode at 84 µV, open mode at 3731 µV, valley
  between them at 134 µV.

**`FLAT_UV` = 11 µV**
: Below this EEG rms for one epoch, the signal momentarily dropped out.
  Measured at the local minimum separating the amplifier noise floor from real
  signal.

**`DEAD_CHANNEL_UV` = 20 µV**
: Applied to the **channel median over the whole recording**, not to an epoch.
  A channel below it never carried EEG at all, and no epoch level test can
  rescue it. Splitting the old single 25 µV rule into this plus `FLAT_UV` is
  what removed the pipeline's only threshold sensitivity.

**Block** ⭐
: An **unbroken run of consecutive passing epochs**, at least 124 seconds long.
  The `blocks` array gives start and end epoch index of each one.
  > [!danger] The most important concept on this page
  > Contact is intermittent, so once failing epochs are dropped, epoch `k` and
  > epoch `k+15` can sit next to each other in the array while being **hours
  > apart in real time**. Anything involving a time lag — autocorrelation, bout
  > length, transition probability — must be computed *inside* one block and then
  > averaged across blocks. Ignoring this produced `r = +0.854` on a stretch
  > that is 39 minutes of pure wake.

**Verdict**
: Stage 1's per-animal answer. Six possible values:

| verdict | meaning | usable? |
| --- | --- | --- |
| `CLEAN` | ≥90% of epochs pass, ≥90% of usable time in long blocks | yes |
| `DIRTY` | usable data exists but fragmented or partly contaminated | **yes** |
| `OPEN` | electrode not connected for >95% of the recording | no |
| `DEAD` | channel median below the floor; never carried EEG | no |
| `CLIPPED` | amplifier railed in >95% of epochs | no |
| `INSUFFICIENT` | under 15 minutes inside blocks ≥124 s | no |

  > [!warning] `DIRTY` does not mean bad, and `INSUFFICIENT` is not a result
  > C1 on 2026-07-31 is the best animal in the project and it is `DIRTY`,
  > because the surrounding 19 hours are open. And `INSUFFICIENT` means the
  > question could not be asked, not "this mouse did not sleep". Writing it up
  > as a negative result is a category error.

**Impedance (`Z`, megaohms)**
: How much the electrode resists a small test current. Low means good contact.
  Published epidural screws sit at 10 to 50 kΩ; our best is 73 kΩ, our thresholds
  are `IMP_GOOD_MOHM = 0.10` (contact confirmed) and `IMP_CONNECTED_MOHM = 2.0`
  (our own open/closed separator, since a no-wire control measured 5.233 MΩ).
  > [!warning] Only half of each pair has ever been measured
  > The chip can test either pin of a bipolar pair, but Radiens exposes no
  > polarity control, so every number we hold is the positive input only. See
  > [[impedance-sweep-register]].

---

## 4. Words about the sleep scoring

**Hypnogram**
: The list of sleep stages over time, one row per epoch. Our
  `*_hypnogram.csv`.

**WAKE / NREM / REM**
: The three states. **WAKE** = high muscle tone. **NREM** (non rapid eye
  movement) = low muscle tone, low theta over delta, big slow waves. **REM** =
  low muscle tone, high theta over delta.

**Bout**
: One continuous run of the same state. We never report bouts shorter than two
  epochs.

**`rem_pct_CONSTRUCTED`** ⭐
: Named that way as a warning.
  > [!danger] Never quote a REM percentage
  > REM is defined here as the top 20% of theta over delta among non wake
  > epochs, so its share is **fixed by the rule rather than measured**. Both our
  > percentile rule and an Otsu cut land far above the literature value of under
  > 10% of sleep, so neither is a measurement. What *is* evidence is REM's
  > **order** — that it is entered from non REM rather than from wake.

**SCOREABLE**
: Stage 3's verdict. All four must hold: ≥15 min inside blocks ≥124 s;
  within-block `r@1min` > 0.30; physiology passes (wake has the highest EMG,
  NREM the most delta, REM the highest theta over delta with low EMG); wake
  fraction between 15% and 90%.

**ZT (zeitgeber time)**
: Hours since lights on. **ZT0 = 09:00 KST** here, lights on 09:00, off 21:00,
  a 12:12 cycle. ZT is the right x-axis for sleep, because a mouse's behaviour
  tracks the light cycle rather than the clock. Nocturnal, so mice sleep mostly
  during the **light** phase.

**Light phase / dark phase**
: `is_light` in the output files. 09:00 to 21:00 KST is light. Our strongest
  external check is that C1 was 66.9% asleep in the light phase against a
  literature value near 70%.

---

## 5. Words about the files

**`.xdat`**
: What Allego writes. Three files sharing one base name: `<base>_data.xdat`
  (float32 microvolts, sample major), `<base>_timestamp.xdat`, and
  `<base>.xdat.json` (metadata). **The master. Never edit it.** Everything is
  re-derivable from it.

**`.npz`**
: A zip of numpy arrays, one per mouse, what stage 2 writes. **Do not unzip
  it** — numpy opens it directly and hands back named arrays. Contains `eeg`,
  `emg`, `fs`, `epoch_ok`, `blocks`, `zt`, `is_light`, `meta`.

**`.npy`**
: A single numpy array on disk. The things inside an `.npz`.

**memmap**
: Reading a huge file by mapping it into memory rather than loading it. How the
  pipeline reads a 105 GB recording without 105 GB of RAM.

**EDF / EDF+C**
: European Data Format, the portable standard every sleep scoring program
  opens. The `C` means continuous. Stage 4 writes one per mouse, with EEG and
  EMG, deliberately **without** our automatic labels so a human scores blind.

**`meta`**
: The JSON string travelling inside every `.npz`: port, slot, animal name, QC
  verdict and its reason, thresholds used, provenance. It exists so a number can
  never travel without its caveats.

**Port / slot**
: Physical position. Port is the XDAQ port (A to D). Slot is the position on the
  splitter: slot 1 = native offset 0 (`/1`, `/2`), slot 2 = offset 32 (`/33`,
  `/34`). One mouse per slot.
  > [!warning] Animal names are positional
  > `D2` in one recording is not necessarily the same mouse as `D2` in another.
  > Fixing that needs cage records.

---

## 6. The four things that are easy to get wrong

> [!danger] 1. The signals are ALREADY bipolar
> The RHD2216 subtracts each electrode pair inside the chip, before the
> converter. `/1` is EEG (frontal minus parietal) and `/2` is EMG (left minus
> right neck), each already a difference. **Never subtract EMG from EEG, and
> never re-reference.** The old `EEG = n0 − n1` computed EEG-minus-EMG, and it
> is the reason 24 working EMG implants were once recorded as failed surgeries.
> Canonical page: [[CANONICAL-allego-channel-selection]].

> [!danger] 2. Analyse inside blocks, never across them
> See **block** above. This is not a theoretical worry, it produced both the
> largest false positive and a false negative in this project.

> [!danger] 3. Never report a REM share
> See `rem_pct_CONSTRUCTED` above.

> [!danger] 4. `OPEN` and `INSUFFICIENT` are not negative results
> They mean the question could not be asked.

> [!quote] Paper-ready
> Spectral estimates use Welch's method with a 2048 sample segment, giving a
> frequency resolution of 0.49 hertz, computed on 4 second epochs of signal
> band-passed 0.5 to 30 hertz (electroencephalogram) and 10 to 300 hertz
> (electromyogram) with a zero-phase fourth-order Butterworth filter.

## Related
- [[live-signal-quality-terms]] — the same job for the numbers Allego shows LIVE
- [[_eeg-analysis-hub]] — the ordered procedure these terms appear in
- [[analysis-methods-and-justification]] — what is standard and what is ours, with citations
- [[eeg-analysis-problems]] — what to do when a step misbehaves
- `eeg-emg-analysis/core/qc_thresholds.py` — every constant with its provenance
- [[CANONICAL-allego-channel-selection]] — which channel is which


---

## Terms added 2026-08-06 to 2026-08-08

**duty cycle** — the fraction of repeated impedance sweeps in which a channel came back below the
connected threshold. Used instead of a single reading because contact flips within minutes.
⚠️ A block of sweeps spans only ~20 min, and contact states persist longer than that, so **a duty
cycle screens; only a multi-hour recording is an outcome**. Always state the block's duration.

**floor control / wire-free channels** — amplifier inputs with **no electrode attached**, recorded
at the same instant in the same file. A mouse uses only a few of its chip's 16 inputs, so the rest
are free nulls. Every threshold is now derived from these rather than inherited.
❌ Never include the **inactive slots** (`/17`-`/32`, `/49`-`/64`); they are internally tied and read
low almost always.

**spectral slope** — the gradient of log power against log frequency over 1-30 Hz. Real neural
activity falls steeply (about −1.8 to −2.1 here); noise is flat (−1.3 to 0.0). **The discriminator
that survives filtering**, unlike amplitude or trace appearance.
🛑 It judges **EEG only**. Real EMG is broadband, so a flat EMG spectrum is expected.

**railing / clipping** — samples at the ADC ceiling, 6389.6 µV. **Missing data, not noisy data**:
clipping is nonlinear and irreversible. On this rig it is the **open-electrode signature**, not
movement artefact — the no-mouse position railed 100% of the time.

**minimum bout** — a run of a state shorter than 3 epochs (12 s) is not counted as that state and is
merged into the longer neighbour. **Lab convention, not from the IIIS reference**, which has no
minimum-bout rule at all.

**raw versus smoothed labels** — validity statistics (`r@1min`, REM order) are computed **before**
the minimum-bout merge; architecture and bouts **after**. Smoothing raises autocorrelation by
construction, so computing persistence after it inflates the number with no new information.

**staging delta versus reporting delta** — two different bands on purpose. **Staging 0.5-4.5 Hz**
(the Japanese tool's low-pass, used for the theta/delta ratio) and **reporting 1-4 Hz** (the paper's
band, used for quoted spectra).

**transition epoch** — an epoch whose preceding or following epoch is a different state. Excluded
from **spectra only**, never from staging or state totals. IIIS practice.

**forced check** — a physiology check that cannot fail because it restates the staging rule.
**4 of our 5 are forced.** Only `nrem_largest_amplitude` is informative.

**run-order shuffle null** — permutes the order of state runs within a block while preserving run
lengths and composition. Tests whether a sequential property is real or forced by composition.
The REM-from-NREM order passes it at ~10 SD.

**Cohen's kappa** — agreement between two scorers corrected for chance. The measurement that turns
"the pipeline runs" into "the pipeline is accurate". ⚠️ **Prevalence-sensitive**, so a stratified
scoring pack gives a stratified kappa, not the whole-recording value.

**pseudoreplication** — treating correlated measurements as independent. Our 112 wire-free nulls
share a board, reference and ground, so their **effective n is closer to the number of sessions**
than to 112. Unresolved.

**emg_activity** — `var(raw) / sum(|high-pass filtered|)`, a burst-versus-tonic shape measure used
by the Japanese tool. We do not compute it. Possibly useful for separating real EMG bursts from
movement artefact.
