---
tags: [troubleshooting, symptom, allego, radiens, deferred]
created: 2026-08-03
severity: cosmetic
status: DEFERRED, does NOT affect recording, display band CONFIRMED to apply 2026-08-03
---

# Allego throws IIR filter design errors when I change the Monitor band filter

> [!abstract] TL;DR
> When I change the visualization band filter in Allego's Monitor tab, the
> Radiens logs fill up with red filter design errors. **The recording is NOT
> affected.** The `.xdat` file is raw wideband, the errors come from a spike
> sorting stage we do not use, and that stage asks for a 6000 hertz filter that
> cannot exist at our 1000 hertz sampling rate. Nothing is broken on the animal
> side, nothing is lost from the data.
>
> ✅ **The one dangerous possibility is now RULED OUT** (tested 2026-08-03). The
> Monitor band really does apply, so I am not looking at an unfiltered trace
> while believing it is filtered. See *The test that closed this* below.
>
> **Still open:** only whether the spike sorter stage can be switched off so the
> log stops filling. Log tidiness, nothing more.

## What I actually see

Three different error strings, all on 2026-08-03, in these two files:

```
~/.local/state/radiens/logs/radix.log          (the Python side, py_bridge)
~/.local/state/radiens/logs/allegoserver.log   (the Go side)
```

**1. The main one. 1142 of them, 13:21:54 to 14:39:03.**

```
radix.py_bridge - ERROR - IirFilterDesign - IirFilterDesign (python) error :
py_bridge.dsp: Failed to design iir filter: Digital filter critical frequencies must be 0 < Wn < 1
```

**2. A different one, 208 of them, in a narrow 42 second window at 13:24.**

```
py_bridge.dsp: Failed to design iir filter: filter critical frequencies must be greater than 0
```

**3. What the server does about it. 40 of them, 38 at `fs=1000` and 2 at `fs=625`.**

```
[KNL:cd14] failed to set dsp group  module=spikesorter
error="DSP scraper/stage spike-sorter, fs=1000 - set DSP failed : , bandpass :
       dsp_flowthru/NewDSP_IIR - invalid design spec"
```

Two more things appear in the same minutes and are unrelated background noise,
so do not chase them:

- `[HAL:386e] error ... unable to send to listener '0'` — a warning about the
  hardware abstraction layer's stream listeners, it fires every 11 seconds all
  day whether or not I touch anything.
- `makeSetStatusChipZMeasureCommand logrus_error="can not add field \"port\""` —
  a cosmetic complaint about a logging field during an impedance measurement.

## What it means, in plain words

A digital filter cannot be told to keep frequencies that the recording is too
slow to see. The hard ceiling is half the sampling rate, called the Nyquist
frequency. We sample at 1000 hertz, so the ceiling is 500 hertz, and the Monitor
plot itself is downsampled further to 625 hertz, ceiling 312.5 hertz.

Filter software does not work in hertz, it works in a fraction of that ceiling,
called `Wn`. A legal filter has `Wn` strictly between 0 and 1. Ask for anything
at or above the ceiling and `Wn` comes out bigger than 1, and the design fails.
That is error 1 word for word.

Now the cause, which is visible one line earlier in `allegoserver.log`:

```
Created DSP ok  spec="DSP flow-thru [Port A/stage spike-sorter ()]  bandpass  fs=3e+04, f_cut=[3e+02, 6e+03]"
```

There is a **spike sorter** stage in the signal chain, and it carries a
hard-wired 300 to 6000 hertz bandpass that was written for a 30000 hertz
sampling rate. That is the band you use to see individual neurons firing, which
is not what we record at all, we record slow sleep rhythms. Allego re-designs
that stage's filter at whatever rate is actually running, so at our 1000 hertz
it computes `Wn = 6000 / 500 = 12`, which is illegal, and it complains. Every
time I touch the filter group it redesigns and complains again, which is why a
handful of clicks produced over a thousand log lines.

