---
tags: [procedure, eeg, artefact, railing, quality-control, scoring]
created: 2026-08-06
---

# Artefact and railing rejection policy for sleep EEG

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The rules we follow when part of a recording is unusable. It answers one
> question: when a channel goes bad for a while, do we throw away those minutes and keep the
> rest of the night, or do we throw away the whole animal?
>
> **Why it exists.** Written 2026-08-06 after a genuinely good proposal — mark the bad epochs
> as missing and keep the 24 hours around them — turned out not to apply to our current
> recordings, for a reason that was not obvious and that we had to measure rather than assume.
> The general policy is right and we will need it. It just cannot rescue a channel that was
> never connected.
>
> **How to read this page.** §1 is the policy itself. §2 explains railing in plain words. §3 is
> the test you must run before applying the policy, and §4 is the measurement that showed why.
> Big picture: [[nvr-system-overview]].

Source data: [[2026-08-06-recording-data-quality-preregistration]] · contact context:
[[2026-08-06-fleet-duty-cycle-census]] · signal signatures: [[signal-quality-and-grounding]]

## 1. The policy

**Reject at the epoch level, never at the animal level, provided the channel is connected.**

1. **Mark every epoch containing any railed sample as missing.** Do not treat a railed segment
   as valid EEG even when the EMG in the same epoch looks fine. Railing destroys information
   at the moment of recording and no filter recovers it.
2. **Report the rejected percentage separately for wake, NREM and REM**, not only as a total.
   Artefact that removes one state preferentially biases time-in-state and every spectral
   result that follows.
3. **Check whether rejected epochs cluster.** Scattered rejections are tolerable. Long
   continuous blocks, or clustering at state transitions, are not, because they remove exactly
   the epochs that carry the transition information.
4. **Score the surviving epochs, then repeat the analysis with and without them** and report
   both. If the conclusion changes, the artefact is load-bearing and must be reported as such.
5. **Only exclude an entire animal** when §3 below shows the surviving epochs are not
   physiologically distinguishable from an unconnected amplifier.

> [!important] There is no universal acceptance threshold, and we should not invent one
> Published sleep-EEG standards require technically interpretable recordings and explicit
> artefact identification. They do **not** specify a percentage of rejected epochs above which
> a recording is invalid. Human sleep pipelines commonly pre-define a rejection threshold, but
> it is study and analysis specific. **We therefore pre-register our threshold per experiment
> rather than adopting a fixed number**, and we always report the achieved rejection rate.

> [!warning] State the unit, always: samples or epochs
> On 2026-08-06 a channel was described as "7% railed" from a **fraction of samples**
> measurement. At the **epoch** level the same channel had railing in **77.6% of epochs**,
> because a single railed sample spoils a whole 10 s epoch. These differ by an order of
> magnitude and they lead to opposite decisions. **Always say which unit you mean.**

## 2. What railing is, in plain words

The amplifier can only represent voltages inside a fixed window, about ±6389 µV per sample,
12.8 mV peak to peak. When the incoming signal is bigger than that, the tops and bottoms of the
wave are **flattened off**, like a photograph where the sky is blown out to pure white.

This matters more than it sounds:

- The flattening is **not a frequency** you can filter out. Notching and band-passing rearrange
  which frequencies survive; they cannot restore a value that was never recorded.
- Clipping is **non-linear**, so it creates harmonics that were not in the original signal. A
  clipped 60 Hz hum generates energy at 120, 180, 240 Hz that a 60 Hz notch will not touch.
- Therefore a railed epoch is **missing data**, not noisy data, and must be marked missing.

## 3. 🔴 The test you MUST run before applying the policy

The policy assumes the channel is genuinely connected and is being intermittently spoiled. That
assumption has to be checked, because there is a second possibility that looks identical from
the outside: **the channel is disconnected, and the railing is a symptom of the disconnection
rather than an artefact on top of good data.**

Physically, on our rig: an open electrode acts as an antenna, picks up 1000-4700 µV of 60 Hz
mains, and that alone is enough to reach the 6389 µV ceiling. **A disconnected channel rails
because it is disconnected.**