**So error 1 is not my EEG band at all.** It is a stage I never asked for,
asking for a band that cannot exist at our sample rate.

Error 2 IS mine. Something submitted a **low cutoff of exactly 0**, and 0 is not
allowed either, `Wn` must be strictly greater than 0. A high pass at 0 hertz is
a meaningless instruction, it is the same as no high pass.

## ⚠️ WHY THIS DOES NOT TOUCH THE DATA

**The Allego filters are display only. They never reach the saved file.** We
proved this on 2026-07-31 by parking the notch filter at 50 hertz, where nothing
real lives, and then checking the saved spectrum. The 1 hertz bins from 47 to 53
hertz came out 2.457, 2.504, 2.354, 2.401, 2.365 and 2.462, perfectly flat, no
notch. See [[electrode-connection-state-test]] and [[2026-07-31]].

The `.xdat` primary file is raw wideband with only the hardware bandpass on the
chip. Everything we do to the picture on screen is cosmetic. A failed display
filter therefore CANNOT corrupt a recording, and it cannot explain any of the
electrode contact problems.

## How to fix it

**For error 2, which is the one I caused.** Never type 0 as the low cutoff. Use
**0.1 hertz** or **0.5 hertz**. For our sleep EEG the display band is 0.5 to 30
hertz, and for EMG it is 10 to 300 hertz, same numbers as the offline pipeline.

**For error 1, the spike sorter.** Keep every band strictly inside the ceiling of
whatever rate is running:

| Rate in play | Ceiling (Nyquist) | Highest legal high cutoff |
| --- | --- | --- |
| acquisition 1000 Hz | 500 Hz | use 300 Hz or below |
| Monitor plot 625 Hz | 312.5 Hz | use 250 Hz or below |

Our EEG band, 0.5 to 30 hertz, is far inside both, so it is always safe. The EMG
band, 10 to 300 hertz, is legal at acquisition rate but sits ABOVE the Monitor
plot ceiling of 312.5 only if you push it past 300, so leave it at 300.

The spike sorter's own 300 to 6000 hertz band is not something I set, and it
will keep failing at 1000 hertz no matter what I type in the EEG band. The clean
fix is to disable or remove the spike sorter stage so it stops being designed at
all. **I have not found where to do that yet.** That is the deferred part.

## ✅ The test that closed this, 2026-08-03

The one thing that could have made this serious was: when `failed to set dsp
group` fires, does the WHOLE filter group get rejected? If it did, my EEG band
would silently not be applied, and I would be judging traces I believed were
filtered but were not.

I parked the Monitor display band at **0.5 to 5 hertz** and looked. **The trace
visibly changed.** So the band applied.

That means the rejection is **per stage, not per group**. Allego drops the one
stage whose design is impossible, the spike sorter, and keeps the rest of the
chain. The Monitor band is unaffected. Combined with the display filters never
reaching the saved file, this is now confirmed cosmetic on both counts, the
picture is right AND the data is untouched.

> [!quote] Paper-ready
> Visualization filters in Allego are applied per processing stage and are
> display side only, so a rejected stage neither alters the applied display band
> nor reaches the raw wideband `.xdat` primary file.

## Deferred, to pick up on a quiet day

1. Find where the spike sorter stage is enabled, in Allego's Signal Processing
   tab or in the workspace file, and turn it off. Then confirm the log goes
   quiet after a filter change. See [[allego-presets-workspace]] for what the
   workspace does and does not remember. **Log tidiness only, nothing depends
   on it.**
2. If the spike sorter cannot be disabled, ask Kontex whether the stage can be
   suppressed for a 1000 hertz configuration. Low priority, log noise only.
   Vendor thread lives in `01-infrastructure/vendor-correspondence/`.

## Related

- [[allego-monitor-guide]] — what every Monitor control does
- [[signal-quality-and-grounding]] — where the bandpass and notch are actually set
- [[electrode-connection-state-test]] — the proof that the notch is display side
- [[eeg-analysis-pipeline]] — the offline path, where the real filtering happens