**The test.** Discard every epoch containing any railing, then measure the **spectral shape** of
what survives and compare it to the wire-free floor control channels recorded in the same file
(`/3`-`/16` and `/35`-`/48`, never `/17`-`/32` or `/49`-`/64`).

| outcome on the surviving epochs | meaning | action |
| --- | --- | --- |
| spectral slope clearly steeper than the floor range, delta fraction above it | real EEG, intermittently spoiled | **apply the policy, keep the animal** |
| slope and delta fraction inside the floor range | the surviving epochs are not EEG either | **exclude the animal; rejection cannot help** |

Real neural activity has most of its power at low frequencies and falls steeply with increasing
frequency, the one-over-f shape. Noise is spread evenly and plots flat. **Filtering cannot
create that shape**, which is why it survives as a discriminator when amplitude does not.

## 4. The measurement that produced this policy, 2026-08-06

Recording `allego_0__uid0806-12-45-02`, 782 epochs of 10 s, all 8 positions. Floor control slope
range, 5th to 95th percentile: **[−0.98, −0.10]**.

| position | % epochs with any railing | longest continuous railed run | clean epochs | slope on **clean epochs only** | conclusion |
| --- | --- | --- | --- | --- | --- |
| **B1** | **0.0%** | 0 min | 782 | **−2.14**, delta 0.43 | **real EEG, no rejection needed** |
| B2 | 16.1% | 4.5 min | 656 | −0.48 | not EEG |
| D2 | 29.7% | 9.2 min | 550 | −0.30 | not EEG |
| C2 | 41.2% | 12.3 min | 460 | −0.33 | not EEG |
| C1 | 77.6% | 30.0 min | 175 | −0.26 | not EEG |
| A1 | 99.7% | **91.2 min** | 2 | — | not EEG |
| D1 | 100% | **130.3 min** | 0 | — | not EEG |
| **A2, NO MOUSE** | **100%** | 130.3 min | 0 | — | **the control** |

> [!danger] Three findings, and the third is the decisive one
> **1. The railing is not scattered movement artefact.** A1 and D1 rail in continuous blocks of
> 91 and 130 minutes. 130 minutes was the entire analysis window. That is a sustained saturated
> state, not transient movement.
>
> **2. The A2 position, which contains no animal at all, rails 100% of the time.** There is no
> mouse there to move. This is direct proof that on this rig **railing is the open-electrode
> signature**, not something the animal does.
>
> **3. Discarding railed epochs rescues nothing.** Taking only the perfectly clean epochs — 656
> for B2, 550 for D2, 460 for C2 — the spectral shape still sits inside the bare-wire range.
> **The surviving epochs are not corrupted EEG. They are not EEG.**

### The EEG-versus-EMG co-railing diagnostic

Whether the two channels of an animal rail **at the same time** localises the fault, because
they share a tether, slip ring, ground and headstage but not an electrode.

| position | EEG epochs that also have EMG railing | interpretation |
| --- | --- | --- |
| B2 | **100%** | **shared path** — tether, ground, connector or headstage, not the EEG electrode |
| C2 | 54% | mixed |
| C1 | 46% | mixed |
| D2 | **0%** | **EEG path alone** — the EEG pin pair or its board connection |
| B1 | neither channel ever rails | — |

> [!quote] Paper-ready
> Epochs containing any amplifier saturation were marked as missing rather than filtered,
> because clipping is non-linear and irreversible. Before applying epoch rejection, the
> spectral slope of non-saturated epochs was compared against simultaneously recorded amplifier
> inputs with no electrode attached; channels whose non-saturated epochs fell within the
> unconnected distribution were excluded entirely, as epoch rejection cannot recover a channel
> that was never connected.

## 5. When this policy becomes the operative one

Today it changes nothing, because only one animal has EEG and that animal has **zero** railed
epochs. The policy matters the moment we have several connected animals, which is the situation
the rig is being rebuilt for. **Keep this page; it is written for that day.**
